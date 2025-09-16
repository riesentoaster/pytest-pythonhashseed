import sys
from unittest.mock import MagicMock, patch

import pytest_pythonhashseed as plugin


def _get_platform_specific_patches():
    """Return the appropriate patch context manager based on platform."""
    if sys.platform == 'win32':
        return patch('subprocess.run', return_value=MagicMock(returncode=0))

    return patch('os.execve')


def _assert_platform_specific_calls(
    mock_obj,
    expected_extra_args=None,
    expected_env=None,
):
    """Assert platform-specific calls based on the current platform."""
    mock_obj.assert_called_once()
    assert mock_obj.call_args.args[-1] == expected_env
    if expected_extra_args:
        print(mock_obj.call_args.args)  # noqa: T201
        actual_args = mock_obj.call_args.args[1]
        expected_args = expected_extra_args + sys.argv[1:]
        assert actual_args == expected_args


def test_pytest_addoption():
    parser = MagicMock()
    group = MagicMock()
    parser.getgroup.return_value = group

    plugin.pytest_addoption(parser)

    parser.getgroup.assert_called_once_with('general')
    group.addoption.assert_called_once()
    assert group.addoption.call_args.args[0] == '--pythonhashseed'


@patch.dict('os.environ', {}, clear=True)
def test_pytest_configure_opt_not_defined():
    config = MagicMock()
    config.getoption.return_value = None

    with _get_platform_specific_patches() as mock_func:
        plugin.pytest_configure(config)

        config.getoption.assert_called_once_with('pythonhashseed')
        mock_func.assert_not_called()


@patch.dict('os.environ', {'SMTH': '1'}, clear=True)
def test_pytest_configure_opt_set_env_not():
    config = MagicMock()
    config.getoption.return_value = 42

    with _get_platform_specific_patches() as mock_func:
        plugin.pytest_configure(config)

        config.getoption.assert_called_once_with('pythonhashseed')

        expected_env = {'PYTHONHASHSEED': '42', 'SMTH': '1'}
        _assert_platform_specific_calls(
            mock_func,
            expected_env=expected_env,
        )


@patch.dict('os.environ', {'PYTHONHASHSEED': '42'}, clear=True)
def test_pytest_configure_opt_match_env():
    config = MagicMock()
    config.getoption.return_value = 42

    with _get_platform_specific_patches() as mock_func:
        plugin.pytest_configure(config)

        config.getoption.assert_called_once_with('pythonhashseed')
        mock_func.assert_not_called()


@patch.dict('os.environ', {'PYTHONHASHSEED': '42', 'SMTH': '1'}, clear=True)
def test_pytest_configure_opt_mismatch_env():
    config = MagicMock()
    config.getoption.return_value = 0

    with _get_platform_specific_patches() as mock_func:
        plugin.pytest_configure(config)

        config.getoption.assert_called_once_with('pythonhashseed')

        expected_env = {'PYTHONHASHSEED': '0', 'SMTH': '1'}
        _assert_platform_specific_calls(
            mock_func,
            expected_env=expected_env,
        )


@patch.dict('os.environ', {'PYTHONHASHSEED': '42'}, clear=True)
def test_pytest_configure_opt_mismatch_env_run_as_module():
    config = MagicMock()
    config.getoption.return_value = 0

    mod = MagicMock()
    mod.__spec__ = MagicMock()
    mod.__spec__.name = 'pytest_module_name.__main__'

    with patch.dict('sys.modules', {'__main__': mod}):  # noqa: SIM117
        with _get_platform_specific_patches() as mock_func:
            plugin.pytest_configure(config)

            expected_extra_args = [
                sys.executable,
                '-m',
                'pytest_module_name',
            ]
            expected_env = {'PYTHONHASHSEED': '0'}
            _assert_platform_specific_calls(
                mock_func,
                expected_extra_args=expected_extra_args,
                expected_env=expected_env,
            )

from unittest.mock import MagicMock, patch

import pytest_pythonhashseed as plugin


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

    with patch('os.execve') as execve:
        plugin.pytest_configure(config)

        config.getoption.assert_called_once_with('pythonhashseed')
        execve.assert_not_called()


@patch.dict('os.environ', {'SMTH': '1'}, clear=True)
def test_pytest_configure_opt_set_env_not():
    config = MagicMock()
    config.getoption.return_value = 42

    with patch('os.execve') as execve:
        plugin.pytest_configure(config)

        config.getoption.assert_called_once_with('pythonhashseed')
        execve.assert_called_once()
        assert execve.call_args.args[2] == {
            'PYTHONHASHSEED': '42',
            'SMTH': '1',
        }


@patch.dict('os.environ', {'PYTHONHASHSEED': '42'}, clear=True)
def test_pytest_configure_opt_match_env():
    config = MagicMock()
    config.getoption.return_value = 42

    with patch('os.execve') as execve:
        plugin.pytest_configure(config)

        config.getoption.assert_called_once_with('pythonhashseed')
        execve.assert_not_called()


@patch.dict('os.environ', {'PYTHONHASHSEED': '42', 'SMTH': '1'}, clear=True)
def test_pytest_configure_opt_mismatch_env():
    config = MagicMock()
    config.getoption.return_value = 0

    with patch('os.execve') as execve:
        plugin.pytest_configure(config)

        config.getoption.assert_called_once_with('pythonhashseed')
        execve.assert_called_once()
        assert execve.call_args.args[2] == {'PYTHONHASHSEED': '0', 'SMTH': '1'}

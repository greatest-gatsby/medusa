import unittest
import unittest.mock

import medusa.config

class ConfigTestCase(unittest.TestCase):

    # Verifies that not providing a subcommand to `config` won't throw
    @unittest.mock.patch('builtins.print')
    def test_config_no_subcommand(self, mock_print):
        newArgs = []
        medusa.config.process_config(newArgs)

        mock_print.assert_called_with('Please specify a subcommand for "config"')
        mock_print.assert_called_once()

    # Verifies that passing an empty key to getConfigValue(key) won't throw
    @unittest.mock.patch('builtins.print')
    def test_config_getConfigValue_emptyKey(self, mock_print):
        arg = None
        val = medusa.config.get_config_value(arg)

        mock_print.assert_called_with('No key specified')
        mock_print.assert_called_once()
        assert val == None

    # Verifies passing an unknown key simply prints an error
    @unittest.mock.patch('builtins.print')
    def test_config_getConfigValue_invalidKey(self, mock_print):
        arg = 'unused-key'
        val = medusa.config.get_config_value(arg)

        mock_print.assert_called_with('No key', arg)
        mock_print.assert_called_once()
        assert val == None


if __name__ == '__main__':
    unittest.main()
from pyfakefs.fake_filesystem_unittest import TestCase
from pyfakefs import fake_filesystem

import json
import unittest
import unittest.mock
from unittest.mock import Mock, MagicMock, patch

import medusa.config
import medusa.parsers

class ConfigTestCase(TestCase):

    def setUp(self):
        self.setUpPyfakefs()

    # Verifies that not providing a subcommand to `config` won't throw
    @unittest.mock.patch('medusa.parsers.get_config_parsers')
    @unittest.mock.patch('builtins.print')
    def test_config_process_noSubcommand(self, mock_print, conf_parser):
        newArgs = []
        fakeParser = medusa.parsers
        fakeParser.parse_args = MagicMock()
        conf_parser = MagicMock(return_value=fakeParser)

        with unittest.mock.patch.object(fakeParser, 'get_config_parsers', wraps=fakeParser.get_config_parsers) as faked:
            medusa.config.process_config(newArgs)
            mock_print.assert_called_with('Please specify a subcommand for `config`')
            mock_print.assert_called_once()
            # fakeParser.print_usage.assert_called_once()
            # todo: actually verify print_usage gets called here
    
    # Verifies that the `get` subcommand triggers `get_config_value(key)`
    @unittest.mock.patch('builtins.print')
    def test_config_process_get(self, mock_print):
        arg = ['get', 'unused-key']
        medusa.config.get_config_value = MagicMock(return_value='Planted value')

        medusa.config.process_config(arg)
        
        mock_print.assert_called_with('Planted value')

    @patch('builtins.print')
    @patch('medusa.config.set_config_value')
    def test_config_process_set(self, mock_print, set_conf_val):
        arg = ['set', 'unused-key', 'incredible value!']

        medusa.config.process_config(arg)

        set_conf_val.assert_not_called()

    # Verifies that passing an empty key to getConfigValue(key) won't throw
    @unittest.mock.patch('builtins.print')
    def test_config_getConfigValue_emptyKey(self, mock_print):
        with self.assertRaises(KeyError):
            val = medusa.config.get_config_value(None)
        mock_print.assert_not_called()

    # Verifies that passing an unknown key simply prints an error
    @unittest.mock.patch('builtins.print')
    def test_config_getConfigValue_unknownKey(self, mock_print):
        fContents = '{"server_directory":"not_real_location"}'
        self.fs.create_file(medusa.config.get_config_location(), contents = fContents)
        
        val = medusa.config.get_config_value('unused_key')

        mock_print.assert_not_called()
        assert val == None

    # Verifies that passing a valid key returns its value
    def test_config_getConfigValue_validKey(self):
        fContents = '{"server_directory":"not_real_location"}'
        self.fs.create_file(medusa.config.get_config_location(), contents = fContents)
        
        assert medusa.config.get_config_value('server_directory') == 'not_real_location'

    # Verifies that getting a config value with no on-disk config throws
    @unittest.mock.patch('builtins.print')
    def test_config_getConfigValue_noConfig(self, mock_print):
        with self.assertRaises(FileNotFoundError):
            medusa.config.get_config_value('server_directory')
            mock_print.assert_called_with('Config not found at', medusa.config.get_config_location())

    # Verifies that setting a new config value writes changes to disk
    def test_config_setConfigValue_writesVal(self):
        fContents = '{"server_directory":"not_real_location"}'
        self.fs.create_file(medusa.config.get_config_location(), contents = fContents)

        medusa.config.set_config_value('server_directory', 'new test value')

        with open(medusa.config.get_config_location(), 'r') as file:
            thing = json.load(file)
            assert thing['server_directory'] == 'new test value'

    # Verifies that setting a new config value with no on-disk config throws
    @unittest.mock.patch('builtins.print')
    def test_config_setConfigValue_noConfig(self, mock_print):
        with self.assertRaises(FileNotFoundError):
            medusa.config.set_config_value('server_directory','new test value')
            mock_print.assert_called_with('Config not found at', medusa.config.get_config_location())


if __name__ == '__main__':
    unittest.main()
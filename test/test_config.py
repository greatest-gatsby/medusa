from pyfakefs.fake_filesystem_unittest import TestCase
from pyfakefs import fake_filesystem

import json
import unittest
import unittest.mock
import os

import medusa.config

class ConfigTestCase(TestCase):

    def setUp(self):
        self.setUpPyfakefs()

    # Verifies that not providing a subcommand to `config` won't throw
    @unittest.mock.patch('builtins.print')
    def test_config_process_noSubcommand(self, mock_print):
        newArgs = []
        medusa.config.process_config(newArgs)

        mock_print.assert_called_with('Please specify a subcommand for "config"')
        mock_print.assert_called_once()

    # Verifies that passing an empty key to getConfigValue(key) won't throw
    @unittest.mock.patch('builtins.print')
    def test_config_getConfigValue_emptyKey(self, mock_print):
        val = medusa.config.get_config_value(None)

        mock_print.assert_called_with('No key specified')
        mock_print.assert_called_once()
        assert val == None

    # Verifies that passing an unknown key simply prints an error
    @unittest.mock.patch('builtins.print')
    def test_config_getConfigValue_unknownKey(self, mock_print):
        fContents = '{"server_directory":"not_real_location"}'
        self.fs.create_file(medusa.config.get_config_location(), contents = fContents)
        
        val = medusa.config.get_config_value('unused_key')

        mock_print.assert_called_with('No key', 'unused_key')
        mock_print.assert_called_once()
        assert val == None

    # Verifies that passing a valid key returns its value
    def test_config_getConfigValue_validKey(self):
        fContents = '{"server_directory":"not_real_location"}'
        self.fs.create_file(medusa.config.get_config_location(), contents = fContents)
        
        assert medusa.config.get_config_value('server_directory') == 'not_real_location'

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

    # Verifies that setting a new config value with no on-disk config
    @unittest.mock.patch('builtins.print')
    def test_config_setConfigValue_noConfig(self, mock_print):
        with self.assertRaises(FileNotFoundError):
            medusa.config.set_config_value('server_directory','new test value')
            mock_print.assert_called_with('Config not found at', medusa.config.get_config_location())


if __name__ == '__main__':
    unittest.main()
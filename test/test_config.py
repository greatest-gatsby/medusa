from pyfakefs.fake_filesystem_unittest import TestCase

import json
from json import JSONDecodeError
import unittest
import unittest.mock
from unittest.mock import MagicMock, patch

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

        medusa.config.process_config(newArgs)
        mock_print.assert_called_with('Please specify a subcommand for `config`')
        mock_print.assert_called_once()
            # fakeParser.print_usage.assert_called_once()
            # todo: actually verify print_usage gets called here
    
    # Verifies that the `get` subcommand triggers `get_config_value(key)`
    @unittest.mock.patch('medusa.config.get_config_value', return_value='Planted value')
    @unittest.mock.patch('builtins.print')
    def test_config_process_get(self, mock_print, mock_get_conf_val):
        arg = ['get', 'unused-key']
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

    # Verifies that argparse prints an error if command is "get" but is given no config key
    @unittest.mock.patch('sys.stderr')
    def test_config_process_getConfigKey_printErrorIfNoKey(self, mock_err):
        args = ['get']
        with self.assertRaises(SystemExit):
            medusa.config.process_config(args)
        
    # Verifies that an error is printed if command is "get" but is given an empty config key
    @unittest.mock.patch('sys.stderr')
    @unittest.mock.patch('builtins.print')
    def test_config_process_getConfigKey_printErrorIfEmptyKey(self, mock_print, mock_err):
        args = ['get', '']
        medusa.config.process_config(args)
        mock_print.assert_called_once_with('Invalid key', '')
    
    # Verifies that an error is printed if the given key is not found in the config  
    @unittest.mock.patch('medusa.config.get_config_value')
    @unittest.mock.patch('builtins.print')
    def test_config_process_getConfigKey_noMatchingKey(self, mock_print, mock_get_config_val):
        key_name = 'fake key'
        args = ['get', key_name]
        medusa.config.get_config_value = MagicMock(return_value=None)
        medusa.config.process_config(args)
        mock_print.assert_called_once_with(None)
    
    @unittest.mock.patch('medusa.config.init_config')
    # Verifies that `config init` invokes the config initialization method
    def test_config_process_init_invokesInitConfig(self, mock_init):
        args = ['init']
        medusa.config.init_config = MagicMock()
        medusa.config.process_config(args)
        medusa.config.init_config.assert_called_once_with(None)
    
    # Verifies that `config where` prints the config location
    @unittest.mock.patch('medusa.config.get_config_location')
    @unittest.mock.patch('builtins.print')
    def test_config_process_where_printsConfigLocation(self, mock_print, mock_loc):
        args = ['where']
        planted_path = '/bridge/to/terabythea'
        medusa.config.get_config_location = MagicMock(return_value = planted_path)
        medusa.config.process_config(args)
        medusa.config.get_config_location.assert_called_once()
        mock_print.assert_called_once_with(planted_path)
    
    @unittest.mock.patch('builtins.print')
    def test_config_setConfigValue_exitsIfConfigEmpty(self, mock_print):
        self.fs.create_file(medusa.config.get_config_location())
        with self.assertRaises(SystemExit):
            medusa.config.set_config_value('key', 'value')
        mock_print.assert_called_once_with('Config file empty -- generate a new one with `medusa config init`')
      
    @unittest.mock.patch('builtins.print')  
    def test_config_setConfigValue_printsJsonDecodeError(self, mock_print):
        self.fs.create_file(medusa.config.get_config_location(), contents='"property":"unclosed')
        with self.assertRaises(JSONDecodeError) as jer:
            medusa.config.set_config_value('key', 'value')
            mock_print.assert_called_with(jer)
            mock_print.assert_called_with('Error opening config for write -- file is malformed or corrupt')
            
    @unittest.mock.patch('json.load')
    @unittest.mock.patch('builtins.print')
    def test_config_setConfigValue_rethrowsMiscError(self, mock_print, mock_json):
        self.fs.create_file(medusa.config.get_config_location())
        json.load = MagicMock(side_effect=IOError())
        with self.assertRaises(IOError):
            medusa.config.set_config_value('key', 'value')
        mock_print.assert_called_once_with('Unknown error opening config for write')
     
    @unittest.mock.patch('json.dump')
    @unittest.mock.patch('builtins.print')   
    def test_config_setConfigValue_printsAndExits(self, mock_print, mock_json):
        self.fs.create_file(medusa.config.get_config_location(), contents='{"key":"oldvalue"}')
        json.dump = MagicMock(side_effect=TypeError())
        with self.assertRaises(TypeError):
            medusa.config.set_config_value('key', 'value')
        mock_print.assert_called_once_with('Error writing updated config to disk')
    
    @unittest.mock.patch('builtins.input', return_value = 'r')
    @unittest.mock.patch('builtins.print')
    def test_config_init_promptsForOverwrite(self, mock_print, mock_input):
        self.fs.create_file(medusa.config.get_config_location(), contents='{"key":"oldvalue"}')
        result = medusa.config.init_config(verbosity=1)
        mock_print.assert_called_with('Config init aborted.')
        mock_input.assert_called_once_with('Are you SURE you want to OVERWRITE this file? [y/N]: ')
        self.assertFalse(result)
    
    @unittest.mock.patch('builtins.print')
    @unittest.mock.patch('medusa.config.get_config_location', return_value='/brandnew/directory/medusa.json')
    def test_config_init_createsDirectoryIfNotExists(self, mock_conf_location, mock_print):
        self.assertFalse(self.fs.isdir(medusa.config.get_config_location()))
        medusa.config.init_config()
        self.assertTrue(self.fs.isdir('/brandnew/directory/'))
        sep = self.fs.path_separator
        mock_print.assert_called_once_with('Created new Medusa config at', f'{sep}brandnew{sep}directory{sep}medusa.json')

if __name__ == '__main__':
    unittest.main()
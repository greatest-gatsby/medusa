from pyfakefs.fake_filesystem_unittest import TestCase
from pyfakefs import fake_filesystem

from prettytable import PrettyTable

import jsonpickle

import json
import unittest
import unittest.mock
import os

import medusa.server
import medusa.filebases
import medusa.config

class ServerTestCase(TestCase):

    def setUp(self):
        self.setUpPyfakefs()
        medusa.server._servers = []

    # Verifies that the `server` command invokes the server CLI parser
    @unittest.mock.patch('medusa.server.get_servers_from_config', return_value=[])
    @unittest.mock.patch('medusa.parsers.get_server_parsers')
    def test_server_process_callsParser(self, mock_parser_getter, mock_is_file):
        args = []
        mock_parser = unittest.mock.Mock()
        mock_parser_getter.return_value = mock_parser

        medusa.server.process_server(args)

        mock_parser_getter.assert_called_once()
        mock_parser.parse_args.assert_called_once()


    # Verifies that the list function shows a message when there are no registered servers
    @unittest.mock.patch('builtins.print')
    @unittest.mock.patch('medusa.server._servers', return_value = [])
    def test_server_list_printsWhenEmpty(self, mock_servers, mock_print):
        medusa.server.list_servers()

        mock_print.assert_called_once_with('No registered servers')

    # Verifies that the list function accesses and prints key server fields
    @unittest.mock.patch('medusa.server._servers')
    @unittest.mock.patch('builtins.print')
    def test_server_list_accessesFields(self, mock_print, mock_servers):
        srv1 = medusa.server.Server()
        srv1.Alias = 'Friendly'
        srv1.Path = '/Test1'
        srv1.Type = medusa.server.ServerType.PAPER

        medusa.server._servers = [srv1]
        medusa.server.list_servers()

        assert 'No registered servers' not in mock_print.call_args.args

        table = mock_print.call_args.args[0]

        assert 'Friendly' in table.get_string(fields=['Alias'])
        assert 'Test1' in table.get_string(fields=['Path'])
        assert 'PAPER' in table.get_string(fields=['Type'])

    # Verifies that the function to retrieve servers from saved entries
    # in the config file throws if the config file cannot be found.
    def test_server_getFromConfig_throwsIfNoFile(self):
        with self.assertRaises(FileNotFoundError):
            medusa.server.get_servers_from_config()
    
    # Verifies that getFromConfig reads from the 'server_registry' config block
    def test_server_getFromConfig_readsConfig(self):
        test_data = medusa.server.Server()
        test_data.Alias = 'Advanced Cosmonaut'
        test_data.Path = 'Farout Dir/'
        test_data.Type = medusa.server.ServerType.FORGE
        file = jsonpickle.decode(medusa.filebases.DATA)
        file['server_registry'] = [test_data]

        self.fs.create_file(medusa.config.get_config_location(), contents = jsonpickle.encode(file))

        servers = medusa.server.get_servers_from_config()
        assert len(servers) == 1
        assert servers[0].Alias == 'Advanced Cosmonaut'
        assert servers[0].Path == 'Farout Dir/'
        assert servers[0].Type == medusa.server.ServerType.FORGE

    # Verifies that `get_servers()` reads from config if `_servers` is None.
    # If there are no servers, then `_servers` should be an empty list --
    # but it should never be None.
    @unittest.mock.patch('medusa.server._servers')
    @unittest.mock.patch('medusa.server.get_servers_from_config')
    def test_server_get_readsConfigWhenNone(self, mock_config_reader, mock_servers):
        medusa.server._servers = None

        medusa.server.get_servers()

        mock_config_reader.assert_called_once()

    # Verifies that `register_server` writes new servers to disk
    @unittest.mock.patch('builtins.print')
    def test_server_register_writesConfigToDisk(self, mock_print):
        file = jsonpickle.decode(medusa.filebases.DATA)
        self.fs.create_file(medusa.config.get_config_location(), contents = jsonpickle.encode(file))
        self.fs.create_dir('/false/path')

        assert medusa.server.register_server('/false/path', medusa.server.ServerType.SPIGOT, 'Unbelievable')

        with open(medusa.config.get_config_location(), 'r') as conf:
            conf_obj = json.load(conf)
            assert conf_obj['server_registry'][0]['Alias'] == 'Unbelievable'
        
        assert len(medusa.server._servers) == 1
        assert medusa.server._servers[0].Alias == 'Unbelievable'

    # Verifies that `register_server` writes the `.medusa` file
    def test_server_register_writesDotMedusa(self):
        path = os.path.join('/inventive/trail', '.medusa')
        self.fs.create_dir('/inventive/trail')
        file = jsonpickle.decode(medusa.filebases.DATA)
        self.fs.create_file(medusa.config.get_config_location(), contents = jsonpickle.encode(file))

        assert not os.path.exists(path)

        assert medusa.server.register_server('/inventive/trail', medusa.server.ServerType.SPIGOT, 'Monsieur Increible')

        with open(path, 'r') as dotmed:
            med_json = json.load(dotmed)
            assert med_json['metadata']['alias'] == 'Monsieur Increible'

    # Verifies that `register_server` returns False when
    # attempting to register the same server twice
    def test_server_register_falseOnDuplicate(self):
        self.fs.create_dir('/inventive/trail')
        existing_server = medusa.server.Server()
        existing_server.Alias = 'Yo bobby run it'
        existing_server.Path = '/inventive/trail'
        existing_server.Type = medusa.server.ServerType.VANILLA
        
        file = jsonpickle.decode(medusa.filebases.DATA)
        file['server_registry'] = [existing_server]
        self.fs.create_file(medusa.config.get_config_location(), contents = jsonpickle.encode(file))
        medusa.server._servers = medusa.server.get_servers_from_config()

        assert not medusa.server.register_server('/inventive/trail', medusa.server.ServerType.VANILLA, 'Yo bobby run it')


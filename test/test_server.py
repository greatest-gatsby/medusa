from pyfakefs.fake_filesystem_unittest import TestCase
from pyfakefs import fake_filesystem

from prettytable import PrettyTable

import jsonpickle

import json
import unittest
import unittest.mock
import os

import medusa.servers
import medusa.servers.manager
import medusa.filebases
import medusa.config

class ServerTestCase(TestCase):

    def setUp(self):
        self.setUpPyfakefs()
        medusa.servers.manager._servers = []

    def plant_server(self, servers):
         # Write data to fake fs
        file = jsonpickle.decode(medusa.filebases.DATA)
        file['server_registry'] = servers
        file_str = jsonpickle.encode(file)
        self.fs.create_file(medusa.config.get_config_location(), contents = file_str)
        medusa.servers.manager._servers = servers


    # Verifies that the `server` command invokes the server CLI parser
    @unittest.mock.patch('medusa.servers.manager.get_servers_from_config', return_value=[])
    @unittest.mock.patch('medusa.parsers.get_server_parsers')
    def test_server_process_callsParser(self, mock_parser_getter, mock_is_file):
        args = []
        mock_parser = unittest.mock.Mock()
        mock_parser_getter.return_value = mock_parser

        medusa.servers.manager.process_server(args)

        mock_parser_getter.assert_called_once()
        mock_parser.parse_args.assert_called_once()


    # Verifies that the list function shows a message when there are no registered servers
    @unittest.mock.patch('builtins.print')
    @unittest.mock.patch('medusa.servers.manager._servers', return_value = [])
    def test_server_list_printsWhenEmpty(self, mock_servers, mock_print):
        medusa.servers.manager.list_servers()

        mock_print.assert_called_once_with('No registered servers')

    # Verifies that the list function accesses and prints key server fields
    @unittest.mock.patch('medusa.config.get_config_value', return_value='/srv')
    @unittest.mock.patch('medusa.servers.manager._servers')
    @unittest.mock.patch('builtins.print')
    def test_server_list_accessesFields(self, mock_print, mock_servers, mock_config_get):
        srv1 = medusa.servers.Server()
        srv1.Alias = 'Friendly'
        srv1.Path = '/srv/friends forever/s1'
        srv1.Type = medusa.servers.manager.ServerType.PAPER

        medusa.servers.manager._servers = [srv1]
        medusa.servers.manager.list_servers()

        assert 'No registered servers' not in mock_print.call_args.args

        table = mock_print.call_args.args[0]

        assert 'Friendly' in table.get_string(fields=['Alias'])
        assert 'friends forever' + os.path.sep + 's1' in table.get_string(fields=['Path'])
        assert 'PAPER' in table.get_string(fields=['Type'])

    # Verifies that the function to retrieve servers from saved entries
    # in the config file throws if the config file cannot be found.
    def test_server_getFromConfig_throwsIfNoFile(self):
        with self.assertRaises(FileNotFoundError):
            medusa.servers.manager.get_servers_from_config()
    
    # Verifies that getFromConfig reads from the 'server_registry' config block
    def test_server_getFromConfig_readsConfig(self):
        test_data = medusa.servers.Server()
        test_data.Alias = 'Advanced Cosmonaut'
        test_data.Path = 'Farout Dir/'
        test_data.Type = medusa.servers.manager.ServerType.FORGE
        file = jsonpickle.decode(medusa.filebases.DATA)
        file['server_registry'] = [test_data]

        self.fs.create_file(medusa.config.get_config_location(), contents = jsonpickle.encode(file))

        servers = medusa.servers.manager.get_servers_from_config()
        assert len(servers) == 1
        assert servers[0].Alias == 'Advanced Cosmonaut'
        assert servers[0].Path == 'Farout Dir/'
        assert servers[0].Type == medusa.servers.manager.ServerType.FORGE

    # Verifies that `get_servers()` reads from config if `_servers` is None.
    # If there are no servers, then `_servers` should be an empty list --
    # but it should never be None.
    @unittest.mock.patch('medusa.servers.manager._servers')
    @unittest.mock.patch('medusa.servers.manager.get_servers_from_config')
    def test_server_get_readsConfigWhenNone(self, mock_config_reader, mock_servers):
        medusa.servers.manager._servers = None

        medusa.servers.manager.get_servers()

        mock_config_reader.assert_called_once()

    # Verifies that `register_server` writes new servers to disk
    @unittest.mock.patch('builtins.print')
    def test_server_register_writesConfigToDisk(self, mock_print):
        file = jsonpickle.decode(medusa.filebases.DATA)
        self.fs.create_file(medusa.config.get_config_location(), contents = jsonpickle.encode(file))
        self.fs.create_dir('/false/path')

        assert medusa.servers.manager.register_server('/false/path', medusa.servers.manager.ServerType.SPIGOT, 'Unbelievable')

        with open(medusa.config.get_config_location(), 'r') as conf:
            conf_obj = json.load(conf)
            assert conf_obj['server_registry'][0]['Alias'] == 'Unbelievable'
        
        assert len(medusa.servers.manager._servers) == 1
        assert medusa.servers.manager._servers[0].Alias == 'Unbelievable'

    # Verifies that `register_server` writes the `.medusa` file
    def test_server_register_writesDotMedusa(self):
        path = os.path.join('/inventive/trail', '.medusa')
        self.fs.create_dir('/inventive/trail')
        file = jsonpickle.decode(medusa.filebases.DATA)
        self.fs.create_file(medusa.config.get_config_location(), contents = jsonpickle.encode(file))

        assert not os.path.exists(path)

        assert medusa.servers.manager.register_server('/inventive/trail', medusa.servers.manager.ServerType.SPIGOT, 'Monsieur Increible')

        with open(path, 'r') as dotmed:
            med_json = json.load(dotmed)
            assert med_json['metadata']['alias'] == 'Monsieur Increible'

    # Verifies that `register_server` returns False when
    # attempting to register the same server twice
    def test_server_register_falseOnDuplicate(self):
        self.fs.create_dir('/inventive/trail')
        existing_server = medusa.servers.Server()
        existing_server.Alias = 'Yo bobby run it'
        existing_server.Path = '/inventive/trail'
        existing_server.Type = medusa.servers.manager.ServerType.VANILLA
        self.plant_server([existing_server])

        assert not medusa.servers.manager.register_server('/inventive/trail', medusa.servers.manager.ServerType.VANILLA, 'Yo bobby run it')

    # Verifies that `deregister_server` raises an error if
    # the given identifier is None or empty
    def test_server_deregister_throwsIfNullOrEmpty(self):
        with(self.assertRaises(ValueError)):
            medusa.servers.manager.deregister_server(None)
        with(self.assertRaises(ValueError)):
            medusa.servers.manager.deregister_server("  ")
        

    # Verifies that `deregister_server` raises an error if
    # the given identifier matches no known servers
    def test_server_deregister_throwsIfNoneFound(self):
        srv = medusa.servers.Server()
        # Patch the function because we aren't trying to test `is_identifiable_by`,
        # only that its return value is used properly
        with unittest.mock.patch.object(srv, 'is_identifiable_by', return_value=False) as patched:
            medusa.servers.manager._servers = [srv]
            
            with self.assertRaises(KeyError):
                medusa.servers.manager.deregister_server('conflicting')
            patched.assert_called_once()

    # Verifies that `deregister_server` writes its changed config to disk
    def test_server_deregister_writesConfig(self):
        # Generate data
        existing_server = medusa.servers.manager.Server()
        existing_server.Alias = 'delete me!'
        existing_server.Path = '/creative/venture'
        existing_server.Type = medusa.servers.manager.ServerType.FORGE
        self.plant_server([existing_server])
        
        
        with unittest.mock.patch.object(existing_server, 'is_identifiable_by', return_value=True) as patched:
            medusa.servers.manager._servers = [existing_server]
            medusa.servers.manager.deregister_server('delete me!')
            # Call once in memory, call once on disk
            assert patched.call_count == 2
        
        with open(medusa.config.get_config_location(), 'r') as conf:
            txt = conf.read()
            conf_json = jsonpickle.decode(txt)
            assert len(conf_json['server_registry']) == 0

    # Verifies that `deregister_server` updates the servers in memory
    def test_server_deregister_updatesServersInMemory(self):
        # Generate data
        existing_server = medusa.servers.manager.Server()
        existing_server.Alias = 'traaash'
        existing_server.Path = '/unique/outing'
        existing_server.Type = medusa.servers.manager.ServerType.FORGE
        self.plant_server([existing_server])
        
        with unittest.mock.patch.object(existing_server, 'is_identifiable_by', return_value=True) as patched:
            medusa.servers.manager._servers = [existing_server]
            medusa.servers.manager.deregister_server('traaash')
            # Call once in memory, call once on disk
            assert patched.call_count == 2

        assert len(medusa.servers.manager._servers) == 0

    # Verifies that a server can be identified by its path
    def test_server_identifiableBy_matchesPath(self):
        path1 = 'C:/Winders/fabric3'
        srv1 = medusa.servers.manager.Server()
        srv1.Alias = 'Shorthand'
        srv1.Path = path1
        assert srv1.is_identifiable_by(path1)
        
        path2 = '/var/www/sukkit'
        srv2 = medusa.servers.manager.Server()
        srv2.Alias = 'Insinuations'
        srv2.Path = path2
        assert srv2.is_identifiable_by(path2)

    def test_server_identifiableBy_matchesAlias(self):
        alias1 = 'Shorthand'
        srv1 = medusa.servers.manager.Server()
        srv1.Alias = alias1
        srv1.Path = 'C:/Winders/fabric3'
        assert srv1.is_identifiable_by(alias1)
        
        alias2 = 'Kids These Days Dont Know Hardcode Minecraft and that Pains Me'
        srv2 = medusa.servers.manager.Server()
        srv2.Alias = alias2
        srv2.Path = '/var/www/sukkit'
        assert srv2.is_identifiable_by(alias2)
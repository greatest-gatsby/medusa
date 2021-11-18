from os.path import join, curdir
import unittest
from unittest.mock import MagicMock, patch
import jsonpickle
from pyfakefs.fake_filesystem_unittest import TestCase
import medusa

from medusa.filebases import DATA
from medusa.servers import manager
from medusa.config import get_config_location
from medusa.servers.models import Server, ServerType

class ManagerTests(TestCase):
    VIR_PATH = 'D:\\Minecraft\\Servers'

    def setUp(self):
        self.setUpPyfakefs()
        manager._servers = []

    def plant_server(self, servers):
        # Write data to fake fs
        file = jsonpickle.decode(DATA)
        file['server_registry'] = servers
        file_str = jsonpickle.encode(file)
        path = get_config_location()
        outfile = self.fs.create_file(path, contents=file_str)
        manager._servers = servers

    def test_startupScriptFinder_getsSingle(self):
        self.fs.create_file(join(self.VIR_PATH,'bait.bat'))
        self.fs.create_file(join(self.VIR_PATH,'run.bat'))
        self.fs.create_file(join(self.VIR_PATH,'run.sh'))
        self.fs.create_file(join(self.VIR_PATH,'serverstart.bat'))

        
        paths = manager.find_startup_script_paths(self.VIR_PATH)
        assert len(paths) == 1
        assert paths[0] == 'serverstart.bat'

    def test_startupScriptFinder_getsMany(self):
        self.fs.create_file(join(self.VIR_PATH,'bait.bat'))
        self.fs.create_file(join(self.VIR_PATH,'startup.sh'))
        self.fs.create_file(join(self.VIR_PATH,'run.sh'))
        self.fs.create_file(join(self.VIR_PATH,'serverstart.bat'))
        
        paths = manager.find_startup_script_paths(self.VIR_PATH)

        assert len(paths) == 2
        assert 'startup.sh' in paths
        assert 'serverstart.bat' in paths
    
    def test_startupScriptFinder_getsNone(self):
        self.fs.create_file(join(self.VIR_PATH, 'no.txt'))

        paths = manager.find_startup_script_paths(self.VIR_PATH)

        assert len(paths) == 0

    @patch('medusa.servers.manager.create_server')
    @patch('medusa.servers.manager.get_servers_from_config', return_value = [])
    def test_process_create_invokesCreate(self, mock_from, mock_create):
        self.fs.create_file(get_config_location())
        args = ['create']
        manager.process_server(args)
        mock_create.assert_called_once()
        pass
    
    @patch('medusa.servers.manager.deregister_server')
    @patch('medusa.servers.manager.get_servers_from_config')
    def test_process_remove_invokesDeregister(self, mock_from, mock_dereg):
        self.fs.create_file(get_config_location())
        args = ['remove', 'my id']
        manager.process_server(args)
        mock_dereg.assert_called_once_with('my id')
        
    @patch('medusa.servers.manager.list_servers')
    @patch('medusa.servers.manager.get_servers_from_config')
    def test_process_list_invokesList(self, mock_from, mock_list):
        self.fs.create_file(get_config_location())
        args = ['list']
        manager.process_server(args)
        mock_list.assert_called_once()
        
    @patch('medusa.servers.manager.scan_directory_for_servers')
    @patch('medusa.servers.manager.get_servers_from_config')
    def test_process_scan_invokesScan(self, mock_from, mock_scan):
        self.fs.create_file(get_config_location())
        args = ['scan']
        manager.process_server(args)
        mock_scan.assert_called_once_with('')
    
    @patch('builtins.print')
    @patch('medusa.servers.manager.get_server_by_identifier', return_value = None)
    @patch('medusa.servers.manager.get_servers_from_config')
    def test_process_set_printsIfNoServer(self, mock_from, mock_getby, mock_print):
        self.fs.create_file(get_config_location())
        args = ['set', 'no corresponding id', 'alias', 'value']
        manager.process_server(args)
        mock_getby.assert_called_once_with('no corresponding id')
        mock_print.assert_called_once_with('No server "no corresponding id"')
    
    @patch('medusa.servers.manager.update_server')    
    @patch('medusa.servers.manager.get_server_by_identifier')
    @patch('medusa.servers.manager.get_servers_from_config')
    def test_process_set_alias_invokesUpdateServer(self, mock_from, mock_getby, mock_update):
        self.fs.create_file(get_config_location())
        args = ['set', 'bestest server ever', 'alias', 'now the worst server']
        planted_server = Server()
        planted_server.Alias = 'bestest server ever'
        mock_getby.return_value = planted_server
        manager.process_server(args)
        mock_update.assert_called_once()
        called_args = mock_update.call_args[0]
        self.assertEqual('bestest server ever', called_args[0], 'Update should have been invoked with original identifier')
        self.assertEqual('now the worst server', called_args[1].Alias, 'Update was invoked with a non-updated object')
        
    @patch('medusa.servers.manager.update_server')    
    @patch('medusa.servers.manager.get_server_by_identifier')
    @patch('medusa.servers.manager.get_servers_from_config')
    def test_process_set_path_invokesUpdateServer(self, mock_from, mock_getby, mock_update):
        self.fs.create_file(get_config_location())
        args = ['set', 'bestest server ever', 'path', '//remote/server/bro']
        planted_server = Server()
        planted_server.Alias = 'bestest server ever'
        mock_getby.return_value = planted_server
        manager.process_server(args)
        mock_update.assert_called_once()
        called_args = mock_update.call_args[0]
        self.assertEqual('bestest server ever', called_args[0], 'Update should have been invoked with original identifier')
        self.assertEqual('//remote/server/bro', called_args[1].Path, 'Update was invoked with a non-updated object')
        
    @patch('medusa.servers.manager.update_server')    
    @patch('medusa.servers.manager.get_server_by_identifier')
    @patch('medusa.servers.manager.get_servers_from_config')
    def test_process_set_type_invokesUpdateServer(self, mock_from, mock_getby, mock_update):
        self.fs.create_file(get_config_location())
        args = ['set', 'bestest server ever', 'type', 'spigot']
        planted_server = Server()
        planted_server.Alias = 'bestest server ever'
        mock_getby.return_value = planted_server
        manager.process_server(args)
        mock_update.assert_called_once()
        called_args = mock_update.call_args[0]
        self.assertEqual('bestest server ever', called_args[0], 'Update should have been invoked with original identifier')
        self.assertEqual('spigot', called_args[1].Type, 'Update was invoked with a non-updated object')
        
    @patch('builtins.print')
    @patch('medusa.config.get_config_value', return_value='/new/dir')
    def test_scan_emptyDirReturnsZero(self, mock_get, mock_print):
        self.fs.create_dir('/new/dir')
        result = manager.scan_directory_for_servers(verbosity=1)
        self.assertEqual(0, result, 'Server should have found NO servers in the empty directory')
        mock_get.assert_called_once_with('server_directory')
        #mock_print.assert_called_with('Scanning for existing servers in', '/new/dir')
        self.assertEqual(2, mock_print.call_count, 'Print should have been called twice: once when beginning scan and once to recap')
    
    @patch('medusa.servers.forge.is_path_forge', return_value = True)
    @patch('builtins.print')
    @patch('medusa.servers.manager.register_server', return_value = 1)    
    def test_scan_removesDeletedServers(self, mock_register, mock_print, mock_is_forge):
        # Create two servers, but only keep 1 of them on disk
        srv_stays = Server()
        srv_stays.Path = '/srvs/creative1'
        srv_stays.Type = manager.ServerType.FORGE
        srv_delete = Server()
        srv_delete.Path = '/srvs/creative2'
        srv_delete.Type = manager.ServerType.FORGE
        self.fs.create_dir(srv_stays.Path)
        
        manager._servers = [srv_stays, srv_delete]
        result = manager.scan_directory_for_servers(scan_path='/srvs/', verbosity=1)
        mock_register.assert_called_once_with(srv_stays.Path, manager.ServerType.FORGE)
        mock_print.assert_called_with('Found 1 servers')
        self.assertEqual(1, result)
        
    def test_scan_skipsNonServers(self):
        self.fs.create_dir('/srvs/creative1')
        self.fs.create_file('/srvs/trickytricky')
        result = manager.scan_directory_for_servers(scan_path='/srvs/', verbosity=0)
        self.assertEqual(0, result)
        
    def test_getByIdentifier_returnsMatch(self):
        srv1 = Server()
        srv1.Path = '/path/to/gold'
        srv2 = Server()
        srv2.Path = '/not/the/answer'
        manager._servers = [srv1, srv2]
        result = manager.get_server_by_identifier(srv1.Path)
        self.assertEqual(srv1, result)
        
    def test_getByIdentifier_returnsNoneIfNoMatch(self):
        srv1 = Server()
        srv1.Path = '/path/to/gold'
        srv2 = Server()
        srv2.Path = '/not/the/answer'
        self.plant_server([srv1, srv2])
        result = manager.get_server_by_identifier('bruh')
        self.assertIsNone(result)
    
    @patch('medusa.servers.manager.get_server_by_identifier', return_value = None)
    def test_update_throwsIfUnknownServer(self, mock_getby):
        updated = Server()
        with self.assertRaises(KeyError) as kex:
            manager.update_server('no such thing', updated)
            self.assertEqual('No server "no such thing"', kex.exception.args[0])
    
    def test_update_writesChangesToMemory(self):
        srv1 = Server()
        srv1.Path = '/road/to/riches'
        srv2 = Server()
        srv2.Path = '/another/one'
        srv_updated = Server()
        srv_updated.Path = '/road/to/owning a home'
        self.plant_server([srv1, srv2])
        manager.update_server('/road/to/riches', srv_updated)
        self.assertIn(srv_updated, manager._servers)
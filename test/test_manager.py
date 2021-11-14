from os.path import join
import unittest
from unittest.mock import MagicMock, patch
from pyfakefs.fake_filesystem_unittest import TestCase

from medusa.servers import manager
from medusa.config import get_config_location

class ManagerTests(TestCase):
    VIR_PATH = 'D:\\Minecraft\\Servers'

    def setUp(self):
        self.setUpPyfakefs()


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
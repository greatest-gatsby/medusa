import pyfakefs
from pyfakefs.fake_filesystem_unittest import TestCase
from os.path import join
from unittest.mock import Mock, patch

from medusa.servers.models import Server, ServerController, ServerType
from medusa.servers.forge import ForgeController

class ServerControllerTests(TestCase):

    srv: Server = Server()
    control: ServerController
    VIR_PATH = 'D:\\Minecraft\\Servers'
    
    def setUp(self):
        self.setUpPyfakefs()

        self.srv.Path = self.VIR_PATH
        self.srv.Type = ServerType.FORGE
        self.control = ForgeController(self.srv)

    def test_startupScriptFinder_getsSingle(self):
        self.fs.create_file(join(self.VIR_PATH,'bait.bat'))
        self.fs.create_file(join(self.VIR_PATH,'run.bat'))
        self.fs.create_file(join(self.VIR_PATH,'run.sh'))
        self.fs.create_file(join(self.VIR_PATH,'serverstart.bat'))

        
        paths = self.control.find_startup_script_paths()
        assert len(paths) == 1
        assert paths[0] == 'serverstart.bat'

    def test_startupScriptFinder_getsMany(self):
        self.fs.create_file(join(self.VIR_PATH,'bait.bat'))
        self.fs.create_file(join(self.VIR_PATH,'startup.sh'))
        self.fs.create_file(join(self.VIR_PATH,'run.sh'))
        self.fs.create_file(join(self.VIR_PATH,'serverstart.bat'))
        
        paths = self.control.find_startup_script_paths()

        assert len(paths) == 2
        assert 'startup.sh' in paths
        assert 'serverstart.bat' in paths
    
    def test_startupScriptFinder_getsNone(self):
        self.fs.create_file(join(self.VIR_PATH, 'no.txt'))

        paths = self.control.find_startup_script_paths()

        assert len(paths) == 0

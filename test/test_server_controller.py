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

    
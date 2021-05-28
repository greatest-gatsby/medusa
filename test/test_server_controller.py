import argparse
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

    def test_parser_passthru(self):
        args = ['run','my-identifier', 'pass', 'op TargetPlayer']
        parsed = self.control.get_parser().parse_args(args)

        assert parsed.identifier == 'my-identifier'
        assert parsed.action == 'pass'
        assert parsed.command == 'op TargetPlayer'

    def test_parser_start(self):
        args = ['run', 'de ayedee', 'start']
        parsed = self.control.get_parser().parse_args(args)

        assert parsed.identifier == 'de ayedee'
        assert parsed.action == 'start'

    def test_parser_stop(self):
        args = ['run', 'wheres waldo', 'stop']
        parsed = self.control.get_parser().parse_args(args)

        assert parsed.identifier == 'wheres waldo'
        assert parsed.action == 'stop'

    def test_parser_restart(self):
        args = ['run', 'look at my head', 'restart']
        parsed = self.control.get_parser().parse_args(args)

        assert parsed.identifier == 'look at my head'
        assert parsed.action == 'restart'

        
        

    
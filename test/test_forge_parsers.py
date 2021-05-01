import argparse

from unittest import TestCase
from unittest.mock import Mock

from medusa.servers import forge
from medusa.servers import models

class ForgeParserTests(TestCase):
    forge_srv = models.Server
    forge_srv.Alias = 'Test Alias'
    forge_srv.Path = '/srv/test dir/mc'
    forge_srv.Type = models.ServerType.FORGE
    forge_control = forge.ForgeController(forge_srv)

    def test_forge_run(self):
        args = ['run', 'my glorious identifier', 'command here --fake-opt']
        parser = self.forge_control.get_parser()
        proc = parser.parse_args(args)

        assert proc.identifier == 'my glorious identifier'
        assert proc.command == ['command here --fake-opt']
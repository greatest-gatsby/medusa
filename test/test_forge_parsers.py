import argparse

from unittest import TestCase
from unittest.mock import Mock

from medusa.servers import forge, models, FORGE

class ForgeParserTests(TestCase):
    forge_srv = models.Server
    forge_srv.Alias = 'Test Alias'
    forge_srv.Path = '/srv/test dir/mc'
    forge_srv.Type = FORGE
    forge_control = forge.ForgeController(forge_srv)

    def test_forge_run_start(self):
        args = ['run', 'start']
        parser = self.forge_control.get_parser()
        proc = parser.parse_args(args)

        assert proc.action == 'start'
    
    def test_forge_run_pass(self):
        args = ['run', 'pass', 'op TheDude']
        parser = self.forge_control.get_parser()
        proc = parser.parse_args(args)

        assert proc.action == 'pass'
        assert proc.command == 'op TheDude'
        
    def test_forge_run_stop(self):
        args = ['run', 'stop']
        parser = self.forge_control.get_parser()
        proc = parser.parse_args(args)
        
        assert proc.action == 'stop'
        
    def test_forge_run_restart(self):
        args = ['run', 'restart']
        parser = self.forge_control.get_parser()
        proc = parser.parse_args(args)
        
        assert proc.action == 'restart'
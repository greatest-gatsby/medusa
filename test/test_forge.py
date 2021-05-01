from unittest import TestCase

from medusa.servers import forge
from medusa.servers import models

class ForgeTests(TestCase):
    def test_forge_init_wrongTypeThrows(self):
        srv = models.Server()
        srv.Alias = 'MR BOND'
        srv.Path = '/media/pron/trucks'
        srv.Type = models.ServerType.NOTASERVER
        
        with self.assertRaises(TypeError):
            forge.ForgeController(srv)

    def test_forge_init_rightType(self):
        srv = models.Server()
        srv.Alias = 'All The Mods Again'
        srv.Path = 'C:\\Windows\\Legit\\big wooden horse\\atm6'
        srv.Type = models.ServerType.FORGE

        control = forge.ForgeController(srv)

        assert control.info.Alias == 'All The Mods Again'
        assert control.info.Path == 'C:\\Windows\\Legit\\big wooden horse\\atm6'
        assert control.info.Type == models.ServerType.FORGE
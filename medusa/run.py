from medusa.servers.forge import ForgeController
from . import parsers
from . import servers
from .servers import FORGE, manager

def process_run(args):
    """
    Process CLI arguments for `run` command. This method should really
    only be called from the main parsing logic; it provides verbose, human-friendly
    access to methods that can be more easily invoked programatically.

    The most significant component of this method is the generation of
    a `ServerController` object for the named server. The desired command
    is handled within the ServerController.
    """
    parser = parsers.get_run_parsers()
    args = parser.parse_args(args)
    srv = manager.get_server_by_identifier(args.identifier)

    if srv is None:
        print('No server "{}"'.format(args.identifier))
        return
    else:
        if srv.Type == FORGE:
            controller = ForgeController(srv)
            
        else:
            print('No controller available for', srv.Type)
            return

    pass
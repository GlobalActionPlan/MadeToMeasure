import optparse
import sys
import textwrap

from pyramid.paster import bootstrap
from repoze.evolution import ZODBEvolutionManager
from repoze.evolution import evolve_to_latest


VERSION = 1


def run_evolve(*args):
    description = """\
    Run evolve script(s) to make changes to the database when the application is upgraded.  Example:
    'evolve development.ini'
    """
    usage = "usage: %prog config_uri"
    parser = optparse.OptionParser(
        usage=usage,
        description=textwrap.dedent(description)
        )
    options, args = parser.parse_args(sys.argv[1:])
    if not len(args) >= 1:
        print('You must provide at least one argument')
        return 2
    config_uri = args[0]
    env = bootstrap(config_uri)
    root = env['root']
    try:
        manager = ZODBEvolutionManager(root, evolve_packagename = 'madetomeasure.evolve',
                                       sw_version = VERSION,
                                       initial_db_version = 0)
        ver = manager.get_db_version()
        if ver < VERSION:
            evolve_to_latest(manager)
            print 'Evolved from %s to %s' % (ver, manager.get_db_version())
        else:
            print 'Already evolved to latest version'
    finally:
        env['closer']

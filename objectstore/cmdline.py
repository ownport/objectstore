# system modules
import sys
import inspect
import argparse


from command import Command
from pkgutil import iter_modules

def execute(argv=None):

    if argv is None:
        argv = sys.argv

    cmds = _get_commands_from_module('commands')
    argv, cmdname = _pop_command_name(argv)
    parser = argparse.ArgumentParser()
    
    if not cmdname:
        _print_commands(cmds)
        sys.exit(0)
    elif cmdname not in cmds:
        _print_unknown_command(cmdname)
        sys.exit(2)

    cmd = cmds[cmdname]
    parser.usage = "objectstore %s %s" % (cmdname, cmd.syntax())
    parser.description = cmd.long_desc()
    cmd.add_options(parser)

    if argv:
        args = parser.parse_args(args=argv)
    else:
        args = parser.parse_args(args=['--help'])
    
    _run_print_help(parser, cmd.process_options, args)
    _run_print_help(parser, cmd.run)
    sys.exit(cmd.exitcode)
    

def _get_commands_from_module(module):
    ''' returns commands for module
    '''
    return dict([(cmd.__module__.split('.')[-1], cmd()) \
                for cmd in _iter_command_classes(module)])


def _iter_command_classes(module_name):

    for module in walk_modules(module_name):
        for obj in vars(module).itervalues():
            if inspect.isclass(obj) and issubclass(obj, Command) and \
               obj.__module__ == module.__name__:
                yield obj

    
def walk_modules(path, load=False):
    """Loads a module and all its submodules from a the given module path and
    returns them. If *any* module throws an exception while importing, that
    exception is thrown back.

    For example: walk_modules('scrapy.utils')
    """

    mods = []
    mod = __import__(path, {}, {}, [''])
    mods.append(mod)
    if hasattr(mod, '__path__'):
        for _, subpath, ispkg in iter_modules(mod.__path__):
            fullpath = path + '.' + subpath
            if ispkg:
                mods += walk_modules(fullpath)
            else:
                submod = __import__(fullpath, {}, {}, [''])
                mods.append(submod)
    return mods


def _pop_command_name(argv):

    if len(argv) > 1:
        argv = argv[1:]
        cmdname = argv.pop(0) if not argv[0].startswith('-') else None
        return argv, cmdname
    return (argv, None)


def _print_commands(cmds):

    print "Usage:"
    print "  objectstore <command> [options] [args]\n"
    print "Available commands:"
    for cmdname, cmdclass in sorted(cmds.iteritems()):
        print "  %-13s %s" % (cmdname, cmdclass.short_desc())
    print
    print 'Use "objectstore <command> -h" to see more info about a command'


def _print_unknown_command(cmdname):
    print "Unknown command: %s\n" % cmdname
    print 'Use "objectstore" to see available commands'


def _run_print_help(parser, func, *a):

    try:
        func(*a)
    except RuntimeError as e:
        if str(e):
            parser.error(str(e))
        if e.print_help:
            parser.print_help()
        sys.exit(2)
            

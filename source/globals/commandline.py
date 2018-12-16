# -*- coding: utf-8 -*-

## \package globals.commandline
#
#  Retrieves the FFmpeg executable

# MIT licensing
# See: LICENSE.txt


import sys


args = ()

if len(sys.argv) > 1:
    args = tuple(sys.argv[1:])


## Retrieves the command, if any, passed to the command line
def GetCommandArg():
    if args and not args[0].startswith(u'-'):
        return args[0]

    return None


## TODO: Doxygen
def GetOption(option):
    opt_index = None
    for A in args:
        if A.startswith(u'-') and A.lstrip(u'-') == option:
            opt_index = args.index(A)

    if opt_index == None:
        return False

    if len(args) > opt_index+1 and not args[opt_index+1].startswith(u'-'):
        value = unicode(args[opt_index+1])
        if value.isnumeric():
            value = int(value)

        return value

    return True

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

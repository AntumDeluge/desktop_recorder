# -*- coding: utf-8 -*-

## \package globals.cmds
#  
#  Retrieves & defines paths to commands that this app uses

# MIT licensing
# See: LICENSE.txt


import os
from subprocess     import PIPE
from subprocess     import Popen
from subprocess     import STDOUT

from globals.debug  import pDebug


def GetCMD(cmdname):
    output, returncode = Popen((u'which', cmdname,), stdout=PIPE, stderr=STDOUT).communicate()
    
    # NOTE: Not sure why '\n' is appended from Popen command
    output = output.strip(u'\n')
    if not returncode and os.access(output, os.X_OK):
        return output
    
    pDebug(u'Failed to find command: {}'.format(cmdname))

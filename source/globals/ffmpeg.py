# -*- coding: utf-8 -*-

## \package globals.ffmpeg
#  
#  Retrieves the FFmpeg executable

# MIT licensing
# See: LICENSE.txt


import subprocess
from subprocess import PIPE
from subprocess import STDOUT


## Locates an executable
#  
#  \param cmd
#    \b \e unicode|str : Name of the executable to search for
#  \return
#    \b \e unicode|str : Absolute path to executable or None if not found
def GetExecutable(cmd):
    output, returncode  = subprocess.Popen([u'which', cmd,], stdout=PIPE, stderr=STDOUT).communicate()
    
    if returncode:
        return None
    
    return output


CMD_ffmpeg = GetExecutable(u'ffmpeg')


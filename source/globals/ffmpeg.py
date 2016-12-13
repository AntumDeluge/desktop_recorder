# -*- coding: utf-8 -*-

## \package globals.ffmpeg
#  
#  Retrieves the FFmpeg executable

# MIT licensing
# See: LICENSE.txt


import subprocess
from subprocess import PIPE
from subprocess import STDOUT


def GetExecutable(cmd):
    sp = subprocess.Popen([u'which', cmd,], stdout=PIPE, stderr=STDOUT)
    output, returncode = sp.communicate()
    
    print(u'Return code: {}\nSTDOUT: {}'.format(returncode, output))
    
    if returncode:
        return None
    
    return output


CMD_ffmpeg = GetExecutable(u'ffmpeg')


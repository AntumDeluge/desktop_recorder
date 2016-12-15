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


# --- Check to see if ffmpeg supports xvid and x264
no_xvid = subprocess.call(u'{} -codecs | grep -i "libxvid"'.format(CMD_ffmpeg), stdout=PIPE, stderr=PIPE, shell=True)
if no_xvid:
    no_xvid = subprocess.call(u'{} -formats | grep -i "libxvid"'.format(CMD_ffmpeg), stdout=PIPE, stderr=PIPE, shell=True)

no_x264 = subprocess.call(u'{} -codecs | grep -i "libx264"'.format(CMD_ffmpeg), stdout=PIPE, stderr=PIPE, shell=True)
if no_x264:
    no_x264 = subprocess.call(u'{} -formats | grep -i "libx264"'.format(CMD_ffmpeg), stdout=PIPE, stderr=PIPE, shell=True)

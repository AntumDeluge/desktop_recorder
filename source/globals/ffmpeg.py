# -*- coding: utf-8 -*-

## \package globals.ffmpeg
#  
#  Retrieves the FFmpeg executable

# MIT licensing
# See: LICENSE.txt


import subprocess
from subprocess import PIPE
from subprocess import STDOUT

from globals.system import PY_VER_MAJ


## Locates an executable
#  
#  \param cmd
#    \b \e unicode|str : Name of the executable to search for
#  \return
#    \b \e unicode|str : Absolute path to executable or None if not found
def GetExecutable(cmd):
    output, returncode = subprocess.Popen((u'which', cmd,), stdout=PIPE, stderr=STDOUT).communicate()
    
    # FIXME: subprocess is adding newline at end of output
    output = output.rstrip(u'\n')
    
    if returncode:
        return None
    
    if PY_VER_MAJ < 3:
        output = unicode(output)
    
    return output


CMD_ffmpeg = GetExecutable(u'ffmpeg')


# --- Check to see if ffmpeg supports xvid and x264
no_xvid = subprocess.call(u'{} -codecs | grep -i "libxvid"'.format(CMD_ffmpeg), stdout=PIPE, stderr=PIPE, shell=True)
if no_xvid:
    no_xvid = subprocess.call(u'{} -formats | grep -i "libxvid"'.format(CMD_ffmpeg), stdout=PIPE, stderr=PIPE, shell=True)

no_x264 = subprocess.call(u'{} -codecs | grep -i "libx264"'.format(CMD_ffmpeg), stdout=PIPE, stderr=PIPE, shell=True)
if no_x264:
    no_x264 = subprocess.call(u'{} -formats | grep -i "libx264"'.format(CMD_ffmpeg), stdout=PIPE, stderr=PIPE, shell=True)


## Retrieves a list of usable codecs from FFmpeg
def GetCodecs():
    if CMD_ffmpeg:
        output, returncode = subprocess.Popen((CMD_ffmpeg, u'-encoders',), stdout=PIPE, stderr=STDOUT).communicate()
        
        if returncode:
            print(u'Error: Could not get codec list')
            return None
        
        output = output.strip(u' \t\n').split(u'\n')
        
        vcodecs = []
        acodecs = []
        for LI in reversed(output):
            # Reached end of encoder list
            if LI.strip() == u'------':
                break
            
            codec = LI.split(u' ')[1:3]
            codec_type = codec[0][0]
            codec = codec[1]
            
            if codec_type == u'V':
                vcodecs.append(codec)
            
            elif codec_type == u'A':
                acodecs.append(codec)
        
        codecs = {}
        
        if vcodecs:
            codecs[u'video'] = tuple(sorted(vcodecs))
        
        if acodecs:
            codecs[u'audio'] = tuple(sorted(acodecs))
        
        return codecs
    
    print(u'Error: Cannot find ffmpeg executable')

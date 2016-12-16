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


## Retrieves a list of input devices
def GetFFmpegList(switch, t_filter=None, t_index=0):
    if not CMD_ffmpeg:
        print(u'Error: Cannot find ffmpeg executable')
        
        return
    
    output, returncode = subprocess.Popen((CMD_ffmpeg, u'-{}'.format(switch),), stdout=PIPE, stderr=STDOUT).communicate()
    
    if returncode:
        print(u'Error: Could not get list for option "-{}"'.format(switch))
        return
    
    output = output.strip().split(u'\n')
    
    output_list = []
    for LI in reversed(output):
        LI = LI.strip()
        
        if LI[:2] == u'--':
            break
        
        LI = LI.split()[:2]
        
        if u',' in LI[1]:
            LI[1] = LI[1].split(u',')[0]
        
        if t_filter:
            if LI[t_index] == t_filter:
                output_list.append(LI[1])
            
            continue
        
        output_list.append(LI)
    
    return tuple(sorted(output_list))


## Get a list of containers available for file output
def GetContainers():
    containers = GetFFmpegList(u'formats', u'E')
    
    return containers


## Retrieves a list of usable encoders from FFmpeg
def GetEncoders():
    #codecs = GetFFmpegList(u'encoders', codec_type[0].upper())
    codec_list = GetFFmpegList(u'encoders')
    
    v_codecs = []
    a_codecs = []
    for C in codec_list:
        codec_type = C[0][0]
        codec = C[1]
        
        if codec_type == u'V':
            v_codecs.append(codec)
        
        elif codec_type == u'A':
            a_codecs.append(codec)
    
    return {u'video': tuple(sorted(v_codecs)), u'audio': tuple(sorted(a_codecs))}


## Get a list of available input devices
def GetInputDevices():
    devices = GetFFmpegList(u'devices', u'D')
    
    return devices


def GetInputDevicesOld():
    devices = GetFFmpegList(u'devices')
    
    device_list = []
    for D in devices:
        if u'D' in D[0]:
            device_list.append(D[1])
    
    return tuple(sorted(device_list))

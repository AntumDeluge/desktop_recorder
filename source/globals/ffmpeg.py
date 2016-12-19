# -*- coding: utf-8 -*-

## \package globals.ffmpeg
#  
#  Retrieves the FFmpeg executable

# MIT licensing
# See: LICENSE.txt


import subprocess
from subprocess import PIPE
from subprocess import STDOUT

from globals.cmds import GetCMD


CMD_ffmpeg = GetCMD(u'ffmpeg')


# --- Check to see if ffmpeg supports xvid and x264
no_xvid = subprocess.call(u'{} -codecs | grep -i "libxvid"'.format(CMD_ffmpeg), stdout=PIPE, stderr=PIPE, shell=True)
if no_xvid:
    no_xvid = subprocess.call(u'{} -formats | grep -i "libxvid"'.format(CMD_ffmpeg), stdout=PIPE, stderr=PIPE, shell=True)

no_x264 = subprocess.call(u'{} -codecs | grep -i "libx264"'.format(CMD_ffmpeg), stdout=PIPE, stderr=PIPE, shell=True)
if no_x264:
    no_x264 = subprocess.call(u'{} -formats | grep -i "libx264"'.format(CMD_ffmpeg), stdout=PIPE, stderr=PIPE, shell=True)


## Retrieves a list of input devices
def GetFFmpegList(switch, t_filter=None, t_index=None, description=False):
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
        
        if description:
            LI = LI.split()
            
            s_types = LI[0]
            s_name = LI[1]
            s_desc = u' '.join(LI[2:])
            
            if u',' in s_name:
                s_name = s_name.split(u',')[0]
            
            if t_filter and t_filter in s_types:
                output_list.append((s_name, s_desc))
                
                continue
            
            output_list.append((s_name, s_desc,))
            
            continue
        
        LI = LI.split()[:2]
        
        if u',' in LI[1]:
            LI[1] = LI[1].split(u',')[0]
        
        if t_filter:
            if t_index == None:
                if t_filter in LI[0]:
                    output_list.append(LI[1])
            
            else:
                if LI[t_index] == t_filter:
                    output_list.append(LI[1])
            
            continue
        
        output_list.append(LI)
    
    return tuple(sorted(output_list))


## Get a list of containers available for file output
def GetContainers():
    mpeg_formats = (
        u'mpeg',
        u'mpeg1video',
        u'mpeg2video',
        u'mpegts',
        u'mpegtsraw',
        u'mpegvideo',
        )
    containers = list(GetFFmpegList(u'formats', u'E'))
    
    if u'mpg' not in containers:
        for MPG in mpeg_formats:
            if MPG in containers:
                containers.append(u'mpg')
                break
    
    return tuple(sorted(containers))


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
    devices = GetFFmpegList(u'devices', u'D', description=True)
    
    v_keywords = (u'video', u'a/v', u'dv', u'sdl', u'x11', u'screen',)
    a_keywords = (u'audio', u'a/v', u'sound', u'sdl',)
    
    v_devices = []
    v_defs = []
    a_devices = []
    a_defs = []
    
    for D, DEF in sorted(devices):
        for V in v_keywords:
            if V in DEF.lower():
                v_devices.append(D)
                v_defs.append(DEF)
                break
        
        for A in a_keywords:
            if A in DEF.lower():
                a_devices.append(D)
                a_defs.append(DEF)
                break
    
    devices = {
        u'video': (tuple(v_devices), tuple(v_defs)),
        u'audio': (tuple(a_devices), tuple(a_defs)),
        }
    
    return devices

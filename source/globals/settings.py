# -*- coding: utf-8 -*-

## \package globals.settings
#  
#  Retrieves the FFmpeg executable

# MIT licensing
# See: LICENSE.txt


import os

from globals.paths import PATH_root


FILE_settings = u'{}/settings'.format(PATH_root)

def GetAppInfo(key_search):
    if not os.path.isfile(FILE_settings):
        print(u'Warning: App settings file does not exists: {}'.format(FILE_settings))
        return None
    
    FILE_BUFFER = open(FILE_settings)
    info_lines = FILE_BUFFER.read().split(u'\n')
    FILE_BUFFER.close()
    
    for LI in info_lines:
        # Ignore empty lines & lines that begin with a hashtag
        if LI and not LI.startswith(u'#'):
            if u'=' in LI:
                # Only split on first '='
                split_index = LI.index(u'=')
                key = LI[:split_index].rstrip()
                value = LI[split_index+1:].lstrip()
                
                if key == key_search:
                    return value


APP_version_string = GetAppInfo(u'VERSION')

APP_version = []
APP_version_maj = None
APP_version_min = None
APP_version_rel = None
APP_version_dev = None

# Setting up integer app version
if u'.' in APP_version_string:
    for V in APP_version_string.split(u'.'):
        if V.isnumeric():
            APP_version.append(int(V))
            continue
        
        APP_version.append(V)

elif APP_version_string.isnumeric():
    APP_version.append(int(APP_version_string))

APP_version = tuple(APP_version)
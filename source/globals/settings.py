# -*- coding: utf-8 -*-

## \package globals.settings
#  
#  Retrieves the FFmpeg executable

# MIT licensing
# See: LICENSE.txt


import os, sys

from globals       import ident as ID
from globals.files import ReadFile
from globals.paths import PATH_root


EXE_name = None

FILE_settings = u'{}/settings'.format(PATH_root)

# Settings file is required
if not os.path.isfile(FILE_settings):
    print(u'Error: App settings file does not exists: {}'.format(FILE_settings))
    sys.exit(1)


## Retrieves installed status of application
#  
#  0:           Running from source
#  ID.PORTABLE: Running portably
#  ID.SYSTEM:   Installed to system
def GetInstalledStatus():
    status_file = ReadFile(u'STATUS')
    
    if not status_file:
        return 0
    
    # First line determines installed status
    status = status_file[0].upper()
    
    if status.startswith(u'SYSTEM'):
        return ID.SYSTEM
    
    if status.startswith(u'PORTABLE'):
        return ID.PORTABLE
    
    return 0


## Reads the settings file
#  
#  \param key_search
#    \b \e string : Key to search for
#  \return
#    \b \e string : Value of key if found
def GetSetting(key_search):
    info_lines = ReadFile(FILE_settings)
    
    if not info_lines:
        return None
    
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


APP_name = GetSetting(u'NAME')
APP_version_string = GetSetting(u'VERSION')

APP_version = []
APP_version_maj = None
APP_version_min = None
APP_version_rel = None
APP_version_dev = None

# Setting up integer app version
if APP_version_string:
    if u'.' in APP_version_string:
        for V in APP_version_string.split(u'.'):
            if V.isnumeric():
                APP_version.append(int(V))
                continue
            
            APP_version.append(V)
    
    elif APP_version_string.isnumeric():
        APP_version.append(int(APP_version_string))
    
    APP_version = tuple(APP_version)

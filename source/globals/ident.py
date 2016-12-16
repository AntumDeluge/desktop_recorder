# -*- coding: utf-8 -*-

## \package globals.ident

# MIT licensing
# See: LICENSE.txt


# NOTE: Do not import wx here unless init script is modified to call wxversion.select sooner


next_id = 2500

def NewId():
    global next_id
    
    new_id = next_id
    next_id += 1
    
    return new_id
    


ABOUT = NewId()
EXIT = NewId()
OPT = NewId()
PAUSE = NewId()
REC = NewId()
STOP = NewId()

AUDIO = NewId()
VIDEO = NewId()

# Installed status
SYSTEM = NewId()
PORTABLE = NewId()

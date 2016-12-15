# -*- coding: utf-8 -*-

## \package globals.lock

# MIT licensing
# See: LICENSE.txt


import os

from globals.paths import FILE_lock


## Checks if app is locked
def AppIsLocked():
    return os.path.exists(FILE_lock)


## Locks the app so not other instances may be started
def LockApp():
    if AppIsLocked():
        return False
    
    FILE_BUFFER = open(FILE_lock, u'w')
    FILE_BUFFER.close()
    
    return AppIsLocked()


## Unlocks the app for future instances to be invoked
def UnlockApp():
    if not AppIsLocked():
        return False
    
    os.remove(FILE_lock)
    
    return not AppIsLocked()

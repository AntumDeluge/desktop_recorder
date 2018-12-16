# -*- coding: utf-8 -*-

## \package globals.lock

# MIT licensing
# See: LICENSE.txt


import os

from globals.files import FILE_lock
from globals.files import WriteEmptyFile


## Checks if app is locked
def AppIsLocked():
    return os.path.exists(FILE_lock)


## Locks the app so not other instances may be started
def LockApp():
    if AppIsLocked():
        return False

    if not WriteEmptyFile(FILE_lock):
        return False

    return AppIsLocked()


## Unlocks the app for future instances to be invoked
def UnlockApp():
    if not AppIsLocked():
        return False

    os.remove(FILE_lock)

    return not AppIsLocked()

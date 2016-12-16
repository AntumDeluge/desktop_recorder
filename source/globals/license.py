# -*- coding: utf-8 -*-

## \package globals.license

# MIT licensing
# See: LICENSE.txt


import os

from globals            import ident as ID
from globals.files      import ReadFile
from globals.paths      import PATH_root
from globals.settings   import GetInstalledStatus


FILE_license = None

status = GetInstalledStatus()

# LICENSE.txt is located in parent source directory
if not status:
    FILE_license = u'{}/LICENSE.txt'.format(os.path.dirname(PATH_root))

# LICENSE.txt is located in app's 'doc' directory
if status == ID.PORTABLE:
    FILE_license = u'{}/doc/LICENSE.txt'.format(PATH_root)

# LICENSE.txt is located in system doc directory
if status == ID.SYSTEM:
    # TODO:
    pass

# Free up memory
del status


## Retrieves text from license file
def GetLicenseText():
    # Do not split license text into list
    return ReadFile(FILE_license, False)

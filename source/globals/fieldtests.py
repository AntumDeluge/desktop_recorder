# -*- coding: utf-8 -*-

## \package globals.fieldtests

# MIT licensing
# See: LICENSE.txt


import wx


## Tests if a wx control/instance is enabled
#  
#  Function for compatibility between wx versions
def FieldEnabled(field):
    if wx.MAJOR_VERSION > 2:
        return field.IsThisEnabled()
    
    else:
        return field.IsEnabled()

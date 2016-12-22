# -*- coding: utf-8 -*-

## \package globals.fieldtests

# MIT licensing
# See: LICENSE.txt


import wx


## Tests if a wx control/instance is enabled
#  
#  Function for compatibility between wx versions
#  \param enabled
#    \b \e bool : Check if enabled or disabled
def FieldEnabled(field, enabled=True):
    if wx.MAJOR_VERSION > 2:
        return field.IsThisEnabled() == enabled
    
    else:
        return field.IsEnabled() == enabled


## Tests multiple fields
#  
#  \return
#    \b \e bool : True if all fields are enabled
def FieldsEnabled(field_list):
    if isinstance(field_list, (tuple, list)):
        return FieldEnabled(field_list)
    
    for F in field_list:
        if not FieldEnabled(F):
            return False
    
    return True

# -*- coding: utf-8 -*-

## \package globals.fieldtests

# MIT licensing
# See: LICENSE.txt


import wx


## Tests if a wx control/instance is enabled/disabled
#  
#  Function for compatibility between wx versions
#  \param field
#    \b \e wx.Window : the wx control to check
#  \param enabled
#    \b \e bool : Check if enabled or disabled
#  \return
#    \b \e bool : True if field's enabled status is same as 'enabled'
def FieldEnabled(field, enabled=True):
    if wx.MAJOR_VERSION > 2:
        return field.IsThisEnabled() == enabled
    
    else:
        return field.IsEnabled() == enabled


## Tests if a wx control/instance is disabled
#  
#  \param field
#    \b \e wx.Window : The wx field to check
#  \return
#    \b \e : True if field is disabled
def FieldDisabled(field):
    return FieldEnabled(field, False)


## Tests multiple fields
#
#  \param field_list
#    \b \e tuple|list : List of wx control to be checked
#  \param enabled
#    \b \e bool : Status to check for (True=enabled, False=disabled)
#  \return
#    \b \e bool : True if all fields are enabled
def FieldsEnabled(field_list, enabled=True):
    if not isinstance(field_list, (tuple, list)):
        return FieldEnabled(field_list, enabled)
    
    for F in field_list:
        if not FieldEnabled(F, enabled):
            return False
    
    return True

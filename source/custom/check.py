# -*- coding: utf-8 -*-

## \package custom.check

# MIT licensing
# See: LICENSE.txt


import wx


## wx.CheckBox class that defines a 'Default' attribute
class CheckBox(wx.CheckBox):
    def __init__(self, parent, win_id=wx.ID_ANY, value=False, label=wx.EmptyString, pos=wx.DefaultPosition,
            size=wx.DefaultSize, style=0, validator=wx.DefaultValidator, name=wx.CheckBoxNameStr):
        wx.CheckBox.__init__(self, parent, win_id, label, pos, size, style, validator, name)
        
        self.SetValue(value)
        
        self.Default = value

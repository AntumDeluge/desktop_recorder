# -*- coding: utf-8 -*-

## \package custom.textinput

# MIT licensing
# See: LICENSE.txt


import wx


## wx.TextCtrl derived class that sets 'Default' attribute & 'Reset' method
class TextCtrl(wx.TextCtrl):
    def __init__(self, parent, win_id=wx.ID_ANY, value=wx.EmptyString, pos=wx.DefaultPosition,
            size=wx.DefaultSize, style=0, validator=wx.DefaultValidator, name=wx.TextCtrlNameStr):
        wx.TextCtrl.__init__(self, parent, win_id, value, pos, size, style, validator, name)
        
        self.Default = value
    
    
    ## TODO: Doxygen
    def Reset(self):
        self.SetValue(self.Default)
        
        return self.Value == self.Default

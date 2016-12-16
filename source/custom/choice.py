# -*- coding: utf-8 -*-

## \package custom.choice

# MIT licensing
# See: LICENSE.txt


import wx


## A wx.Choice class that is compatible with older wx versions
class Choice(wx.Choice):
    def __init__(self, parent, window_id=wx.ID_ANY, pos=wx.DefaultPosition, size=wx.DefaultSize,
            choices=[], style=0, validator=wx.DefaultValidator, name=wx.ChoiceNameStr):
        wx.Choice.__init__(self, parent, window_id, pos, size, choices, style, validator, name)
    
    
    ## Set method compatible for older wx versions
    def Set(self, *args, **kwargs):
        if wx.MAJOR_VERSION > 2:
            return wx.Choice.Set(self, *args, **kwargs)
        
        choices = args[0]
        
        # Clear old options first
        self.Clear()
        for C in choices:
            self.Append(C)

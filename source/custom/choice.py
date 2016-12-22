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
    
    
    ## Appends an item to the end of options
    #  
    #  \override wx.Choice.Append
    def Append(self, item):
        appended = wx.Choice.Append(self, item)
        
        if wx.MAJOR_VERSION <= 2:
            if not self.IsEnabled() and self.GetCount():
                self.Enable(True)
        
        return appended
    
    
    ## Disabled control when empty for older wx versions
    def Clear(self):
        cleared = wx.Choice.Clear(self)
        
        if wx.MAJOR_VERSION <= 2:
            if not self.GetCount():
                self.Enable(False)
            
            else:
                self.Enable(True)
        
        return cleared
    
    
    def Enable(self, enable=True):
        if wx.MAJOR_VERSION <= 2:
            # HACK: Bypass wx 2.8 call to Enable(True) when app is constructed
            if not self.GetCount():
                enable = False
        
        return wx.Choice.Enable(self, enable)
    
    
    ## Sets choices available wx.Choice instances
    #  
    #  \override wx.Choice.Set
    #    Causes wx 2.8 to behave like 3, disables control if empty
    def Set(self, choices):
        if wx.MAJOR_VERSION > 2:
            return wx.Choice.Set(self, choices)
        
        # Clear old options first (& disables field in wx 2.8)
        self.Clear()
        for C in choices:
            self.Append(C)

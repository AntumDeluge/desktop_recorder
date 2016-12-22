# -*- coding: utf-8 -*-

## \package custom.choice

# MIT licensing
# See: LICENSE.txt


import traceback, wx


## A wx.Choice class that is compatible with older wx versions
class Choice(wx.Choice):
    def __init__(self, parent, window_id=wx.ID_ANY, pos=wx.DefaultPosition, size=wx.DefaultSize,
            choices=[], style=0, validator=wx.DefaultValidator, name=wx.ChoiceNameStr):
        wx.Choice.__init__(self, parent, window_id, pos, size, choices, style, validator, name)
        
        self.DefaultIndex = 0
        self.Default = self.DefaultIndex
        self.Priority = []
    
    
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
            if not self.Count:
                self.Enable(False)
            
            else:
                self.Enable(True)
        
        return cleared
    
    
    def Enable(self, enable=True):
        if wx.MAJOR_VERSION <= 2:
            # HACK: Bypass wx 2.8 call to Enable(True) when app is constructed
            if not self.Count:
                enable = False
        
        return wx.Choice.Enable(self, enable)
    
    
    ## Resets the field with the priority list or default attribute
    def Reset(self):
        if not self.Count:
            return False
        
        for O in self.Priority:
            if type(O) == int:
                O = unicode(O)
            
            if O in self.Strings:
                return self.SetStringSelection(O)
        
        if self.DefaultIndex <= self.Count:
            return self.SetSelection(self.DefaultIndex)
        
        return False
        
        
    
    
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
    
    
    ## Overrides default behavior to reset to default in case of error
    #  
    #  FIXME: How to get object instance in traceback???
    def SetSelection(self, index):
        try:
            wx.Choice.SetSelection(self, index)
            
            return self.Selection == index
        
        except:
            print(u'\nWARNING:\n    Error when attempting to call {}.SetSelection.\n    Setting default selection.\n    Error output below:\n'.format(__name__))
            print(traceback.format_exc())
            
            if self.Count:
                wx.Choice.SetSelection(self.DefaultIndex)
        
        return False

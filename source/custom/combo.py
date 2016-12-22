# -*- coding: utf-8 -*-

## \package custom.combo

# MIT licensing
# See: LICENSE.txt


import wx
from wx.combo import OwnerDrawnComboBox


class ComboBox(OwnerDrawnComboBox):
    def __init__(self, parent, win_id=wx.ID_ANY, value=wx.EmptyString, pos=wx.DefaultPosition,
            size=wx.DefaultSize, choices=[], style=0, validator=wx.DefaultValidator,
            name=wx.ComboBoxNameStr):
        OwnerDrawnComboBox.__init__(self, parent, win_id, value, pos, size, choices,
                style, validator, name)
        
        self.Default = self.GetLabel()
        self.Priority = []
    
    
    ## Resets ComboBox to defaults
    def Reset(self):
        if not self.Count:
            self.SetValue(self.Default)
            return self.Value == self.Default
        
        return False

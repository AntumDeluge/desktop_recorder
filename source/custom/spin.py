# -*- coding: utf-8 -*-

## \package custom.spin

# MIT licensing
# See: LICENSE.txt


import wx


## Custom wx.SpinCtrl class that sets 'Default' attribute & 'Reset' method
class SpinCtrl(wx.SpinCtrl):
    def __init__(self, parent, win_id=wx.ID_ANY, value=wx.EmptyString, pos=wx.DefaultPosition,
            size=wx.DefaultSize, style=wx.SP_ARROW_KEYS, sp_min=0, sp_max=100, sp_initial=0,
            name=wx.SpinCtrlNameStr):
        
        wx.SpinCtrl.__init__(self, parent, win_id, value, pos, size, style, sp_min, sp_max,
                sp_initial, name)
        
        self.Default = sp_initial
        
    
    ## TODO: Doxygen
    def Reset(self):
        self.SetValue(self.Default)
        
        return self.Value == self.Default

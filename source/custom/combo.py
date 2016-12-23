# -*- coding: utf-8 -*-

## \package custom.combo

# MIT licensing
# See: LICENSE.txt


import wx
from wx.combo import OwnerDrawnComboBox

from custom.toggle      import ToggleArrow
from globals.fieldtests import FieldsEnabled


## Custom ComboBox class where Button & TextCtrl can be disabled
class ComboBoxNew(wx.BoxSizer):
    def __init__(self, parent, name=u'ComboBox'):
        wx.BoxSizer.__init__(self, wx.VERTICAL)
        
        self.Parent = parent
        
        self.Name = name
        
        self.TextCtrl = wx.TextCtrl(parent)
        
        self.ListBox = wx.ListBox(parent.GetParent(), style=wx.LB_SINGLE|wx.LB_ALWAYS_SB|wx.BORDER_THEME)
        
        # FIXME: Find how to attach posted event to custom.toggle.ToggleArrow
        self.ToggleArrow = ToggleArrow(parent, self.ListBox)
        
        # *** Event Handlers *** #
        
        parent.Bind(wx.EVT_TOGGLEBUTTON, self.OnToggleArrow)
        
        # wx.Panel doesn't take focus when clicked in wx 3.0
        if wx.MAJOR_VERSION > 2:
            parent.Bind(wx.EVT_LEFT_DOWN, self.OnClickPanel)
        
        self.ListBox.Bind(wx.EVT_LEFT_DOWN, self.OnSelect)
        self.ListBox.Bind(wx.EVT_KEY_DOWN, self.OnSelect)
        
        # *** Layout *** #
        
        lyt_h = wx.BoxSizer(wx.HORIZONTAL)
        
        lyt_h.Add(self.TextCtrl, 1)
        lyt_h.Add(self.ToggleArrow, 1, wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5)
        
        self.Add(lyt_h, 1)
    
    
    ## TODO: Doxygen
    def Bind(self, *args):
        self.Parent.Bind(*args)
    
    
    ## TODO: Doxygen
    def GetName(self):
        return self.Name
    
    
    ## TODO: Doxygen
    def GetParent(self):
        return self.Parent
    
    
    ## Get a control's position relative to the grandparent
    def GetPosFromGrandparent(self, control):
        pos_p = self.Parent.GetPositionTuple()
        pos_c = control.GetPositionTuple()
        
        return (pos_c[0] + pos_p[0], pos_c[1] + pos_p[1],)
    
    
    ## TODO: Doxygen
    def LayoutListBox(self):
        # The ListBox is drawn on the grandparent, so position relative to grandparent must be found
        text_pos = self.GetPosFromGrandparent(self.TextCtrl)
        text_size = self.TextCtrl.GetSizeTuple()
        
        target_pos = wx.Point(text_pos[0], text_pos[1]+text_size[1])
        
        if self.ListBox.GetPosition() != target_pos:
            self.ListBox.SetPosition(target_pos)
        
        size = self.ListBox.GetSizeTuple()
        best_size = self.ListBox.GetBestSizeTuple()
        
        if size < best_size:
            self.ListBox.SetSize(best_size)
        
        # Drop down should be at least as wide as text area
        elif size[0] < text_size[0]:
            self.ListBox.SetSize(wx.Size(text_size[0], size[1]))
    
    
    ## Causes ListBox to lose focus in wx 3.0
    def OnClickPanel(self, event=None):
        if self.ListBox.HasFocus() and not self.ToggleArrow.IsCollapsed():
            self.ToggleArrow.Collapse()
        
        if event:
            event.Skip()
    
    
    ## TODO: Doxygen
    def OnSelect(self, event=None):
        if event:
            if isinstance(event, wx.KeyEvent):
                if event.GetKeyCode() == wx.WXK_ESCAPE:
                    self.ToggleArrow.Collapse()
            
            else:
                selection = self.ListBox.GetStringSelection()
                self.TextCtrl.SetValue(selection)
                self.TextCtrl.SetFocus()
            
            event.Skip()
    
    
    ## TODO: Doxygen
    def OnToggleArrow(self, event=None):
        if event:
            self.LayoutListBox()


## Custom wx.combo.OwnerDrawnCombBox
#  
#  wx.combo.OwnerDrawnComboBox is preferred over wx.ComboBox because
#  its PopupWindow is more compact.
class ComboBox(OwnerDrawnComboBox):
    def __init__(self, parent, win_id=wx.ID_ANY, value=wx.EmptyString, pos=wx.DefaultPosition,
            size=wx.DefaultSize, choices=[], style=0, validator=wx.DefaultValidator,
            name=wx.ComboBoxNameStr):
        OwnerDrawnComboBox.__init__(self, parent, win_id, value, pos, size, choices,
                style, validator, name)
        
        self.Default = self.GetLabel()
        self.Priority = []
        
        if wx.MAJOR_VERSION <= 2:
            self.BGDefault = self.TextCtrl.GetBackgroundColour()
            self.BGDisabled = self.TextCtrl.GetForegroundColour()
    
    
    ## Enables/Disables the ComboBox
    #  
    #  Override default behavior to only affect ComboBox's TextCtrl & PopupWindow instances
    def Enable(self, enable=True):
        # Only change if 'enable' is different than current state
        if enable != self.IsEnabled():
            if wx.MAJOR_VERSION <= 2:
                # DEBUG: START
                print(u'\nDEBUG custom.ComboCtrl:')
                print(u'    Enabled status: {}; Target status: {}'.format(self.IsEnabled(), enable))
                # DEBUG: END
                
                self.TextCtrl.Enable(enable)
                self.PopupWindow.Enabled(enable)
                
                # DEBUG: LINE
                print(u'    New status: {}'.format(self.IsEnabled()))
                
                return self.IsEnabled() == enable
        
        return True
    
    
    ## Override default behavior to check only ComboBox's TextCtrl & PopupWindow instances
    def IsEnabled(self):
        if wx.MAJOR_VERSION > 2:
            return OwnerDrawnComboBox.IsEnabled(self)
        
        enabled = FieldsEnabled((self.TextCtrl, self.PopupWindow,))
        
        # DEBUG: START
        print(u'\nDEBUG custom.combo.ComboCtrl.IsEnabled override')
        print(u'    FieldsEnabled returned "{}"'.format(enabled))
        # DEBUG: END
        
        return enabled
    
    
    ## Resets ComboBox to defaults
    def Reset(self):
        if not self.Count:
            self.SetValue(self.Default)
            return self.Value == self.Default
        
        return False

# -*- coding: utf-8 -*-

## \package custom.toggle

# MIT licensing
# See: LICENSE.txt


import wx


class arrow:
    LEFT = 0
    RIGHT = 1
    UP = 2
    DOWN = 3
    ULEFT = 4
    URIGHT = 5
    DLEFT = 6
    DRIGHT = 7
    
    defs = {
        LEFT: u'◀',
        RIGHT: u'▶',
        UP: u'▲',
        DOWN: u'▼',
        ULEFT: u'◤',
        URIGHT: u'◥',
        DLEFT: u'◣',
        DRIGHT: u'◢',
        }

## An arrow that toggles direction
#  
#  \param drop_window
#  \param arrow
class ToggleArrow(wx.StaticText):
    def __init__(self, parent, drop_window, w_id=wx.ID_ANY, state_normal=arrow.LEFT, state_alt=arrow.DLEFT):
        wx.StaticText.__init__(self, parent, w_id, label=arrow.defs[state_normal])
        
        if wx.MAJOR_VERSION <= 2:
            wx.YELLOW = wx.Colour(255, 255, 0, 255)
        
        self.ColorNormal = self.GetForegroundColour()
        self.ColorHighlight = wx.YELLOW
        
        self.DropWindow = drop_window
        
        self.StateNormal = state_normal
        self.StateAlt = state_alt
        
        # *** Event Handlers *** #
        
        self.DropWindow.Bind(wx.EVT_KILL_FOCUS, self.OnLoseFocus)
        
        # Binding parent window allows adding padding a larger area
        parent.Bind(wx.EVT_LEFT_DOWN, self.OnLeftDown)
        self.Bind(wx.EVT_LEFT_DOWN, self.OnLeftDown)
        
        parent.Bind(wx.EVT_MOTION, self.OnMotion)
        
        # *** Actions *** #
        
        # Don't show drop window initially
        self.DropWindow.Hide()
    
    
    ## Show or hide the drop down window
    def Collapse(self, collapse=True):
        if collapse:
            self.SetLabel(arrow.defs[self.StateNormal])
            self.DropWindow.Hide()
        
        else:
            self.SetLabel(arrow.defs[self.StateAlt])
            self.DropWindow.Show()
            self.DropWindow.SetFocus()
        
        # FIXME: How to attach event to ToggleArrow so wx.Event.GetEventObject returns ToggleArrow instance
        wx.PostEvent(self.GetParent(), wx.CommandEvent(wx.EVT_TOGGLEBUTTON.typeId, self.Id))
    
    
    ## Performs a hit test to determine if click is close enough execute toggle
    def IsHit(self):
        if wx.MAJOR_VERSION <= 2:
            xy_absolute = tuple(self.GetScreenPosition())
        
        else:
            xy_absolute = self.GetScreenPositionTuple()
        
        padding = 15
        
        # X, Y, W, H
        hit_box = (
            xy_absolute[0] - padding,
            xy_absolute[1] - padding,
            xy_absolute[0] + self.Size[0] + padding,
            xy_absolute[1] + self.Size[1] + padding,
            )
        
        mouse = wx.GetMouseState()
        
        if wx.MAJOR_VERSION <= 2:
            mouse.X = mouse.GetX()
            mouse.Y = mouse.GetY()
        
        x_inside = hit_box[0] <= mouse.X <= hit_box[2]
        y_inside = hit_box[1] <= mouse.Y <= hit_box[3]
        
        return x_inside and y_inside
    
    
    ## TODO: Doxygen
    def IsCollapsed(self):
        return self.Label == arrow.defs[self.StateNormal]
    
    
    ## TODO: Doxygen
    def IsToggled(self):
        return self.Label == arrow.defs[self.StateAlt]
    
    
    ## TODO: Doxygen
    def OnLeftDown(self, event=None):
        if event:
            if self.IsHit():
                self.Toggle()
            
            event.Skip()
    
    
    ## TODO: Doxygen
    def OnLoseFocus(self, event=None):
        if not self.IsCollapsed():
            self.Collapse()
    
    
    ## TODO: Doxygen
    def OnMotion(self, event=None):
        FG = self.GetForegroundColour()
        
        if self.IsHit() and FG != self.ColorHighlight:
            self.SetForegroundColour(self.ColorHighlight)
        
        elif not self.IsHit() and FG != self.ColorNormal:
            self.SetForegroundColour(self.ColorNormal)
        
        wx.YieldIfNeeded()
    
    
    ## Reset ToggleArrow to default appearance
    def Reset(self):
        self.SetLabel(self.StateNormal)
        self.DropWindow.Hide()
    
    
    ## TODO: Doxygen
    def Toggle(self):
        self.Collapse(self.IsToggled())

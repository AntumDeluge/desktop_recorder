# -*- coding: utf-8 -*-

## \package custom.menu

# MIT licensing
# See: LICENSE.txt


import wx


class Menu(wx.Menu):
    def __init__(self):
        wx.Menu.__init__(self)


    def GetIdIndex(self, mi_id):
        index = -1
        for MI in self.GetMenuItems():
            index += 1
            if MI.GetId() == mi_id:
                break

        if index < 0:
            return None

        return index

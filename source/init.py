#! /usr/bin/env python
# -*- coding: utf8 -*-

## \package record-desktop

# MIT licensing
# See: LICENSE.txt


import errno, os, shutil, sys

from globals.commandline    import args, GetOption
from globals.paths          import PATH_confdir
from globals.settings       import APP_version_string
from globals.settings       import EXE_name


if not EXE_name:
    EXE_name = os.path.basename(__file__)


legacy = False
deleted = False
deletefile = None
for A in args:
    if A.startswith(u'rmlocal-'):
        deletefile = u'{}/{}'.format(PATH_confdir, A.split(u'-')[1])
        
        if not os.path.exists(deletefile):
            print(u'Error: Cannot delete non-existent file: {}'.format(deletefile))
            sys.exit(errno.ENOENT)
        
        if os.path.isdir(deletefile):
            shutil.rmtree(deletefile)
        
        else:
            # This should throw an exception if the path is a directory & somehow wasn't removed by shutil
            os.remove(deletefile)
        
        deleted = True
        
        continue
    
    if A == u'legacy':
        legacy = True

if deleted:
    sys.exit(0)

# Remove from memory
del deleted, deletefile

if GetOption(u'v') or GetOption(u'version'):
    print(APP_version_string)
    sys.exit(0)

from globals.ffmpeg import CMD_ffmpeg


if not CMD_ffmpeg:
    print(u'ERROR: Could not find ffmpeg executable')
    sys.exit(errno.ENOENT)

print(u'Found ffmpeg executable: {}'.format(CMD_ffmpeg))


from globals.paths  import FILE_lock


locked = os.path.exists(FILE_lock)

wx_compat = (u'3.0', u'2.8')
import wxversion


if legacy:
    try:
        wxversion.select((u'2.8',))
    
    except wxversion.VersionError:
        print(u'Warning:\n  Requested "legacy", but no compatible legacy wx version found.\n  Using default settings ...\n')

# Remove from memory
del legacy

if not wxversion._selected:
    try:
        wxversion.select(wx_compat)
    
    except wxversion.VersionError:
        print(u'Error:\n  You do not have a compatible version of wxPython installed.\n  One of the following versions is required: {}\n'.format(u', '.join(wx_compat)))
        sys.exit(1)

import wx


# Remove from memory
del wx_compat

# Main wx.App instance
APP_wx = wx.App()

# --- Lock script so only one instance can be run
if locked:
    wx.MessageDialog(None, u'An instance of Desktop Recorder is already running.\n\nIf this is an error type "rm ~/.config/desktop_recorder/lock" in a terminal', u'Cannot Start', wx.OK|wx.ICON_ERROR).ShowModal()
    APP_wx.MainLoop()
    
    sys.exit(1)


from ui.taskbar import Icon


if __name__ == u'__main__':
    app = wx.App()
    tray_icon = Icon()
    app.MainLoop()

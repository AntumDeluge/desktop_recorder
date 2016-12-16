#! /usr/bin/env python2
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

# Don't start up app if 'rmlocal' command(s) used
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

from globals.files      import FILE_lock
from globals.lock       import AppIsLocked
from globals.lock       import LockApp
from globals.lock       import UnlockApp
from globals.settings   import APP_name


# Remove from memory
del wx_compat

# Main wx.App instance
APP_wx = wx.App()

# --- Lock script so only one instance can be run
if AppIsLocked():
    # Failsafe in case executable script name has not been set
    if not EXE_name:
        EXE_name = u'desktop-recorder'
    
    err_li1 = u'An instance of {} is already running.'.format(APP_name)
    err_li2 = u'If this is an error, remove the lock file with the following command:'
    err_li3 = u'rm "{}"'.format(FILE_lock)
    err_li4 = u'Or, launch {} with the "rmlocal-lock" command:'.format(APP_name)
    err_li5 = u'{} rmlocal-lock'.format(EXE_name)
    
    wx.MessageDialog(None, u'{}\n\n{}\n\t{}\n\n{}\n\t{}'.format(err_li1, err_li2, err_li3, err_li4, err_li5), u'Cannot Start', wx.OK|wx.ICON_ERROR).ShowModal()
    APP_wx.MainLoop()
    
    sys.exit(1)


import traceback

from ui.taskbar import Icon


if __name__ == u'__main__':
    app = wx.App()
    try:
        # FIXME: Method using processes to lock app???
        LockApp()
        
        tray_icon = Icon()
        app.MainLoop()
    
    except:
        UnlockApp()
        
        err_msg = u'A fatal error has occured'
        err_info = unicode(traceback.format_exc())
        
        print(u'\n{}:\n\n    {}'.format(err_msg, err_info))
        wx.MessageDialog(None, u'{}:\n\n{}'.format(err_msg, err_info), u'Error', style=wx.OK|wx.ICON_ERROR).ShowModal()
        
        sys.exit(1)

UnlockApp()

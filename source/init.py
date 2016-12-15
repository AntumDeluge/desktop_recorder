#! /usr/bin/env python
# -*- coding: utf8 -*-

## \package record-desktop

# MIT licensing
# See: LICENSE.txt


import errno, os, shutil, signal, subprocess, sys

from globals.commandline    import args
from globals.paths          import PATH_confdir
from globals.settings       import EXE_name
from globals.settings       import GetAppInfo


if not EXE_name:
    EXE_name = os.path.basename(__file__)

VERSION = GetAppInfo(u'VERSION')


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


if u'-v' in args or u'--version' in args:
    print(VERSION)
    sys.exit(0)


from globals.ffmpeg import CMD_ffmpeg


if not CMD_ffmpeg:
    print(u'ERROR: Could not find ffmpeg executable')
    sys.exit(errno.ENOENT)

print(u'Found ffmpeg executable: {}'.format(CMD_ffmpeg))


from globals.paths  import FILE_config
from globals.paths  import FILE_lock
from globals.paths  import PATH_home


# --- Create config file
if not os.path.isfile(FILE_config):
    if not os.path.isdir(PATH_confdir):
        os.mkdir(PATH_confdir)
    
    config_data = u'video=1\n\
audio=1\n\
filename=out\n\
dest={}\n\
container=0\n\
vcodec=0\n\
quality=-1\n\
framerate=6\n\
acodec=0\n\
channels=0\n\
samplerate=1\n\
bitrate=2'.format(PATH_home)
    
    FILE_BUFFER = open(FILE_config, u'w')
    FILE_BUFFER.write(config_data)
    FILE_BUFFER.close()


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


from globals.icons  import ICON_rec
from globals.icons  import ICON_main
from globals.icons  import ICON_pause
from globals.icons  import ICON_stop
from ui.options     import Options


ID_STOP = wx.NewId()
ID_REC = wx.NewId()
ID_PAUSE = wx.NewId()
ID_OPT = wx.NewId()



class Icon(wx.TaskBarIcon):
    def __init__(self):
        wx.TaskBarIcon.__init__(self)
        
        self.options = Options(None, -1, u'Desktop Recorder Options')
        self.options.ParseOptions()
        
        self.icon_main = wx.Icon(ICON_main, wx.BITMAP_TYPE_PNG)
        self.icon_rec = wx.Icon(ICON_rec, wx.BITMAP_TYPE_PNG)
        self.icon_pause = wx.Icon(ICON_pause, wx.BITMAP_TYPE_PNG)
        self.icon_stop = wx.Icon(ICON_stop, wx.BITMAP_TYPE_PNG)
        self.menu_icons = [wx.Image(ICON_main, wx.BITMAP_TYPE_PNG), wx.Image(ICON_rec, wx.BITMAP_TYPE_PNG),
            wx.Image(ICON_pause, wx.BITMAP_TYPE_PNG), wx.Image(ICON_stop, wx.BITMAP_TYPE_PNG)]
        
        for ico in xrange(len(self.menu_icons)):
            self.menu_icons[ico].Rescale(16, 16, wx.IMAGE_QUALITY_HIGH)
        
        self.SetIcon(self.icon_stop, u'Desktop Recorder')
        
        # --- Processes for ffmpeg
        self.P1 = None
        self.P2 = None
        self.IsPaused = False
        
        self.menu = wx.Menu()
        self.menu_options = wx.MenuItem(self.menu, ID_OPT, u'Show/Hide Options')
        self.menu_rec = wx.MenuItem(self.menu, ID_REC, u'Record')
        self.menu_pause = wx.MenuItem(self.menu, ID_PAUSE, u'Pause')
        self.menu_stop = wx.MenuItem(self.menu, ID_STOP, u'Stop')
        self.menu_exit = wx.MenuItem(self.menu, wx.ID_EXIT, u'Quit')
        self.menu_about = wx.MenuItem(self.menu, wx.ID_ABOUT, u'About')
        
        self.menu_options.SetBitmap(self.menu_icons[0].ConvertToBitmap())
        self.menu_rec.SetBitmap(self.menu_icons[1].ConvertToBitmap())
        self.menu_pause.SetBitmap(self.menu_icons[2].ConvertToBitmap())
        self.menu_stop.SetBitmap(self.menu_icons[3].ConvertToBitmap())
        
        self.menu.AppendItem(self.menu_options)
        self.menu.AppendSeparator()
        self.menu.AppendItem(self.menu_rec)
        self.menu.AppendItem(self.menu_pause)
        self.menu.AppendItem(self.menu_stop)
        self.menu.AppendItem(self.menu_exit)
        self.menu.AppendItem(self.menu_about)
        
        self.menu.Enable(ID_PAUSE, False)
        self.menu.Enable(ID_STOP, False)
        
        # *** Event handlers *** #
        
        wx.EVT_MENU(self.menu, ID_OPT, self.ToggleOptions)
        wx.EVT_MENU(self.menu, ID_REC, self.Record)
        wx.EVT_MENU(self.menu, ID_PAUSE, self.Pause)
        wx.EVT_MENU(self.menu, ID_STOP, self.Stop)
        wx.EVT_MENU(self.menu, wx.ID_EXIT, self.Exit)
        wx.EVT_MENU(self.menu, wx.ID_ABOUT, self.ShowInfo)
        
        wx.EVT_TASKBAR_LEFT_DOWN(self, self.OnClick)
        wx.EVT_TASKBAR_RIGHT_DOWN(self, self.OnClick)
    
    
    def OnClick(self, event):
        self.PopupMenu(self.menu)
    
    
    def Exit(self, event):
        config_data=u'[CONFIG]\n\
video={}\n\
audio={}\n\
filename={}\n\
dest={}\n\
container={}\n\
vcodec={}\n\
quality={}\n\
framerate={}\n\
acodec={}\n\
channels={}\n\
samplerate={}\n\
bitrate={}'.format(int(self.options.video.GetValue()), int(self.options.audio.GetValue()), self.options.filename.GetValue(), self.options.folder.GetValue(), self.options.vcontainer.GetSelection(), self.options.vcodec.GetSelection(), self.options.qual.GetValue(), self.options.frate.GetSelection(), self.options.acodec.GetSelection(), self.options.chan.GetSelection(), self.options.samplerate.GetSelection(), self.options.bitrate.GetSelection())
        
        FILE_BUFFER = open(FILE_config, u'w')
        FILE_BUFFER.write(config_data)
        FILE_BUFFER.close()
        
        if os.path.exists(FILE_lock):
            os.remove(FILE_lock)
        
        self.options.Destroy()
        self.Destroy()
    
    
    def ShowInfo(self, event):
        about = wx.AboutDialogInfo()
        about.SetIcon(self.icon_main)
        about.SetName(u'Desktop Recorder')
        about.SetVersion(VERSION)
        about.SetCopyright(u'(c) 2012 Jordan Irwin')
        about.SetLicense(u'Copyright (c) 2012, Jordan Irwin\n\
All rights reserved.\n\
\n\
Redistribution and use in source and binary forms, with or without modification, are permitted provided\n\
that the following conditions are met:\n\
\n\
    - Redistributions of source code must retain the above copyright notice, this list of conditions and\n\
      the following disclaimer.\n\
    - Redistributions in binary form must reproduce the above copyright notice, this list of conditions\n\
      and the following disclaimer in the documentation and/or other materials provided with the distribution.\n\
\n\
THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS\n\
OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY\n\
AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR\n\
CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL\n\
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF\n\
USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,\n\
WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY\n\
WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.')
        about.AddDeveloper(u'Jordan Irwin')
        wx.AboutBox(about)
    
    
    def Stop(self, event):
        if self.options.video.GetValue() and self.options.audio.GetValue():
            os.kill(self.P1.pid, signal.SIGINT)
            os.kill(self.P2.pid, signal.SIGINT)
            self.P1.wait()
            self.P2.wait()
            self.P3 = subprocess.call([CMD_ffmpeg, u'-y', u'-i', self.tempvid, u'-i', self.tempaud, u'-vcodec', u'copy', u'-acodec', u'copy', self.output])
        
        elif self.options.video.GetValue():
            os.kill(self.P1.pid, signal.SIGINT)
            self.P1.wait()
            shutil.move(self.tempvid, u'{}/{}.{}'.format(self.dest, self.filename, self.vidext))
        
        elif self.options.audio.GetValue():
            os.kill(self.P2.pid, signal.SIGINT)
            self.P2.wait()
            shutil.move(self.tempaud, u'{}/{}.{}'.format(self.dest, self.filename, self.audext))
        
        # Protect against accidentally deleting temp files
        if os.path.isfile(self.output):
            if os.path.isfile(self.tempvid):
                os.remove(self.tempvid)
            
            if os.path.isfile(self.tempaud):
                os.remove(self.tempaud)
        
        self.IsPaused = False
        self.menu.Enable(ID_OPT, True)
        self.menu.Enable(ID_REC, True)
        self.menu.Enable(ID_PAUSE, False)
        self.menu.Enable(ID_STOP, False)
        self.menu.Enable(wx.ID_EXIT, True)
        self.SetIcon(self.icon_stop)
        self.options.panel.Enable()
    
    
    def Record(self, event):
        def DisableThem():
            self.menu.Enable(ID_REC, False)
            self.menu.Enable(ID_OPT, False)
            self.menu.Enable(wx.ID_EXIT, False)
        
        def EnableThem():
            self.menu.Enable(ID_REC, True)
            self.menu.Enable(ID_OPT, True)
            self.menu.Enable(wx.ID_EXIT, True)
        
        filename = self.options.filename.GetValue()
        filename = u''.join(filename.split(u' '))
        
        if self.IsPaused:
            if self.options.video.GetValue():
                os.kill(self.P1.pid, signal.SIGCONT)
            
            if self.options.audio.GetValue():
                os.kill(self.P2.pid, signal.SIGCONT)
        
        else:
            try:
                # Test for int in quality
                int(self.options.qual.GetValue())
            
            except ValueError:
                DisableThem()
                wx.MessageDialog(self.options, u'Quality must be an integer value.', u'Error', wx.OK|wx.ICON_ERROR).ShowModal()
                EnableThem()
                
                return
            
            if not filename or not os.path.isdir(self.options.folder.GetValue()):
                DisableThem()
                wx.MessageDialog(self.options, u'Please make sure you have suppied a filename and\nselected an existing folder to save the output.', u'Error', wx.OK|wx.ICON_ERROR).ShowModal()
                EnableThem()
            
            elif not self.options.video.GetValue() and not self.options.audio.GetValue():
                DisableThem()
                wx.MessageDialog(self.options, u'You must include at least one of video and audio to record.', u'Error!', wx.OK|wx.ICON_ERROR).ShowModal()
                EnableThem()
            
            else:
                # --- Recording
                self.vcodec = self.options.vcodecs[self.options.vcodec.GetSelection()]
                self.channels = self.options.channels[self.options.chan.GetSelection()]
                self.samplerate = self.options.samplerates[self.options.samplerate.GetSelection()]
                self.bitrate = self.options.bitrates[self.options.bitrate.GetSelection()]
                self.frate = self.options.framerates[self.options.frate.GetSelection()]
                self.display = wx.GetDisplaySize()
                self.display = u'{}x{}'.format(self.display[0], self.display[1])
                self.vidext = self.options.vcontainers[self.options.vcontainer.GetSelection()]
                audio_extensions = {u'libmp3lame': u'mp3', u'libvorbis': u'ogg', u'pcm_s32le': u'wav', u'flac': u'flac'}
                self.audext = audio_extensions[self.options.acodecs[self.options.acodec.GetSelection()]]
                self.tempvid = u'/tmp/video.tmp.{}'.format(self.vidext)
                self.tempaud = u'/tmp/audio.tmp.{}'.format(self.audext)
                self.dest = self.options.folder.GetValue()
                self.filename = self.options.filename.GetValue()
                self.output = u'{}/{}.{}'.format(self.dest, self.filename, self.vidext)
                self.quality = self.options.qual.GetValue()
                
                if int(self.quality) < 0:
                    #self.quality = u'-sameq'
                    vidcommand = (CMD_ffmpeg, u'-y', u'-f', u'x11grab', u'-r', self.frate, u'-s', self.display, u'-i', u':0.0', u'-sameq', u'-vcodec', self.vcodec, self.tempvid)
                
                else:
                    #self.quality = u'-b {}'.format(str(self.quality))
                                    vidcommand = (CMD_ffmpeg, u'-y', u'-f', u'x11grab', u'-r', self.frate, u'-s', self.display, u'-i', u':0.0', u'-b', self.quality, u'-vcodec', self.vcodec, self.tempvid)
                
                self.acodec = self.options.acodecs[self.options.acodec.GetSelection()]
                
                if self.options.video.GetValue():
                    self.P1 = subprocess.Popen(vidcommand)
                
                if self.options.audio.GetValue():
                    self.P2 = subprocess.Popen([CMD_ffmpeg, u'-y', u'-f', u'alsa', u'-i', u'hw:0,0', u'-acodec', self.acodec, u'-ar', self.samplerate, u'-ab', self.bitrate, u'-ac', self.channels, self.tempaud])
        
        self.IsPaused = False
        self.options.Hide()
        self.options.panel.Disable()
        self.menu.Enable(ID_OPT, False)
        self.menu.Enable(ID_REC, False)
        self.menu.Enable(ID_PAUSE, True)
        self.menu.Enable(ID_STOP, True)
        self.menu.Enable(wx.ID_EXIT, False)
        self.SetIcon(self.icon_rec)
    
    
    def Pause(self, event):
        if self.options.video.GetValue():
            os.kill(self.P1.pid, signal.SIGSTOP)
        
        if self.options.audio.GetValue():
            os.kill(self.P2.pid, signal.SIGSTOP)
        
        self.IsPaused = True
        self.menu.Enable(ID_REC, True)
        self.menu.Enable(ID_PAUSE, False)
        self.SetIcon(self.icon_pause)
    
    
    def ToggleOptions(self, event):
        if self.options.IsShown():
            self.options.Hide()
        
        else:
            self.options.Show()





class App(wx.App):
    def __init__(self):
        wx.App.__init__(self)
        
        # --- Icons
        self.icon = Icon()
        self.icon.app = self
        
        return None

if __name__ == u'__main__':
    app = App()
    app.MainLoop()

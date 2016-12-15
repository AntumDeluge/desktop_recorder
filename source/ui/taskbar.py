# -*- coding: utf-8 -*-

## \package ui.taskbar

# MIT licensing
# See: LICENSE.txt


import os, shutil, signal, subprocess, wx

from globals            import ident as ID
from globals.ffmpeg     import CMD_ffmpeg
from globals.files      import FILE_lock
from globals.icons      import GetIcon
from globals.icons      import GetImage
from globals.settings   import APP_version_string
from ui.options         import Options


## Class for the taskbar icon
class Icon(wx.TaskBarIcon):
    def __init__(self):
        wx.TaskBarIcon.__init__(self)
        
        self.options = Options(None, -1, u'Desktop Recorder Options')
        
        self.menu_icons = [
            GetImage(u'icon'),
            GetImage(u'record'),
            GetImage(u'pause'),
            GetImage(u'stop'),
            ]
        
        for ico in xrange(len(self.menu_icons)):
            self.menu_icons[ico].Rescale(16, 16, wx.IMAGE_QUALITY_HIGH)
        
        self.SetIcon(GetIcon(u'stop'), u'Desktop Recorder')
        
        # --- Processes for ffmpeg
        self.P1 = None
        self.P2 = None
        self.IsPaused = False
        
        self.menu = wx.Menu()
        self.menu_options = wx.MenuItem(self.menu, ID.OPT, u'Show/Hide Options')
        self.menu_rec = wx.MenuItem(self.menu, ID.REC, u'Record')
        self.menu_pause = wx.MenuItem(self.menu, ID.PAUSE, u'Pause')
        self.menu_stop = wx.MenuItem(self.menu, ID.STOP, u'Stop')
        self.menu_exit = wx.MenuItem(self.menu, ID.EXIT, u'Quit')
        self.menu_about = wx.MenuItem(self.menu, ID.ABOUT, u'About')
        
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
        
        self.menu.Enable(ID.PAUSE, False)
        self.menu.Enable(ID.STOP, False)
        
        # *** Event handlers *** #
        
        wx.EVT_MENU(self.menu, ID.OPT, self.ToggleOptions)
        wx.EVT_MENU(self.menu, ID.REC, self.Record)
        wx.EVT_MENU(self.menu, ID.PAUSE, self.Pause)
        wx.EVT_MENU(self.menu, ID.STOP, self.Stop)
        wx.EVT_MENU(self.menu, ID.EXIT, self.Exit)
        wx.EVT_MENU(self.menu, ID.ABOUT, self.ShowInfo)
        
        wx.EVT_TASKBAR_LEFT_DOWN(self, self.OnClick)
        wx.EVT_TASKBAR_RIGHT_DOWN(self, self.OnClick)
    
    
    ## Shows a context menu when left or right clicked
    def OnClick(self, event):
        self.PopupMenu(self.menu)
    
    
    ## Actions to take when the app exits
    def Exit(self, event):
        if os.path.exists(FILE_lock):
            os.remove(FILE_lock)
        
        self.options.Destroy()
        self.Destroy()
    
    
    ## Displays an about dialog
    def ShowInfo(self, event):
        about = wx.AboutDialogInfo()
        about.SetIcon(GetIcon(u'icon'))
        about.SetName(u'Desktop Recorder')
        about.SetVersion(APP_version_string)
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
    
    
    ## Stops recording
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
        self.menu.Enable(ID.OPT, True)
        self.menu.Enable(ID.REC, True)
        self.menu.Enable(ID.PAUSE, False)
        self.menu.Enable(ID.STOP, False)
        self.menu.Enable(ID.EXIT, True)
        self.SetIcon(GetIcon(u'stop'))
        self.options.panel.Enable()
    
    
    ## Begins recording
    def Record(self, event):
        def DisableThem():
            self.menu.Enable(ID.REC, False)
            self.menu.Enable(ID.OPT, False)
            self.menu.Enable(ID.EXIT, False)
        
        def EnableThem():
            self.menu.Enable(ID.REC, True)
            self.menu.Enable(ID.OPT, True)
            self.menu.Enable(ID.EXIT, True)
        
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
        self.menu.Enable(ID.OPT, False)
        self.menu.Enable(ID.REC, False)
        self.menu.Enable(ID.PAUSE, True)
        self.menu.Enable(ID.STOP, True)
        self.menu.Enable(ID.EXIT, False)
        self.SetIcon(GetIcon(u'record'))
    
    
    ## Pauses recording
    def Pause(self, event):
        if self.options.video.GetValue():
            os.kill(self.P1.pid, signal.SIGSTOP)
        
        if self.options.audio.GetValue():
            os.kill(self.P2.pid, signal.SIGSTOP)
        
        self.IsPaused = True
        self.menu.Enable(ID.REC, True)
        self.menu.Enable(ID.PAUSE, False)
        self.SetIcon(GetIcon(u'pause'))
    
    
    ## Shows/Hides the options window
    def ToggleOptions(self, event):
        if self.options.IsShown():
            self.options.Hide()
        
        else:
            self.options.Show()

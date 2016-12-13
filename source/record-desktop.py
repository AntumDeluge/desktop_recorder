#! /usr/bin/env python
# -*- coding: utf8 -*-

## \package record-desktop

# MIT licensing
# See: LICENSE.txt


import wxversion, os, sys, shutil, subprocess, signal, time, errno
from subprocess import PIPE

try:
    wxversion.select('2.8')

except wxversion.VersionError:
    print 'You do not have the correct version of wxPython installed.\nPlease install version 2.8'
    sys.exit(1)

import wx

from globals.ffmpeg import CMD_ffmpeg

if not CMD_ffmpeg:
    print(u'ERROR: Could not find ffmpeg executable')
    sys.exit(errno.ENOENT)

print(u'Found ffmpeg executable: {}'.format(CMD_ffmpeg))

version = u'0.2.0 Beta 4'

# --- Check to see if ffmpeg supports xvid and x264
no_xvid = subprocess.call('{} -codecs | grep -i "libxvid"'.format(CMD_ffmpeg), stdout=PIPE, stderr=PIPE, shell=True)
if no_xvid:
    no_xvid = subprocess.call('{} -formats | grep -i "libxvid"'.format(CMD_ffmpeg), stdout=PIPE, stderr=PIPE, shell=True)

no_x264 = subprocess.call('{} -codecs | grep -i "libx264"'.format(CMD_ffmpeg), stdout=PIPE, stderr=PIPE, shell=True)
if no_x264:
    no_x264 = subprocess.call('{} -formats | grep -i "libx264"'.format(CMD_ffmpeg), stdout=PIPE, stderr=PIPE, shell=True)


exedir = os.path.dirname(__file__)
home = os.getenv('HOME')
icondir = '%s/icons' % (exedir)
confdir = '%s/.config/desktop_recorder' % (home)

# --- Create config file
if not os.path.isfile('%s/config' % (confdir)):
    if not os.path.isdir(confdir):
        os.mkdir(confdir)
    config = open('%s/config' % (confdir), 'w')
    data = u'[CONFIG]\n\
video=1\n\
audio=1\n\
filename=out\n\
dest=%s\n\
container=0\n\
vcodec=0\n\
quality=-1\n\
framerate=6\n\
acodec=0\n\
channels=0\n\
samplerate=1\n\
bitrate=2' % (home)
    config.write(data)
    config.close()

# --- Lock script so only one instance can be run
if os.path.isfile('%s/lock' % confdir):
    locked = wx.App(0)
    wx.MessageDialog(None, u'An instance of Desktop Recorder is already running.\n\nIf this is an error type "rm ~/.config/desktop_recorder/lock"', u'Cannot Start', wx.OK|wx.ICON_ERROR).ShowModal()
    sys.exit(1)
    locked.MainLoop()
else:
    lock = open('%s/lock' % confdir, 'w')

# --- Delete the config file
if (len(sys.argv) > 1) and (sys.argv[1] == u'delete-config'):
    if os.path.isdir(confdir):
        shutil.rmtree(confdir)
    exit(0)

# --- Icons
icon_stop = '%s/stop.png' % (icondir)
icon_rec = '%s/record.png' % (icondir)
icon_pause = '%s/pause.png' % (icondir)
icon_main = '%s/icon.png' % (icondir)

ID_STOP = wx.NewId()
ID_REC = wx.NewId()
ID_PAUSE = wx.NewId()
ID_OPT = wx.NewId()



class Icon(wx.TaskBarIcon):
    def __init__(self):
        wx.TaskBarIcon.__init__(self)
        
        self.icon_main = wx.Icon(icon_main, wx.BITMAP_TYPE_PNG)
        self.icon_rec = wx.Icon(icon_rec, wx.BITMAP_TYPE_PNG)
        self.icon_pause = wx.Icon(icon_pause, wx.BITMAP_TYPE_PNG)
        self.icon_stop = wx.Icon(icon_stop, wx.BITMAP_TYPE_PNG)
        self.menu_icons = [wx.Image(icon_main, wx.BITMAP_TYPE_PNG), wx.Image(icon_rec, wx.BITMAP_TYPE_PNG),
            wx.Image(icon_pause, wx.BITMAP_TYPE_PNG), wx.Image(icon_stop, wx.BITMAP_TYPE_PNG)]
        
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
#        self.menu.AppendItem(self.menu_pause)
        self.menu.AppendItem(self.menu_stop)
        self.menu.AppendItem(self.menu_exit)
        self.menu.AppendItem(self.menu_about)
        
        self.menu.Enable(ID_PAUSE, False)
        self.menu.Enable(ID_STOP, False)
        
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
        data=u'[CONFIG]\n\
video=%s\n\
audio=%s\n\
filename=%s\n\
dest=%s\n\
container=%s\n\
vcodec=%s\n\
quality=%s\n\
framerate=%s\n\
acodec=%s\n\
channels=%s\n\
samplerate=%s\n\
bitrate=%s' % (int(self.options.video.GetValue()), int(self.options.audio.GetValue()), self.options.filename.GetValue(), self.options.folder.GetValue(), self.options.vcontainer.GetSelection(), self.options.vcodec.GetSelection(), self.options.qual.GetValue(), self.options.frate.GetSelection(), self.options.acodec.GetSelection(), self.options.chan.GetSelection(), self.options.samplerate.GetSelection(), self.options.bitrate.GetSelection())
        file = open('%s/config' % confdir, 'w')
        file.write(data)
        file.close()
        self.app.ExitMainLoop()
        lock.close()
        os.remove('%s/lock' % confdir)
    
    def ShowInfo(self, event):
        about = wx.AboutDialogInfo()
        about.SetIcon(self.icon_main)
        about.SetName(u'Desktop Recorder')
        about.SetVersion(version)
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
            self.P3 = subprocess.call([CMD_ffmpeg, '-y', '-i', self.tempvid, '-i', self.tempaud, '-vcodec', 'copy', '-acodec', 'copy', self.output])
        elif self.options.video.GetValue():
            os.kill(self.P1.pid, signal.SIGINT)
            self.P1.wait()
            shutil.move(self.tempvid, '%s/%s.%s' % (self.dest, self.filename, self.vidext))
        elif self.options.audio.GetValue():
            os.kill(self.P2.pid, signal.SIGINT)
            self.P2.wait()
            shutil.move(self.tempaud, '%s/%s.%s' % (self.dest, self.filename, self.audext))
        if os.path.isfile(self.output): # Protect against accidentally deleting temp files
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
        filename = ''.join(filename.split(' '))
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
                self.display = '%sx%s' % (self.display[0], self.display[1])
                self.vidext = self.options.vcontainers[self.options.vcontainer.GetSelection()]
                audio_extensions = {'libmp3lame': 'mp3', 'libvorbis': 'ogg', 'pcm_s32le': 'wav', 'flac': 'flac'}
                self.audext = audio_extensions[self.options.acodecs[self.options.acodec.GetSelection()]]
                self.tempvid = '/tmp/video.tmp.%s' % self.vidext
                self.tempaud = '/tmp/audio.tmp.%s' % self.audext
                self.dest = self.options.folder.GetValue()
                self.filename = self.options.filename.GetValue()
                self.output = '%s/%s.%s' % (self.dest, self.filename, self.vidext)
                self.quality = self.options.qual.GetValue()
                if int(self.quality) < 0:
                    #self.quality = '-sameq'
                    vidcommand = (CMD_ffmpeg, '-y', '-f', 'x11grab', '-r', self.frate, '-s', self.display, '-i', ':0.0', '-sameq', '-vcodec', self.vcodec, self.tempvid)
                else:
                    #self.quality = '-b %s' % str(self.quality)
                                    vidcommand = (CMD_ffmpeg, '-y', '-f', 'x11grab', '-r', self.frate, '-s', self.display, '-i', ':0.0', '-b', self.quality, '-vcodec', self.vcodec, self.tempvid)

                self.acodec = self.options.acodecs[self.options.acodec.GetSelection()]
                
                if self.options.video.GetValue():
                    self.P1 = subprocess.Popen(vidcommand)
                if self.options.audio.GetValue():
                    self.P2 = subprocess.Popen([CMD_ffmpeg, '-y', '-f', 'alsa', '-i', 'hw:0,0', '-acodec', self.acodec, '-ar', self.samplerate, '-ab', self.bitrate, '-ac', self.channels, self.tempaud])
            
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

class Options(wx.Dialog):
    def __init__(self, parent, id, title):
        wx.Dialog.__init__(self, parent, id, title, size=(300, 450))
        self.Show(False)
        
        self.vcontainers = (u'avi', u'mkv', u'flv', u'ogg')
        self.acontainers = (u'mp3', u'wav', u'ogg')
        self.containers = self.vcontainers + self.acontainers [:-1]
        self.vcodecs = [u'libtheora', u'huffyuv', u'flv']
        if not no_xvid:
            self.vcodecs.insert(0, u'libxvid')
        if not no_x264:
            self.vcodecs.insert(0, u'libx264')
        self.acodecs = (u'libmp3lame', u'libvorbis', u'pcm_s32le', u'flac')
        self.channels = ('1', '2')
        self.samplerates = ('22050', '44100', '48000')
        self.bitrates = (u'64k', u'96k', u'128k', u'196k', u'224k', u'320k')
        self.framerates = (u'15', u'23.98', u'24', u'24.975', u'25', u'29.97', u'30', u'50', u'60')

        self.config = {}
        self.ParseOptions()
        
        self.icon_main = wx.Icon(icon_main, wx.BITMAP_TYPE_PNG)
        
        self.panel = wx.Panel(self, -1)
        
        self.SetIcon(self.icon_main)
        
        self.video = wx.CheckBox(self.panel, -1, u'Include Video')
        self.video.SetValue(self.config[u'video'])
        self.vcodec = wx.Choice(self.panel, choices=self.vcodecs)
        self.vcodec.Select(self.config[u'vcodec'])
        vcodec_sizer = wx.BoxSizer(wx.HORIZONTAL)
        vcodec_sizer.Add(wx.StaticText(self.panel, -1, u'Video Codec'), 0, wx.ALIGN_CENTER)
        vcodec_sizer.Add(self.vcodec, 0)
        self.qual = wx.TextCtrl(self.panel, -1, unicode(self.config[u'quality']))
        qual_sizer = wx.BoxSizer(wx.HORIZONTAL)
        qual_sizer.Add(wx.StaticText(self.panel, -1, u'Quality'), 0, wx.ALIGN_CENTER)
        qual_sizer.Add(self.qual, 1, wx.EXPAND)
        self.frate = wx.Choice(self.panel, choices=self.framerates)
        self.frate.Select(self.config[u'framerate'])
        frate_sizer = wx.BoxSizer(wx.HORIZONTAL)
        frate_sizer.Add(wx.StaticText(self.panel, -1, u'Framerate'), 0, wx.ALIGN_CENTER)
        frate_sizer.Add(self.frate, 0)
        frate_sizer.Add(wx.StaticText(self.panel, -1, u'FPS'), 0, wx.ALIGN_CENTER)
        vcontain_txt = wx.StaticText(self.panel, -1, u'Container')
        self.vcontainer = wx.Choice(self.panel, choices=self.vcontainers)
        self.vcontainer.Select(self.config[u'container'])
        vcont_sizer = wx.BoxSizer(wx.HORIZONTAL)
        vcont_sizer.Add(vcontain_txt, 0, wx.ALIGN_CENTER)
        vcont_sizer.Add(self.vcontainer, 1, wx.EXPAND)
        
        vidbox = wx.StaticBox(self.panel, -1, u'Video')
        vidbox_sizer = wx.StaticBoxSizer(vidbox, wx.VERTICAL)
        vidbox_sizer.Add(self.video, 0)
        vidbox_sizer.Add(vcodec_sizer, 0)
        vidbox_sizer.Add(qual_sizer, 0, wx.EXPAND)
        vidbox_sizer.Add(frate_sizer, 0)
        vidbox_sizer.Add(vcont_sizer, 0)
        
        self.audio = wx.CheckBox(self.panel, -1, u'Include Audio')
        self.audio.SetValue(self.config[u'audio'])
        self.acodec = wx.Choice(self.panel, choices=self.acodecs)
        self.acodec.Select(self.config[u'acodec'])
        acodec_sizer = wx.BoxSizer(wx.HORIZONTAL)
        acodec_sizer.Add(wx.StaticText(self.panel, -1, u'Audio Codec'), 0, wx.ALIGN_CENTER)
        acodec_sizer.Add(self.acodec, 0)
        self.chan = wx.Choice(self.panel, choices=self.channels)
        self.chan.Select(self.config[u'channels'])
        chan_sizer = wx.BoxSizer(wx.HORIZONTAL)
        chan_sizer.Add(wx.StaticText(self.panel, -1, u'Channels'), 0, wx.ALIGN_CENTER)
        chan_sizer.Add(self.chan, 0)
        self.samplerate = wx.Choice(self.panel, choices=self.samplerates)
        self.samplerate.Select(self.config[u'samplerate'])
        samp_sizer = wx.BoxSizer(wx.HORIZONTAL)
        samp_sizer.Add(wx.StaticText(self.panel, -1, u'Samplerate'), 0, wx.ALIGN_CENTER)
        samp_sizer.Add(self.samplerate, 0)
        samp_sizer.Add(wx.StaticText(self.panel, -1, u'Hz'), 0, wx.ALIGN_CENTER)
        self.bitrate = wx.Choice(self.panel, choices=self.bitrates)
        self.bitrate.Select(self.config[u'bitrate'])
        br_sizer = wx.BoxSizer(wx.HORIZONTAL)
        br_sizer.Add(wx.StaticText(self.panel, -1, u'Bitrate'), 0, wx.ALIGN_CENTER)
        br_sizer.Add(self.bitrate, 0)
        
        audbox = wx.StaticBox(self.panel, -1, u'Audio')
        audbox_sizer = wx.StaticBoxSizer(audbox, wx.VERTICAL)
        audbox_sizer.Add(self.audio, 0)
        audbox_sizer.Add(acodec_sizer, 0)
        audbox_sizer.Add(chan_sizer, 0)
        audbox_sizer.Add(samp_sizer, 0)
        audbox_sizer.Add(br_sizer, 0)
        
        filename_txt = wx.StaticText(self.panel, -1, u'Filename')
        self.filename = wx.TextCtrl(self.panel, -1, self.config[u'filename'])
        fname_sizer = wx.BoxSizer(wx.HORIZONTAL)
        fname_sizer.Add(filename_txt, 0, wx.ALIGN_CENTER)
        fname_sizer.Add(self.filename, 1, wx.EXPAND)
        
        folder_button = wx.Button(self.panel, -1, u'Folder')
        self.folder = wx.TextCtrl(self.panel, -1, self.config[u'dest'])
        fold_sizer = wx.BoxSizer(wx.HORIZONTAL)
        fold_sizer.Add(folder_button, 0, wx.ALIGN_CENTER)
        fold_sizer.Add(self.folder, 1, wx.EXPAND)
        
        wx.EVT_BUTTON(folder_button, -1, self.SelectDest)
        
        misc_box = wx.StaticBox(self.panel, -1, u'Misc')
        misc_sizer = wx.StaticBoxSizer(misc_box, wx.VERTICAL)
        misc_sizer.Add(fname_sizer, 0, wx.EXPAND)
        misc_sizer.Add(fold_sizer, 0, wx.EXPAND)
        
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(vidbox_sizer, 0, wx.EXPAND)
        main_sizer.Add(audbox_sizer, 0, wx.EXPAND)
        main_sizer.Add(misc_sizer, 0, wx.EXPAND)
        
        self.panel.SetAutoLayout(True)
        self.panel.SetSizer(main_sizer)
        self.panel.Layout()
    
    def ParseOptions(self):
        try:
            file = open('%s/config' % confdir, 'r')
            options = file.read().split('\n')[1:]
            file.close()
            for o in options:
                o = o.split('=')
                try:
                    self.config[o[0]] = int(o[1])
                except ValueError:
                    self.config[o[0]] = o[1]
        except IndexError:
            wx.MessageDialog(None, u'Possible corrupted configuration file.\n\nTry deleting it: rm ~/.config/desktop_recorder/config', u'Error', wx.OK|wx.ICON_ERROR).ShowModal()
            os.remove('%s/lock' % confdir)
            sys.exit(1)
    
    def SelectDest(self, event):
        dest = wx.DirDialog(self, defaultPath=os.getcwd(), style=wx.DD_DEFAULT_STYLE|wx.DD_DIR_MUST_EXIST|wx.DD_CHANGE_DIR)
        if dest.ShowModal() == wx.ID_OK:
            self.folder.SetValue(dest.GetPath())

class App(wx.App):
    def __init__(self):
        wx.App.__init__(self)
        
        # --- Icons
        self.icon = Icon()
        self.icon.options = Options(None, -1, u'Desktop Recorder Options')
        self.icon.app = self
        return None

if __name__ == '__main__':
    app = App()
    app.MainLoop()

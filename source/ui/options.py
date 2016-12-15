# -*- coding: utf-8 -*-

## \package ui.options

# MIT licensing
# See: LICENSE.txt


import os, wx

from globals.ffmpeg import no_x264
from globals.ffmpeg import no_xvid
from globals.icons  import ICON_main
from globals.paths  import FILE_config
from globals.paths  import FILE_lock
from globals.paths  import PATH_confdir
from globals.paths  import PATH_home


class Options(wx.Dialog):
    def __init__(self, parent, ID, title):
        wx.Dialog.__init__(self, parent, ID, title, size=(300, 450))
        
        self.Show(False)
        
        self.SetIcon(wx.Icon(ICON_main, wx.BITMAP_TYPE_PNG))
        
        # TODO: Use ffmpeg to find available containers
        vcontainers = (u'avi', u'mkv', u'flv', u'ogg')
        acontainers = (u'mp3', u'wav', u'ogg')
        containers = vcontainers + acontainers [:-1]
        vcodecs = [u'libtheora', u'huffyuv', u'flv']
        acodecs = (u'libmp3lame', u'libvorbis', u'pcm_s32le', u'flac')
        samplerates = (u'22050', u'44100', u'48000')
        bitrates = (u'64k', u'96k', u'128k', u'196k', u'224k', u'320k')
        framerates = (u'15', u'23.98', u'24', u'24.975', u'25', u'29.97', u'30', u'50', u'60')
        
        if not no_xvid:
            vcodecs.insert(0, u'libxvid')
        
        if not no_x264:
            vcodecs.insert(0, u'libx264')
        
        vcodecs = tuple(vcodecs)
        
        self.config = {}
        
        self.pnl_bg = wx.Panel(self)
        
        chk_video = wx.CheckBox(self.pnl_bg, label=u'Include Video', name=u'video')
        chk_video.default = True
        
        sel_vcodec = wx.Choice(self.pnl_bg, choices=vcodecs, name=u'vcodec')
        sel_vcodec.default = u'libtheora'
        
        ti_quality = wx.TextCtrl(self.pnl_bg, name=u'quality')
        ti_quality.default = u'-1'
        
        sel_framerate = wx.Choice(self.pnl_bg, choices=framerates, name=u'framerate')
        sel_framerate.default = u'30'
        
        txt_vcontainer = wx.StaticText(self.pnl_bg, label=u'Container')
        sel_vcontainer = wx.Choice(self.pnl_bg, choices=vcontainers, name=u'container')
        sel_vcontainer.default = u'avi'
        
        chk_audio = wx.CheckBox(self.pnl_bg, label=u'Include Audio', name=u'audio')
        chk_audio.default = True
        
        sel_acodec = wx.Choice(self.pnl_bg, choices=acodecs, name=u'acodec')
        sel_acodec.default = u'libmp3lame'
        
        spin_channels = wx.SpinCtrl(self.pnl_bg, name=u'channels')
        spin_channels.default = 1
        
        sel_samplerate = wx.Choice(self.pnl_bg, choices=samplerates, name=u'samplerate')
        sel_samplerate.default = u'44100'
        
        sel_bitrate = wx.Choice(self.pnl_bg, choices=bitrates, name=u'bitrate')
        sel_bitrate.default = u'128k'
        
        txt_filename = wx.StaticText(self.pnl_bg, label=u'Filename')
        ti_filename = wx.TextCtrl(self.pnl_bg, name=u'filename')
        ti_filename.default = u'out'
        
        btn_target = wx.Button(self.pnl_bg, label=u'Folder')
        self.ti_target = wx.TextCtrl(self.pnl_bg, name=u'dest')
        self.ti_target.default = u'{}/Videos'.format(PATH_home)
        
        # *** Layout *** #
        
        vcodec_sizer = wx.BoxSizer(wx.HORIZONTAL)
        vcodec_sizer.Add(wx.StaticText(self.pnl_bg, label=u'Video Codec'), 0, wx.ALIGN_CENTER)
        vcodec_sizer.Add(sel_vcodec, 0)
        
        qual_sizer = wx.BoxSizer(wx.HORIZONTAL)
        qual_sizer.Add(wx.StaticText(self.pnl_bg, label=u'Quality'), 0, wx.ALIGN_CENTER)
        qual_sizer.Add(ti_quality, 1, wx.EXPAND)
        
        frate_sizer = wx.BoxSizer(wx.HORIZONTAL)
        frate_sizer.Add(wx.StaticText(self.pnl_bg, label=u'Framerate'), 0, wx.ALIGN_CENTER)
        frate_sizer.Add(sel_framerate, 0)
        frate_sizer.Add(wx.StaticText(self.pnl_bg, label=u'FPS'), 0, wx.ALIGN_CENTER)
        
        vcont_sizer = wx.BoxSizer(wx.HORIZONTAL)
        vcont_sizer.Add(txt_vcontainer, 0, wx.ALIGN_CENTER)
        vcont_sizer.Add(sel_vcontainer, 1, wx.EXPAND)
        
        vidbox = wx.StaticBox(self.pnl_bg, label=u'Video')
        vidbox_sizer = wx.StaticBoxSizer(vidbox, wx.VERTICAL)
        vidbox_sizer.Add(chk_video, 0)
        vidbox_sizer.Add(vcodec_sizer, 0)
        vidbox_sizer.Add(qual_sizer, 0, wx.EXPAND)
        vidbox_sizer.Add(frate_sizer, 0)
        vidbox_sizer.Add(vcont_sizer, 0)
        
        acodec_sizer = wx.BoxSizer(wx.HORIZONTAL)
        acodec_sizer.Add(wx.StaticText(self.pnl_bg, label=u'Audio Codec'), 0, wx.ALIGN_CENTER)
        acodec_sizer.Add(sel_acodec, 0)
        
        chan_sizer = wx.BoxSizer(wx.HORIZONTAL)
        chan_sizer.Add(wx.StaticText(self.pnl_bg, label=u'Channels'), 0, wx.ALIGN_CENTER)
        chan_sizer.Add(spin_channels, 0)
        
        samp_sizer = wx.BoxSizer(wx.HORIZONTAL)
        samp_sizer.Add(wx.StaticText(self.pnl_bg, label=u'Samplerate'), 0, wx.ALIGN_CENTER)
        samp_sizer.Add(sel_samplerate, 0)
        samp_sizer.Add(wx.StaticText(self.pnl_bg, label=u'Hz'), 0, wx.ALIGN_CENTER)
        
        br_sizer = wx.BoxSizer(wx.HORIZONTAL)
        br_sizer.Add(wx.StaticText(self.pnl_bg, label=u'Bitrate'), 0, wx.ALIGN_CENTER)
        br_sizer.Add(sel_bitrate, 0)
        
        audbox = wx.StaticBox(self.pnl_bg, label=u'Audio')
        audbox_sizer = wx.StaticBoxSizer(audbox, wx.VERTICAL)
        audbox_sizer.Add(chk_audio, 0)
        audbox_sizer.Add(acodec_sizer, 0)
        audbox_sizer.Add(chan_sizer, 0)
        audbox_sizer.Add(samp_sizer, 0)
        audbox_sizer.Add(br_sizer, 0)
        
        fname_sizer = wx.BoxSizer(wx.HORIZONTAL)
        fname_sizer.Add(txt_filename, 0, wx.ALIGN_CENTER)
        fname_sizer.Add(ti_filename, 1, wx.EXPAND)
        
        fold_sizer = wx.BoxSizer(wx.HORIZONTAL)
        fold_sizer.Add(btn_target, 0, wx.ALIGN_CENTER)
        fold_sizer.Add(self.ti_target, 1, wx.EXPAND)
        
        misc_box = wx.StaticBox(self.pnl_bg, label=u'Misc')
        misc_sizer = wx.StaticBoxSizer(misc_box, wx.VERTICAL)
        misc_sizer.Add(fname_sizer, 0, wx.EXPAND)
        misc_sizer.Add(fold_sizer, 0, wx.EXPAND)
        
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(vidbox_sizer, 0, wx.EXPAND)
        main_sizer.Add(audbox_sizer, 0, wx.EXPAND)
        main_sizer.Add(misc_sizer, 0, wx.EXPAND)
        
        self.pnl_bg.SetAutoLayout(True)
        self.pnl_bg.SetSizer(main_sizer)
        self.pnl_bg.Layout()
        
        # *** Event handlers *** #
        
        wx.EVT_SHOW(self, self.OnShow)
        
        btn_target.Bind(wx.EVT_BUTTON, self.SelectDest)
        
        # *** Actions *** #
        
        if not os.path.isfile(FILE_config):
            self.WriteDefaultConfig()
        
        self.ParseOptions()
    
    
    ## TODO: Doxygen
    def OnShow(self, event=None):
        if self.IsShown():
            for C in self.pnl_bg.GetChildren():
                c_name = C.GetName()
                
                if c_name in self.config:
                    value = self.config[c_name]
                    
                    if isinstance(C, (wx.TextCtrl, wx.CheckBox, wx.SpinCtrl)):
                        C.SetValue(value)
                        continue
                    
                    # TODO: Use string value instead of index integer???
                    if isinstance(C, wx.Choice):
                        # Some wx.Choice field values are stored as integers & need to be converted to string
                        if not isinstance(value, (unicode, str)):
                            value = unicode(value)
                        
                        C.SetStringSelection(value)
        
        else:
            # Set & write config when window is hidden
            for C in self.pnl_bg.GetChildren():
                c_name = C.GetName()
                
                if isinstance(C, wx.TextCtrl):
                    self.config[c_name] = C.GetValue()
                    
                    # Reset field
                    C.Clear()
                    continue
                
                if isinstance(C, (wx.CheckBox, wx.SpinCtrl)):
                    self.config[c_name] = C.GetValue()
                    
                    # Reset field
                    C.SetValue(C.default)
                    continue
                
                if isinstance(C, wx.Choice):
                    self.config[c_name] = C.GetStringSelection()
                    
                    # Reset field
                    C.SetSelection(0)
            
            self.WriteConfig()
        
        if event:
            event.Skip()
    
    
    ## TODO: Doxygen
    def ParseOptions(self):
        try:
            FILE_BUFFER = open(FILE_config, u'r')
            options = FILE_BUFFER.read().split(u'\n')
            FILE_BUFFER.close()
            
            for LI in options:
                if u'=' in LI:
                    split_index = LI.index(u'=')
                    
                    key = LI[:split_index]
                    value = LI[split_index+1:]
                    
                    # Boolean types
                    if value.lower() in (u'true', u'false'):
                        self.config[key] = value.lower() == u'true'
                        continue
                    
                    # Integer types
                    if value.isnumeric():
                        self.config[key] = int(value)
                        continue
                    
                    self.config[key] = value
        
        except IndexError:
            wx.MessageDialog(None, u'Possible corrupted configuration file.\n\nTry deleting it: rm ~/.config/desktop_recorder/config', u'Error', wx.OK|wx.ICON_ERROR).ShowModal()
            
            if os.path.exists(FILE_lock):
                os.remove(FILE_lock)
            
            return False
        
        # DEBUG START
        print(u'DEBUGGING:')
        for C in self.config:
            print(u'\nKey: {}\nValue: {}\nType: {}'.format(C, self.config[C], type(self.config[C])))
        # DEBUG END
        
        return True
    
    
    ## TODO: Doxygen
    def SelectDest(self, event):
        dest = wx.DirDialog(self, defaultPath=os.getcwd(), style=wx.DD_DEFAULT_STYLE|wx.DD_DIR_MUST_EXIST|wx.DD_CHANGE_DIR)
        if dest.ShowModal() == wx.ID_OK:
            self.ti_target.SetValue(dest.GetPath())
    
    
    ## TODO: Doxygen
    def WriteConfig(self, opts_list=[]):
        if not os.path.isdir(PATH_confdir):
            os.makedirs(PATH_confdir)
        
        if not opts_list:
            for OPT in self.config:
                opts_list.append(u'{}={}'.format(OPT, self.config[OPT]))
        
        if opts_list:
            print(u'Writing to config ...')
            
            FILE_BUFFER = open(FILE_config, u'w')
            FILE_BUFFER.write(u'\n'.join(opts_list))
            FILE_BUFFER.close()
            
            return True
        
        return False
    
    
    ## TODO: Doxygen
    def WriteDefaultConfig(self):
        # The children types that we are getting 'default' value from
        usable_types = (
            wx.CheckBox,
            wx.Choice,
            wx.SpinCtrl,
            wx.TextCtrl,
            )
        
        opts_list = []
        for C in self.pnl_bg.GetChildren():
            if isinstance(C, usable_types):
                opts_list.append(u'{}={}'.format(C.GetName(), C.default))
        
        return self.WriteConfig(opts_list)

# -*- coding: utf-8 -*-

## \package ui.options

# MIT licensing
# See: LICENSE.txt


import os, wx

from custom.choice  import Choice
from globals        import ident as ID
from globals.ffmpeg import GetCodecs
from globals.ffmpeg import no_x264
from globals.ffmpeg import no_xvid
from globals.files  import FILE_lock
from globals.files  import FILE_options
from globals.icons  import GetIcon
from globals.paths  import PATH_confdir
from globals.paths  import PATH_home


## Class for the options window
class Options(wx.Dialog):
    def __init__(self, parent, window_id, title, style=wx.DEFAULT_DIALOG_STYLE):
        wx.Dialog.__init__(self, parent, window_id, title, size=(300, 450), style=style|wx.RESIZE_BORDER)
        
        self.Show(False)
        
        self.SetIcon(GetIcon(u'logo'))
        
        # TODO: Use ffmpeg to find available containers
        vcontainers = (u'avi', u'mkv', u'flv', u'ogg')
        acontainers = (u'mp3', u'wav', u'ogg')
        containers = vcontainers + acontainers [:-1]
        
        # These basic lists are used if SetVideoCodecs & SetAudioCodecs fail (ordered in priority)
        vcodecs = [u'libtheora', u'huffyuv', u'flv']
        acodecs = (u'libmp3lame', u'libvorbis', u'pcm_s16le', u'pcm_s32le', u'flac')
        codecs = GetCodecs()
        
        samplerates = (u'22050', u'44100', u'48000')
        bitrates = (u'64k', u'96k', u'128k', u'196k', u'224k', u'320k')
        framerates = (u'15', u'23.98', u'24', u'24.975', u'25', u'29.97', u'30', u'50', u'60')
        
        if not no_x264:
            vcodecs.insert(0, u'libx264')
        
        if not no_xvid:
            vcodecs.insert(0, u'libxvid')
        
        vcodecs = tuple(vcodecs)
        
        self.options = {}
        
        if wx.MAJOR_VERSION > 2:
            PANEL_BORDER = wx.BORDER_THEME
        
        else:
            PANEL_BORDER = wx.BORDER_MASK
        
        # *** Video *** #
        
        self.chk_video = wx.CheckBox(self, ID.VIDEO, u'Include Video', name=u'video')
        self.chk_video.default = True
        
        self.pnl_video = wx.Panel(self, style=PANEL_BORDER)
        
        sel_vcodec = Choice(self.pnl_video, choices=sorted(vcodecs), name=u'vcodec')
        
        # Override default video codec list
        if u'video' in codecs:
            self.SetVideoCodecs(codecs[u'video'])
        
        sel_vcodec.default = sel_vcodec.GetStrings()[0]
        for C in vcodecs:
            if C in sel_vcodec.GetStrings():
                sel_vcodec.default = C
                break
        
        sel_vcodec.SetStringSelection(sel_vcodec.default)
        
        ti_quality = wx.TextCtrl(self.pnl_video, name=u'quality')
        ti_quality.default = u'-1'
        
        sel_framerate = Choice(self.pnl_video, choices=framerates, name=u'framerate')
        sel_framerate.default = u'30'
        
        sel_vcontainer = Choice(self.pnl_video, choices=vcontainers, name=u'container')
        sel_vcontainer.default = u'avi'
        
        # *** Audio *** #
        
        self.chk_audio = wx.CheckBox(self, ID.AUDIO, u'Include Audio', name=u'audio')
        self.chk_audio.default = True
        
        self.pnl_audio = wx.Panel(self, style=PANEL_BORDER)
        
        sel_acodec = Choice(self.pnl_audio, choices=sorted(acodecs), name=u'acodec')
        
        # Override default audio codec list
        if u'audio' in codecs:
            self.SetAudioCodecs(codecs[u'audio'])
        
        sel_acodec.default = sel_acodec.GetStrings()[0]
        for C in acodecs:
            if C in sel_acodec.GetStrings():
                sel_acodec.default = C
                break
        
        sel_acodec.SetStringSelection(sel_acodec.default)
        
        spin_channels = wx.SpinCtrl(self.pnl_audio, name=u'channels')
        spin_channels.default = 1
        
        sel_samplerate = Choice(self.pnl_audio, choices=samplerates, name=u'samplerate')
        sel_samplerate.default = u'44100'
        
        sel_bitrate = Choice(self.pnl_audio, choices=bitrates, name=u'bitrate')
        sel_bitrate.default = u'128k'
        
        # *** Output *** #
        
        #txt_filename = wx.StaticText(self, label=u'Filename')
        ti_filename = wx.TextCtrl(self, name=u'filename')
        ti_filename.default = u'out'
        
        btn_target = wx.Button(self, label=u'Folder')
        self.ti_target = wx.TextCtrl(self, name=u'dest')
        self.ti_target.default = u'{}/Videos'.format(PATH_home)
        
        # *** Layout *** #
        
        lyt_video = wx.GridBagSizer()
        
        # Row 1
        lyt_video.Add(wx.StaticText(self.pnl_video, label=u'Video Codec'), (0, 0), flag=wx.ALIGN_CENTER_VERTICAL|wx.LEFT|wx.TOP, border=5)
        lyt_video.Add(sel_vcodec, (0, 1), (1, 2), wx.TOP, 5)
        
        # Row 2
        lyt_video.Add(wx.StaticText(self.pnl_video, label=u'Quality'), (1, 0), flag=wx.ALIGN_CENTER_VERTICAL|wx.LEFT, border=5)
        lyt_video.Add(ti_quality, (1, 1), (1, 2))
        
        # Row 3
        lyt_video.Add(wx.StaticText(self.pnl_video, label=u'Framerate'), (2, 0), flag=wx.ALIGN_CENTER_VERTICAL|wx.LEFT, border=5)
        lyt_video.Add(sel_framerate, (2, 1))
        lyt_video.Add(wx.StaticText(self.pnl_video, label=u'FPS'), (2, 2), flag=wx.ALIGN_CENTER_VERTICAL)
        
        # Row 4
        lyt_video.Add(wx.StaticText(self.pnl_video, label=u'Container'), (3, 0), flag=wx.ALIGN_CENTER_VERTICAL|wx.LEFT|wx.BOTTOM, border=5)
        lyt_video.Add(sel_vcontainer, (3, 1), (1, 2), wx.BOTTOM, 5)
        
        self.pnl_video.SetAutoLayout(True)
        self.pnl_video.SetSizer(lyt_video)
        self.pnl_video.Layout()
        
        lyt_audio = wx.GridBagSizer()
        
        # Row 1
        lyt_audio.Add(wx.StaticText(self.pnl_audio, label=u'Audio Codec'), (0, 0), flag=wx.ALIGN_CENTER_VERTICAL|wx.LEFT|wx.TOP, border=5)
        lyt_audio.Add(sel_acodec, (0, 1), (1, 2), wx.TOP, 5)
        
        # Row 2
        lyt_audio.Add(wx.StaticText(self.pnl_audio, label=u'Channels'), (1, 0), flag=wx.ALIGN_CENTER_VERTICAL|wx.LEFT, border=5)
        lyt_audio.Add(spin_channels, (1, 1), (1, 2))
        
        # Row 3
        lyt_audio.Add(wx.StaticText(self.pnl_audio, label=u'Samplerate'), (2, 0), flag=wx.ALIGN_CENTER_VERTICAL|wx.LEFT, border=5)
        lyt_audio.Add(sel_samplerate, (2, 1))
        lyt_audio.Add(wx.StaticText(self.pnl_audio, label=u'Hz'), (2, 2), flag=wx.ALIGN_CENTER_VERTICAL)
        
        # Row 4
        lyt_audio.Add(wx.StaticText(self.pnl_audio, label=u'Bitrate'), (3, 0), flag=wx.ALIGN_CENTER_VERTICAL|wx.LEFT|wx.BOTTOM, border=5)
        lyt_audio.Add(sel_bitrate, (3, 1), (1, 2), wx.BOTTOM, 5)
        
        self.pnl_audio.SetAutoLayout(True)
        self.pnl_audio.SetSizer(lyt_audio)
        self.pnl_audio.Layout()
        
        lyt_misc = wx.FlexGridSizer(2, vgap=5)
        lyt_misc.AddGrowableCol(1)
        
        lyt_misc.Add(wx.StaticText(self, label=u'Filename'), flag=wx.ALIGN_CENTER_VERTICAL|wx.LEFT, border=3)
        lyt_misc.Add(ti_filename, flag=wx.EXPAND)
        lyt_misc.Add(btn_target, flag=wx.EXPAND)
        lyt_misc.Add(self.ti_target, flag=wx.EXPAND)
        
        lyt_main = wx.BoxSizer(wx.VERTICAL)
        
        lyt_main.Add(self.chk_video, flag=wx.TOP|wx.LEFT, border=7)
        lyt_main.Add(self.pnl_video, flag=wx.EXPAND|wx.LEFT|wx.RIGHT, border=7)
        lyt_main.Add(self.chk_audio, flag=wx.TOP|wx.LEFT, border=7)
        lyt_main.Add(self.pnl_audio, flag=wx.EXPAND|wx.LEFT|wx.RIGHT, border=7)
        lyt_main.Add(lyt_misc, flag=wx.EXPAND|wx.TOP|wx.LEFT|wx.RIGHT, border=5)
        
        self.SetAutoLayout(True)
        self.SetSizer(lyt_main)
        self.Layout()
        
        # *** Event handlers *** #
        
        wx.EVT_SHOW(self, self.OnShow)
        
        self.chk_video.Bind(wx.EVT_CHECKBOX, self.ToggleOptions)
        self.chk_audio.Bind(wx.EVT_CHECKBOX, self.ToggleOptions)
        
        btn_target.Bind(wx.EVT_BUTTON, self.SelectDest)
        
        # *** Actions *** #
        
        if not os.path.isfile(FILE_options):
            self.WriteDefaultOptions()
        
        self.ParseOptions()
        
        self.chk_video.SetValue(self.options[u'video'])
        self.chk_audio.SetValue(self.options[u'audio'])
        
        # Disables fields if check boxes unchecked
        self.ToggleOptions()
    
    
    ## Ensure that options are saved when app exits
    #  
    #  FIXME: wx 2.8 emits EVT_SHOW when app closes,
    #  so self.WriteOptions is called twice.
    def __del__(self):
        self.WriteOptions()
    
    
    ## Actions to take when the Options window if shown/hidden
    def OnShow(self, event=None):
        field_list = list(self.GetChildren()) + list(self.pnl_video.GetChildren()) + list(self.pnl_audio.GetChildren())
        
        if self.IsShown():
            for C in field_list:
                c_name = C.GetName()
                
                if c_name in self.options:
                    value = self.options[c_name]
                    
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
            # Set & write options when window is hidden
            for C in field_list:
                c_name = C.GetName()
                
                if isinstance(C, wx.TextCtrl):
                    self.options[c_name] = C.GetValue()
                    
                    # Reset field
                    C.Clear()
                    continue
                
                if isinstance(C, (wx.CheckBox, wx.SpinCtrl)):
                    self.options[c_name] = C.GetValue()
                    
                    # Reset field
                    C.SetValue(C.default)
                    continue
                
                if isinstance(C, wx.Choice):
                    self.options[c_name] = C.GetStringSelection()
                    
                    # Reset field
                    C.SetSelection(0)
            
            self.WriteOptions()
        
        if event:
            event.Skip()
    
    
    ## Reads the options file & sets value for each field
    def ParseOptions(self):
        try:
            FILE_BUFFER = open(FILE_options, u'r')
            options = FILE_BUFFER.read().split(u'\n')
            FILE_BUFFER.close()
            
            for LI in options:
                if u'=' in LI:
                    split_index = LI.index(u'=')
                    
                    key = LI[:split_index]
                    value = LI[split_index+1:]
                    
                    # Boolean types
                    if value.lower() in (u'true', u'false'):
                        self.options[key] = value.lower() == u'true'
                        continue
                    
                    # Integer types
                    if value.isnumeric():
                        self.options[key] = int(value)
                        continue
                    
                    self.options[key] = value
        
        except IndexError:
            wx.MessageDialog(None, u'Possible corrupted options file.\n\nTry deleting it: rm "{}"'.format(FILE_options), u'Error', wx.OK|wx.ICON_ERROR).ShowModal()
            
            # ???: Not sure why this is called here (should use UnlockApp())
            if os.path.exists(FILE_lock):
                os.remove(FILE_lock)
            
            return False
        
        return True
    
    
    ## Opens a directory dialog to select output destination
    def SelectDest(self, event):
        dest = wx.DirDialog(self, defaultPath=os.getcwd(), style=wx.DD_DEFAULT_STYLE|wx.DD_DIR_MUST_EXIST|wx.DD_CHANGE_DIR)
        if dest.ShowModal() == wx.ID_OK:
            self.ti_target.SetValue(dest.GetPath())
    
    
    ## Sets the list of audio codecs available from FFmpeg
    #  
    #  \param codec_list
    #    \b \e tuple|list : String list of codec names
    #  \return
    #    \b \e bool : True if list was set successfully
    def SetAudioCodecs(self, codec_list):
        for C in self.pnl_audio.GetChildren():
            if isinstance(C, wx.Choice) and C.GetName() == u'acodec':
                C.Set(codec_list)
                
                return True
        
        return False
    
    
    ## Sets the list of video codecs available from FFmpeg
    #  
    #  \param codec_list
    #    \b \e tuple|list : String list of codec names
    #  \return
    #    \b \e bool : True if list was set successfully
    def SetVideoCodecs(self, codec_list):
        for C in self.pnl_video.GetChildren():
            if isinstance(C, wx.Choice) and C.GetName() == u'vcodec':
                C.Set(codec_list)
                
                return True
        
        return False
    
    
    ## Enables/Disables video & audio settings
    def ToggleOptions(self, event=None):
        v_enabled = self.chk_video.GetValue()
        a_enabled = self.chk_audio.GetValue()
        
        for C in self.pnl_video.GetChildren():
            C.Enable(v_enabled)
        
        for C in self.pnl_audio.GetChildren():
            C.Enable(a_enabled)
    
    
    ## Writes the options values to the options file
    #  
    #  If the options list is empty, uses the standard option list (self.options)
    #  
    #  \param opts_list
    #    \b \e tuple|list : List of strings in key=value format
    #  \return
    #    \b \e bool : True if successfully wrote to options file
    def WriteOptions(self, opts_list=[]):
        if not os.path.isdir(PATH_confdir):
            os.makedirs(PATH_confdir)
        
        if not opts_list:
            for OPT in self.options:
                opts_list.append(u'{}={}'.format(OPT, self.options[OPT]))
        
        if opts_list:
            print(u'\nWriting to {} ...'.format(FILE_options))
            
            FILE_BUFFER = open(FILE_options, u'w')
            FILE_BUFFER.write(u'\n'.join(opts_list))
            FILE_BUFFER.close()
            
            return True
        
        return False
    
    
    ## Retrieves default field values & calls WriteOptions()
    #  
    #  \return
    #    \b \e bool : True if successfully wrote to options file
    def WriteDefaultOptions(self):
        # The children types that we are getting 'default' value from
        usable_types = (
            wx.CheckBox,
            wx.Choice,
            wx.SpinCtrl,
            wx.TextCtrl,
            )
        
        opts_list = []
        for C in list(self.GetChildren()) + list(self.pnl_video.GetChildren()) + list(self.pnl_video.GetChildren()):
            if isinstance(C, usable_types):
                opts_list.append(u'{}={}'.format(C.GetName(), C.default))
        
        return self.WriteOptions(opts_list)

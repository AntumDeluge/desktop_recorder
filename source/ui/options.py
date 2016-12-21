# -*- coding: utf-8 -*-

## \package ui.options

# MIT licensing
# See: LICENSE.txt


import os, wx
from wx.combo import OwnerDrawnComboBox

from custom.choice  import Choice
from globals        import ident as ID
from globals.cmds   import CMD_xrandr
from globals.cmds   import Execute
from globals.device import DisplayDevice
from globals.ffmpeg import GetContainers
from globals.ffmpeg import GetEncoders
from globals.ffmpeg import GetInputDevices
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
        
        devices = GetInputDevices()
        vdevices, vdev_defs = devices[u'video']
        adevices, adev_defs = devices[u'audio']
        
        containers = GetContainers()
        
        # These basic lists are used if SetVideoCodecs & SetAudioCodecs fail (ordered in priority)
        vcodecs = (u'libx264', u'mpeg4', u'libxvid', u'libtheora', u'flv', u'ffvhuff', u'huffyuv')
        acodecs = (u'libfdk_aac', u'aac', u'libmp3lame', u'libvorbis', u'pcm_s16le', u'libtwolame', u'flac')
        codecs = GetEncoders()
        
        samplerates = (u'22050', u'44100', u'48000')
        bitrates = (u'64k', u'96k', u'128k', u'196k', u'224k', u'320k')
        framerates = (u'15', u'23.98', u'24', u'24.975', u'25', u'29.97', u'30', u'50', u'60')
        
        self.options = {}
        
        if wx.MAJOR_VERSION > 2:
            PANEL_BORDER = wx.BORDER_THEME
        
        else:
            PANEL_BORDER = wx.BORDER_MASK
        
        tabs = wx.Notebook(self)
        page1 = wx.Panel(tabs)
        page2 = wx.Panel(tabs)
        
        tabs.AddPage(page1, u'Video')
        tabs.AddPage(page2, u'Audio')
        
        # *** Video *** #
        
        self.chk_video = wx.CheckBox(page1, ID.VIDEO, u'Include Video', name=u'video')
        self.chk_video.default = True
        
        self.pnl_video = wx.Panel(page1, style=PANEL_BORDER)
        
        # Filled with list of Display instances when self.InitDisplays is called
        self.displays = []
        
        self.sel_display = Choice(self.pnl_video, name=u'vinput')
        self.sel_display.default = 0
        
        self.dsp_label = wx.StaticText(self.pnl_video, label=u'Unnamed device')
        self.dsp_label.default = self.dsp_label.GetLabel()
        
        sel_vdevice = Choice(self.pnl_video, choices=vdevices, name=u'vcapture')
        sel_vdevice.defs = vdev_defs
        sel_vdevice.SetSelection(0)
        sel_vdevice.SetToolTipString(sel_vdevice.defs[0])
        
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
        
        sel_vbitrate = OwnerDrawnComboBox(self.pnl_video, name=u'vbitrate')
        sel_vbitrate.default = u''
        
        ti_quality = wx.TextCtrl(self.pnl_video, name=u'quality')
        ti_quality.default = u'-1'
        
        sel_framerate = Choice(self.pnl_video, choices=framerates, name=u'framerate')
        sel_framerate.default = u'30'
        
        # *** Audio *** #
        
        self.chk_audio = wx.CheckBox(page2, ID.AUDIO, u'Include Audio', name=u'audio')
        self.chk_audio.default = True
        
        self.pnl_audio = wx.Panel(page2, style=PANEL_BORDER)
        
        # Filled with list of Display instances when self.InitDisplays is called
        self.audio_inputs = []
        
        self.sel_audio = Choice(self.pnl_audio, name=u'ainput')
        self.sel_audio.default = 0
        
        self.aud_label = wx.StaticText(self.pnl_audio, label=u'Unnamed device')
        self.aud_label.default = self.dsp_label.GetLabel()
        
        sel_adevice = Choice(self.pnl_audio, choices=adevices, name=u'acapture')
        sel_adevice.defs = adev_defs
        sel_adevice.SetSelection(0)
        sel_adevice.SetToolTipString(sel_adevice.defs[0])
        
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
        
        sel_bitrate = OwnerDrawnComboBox(self.pnl_audio, choices=bitrates, name=u'bitrate')
        sel_bitrate.default = u'128k'
        
        spin_channels = wx.SpinCtrl(self.pnl_audio, name=u'channels')
        spin_channels.default = 1
        
        sel_samplerate = Choice(self.pnl_audio, choices=samplerates, name=u'samplerate')
        sel_samplerate.default = u'44100'
        
        # *** Output *** #
        
        ti_filename = wx.TextCtrl(self, name=u'filename')
        ti_filename.default = u'out'
        
        self.sel_container = Choice(self, choices=containers, name=u'container')
        self.sel_container.default = u'avi'
        
        btn_target = wx.Button(self, label=u'Folder')
        self.ti_target = wx.TextCtrl(self, name=u'dest')
        self.ti_target.default = u'{}/Videos'.format(PATH_home)
        
        # *** Layout *** #
        
        ALIGN_TEXT = wx.ALIGN_CENTER_VERTICAL|wx.LEFT
        
        lyt_video = wx.GridBagSizer(5, 2)
        
        # Row 1
        row = 0
        lyt_video.Add(wx.StaticText(self.pnl_video, label=u'Display'), (row, 0), flag=ALIGN_TEXT|wx.TOP, border=5)
        lyt_video.Add(self.sel_display, (row, 1), flag=wx.TOP, border=5)
        lyt_video.Add(self.dsp_label, (row, 2), flag=ALIGN_TEXT|wx.TOP, border=5)
        
        # Row 2
        row += 1
        lyt_video.Add(wx.StaticText(self.pnl_video, label=u'Capture Device'), (row, 0), flag=ALIGN_TEXT|wx.TOP, border=5)
        lyt_video.Add(sel_vdevice, (row, 1), (1, 2))
        
        # Row 3
        row += 1
        lyt_video.Add(wx.StaticText(self.pnl_video, label=u'Video Codec'), (row, 0), flag=ALIGN_TEXT, border=5)
        lyt_video.Add(sel_vcodec, (row, 1), (1, 2))
        
        # Row 4
        row += 1
        lyt_video.Add(wx.StaticText(self.pnl_video, label=u'Bitrate'), (row, 0), flag=ALIGN_TEXT, border=5)
        lyt_video.Add(sel_vbitrate, (row, 1), (1, 2), wx.EXPAND)
        
        # Row 5
        row += 1
        lyt_video.Add(wx.StaticText(self.pnl_video, label=u'Quality'), (row, 0), flag=ALIGN_TEXT, border=5)
        lyt_video.Add(ti_quality, (row, 1), (1, 2))
        
        # Row 6
        row += 1
        lyt_video.Add(wx.StaticText(self.pnl_video, label=u'Framerate'), (row, 0), flag=ALIGN_TEXT, border=5)
        lyt_video.Add(sel_framerate, (row, 1))
        lyt_video.Add(wx.StaticText(self.pnl_video, label=u'FPS'), (row, 2), flag=wx.ALIGN_CENTER_VERTICAL)
        
        self.pnl_video.SetAutoLayout(True)
        self.pnl_video.SetSizer(lyt_video)
        self.pnl_video.Layout()
        
        lyt_audio = wx.GridBagSizer(5, 2)
        
        # Row 1
        row = 0
        lyt_audio.Add(wx.StaticText(self.pnl_audio, label=u'Audio Input'), (row, 0), flag=ALIGN_TEXT|wx.TOP, border=5)
        lyt_audio.Add(self.sel_audio, (row, 1), flag=wx.TOP, border=5)
        lyt_audio.Add(self.aud_label, (row, 2), flag=ALIGN_TEXT|wx.TOP, border=5)
        
        # Row 2
        row += 1
        lyt_audio.Add(wx.StaticText(self.pnl_audio, label=u'Capture Device'), (row, 0), flag=ALIGN_TEXT|wx.TOP, border=5)
        lyt_audio.Add(sel_adevice, (row, 1), (1, 2), wx.TOP, 5)
        
        # Row 3
        row += 1
        lyt_audio.Add(wx.StaticText(self.pnl_audio, label=u'Audio Codec'), (row, 0), flag=ALIGN_TEXT, border=5)
        lyt_audio.Add(sel_acodec, (row, 1), (1, 2))
        
        # Row 4
        row += 1
        lyt_audio.Add(wx.StaticText(self.pnl_audio, label=u'Bitrate'), (row, 0), flag=ALIGN_TEXT, border=5)
        lyt_audio.Add(sel_bitrate, (row, 1), (1, 2), wx.EXPAND)
        
        # Row 5
        row += 1
        lyt_audio.Add(wx.StaticText(self.pnl_audio, label=u'Channels'), (row, 0), flag=ALIGN_TEXT, border=5)
        lyt_audio.Add(spin_channels, (row, 1), (1, 2))
        
        # Row 6
        row += 1
        lyt_audio.Add(wx.StaticText(self.pnl_audio, label=u'Samplerate'), (row, 0), flag=ALIGN_TEXT, border=5)
        lyt_audio.Add(sel_samplerate, (row, 1))
        lyt_audio.Add(wx.StaticText(self.pnl_audio, label=u'Hz'), (row, 2), flag=wx.ALIGN_CENTER_VERTICAL, border=5)
        
        self.pnl_audio.SetAutoLayout(True)
        self.pnl_audio.SetSizer(lyt_audio)
        self.pnl_audio.Layout()
        
        lyt_page1 = wx.BoxSizer(wx.VERTICAL)
        
        lyt_page1.Add(self.chk_video)
        lyt_page1.Add(self.pnl_video, 1, wx.EXPAND)
        
        lyt_page2 = wx.BoxSizer(wx.VERTICAL)
        
        lyt_page2.Add(self.chk_audio)
        lyt_page2.Add(self.pnl_audio, 1, wx.EXPAND)
        
        for page, sizer in ((page1, lyt_page1,), (page2, lyt_page2,)):
            page.SetAutoLayout(True)
            page.SetSizer(sizer)
            page.Layout()
        
        lyt_misc = wx.GridBagSizer()
        lyt_misc.SetCols(3)
        lyt_misc.AddGrowableCol(1)
        
        lyt_misc.Add(wx.StaticText(self, label=u'Filename'), (0, 0), flag=wx.ALIGN_BOTTOM|wx.LEFT, border=3)
        lyt_misc.Add(ti_filename, (1, 0), (1, 2), wx.EXPAND)
        lyt_misc.Add(wx.StaticText(self, label=u'.'), (1, 2), flag=wx.ALIGN_CENTER_VERTICAL)
        lyt_misc.Add(self.sel_container, (1, 3))
        lyt_misc.Add(btn_target, (2, 0), flag=wx.TOP, border=5)
        lyt_misc.Add(self.ti_target, (2, 1), (1, 4), wx.EXPAND|wx.TOP, 5)
        
        lyt_main = wx.BoxSizer(wx.VERTICAL)
        
        lyt_main.Add(tabs, 1, wx.EXPAND)
        lyt_main.Add(lyt_misc, flag=wx.EXPAND|wx.ALL, border=5)
        lyt_main.AddSpacer(5)
        
        self.SetAutoLayout(True)
        self.SetSizer(lyt_main)
        self.Layout()
        
        # *** Event handlers *** #
        
        wx.EVT_SHOW(self, self.OnShow)
        
        self.chk_video.Bind(wx.EVT_CHECKBOX, self.ToggleOptions)
        self.chk_audio.Bind(wx.EVT_CHECKBOX, self.ToggleOptions)
        
        for C in (sel_vdevice, sel_adevice,):
            C.Bind(wx.EVT_CHOICE, self.OnSelectDevice)
        
        self.sel_display.Bind(wx.EVT_CHOICE, self.OnSelectDisplay)
        
        btn_target.Bind(wx.EVT_BUTTON, self.SelectDest)
        
        # *** Actions *** #
        
        if not os.path.isfile(FILE_options):
            self.WriteDefaultOptions()
        
        self.ParseOptions()
        
        # Call after ParseOptions
        self.InitDisplays()
        
        self.chk_video.SetValue(self.options[u'video'])
        self.chk_audio.SetValue(self.options[u'audio'])
        
        # Disables fields if check boxes unchecked
        # Should be called after all fields' settings are initialized
        self.ToggleOptions()
        
        self.SetMinSize(self.GetSize())
    
    
    ## Ensure that options are saved when app exits
    #  
    #  FIXME: wx 2.8 emits EVT_SHOW when app closes,
    #  so self.WriteOptions is called twice.
    def __del__(self):
        self.WriteOptions()
    
    
    ## Checks if it is safe to begin recording
    #  
    #  At least one of video & audio must be enabled
    def CanRecord(self):
        # Use live dialog window if shown
        if self.IsShown():
            return self.chk_video.GetValue() or self.chk_audio.GetValue()
        
        return self.options[u'video'] or self.options[u'audio']
    
    
    ## Loads a list of available audio input devices into memory
    def InitAudioInputDevices(self):
        # Reset input devices
        self.audio_inputs = []
    
    
    ## Loads a list of available display devices into memory
    def InitDisplays(self):
        # Reset input devices
        self.displays = []
        
        displays = Execute(CMD_xrandr).split(u'\n')
        
        for D in displays:
            if u' connected ' in D:
                D = D.split(u' connected ')[1].strip(u' \t')
                
                primary = False
                if D.startswith(u'primary '):
                    primary = True
                    D = D.replace(u'primary ', u'').strip(u' \t')
                
                dimensions = D.split(u' ')[0]
                dimensions = [dimensions.split(u'x')[0]] + dimensions.split(u'x')[1].split(u'+')
                
                for X in range(len(dimensions)):
                    dimensions[X] = int(dimensions[X])
                
                dimensions = tuple(dimensions)
                
                # TODO: Add 'name' argument
                self.displays.append(DisplayDevice(len(self.displays), dimensions, primary))
        
        for D in self.displays:
            print(u'Display: {}; Size: {}; Position: {}; Primary: {}'.format(D.GetIndex(), D.GetSize(), D.GetPosition(), D.IsPrimary()))
        
        if self.displays:
            for X in range(len(self.displays)):
                self.sel_display.Append(unicode(X))
            
            self.sel_display.SetSelection(self.options[u'vinput'])
            self.SetDisplayName()
            
            return True
        
        return False
    
    
    ## Sets tooltips for device fields
    def OnSelectDevice(self, event=None):
        if event:
            choice = event.GetEventObject()
            choice.SetToolTipString(choice.defs[choice.GetSelection()])
    
    
    ## Updates the device name label
    def OnSelectDisplay(self, event=None):
        if event:
            if event.GetEventObject().GetCount():
                self.SetDisplayName()
    
    
    ## Actions to take when the Options window if shown/hidden
    #  
    #  FIXME: These fields should be set at all times, not just when shown
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
                    
                    if isinstance(C, wx.Choice):
                        # Some wx.Choice field values are stored as integers & need to be converted to string
                        if not isinstance(value, (unicode, str)):
                            value = unicode(value)
                        
                        C.SetStringSelection(value)
                        
                        try:
                            C.SetToolTipString(C.defs[C.GetSelection()])
                        
                        except AttributeError:
                            pass
        
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
    #  
    #  Options fields are initially set by these values
    #  ???: Are fields set every time window is shown/hidden?
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
    
    
    ## TODO: Doxygen
    def SetDisplayName(self):
        d_index = self.sel_display.GetSelection()
        self.dsp_label.SetLabel(self.displays[d_index].GetName())
    
    
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

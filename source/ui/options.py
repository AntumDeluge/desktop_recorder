# -*- coding: utf-8 -*-

## \package ui.options

# MIT licensing
# See: LICENSE.txt


import os, wx

from custom.check       import CheckBox
from custom.choice      import Choice
from custom.combo       import ComboBox
from custom.spin        import SpinCtrl
from custom.textinput   import TextCtrl
from globals            import ident as ID
from globals.cmds       import CMD_arecord
from globals.cmds       import CMD_xrandr
from globals.cmds       import Execute
from globals.device     import AudioDevice
from globals.device     import DisplayDevice
from globals.ffmpeg     import GetContainers
from globals.ffmpeg     import GetEncoders
from globals.ffmpeg     import GetInputDevices
from globals.files      import FILE_lock
from globals.files      import FILE_options
from globals.files      import ReadFile
from globals.icons      import GetIcon
from globals.paths      import PATH_confdir
from globals.paths      import PATH_home


class odef:
    # Video
    VID = u'video'
    VIN = u'vinput'
    VDEV = u'vdevice'
    VFR = u'framerate'
    VCOD= u'vcodec'
    VBR = u'vbitrate'
    VQ = u'quality'

    # Audio
    AUD = u'audio'
    AIN = u'ainput'
    ADEV = u'adevice'
    ACOD = u'acodec'
    ABR = u'abitrate'
    ACHN = u'channels'
    ASR = u'samplerate'

    # Output
    ONAM = u'filename'
    OCNT = u'container'
    OTGT = u'target'


## Class for the options window
class Options(wx.Dialog):
    def __init__(self, parent, window_id, title, style=wx.DEFAULT_DIALOG_STYLE):
        wx.Dialog.__init__(self, parent, window_id, title, size=(300, 450), style=style|wx.RESIZE_BORDER)

        self.SetIcon(GetIcon(u'logo'))

        devices = GetInputDevices()
        vdevices, vdev_defs = devices[u'video']
        adevices, adev_defs = devices[u'audio']

        containers = GetContainers()

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

        self.chk_video = CheckBox(page1, ID.VIDEO, True, u'Include Video', name=odef.VID)

        self.pnl_video = wx.Panel(page1, style=PANEL_BORDER)

        sel_vdev = Choice(self.pnl_video, choices=vdevices, name=odef.VDEV)
        sel_vdev.defs = vdev_defs
        #sel_vdev.SetSelection(0)
        #sel_vdev.SetToolTipString(sel_vdev.defs[0])

        # Filled with list of Display instances when self.InitDisplays is called
        self.displays = []

        self.sel_vin = Choice(self.pnl_video, name=odef.VIN)

        ## FIXME: Does this get reset to default setting???
        self.dsp_label = wx.StaticText(self.pnl_video, label=u'Unnamed device')
        self.dsp_label.Default = self.dsp_label.GetLabel()

        sel_vcodec = Choice(self.pnl_video, name=odef.VCOD)
        sel_vcodec.Priority = (
            u'libx264',
            u'mpeg4',
            u'libxvid',
            u'libtheora',
            u'flv',
            u'ffvhuff',
             u'huffyuv',
            )

        sel_vbitrate = ComboBox(self.pnl_video, name=odef.VBR)

        ti_quality = TextCtrl(self.pnl_video, name=odef.VQ)
        ti_quality.Default = u'-1'

        sel_framerate = Choice(self.pnl_video, name=odef.VFR)
        sel_framerate.Priority = (
            u'30',
            u'29.976',
            u'25',
            u'24.976',
            )

        # *** Audio *** #

        self.chk_audio = CheckBox(page2, ID.AUDIO, True, u'Include Audio', name=odef.AUD)

        self.pnl_audio = wx.Panel(page2, style=PANEL_BORDER)

        self.sel_adev = Choice(self.pnl_audio, choices=adevices, name=odef.ADEV)
        self.sel_adev.defs = adev_defs
        self.sel_adev.SetToolTipString(self.sel_adev.defs[0])

        # Filled with list of audio input device instances
        self.audio_inputs = []

        self.sel_ain = Choice(self.pnl_audio, name=odef.AIN)

        self.aud_label = wx.StaticText(self.pnl_audio, label=u'No devices')
        self.aud_label.Default = self.dsp_label.GetLabel()

        self.sel_adev.Priority = (u'alsa', u'pulse',)

        sel_acodec = Choice(self.pnl_audio, name=odef.ACOD)
        sel_acodec.Priority = (
            u'libfdk_aac',
            u'aac',
            u'libmp3lame',
            u'libvorbis',
            u'pcm_s16le',
            u'libtwolame',
            u'flac',
            )

        sel_bitrate = ComboBox(self.pnl_audio, name=odef.ABR)
        sel_bitrate.Default = u'128k'

        spin_channels = SpinCtrl(self.pnl_audio, name=odef.ACHN)
        spin_channels.Default = 1

        sel_samplerate = Choice(self.pnl_audio, name=odef.ASR)
        sel_samplerate.Default = u'44100'

        # *** Output *** #

        ti_filename = TextCtrl(self, name=odef.ONAM)
        ti_filename.Default = u'out'

        self.sel_container = Choice(self, name=odef.OCNT)
        self.sel_container.Default = u'avi'

        btn_target = wx.Button(self, label=u'Folder')
        self.ti_target = TextCtrl(self, name=odef.OTGT)
        self.ti_target.Default = u'{}/Videos'.format(PATH_home)

        # *** Event handlers *** #

        self.chk_video.Bind(wx.EVT_CHECKBOX, self.ToggleOptions)
        self.chk_audio.Bind(wx.EVT_CHECKBOX, self.ToggleOptions)

        sel_vdev.Bind(wx.EVT_CHOICE, self.OnSelectDevice)
        self.sel_adev.Bind(wx.EVT_CHOICE, self.OnSelectAudioCapture)

        self.sel_vin.Bind(wx.EVT_CHOICE, self.OnSelectDisplay)

        btn_target.Bind(wx.EVT_BUTTON, self.OnSelectTarget)

        wx.EVT_SHOW(self, self.OnShow)

        # *** Pre-layout Actions *** #

        # Set list of available video codecs
        if u'video' in codecs:
            self.SetVideoCodecs(codecs[u'video'])

        # Set list of available audio codecs
        if u'audio' in codecs:
            self.SetAudioCodecs(codecs[u'audio'])

        # *** Layout *** #

        ALIGN_TEXT = wx.ALIGN_CENTER_VERTICAL|wx.LEFT
        ATEXT_LEFT = wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_LEFT

        lyt_video = wx.GridBagSizer(5, 2)

        # Row 1
        row = 0
        lyt_video.Add(wx.StaticText(self.pnl_video, label=u'Display'), (row, 0), flag=ALIGN_TEXT|wx.TOP, border=5)
        lyt_video.Add(self.sel_vin, (row, 1), flag=wx.EXPAND|wx.TOP, border=5)
        lyt_video.Add(self.dsp_label, (row, 2), flag=ATEXT_LEFT|wx.TOP, border=5)

        # Row 2
        row += 1
        lyt_video.Add(wx.StaticText(self.pnl_video, label=u'Capture Device'), (row, 0), flag=ALIGN_TEXT, border=5)
        lyt_video.Add(sel_vdev, (row, 1), (1, 2))

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
        lyt_audio.Add(self.sel_ain, (row, 1), flag=wx.TOP, border=5)
        lyt_audio.Add(self.aud_label, (row, 2), flag=ATEXT_LEFT|wx.TOP, border=5)

        # Row 2
        row += 1
        lyt_audio.Add(wx.StaticText(self.pnl_audio, label=u'Capture Device'), (row, 0), flag=ALIGN_TEXT, border=5)
        lyt_audio.Add(self.sel_adev, (row, 1), (1, 2))

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

        # *** Post-layout Actions *** #

        self.SetMinSize(self.GetSize())

        # Call before ParseOptions
        if not os.path.isfile(FILE_options):
            self.WriteDefaultOptions()

        self.ParseOptions()

        # Fill fields (call after ParseOptions)
        self.InitOptions()

        # FIXME: Need to catch KeyErrors & re-write options file
        self.chk_video.SetValue(self.options[u'video'])
        self.chk_audio.SetValue(self.options[u'audio'])

        # Disables fields if check boxes unchecked
        # Should be called after all fields' settings are initialized
        self.ToggleOptions()

        # Ensure that dialog is not initially displayed
        # FIXME: Writes to options file
        if self.IsShown():
            self.Show(False)


    ## Checks if it is safe to begin recording
    #
    #  At least one of video & audio must be enabled
    def CanRecord(self):
        return self.chk_video.GetValue() or self.chk_audio.GetValue()


    ## Retrieves a list of all available option fields
    def GetOptionFields(self):
        options_fields = [self.chk_video, self.chk_audio,]

        for C in list(self.pnl_video.GetChildren()) + list(self.pnl_audio.GetChildren()):
            if not isinstance(C, wx.StaticText):
                options_fields.append(C)

        return options_fields


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
                self.sel_vin.Append(unicode(X))

            self.sel_vin.SetSelection(self.options[u'vinput'])
            self.SetDisplayName()

            return True

        return False


    ## Initialize field values
    def InitOptions(self):
        field_list = [self.chk_video, self.chk_audio] + list(self.pnl_video.GetChildren()) + list(self.pnl_audio.GetChildren())

        for C in field_list:
            c_name = C.GetName()

            # Compare field names against parsed options keys
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

        # *** Actions to take after all fields are updated *** #
        self.InitDisplays()

        self.OnSelectAudioCapture(self.sel_adev)


    ## Sets tooltips & updates audio input devices list
    def OnSelectAudioCapture(self, event=None):
        if event:
            if isinstance(event, wx.Choice):
                choice = event

            else:
                choice = event.GetEventObject()

            choice.SetToolTipString(choice.defs[choice.GetSelection()])

            capture_device = choice.GetStringSelection()

            retval = False

            # Save index to update for new audio input device list
            saved_index = self.sel_ain.GetSelection()

            # Input device list needs to be refreshed
            self.sel_ain.Clear()

            if capture_device == u'alsa':
                retval = self.SetAlsaInput()

            if self.sel_ain.GetCount():
                if saved_index == wx.NOT_FOUND:
                    self.sel_ain.SetSelection(self.sel_ain.Default)

                else:
                    self.sel_ain.SetSelection(saved_index)

            return retval

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


    ## Opens a directory dialog to select output destination
    def OnSelectTarget(self, event):
        dest = wx.DirDialog(self, defaultPath=os.getcwd(), style=wx.DD_DEFAULT_STYLE|wx.DD_DIR_MUST_EXIST|wx.DD_CHANGE_DIR)
        if dest.ShowModal() == wx.ID_OK:
            self.ti_target.SetValue(dest.GetPath())


    ## Write settings to file when options window is hidden
    #
    #  FIXME: Write settings to file when options window is hidden ...
    #         Do not change values
    def OnShow(self, event=None):
        # Only write options when window is hidden
        if not self.IsShown():
            field_list = [self.chk_video, self.chk_audio] + list(self.pnl_video.GetChildren()) + list(self.pnl_audio.GetChildren())

            # Set & write options when window is hidden
            for C in field_list:
                c_name = C.GetName()

                if isinstance(C, wx.TextCtrl):
                    self.options[c_name] = C.GetValue()
                    continue

                if isinstance(C, (wx.CheckBox, wx.SpinCtrl)):
                    self.options[c_name] = C.GetValue()
                    continue

                if isinstance(C, wx.Choice):
                    self.options[c_name] = C.GetStringSelection()

            self.WriteOptions()

        if event:
            event.Skip()


    ## Reads the options file & stores values
    #
    #  Options fields are initially set by these values
    #  ???: Are fields set every time window is shown/hidden?
    def ParseOptions(self):
        try:
            options = ReadFile(FILE_options, split=True)

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


    ## Reset all option fields to default or priority values
    def ResetDefaults(self):
        for F in self.GetOptionFields():
            F.Reset()


    ## Loads a list of available audio input devices into memory
    def SetAlsaInput(self):
        # Reset input devices
        self.audio_inputs = []

        retval = False

        index = self.sel_adev.FindString(u'alsa')
        if index != wx.NOT_FOUND:
            # alsa requires arecord to find input devices
            if not CMD_arecord:
                self.sel_adev.Delete(index)

            else:
                output = Execute((CMD_arecord, u'--list-devices',)).split(u'\n')

                for LI in output:
                    if LI.startswith(u'card '):
                        card = LI.split(u',')
                        device = card[1].strip()
                        device = device.split(u':')[0].replace(u'device', u'').strip()

                        card = card[0].strip().split(u':')
                        card_name = card[1].strip()
                        card = card[0].replace(u'card', u'').strip()

                        hw_id = u'hw:{},{}'.format(card, device)

                        self.audio_inputs.append(AudioDevice(len(self.audio_inputs), card, card_name))

                        self.sel_ain.Append(hw_id)

                        retval = True

        return retval


    ## Sets the list of audio codecs available from FFmpeg
    #
    #  \param codec_list
    #    \b \e tuple|list : String list of codec names
    #  \return
    #    \b \e bool : True if list was set successfully
    def SetAudioCodecs(self, codec_list):
        for C in self.pnl_audio.GetChildren():
            if isinstance(C, Choice) and C.GetName() == odef.ACOD:
                C.Set(codec_list)

                return True

        return False


    ## TODO: Doxygen
    def SetDisplayName(self):
        d_index = self.sel_vin.GetSelection()
        self.dsp_label.SetLabel(self.displays[d_index].GetName())


    ## Sets the list of video codecs available from FFmpeg
    #
    #  \param codec_list
    #    \b \e tuple|list : String list of codec names
    #  \return
    #    \b \e bool : True if list was set successfully
    def SetVideoCodecs(self, codec_list):
        for C in self.pnl_video.GetChildren():
            if isinstance(C, Choice) and C.GetName() == u'vcodec':
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
        for C in self.GetOptionFields():
            if isinstance(C, usable_types):
                opts_list.append(u'{}={}'.format(C.GetName(), C.Default))

        return self.WriteOptions(opts_list)

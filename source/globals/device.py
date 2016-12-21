# -*- coding: utf-8 -*-

## \package globals.device

# MIT licensing
# See: LICENSE.txt


import os

from globals.files import ReadFile


# These files are used for attempting retrieval of display names
# if wx.Display.GetName fails.
# ???: Should the log number be dynamic?
v_parse_files = {
    u'/var/log/Xorg.0.log': u'Monitor name: ',
    }


## Class representing a physical input device
#  
#  FIXME: This should be abstract
class Device:
    def __init__(self, index, name=None):
        self.index = index
        self.name = name
    
    
    ## Scans specified files to try & set the device's name
    def AutoSetName(self, search_list):
        sfile = None
        sstring = None
        for F in search_list:
            if os.path.isfile(F):
                sfile = ReadFile(F, False)
                
                if search_list[F] in sfile:
                    sstring = search_list[F]
                    sfile = sfile.split(u'\n')
        
        # Default name
        d_name = u'(Unnamed device {})'.format(self.index)
        
        if sstring:
            li_index = 0
            
            for LI in sfile:
                if sstring in LI:
                    if li_index == self.index:
                        d_name = LI.split(sstring)[-1]
                    
                    li_index += 1
                    
                    if li_index > self.index:
                        break
        
        if d_name != self.name:
            self.name = d_name
            
            return True
        
        # Name was not changed, either because no name was
        # found or found name was the same as original.
        return False
    
    
    ## Retrieves the index of the device
    #  
    #  \return
    #    \b \e int : The devices ordered index on the system
    def GetIndex(self):
        return self.index
    
    
    ## Set/Change the name of the device
    def SetName(self, name):
        self.name = name
    
    
    ## Retrieves device name
    #  
    #  \return
    #    \b \e String name
    def GetName(self):
        return self.name


## Class representing physical screen displays & attributes
class DisplayDevice(Device):
    def __init__(self, index, dimensions, primary=False, name=None):
        Device.__init__(self, index, name)
        
        self.dimensions = dimensions
        self.primary = primary
        
        if not self.name:
            self.AutoSetName(v_parse_files)
    
    
    ## Retrieves screen position
    def GetPosition(self):
        return self.dimensions[2:]
    
    
    ## Retrieves screen size
    def GetSize(self):
        return self.dimensions[:2]
    
    
    ## TODO: Doxygen
    def IsPrimary(self):
        return self.primary
    
    
    ## Defines the modes that this display can use
    def LoadModes(self):
        #modes_output = Execute(CMD_xrandr)
        
        print(u'DEBUG: Modes:')
        #print(modes_output)


## Class representing physical audio output device & attributes
class AudioDevice(Device):
    def __init__(self, index, hw_id, name=None):
        Device.__init__(self, index, name)
        
        self.hw_id = hw_id
    
    
    ## Retrieves the hardware identifier string to pass to FFmpegs input option
    def GetHardwareId(self):
        return self.hw_id

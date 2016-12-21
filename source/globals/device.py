# -*- coding: utf-8 -*-

## \package globals.device

# MIT licensing
# See: LICENSE.txt


from getcmd import Execute


## Class representing a physical input device
#  
#  FIXME: This should be abstract
class Device:
    def __init__(self, index, name=None):
        self.index = index
        
        if not name:
            self.name = u'(Unnamed device {})'.format(index)
        
        else:
            self.name = name
    
    
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
    def __init__(self, index, name=None):
        Device.__init__(self, index, name)

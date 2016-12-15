# -*- coding: utf-8 -*-

## \package globals.icons

# MIT licensing
# See: LICENSE.txt


import os, wx

from globals.paths import PATH_icons


## Sets up a wx.Icon for use
#  
#  \param basename
#    \b \e string : Name of image file without file extension (must be PNG)
def GetIcon(basename):
    image_file = u'{}/{}.png'.format(PATH_icons, basename)
    if not os.path.isfile(image_file):
        print(u'Warning: Could not locale image file: {}'.format(image_file))
        
        return None
    
    return wx.Icon(image_file, wx.BITMAP_TYPE_PNG)


## Sets up a wx.Image for use
#  
#  \param basename
#    \b \e string : Name of image file without file extension (must be PNG)
def GetImage(basename):
    image_file = u'{}/{}.png'.format(PATH_icons, basename)
    if not os.path.isfile(image_file):
        print(u'Warning: Could not locale image file: {}'.format(image_file))
        
        return None
    
    return wx.Image(image_file, wx.BITMAP_TYPE_PNG)

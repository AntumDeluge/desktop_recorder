# -*- coding: utf-8 -*-

## \package globals.icons

# MIT licensing
# See: LICENSE.txt


import os, wx

from globals.paths import PATH_icons


## Sets up a wx.Bitmap for use
#  
#  \param basename
#    \b \e string : Name of image file without file extension (must be PNG)
def GetBitmap(basename, width=-1, height=-1):
    image = GetImage(basename, width, height)
    
    return image.ConvertToBitmap()


## Sets up a wx.Icon for use
#  
#  \param basename
#    \b \e string : Name of image file without file extension (must be PNG)
def GetIcon(basename, width=-1, height=-1):
    bitmap = GetBitmap(basename, width, height)
    
    icon = wx.NullIcon
    icon.CopyFromBitmap(bitmap)
    
    return icon


## Sets up a wx.Image for use
#  
#  Uses 'icons' directory to locate images
#  
#  \param basename
#    \b \e string : Name of image file without file extension (must be PNG)
#  \param width
#    \b \e int : Rescales image if greater than 0
#  \param height
#    \b \e int : Rescales image if greater than 0
def GetImage(basename, width=-1, height=-1):
    image_file = u'{}/{}.png'.format(PATH_icons, basename)
    if not os.path.isfile(image_file):
        print(u'Warning: Could not locate image file: {}'.format(image_file))
        
        return None
    
    image = wx.Image(image_file, wx.BITMAP_TYPE_PNG)
    
    if width > 0 or height > 0:
        image.Rescale(width, height, wx.IMAGE_QUALITY_HIGH)
    
    return image

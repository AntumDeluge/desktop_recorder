# -*- coding: utf-8 -*-

## \package globals.files

# MIT licensing
# See: LICENSE.txt


import codecs, os

from globals.paths import PATH_confdir
from globals.paths import PATH_root


ENCODING=u'utf-8'

FILE_lock = u'{}/lock'.format(PATH_confdir)
FILE_options = u'{}/options'.format(PATH_confdir)


## Writes contents to a file
#  
#  \param filename
#    \b \e string : Path to file to be written
#  \param contents
#    \b \e string : Content to be written to file
#  \return
#    \b \e bool : True if contents successfully written to file
def WriteFile(filename, contents):
    # Check if parent directory exists
    parent_dir = os.path.dirname(filename)
    if not os.path.isdir(parent_dir):
        os.makedirs(parent_dir)
    
    # Check for write access to parent directory
    if not os.access(parent_dir, os.W_OK):
        print(u'Error: Cannot write to directory: {}'.format(parent_dir))
        
        return False
    
    # Make sure we are dealing with a string
    if isinstance(contents, (tuple, list,)):
        contents = u'\n'.join(contents)
    
    print(u'DEBUG: Writing to file: {}'.format(filename))
    
    FILE_BUFFER = codecs.open(filename, u'w', encoding=ENCODING)
    
    if contents != None:
        FILE_BUFFER.write(contents)
    
    FILE_BUFFER.close()
    
    # Failsafe
    if not os.path.isfile(filename):
        return False
    
    return True


## Creates an empty file
#  
#  \param filename
#    \b \e string : Path to file to be created
#  \return
#    \b \e bool : True if successful, False otherwise or if file already exists
def WriteEmptyFile(filename):
    if os.path.isfile(filename):
        return False
    
    return WriteFile(filename, None)


## Reads contents of a file
#  
#  \param filename
#    \b \e string : Path to file to be read
#  \param lines
#    \b \e bool : If True, returned vale will be a line separated tuple
def ReadFile(filename, split=True):
    # Look for file in app root directory if 'filename' is not a path
    if u'/' not in filename:
        filename = u'{}/{}'.format(PATH_root, filename)
    
    if not os.path.isfile(filename) or not os.access(filename, os.R_OK):
        print(u'Warning: Could not read file: {}'.format(filename))
        
        return
    
    print(u'DEBUG: Reading file: {}'.format(filename))
    
    FILE_BUFFER = codecs.open(filename, u'r', encoding=ENCODING)
    # contents is joined into a string so whitespace & empty lines can be stripped
    contents = u'\n'.join(FILE_BUFFER).strip(u' \t\n')
    FILE_BUFFER.close()
    
    if split:
        contents = contents.split(u'\n')
    
    return contents

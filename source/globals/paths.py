# -*- coding: utf8 -*-

## \package globals.paths

# MIT licensing
# See: LICENSE.txt


import os


# Application paths
PATH_globals = os.path.dirname(__file__)
PATH_root = os.path.dirname(PATH_globals)

# System paths
PATH_home = os.getenv(u'HOME')
PATH_confdir = u'{}/.config/desktop_recorder'.format(PATH_home)

# System files
FILE_config = u'{}/config'.format(PATH_confdir)

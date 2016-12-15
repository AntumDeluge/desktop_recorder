# -*- coding: utf8 -*-

## \package globals.paths

# MIT licensing
# See: LICENSE.txt


import os


# Application paths
PATH_globals = os.path.dirname(__file__)
PATH_root = os.path.dirname(PATH_globals)
PATH_icons = u'{}/icons'.format(PATH_root)

# System paths
PATH_home = os.getenv(u'HOME')
PATH_confdir = u'{}/.config/desktop_recorder'.format(PATH_home)

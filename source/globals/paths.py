# -*- coding: utf8 -*-

## \package globals.paths

# MIT licensing
# See: LICENSE.txt


import os


PATH_globals = os.path.dirname(__file__)
PATH_root = os.path.dirname(PATH_globals)
PATH_home = os.getenv(u'HOME')
PATH_config = u'{}/.config/desktop_recorder'.format(PATH_home)

# -*- coding: utf-8 -*-

## \package globals.debug

# MIT licensing
# See: LICENSE.txt


from globals.commandline import GetOption


class dmode:
    QUIET = 0
    INFO = 1
    WARN = 2
    ERROR = 3
    DEBUG = 4

    name = {
        QUIET: u'QUIET',
        INFO: u'INFO',
        WARN: u'WARN',
        ERROR: u'ERROR',
        DEBUG: u'DEBUG',
        }


LogLevel = dmode.ERROR

def SetLogLevel(lvl):
    global LogLevel

    if isinstance(lvl, int):
        LogLevel = lvl
        return True

    if isinstance(lvl, (unicode, str)):
        if lvl.isnumeric():
            LogLevel = int(lvl)
            return True

        for L in dmode.name:
            if lvl.upper() == dmode.name[L]:
                LogLevel = L
                return True

    return False

new_level = GetOption(u'log-level')
if new_level != None:
    SetLogLevel(new_level)


def dprint(msg, mode, module=None, line=None, newline=True):
    if mode <= LogLevel:
        if module != None:
            if line != None:
                msg = u'[{}:{}] {}'.format(module, line, msg)

        mode = dmode.name[mode]

        if newline:
            mode = u'\n{}'.format(mode)

        print(u'{}: {}'.format(mode, msg))


def pDebug(msg, module=None, line=None, newline=True):
    dprint(msg, dmode.DEBUG, module, line, newline)


def pError(msg, module=None, line=None, newline=True):
    dprint(msg, dmode.ERROR, module, line, newline)


def pInfo(msg, module=None, line=None, newline=True):
    dprint(msg, dmode.INFO, module, line, newline)


def pWarn(msg, module=None, line=None, newline=True):
    dprint(msg, dmode.WARN, module, line, newline)

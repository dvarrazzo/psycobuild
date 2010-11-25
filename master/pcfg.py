"""Private settings file access."""

import os

from twisted.python import log

pcfg = {}
if os.path.exists('./private_settings.py'):
    log.msg("reading private settings file")
    execfile('./private_settings.py', pcfg)


def get(key, default=None):
    return pcfg.get(key, default)

def get_password(name):
    pwds = pcfg['passwords']
    return pwds[name]

"""Private settings file access."""

import os

from twisted.python import log

builddir = os.path.dirname(__file__)
fn = os.path.abspath(builddir + "/../private_settings.py")

pcfg = {}
if os.path.exists(fn):
    log.msg("reading private settings file %s", fn)
    execfile(fn, pcfg)
else:
    log.msg("private settings file not found: %s", fn)


def get(key, default=None):
    return pcfg.get(key, default)

def get_password(name):
    pwds = pcfg['passwords']
    return pwds[name]

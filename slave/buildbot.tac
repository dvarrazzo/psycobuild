# -*- python -*-
# ex: set syntax=python:

# These parameters must be set in ``private_settings.py``.
slave_name = ''
slave_password = ''

master_host = 'localhost'
master_port = 9989

basedir = r'/var/lib/buildbot/psycobuild/slave'
keepalive = 600
usepty = 0
umask = None
maxdelay = 300
rotateLength = 1000000
maxRotatedFiles = None

import os
from twisted.python import log
if os.path.exists('./private_settings.py'):
    execfile('./private_settings.py')

if not slave_name:
    raise Exception("slave name not set")

from twisted.application import service
from buildbot.slave.bot import BuildSlave

application = service.Application('buildslave')
try:
  from twisted.python.logfile import LogFile
  from twisted.python.log import ILogObserver, FileLogObserver
  logfile = LogFile.fromFullPath("twistd.log", rotateLength=rotateLength,
                                 maxRotatedFiles=maxRotatedFiles)
  application.setComponent(ILogObserver, FileLogObserver(logfile).emit)
except ImportError:
  # probably not yet twisted 8.2.0 and beyond, can't set log yet
  pass
s = BuildSlave(master_host, master_port, slave_name, slave_password, basedir,
               keepalive, usepty, umask=umask, maxdelay=maxdelay)
s.setServiceParent(application)


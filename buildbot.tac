# -*- python -*-
# ex: set syntax=python:


# basedir = r'/var/lib/buildbot/psycobuild/master'
basedir = r'/home/psycoweb/psycobuild/var/master'

rotateLength = 1000000
maxRotatedFiles = None

import os
project_dir = os.path.dirname(os.path.abspath(__file__))
configfile = os.path.join(project_dir, 'settings.py')

from twisted.application import service
from buildbot.master import BuildMaster

application = service.Application('buildmaster')
try:
  from twisted.python.logfile import LogFile
  from twisted.python.log import ILogObserver, FileLogObserver
  logfile = LogFile.fromFullPath("twistd.log", rotateLength=rotateLength,
                                 maxRotatedFiles=maxRotatedFiles)
  application.setComponent(ILogObserver, FileLogObserver(logfile).emit)
except ImportError:
  # probably not yet twisted 8.2.0 and beyond, can't set log yet
  pass
BuildMaster(basedir, configfile).setServiceParent(application)


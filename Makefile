# control makefile for psycobuild master

PYTHON ?= python

MASTER_DIR ?= $(shell grep -E '^basedir'  buildbot.tac  | sed -e "s/.*'\(.*\)'/\1/")

PY_VER = $(shell $(PYTHON) -c "import sys; print '%d.%d' % sys.version_info[:2]")

BUILDBOT ?= $(shell $(PYTHON) -c "import buildbot; print buildbot.__file__.rsplit('/', 2)[0] + '/EGG-INFO/scripts/buildbot'")

start:
	twistd --no_save -y buildbot.tac

stop:
	kill `cat twistd.pid`

reconfig:
	kill -HUP `cat twistd.pid`

log:
	tail -f twistd.log

create-master:
	$(PYTHON) $(BUILDBOT) create-master $(MASTER_DIR)

install-buildbot:
	mkdir -p lib
	PYTHONPATH=lib easy_install -Z -d lib buildbot

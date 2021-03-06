Psycopg Buildbot
================

This project contains configuration for master and slaves to build and test
Psycopg on supported platforms.

If you are interested in providing a build slave, for example if you want to
be sure that Psycopg works as expected on your platform or with your server
configuration, you can provide a specific build slave.

The code is currently tested with *buildbot 0.8.3p1*. You can try your luck
with a newer version, but if you are not into gambling you can specify the
release and install its dependencies using::

    sudo easy_install buildbot==0.8.3p1

In order to create a slave you will need to:

- configure your slave... in the master: see `Configuring a slave`_,
- run a local copy of the master: see `Running the master`_,
- create a new slave and run it: see `Creating a slave`_,
- go on ``http://localhost:8010`` and use the web interface to test the slave
  configuration.

Once you are happy send us a patch containing the configuration and the
password for the slave.


Configuring a slave
-------------------

Surprisingly enough, the slaves configuration resides in the master. So, if
you want to create a new slave (e.g. to test Python 2.7 against PostgreSQL 9.1
on Slackware 64 bit) you need to:

- define the slave configuration in ``psycobuild/slaves.py``,
- add your slave to the ``slaves`` setting in ``settings.py``,
- add jobs for the slave in the ``builders`` settings.

These files already contain a few configured slave: use them to understand how
to configure yours.

Once you have configured your slave, send us a patch to allow us to send it
the correct jobs.


Running the master
------------------

The official master runs on maya.initd.org. You may want to run a master on
your box in order to test a build process:

- check out this project code,
- create a build directory,
- edit ``buildbot.tac`` and set the build directory as ``basedir``,
- use ``make start`` to start the build master,
- take a look at ``twistd.log`` to check the system started correctly.


Creating a slave
----------------

Because all the configuration is in the master, the slave itself has little
configuration: it only knows how to reach the master. If you only need a slave
you don't even need the buildbot package: you may use ``easy_install
buildbot-slave`` to get only the slave part.

- Create an unprivileged user ``buildbot``.
- Create a dir ``/var/lib/buildbot`` and set ``buildbot`` as owner.
- Decide a name for the slave, e.g. after your host name.
- Make a random password, e.g. with::

    python -c "import hashlib; print hashlib.md5(open('/dev/urandom').read(16)).hexdigest()"

- Create the slave::

    sudo -u buildbot buildbot create-slave /var/lib/buildbot/NAME maya.initd.org:49989 NAME PASSWORD

  (the command may be different using the ``buildbot-slave`` package).

- Add informations to ``admin`` and ``host`` in the ``info`` dir

To run the slave you can use::

    sudo -u buildbot twistd --nodaemon --no_save -y buildbot.tac

in the slave directory. The slave actions are logged in ``twistd.log``.

You can use ``localhost:9899`` instead of ``maya`` in order to test the slave
with a master of your own. You can change the values later in the
``buildbot.tac`` file. In order to allow the slave to connect to your local
master you must add the slave password to the ``private_settings.py`` file.


Starting the slave with upstart
-------------------------------

In order to have your slave automatically start with your machine, you may use
an upstart (such as ``/etc/init/psycoslave.conf``) script similar to this one::

    description     "psycopg buildbot slave"

    start on runlevel [2345]
    stop on runlevel [!2345]

    respawn

    script
        cd /var/lib/buildbot/psycoslave
        sudo -u buildbot twistd --nodaemon --no_save -y buildbot.tac
    end script


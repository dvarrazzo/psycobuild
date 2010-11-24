Psycopg Buildbot
================

This project contains configuration for master and slaves to build and test
Psycopg on supported platforms.

If you are interested in providing a build slave, for example if you want to
be sure that Psycopg works as expected on your platform or with your server
configuration, you can provide a build slave.


Quick start
-----------

- Checkout the code from ``git://github.com/dvarrazzo/psycobuild.git``
- Copy ``slaves/personal_settings.py.example`` into
  ``slaves/personal_settings.py`` and set a name for it.
- Configure the parameters of your slave into ``master/master.cfg``. See the
  ``ikki`` slave for an example of what to do. Use your slaves to create new
  builders: again, check what's already available in the file to see how.
- Open two shell, cd in ``master`` and in ``slave`` respectively
- First in the ``master`` shell, then in the ``slave``, type ``make start``.
  If your platform doesn't support ``make``, take a look at the ``Makefile``
  files to see what it would have done. The logs will be saved to
  ``twistd.log`` in the respective directories.
- Use the web interface to force test builds.
- Once you are happy, send us a patch to add your slave configuration.

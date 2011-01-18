"""Buildbot configuration file for Psycopg."""

import os

from psycobuild import pcfg; reload(pcfg)

c = BuildmasterConfig = {}


####### PROJECT IDENTITY

c['projectName'] = "Psycopg"
c['projectURL'] = "http://initd.org/psycopg"
c['buildbotURL'] = pcfg.get('buildbotUrl', "http://localhost:8010/")


####### BUILDSLAVES

from psycobuild import slaves; reload(slaves)

c['slaves'] = [ slaves.ikki, slaves.win2k_vbox, slaves.centos_55_64, slaves.ubuntu32, slaves.ubuntu64 ]
c['slavePortnum'] = pcfg.get('slavePortnum', 9989)


####### CHANGESOURCES

from buildbot.changes.pb import PBChangeSource

c['change_source'] = PBChangeSource()


####### SCHEDULERS

from buildbot.scheduler import Scheduler, Triggerable

c['schedulers'] = []

# Run the test after the sdist is ready.
sdist_trigger = Triggerable(name='test-sdist', builderNames=[])

c['schedulers'].append(sdist_trigger)



####### BUILDERS

repourl = "git://src.develer.com/users/piro/psycopg2.git"
#repourl = "/home/piro/dev/psycopg2/"
branch = "python2"

from buildbot.config import BuilderConfig
from buildbot.process.factory import BuildFactory
from buildbot.process.properties import WithProperties
from buildbot.steps.source import Git
from buildbot.steps.shell import Compile, Test, ShellCommand, SetProperty
from buildbot.steps.trigger import Trigger
from buildbot.steps.transfer import FileUpload, FileDownload

def make_sdist(slave):
    """Create the builder that makes the sdist."""
    make = ['make']
    f = BuildFactory()
    f.addStep(Git(repourl=repourl, branch=branch))
    f.addStep(SetProperty(
        command=r"""grep PSYCOPG_VERSION setup.py | head -1 | sed -e "s/.*'\(.*\)'/\1/" """,
        property="version"))
    f.addStep(Compile(command=make + ["package"]))
    f.addStep(ShellCommand(
        description="making env", descriptionDone="env",
        command=make + ["env"]))
    f.addStep(ShellCommand(
        description="making docs", descriptionDone="docs",
        command=make + ["docs"]))
    f.addStep(ShellCommand(
        description="making sdist", descriptionDone="sdist",
        command=make + ["sdist"]))
    f.addStep(FileUpload(
        slavesrc=WithProperties("dist/psycopg2-%s.tar.gz", "version"),
        masterdest=WithProperties(
            "%s/public_html/dist/psycopg2-%%s.tar.gz" % basedir, 'version')))

    f.addStep(Trigger(schedulerNames=['test-sdist'],
        copy_properties=['version']))

    b = BuilderConfig(
        name="sdist",
        slavename=slave.slavename,
        factory=f)

    return b

def make_test_sdist(slave):
    builders = {}   # py name -> builder

    for py, pg in sorted(slave.properties['tested_pairs']):

        py = slave.properties['pys'][py]
        pg = slave.properties['pgs'][pg]

        # Download and build only once per python instance
        if py.name in builders:
            b = builders[py.name]
            f = b.factory

        else:
            f = BuildFactory()
            b = builders[py.name] = BuilderConfig(
                name="test-py%s-%s" % (py.name, slave.slavename),
                slavename=slave.slavename,
                factory=f)
            sdist_trigger.builderNames.append(b.name)

            make = ["make", "PYTHON=%s" % py.executable]
            if py.pg_config:
                make += ["PG_CONFIG=" + py.pg_config]

            f.addStep(FileDownload(
                mastersrc=WithProperties(
                    "%s/public_html/dist/psycopg2-%%s.tar.gz" % basedir,
                    'version'),
                slavedest=WithProperties("psycopg2-%s.tar.gz", 'version')))
            f.addStep(ShellCommand(
                description="clearing", descriptionDone="clear",
                command=["rm", "-rf",
                    WithProperties("psycopg2-%s", "version")]))
            f.addStep(ShellCommand(
                description="unpacking", descriptionDone="unpack",
                command=["tar", "xzvf",
                    WithProperties("psycopg2-%s.tar.gz", 'version')]))
            f.addStep(Compile(command=make + ["package"],
                workdir=WithProperties("build/psycopg2-%s", "version")))

            if py.pg_config:
                f.addStep(SetProperty(
                    command="%s --libdir" % py.pg_config,
                    property="libdir"))

        # Add tests on this factory

        # Make it found the libpq we compiled against
        env = pg.get_test_env()
        if py.pg_config:
            env['LD_LIBRARY_PATH'] = WithProperties("%s", "libdir")

        # ensure to link to the intended libpq version
        f.addStep(Test(command=make + ["check"],
            description="testing %s" % pg.name,
            descriptionDone="test %s" % pg.name,
            workdir=WithProperties("build/psycopg2-%s", "version"),
            env=env, locks=[pg.get_lock()]))

        for lib in py.green_libs or ['1']:
            genv=env.copy()
            genv['PSYCOPG2_TEST_GREEN'] = lib
            libname = lib == '1' and 'green' or lib
            f.addStep(Test(command=make + ["check"],
                description="%s testing %s" % (libname, pg.name),
                descriptionDone="%s test %s" % (libname, pg.name),
                workdir=WithProperties("build/psycopg2-%s", "version"),
                env=genv, locks=[pg.get_lock()]))

    for name, b in sorted(builders.iteritems()):
        yield b

def make_wininst(slave):
    """Create the builder that makes a wininst."""
    for py in slave.properties['pys'].itervalues():
        name = "wininst-" + py.name
        pg_config = (py.pg_config
            and ['--pg-config', py.pg_config] or [])
        compiler = (py.compiler
            and ['--compiler', py.compiler] or [])

        f = BuildFactory()
        f.addStep(Git(repourl=repourl, branch=branch))
        f.addStep(ShellCommand(
            description="clearing", descriptionDone="clean",
            command=[py.executable, "-c",
                "import shutil; shutil.rmtree('dist', ignore_errors=True)"]))
        f.addStep(ShellCommand(
            description="making wininst", descriptionDone="wininst",
            command=[py.executable, "setup.py", "build_ext"]
                + pg_config + compiler + ["bdist_wininst"]))
        f.addStep(SetProperty(
            command=[py.executable, "-c",
                'import os; print os.listdir("dist")[0]'],
            property="installer"))
        f.addStep(FileUpload(
            slavesrc=WithProperties("dist/%s", "installer"),
            masterdest=WithProperties(
                "%s/public_html/dist/%%s" % basedir, 'installer')))

        f.addStep(Trigger(schedulerNames=[name],
            copy_properties=['installer']))

        # Create a trigger for the test slave interested to this package
        trigger = Triggerable(name=name, builderNames=[])
        c['schedulers'].append(trigger)

        b = BuilderConfig(
            name=name,
            slavename=slave.slavename,
            factory=f)

        yield b

def make_test_wininst(slave):
    builders = {}  # py.name -> builder

    for py, pg in sorted(slave.properties['tested_pairs']):

        py = slave.properties['pys'][py]
        pg = slave.properties['pgs'][pg]

        # Download and build only once per python instance
        if py.name in builders:
            b = builders[py.name]
            f = b.factory
        else:
            env = {}
            env['PYTHONPATH'] = 'PLATLIB;PLATLIB\\psycopg2'

            # TODO: required for the libpq.dll, not for the static lib
            if py.pg_config:
                env['PATH'] = os.path.dirname(py.pg_config)

            f = BuildFactory()
            b = BuilderConfig(
                # TODO: should be more specific?
                name="test-win-py%s-%s"
                    % (py.name, slave.slavename),
                slavename=slave.slavename,
                factory=f,
                env=env)

            builders[py.name] = b

            f.addStep(FileDownload(
                mastersrc=WithProperties(
                    "%s/public_html/dist/%%s" % basedir, 'installer'),
                slavedest=WithProperties("%s", 'installer')))
            f.addStep(ShellCommand(
                description="unpacking", descriptionDone="unpack",
                # TODO: replace with a portable script
                command=["C:/python26/python.exe", "-c", "import sys, zipfile; "
                "zipfile.ZipFile(sys.argv[1]).extractall()",
                    WithProperties("%s", 'installer')]))

            # Be ready for a package with the required characteristics
            tname = "wininst-" + py.name
            for t in c['schedulers']:
                if t.name == tname:
                    t.builderNames.append(b.name)
                    break
            else:
                raise Exception("can't find trigger %s" % tname)

        # Test against the different pg servers.
        env = pg.get_test_env()

        f.addStep(Test(command=[py.executable,
            "PLATLIB/psycopg2/tests/__init__.py", "--verbose"],
                description="testing %s" % pg.name,
                descriptionDone="test %s" % pg.name,
            env=env, locks=[pg.get_lock()]))

        for lib in py.green_libs or ['1']:
            genv=env.copy()
            genv['PSYCOPG2_TEST_GREEN'] = lib
            libname = lib == '1' and 'green' or lib
            f.addStep(Test(command=[py.executable,
                "PLATLIB/psycopg2/tests/__init__.py", "--verbose"],
                description="%s testing %s" % (libname, pg.name),
                descriptionDone="%s test %s" % (libname, pg.name),
                env=genv, locks=[pg.get_lock()]))

    for name, b in sorted(builders.iteritems()):
        yield b


builders = c['builders'] = []
builders.append(make_sdist(slaves.ikki))
# builders += list(make_test_sdist(slaves.ikki))
builders += list(make_test_sdist(slaves.ubuntu32))
builders += list(make_test_sdist(slaves.ubuntu64))
builders += list(make_test_sdist(slaves.centos_55_64))

builders += list(make_wininst(slaves.win2k_vbox))
builders += list(make_test_wininst(slaves.win2k_vbox))

####### STATUS TARGETS

c['status'] = []

from buildbot.status import html
http_port = pcfg.get('webStatusPort', 'tcp:8010:interface=127.0.0.1')
allowForce = pcfg.get('webAllowForce', True)
c['status'].append(html.WebStatus(http_port=http_port, allowForce=allowForce))


####### DEBUGGING OPTIONS

# c['debugPassword'] = "debugpassword"

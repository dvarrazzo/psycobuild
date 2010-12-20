"""Objects used to define the testing configuration for Psycopg."""

from buildbot.buildslave import BuildSlave
from buildbot.locks import MasterLock


class PythonInstance(object):
    """Represent a Python installation on a slave."""
    def __init__(self, name, executable='python',
            pg_config=None, compiler=None, green_libs=()):
        # A short name to identify this install on the slave
        # E.g. 2.6, 2.4_d
        self.name = name

        # The full path of the Python executable
        self.executable = executable

        # The full path of the pg_config program.
        # Only useful if this Python is used to build Psycopg
        self.pg_config = pg_config

        # The compiler to use to build Psycopg, if not the default
        self.compiler = compiler

        # Green libraries to test against.
        # If none defined test against the wait_select().
        self.green_libs = green_libs

    def __repr__(self):
        d = self.__dict__.copy()
        name = d.pop('name')
        return "%s(%r, %s)" % (
            self.__class__.__name__,
            self.name,
            ", ".join("%s=%r" % p for p in sorted(d.iteritems())))


class PostgresInstance(object):
    """Represent a database to connect to.

    Different instances can represent the same database accessed using
    different connection strings.
    """
    def __init__(self, name, id, dbname='psycopg2_test',
            host=None, port=None, user=None):
        # A short name to identify this PG instance on the slave
        # E.g. 8.2, 8.4_ger
        self.name = name

        # A global identifier to univocally identify the database across
        # all the servers, e.g. to provide mutual exclusion.
        self.id = id

        # Connection parameters
        self.dbname = dbname
        self.host = host
        self.port = port
        self.user = user

    def __repr__(self):
        d = self.__dict__.copy()
        name = d.pop('name')
        id = d.pop('id')
        return "%s(%r, %r, %s)" % (
            self.__class__.__name__,
            self.name, self.id,
            ", ".join("%s=%r" % p for p in sorted(d.iteritems())))

    def get_test_env(self):
        """Create a new dict with the env variables to configure the tests."""
        env = {}
        if self.dbname: env['PSYCOPG2_TESTDB'] = self.dbname
        if self.host: env['PSYCOPG2_TESTDB_HOST'] = self.host
        if self.port: env['PSYCOPG2_TESTDB_PORT'] = str(self.port)
        if self.user: env['PSYCOPG2_TESTDB_USER'] = self.user
        return env

    _locks = {}

    def get_lock(self):
        """Return a lock for database access mutual exclusion."""
        lock = self._locks.get(self.id)
        if lock is None:
            lock = self._locks[self.id] = MasterLock(self.id)

        return lock.access('exclusive')


def create_slave(name, **kwargs):
    import pcfg
    passwd = pcfg.get_password(name)

    props = kwargs.setdefault('properties', {})
    props['pys'] = {}
    props['pgs'] = {}
    props['tested_pairs'] = []

    slave = BuildSlave(name, passwd, **kwargs)
    return slave


def add_python(slave, py):
    pys = slave.properties['pys']
    assert py.name not in pys
    pys[py.name] = py

def add_postgres(slave, pg):
    pgs = slave.properties['pgs']
    assert pg.name not in pgs
    pgs[pg.name] = pg

def add_test(slave, py_name, pg_name):
    assert py_name in slave.properties['pys']
    assert pg_name in slave.properties['pgs']
    pairs = slave.properties['tested_pairs']
    assert (py_name, pg_name) not in pairs
    pairs.append((py_name, pg_name))




"""Definition of slaves used in Psycopg building and testing."""

import psycobuild; reload(psycobuild)
from psycobuild import PythonInstance, PostgresInstance
from psycobuild import create_slave, add_postgres, add_python, add_test


# piro's development laptop

ikki = create_slave("ikki", max_builds=2)

add_python(ikki, PythonInstance('2.4',
    executable="/usr/local/py24/bin/python2.4", ))
add_python(ikki, PythonInstance('2.5',
    executable="/usr/local/py251/bin/python2.5",
    green_libs=["eventlet"], ))
add_python(ikki, PythonInstance('2.6',
    executable="python2.6",
    pg_config='/usr/local/pgsql/bin/pg_config', ))

add_postgres(ikki, PostgresInstance('7.4', 'ikki-7.4',
    host='localhost', port=54374, ))
add_postgres(ikki, PostgresInstance('8.0', 'ikki-8.0',
    host='localhost', port=54380, ))
add_postgres(ikki, PostgresInstance('8.4', 'ikki-8.4',
    host='localhost', ))
add_postgres(ikki, PostgresInstance('9.0', 'ikki-9.0',
    host='localhost', port=54390, ))

add_test(ikki, '2.4', '8.0')
add_test(ikki, '2.4', '8.4')
add_test(ikki, '2.5', '8.4')
add_test(ikki, '2.6', '8.0')
add_test(ikki, '2.6', '8.4')
add_test(ikki, '2.6', '9.0')


# CentOS 5.5 x86_64 failed the 2.3.0 build

centos_55_64  = create_slave("centos-55-64", max_builds=1)

add_python(centos_55_64, PythonInstance('2.4',
    executable="python2.4", ))
add_postgres(centos_55_64, PostgresInstance('7.4', 'ikki-7.4',
    host='192.168.1.4', user='piro', port=54374))
add_postgres(centos_55_64, PostgresInstance('8.0', 'ikki-8.0',
    host='192.168.1.4', user='piro', port=54380))
add_postgres(centos_55_64, PostgresInstance('8.4', 'ikki-8.4',
    host='192.168.1.4', user='piro', ))

add_test(centos_55_64, '2.4', '7.4')
add_test(centos_55_64, '2.4', '8.0')
add_test(centos_55_64, '2.4', '8.4')


# a win2k vm on ikki, mostly used to test psycobuild itself

win2k_vbox = create_slave("win2k-vbox", max_builds=1)

add_python(win2k_vbox, PythonInstance('2.5',
    executable="C:/python25/python.exe",
    pg_config='C:/pgsql90/bin/pg_config.exe',
    compiler='mingw32', ))

add_postgres(win2k_vbox, PostgresInstance('7.4', 'ikki-7.4',
    host='10.0.2.2', user='piro', port=54374))
add_postgres(win2k_vbox, PostgresInstance('8.4', 'ikki-8.4',
    host='10.0.2.2', user='piro', ))
add_postgres(win2k_vbox, PostgresInstance('9.0', 'ikki-9.0',
    host='10.0.2.2', user='piro', port=54390))

add_test(win2k_vbox, '2.5', '7.4')
add_test(win2k_vbox, '2.5', '8.4')
add_test(win2k_vbox, '2.5', '9.0')


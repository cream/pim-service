#!/usr/bin/env python

from distutils.core import setup
from distutils.command.install_scripts import install_scripts

class post_install(install_scripts):

    def run(self):
        install_scripts.run(self)

        from shutil import move
        for i in self.get_outputs():
            n = i.replace('.py', '')
            move(i, n)
            print "moving '{0}' to '{1}'".format(i, n)

ID = 'org.cream.PIM'

data_files = [
    ('share/cream/{0}'.format(ID), ['src/manifest.xml']),
    ('share/dbus-1/services', ['src/org.cream.PIM.service'])
]

setup(
    name = 'cream-pim-service',
    version = '0.1',
    author = 'The Cream Project (http://cream-project.org)',
    url = 'http://github.com/cream/pim-service',
    package_dir = {'pim': 'src/pim'},
    packages = ['pim'],
    data_files = data_files,
    cmdclass={'install_scripts': post_install},
    scripts = ['src/pim-service.py']
)

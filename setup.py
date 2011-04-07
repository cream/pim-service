#!/usr/bin/env python

import os

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



def collect_data_files():

    extensions = ['tasks']
    data_files = []

    for extension in extensions:
        for directory, directories, files in os.walk('src/{0}'.format(extension)):
            rel_dir = directory.replace('src/{0}'.format(extension), '')
            for file_ in files:
                data_files.append((
                        os.path.join('share/cream/org.cream.PIM/extensions/{0}'.format(extension), rel_dir),
                        [os.path.join(directory, file_)]
                ))

    return data_files

ID = 'org.cream.PIM'

data_files = [
    ('share/cream/{0}'.format(ID), ['src/manifest.xml']),
    ('share/dbus-1/services', ['src/org.cream.PIM.service'])
]
data_files.extend(collect_data_files())

setup(
    name = 'cream-pim-service',
    version = '0.1',
    author = 'The Cream Project (http://cream-project.org)',
    url = 'http://github.com/cream/pim-service',
    package_dir = {'pim': 'src'},
    packages = ['pim'],
    data_files = data_files,
    cmdclass={'install_scripts': post_install},
    scripts = ['src/pim-service.py']
)

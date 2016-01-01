#!/usr/bin/env python

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import os

from setuptools import setup, find_packages


FOLDER_PATH = os.path.dirname(os.path.realpath(__file__))
_, FOLDER_NAME = os.path.split(FOLDER_PATH)
NAME = FOLDER_NAME


setup(
    name=NAME,
    version='0.1.1',
    description='virtualenv with less hassle',
    url='http://autovenv.readthedocs.org',
    long_description='Virtual environments are great, but they can be a bit annoying to create, manage, and switch between. autovenv takes the annoyance away.\n\nFull documentation is at https://autovenv.readthedocs.org',
    author='Robert Lechte',
    author_email='robertlechte@gmail.com',
    install_requires=[
        'virtualenv',
    ],
    packages=find_packages(),
    classifiers=[
        'Development Status :: 3 - Alpha'
    ],
    scripts=['scripts/autovenv.sh'],
    entry_points={
        'console_scripts': [
            'autovenv = autovenv:do_command',
        ],
    }
)

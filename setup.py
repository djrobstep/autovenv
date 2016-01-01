#!/usr/bin/env python

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import os
import io

from setuptools import setup, find_packages


FOLDER_PATH = os.path.dirname(os.path.realpath(__file__))
_, FOLDER_NAME = os.path.split(FOLDER_PATH)
NAME = FOLDER_NAME


setup(
    name=NAME,
    version='0.1.0',
    description='virtualenv with less hassle',
    url='http://autovenv.readthedocs.org',
    long_description=io.open('README.rst').read(),
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

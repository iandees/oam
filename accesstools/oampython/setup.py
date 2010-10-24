#!/usr/bin/env python

from distutils.core import setup

setup(
    name='OAM',
    version='0.1',
    description='OpenAerialMap',
    author='Schuyler Erle',
    author_email='schuyler@nocat.net',
    url='http://github.com/oam/oam/',
    packages=['oam'],
    scripts=['scripts/oam-post', 'scripts/oam-fetch', 'scripts/oam2vrt']
)

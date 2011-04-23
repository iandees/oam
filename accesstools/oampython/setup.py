#!/usr/bin/env python

from distutils.core import setup

setup(
    name='OAM',
    version='0.2.1',
    description='Client library for OpenAerialMap (http://oam.osgeo.org)',
    author='Schuyler Erle',
    author_email='schuyler@nocat.net',
    url='https://github.com/oam/oam/tree/master/accesstools/oampython',
    packages=['oam'],
    scripts=['scripts/oam-post', 'scripts/oam-fetch', 'scripts/oam2vrt']
)

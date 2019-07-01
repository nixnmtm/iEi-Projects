#!/usr/bin/env python

from distutils.core import setup

setup(name='pzlDevScan',
      version='1.0',
      description='Puzzle Scanning utility: Device Side',
      author='Nixon Raj',
      author_email='nixon@ieiworld.com',
      url='https://www.python.org/sigs/distutils-sig/',
      packages=['device_client'],
      entry_points={'console_scripts': ['scandev = device_client.device_scan',],},
     )
#!/usr/bin/env python

from setuptools import setup

setup(name='pysumix',
	  description='Sumix SMX API and data writing and live display',
	  author='Michael Hirsch',
	  url='https://github.com/scivision/pysumix',
	  install_requires=['tifffile','pathlib2'],
      packages=['pysumix'],
	  )

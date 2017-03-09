#!/usr/bin/env python
from setuptools import setup

req = ['tifffile','nose','numpy','scipy','matplotlib','h5py']

setup(name='pysumix',
	  description='Sumix SMX API and data writing and live display',
	  author='Michael Hirsch, Ph.D.',
	  url='https://github.com/scivision/pysumix',
	  install_requires=req,
      packages=['pysumix'],
	  )

#!/usr/bin/env python3

from setuptools import setup 

with open('README.rst','r') as f:
	long_description = f.read()
	
setup(name='pysumix',
      version='0.1',
	  description='Sumix SMX API and data writing and live display',
	  long_description=long_description,
	  author='Michael Hirsch',
	  url='https://github.com/scivision/pysumix',
	  install_requires=['h5py','tifffile','nose'],
      packages=['pysumix'],
	  )
	  	  

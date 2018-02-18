#!/usr/bin/env python
from setuptools import setup, find_packages

install_requires = ['tifffile','numpy','scipy','imageio']
tests_require = ['nose','coveralls']

setup(name='pysumix',
      version='0.5.0',
	  description='Sumix SMX API and data writing and live display',
      long_description=open('README.rst').read(),
	  author='Michael Hirsch, Ph.D.',
	  url='https://github.com/scivision/pysumix',
	  install_requires=install_requires,
      packages=find_packages(),
      extras_require={'plot':['matplotlib'],'io':['h5py',],
                      'tests':tests_require},
      python_requires='>=3.5',
      tests_require=tests_require,
	  )

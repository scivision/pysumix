#!/usr/bin/env python
from setuptools import setup, find_packages

install_requires = ['tifffile','numpy','scipy','h5py']
tests_require = ['nose','coveralls']

setup(name='pysumix',
      version='0.5.0',
	  description='Sumix SMX API and data writing and live display',
	  author='Michael Hirsch, Ph.D.',
	  url='https://github.com/scivision/pysumix',
	  install_requires=install_requires,
      packages=find_packages(),
      extras_require={'plot':['matplotlib'],
                      'tests':tests_require},
      python_requires='>=2.7',
      tests_require=tests_require,
	  )

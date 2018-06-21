#!/usr/bin/env python
from setuptools import setup, find_packages

install_requires = ['tifffile', 'numpy', 'scipy', 'imageio']
tests_require = ['pytest', 'coveralls', 'flake8', 'mypy']

setup(name='pysumix',
      version='0.6.0',
      description='Sumix SMX API and data writing and live display',
      long_description=open('README.md').read(),
      long_description_content_type="text/markdown",
      author='Michael Hirsch, Ph.D.',
      url='https://github.com/scivision/pysumix',
      install_requires=install_requires,
      packages=find_packages(),
      extras_require={'plot': ['matplotlib'], 'io': ['h5py', ],
                      'tests': tests_require},
      python_requires='>=3.6',
      tests_require=tests_require,
      classifiers=[
          'Development Status :: 4 - Beta',
          'Environment :: Console',
          'Intended Audience :: Science/Research',
          'Operating System :: OS Independent',
          'Programming Language :: Python :: 3.6',
          'Programming Language :: Python :: 3.7',
          'Topic :: Scientific/Engineering :: Medical Science Apps.',
      ],
      )

.. image:: https://travis-ci.org/scivision/sumix-smx-python-api.svg?branch=master
  :target: https://travis-ci.org/scivision/sumix-smx-python-api
  :alt: Build Status
.. image:: https://coveralls.io/repos/scivision/sumix-smx-python-api/badge.svg?branch=master
  :target: https://coveralls.io/r/scivision/sumix-smx-python-api?branch=master
  :alt: Coverage Status

======================
sumix-smx-python-api
======================

API in Python that wraps `Sumix SMX M8X  C API <http://www.sumix.com/cameras/downloads.shtml>`_.

Requires: Windows XP/7/8/10 (32 or 64 bit) and Python 32-bit

Installation
============
from Terminal::
  
  git clone --depth 1 https://github.com/scivision/sumix-smx-python-api/
  conda install --file requirements.txt
  pip install tifffile

Usage
=====
To acquire color images:

1. plug in Sumix SMX-M8X(C) monochrome or color USB camera to your Windows PC
2. at command prompt, type ``python sumix_demo.py -x 640 -y 480 -e 20`` that sets your exposure to 20ms, with a frame size of 640x480.
3. you will see a live demosaiced display.

The program has the option to save as multipage TIFF or HDF5 by using the ``-f`` command line option with a filename::

  python sumix_demo.py -f blah.tif

File description
=================

================  =================
File              Description
================  =================
demosaic.py       Bayer demosaic for 'grbg' filters. 
rgb2gray.py       RGB to gray, also RGBA to gray (discards alpha channel). 
sumix_demo.py     Sumix SMX-M8XC camera Python image acquisition and recording test program.
sumixapi.py       Wraps Sumix C Windows DLL in Python. Not every last function has been implemented or tested.
test_demosaic.py  loads TIFF or HDF5 saved files to playback video on screen.
================  =================

References
==========
http://www.ece.ncsu.edu/imaging/Publications/2002/demosaicking-JEI-02.pdf

http://www.csee.wvu.edu/~xinl/papers/demosaicing_survey.pdf

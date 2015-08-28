.. image:: https://travis-ci.org/scivision/pysumix.svg?branch=master
  :target: https://travis-ci.org/scivision/pysumix
  :alt: Build Status
.. image:: https://coveralls.io/repos/scivision/pysumix/badge.svg?branch=master
  :target: https://coveralls.io/r/scivision/pysumix?branch=master
  :alt: Coverage Status

======================
sumix-smx-python-api
======================

API in Python that wraps `Sumix SMX M8X  C API <http://www.sumix.com/cameras/downloads.shtml>`_.

:Version: 0.1
:Author: Michael Hirsch
:Requires: Windows (32 or 64 bit); `Python 32-bit <https://repo.continuum.io/miniconda/Miniconda-latest-Windows-x86.exe>`_; `Sumix SMX M8X  C API <http://www.sumix.com/cameras/downloads.shtml>`_
:Note 1: So far I have not seen the camera driver work properly from a virtual machine (VirtualBox). Best to run in actual Windows.
:Note 2: Most people rightly use 64-bit Python. You will need a 32-bit Python install; it doesn't take much hard drive space.

Installation
============
1. Download the `Sumix SMX M8X  C API <http://www.sumix.com/cameras/downloads.shtml>`_
    a) Extract ZIP file, run EXE as Administrator
    b) install under C:/Sumix/, NOT C:/Program Files (x86)/Sumix
    c) plug in your Sumix SMX-M8X(C) camera into a USB 2.0 port
    d) be sure the camera is working properly with Sumix's demo program, get familiar with setting exposure, gain, ROI, etc.
2. download latest Python code. Can simply `download and extract zip <https://github.com/scivision/pysumix/archive/master.zip>`_ or via git::

      git clone --depth 1 https://github.com/scivision/sumix-smx-python-api/

3. Ensure you have the necessary Python modules by typing in Command Prompt::

    conda install --file requirements.txt
    pip install tifffile

Usage
=====
To acquire color images:

1. plug in Sumix SMX-M8X(C) monochrome or color USB camera to your Windows PC
2. at Command Prompt, type::

    python sumix_demo.py -x 640 -y 480 -e 20

   that sets your exposure to 20ms, with a frame size of 640x480.
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
.. [demosaic1] http://www.ece.ncsu.edu/imaging/Publications/2002/demosaicking-JEI-02.pdf

.. [demosaic2] http://www.csee.wvu.edu/~xinl/papers/demosaicing_survey.pdf

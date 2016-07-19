======================
sumix-smx-python-api
======================

API in Python that wraps `Sumix SMX M8X  C API <http://www.sumix.com/cameras/downloads.shtml>`_.

:Author: Michael Hirsch
:Requires: Windows (32 or 64 bit); `Python 32-bit <https://repo.continuum.io/miniconda/Miniconda-latest-Windows-x86.exe>`_; `Sumix SMX M8X  C API <http://www.sumix.com/cameras/downloads.shtml>`_
:Note 1: So far I have not seen the camera driver work properly from a virtual machine (VirtualBox). Best to run in actual Windows.
:Note 2: Most people rightly use 64-bit Python. You will need a 32-bit Python install; it doesn't take much hard drive space.

.. contents::

Installation
============
1. Download the `Sumix SMX M8X  C API <http://www.sumix.com/cameras/downloads.shtml>`_
    a) Extract ZIP file, run EXE as Administrator
    b) install under C:/Sumix/, NOT C:/Program Files (x86)/Sumix
    c) plug in your Sumix SMX-M8X(C) camera into a USB 2.0 port
    d) be sure the camera is working properly with Sumix's demo program, get familiar with setting exposure, gain, ROI, etc.

Then::

      git clone --depth 1 https://github.com/scivision/sumix-smx-python-api/

      python setup.py develop

Usage
=====

Live stream images
------------------
To see a live demosaiced display::

    python sumix_demo.py -p


Note that the default is NOT to show the live preview as the preview is computationally expensive.

Write fixed number of images to file
------------------------------------
::

    python sumix_demo.py -n 10 -f test.h5

that is written to HDF5 (viewable with `HDFView <https://www.hdfgroup.org/products/java/release/download.html>`_)
HDF5 is a very common format in the science and engineering community and has superceded TIFF and FITS for many applications

sumix_demo.py options
---------------------

-p  show live preview (for focusing camera)
-f  save multipage TIFF or HDF5 based on the file extension '.tif' '.h5'
-e  set exposure (ms)
-x  set ROI width
-y  set ROI height
-d  decimation (binning)
-g  set image amplifier gain

Troubleshooting
===============

You might have multiple copies of Python installed. For this program be sure you're using the 32-bit Python, perhaps by manually specifying on the Command Line the full path to Python.

File description
=================

================  =================
File              Description
================  =================
sumix_demo.py     Sumix SMX-M8XC camera Python image acquisition and recording test program.
test_demosaic.py  loads TIFF or HDF5 saved files to playback video on screen (can also use ImageJ)
demosaic.py       Bayer demosaic for 'grbg' filters.
rgb2gray.py       RGB to gray, also RGBA to gray (discards alpha channel).
sumixapi.py       Wraps Sumix C Windows DLL in Python. Not every last function has been implemented or tested.
================  =================

References
==========
.. [demosaic1] http://www.ece.ncsu.edu/imaging/Publications/2002/demosaicking-JEI-02.pdf

.. [demosaic2] http://www.csee.wvu.edu/~xinl/papers/demosaicing_survey.pdf

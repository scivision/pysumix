[![Travis CI](https://travis-ci.org/scivision/pysumix.svg?branch=master)](https://travis-ci.org/scivision/pysumix)
[![Coveralls](https://coveralls.io/repos/github/scivision/pysumix/badge.svg?branch=master)](https://coveralls.io/github/scivision/pysumix?branch=master)
[![PyPi versions](https://img.shields.io/pypi/pyversions/pysumix.svg)](https://pypi.python.org/pypi/pysumix)
[![PyPi wheels](https://img.shields.io/pypi/format/pysumix.svg)](https://pypi.python.org/pypi/pysumix)
[![PyPi Download stats](http://pepy.tech/badge/pysumix)](http://pepy.tech/project/pysumix)

# Sumix SMX Camera for Python

API in Python that wraps [Sumix SMX M8X C API](http://www.sumix.com/cameras/downloads.shtml).

Requires:   

* Windows (32 or 64 bit)
* [Python 32-bit](https://conda.io/miniconda.html)
* [Sumix SMX M8X C API](http://www.sumix.com/cameras/downloads.shtml)

Note:

* Best to run in native Windows instead of virtual machine
* Most people rightly use 64-bit Python. However, here you will need a 32-bit Python install; it doesn't take much hard drive space.

## Installation

1. Download [Sumix SMX M8X C API](http://www.sumix.com/cameras/downloads.shtml)
2. Extract ZIP file, run EXE as Administrator
3. install under C:/Sumix/, NOT C:/Program Files (x86)/Sumix
4. plug in your Sumix SMX-M8X(C) camera into a USB 2.0 port
5. be sure the camera is working properly with Sumix's demo program, get familiar with setting exposure, gain, ROI, etc.
6. Setup this program:
    
        pip install -e .

## Usage

### Live stream images

To see a live demosaiced display:

    python sumix_demo.py -p

Note that the default is NOT to show the live preview as the preview is computationally expensive.

### Write fixed number of images to file

    python sumix_demo.py -n 10 -f test.h5

that is written to HDF5 (viewable with
[HDFView](https://www.hdfgroup.org/products/java/release/download.html))
HDF5 is a very common format in the science and engineering community and has superceded TIFF and FITS for many applications

### sumix_demo.py options

* -p show live preview (for focusing camera) 
* -f save multipage TIFF or HDF5 based on the file extension '.tif' '.h5' 
* -e set exposure (ms) 
* -x set ROI width 
* -y set ROI height 
* -d decimation (binning) 
* -g set image amplifier gain

## Troubleshooting

You might have multiple copies of Python installed. For this program be
sure you're using the 32-bit Python, perhaps by manually specifying on
the Command Line the full path to Python.

## File description

  File                Description
  ------------------- ----------------------------------------------------------------------------------------------
  sumix\_demo.py      Sumix SMX-M8XC camera Python image acquisition and recording test program.
  test\_demosaic.py   loads TIFF or HDF5 saved files to playback video on screen (can also use ImageJ)
  demosaic.py         Bayer demosaic for 'grbg' filters.
  rgb2gray.py         RGB to gray, also RGBA to gray (discards alpha channel).
  sumixapi.py         Wraps Sumix C Windows DLL in Python. Not every last function has been implemented or tested.

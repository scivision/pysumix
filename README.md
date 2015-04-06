[![Build Status](https://travis-ci.org/scivision/sumix-smx-python-api.svg?branch=master)](https://travis-ci.org/scivision/sumix-smx-python-api)
# sumix-smx-python-api
API in Python that wraps [Sumix SMX M8X  C API](http://www.sumix.com/cameras/downloads.shtml).

Requires: Windows XP/7/8/10 (32 or 64 bit) and Python 32-bit

API prereqs: 
------------
```
pip install -r requirements.txt
```

Full demo Prereqs:
------------------
```
pip install -r requirements.txt
pip install -r optional-requirements.txt
```

Optional:
* h5py (saving/loading HDF5 image sets).
* tifffile (saving/loading multipage TIFF with custom tags)

To acquire color images:
  0. plug in Sumix SMX-M8X(C) monochrome or color USB camera to your Windows PC
  1. at command prompt, type ```python sumix_demo.py -x 640 -y 480 -e 20``` that sets your exposure to 20ms, with a frame size of 640x480.
  2. you will see a live demosaiced display.

The program has the option to save as multipage TIFF or HDF5 by using the ```-f``` command line option with a filename. E.g. ```python sumix_demo.py -f blah.tif```

File description:
=================
``` demosaic.py ```  
Bayer demosaic for 'grbg' filters. 
By default a simple numerical method is used, however a gateway to the Sumix API is also provided should you want to use their several choices (detailed in the demosaic.py comments).

``` rgb2gray.py ```
RGB to gray, also RGBA to gray (discards alpha channel). 

``` sumix_demo.py ```: Sumix SMX-M8XC camera Python image acquisition and recording test program.

```sumixapi.py```: Wraps Sumix C Windows DLL in Python. Not every last function has been implemented or tested. Ask for more.

```test_demosaic.py```: loads TIFF or HDF5 saved files to playback video on screen.

References:
-----------
http://www.ece.ncsu.edu/imaging/Publications/2002/demosaicking-JEI-02.pdf

http://www.csee.wvu.edu/~xinl/papers/demosaicing_survey.pdf

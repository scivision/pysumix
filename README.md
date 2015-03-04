# sumix-smx-python-api
API in Python that wraps [C API](http://www.sumix.com/cameras/downloads.shtml). 

Requires: WIndows (32 or 64 bit) and Python 32-bit

Prereqs: Numpy, Scipy, Matplotlib.

Optional: 
* h5py (saving/loading HDF5 image sets).  
* Scikit-image: Saving multipage TIFFs using [FreeImage](http://bostonmicrowave.com/2015/01/writing-multipage-tiff-with-python/).

To acquire images (requires Windows 32 or 64 bit, with Python (2.7 or 3.4) 32-bit ):
  0. plug in Sumix SMX-M8XC color USB camera to your Windows PC
  1. at command prompt, type ```python main.py -x 640 -y 480 -e 20``` that sets your exposure to 20ms, with a frame size of 640x480.
  2. you will see a live display. The video is demosaiced for your viewing enjoyment.
  
The program has the option to save as multipage TIFF or HDF5 by using the ```-f``` command line option with a filename. E.g. ```python main.py -f blah.h5```

The demosaicing is primitive, using nearest neighbor interpolation. I have not verified the correctness of this simple algorithm, only that it "looks right".

File description:
=================
```demosaic.py```: trivial nearest neighbor Bayer demosaic for 'gbrg' filters. Input/Output: 2-D 8-bit array

```main.py```: Sumix SMX-M8XC camera Python image acquisition and recording program. Non-optimized program.

```sumixapi.py```: Wraps Sumix C Windows DLL in Python. Not every last function has been implemented or tested. Ask for more.

```test_demosaic.py```: loads HDF5 saved files to playback video on screen.
  

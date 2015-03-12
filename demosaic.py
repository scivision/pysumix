"""
gbrg2rgb.py
demosaic bayer filter of type 'gbrg' using nearest neighbor interpolation
this is a poor way of doing it, but illustrates a very basic case
michael@scivision.co
GPLv3+

input:
assumes uint8 or uint16 raw bayer filtered gbrg input
assumes 2-D I x J pixels, where a single image is I x J pixels,
        where I and J are both even numbers

output:
same uint8 or uint16 shape as inpout
"""
from __future__ import division
import numpy as np
from scipy.ndimage.interpolation import zoom

def gbrg2rgb(img,color=True):
    """ GBRG means the upper left corner of the image has four pixels arranged like
    green  blue
    red    green
    """
    if img.ndim !=2:
        exit('*** demosaic: for now, only 2-D numpy array is accepted')

    if img.shape[0] % 2 or img.shape[1] % 2:
        exit('*** demosaic: requires even-numbered number of pixels on both axes')

    if not img.dtype in (np.uint8, np.uint16):
        exit('*** demosaic is currently for uint8 and uint16 input ONLY')

   #upcast g1,g2 to avoid overflow from 8-bit or 16-bit input
    g1 = img[0::2,0::2].astype(np.uint32)
    g2 = img[1::2,1::2].astype(np.uint32)
    r =  img[0::2,1::2]
    b =  img[1::2,0::2]

    g = ((g1+g2) // 2).astype(img.dtype)

    rgb = np.dstack((r,g,b)) #this is the way matplotlib likes it for imshow (RGB in axis=2)

    if color:
        demos = zoom(rgb,(2,2,1),order=0,) #0:nearest neighbor
    else: #gray
        demos = rgb2gray(rgb)

    return demos

def rgb2gray(rgb):
    return rgb[...,:].dot([0.299,0.587,0.144]).astype(rgb.dtype)

if __name__ == '__main__':
    from matplotlib.pyplot import figure,show
    x = (np.random.rand(10,10)*65535).astype(np.uint16)
    y = gbrg2rgb(x)
    print(y.shape)
    print(y.dtype)

    fg = figure(); ax = fg.gca()
    im = ax.imshow(y,interpolation='none',origin='lower')
    fg.colorbar(im)
    ax.set_title('rgb output')
    show()


"""
gbrg2rgb.py
demosaic bayer filter of type 'gbrg' using nearest neighbor interpolation
this is a poor way of doing it, but illustrates a very basic case
michael@scivision.co
GPLv3+
assumes uint8 or uint16 raw bayer filtered gbrg input
"""
from __future__ import division
from numpy import uint16, dstack
from scipy.misc import imresize  #<-- requires scikit-image

def gbrg2rbg(img):
   """ GBRG means the upper left corner of the image has four pixels arranged like
   green  blue
   red    green
   """
   g1 = img[0::2,0::2].astype(uint16)
   g2 = img[1::2,1::2].astype(uint16)
   r =  img[0::2,1::2]
   b =  img[1::2,0::2]

   g = ((g1+g2) // 2).astype(img.dtype) #allows uint16 to pass through, or if original is uint 8, converts to uint8

   rgb = dstack((r,g,b)) #this is the way matplotlib likes it for imshow

   """http://pillow.readthedocs.org/en/latest/handbook/concepts.html"""
   rgbup = imresize(rgb,200,'nearest',"RGB")
   return rgbup

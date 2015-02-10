"""
gbrg2rgb.py
demosaic bayer filter of type 'gbrg' using nearest neighbor interpolation
this is a poor way of doing it, but illustrates a very basic case
Not guaranteed to be correct. It "looked right" in matplotlib 1.4.2.
michael@scivision.co
GPLv3+
assumes uint8 raw bayer filtered gbrg input
"""
from __future__ import division
from numpy import uint16,uint8, dstack
from scipy.misc import imresize

def gbrg2rbg(img):

   g1 = img[0::2,0::2].astype(uint16)
   g2 = img[1::2,1::2].astype(uint16)
   r =  img[0::2,1::2]
   b =  img[1::2,0::2]

   g = ((g1+g2) // 2).astype(uint8)

   rgb = dstack((r,g,b)) #this is the way matplotlib likes it for imshow

   """http://pillow.readthedocs.org/en/latest/handbook/concepts.html"""
   rgbup = imresize(rgb,200,'nearest',"RGB")
   return rgbup

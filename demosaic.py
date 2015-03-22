"""
demosaic bayer filter of type 'grbg' using nearest neighbor interpolation
michael@scivision.co
GPLv3+

input:
assumes uint8 or uint16 raw bayer filtered grbg input
assumes 2-D I x J pixels, where a single image is I x J pixels,
        where I and J are both even numbers

output:
same uint8 or uint16 shape as inpout
"""
from __future__ import division
try:
    import numpy as np
    from scipy.ndimage.interpolation import zoom
except ImportError as e:
    print(e)
    print('If youre on Windows, be sure your PATH environment variable includes your Python DLLs directory.')
    print('E.g. for Anaconda on Windows installed to C:\Anaconda, you should have C:\Anaconda\DLLs on your Windows PATH.')
    exit()

"""
you may not have the Sumix API installed. Try the method='ours' to fallback to non-sumix demosaic
"""

def demosaic(img,method='',alg=1,color=True):
    if img is None:
        return None

    ndim = img.ndim
    if ndim==2:
        pass #normal case
    elif ndim==3 and img.shape[-1] != 3: #normal case, iterate
        print('demosaic: iterate over {:d} frames'.format(img.shape[0]))
        if color:
            dem = np.empty(img.shape+(3,),dtype=img.dtype)
        else:
            dem = np.empty(img.shape,dtype=img.dtype)
        for i,f in enumerate(img):
            dem[i,...] = demosaic(f,method,alg,color)
        return dem
    else:
        print('demosaic: unsure what you want with shape ' + str(img.shape) + ' so return unmodified')
        return img

    if str(method).lower()=='sumix':
        from sumixapi import Convert
        return Convert().BayerToRgb(img,alg)
    else:
        return grbg2rgb(img,alg,color)

def grbg2rgb(img,alg=1,color=True):
    """ GRBG means the upper left corner of the image has four pixels arranged like
    green  red
    blue    green
    """
    if img.ndim !=2:
        print(img.shape)
        print('*** demosaic: for now, only 2-D numpy array is accepted')
        return None

    if img.shape[0] % 2 or img.shape[1] % 2:
        print(img.shape)
        print('*** demosaic: requires even-numbered number of pixels on both axes')
        return None

    if not img.dtype in (np.uint8, np.uint16):
        print('*** demosaic is currently for uint8 and uint16 input ONLY')
        return None

   #upcast g1,g2 to avoid overflow from 8-bit or 16-bit input
    g1 = img[0::2,0::2].astype(np.uint32)
    g2 = img[1::2,1::2].astype(np.uint32)
    r =  img[0::2,1::2]
    b =  img[1::2,0::2]

    g = np.round(((g1+g2) / 2)).astype(img.dtype)

    rgb = np.dstack((r,g,b)) #this is the way matplotlib likes it for imshow (RGB in axis=2)


    if 1<=alg<=4:
        order=alg-1
    else:
        print('unknown method ' +str(alg) +' falling back to nearest neighbor alg=1')
        order=0

    demos = zoom(rgb,(2,2,1),order=order,) #0:nearest neighbor

    if not color:
        demos = rgb2gray(demos)

    return demos

def rgb2gray(rgb):
    """
    http://en.wikipedia.org/wiki/Grayscale#Converting_color_to_grayscale
    These coefficients may not be the ones desired for your system, but may well
    be better than just averaging RGB channels.
    """
    ndim = rgb.ndim
    if ndim==2:
        print('rgb2gray: assuming its already gray since ndim=2')
    elif ndim==3 and rgb.shape[-1] == 3: #this is the normal case
        return np.round(rgb[...,:].dot([0.299,0.587,0.114])).astype(rgb.dtype)
    elif ndim==4 and rgb.shape[-1] ==3:
        print('rgb2gray: iterating over {:d} frames'.format(rgb.shape[0]))
        gray = np.empty(rgb.shape[:3],dtype=rgb.dtype)
        for i,f in enumerate(rgb):
            gray[i,...] = rgb2gray(f)
        return gray
    else:
        print('rgb2gray: unsure what you want with shape ' + str(rgb.shape) + ' so return unmodified')
    #finally
    return rgb

if __name__ == '__main__':
    # selftest
    from numpy.testing import assert_array_equal
#%% test raw->color, nearest neighbor
    testimg = np.array([[23,128],
                        [202,27],],dtype=np.uint8)

    # we make it artifically 1 frame of a series
    testnear = demosaic(testimg[None,:,:],'',1,color=True)

    refnear = np.array([[[128,25,202],
                        [128,25,202]],
                       [[128,25,202],
                        [128,25,202]]], dtype=testimg.dtype)[None,:,:]

    assert_array_equal(testnear,refnear)
    assert testimg.dtype == testnear.dtype
#%% test raw->mono, nearest neighbor
    testnear = demosaic(testimg[None,:,:],'',1,color=False)

    refnear = np.array([[76,76],
                        [76,76]], dtype=testimg.dtype)[None,:,:]

    assert_array_equal(testnear,refnear)
    assert testimg.dtype == testnear.dtype
#!/usr/bin/env python3
from numpy import around,empty, array,uint8

def rgb2gray(rgb):
    """
    http://en.wikipedia.org/wiki/Grayscale#Converting_color_to_grayscale
    These coefficients may not be the ones desired for your system, but may well
    be better than just averaging RGB channels.

    Note: Transparency RGBA is discarded
    """
    ndim = rgb.ndim
    if ndim==2:
        print('rgb2gray: assuming its already gray since ndim=2')

    elif ndim==3 and rgb.shape[-1] == 3: #this is the normal case
        return around(rgb[...,:].dot([0.299,0.587,0.114])).astype(rgb.dtype)
    elif ndim==3 and rgb.shape[-1] == 4:
        print('assuming this is an RGBA image, discarding alpha channel')
        return rgb2gray(rgb[...,:-1])

    elif ndim==4 and rgb.shape[-1] in (3,4):
        print('rgb2gray: iterating over {:d} frames'.format(rgb.shape[0]))
        gray = empty(rgb.shape[:3],dtype=rgb.dtype)
        for i,f in enumerate(rgb):
            gray[i,...] = rgb2gray(f)
        return gray
    else:
        print('rgb2gray: unsure what you want with shape ' + str(rgb.shape) + ' so return unmodified')
    #finally
    return rgb

if __name__ == '__main__':
    from numpy.testing import assert_array_equal
    #RGBA test image
    rgba = array([[[[  76.,   76.,   76.,  255.],
                        [  76.,   76.,   76.,  255.]],
                       [[  76.,   76.,   76.,  255.],
                         [  76.,   76.,   76.,  255.]]]],dtype=uint8)

    testgray =  rgb2gray(rgba)
    refalpha = array([[76,76],
                        [76,76]], dtype=rgba.dtype)[None,:,:]
    assert_array_equal(testgray,refalpha)
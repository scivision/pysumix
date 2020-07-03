"""
demosaic bayer filter of type 'grbg' using nearest neighbor interpolation

input:
assumes uint8 or uint16 raw bayer filtered grbg input
assumes 2-D I x J pixels, where a single image is I x J pixels,
        where I and J are both even numbers

output:
same uint8 or uint16 shape as inpout

Note:  If you're on Windows, be sure your PATH environment variable includes your Python DLLs directory.
    E.g. Python installed to C:/Miniconda3, you should have C:/Miniconda3/DLLs on your Windows PATH.

"""
import logging
import numpy as np
from scipy.ndimage.interpolation import zoom

#
try:
    from .api import Convert
except Exception:
    Convert = None  # type: ignore
#
from .rgb2gray import rgb2gray


def demosaic(img: np.ndarray, method: str = "", alg: int = 1, color: bool = True):

    ndim = img.ndim
    if ndim == 2:
        pass  # normal case
    elif ndim == 3 and img.shape[-1] != 3:  # normal case, iterate
        logging.info(f"iterate over {img.shape[0]} frames")
        if color:
            dem = np.empty(img.shape + (3,), dtype=img.dtype)
        else:
            dem = np.empty(img.shape, dtype=img.dtype)
        for i, f in enumerate(img):
            dem[i, ...] = demosaic(f, method, alg, color)
        return dem
    else:
        raise ValueError(f"unsure what you want with shape {img.shape}")

    if str(method).lower() == "sumix" and Convert is not None:
        return Convert().BayerToRgb(img, alg)
    else:
        return grbg2rgb(img, alg, color)


def grbg2rgb(img: np.ndarray, alg: int = 1, color: bool = True) -> np.ndarray:
    """ GRBG means the upper left corner of the image has four pixels arranged like
    green  red
    blue    green
    """
    if img.ndim != 2:
        raise NotImplementedError(f"for now, only 2-D Numpy ndarray is accepted {img.shape}")

    if img.shape[0] % 2 or img.shape[1] % 2:
        raise TypeError(f"requires even-numbered number of pixels on both axes {img.shape}")

    if img.dtype not in (np.uint8, np.uint16):
        raise TypeError(f"demosaic is currently for uint8 and uint16 input ONLY {img.shape}")

    # upcast g1,g2 to avoid overflow from 8-bit or 16-bit input
    g1 = img[0::2, 0::2].astype(np.uint32)
    g2 = img[1::2, 1::2].astype(np.uint32)
    r = img[0::2, 1::2]
    b = img[1::2, 0::2]

    g = np.round(((g1 + g2) / 2)).astype(img.dtype)

    rgb = np.dstack((r, g, b))  # this is the way matplotlib likes it for imshow (RGB in axis=2)

    if 1 <= alg <= 4:
        order = alg - 1
    else:
        logging.warning(f"unknown method {alg}  falling back to nearest neighbor alg=1")
        order = 0

    demos = zoom(rgb, (2, 2, 1), order=order)  # 0:nearest neighbor

    if not color:
        demos = rgb2gray(demos)

    return demos

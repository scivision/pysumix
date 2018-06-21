#!/usr/bin/env python
"""
Python API using Windows C DLL for Sumix SMX-M8X(C) cameras
Requirements: Windows (32 or 64 bit), Python 32-bit (2.7 or 3.4)

Notes:
if you get WindowsError: [Error 193] %1 is not a valid Win32 application, it
    means you're using a 64-bit Python with a 32-bit DLL. Try 32-bit Python!

michael@scivision.co
"""
from pathlib import Path
import ctypes as ct
import numpy as np
from numpy import asarray
import logging
from typing import Dict, Tuple
# %%
DLL = Path('c:')/'Sumix'/'SMX-M8x USB2.0 Camera'/'API'/'SMXM8X.dll'
# %%


class Camera:
    def __init__(self, width: int=None, height: int=None, decim: int=None, tenbit=None,
                 startx: int=None, starty: int=None, mirrorv=None, mirrorh=None, verbose: bool=False,
                 dll=DLL) -> None:
        if DLL.is_file():
            print('using {}'.format(DLL))
        else:
            raise ImportError('could not find driver file {}'.format(DLL))

        self.dll = ct.windll.LoadLibrary(dll)  # type: ignore
        self.isopen = False
        self.h = None

        # self.info = self.getCameraInfo() #This function can cause crashes
# %% enact initialized settings from abvoe
        self.setParams(width, height, decim, startx, starty, mirrorv, mirrorh)

        cpr = self.getParams()
        self.decim = cpr.Decimation
        self.xpix = cpr.Width // cpr.Decimation
        self.ypix = cpr.Height // cpr.Decimation
        self.mirrorv = cpr.MirrorV
        self.mirrorh = cpr.MirrorH
        self.startx = cpr.StartX
        self.starty = cpr.StartY
        self.verbose = verbose

        print('ROI width,height = {}, {}'.format(self.xpix, self.ypix))
        self.color = cpr.ColorDeep == 24
        if verbose > 1:
            print('color depth ' + str(cpr.ColorDeep))

        if self.color:
            self.maxgain = 160
        else:  # monochrome camera
            self.maxgain = 47

# %% 8/10 bit setup
        if tenbit:  # FIXME just convert bool to byte instead
            self.set10BitsOutput(1)
        else:
            self.set10BitsOutput(0)

        self.tenbit = self.get10BitsOutput()
        if self.tenbit == 1:
            print(' TEN BIT mode enabled')
        elif verbose > 1:
            print(' EIGHT BIT mode enabled')
# %%

    def setParams(self, width: int=None, height: int=None, decim: int=None,
                  startx: int=None, starty: int=None, mirrorv=None, mirrorh=None):  # Set camera params
        old = self.getParams()

        params = _TFrameParams()
        if startx is not None and startx >= 0:
            params.StartX = ct.c_int32(startx)
        else:
            params.StartX = ct.c_int32(old.StartX)

        if starty is not None and starty >= 0:
            params.StartY = ct.c_int32(starty)
        else:
            params.StartY = ct.c_int32(old.StartY)

        if width is not None and width > 0:  # it's ok to pass odd number
            params.Width = ct.c_int32(width)
        else:
            params.Width = ct.c_int32(old.Width)

        if height is not None and height > 0:
            params.Height = ct.c_int32(height)
        else:
            params.Height = ct.c_int32(old.Height)

        if decim is not None and decim in tuple(range(1, 9)):
            params.Decimation = ct.c_int32(decim)
        else:
            params.Decimation = ct.c_int32(old.Decimation)

        if mirrorv is not None and mirrorv > 0:
            params.MirrorV = ct.c_byte(mirrorv)
        else:
            params.MirrorV = ct.c_byte(old.MirrorV)

        if mirrorh is not None and mirrorh > 0:
            params.MirrorH = ct.c_byte(mirrorh)
        else:
            params.MirrorH = ct.c_byte(old.MirrorH)

        self.openCamera()
        rc = self.dll.CxSetScreenParams(self.h, ct.byref(params))
        if rc == 0:
            raise RuntimeError('CxSetScreenParams: problem setting parameter choices')
        else:
            rc = self.dll.CxActivateScreenParams(self.h)
            if rc == 0:
                raise RuntimeError('CxActivateScreenParams: Problem activating parameters')

        self.closeCamera()
# %%

    def openCamera(self, cid=None):  # attempt initial connection to camera
        if not self.isopen:
            self.h = self.dll.CxOpenDevice(cid)
        if self.h == -1:
            raise TypeError(f"Camera not found on open attempt with {DLL}")
        else:
            self.isopen = True

    def open(self, cid=None):
        self.openCamera(cid)

    def close(self):
        self.closeCamera()

    def closeCamera(self):  # final closing of camera connection
        if self.isopen:
            self.dll.CxCloseDevice(self.h)  # no return code
            self.h = None
        self.isopen = False
# %%

    def setFrequency(self, freqbyte: int):
        if freqbyte == 1:  # 24MHz
            freq = ct.c_byte(1)
        elif freqbyte == 0:  # 12MHz
            freq = ct.c_byte(0)
        else:
            raise ValueError('I can only accept 1->24MHz or 0->12MHz to set sensor frequency')

        self.openCamera()
        rc = self.dll.CxSetFrequency(self.h, freq)  # not ct.byref()
        if rc == 0:
            logging.error("CxSetFrequency: Unable to set sensor frequency ")
        self.closeCamera()

    def getFrequency(self):
        freq = ct.c_byte()
        self.openCamera()
        rc = self.dll.CxGetFrequency(self.h, ct.byref(freq))
        self.closeCamera()
        if rc == 0:
            raise RuntimeError("CxGetFrequency: Unable to get sensor frequency")

        freq = freq.value

        if freq == 0:
            return '12 MHz'
        elif freq == 1:
            return '24 MHz'
        else:
            raise RuntimeError('CxGetFrequency: unknown response to CxGetFrequency')

# %%

    def getExposureMinMax(self) -> Tuple[float, float]:
        emin = ct.c_float()
        emax = ct.c_float()
        self.openCamera()
        rc = self.dll.CxGetExposureMinMaxMs(self.h, ct.byref(emin), ct.byref(emax))
        self.closeCamera()
        if rc == 0:
            raise RuntimeError("CxGetExposureMinMaxMs: Unable to get min/max exposure")

        return emin.value, emax.value

    def getExposure(self) -> float:  # get comera exposure in milliseconds
        exp = ct.c_float()
        self.openCamera()
        rc = self.dll.CxGetExposureMs(self.h, ct.byref(exp))
        self.closeCamera()
        if rc == 0:
            raise RuntimeError("CxGetExposureMs: Unable to get exposure")

        return exp.value

    def setExposure(self, expreq: float):  # set comera exposure in milliseconds
        if expreq is not None:
            if expreq < 0:
                raise ValueError('exposure request must be a positive number')

            exp = ct.c_float()
            self.openCamera()
            rc = self.dll.CxSetExposureMs(self.h, ct.c_float(expreq), ct.byref(exp))
            self.closeCamera()
            if rc == 0:
                raise RuntimeError("CxSetExposureMs: Unable to set exposure=" + str(expreq))
# %%

    def getGain(self) -> Dict[str, int]:
        gg1 = ct.c_int32()
        gr = ct.c_int32()
        gg2 = ct.c_int32()
        gb = ct.c_int32()

        self.openCamera()
        rc = self.dll.CxGetGain(self.h, ct.byref(gg1), ct.byref(gr),
                                ct.byref(gg2), ct.byref(gb))
        self.closeCamera()
        if rc == 0:
            raise RuntimeError('CxGetGain: could not read gain.')

        return {'g1': gg1.value, 'gr': gr.value, 'gg2': gg2.value, 'gb': gb.value}

    def setGain(self, greq: int) -> Dict[str, int]:
        """
        This function not completely implemented
        """
        assert isinstance(greq, int), 'just a single integer to set gain for all channels.'

        greq = np.clip(greq, 0, self.maxgain)

        gg1 = ct.c_int32(greq)
        gr = ct.c_int32(greq)
        gg2 = ct.c_int32(greq)
        gb = ct.c_int32(greq)

        self.openCamera()
        rc = self.dll.CxSetGain(self.h, gg1, gr, gg2, gb)
        self.closeCamera()

        if rc == 0:
            raise RuntimeError('CxSetGain: could not set gain.')

        # confirm gain setting
        rgain = self.getGain()
        if self.verbose:
            print(rgain)

        return rgain

    def setAllGain(self, gainreq: int) -> Dict[str, int]:  # sets gain for all colors simultaneously
        if gainreq is not None:
            gainreq = np.clip(gainreq, 0, self.maxgain)
            if self.verbose:
                print(f'attempting to set all gains to {gainreq:d}')
            gain = ct.c_int32(gainreq)
            self.openCamera()
            rc = self.dll.CxSetAllGain(self.h, gain)
            self.closeCamera()
            if rc == 0:
                raise RuntimeError(f'unable to set gain {gainreq}')

            # confirm gain setting
            rgain = self.getGain()
            if self.verbose:
                print(rgain)

            return rgain
# %%

    def setBrightnessContrastGamma(self, bright: int, contrast: int, gamma: int):
        if bright is not None and contrast is not None and gamma is not None:
            if -127 <= bright <= 127 and -127 <= contrast <= 127 and -127 <= gamma <= 127:
                b = ct.c_int32(bright)
                c = ct.c_int32(contrast)
                g = ct.c_int32(gamma)
                self.openCamera()
                rc = self.dll.CxSetBrightnessContrastGamma(self.h, b, c, g)
                self.closeCamera()
                if rc == 0:
                    raise RuntimeError('CxSetBrightnessContrastGamma: problem setting')
            else:
                raise ValueError('brightness, contrast, and gamma must be in -127..127')
# %%

    def getConversionTable(self):
        """
        gets mapping from 10-bit sensor to 8-bit output that's more typically
        used
        """
        tbuf = (ct.c_ubyte * 1024)()
        self.openCamera()
        rc = self.dll.CxGetConvertionTab(self.h, ct.byref(tbuf))
        self.closeCamera()
        if rc == 0:
            raise RuntimeError('trouble getting 10-8 bit conversion table')

        return asarray(tbuf)

# %%
    def startStream(self):  # begin streaming acquisition
        print('starting camera stream ')
        self.openCamera()
        if True:  # not self.getStreamMode(): #this call crashes camera
            rc = self.dll.CxSetStreamMode(self.h, ct.c_byte(1))
            # leave connection open for streaming
            if rc == 0:
                raise RuntimeError('CxSetStreamMode: unable to start camera stream')

    def stopStream(self):  # end streaming acquisition
        if True:  # self.getStreamMode(): #this call crashes camera
            print('stopping camera stream')
            self.openCamera()
            rc = self.dll.CxSetStreamMode(self.h, ct.c_byte(0))
            self.closeCamera()
            if rc == 0:
                raise RuntimeError('CxSetStreamMode: unable to stop camera stream')

    def getStreamMode(self) -> bool:
        """
        this function prevents following commands from working (bug)
        """
        smode = ct.c_ubyte()  # tried ubyte and byte
        self.openCamera()
        rc = self.dll.CxGetStreamMode(self.h, ct.byref(smode))  # pointer didn't help
        self.closeCamera()
        if rc == 0:
            raise RuntimeError('CxGetStreamMode: problem checking stream status')

        return bool(smode)
# %%

    def grabFrame(self):  # grab latest frame in stream
        """ for SMX-M8XC, the "color" camera passes back a grayscale image that was
         Bayer filtered--you'll need to demosaic! """
        Nbuffer = self.xpix * self.ypix
        imbuffer = (ct.c_ubyte * Nbuffer)()
        bufferbytes = Nbuffer  # each pixel is 1 byte

        if not self.isopen:
            print('* grabframe: attempting to reopen camera connection')
            self.openCamera()
            self.startStream()

        rc = self.dll.CxGrabVideoFrame(self.h, ct.byref(imbuffer), bufferbytes)
        if rc == 0:
            logging.error("CxGrabVideoFrame: problem getting frame")
            return

        return asarray(imbuffer).reshape((self.ypix, self.xpix), order='C')
# %%

    def get10BitsOutput(self):  # 8 or 10 bits
        getbit = ct.c_bool()
        self.openCamera()
        rc = self.dll.CxGet10BitsOutput(self.h, ct.byref(getbit))
        self.closeCamera()
        if rc == 0:
            logging.error("CxGet10BitsOutput: Error getting bit mode")
            return
        return getbit.value

    def set10BitsOutput(self, useten):  # False=8 bit, True=10bit
        if useten not in (0, 1):
            logging.error('valid input is 0 for 8-bit, or 1 for 10-bit')
            return

        self.openCamera()
        rc = self.dll.CxSet10BitsOutput(self.h, ct.c_bool(useten))
        self.closeCamera()
        if rc == 0:
            logging.error("CxSet10BitsOutput: Error setting bit mode")
# %%

    def getParams(self):
        params = _TFrameParams()
        self.openCamera()
        rc = self.dll.CxGetScreenParams(self.h, ct.byref(params))
        self.closeCamera()
        if rc == 0:
            logging.error('CxGetScreenParams: error getting params')
            return
        return params

    def getCameraInfoEx(self):
        det = _TCameraInfoEx()
        self.openCamera()
        rc = self.dll.CxGetCameraInfoEx(self.h, ct.byref(det))
        self.closeCamera()
        if rc == 0:
            logging.error('CxGetCameraInfoEx: error getting camera info')
            return
        return det

    def getCameraInfo(self):
        """
        this function prevents folllowing functions from working (bug)
        """
        det = _TCameraInfo()
        self.openCamera()
        rc = self.dll.CxGetCameraInfo(self.h, ct.byref(det))
        self.closeCamera()
        if rc == 0:
            logging.error('CxGetCameraInfo: Error getting camera info')
            return
        # print((det.MaxWidth, det.MaxHeight))
        return det
# %%

    def getFrameCounter(self):
        count = ct.c_uint32()
        self.openCamera()
        rc = self.dll.CxGetFrameCounter(self.h, ct.byref(count))  # pointer didn't help
        self.closeCamera()
        if rc == 0:
            logging.error('CxGetFrameCounter: problem checking frame number')
            return
        return count.value

# %%
    def guiStartVideo(self, hwnd):
        """ very experimental function, does not work """
        self.openCamera()
        # setStreamMode NOT needed per API doc
        rc = self.dll.CxStartVideo(self.h, hwnd)
        if rc == 0:
            logging.error('CxStartVideo experiment had problem')


# %%
"""
https://docs.python.org/3/library/ctypes.html#ctypes.Structure
"""


class _TFrameParams(ct.Structure):  # ct.Structure must be input argument
    _fields_ = [("StartX", ct.c_int),
                ("StartY", ct.c_int),
                ("Width", ct.c_int),
                ("Height", ct.c_int),
                ("Decimation", ct.c_int),
                ("ColorDeep", ct.c_int32),
                ("MirrorV", ct.c_byte),
                ("MirrorH", ct.c_byte)]


class _TCameraInfo(ct.Structure):
    _fields_ = [("SensorType", ct.c_int32),
                ("MaxWidth", ct.c_int32),
                ("MaxHeight", ct.c_int32),
                ("DeviceName", ct.c_char)
                ]


class _TCameraInfoEx(ct.Structure):
    _fields_ = [("HWModelID", ct.c_ushort),
                ("HWVersion", ct.c_ushort),
                ("HWSerial", ct.c_ulong)]

# %%


class Convert:
    def __init__(self, dll=DLL):
        if DLL.is_file():
            print('using {}'.format(DLL))
        else:
            raise ImportError('could not find driver file {}'.format(DLL))

        self.dll = ct.windll.LoadLibrary(dll)

    def BayerToRgb(self, bayerimg: np.ndarray, bayerint: int):
        if bayerimg is None:
            return

        assert bayerimg.ndim == 2, 'only accepts 2-D mosaiced images'

        assert bayerint in range(6), ('bayer mode must be in 0,1,2,3,4,5\n '
                                      '0: monochrome 1: nearest neighbor 2: bilinear 3:Laplacian 4:Real Monochrome 5:Bayer Average')

        """
        note, even if selecting 0: Monochrome, the image returned is I X J X 3
        """
        h, w = bayerimg.shape

        Width = ct.c_int32(w)
        Height = ct.c_int32(h)
        BayerAlg = ct.c_int32(bayerint)

        Nbuffer = w * h
        inbuffer = (ct.c_ubyte * Nbuffer)(*bayerimg.ravel(order='C'))
        outbuffer = (ct.c_ubyte * Nbuffer*3)()

        rc = self.dll.CxBayerToRgb(ct.byref(inbuffer),
                                   Width, Height, BayerAlg,
                                   ct.byref(outbuffer))
        if rc == 0:
            logging.error('could not convert image')
            return

        # this is a BGR array if color
        dimg = asarray(outbuffer).reshape((h, w, 3), order='C')

        if bayerint in (0, 4):  # monochrome
            dimg = dimg[..., 0]  # all pages identical
        else:
            dimg = dimg[..., ::-1]  # reverse colors, BGR -> RGB
        return dimg


# %%
if __name__ == '__main__':
    c = Camera()

"""
Python API using Windows C DLL for Sumix SMX-M8X(C) cameras
Requirements: Windows (32 or 64 bit), Python 32-bit (2.7 or 3.4)

Notes:
if you get WindowsError: [Error 193] %1 is not a valid Win32 application, it
    means you're using a 64-bit Python with a 32-bit DLL. Try 32-bit Python!

michael@scivision.co
GPLv3+ license
"""
import ctypes as ct
from numpy import asarray
from os.path import join,isfile
from platform import system
#from time import sleep

if system().lower()=='windows':
    DLL = join('c:\\','Sumix','SMX-M8x USB2.0 Camera','API','SMXM8X.dll')
else:
    exit('*** this driver made only for Windows, you appear to be running ' + system() )

if isfile(DLL):
    print('using ' + DLL)
else:
    exit('could not find driver file ' + DLL)

class Camera:
    def __init__(self, width=None,height=None, decim=None, tenbit=None,
                 startx=None, starty=None, mirrorv=None,mirrorh=None,verbose=False,
                 dll=DLL):
        self.dll = ct.windll.LoadLibrary(dll)
        self.isopen = False
        self.h = None

        #self.info = self.getCameraInfo() #This function can cause crashes
#%% enact initialized settings from abvoe
        self.setParams(width,height,decim,startx,starty,mirrorv,mirrorh)

        cpr = self.getParams()
        self.decim = cpr.Decimation
        self.xpix = cpr.Width // cpr.Decimation
        self.ypix = cpr.Height // cpr.Decimation
        self.mirrorv= cpr.MirrorV
        self.mirrorh = cpr.MirrorH
        self.startx = cpr.StartX
        self.starty = cpr.StartY

        print('ROI width,height = ' + str(self.xpix) + ', ' + str(self.ypix))

        if verbose:
            print('color depth ' + str(cpr.ColorDeep))
#%% 8/10 bit setup
        if tenbit:  #FIXME just convert bool to byte instead
            self.set10BitsOutput(1)
        else:
            self.set10BitsOutput(0)

        self.tenbit = self.get10BitsOutput()
        if self.tenbit==1:
            print(' TEN BIT mode enabled')
        else:
            print(' EIGHT BIT mode enabled')
#%%
    def setParams(self,width,height,decim,startx,starty, mirrorv, mirrorh): #Set camera params
        old = self.getParams()

        params = _TFrameParams()
        if startx is not None and startx>=0:
            params.StartX = ct.c_int32(startx)
        else:
            params.StartX = ct.c_int32(old.StartX)

        if starty is not None and starty>=0:
            params.StartY = ct.c_int32(starty)
        else:
            params.StartY = ct.c_int32(old.StartY)

        if width is not None and width>0: #it's ok to pass odd number
            params.Width  = ct.c_int32(width)
        else:
            params.Width  = ct.c_int32(old.Width)

        if height is not None and height>0:
            params.Height = ct.c_int32(height)
        else:
            params.Height = ct.c_int32(old.Height)

        if decim is not None and decim in tuple(range(1,9)):
            params.Decimation= ct.c_int32(decim)
        else:
            params.Decimation= ct.c_int32(old.Decimation)

        if mirrorv is not None and mirrorv>0:
            params.MirrorV = ct.c_byte(mirrorv)
        else:
            params.MirrorV = ct.c_byte(old.MirrorV)

        if mirrorh is not None and mirrorh>0:
            params.MirrorH = ct.c_byte(mirrorh)
        else:
            params.MirrorH = ct.c_byte(old.MirrorH)

        self.openCamera()
        rc = self.dll.CxSetScreenParams(self.h, ct.byref(params))
        if rc == 0:
            print('** CxSetScreenParams: problem setting parameter choices')
        else:
            rc = self.dll.CxActivateScreenParams(self.h)
            if rc == 0:
                print('** CxActivateScreenParams: Problem activating parameters')
        self.closeCamera()
#%%
    def openCamera(self, cid=None): #attempt initial connection to camera
        if not self.isopen:
            self.h = self.dll.CxOpenDevice(cid)
        if self.h == -1:
            exit("*** Camera not found on open attempt with " + str(DLL))
        else:
            self.isopen = True

    def open(self,cid=None):
        self.openCamera(cid)

    def close(self):
        self.closeCamera()

    def closeCamera(self): #final closing of camera connection
        if self.isopen:
            self.dll.CxCloseDevice(self.h) #no return code
            self.h = None
        self.isopen = False

    def setFrequency(self,freqbyte):
        if freqbyte == 1: #24MHz
            freq = ct.c_byte(1)
        elif freqbyte == 0: #12MHz
            freq = ct.c_byte(0)
        else:
            print('*** I can only accept 1->24MHz or 0->12MHz to set sensor frequency')
            return

        self.openCamera()
        rc = self.dll.CxSetFrequency(self.h,freq) #not ct.byref()
        if rc == 0:
            print("** CxSetFrequency: Unable to set sensor frequency ")
        self.closeCamera()

    def getFrequency(self):
        freq = ct.c_byte()
        self.openCamera()
        rc = self.dll.CxGetFrequency(self.h, ct.byref(freq))
        self.closeCamera()
        if rc == 0:
            print("*** CxGetFrequency: Unable to get sensor frequency")
            return None

        freq = freq.value

        if freq==0:
            return '12 MHz'
        elif freq==1:
            return '24 MHz'
        else:
            print('** CxGetFrequency: unknown response to CxGetFrequency')
            return None

    def getExposureMinMax(self):
        emin = ct.c_float(); emax = ct.c_float()
        self.openCamera()
        rc = self.dll.CxGetExposureMinMaxMs(self.h, ct.byref(emin), ct.byref(emax))
        self.closeCamera()
        if rc == 0:
            print("** CxGetExposureMinMaxMs: Unable to get min/max exposure")
            return None, None

        return emin.value, emax.value

    def getExposure(self): # get comera exposure in milliseconds
        exp = ct.c_float()
        self.openCamera()
        rc = self.dll.CxGetExposureMs(self.h, ct.byref(exp))
        self.closeCamera()
        if rc==0:
            print("*** CxGetExposureMs: Unable to get exposure")
            return None

        return exp.value

    def setExposure(self, expreq): # set comera exposure in milliseconds
        if expreq is not None:
            if expreq<0:
                print('** ignoring exposure request, it must be a positive number')
                return

            exp = ct.c_float()
            self.openCamera()
            rc = self.dll.CxSetExposureMs(self.h, ct.c_float(expreq), ct.byref(exp))
            self.closeCamera()
            if rc==0:
                print("** CxSetExposureMs: Unable to set exposure=" + str(expreq))

    def setAllGain(self, gainreq): #sets gain for all colors simultaneously
        if gainreq is not None:

            gain = ct.c_int32(gainreq)
            self.openCamera()
            rc = self.dll.CxSetAllGain(self,gain)
            self.closeCamera()
            if rc==0:
                print('** unable to set gain ' + str(gainreq))

    def startStream(self): # begin streaming acquisition
        print('starting camera stream ')
        self.openCamera()
        rc = self.dll.CxSetStreamMode(self.h, ct.c_byte(1))
        #leave connection open for streaming
        if rc==0:
            print('** CxSetStreamMode: unable to start camera stream')

    def stopStream(self): # end streaming acquisition
        print('stopping camera stream')
        self.openCamera()
        rc=self.dll.CxSetStreamMode(self.h, ct.c_byte(0))
        self.closeCamera()
        if rc==0:
            print('** CxSetStreamMode: unable to stop camera stream')

    def grabFrame(self): #grab latest frame in stream
        """ for SMX-M8XC, the "color" camera passes back a grayscale image that was
         Bayer filtered--you'll need to demosaic! """
        Nbuffer = self.xpix * self.ypix
        imbuffer = (ct.c_ubyte * Nbuffer)()
        bufferbytes = Nbuffer # each pixel is 1 byte

        if not self.isopen: self.openCamera()
        rc = self.dll.CxGrabVideoFrame(self.h, ct.byref(imbuffer), bufferbytes)
        if rc==0:
            print("** CxGrabVideoFrame: problem getting frame, return code " + str(rc))
            return None

        return asarray(imbuffer).reshape((self.ypix,self.xpix), order='C')

    def get10BitsOutput(self): #8 or 10 bits
        getbit = ct.c_byte()
        self.openCamera()
        rc = self.dll.CxGet10BitsOutput(self.h, ct.byref(getbit))
        self.closeCamera()
        if rc==0:
            print("** CxGet10BitsOutput: Error getting bit mode")
            return None
        return getbit.value

    def set10BitsOutput(self,useten): #0=8 bit, 1=10bit
        if not useten in (0,1):
            print('*** valid input is 0 for 8-bit, or 1 for 10-bit')
            return

        self.openCamera()
        rc = self.dll.CxSet10BitsOutput(self.h, ct.c_byte(useten))
        self.closeCamera()
        if rc==0:
            print("** CxSet10BitsOutput: Error setting bit mode")

    def getParams(self):
        params = _TFrameParams()
        self.openCamera()
        rc = self.dll.CxGetScreenParams(self.h, ct.byref(params))
        self.closeCamera()
        if rc==0:
            print('** CxGetScreenParams: error getting params')
            return None
        return params

    def getCameraInfoEx(self):
        det = _TCameraInfoEx()
        self.openCamera()
        rc = self.dll.CxGetCameraInfoEx(self.h, ct.byref(det))
        self.closeCamera()
        if rc==0:
            print('** CxGetCameraInfoEx: error getting camera info')
            return None
        return det

    def getCameraInfo(self):
        det = _TCameraInfo()
        self.openCamera()
        rc = self.dll.CxGetCameraInfo(self.h, ct.byref(det))
        self.closeCamera()
        if rc == 0:
            print('** CxGetCameraInfo: Error getting camera info')
            return None
        #print((det.MaxWidth, det.MaxHeight))

        return det

"""
https://docs.python.org/3/library/ctypes.html#ctypes.Structure
"""

class _TFrameParams(ct.Structure): #ct.Structure must be input argument
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
    _fields_ = [("HWModelID",ct.c_ushort),
                ("HWVersion",ct.c_ushort),
                ("HWSerial", ct.c_ulong)]


class Convert:
    def __init__(self, dll=DLL):
        self.dll = ct.windll.LoadLibrary(dll)

    def BayerToRgb(self,bayerimg, bayerint):
        if bayerimg is None: return None

        if bayerimg.ndim != 2:
            print('only accepts 2-D mosaiced images')
            return None

        if not bayerint in range(6):
            print('** bayer mode must be in 0,1,2,3,4,5')
            print('0: monochrome , 1: nearest neighbor, 2: bilinear' +
            '3:Laplacian, 4:Real Monochrome, 5:Bayer Average')
            return None

        """
        note, even if selecting 0: Monochrome, the image returned is I X J X 3
        """
        h,w = bayerimg.shape

        Width = ct.c_int32(w)
        Height = ct.c_int32(h)
        BayerAlg = ct.c_int32(bayerint)

        Nbuffer = w * h
        inbuffer = (ct.c_ubyte * Nbuffer)(*bayerimg.ravel(order='C'))
        outbuffer = (ct.c_ubyte * Nbuffer*3)()

        rc = self.dll.CxBayerToRgb(ct.byref(inbuffer),
                                   Width, Height, BayerAlg,
                                   ct.byref(outbuffer))
        if rc==0:
            print('could not convert image'); return None

        # this is a BGR array if color
        dimg = asarray(outbuffer).reshape((h,w,3), order='C')

        if bayerint in (0,4): #monochrome
            dimg = dimg[...,0] # all pages identical
        else:
            dimg = dimg[...,::-1] #reverse colors, BGR -> RGB
        return dimg

if __name__ == '__main__':
    c = Camera()
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

if system().lower()=='windows':
    DLL = join('c:\\','Sumix','SMX-M8x USB2.0 Camera','API','SMXM8X.dll')
else:
    exit('*** this driver made only for Windows, you appear to be running ' + system() )

if isfile(DLL):
    print('using ' + DLL)
else:
    exit('could not find driver file ' + DLL)

class Camera:
    def __init__(self, width=None,height=None, decim=None,
                 dll=DLL):
        self.dll = ct.windll.LoadLibrary(dll)
        self.isopen = False
        self.h = None
        self.startx=0
        self.starty=0
        self.width = width
        self.height = height
        self.decimation = decim #1,2,3 are believed to work. 4 was scrambled?
        self.mirrorv=0
        self.mirrorh=0

    def openCamera(self, cid=None): #attempt initial connection to camera
        if not self.isopen:
            self.h = self.dll.CxOpenDevice(cid)
        if self.h == -1:
            exit("*** Camera not found on open attempt with " + str(DLL))
        else:
            self.isopen = True

    def closeCamera(self): #final closing of camera connection
        if self.isopen:
            self.dll.CxCloseDevice(self.h) #no return code
        self.isopen = False

    def setFrequency(self,freqbyte):
        if not self.isopen: exit("*** Camera connection is not open")

        if freqbyte == 1: #24MHz
            freq = ct.c_byte(1)
        elif freqbyte == 0: #12MHz
            freq = ct.c_byte(0)
        else:
            exit('*** I can only accept 1->24MHz or 0->12MHz to set sensor frequency')

        rc = self.dll.CxSetFrequency(self.h,freq) #not ct.byref()
        if rc == 0: exit("*** Unable to set sensor frequency")

    def getFrequency(self):
        if not self.isopen: exit("*** Camera connection is not open")

        freq = ct.c_byte()
        rc = self.dll.CxGetFrequency(self.h, ct.byref(freq))
        freq = freq.value
        if rc == 0: exit("*** Unable to get sensor frequency")

        if freq==0:
            return '12 MHz'
        elif freq==1:
            return '24 MHz'
        else:
            print('** unknown response to CxGetFrequency')
            return None

    def getExposureMinMax(self):
        if not self.isopen:  exit("*** Camera connection is not open")

        emin = ct.c_float(); emax = ct.c_float()
        rc = self.dll.CxGetExposureMinMaxMs(self.h, ct.byref(emin), ct.byref(emax))
        if rc == 0: exit("*** Unable to get min/max exposure")

        return emin.value, emax.value

    def getExposure(self): # get comera exposure in milliseconds
        if not self.isopen:  exit("*** Camera connection is not open")

        exp = ct.c_float()
        rc = self.dll.CxGetExposureMs(self.h, ct.byref(exp))
        if rc==0: exit("*** Unable to get exposure")

        return exp.value

    def setExposure(self, expreq): # set comera exposure in milliseconds
        if expreq is not None:
            if not self.isopen:  exit("*** Camera connection is not open")
    
            exp = ct.c_float()
            rc = self.dll.CxSetExposureMs(self.h, ct.c_float(expreq), ct.byref(exp))
            if rc==0: exit("*** Unable to set exposure")

    def startStream(self): # begin streaming acquisition
        if not self.isopen:  exit("*** Camera connection is not open")

        return self.dll.CxSetStreamMode(self.h, ct.c_byte(1))

    def stopStream(self): # end streaming acquisition
        if not self.isopen:  exit("*** Camera connection is not open")

        return self.dll.CxSetStreamMode(self.h, ct.c_byte(0))

    def grabFrame(self,xpix,ypix): #grab latest frame in stream
        """ for SMX-M8XC, the "color" camera passes back a grayscale image that was
         Bayer filtered--you'll need to demosaic! """
        if not self.isopen:  exit("*** Camera connection is not open")

        Nbuffer = xpix*ypix
        imbuffer = (ct.c_ubyte * Nbuffer)()
        bufferbytes = Nbuffer # each pixel is 1 byte

        rc = self.dll.CxGrabVideoFrame(self.h, ct.byref(imbuffer), bufferbytes)
        if rc==0: exit("*** problem getting frame, return code " + str(rc))

        out = asarray(imbuffer).reshape((ypix,xpix), order='C')
        return out

    def get10BitsOutput(self): #8 or 10 bits
        if not self.isopen:  exit("*** Camera connection is not open")

        getbit = ct.c_byte()
        rc = self.dll.CxGet10BitsOutput(self.h, ct.byref(getbit))
        if rc==0:  exit("*** Error getting bit mode")
        return getbit.value

    def set10BitsOutput(self,useten): #0=8 bit, 1=10bit
        if not self.isopen:  exit("*** Camera connection is not open")

        rc = self.dll.CxSet10BitsOutput(self.h, ct.c_byte(useten))
        if rc==0: exit("*** Error setting bit mode")


    def setParams(self): #Set camera params
        if not self.isopen:  exit("*** Camera connection is not open")

        params = _TFrameParams()
        params.StartX = ct.c_int(self.startx)
        params.StartY = ct.c_int(self.starty)
        params.Width  = ct.c_int(self.width)
        params.Height = ct.c_int(self.height)
        params.Decimation= ct.c_int(self.decimation)
        params.MirrorV = ct.c_byte(self.mirrorv)
        params.MirrorH = ct.c_byte(self.mirrorh)
        self.dll.CxSetScreenParams(self.h, ct.byref(params))

    def getParams(self):
        if not self.isopen:  exit("*** Camera connection is not open")

        params = _TFrameParams()
        self.dll.CxGetScreenParams(self.h, ct.byref(params))

        return params

    def getCameraInfoEx(self):
        if not self.isopen:  exit("*** Camera connection is not open")

        details = _TCameraInfoEx()
        self.dll.CxGetCameraInfoEx(self.h, ct.byref(details))

        return details

    def getCameraInfo(self):
        if not self.isopen:  exit("*** Camera connection is not open")

        details = _TCameraInfo()
        self.dll.CxGetCameraInfo(self.h, ct.byref(details))

        return details

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
                ("DeviceName", ct.c_char_p)]

class _TCameraInfoEx(ct.Structure):
    _fields_ = [("HWModelID",ct.c_ushort),
                ("HWVersion",ct.c_ushort),
                ("HWSerial", ct.c_ulong)]

#!/usr/bin/python3
"""
Demonstrator of Sumix camera
michael@scivision.co
GPLv3+ license
to stop free run demo, on Windows press <esc> or <space> when focused on terminal window
    on Linux, press <ctrl> c (sigint)
"""
from numpy import uint8, empty
from os.path import splitext,expanduser
from platform import system
#
from sumixapi import Camera
from demosaic import gbrg2rbg
platf = system().lower()
if platf=='windows':
    from msvcrt import getwch, kbhit
    windows = True
else:
    windows = False

def main(w,h,nframe,expreq, decimreq, color, set10bit, preview, verbose=False):
#%% setup camera class
    cam = Camera(w,h,decimreq) # creates camera object
    cam.openCamera()     # makes connection to camera

    if verbose:
        cdet = cam.getCameraInfo()
        if cdet.SensorType==0:
            print('camera is black and white')
        elif cdet.SensorType==1:
            print('camera is color')
        cdetex = cam.getCameraInfoEx()
        print(cdetex.HWModelID, cdetex.HWVersion, cdetex.HWSerial)


    if set10bit:  #FIXME just convert bool to byte instead
        cam.set10BitsOutput(1)
    else:
        cam.set10BitsOutput(0)
    tenbit = cam.get10BitsOutput()
    if tenbit==1:
        print(' TEN BIT mode enabled')
    else:
        print(' EIGHT BIT mode enabled')
#%% sensor configuration
    cam.setParams()

    cparam = cam.getParams()
    decim = cparam.Decimation
    xpix = cparam.Width//decim
    ypix = cparam.Height//decim
    print('ROI width,height = ' + str(xpix) + ', ' + str(ypix))
    if verbose:
        print('color depth ' + str(cparam.ColorDeep))

    cam.setFrequency(1)     #set to 24MHz (fastest)
    print('camera sensor frequency ' + str(cam.getFrequency())) #str() in case it's NOne

    if expreq is not None and 0.2 < expreq < 10000: #need short circuit
        if verbose:
            emin,emax = cam.getExposureMinMax()
            print('camera exposure min, max [ms] = {:0.3f}'.format(emin) + ', {:0.1f}'.format(emax))
        cam.setExposure(expreq)
    exptime = cam.getExposure()
    print('exposure is {:0.3f}'.format(exptime) + ' ms.')
#%% setup figure (for loter plotting)
    if preview:
        figure(1).clf(); fgrw = figure(1);  axrw = fgrw.gca()
        hirw = axrw.imshow(empty((ypix,xpix), dtype=uint8),
                           origin='upper', #this is consistent with Sumix chip and tiff
                           vmin=0, vmax=256, cmap='gray')
        #fgrw.colorbar(hirw,ax=axrw)
    else:
        hirw = None
#%% start acquisition
    cam.startStream()
    if nframe is None:
        frames = freewheel(cam,xpix,ypix, color,hirw)
    elif 0 < nframe < 200:
        frames =fixedframe(nframe,cam,xpix,ypix, color,hirw)
    else:
        exit('*** I dont know what to do with nframe=' + str(nframe))
#%% shutdown camera
    cam.stopStream()
    cam.closeCamera()
    return frames
#%% ===========================
def freewheel(cam,xpix,ypix, color,hirw):
    try:
        while True:
            frame = cam.grabFrame(xpix,ypix)

            if color:
                frame = gbrg2rbg(frame, color)

            if hirw is not None:
                hirw.set_data(frame.astype(uint8))
                draw(); pause(0.001)

            if windows and kbhit():
                keyputf = getwch()
                if keyputf == u'\x1b' or keyputf == u' ':
                    print('halting acquisition due to user keypress')
                    break

    except KeyboardInterrupt:
        print('halting acquisition')

    return frame

def fixedframe(nframe,cam,xpix,ypix, color,hirw):
    if color:
        frames = empty((nframe,ypix,xpix,3), dtype=uint8)
    else:
        frames = empty((nframe,ypix,xpix), dtype=uint8)

    try:
        for i in range(nframe):
            frame = cam.grabFrame(xpix,ypix)

            if color:
                frames[i,...] = gbrg2rbg(frame, color)
            else:
                frames[i,...] = frame

            if hirw is not None:
                hirw.set_data(frames[i,...].astype(uint8))
                #hirw.cla()
                #hirw.imshow(dframe)
                draw(); pause(0.001)
    except KeyboardInterrupt:
        print('halting acquisition per user Ctrl-C')

    return frames

def saveframes(ofn,frames):
    if ofn is not None and frames is not None:
        ext = splitext(expanduser(ofn))[1].lower()
        if ext[:4] == '.tif':
            #from skimage.io._plugins import freeimage_plugin as freeimg
            #freeimg.write_multipage(frames, ofn)
            import tifffile
            print('tifffile write ' + ofn)
            tifffile.imsave(ofn,frames,compress=6,
                        photometric='minisblack', # to avoid writing RGB!
                        description='my Sumix data',
                        extratags=[(65000,'s',None,'My custom tag #1',True),
                                   (65001,'s',None,'My custom tag #2',True),
                                   (65002,'f',2,[123456.789,9876.54321],True)])
        elif ext == '.h5':
            import h5py
            with h5py.File(ofn,libver='latest') as f:
                f.create_dataset('/images',data=frames,compression='gzip')
#%%
if __name__ == '__main__':
    from argparse import ArgumentParser
    p = ArgumentParser(description="Sumix Camera demo")
    p.add_argument('-c','--color',help='use Bayer demosaic for color camera (display only, disk writing is raw)',action='store_true')
    p.add_argument('-d','--decim',help='decimation (binning)',type=int,default=1)
    p.add_argument('-e','--exposure',help='exposure set [ms]',type=float,default=None)
    p.add_argument('-n','--nframe',help='number of images to acquire',type=int,default=None)
    p.add_argument('-f','--file',help='name of tiff file to save (non-demosaiced)',type=str,default=None)
    p.add_argument('-x','--width',help='width in pixels of ROI',type=int,default=1280)
    p.add_argument('-y','--height',help='height in pixels of ROI',type=int,default=1024)
    p.add_argument('-t','--tenbit',help='selects 10-bit data mode (default 8-bit)',action='store_true')
    p.add_argument('-p','--preview',help='shows live preview of images acquired',action='store_true')
    p.add_argument('-v','--verbose',help='more verbose feedback to user console',action='store_true')
    a = p.parse_args()

    if a.preview:
        from matplotlib.pyplot import figure,draw,pause#, show

    frames = main(a.width,a.height, a.nframe, a.exposure, a.decim, a.color, a.tenbit, a.preview, a.verbose)

    saveframes(a.file,frames)

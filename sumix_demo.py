#!/usr/bin/python3
"""
Demonstrator of Sumix camera
michael@scivision.co
GPLv3+ license
"""
from sumixapi import Camera
from matplotlib.pyplot import figure,draw,pause#, show
from numpy import uint8, empty
#
from demosaic import gbrg2rbg

def main(w,h,nframe,expreq, decimreq, color, set10bit, verbose=False):
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
    figure(1).clf(); fgrw = figure(1);  axrw = fgrw.gca()
    hirw = axrw.imshow(empty((ypix,xpix), dtype=uint8), origin='bottom',
                       vmin=0, vmax=256, cmap='gray')
    #fgrw.colorbar(hirw,ax=axrw)
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
                dframe = gbrg2rbg(frame)
            else:
                dframe = frame
            
            if hirw is not None:
                hirw.set_data(dframe)
                draw(); pause(0.001)
    except KeyboardInterrupt:
        print('halting acquisition')

    return frame

def fixedframe(nframe,cam,xpix,ypix, color,hirw):
    frames = empty((nframe,ypix,xpix), dtype=uint8)
    try:
        for i in range(nframe):
            frame = cam.grabFrame(xpix,ypix)
            frames[i,...] = frame
            
            if color:
                dframe = gbrg2rbg(frame)
            else:
                dframe = frame
            
            if hirw is not None:
                hirw.set_data(dframe)
                #hirw.cla()
                #hirw.imshow(dframe)
                draw(); pause(0.001)
    except KeyboardInterrupt:
        print('halting acquisition per user Ctrl-C')

    return frames
#%%
if __name__ == '__main__':
    from argparse import ArgumentParser
    p = ArgumentParser(description="Sumix Camera demo")
    p.add_argument('-c','--color',help='use Bayer demosaic for color camera (display only, disk writing is raw)',action='store_true')
    p.add_argument('-d','--decim',help='decimation (binning)',type=int,default=1)
    p.add_argument('-e','--exposure',help='exposure set [ms]',type=float,default=None)
    p.add_argument('-n','--nframe',help='number of images to acquire',type=int,default=None)
    p.add_argument('-f','--file',help='name of tiff file to save',type=str,default=None)
    p.add_argument('-x','--width',help='width in pixels of ROI',type=int,default=1280)
    p.add_argument('-y','--height',help='height in pixels of ROI',type=int,default=1024)
    p.add_argument('-t','--tenbit',help='selects 10-bit data mode (default 8-bit)',action='store_true')
    a = p.parse_args()

    frames = main(a.width,a.height, a.nframe, a.exposure, a.decim, a.color,a.tenbit)
    
    if a.file is not None:
        from os.path import splitext
        ext = splitext(a.file)[1].lower()
        if ext[:4] == '.tif':
            from skimage.io._plugins import freeimage_plugin as freeimg
            freeimg.write_multipage(frames, a.file)
        elif ext == '.h5':
            import h5py
            with h5py.File(a.file,libver='latest') as f:
                f.create_dataset('/images',data=frames,compression='gzip')
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
from demosaic import demosaic

def main(w,h,nframe,expreq, decimreq,verbose=False):
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

        tenbit = cam.get10BitsOutput()
        if tenbit==1:
            print(' TEN BIT model enabled')
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
        frames = freewheel(cam,hirw,xpix,ypix)
    elif 0 < nframe < 200:
        frames =fixedframe(nframe,cam,hirw,xpix,ypix)
    else:
        exit('*** I dont know what to do with nframe=' + str(nframe))
#%% shutdown camera
    cam.stopStream()
    cam.closeCamera()
    return frames
#%% ===========================
def freewheel(cam,hirw,xpix,ypix):
    try:
        while True:
            frame = cam.grabFrame(xpix,ypix)
            frame = demosaic(frame,pattern='gbrg',clip=(0.,255.))
            hirw.set_data(frame)
            draw(); pause(0.001)
    except KeyboardInterrupt:
        print('halting acquisition')

    return frame

def fixedframe(nframe,cam,hirw,xpix,ypix):
    frames = empty((nframe,ypix,xpix), dtype=uint8)
    try:
        for i in range(nframe):
            frame = cam.grabFrame(xpix,ypix)
            frames[i,...] = frame
            dframe = demosaic(frame,pattern='gbrg',clip=(0,255))
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
    p.add_argument('-d','--decim',help='decimation (binning)',type=int,default=1)
    p.add_argument('-e','--exposure',help='exposure set [ms]',type=float,default=None)
    p.add_argument('-n','--nframe',help='number of images to acquire',type=int,default=None)
    p.add_argument('-f','--file',help='name of tiff file to save',type=str,default=None)
    p.add_argument('-x','--width',help='width in pixels of ROI',type=int,default=1280)
    p.add_argument('-y','--height',help='height in pixels of ROI',type=int,default=1024)
    a = p.parse_args()

    frames = main(a.width,a.height, a.nframe, a.exposure, a.decim)
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
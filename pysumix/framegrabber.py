from __future__ import division,absolute_import
import logging
from numpy import empty,uint8,string_
from os.path import splitext,expanduser
import tifffile
import h5py
from matplotlib.pyplot import figure,draw,pause
#
from .imgutil import iswindows,imagequota
from .sumixapi import Camera
from .demosaic import demosaic
#
windows = iswindows()
if windows:
    from msvcrt import getwch, kbhit

def runcam(w,h,nframe,expos, gain, decim, color, tenbit, preview, verbose=False):
#%% setup camera class
    cam = Camera(w,h,decim,tenbit,verbose=verbose) # creates camera object and opens connection

    if verbose>0:
        cdetex = cam.getCameraInfoEx()
        print('model {}  HWversion {}  serial {}'.format(cdetex.HWModelID, cdetex.HWVersion, cdetex.HWSerial))
#%% sensor configuration
    cam.setFrequency(1)     #set to 24MHz (fastest)
    logging.info('camera sensor frequency {}'.format(cam.getFrequency()))


    if verbose>1:
        emin,emax = cam.getExposureMinMax()
        print('camera exposure min, max [ms] = {:.3f}, {:.1f}'.format(emin,emax))
    cam.setExposure(expos)
    exptime = cam.getExposure()
    print('exposure is {:.3f}'.format(exptime) + ' ms.')

    rgain = cam.setAllGain(gain)
#%% setup figure (for later plotting)
    if preview:
        fgrw = figure();  axrw = fgrw.gca()
        hirw = axrw.imshow(empty((cam.ypix,cam.xpix), dtype=uint8),
                           origin='upper', #this is consistent with Sumix chip and tiff
                           vmin=0, vmax=256, cmap='gray')
    else:
        hirw = None
#%% start acquisition
    cam.startStream()
    if nframe is None:
        frames = freewheel(cam, color,hirw)
    elif 0 < nframe < imagequota(): #you'll run out of PC RAM
        frames =fixedframe(nframe,cam, color,hirw)
    else:
        raise ValueError('I dont know what to do with nframe={}'.format(nframe))
#%% shutdown camera
    cam.stopStream()

    return frames, exptime, rgain

#%% grabber functions
def freewheel(cam, color,hirw):
    try:
        if windows:
            print('press Escape or Space to abort')
        while True:
            frame = cam.grabFrame()
            if frame is None:
                logging.critical('aborting acqusition due to camera communication problem')
                break

            if color:
                frame = demosaic(frame, '')

            if hirw is not None:
                hirw.set_data(frame.astype(uint8))
                draw(); pause(0.001)

            if windows and kbhit():
                keyputf = getwch()
                if keyputf in (u'\x1b',u' '):
                    print('halting acquisition due to user keypress')
                    break

    except KeyboardInterrupt:
        print('halting acquisition due to user keypress')

    return frame

def fixedframe(nframe,cam, color,hirw):
    """ grabs a preset number of frames, then exits
    """
    if color:
        frames = empty((nframe,cam.ypix,cam.xpix,3), dtype=uint8)
    else:
        frames = empty((nframe,cam.ypix,cam.xpix), dtype=uint8)

    try:
        for i in range(nframe):
            frame = cam.grabFrame()

            if color:
                frames[i,...] = demosaic(frame, '', color=color)
            else:
                frames[i,...] = frame

            if hirw is not None:
                hirw.set_data(frames[i,...].astype(uint8))
                draw(); pause(0.001)
    except KeyboardInterrupt:
        print('halting acquisition at frame {} / {}'.format(i,nframe))

    return frames
#%% writer
def saveframes(ofn,frames,color,exptime,gain):
    if ofn is not None and frames is not None:
        ext = splitext(expanduser(ofn))[1].lower()
        print('tifffile write {}'.format(ofn))
        if ext[:4] == '.tif':
            pho = 'rgb' if color else 'minisblack'

            tifffile.imsave(ofn,frames,compress=6,
                        photometric=pho,
                        description=('exposure_sec {:0.3f}'.format(exptime/1000) +
                                     ',  gains_(g1 red g2 blue) '+str(list(gain.values()))  ),
                        extratags=[(33434,'f',1,exptime,True),
                                   (41991,'f',4,list(gain.values()),True),])
                                   #(65002,'f',2,[123456.789,9876.54321],True)])

        elif ext == '.h5':
            with h5py.File(ofn,'w',libver='latest') as f:
                fimg = f.create_dataset('/images',data=frames,compression='gzip')
                fimg.attrs["CLASS"] = string_("IMAGE")
                fimg.attrs["IMAGE_VERSION"] = string_("1.2")
                fimg.attrs["IMAGE_SUBCLASS"] = string_("IMAGE_GRAYSCALE")
                fimg.attrs["DISPLAY_ORIGIN"] = string_("LL")
                fimg.attrs['IMAGE_WHITE_IS_ZERO'] = uint8(0)

#!/usr/bin/python3
"""
Demonstrator of Sumix camera
michael@scivision.co
GPLv3+ license
to stop free run demo, on Windows press <esc> or <space> when focused on terminal window
    on Linux, press <ctrl> c (sigint)

Note: this demo has only been tested in 8 bit mode, 10 bit mode is untested.
"""
from __future__ import division,absolute_import
#
from pysumix.framegrabber import saveframes,runcam

if __name__ == '__main__':
    from argparse import ArgumentParser
    p = ArgumentParser(description="Sumix Camera demo")
    p.add_argument('-c','--color',help='use Bayer demosaic for color camera (display only, disk writing is raw)',action='store_true')
    p.add_argument('-d','--decim',help='decimation (binning)',type=int)
    p.add_argument('-e','--exposure',help='exposure set [ms]',type=float)
    p.add_argument('-n','--nframe',help='number of images to acquire',type=int)
    p.add_argument('-g','--gain',help='set gain for all channels',type=int)
    p.add_argument('-f','--file',help='name of tiff file to save (non-demosaiced)')
    p.add_argument('-x','--width',help='width in pixels of ROI',type=int)
    p.add_argument('-y','--height',help='height in pixels of ROI',type=int)
    p.add_argument('-t','--tenbit',help='selects 10-bit data mode (default 8-bit)',action='store_true')
    p.add_argument('-p','--preview',help='shows live preview of images acquired',action='store_true')
    p.add_argument('-v','--verbose',help='more verbose feedback to user console',action='count',default=0)
    p = p.parse_args()

    frames,exptime,gain = runcam(p.width,p.height, p.nframe, p.exposure, p.gain,
                                 p.decim, p.color, p.tenbit, p.preview, p.verbose)

    saveframes(p.file,frames,p.color, exptime,gain)

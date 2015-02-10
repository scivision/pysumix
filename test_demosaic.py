#!/usr/bin/env python3
""" testing demosaic of images"""
import h5py
from demosaic import gbrg2rbg
from numpy import empty,uint8
from matplotlib.pyplot import figure,draw,pause, hist, show
from os.path import expanduser

def main(fn,maxframe):

    with h5py.File(expanduser(fn),libver='latest',mode='r') as f:
        data = f['/images'].value


    ddim = data.shape
    #proc = empty((ddim[1],ddim[2],3,ddim[0]), dtype=float)
    fg = figure()
    ax = fg.gca()
    hi = ax.imshow(empty((ddim[1],ddim[2]), dtype=uint8), vmin=0, vmax=255)
    ht = ax.set_title('')
    for i,d in enumerate(data):
        proc = gbrg2rbg(d)
        hi.set_data(proc)
        ht.set_text(str(i) + ' max: ' + str(proc.max()))
        draw(); pause(0.001)

    figure(2)
    hist(proc.ravel(),bins=128)
    show()

if __name__ == '__main__':
    from argparse import ArgumentParser
    p = ArgumentParser(description='demosaicking test')
    p.add_argument('file',help='file to load',type=str)
    p.add_argument('-n','--frames',help='frame to read up to',type = int, default = None)
    a=p.parse_args()

    main(a.file,a.frames)


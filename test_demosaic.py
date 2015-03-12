#!/usr/bin/env python3
""" testing demosaic of images"""
from demosaic import gbrg2rgb
from numpy import empty,uint8, atleast_3d
from matplotlib.pyplot import figure,draw,pause, hist, show
from os.path import expanduser,splitext

def main(fn):
    fn = expanduser(fn)
    ext = splitext(fn)[1].lower()
    if ext == '.h5':
        import h5py
        with h5py.File(fn,libver='latest',mode='r') as f:
            data = f['/images'].value
    elif ext[:4] == '.tif':
        from tifffile import imread
        data = imread(fn)
    else:
        exit('unrecognized file type ' + ext)
        
    #keep axes in preferred order
    if data.ndim == 2:
        data = atleast_3d(data).transpose((2,0,1))
    elif data.ndim ==3:
        pass
    else:
        exit('unknown number of dimensions {:0d}'.format(data.ndim))
    ddim = data.shape

    fg = figure()
    ax = fg.gca()
    hi = ax.imshow(empty((ddim[1],ddim[2]), dtype=uint8), vmin=0, vmax=255)
    ht = ax.set_title('')
    for i,d in enumerate(data):
        proc = gbrg2rgb(d)
        hi.set_data(proc)
        ht.set_text('frame: ' + str(i) )
        draw(); pause(0.001)

    ax2 = figure(2).gca()
    hist(proc.ravel(),bins=128,normed=1)
    ax2.set_title('mean: {:0.1f}'.format(data.mean()) + ' max: ' + str(data.max()))
    ax2.set_xlabel('pixel value')
    ax2.set_ylabel('density')
    show()

if __name__ == '__main__':
    from argparse import ArgumentParser
    p = ArgumentParser(description='demosaicking test')
    p.add_argument('file',help='file to load',type=str)
    a=p.parse_args()

    main(a.file)


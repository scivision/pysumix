#!/usr/bin/env python3
""" testing demosaic of images"""
from demosaic import demosaic
from matplotlib.pyplot import figure,draw,pause, hist, show
from os.path import expanduser,splitext

def readimages(fn):
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
        data = data[None,:,:]
    elif data.ndim ==3:
        pass
    else:
        exit('unknown number of dimensions {:0d}'.format(data.ndim))
    return data

def showimages(data,demosalg='ours'):
    #ddim = data.shape

    fg = figure()
    ax = fg.gca()
    #without vmin, vmax it doesn't show anything!
   # hi = ax.imshow(empty((ddim[1],ddim[2],3), dtype=uint8), vmin=0, vmax=255)
    #ht = ax.set_title('')
    for i,d in enumerate(data):
        proc = demosaic(d,demosalg,4)
       # hi.set_data(proc)
       # ht.set_text('frame: ' + str(i) )
        if proc.ndim==2: #monochrome
            ax.imshow(proc,cmap='gray')
        else:
            ax.imshow(proc)
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

    data = readimages(a.file) #DONT'T squeeze, so that we can iterate
    #showimages(data,'ours')

    showimages(data,'sumix')



#!/usr/bin/env python
""" testing demosaic of images"""
from pysumix import Path
import logging
from matplotlib.pyplot import figure,draw,pause, hist, show
#
from pysumix.demosaic import demosaic

def readimages(fn):
    fn = Path(fn).expanduser()
    ext = fn.suffix.lower()
    if ext == '.h5':
        import h5py
        with h5py.File(str(fn),libver='latest',mode='r') as f:
            data = f['/images'].value
    elif ext.startswith('.tif'):
        from tifffile import imread
        data = imread(fn)
    else:
        from scipy.ndimage import imread
        try:
            data = imread(fn)
        except Exception as e:
            raise TypeError(' '.join(('unrecognized file type ', ext, str(e))))

    print('img shape  ' + str(data.shape))
    #keep axes in preferred order
    if data.ndim == 2:
        data = data[None,:,:]
    elif data.ndim ==3:
        if data.shape[2]==3: #try to detect RGB images wrongly passed in
            logging.warning('check that you havent loaded an RGB image, this may not work for shape ' + str(data.shape))
    else:
        raise TypeError('unknown number of dimensions {}'.format(data.ndim))
    return data

def showimages(data,demosalg):
    fg = figure()
    ax = fg.gca()
    #without vmin, vmax it doesn't show anything!
   # hi = ax.imshow(empty((ddim[1],ddim[2],3), dtype=uint8), vmin=0, vmax=255)
    #ht = ax.set_title('')
    proc = demosaic(data,demosalg,1,False)
    if proc is None:
        return

    for i,d in enumerate(proc):
       # hi.set_data(proc)
       # ht.set_text('frame: ' + str(i) )
        ax.cla()
        if d.ndim==2: #monochrome
            ax.imshow(d,cmap='gray')
        else:
            ax.imshow(d)
        draw(); pause(0.001)

    ax2 = figure(2).gca()
    hist(proc.ravel(),bins=128,normed=1)
    ax2.set_title('mean: {:.1f},  max: {:.1f}'.format(data.mean(), data.max()))
    ax2.set_xlabel('pixel value')
    ax2.set_ylabel('density')

if __name__ == '__main__':
    from argparse import ArgumentParser

    p = ArgumentParser(description='demosaicking test')
    p.add_argument('file',help='file to load')
    a=p.parse_args()

    data = readimages(a.file) #DON'T squeeze, so that we can iterate
    #showimages(data,'ours')

    showimages(data,'')
    show()

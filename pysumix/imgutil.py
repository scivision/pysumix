from platform import system
import psutil
#%% imaging utilities
def iswindows():
    return system().lower()=='windows'

def imagequota(x,y,bpp):
    """ calculates how many image frames you can have for a given pixel count and
    bit depth

    x: number of x pixels
    y: "       " y "
    bpp: bits per pixel
    """
    frac2use = 0.8 # 0.8 = use up to 80% of available RAM
    availbytes = psutil.virtual_memory().available
    framebytes = x*y*bpp//8
    return int(frac2use * (availbytes/framebytes))
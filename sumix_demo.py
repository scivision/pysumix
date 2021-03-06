#!/usr/bin/env python
"""
Demonstrator of Sumix camera

to stop free run demo, on Windows press <esc> or <space> when focused on terminal window
    on Linux, press <ctrl> c (sigint)

Note: this demo has only been tested in 8 bit mode, 10 bit mode is untested.
"""
from numpy import uint8, empty, string_
import numpy as np
from pathlib import Path
import os
import logging
from typing import Dict, Tuple

#
from pysumix.api import Camera
from pysumix.demosaic import demosaic

#
if os.name == "nt":
    from msvcrt import getwch, kbhit  # type: ignore
else:
    getwch = kbhit = None


def main(
    w: int,
    h: int,
    nframe: int,
    expos: float,
    gain: int,
    decim: int,
    color: bool,
    tenbit: bool,
    preview: bool,
    verbose: bool = False,
) -> Tuple[np.ndarray, float, Dict[str, int]]:
    # %% setup camera class
    cam = Camera(
        w, h, decim, tenbit, verbose=verbose
    )  # creates camera object and opens connection

    if verbose > 0:
        cdetex = cam.getCameraInfoEx()
        print("model", cdetex.HWModelID, "HWversion", cdetex.HWVersion, "serial", cdetex.HWSerial)
    # %% sensor configuration
    cam.setFrequency(1)  # set to 24MHz (fastest)
    if verbose > 0:
        print("camera sensor frequency", cam.getFrequency())  # str() in case it's NOne

    if verbose > 1:
        emin, emax = cam.getExposureMinMax()
        print("camera exposure min, max [ms] = {:.3f}, {:.1f}".format(emin, emax))

    cam.setExposure(expos)
    exptime = cam.getExposure()
    print("exposure is {:0.3f}".format(exptime) + " ms.")

    rgain = cam.setAllGain(gain)
    # %% setup figure (for loter plotting)
    if preview:
        figure(1).clf()
        fgrw = figure(1)
        axrw = fgrw.gca()
        hirw = axrw.imshow(
            empty((cam.ypix, cam.xpix), dtype=uint8),
            origin="upper",  # this is consistent with Sumix chip and tiff
            vmin=0,
            vmax=256,
            cmap="gray",
        )
    else:
        hirw = None
    # %% start acquisition
    cam.startStream()
    if nframe is None:
        frames = freewheel(cam, color, hirw)
    elif 0 < nframe < 200:
        frames = fixedframe(nframe, cam, color, hirw)
    else:
        raise ValueError("I dont know what to do with nframe={:d}".format(nframe))
    # %% shutdown camera
    cam.stopStream()

    return frames, exptime, rgain


# %% ===========================


def freewheel(cam, color: bool, hirw) -> np.ndarray:
    try:
        if kbhit is not None:
            print("press Escape or Space to abort")
        while True:
            frame = cam.grabFrame()
            if frame is None:
                logging.error("aborting acqusition due to camera communication problem")
                break

            if color:
                frame = demosaic(frame, "")

            if hirw is not None:
                hirw.set_data(frame.astype(uint8))
                draw()
                pause(0.001)

            if kbhit is not None and kbhit():
                keyputf = getwch()
                if keyputf == u"\x1b" or keyputf == u" ":
                    print("halting acquisition due to user keypress")
                    break

    except KeyboardInterrupt:
        print("halting acquisition")

    return frame


def fixedframe(nframe: int, cam, color: bool, hirw) -> np.ndarray:
    if color:
        frames = empty((nframe, cam.ypix, cam.xpix, 3), dtype=uint8)
    else:
        frames = empty((nframe, cam.ypix, cam.xpix), dtype=uint8)

    try:
        for i in range(nframe):
            frame = cam.grabFrame()

            if color:
                frames[i, ...] = demosaic(frame, "", color=color)
            else:
                frames[i, ...] = frame

            if hirw is not None:
                hirw.set_data(frames[i, ...].astype(uint8))
                # hirw.cla()
                # hirw.imshow(dframe)
                draw()
                pause(0.001)
    except KeyboardInterrupt:
        print("halting acquisition per user Ctrl-C")

    return frames


def saveframes(ofn: Path, frames, color: bool, exptime: float, gain: Dict[str, int]):
    if ofn is not None and frames is not None:
        ext = Path(ofn).expanduser().suffix.lower()
        if ext[:4] == ".tif":
            import tifffile

            print("write", ofn)

            pho = "rgb" if color else "minisblack"

            tifffile.imsave(
                ofn,
                frames,
                compress=6,
                photometric=pho,
                description=(
                    "exposure_sec {:0.3f}".format(exptime / 1000)
                    + ",  gains_(g1 red g2 blue) "
                    + str(list(gain.values()))
                ),
                extratags=[
                    (33434, "f", 1, exptime, True),
                    (41991, "f", 4, list(gain.values()), True),
                ],
            )
            # (65002,'f',2,[123456.789,9876.54321],True)])

        elif ext == ".h5":
            import h5py

            with h5py.File(ofn, "w") as f:
                fimg = f.create_dataset("/images", data=frames, compression="gzip")
                fimg.attrs["CLASS"] = string_("IMAGE")
                fimg.attrs["IMAGE_VERSION"] = string_("1.2")
                fimg.attrs["IMAGE_SUBCLASS"] = string_("IMAGE_GRAYSCALE")
                fimg.attrs["DISPLAY_ORIGIN"] = string_("LL")
                fimg.attrs["IMAGE_WHITE_IS_ZERO"] = uint8(0)


# %%
if __name__ == "__main__":
    from argparse import ArgumentParser

    p = ArgumentParser(description="Sumix Camera demo")
    p.add_argument(
        "-c",
        "--color",
        help="use Bayer demosaic for color (display only, disk writing is raw)",
        action="store_true",
    )
    p.add_argument("-d", "--decim", help="decimation (binning)", type=int)
    p.add_argument("-e", "--exposure", help="exposure set [ms]", type=float)
    p.add_argument("-n", "--nframe", help="number of images to acquire", type=int)
    p.add_argument("-g", "--gain", help="set gain for all channels", type=int)
    p.add_argument("-f", "--file", help="name of tiff file to save (non-demosaiced)")
    p.add_argument("-x", "--width", help="width in pixels of ROI", type=int)
    p.add_argument("-y", "--height", help="height in pixels of ROI", type=int)
    p.add_argument(
        "-t", "--tenbit", help="selects 10-bit data mode (default 8-bit)", action="store_true"
    )
    p.add_argument(
        "-p", "--preview", help="shows live preview of images acquired", action="store_true"
    )
    p.add_argument(
        "-v", "--verbose", help="more verbose feedback to user console", action="count", default=0
    )
    P = p.parse_args()

    if P.preview:
        from matplotlib.pyplot import figure, draw, pause

    frames, exptime, gain = main(
        P.width,
        P.height,
        P.nframe,
        P.exposure,
        P.gain,
        P.decim,
        P.color,
        P.tenbit,
        P.preview,
        P.verbose,
    )

    saveframes(P.file, frames, P.color, exptime, gain)

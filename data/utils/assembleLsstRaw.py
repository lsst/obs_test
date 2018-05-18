#!/usr/bin/env python
#
# LSST Data Management System
# Copyright 2016 LSST Corporation.
#
# This product includes software developed by the
# LSST Project (http://www.lsst.org/).
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the LSST License Statement and
# the GNU General Public License along with this program.  If not,
# see <http://www.lsstcorp.org/LegalNotices/>.
#
"""Assemble a set of LSSTSim channel images into one obs_test image
"""
from __future__ import absolute_import, division, print_function
import argparse
import glob
import os.path
import re

import numpy

import lsst.afw.geom as afwGeom
import lsst.afw.image as afwImage

OutFileName = "raw.fits"
SizeY = 1000  # number of pixels per amplifier in X direction (Y uses all pixels)


def openChannelImage(dirPath, x, y):
    """Open an LSSTSim channel raw image
    """
    globStr = os.path.join(dirPath, "imsim_*_R22_S00_C%d%d*" % (y, x))
    inDecoImagePathList = glob.glob(globStr)
    if len(inDecoImagePathList) != 1:
        raise RuntimeError("Found %s instead of 1 file" % (inDecoImagePathList,))
    inDecoImagePath = inDecoImagePathList[0]
    inDecoImageFileName = os.path.basename(inDecoImagePath)
    # calib images (which are float) have names such as imsim_2_R22_S00_C00.fits
    # raw images (which are unsigned int) have names such as imsim_890104911_R22_S00_C00_E000....
    if not re.match(r"imsim_\d\d\d\d\d", inDecoImageFileName):
        raise RuntimeError("Not raw data")

    print("loading %s as raw unsigned integer data" % (inDecoImageFileName,))
    return afwImage.DecoratedImageU(inDecoImagePath)


def assembleImage(dirPath):
    """Make one image by combining half of amplifiers C00, C01, C10, C11 of lsstSim data
    """
    # views and assembly operations require a masked image, not a DecoratedImage
    inDecoImage = openChannelImage(dirPath, 0, 0)
    fullInDim = inDecoImage.getDimensions()
    yStart = fullInDim[1] - SizeY
    if yStart < 0:
        raise RuntimeError("channel image unexpectedly small")
    subDim = afwGeom.Extent2I(fullInDim[0], SizeY)  # dimensions of the portion of a channel that we use
    inSubBBox = afwGeom.Box2I(afwGeom.Point2I(0, yStart), subDim)
    outBBox = afwGeom.Box2I(afwGeom.Point2I(0, 0), subDim*2)
    outDecoImage = afwImage.DecoratedImageU(outBBox)

    # copy metadata
    outDecoImage.setMetadata(inDecoImage.getMetadata())

    for x in (0, 1):
        for y in (0, 1):
            inDecoImage = openChannelImage(dirPath, x, y)
            inImage = inDecoImage.getImage()
            inView = inImage.Factory(inImage, inSubBBox)

            # flip image about x axis for the y = 1 channels
            if y == 1:
                arr = inView.getArray()
                if numpy.any(arr != 0):
                    arr[:, :] = numpy.flipud(arr)

            xStart = x*subDim[0]
            yStart = y*subDim[1]
            outSubBBox = afwGeom.Box2I(afwGeom.Point2I(xStart, yStart), subDim)
            outImage = outDecoImage.getImage()
            outView = outImage.Factory(outImage, outSubBBox)
            outView[:] = inView

    outDecoImage.writeFits(OutFileName)
    print("wrote assembled data as %r" % (OutFileName,))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="""Assemble a set of LSSTSim raw channel images into one obs_test image.

Output is written to the current directory as file %r, which is OVERWRITTEN if it exists.
""" % (OutFileName,),
    )
    parser.add_argument("dir", default=".", nargs="?",
                        help="directory containing LSSTSim channel images (at least for channels " +
                             "0,0, 0,1, 1,0 and 1,1); defaults to the current working directory.")
    args = parser.parse_args()

    assembleImage(args.dir)

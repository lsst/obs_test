#!/usr/bin/env python
#
# LSST Data Management System
# Copyright 2014 LSST Corporation.
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
import argparse
import time

import numpy
from astropy.io import fits

import lsst.afw.geom as afwGeom
import lsst.afw.image as afwImage
from lsst.meas.algorithms import Defects
from lsst.ip.isr import getDefectListFromMask

DefectsPath = "defects_c0.dat"
"""Output path for defects file."""
detectorName = "0"
"""Detector name."""
detectorSerial = "0000011"
"""Detector serial code"""


def writeDefectsFile(bboxList, path, detectorSerial, detectorName):
    """Write a defects FITS file.

    Parameters
    ----------
    bboxList : `list` of `lsst.geom.Box2I`
        List of bounding boxes defining defect locations.
    path : `str`
        Path of output defects file; should end with ".dat".
    detectorSerial : `str`
        Serial code of detector.
    detectorName : `str`
        Name of detector.
    """
    with open(path, 'w') as fh:
        fh.write("#  x0 y0 x_extent y_extent\n")
        for box in bboxList:
            fh.write(f'{box.getMinX():>8} {box.getMinY():>8} {box.getWidth():>8} {box.getHeight():>8}\n')


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="""Construct a defects file from the mask plane of a test camera bias frame.
To use this command you must setup ip_isr and astropy.
Output is written to the current directory as file %r, which must not already exist.
""" % (DefectsPath,)
    )
    parser.add_argument("bias", help="path to bias image for the test camera")
    args = parser.parse_args()

    biasMI = afwImage.MaskedImageF(args.bias)
    defectList = getDefectListFromMask(biasMI, "BAD")
    bboxList = [defect.getBBox() for defect in defectList]
    writeDefectsFile(bboxList, DefectsPath, detectorSerial, detectorName)
    print("wrote defects file %r" % (DefectsPath,))

    test2BBoxList = Defects.readLsstDefectsFile(DefectsPath)
    assert len(bboxList) == len(test2BBoxList)
    for boxA, boxB in zip(bboxList, test2BBoxList):
        assert boxA == boxB.getBBox()
    print("verified that defects file %r round trips correctly" % (DefectsPath,))

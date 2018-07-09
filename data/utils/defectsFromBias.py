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
from lsst.ip.isr import getDefectListFromMask

DefectsPath = "defects_c0.fits"
detectorName = "0"
detectorSerial = "0000011"


def getBBoxList(path, detectorName):
    """Read a defects file and return the defects as a list of bounding boxes
    """
    with fits.open(path) as hduList:
        for hdu in hduList[1:]:
            if hdu.header["name"] != detectorName:
                print("skipping header with name=%r" % (hdu.header["name"],))
                continue

            bboxList = []
            for data in hdu.data:
                bbox = afwGeom.Box2I(
                    afwGeom.Point2I(int(data['x0']), int(data['y0'])),
                    afwGeom.Extent2I(int(data['width']), int(data['height'])),
                )
                bboxList.append(bbox)
            return bboxList
        raise RuntimeError("Data not found for detector %r" % (detectorName,))


def writeDefectsFile(bboxList, path, detectorSerial, detectorName):
    head = fits.Header()
    head.update('SERIAL', detectorSerial, 'Serial of the detector')
    head.update('NAME', detectorName, 'Name of detector for this defect map')
    head.update('CDATE', time.asctime(time.gmtime()), 'UTC of creation')

    x0 = numpy.array([d.getMinX() for d in bboxList])
    y0 = numpy.array([d.getMinY() for d in bboxList])
    width = numpy.array([d.getWidth() for d in bboxList])
    height = numpy.array([d.getHeight() for d in bboxList])

    col1 = fits.Column(name='x0', format='I', array=numpy.array(x0))
    col2 = fits.Column(name='y0', format='I', array=numpy.array(y0))
    col3 = fits.Column(name='height', format='I', array=numpy.array(height))
    col4 = fits.Column(name='width', format='I', array=numpy.array(width))
    cols = fits.ColDefs([col1, col2, col3, col4])
    tbhdu = fits.new_table(cols, header=head)
    hdu = fits.PrimaryHDU()
    thdulist = fits.HDUList([hdu, tbhdu])
    thdulist.writeto(DefectsPath)


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

    test2BBoxList = getBBoxList(DefectsPath, detectorName)
    assert len(bboxList) == len(test2BBoxList)
    for boxA, boxB in zip(bboxList, test2BBoxList):
        assert boxA == boxB
    print("verified that defects file %r round trips correctly" % (DefectsPath,))

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

import dateutil.parser

import lsst.afw.image as afwImage
from lsst.ip.isr import Defects

DefectsPath = "defects_c0"
"""Output path for defects file."""
detectorName = "0"
"""Detector name."""
detectorSerial = "0000011"
"""Detector serial code"""


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=f"""Construct a defects file from the mask plane of a test camera bias frame.
To use this command you must setup ip_isr and astropy.
Output is written to the current directory as file {DefectsPath}, which must not already exist.
"""
    )
    parser.add_argument("bias", help="path to bias image for the test camera")
    args = parser.parse_args()

    biasMI = afwImage.MaskedImageF(args.bias)
    defectList = Defects.fromMask(biasMI, "BAD")
    valid_start = dateutil.parser.parse('19700101T000000')
    md = defectList.getMetadata()
    md['INSTRUME'] = 'test'
    md['DETECTOR'] = detectorName
    md['CALIBDATE'] = valid_start.isoformat()
    md['FILTER'] = None
    defect_file = defectList.writeText(DefectsPath)
    print("wrote defects file %r" % (DefectsPath,))

    test2defectList = Defects.readText(defect_file)
    assert defectList == test2defectList
    print("verified that defects file %r round trips correctly" % (DefectsPath,))

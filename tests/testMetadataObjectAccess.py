#!/usr/bin/env python

#
# LSST Data Management System
# Copyright 2017 LSST Corporation.
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

import lsst.afw.image
import lsst.daf.persistence as dafPersist
import lsst.utils.tests
from lsst.utils import getPackageDir
import os
import unittest

obsTestDir = getPackageDir('obs_test')

class TestCalexpMetadataObjects(unittest.TestCase):
    """A test case for getting metadata objects from a Calexp"""

    def setUp(self):
        self.input = os.path.join(obsTestDir,
                                  'data',
                                  'calexpMetadataObjectsTest')

    def test(self):
        """Get the wcs, calib, and visitInfo from a calexp dataset."""
        butler = dafPersist.Butler(inputs=self.input)
        wcs = butler.get('calexp_wcs', filter='r', immediate=True)
        calib = butler.get('calexp_calib', filter='r', immediate=True)
        visitInfo = butler.get('calexp_visitInfo', filter='r', immediate=True)
        calexp = butler.get('calexp', filter='r', immediate=True)
        self.assertIsInstance(wcs, lsst.afw.image.Wcs)
        self.assertIsInstance(calib, lsst.afw.image.Calib)
        self.assertIsInstance(visitInfo, lsst.afw.image.VisitInfo)
        self.assertIsInstance(calexp, lsst.afw.image.ExposureF)


class MemoryTester(lsst.utils.tests.MemoryTestCase):
    pass


def setup_module(module):
    lsst.utils.tests.init()


if __name__ == "__main__":
    lsst.utils.tests.init()
    unittest.main()

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
from __future__ import absolute_import, division, print_function

import math
import os
import unittest

import lsst.afw.image
import lsst.daf.persistence as dafPersist
import lsst.utils.tests
from lsst.utils import getPackageDir

obsTestDir = getPackageDir('obs_test')


class TestCalexpMetadataObjects(lsst.utils.tests.TestCase):
    """A test case for getting metadata objects from a Calexp"""

    def setUp(self):
        self.input = os.path.join(obsTestDir,
                                  'data',
                                  'calexpMetadataObjectsTest')

    def nanSafeAssertEqual(self, val1, val2):
        try:
            self.assertEqual(val1, val2)
        except AssertionError as err:
            if math.isnan(val1) and math.isnan(val2):
                pass
            else:
                raise err

    def testNanSafeAssertEqual(self):
        val1 = float('nan')
        val2 = float(123.45)
        with self.assertRaises(AssertionError):
            self.nanSafeAssertEqual(val1, val2)
        val1 = float(123.44)
        val2 = float(123.45)
        with self.assertRaises(AssertionError):
            self.nanSafeAssertEqual(val1, val2)
        # should not raise:
        val1 = float('nan')
        val2 = float('nan')
        self.nanSafeAssertEqual(val1, val2)
        val1 = float(123.45)
        val2 = float(123.45)
        self.nanSafeAssertEqual(val1, val2)

    def test(self):
        """Get the wcs, calib, and visitInfo from a calexp dataset."""
        butler = dafPersist.Butler(inputs=self.input)
        wcs = butler.get('calexp_wcs', immediate=True)
        calib = butler.get('calexp_calib', immediate=True)
        visitInfo = butler.get('calexp_visitInfo', immediate=True)
        filt = butler.get('calexp_filter', immediate=True)
        calexp = butler.get('calexp', immediate=True)
        self.assertIsInstance(calexp, lsst.afw.image.ExposureF)

        self.assertIsInstance(wcs, lsst.afw.image.Wcs)
        self.assertWcsAlmostEqualOverBBox(wcs, calexp.getWcs(), calexp.getBBox())

        self.assertIsInstance(calib, lsst.afw.image.Calib)
        self.assertEqual(calib, calexp.getCalib())

        self.assertIsInstance(visitInfo, lsst.afw.image.VisitInfo)
        self.assertIsInstance(filt, lsst.afw.image.Filter)

        self.assertEqual(visitInfo.getExposureId(), calexp.getInfo().getVisitInfo().getExposureId())
        self.assertEqual(visitInfo.getExposureTime(), calexp.getInfo().getVisitInfo().getExposureTime())
        self.nanSafeAssertEqual(visitInfo.getDarkTime(), calexp.getInfo().getVisitInfo().getDarkTime())
        self.assertEqual(visitInfo.getDate(), calexp.getInfo().getVisitInfo().getDate())
        self.nanSafeAssertEqual(visitInfo.getUt1(), calexp.getInfo().getVisitInfo().getUt1())
        self.nanSafeAssertEqual(visitInfo.getEra(), calexp.getInfo().getVisitInfo().getEra())
        self.assertEqual(visitInfo.getBoresightRaDec(), calexp.getInfo().getVisitInfo().getBoresightRaDec())
        self.assertEqual(visitInfo.getBoresightAzAlt(), calexp.getInfo().getVisitInfo().getBoresightAzAlt())
        self.assertEqual(visitInfo.getBoresightAirmass(),
                         calexp.getInfo().getVisitInfo().getBoresightAirmass())
        self.nanSafeAssertEqual(visitInfo.getBoresightRotAngle(),
                                calexp.getInfo().getVisitInfo().getBoresightRotAngle())
        self.assertEqual(visitInfo.getRotType(), calexp.getInfo().getVisitInfo().getRotType())
        self.assertEqual(visitInfo.getObservatory(), calexp.getInfo().getVisitInfo().getObservatory())
        self.assertEqual(visitInfo.getWeather(), calexp.getInfo().getVisitInfo().getWeather())
        self.nanSafeAssertEqual(visitInfo.getLocalEra(), calexp.getInfo().getVisitInfo().getLocalEra())
        self.nanSafeAssertEqual(visitInfo.getBoresightHourAngle(),
                                calexp.getInfo().getVisitInfo().getBoresightHourAngle())


class MemoryTester(lsst.utils.tests.MemoryTestCase):
    pass


def setup_module(module):
    lsst.utils.tests.init()


if __name__ == "__main__":
    lsst.utils.tests.init()
    unittest.main()

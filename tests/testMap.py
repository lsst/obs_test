#!/usr/bin/env python

#
# LSST Data Management System
# Copyright 2008, 2009, 2010 LSST Corporation.
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

import math
import os
import unittest

import lsst.utils.tests
from lsst.utils import getPackageDir
# we only import TestMapper from lsst.obs.test, but use the namespace to hide it from pytest
import lsst.obs.test
from lsst.daf.base import DateTime
from lsst.obs.base import MakeRawVisitInfo
from lsst.daf.persistence import Butler
from lsst.afw.image import DecoratedImageU, ExposureU, RotType_SKY
from lsst.afw.coord import IcrsCoord, Coord
from lsst.afw.geom import degrees


class TestMapperTestCase(lsst.utils.tests.TestCase):
    """A test case for the test mapper."""

    def setUp(self):
        obsTestDir = getPackageDir('obs_test')
        self.input = os.path.join(obsTestDir, "data", "input")
        self.output = self.input
        self.mapper = lsst.obs.test.TestMapper(root=self.input)

    def tearDown(self):
        del self.mapper

    def testMapConfigData(self):
        dataId = dict(visit=1)
        loc = self.mapper.map_processCcd_config(dataId)
        self.assertEqual(loc.getPythonType(), "lsst.pipe.tasks.processCcd.ProcessCcdConfig")
        self.assertEqual(loc.getCppType(), "Config")
        self.assertEqual(loc.getStorageName(), "ConfigStorage")
        self.assertEqual(loc.getLocations(), [os.path.join(self.output,
                                                           "config", "processCcd.py")])
        for k, v in dataId.items():
            self.assertEqual(loc.getAdditionalData().get(k), v)

    def testMapMetadataData(self):
        dataId = dict(visit=1)
        loc = self.mapper.map_processCcd_metadata(dataId)
        self.assertEqual(loc.getPythonType(), "lsst.daf.base.PropertySet")
        self.assertEqual(loc.getCppType(), "PropertySet")
        self.assertEqual(loc.getStorageName(), "BoostStorage")
        self.assertEqual(loc.getLocations(), [os.path.join(self.output,
                                                           "processCcd_metadata", "v1_fg.boost")])
        for k, v in dataId.items():
            self.assertEqual(loc.getAdditionalData().get(k), v)

    def testKeys(self):
        self.assertEqual(set(self.mapper.keys()),
                         set(['filter', 'patch', 'skyTile', 'tract', 'visit', 'pixel_id']))

    def testGetDatasetTypes(self):
        someKeys = set(['raw', 'processCcd_config', 'processCcd_metadata'])
        self.assertTrue(set(self.mapper.getDatasetTypes()).issuperset(someKeys))

    def testGetKeys(self):
        self.assertEqual(set(self.mapper.getKeys("raw", "skyTile")),
                         set(["filter"]))
        self.assertEqual(set(self.mapper.getKeys("raw", "visit")),
                         set(["filter", "visit"]))

    def testGetDefaultLevel(self):
        self.assertEqual(self.mapper.getDefaultLevel(), "visit")

    def testMap(self):
        dataId = dict(visit=1)
        for loc in (
            self.mapper.map_raw(dataId),
            self.mapper.map("raw", dataId),
        ):
            self.assertEqual(loc.getPythonType(), "lsst.afw.image.DecoratedImageU")
            self.assertEqual(loc.getCppType(), "DecoratedImageU")
            self.assertEqual(loc.getStorageName(), "FitsStorage")
            locationList = loc.getLocations()
            self.assertEqual(len(locationList), 1)
            fileName = os.path.basename(locationList[0])
            self.assertEqual(fileName, "raw_v1_fg.fits.gz")
            for k, v in dataId.items():
                self.assertEqual(loc.getAdditionalData().get(k), v)

    def testQueryMetadata(self):
        """Test expansion of incomplete information
        """
        for visit, filt in ((1, "g"), (2, "g"), (3, "r")):
            tuples = self.mapper.queryMetadata("raw", ["visit", "filter"], dict(visit=visit))
            self.assertEqual(len(tuples), 1)
            self.assertEqual(tuples[0], (visit, filt))

        for filt, visitList in (
            ("g", (1, 2)),
            ("r", (3,)),
        ):
            tuples2 = self.mapper.queryMetadata("raw", ["visit", "filter"], dict(filter=filt))
            self.assertEqual(len(tuples2), len(visitList))
            for visit in visitList:
                self.assertIn((visit, filt), tuples2)

    def testCanStandardize(self):
        self.assertTrue(self.mapper.canStandardize("raw"))
        self.assertFalse(self.mapper.canStandardize("camera"))
        self.assertFalse(self.mapper.canStandardize("processCcd_config"))
        self.assertFalse(self.mapper.canStandardize("processCcd_metadata"))

    def testStandardizeRaw(self):
        pathToRaw = os.path.join(self.input, "raw", "raw_v1_fg.fits.gz")
        rawImage = DecoratedImageU(pathToRaw)
        dataId = dict(visit=1)
        stdImage = self.mapper.standardize("raw", rawImage, dataId)
        self.assertIsInstance(stdImage, ExposureU)
        visitInfo = stdImage.getInfo().getVisitInfo()

        exposureTime = 15.0
        darkTime = 15.0
        dateObs = DateTime(51195.2035520278, DateTime.MJD, DateTime.TAI)
        dateAvg = DateTime(dateObs.nsecs(DateTime.TAI) + int(0.5e9*exposureTime), DateTime.TAI)
        boresightRaDec = IcrsCoord(79.2452196867*degrees, -9.70229541541*degrees)
        boresightAzAlt = Coord(289.979375363*degrees, (90 - 42.0568785956)*degrees)
        boresightAirmass = 1.34682439137302
        boresightRotAngle = (90-248.022002123)*degrees
        rotType = RotType_SKY
        obs_longitude = -70.749417*degrees
        obs_latitude = -30.244633*degrees
        obs_elevation = 2663.0
        weath_airTemperature = 5.0
        weath_airPressure = MakeRawVisitInfo.pascalFromMmHg(520.0)

        visitInfo = stdImage.getInfo().getVisitInfo()
        self.assertAlmostEqual(visitInfo.getDate().get(), dateAvg.get())
        self.assertAlmostEqual(visitInfo.getExposureTime(), exposureTime)
        self.assertAlmostEqual(visitInfo.getDarkTime(), darkTime)
        self.assertCoordsNearlyEqual(visitInfo.getBoresightRaDec(), boresightRaDec)
        self.assertCoordsNearlyEqual(visitInfo.getBoresightAzAlt(), boresightAzAlt)
        self.assertAlmostEqual(visitInfo.getBoresightAirmass(), boresightAirmass)
        self.assertAnglesNearlyEqual(visitInfo.getBoresightRotAngle(), boresightRotAngle)
        self.assertEqual(visitInfo.getRotType(), rotType)
        observatory = visitInfo.getObservatory()
        self.assertAnglesNearlyEqual(observatory.getLongitude(), obs_longitude)
        self.assertAnglesNearlyEqual(observatory.getLatitude(), obs_latitude)
        self.assertAlmostEqual(observatory.getElevation(), obs_elevation)
        weather = visitInfo.getWeather()
        self.assertAlmostEqual(weather.getAirTemperature(), weath_airTemperature)
        self.assertAlmostEqual(weather.getAirPressure(), weath_airPressure)
        self.assertTrue(math.isnan(weather.getHumidity()))

    def testCameraFromButler(self):
        """Test that the butler can return the camera
        """
        butler = Butler(self.input)
        camera = butler.get("camera", immediate=True)
        self.assertEqual(camera.getName(), self.mapper.camera.getName())
        self.assertEqual(len(camera), len(self.mapper.camera))
        self.assertEqual(len(camera[0]), len(self.mapper.camera[0]))

    def testExposureIdInfo(self):
        butler = Butler(self.input)
        expIdBits = self.mapper.bypass_ccdExposureId_bits(  # args are ignored
            datasetType=None,
            pythonType=int,
            location=None,
            dataId=dict(),
        )
        for visit in (1, 2, 3):
            dataId = dict(visit=visit)
            expIdInfo = butler.get("expIdInfo", dataId=dataId)
            self.assertEqual(expIdInfo.expId, visit)
            self.assertEqual(expIdInfo.expBits, expIdBits)
            self.assertEqual(expIdInfo.maxBits, 64)
            self.assertEqual(expIdInfo.unusedBits, expIdInfo.maxBits-expIdBits)

    def testValidate(self):
        for dataId in [
            dict(visit=1),
            dict(visit=25),
        ]:
            self.assertEqual(self.mapper.validate(dataId), dataId)
        for dataId in [
            dict(visit="not-an-int"),  # visit must be an integer
        ]:
            self.assertRaises(Exception, self.mapper.validate, dataId)


class MemoryTester(lsst.utils.tests.MemoryTestCase):
    pass


def setup_module(module):
    lsst.utils.tests.init()


if __name__ == "__main__":
    lsst.utils.tests.init()
    unittest.main()

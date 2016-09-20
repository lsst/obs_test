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

import filecmp
import os
import pickle
import shutil
import unittest

import lsst.afw.image as afwImage
import lsst.daf.persistence as dafPersist
import lsst.obs.test
import lsst.utils.tests
from lsst.utils import getPackageDir



class TestCompositeTestCase(unittest.TestCase):
    """A test case for composite object i/o."""

    def setUp(self):
        obsTestDir = getPackageDir('obs_test')
        self.input = os.path.join(obsTestDir, 'data', 'input')
        self.output = os.path.join(obsTestDir, 'tests', 'outputs')
        self.compositeOutput = os.path.join(self.output, 'composite')
        self.nonCompositeOutput = os.path.join(self.output, 'noncomposite')

    def tearDown(self):
        if os.path.exists(self.output):
            shutil.rmtree(self.output)

    def test(self):
        """Verify that a composite can be loaded and that its components are the same as when the type1
        components are loaded individually (verifies correct lookup in this case).
        Also verify that when the individual components are put and when the composite is put (which
        disassembles into individual components) that the objects that are written are the same.
        """
        outputs = (dafPersist.RepositoryArgs(root=self.compositeOutput, tags='composite'),
                   dafPersist.RepositoryArgs(root=self.nonCompositeOutput, tags='noncomposite'))
        butler = dafPersist.Butler(inputs=dafPersist.RepositoryArgs(root=self.input,
            mapper='lsst.obs.test.testMapper.TestMapper'), outputs=outputs)
        rawAndFlat = butler.get('rawAndFlat', dataId={'visit':1, 'filter':'g'})
        raw = butler.get('raw', dataId={'visit':1, 'filter':'g'})
        flat = butler.get('flat', dataId={'filter':'g'})

        # verify that the flat & raw loaded by the composite object are correct by loading the non-composite
        # flat & raw, serializing (via pickle) and using filecmp to check that they are the same.
        flatPath = os.path.join(self.output, 'pickleFlat')
        compositeFlatPath = os.path.join(self.output, 'pickleCompositeFlat')
        with open(flatPath, 'wb') as f:
            pickle.dump(flat, f)
        with open(compositeFlatPath, 'wb') as f:
            pickle.dump(rawAndFlat.flat, f)
        self.assertTrue(filecmp.cmp(flatPath, compositeFlatPath))

        rawPath = os.path.join(self.output, 'pickleRaw')
        compositeRawPath = os.path.join(self.output, 'pickleCompositeRaw')
        with open(rawPath, 'wb') as f:
            pickle.dump(raw, f)
        with open(compositeRawPath, 'wb') as f:
            pickle.dump(rawAndFlat.raw, f)
        self.assertTrue(filecmp.cmp(rawPath, compositeRawPath))

        butler.put(rawAndFlat, 'rawAndFlat', dataId=dafPersist.DataId({'visit':1, 'filter':'g'}, tags='composite'))
        butler.put(raw, 'raw', dataId=dafPersist.DataId({'visit':1, 'filter':'g'}, tags='noncomposite'))
        butler.put(raw, 'flat', dataId=dafPersist.DataId({'filter':'g'}, tags='noncomposite'))

        self.assertTrue(filecmp.cmp(os.path.join(self.compositeOutput, 'raw', 'raw_v1_fg.fits.gz'),
                                    os.path.join(self.nonCompositeOutput, 'raw', 'raw_v1_fg.fits.gz')))

        self.assertTrue(filecmp.cmp(os.path.join(self.compositeOutput, 'flat', 'flat_fg.fits.gz'),
                                    os.path.join(self.nonCompositeOutput, 'flat', 'flat_fg.fits.gz')))




class MemoryTester(lsst.utils.tests.MemoryTestCase):
    pass


def setup_module(module):
    lsst.utils.tests.init()


if __name__ == "__main__":
    lsst.utils.tests.init()
    unittest.main()

# This file is part of obs_test.
#
# Developed for the LSST Data Management System.
# This product includes software developed by the LSST Project
# (http://www.lsst.org).
# See the COPYRIGHT file at the top-level directory of this distribution
# for details of code ownership.
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
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

import filecmp
import os
import pickle
import shutil
import tempfile
import unittest


from lsst.afw.image.testUtils import makeRampImage
import lsst.geom as geom
import lsst.afw.image as afwImage
import lsst.daf.persistence as dafPersist
import lsst.obs.test
import lsst.utils.tests
from lsst.utils import getPackageDir

ROOT = getPackageDir('obs_test')


def makeRampDecoratedImage(bbox, start, **metadataDict):
    """Make a DecoratedImageU that is a ramp."""
    rampArr = makeRampImage(bbox=bbox, start=start, imageClass=afwImage.ImageU).getArray()
    decoratedImage = afwImage.DecoratedImageU(bbox)
    imarr = decoratedImage.getImage().getArray()
    imarr[:] = rampArr
    md = decoratedImage.getMetadata()
    for (key, val) in metadataDict.items():
        md.set(key, val)
    return decoratedImage


class TestCompositeTestCase(lsst.utils.tests.TestCase):
    """A test case for composite object I/0."""
    def setUp(self):
        self.testDir = tempfile.mkdtemp(dir=os.path.join(ROOT, 'tests'), prefix=type(self).__name__+'-')
        self.input = os.path.join(ROOT, 'data', 'input')
        self.output = os.path.join(self.testDir, 'tests', 'outputs')
        self.compositeOutput = os.path.join(self.output, 'composite')
        self.nonCompositeOutput = os.path.join(self.output, 'noncomposite')
        self.dataId = {'visit': 1, 'filter': 'g'}

    def tearDown(self):
        if os.path.exists(self.testDir):
            shutil.rmtree(self.testDir)

    def testGet(self):
        """Verify get of individual components vs a composite.
        """
        butler = dafPersist.Butler(
            inputs=dafPersist.RepositoryArgs(root=self.input, mapper='lsst.obs.test.testMapper.TestMapper'),
        )
        rawAndFlat = butler.get('rawAndFlat', dataId=self.dataId)
        raw = butler.get('raw', dataId=self.dataId)
        flat = butler.get('flat', dataId=self.dataId)

        # Exposures (which is how these are retrieved) cannot be directly compared,
        # including associated objects and metadata, so pickle them and cmpare the pickles
        self.assertEqual(pickle.dumps(raw), pickle.dumps(rawAndFlat.raw))
        self.assertEqual(pickle.dumps(flat), pickle.dumps(rawAndFlat.flat))

    def testPut(self):
        """Compare put of individual components vs a composite.

        Notes
        -----
        Raw and calibration frames do not round trip (they are saved as
        DecoratedImageU and read in as ExposureU), so create the raw
        and flat manually.
        """
        outputs = (dafPersist.RepositoryArgs(root=self.compositeOutput, tags='composite'),
                   dafPersist.RepositoryArgs(root=self.nonCompositeOutput, tags='noncomposite'))
        butler = dafPersist.Butler(
            inputs=dafPersist.RepositoryArgs(root=self.input, mapper='lsst.obs.test.testMapper.TestMapper'),
            outputs=outputs)
        bbox = geom.Box2I(geom.Point2I(0, 0), geom.Point2I(10, 10))
        raw = makeRampDecoratedImage(bbox=bbox, start=100, raw1=5, raw2="hello")
        flat = makeRampDecoratedImage(bbox=bbox, start=-55, flat1="me", flat2=47)

        # a hack-ish way of creating a rawAndFlat object; read in the data, then replace it with our own
        rawAndFlat = butler.get('rawAndFlat', dataId=self.dataId)
        rawAndFlat.raw = raw
        rawAndFlat.flat = flat

        butler.put(rawAndFlat, 'rawAndFlat', dataId=self.dataId, tags='composite')
        butler.put(raw, 'raw', dataId=self.dataId, tags='noncomposite')
        butler.put(raw, 'flat', dataId=self.dataId, tags='noncomposite')

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

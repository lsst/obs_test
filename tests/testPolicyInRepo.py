#!/usr/bin/env python

#
# LSST Data Management System
# Copyright 2015 LSST Corporation.
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

import os
import unittest

import lsst.daf.persistence as dafPersist
# we only import lsst.obs.test.TestMapper from lsst.obs.test, but use the namespace to hide it from pytest
import lsst.obs.test
import lsst.utils.tests
from lsst.utils import getPackageDir
import shutil


class PolicyTestCase(unittest.TestCase):

    """Tests related to the use of the policy file in Butler/butlerUtils."""
    obsTestDir = getPackageDir("obs_test")
    testDir = os.path.join(obsTestDir, 'tests', 'PolicyTestCase')
    repoARoot = os.path.join(testDir, 'a')

    def setUp(self):
        self.tearDown()

    def tearDown(self):
        if os.path.exists(self.testDir):
            shutil.rmtree(self.testDir)

    def testInRepoPolicyOverrides(self):
        """Verify that the template value specified in the policy file in the repository
        overrides the template value set in the policy file in the package.
        Checks that child repositories do not get the policy from the parent (per specification).
        Checks that values not specified in the local _policy file are set with those of the package's
        _policy file.
        """
        policyOverride = {'exposures': {'raw': {'template': "raw/v%(visit)d_f%(filter)s.fits.gz"}}}
        policyPath = os.path.join(self.obsTestDir, 'policy', 'testMapper.yaml')
        policy = dafPersist.Policy(policyPath)
        postISRCCDtemplate = policy.get('exposures.postISRCCD.template')

        butler = dafPersist.Butler(outputs={'root': self.repoARoot,
                                            'mapper': lsst.obs.test.TestMapper,
                                            'policy': policyOverride})

        # check that the declared policy got used in the mapper
        mapper = butler._repos.outputs()[0].repo._mapper
        self.assertEqual(mapper.mappings['raw'].template, "raw/v%(visit)d_f%(filter)s.fits.gz")
        # Run a simple test case to verify that although the package's policy was overloaded with some
        # values, other values specified in the policy file in the package are loaded.
        self.assertEqual(postISRCCDtemplate, mapper.mappings['postISRCCD'].template)
        del butler
        del mapper

        repoBRoot = os.path.join(self.testDir, 'b')
        butler = dafPersist.Butler(inputs=self.repoARoot, outputs=repoBRoot)
        # check that the reloaded policy got used in the mapper for repo A
        mapper = butler._repos.inputs()[0].repo._mapper
        self.assertEqual(mapper.mappings['raw'].template, "raw/v%(visit)d_f%(filter)s.fits.gz")
        # again, test that another value is loaded from package policy file is loaded correctly.
        self.assertEqual(postISRCCDtemplate, mapper.mappings['postISRCCD'].template)
        # also check that repo B does not get the in-repo policy from A
        mapper = butler._repos.outputs()[0].repo._mapper
        self.assertNotEqual(mapper.mappings['raw'].template, "raw/v%(visit)d_f%(filter)s.fits.gz")
        # and again, test that another value is loaded from package policy file is loaded correctly.
        self.assertEqual(postISRCCDtemplate, mapper.mappings['postISRCCD'].template)


class MemoryTester(lsst.utils.tests.MemoryTestCase):
    pass


def setup_module(module):
    lsst.utils.tests.init()


if __name__ == "__main__":
    lsst.utils.tests.init()
    unittest.main()

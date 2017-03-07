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

import lsst.pex.policy
# we only import lsst.obs.test.TestMapper from lsst.obs.test, but use the namespace to hide it from pytest
import lsst.obs.test
import lsst.utils.tests
from lsst.utils import getPackageDir


class PolicyTestCase(unittest.TestCase):

    """Tests related to the use of the policy file in Butler/butlerUtils."""

    def testInRepoPolicyOverrides(self):
        """Verify that the template value specified in the policy file in the repository
        overrides the template value set in the policy file in the package.
        Checks the _parent symlink chain works.
        Checks that values not specified in the local _policy file are set with those of the package's
        _policy file.
        """
        obsTestDir = getPackageDir("obs_test")
        obsTestRepoDir = os.path.join(obsTestDir, "data")
        testData = (
            (os.path.join(obsTestRepoDir, 'policyInRepo1/a'),
                os.path.join(obsTestRepoDir, 'policyInRepo1', 'a', '_parent', '_policy.paf')),
            (os.path.join(obsTestRepoDir, 'policyInRepo2/a'),
                os.path.join(obsTestRepoDir, 'policyInRepo2', 'a', '_parent', '_parent', '_policy.paf'))
        )

        for mapperRoot, actualPolicyPath in testData:
            mapper = lsst.obs.test.TestMapper(root=mapperRoot)
            repoPolicy = lsst.pex.policy.Policy.createPolicy(actualPolicyPath)
            template = repoPolicy.get('exposures.raw.template')
            mapperTemplate = mapper.mappings['raw'].template
            self.assertEqual(template, mapperTemplate)

            # Run a simple test case to verify that although the package's policy was overloaded with some
            # values, other values specified in the policy file in the package are loaded.
            policyPath = os.path.join(obsTestDir, 'policy', 'testMapper.paf')
            policy = lsst.pex.policy.Policy.createPolicy(policyPath)
            template = policy.get('exposures.postISRCCD.template')
            mapperTemplate = mapper.mappings['postISRCCD'].template
            self.assertEqual(template, mapperTemplate)


class MemoryTester(lsst.utils.tests.MemoryTestCase):
    pass


def setup_module(module):
    lsst.utils.tests.init()


if __name__ == "__main__":
    lsst.utils.tests.init()
    unittest.main()

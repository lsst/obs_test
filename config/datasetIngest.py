# Config override for lsst.ap.verify.DatasetIngestTask
import os.path

from lsst.utils import getPackageDir
obsConfigDir = os.path.join(getPackageDir('obs_test'), 'config')

config.textDefectPath = os.path.join(getPackageDir('obs_test_data'), 'test', 'defects')
config.dataIngester.load(os.path.join(obsConfigDir, 'ingest.py'))
config.calibIngester.load(os.path.join(obsConfigDir, 'ingestCalibs.py'))

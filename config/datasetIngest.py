# Config override for lsst.ap.verify.DatasetIngestTask
import os.path

from lsst.utils import getPackageDir
obsConfigDir = os.path.join(getPackageDir('obs_test'), 'config')

config.dataIngester.load(os.path.join(obsConfigDir, 'ingest.py'))
config.calibIngester.load(os.path.join(obsConfigDir, 'ingestCalibs.py'))

# obs_test data repository

This ReadMe describes the obs_test data in the "input" repository.

The data are derived from lsstSim and astrometry_net data that are no longer available.

The obs_test camera is described in doc/main.dox, but I will remind you that the obs_test camera
has a single CCD "sensor 0" that corresponds to a subregion of LSST CCD R2,2 S0,0.

The obs_test raw data uses data E000 R22 S00 of the following lsstSim visits:

| obs_test          | lsstSim       |
|-------------------|---------------|
| visit=1 filter=g  | v890104911-fg |
| visit=2 filter=g  | v890106021-fg |
| visit=3 filter=r  | v890880321-fr |

## How to make the data

To create the repository database, from the obs_test directory
(use bin/ to disambiguate from other obs_ packages that may be setup):

    setup -r .
    bin/genInputRegistry.py data/input


To make the obs_test bias image, from the obs_test directory:

    setup -r .
    data/utils/assembleLsstChannels.py <lsstSim data location>/bias/v0/R22/S00 \
        OBSTYPE=bias DATE-OBS=1999-01-17T05:22:00
    mv image.fits bias.fits

To make obs_test flat images, from the obs_test directory:

    setup -r .
    data/utils/assembleLsstChannels.py <lsstSim data location>/flat/v2-fg/R22/S00 \
        OBSTYPE=flat DATE-OBS=1999-01-17T05:22:00
    mv image.fits flat_fg.fits
    data/utils/assembleLsstChannels.py <lsstSim data location>/flat/v2-fr/R22/S00 \
        OBSTYPE=flat DATE-OBS=1999-01-17T05:22:00
    mv image.fits flat_fr.fits

To make obs_test raw images, from the obs_test directory:

    setup -r .
    data/utils/assembleLsstRaw.py <lsstSim data location>/raw/v890104911-fg/E000/R22/S00
    mv raw.fits raw_v1_fg.fits
    data/utils/assembleLsstRaw.py <lsstSim data location>/raw/v890106021-fg/E000/R22/S00
    mv raw.fits raw_v2_fg.fits
    data/utils/assembleLsstRaw.py <lsstSim data location>/raw/v890880321-fr/E000/R22/S00
    mv raw.fits raw_v3_fr.fits

To make an obs_test defects file from the bias frame generated above, from the obs_test directory:

    setup -r .
    data/utils/defectsFromBias.py data/input/bias/bias.fits.gz
    mv defects_c0.dat $OBS_TEST_DATA_DIR/test/defects/0/19700101T000000.dat

## Hints for using the data

To run processCcd.py (the r band image requires increasing nCrPixelMax to be successfully processed):

    setup pipe_tasks
    processCcd.py data/input --id filter=r^g --config calibrate.repair.cosmicray.nCrPixelMax=20000 --output=output

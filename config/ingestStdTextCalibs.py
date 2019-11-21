# Config override for lsst.pipe.tasks.IngestCalibsTask
config.parse.translation = {'calibDate': 'CALIBDATE',
                            'filter': 'FILTER',
                            'ccd': 'DETECTOR',
                           }
config.register.columns = {'calibDate': 'text',
                           'validStart': 'text',
                           'validEnd': 'text',
                           'filter': 'text',
                           'ccd': 'int',
                           }
config.register.visit = ['calibDate']
config.register.validityUntilSuperseded = ['defects',]
config.register.unique = ['calibDate']

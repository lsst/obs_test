# Config override for lsst.pipe.tasks.IngestCalibsTask
config.parse.translation = {'filter': 'FILTER',
                            }
config.parse.translators = {'calibDate': 'translate_date',
                            }
config.register.columns = {'filter': 'text',
                           'calibDate': 'text',
                           'validStart': 'text',
                           'validEnd': 'text',
                           }
config.register.detector = ['filter']
config.register.visit = ['calibDate']
config.register.tables = ['bias', 'flat']  # defects are hardcoded into mapper; cannot be ingested
config.register.validityUntilSuperseded = config.register.tables
config.register.unique = ['filter', 'calibDate']

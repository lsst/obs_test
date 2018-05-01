# Config override for lsst.pipe.tasks.IngestTask
config.parse.translation = {'visit': 'OBSID',
                            'expTime': 'EXPTIME',
                            }
config.parse.translators = {'filter': 'translate_filter',
                            }
config.register.columns = {'visit': 'int',
                           'filter': 'text',
                           'expTime': 'double',
                           }
config.register.visit = ['visit', 'filter']
config.register.unique = ['visit']

# -*- coding: utf-8 -*-

import sys
import logging

LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'loggers': {
        'vksocial': {
            'level': 'INFO',
            'handlers': ['vksocial-stdout'],
            'propagate': False,
            },
        },
    'handlers': {
        'vksocial-stdout': {
            'class': 'logging.StreamHandler',
            'stream': sys.stdout,
            'formatter': 'vksocial-verbose',
        },
    },
    'formatters': {
        'vksocial-verbose': {
            'format': '%(asctime)s %(name) -5s %(module)s:%(lineno)d %(levelname)s: %(message)s',
        },
    },
}

logging.config.dictConfig(LOGGING_CONFIG)


logger = logging.getLogger('vksocial')

vk_logger = logging.getLogger('vk')


logger.setLevel('DEBUG')
#vk_logger.setLevel('DEBUG')
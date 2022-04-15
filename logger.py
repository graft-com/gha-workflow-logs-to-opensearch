import sys
import logging.config
# We don't want to lose logs that occur before the dal being initialized
logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))
logging.getLogger().setLevel(logging.INFO)

LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'default': {
            'level': "DEBUG",
            'formatter': 'jsonFormatter',
            'class': 'logging.StreamHandler'
        },
        'opensearch': {
            'level': "DEBUG",
            'formatter': 'jsonFormatter',
            'class': 'opensearch_handler.SearchHandler'
        }
    },
    'loggers': {
        '': {  # root logger
            'handlers': ['default'],
            'level': "DEBUG",
            'propagate': True
        },
        'opensearch': { 
            'handlers': ['opensearch'],
            'level': "DEBUG",
            'propagate': False
        }
    },
    'formatters': {
        'jsonFormatter': {
            '()': 'json_formatter.JsonFormatter',
        }
    }
}

logging.config.dictConfig(LOGGING_CONFIG)

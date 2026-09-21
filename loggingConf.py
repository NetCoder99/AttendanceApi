import constants

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "detailed": {
            "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "INFO",
            "formatter": "detailed",
            "stream": "ext://sys.stdout",
        },
        "basicFileHandler": {
            "class": "logging.FileHandler",
            "level": "DEBUG",
            "formatter": "detailed",
            "filename": f'{constants.applicationName}.log',
            "mode": "a",
            "encoding": "utf-8",
        },
        "rotatingFileHandler": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "DEBUG",
            "formatter": "detailed",
            "filename": f'{constants.applicationName}.log',
            "maxBytes": 10485760,
            "backupCount": 5,
            "encoding": "utf-8",
        },
    },
    "root": {
        "level": "DEBUG",
        "handlers": ["console", "rotatingFileHandler"],
    },
}
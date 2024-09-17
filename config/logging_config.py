import logging
import os
from config.config import cfg  # Import your config
from core.app_data_manager import app_data_manager
from logging.handlers import RotatingFileHandler

# Define the directory and log file path
log_file_path = app_data_manager.get_file_path('dragonborn_leveler.log')

def get_logging_level(log_level_enum):
    return getattr(logging, log_level_enum.value, logging.INFO)

# Configure the logging with RotatingFileHandler
logging_config = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        },
    },
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': log_file_path,
            'formatter': 'standard',
            'maxBytes': 5 * 1024 * 1024,  # 5 MB max size
            'backupCount': 3,  # Keep 3 backup logs
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'standard',
        },
    },
    'loggers': {
        '': {  # root logger
            'handlers': ['file', 'console'],
            'level': 'DEBUG',
            'propagate': True,
        },
    }
}

def setup_logging():
    """
    Sets up logging configuration using the defined logging configuration.
    """
    import logging.config
    # Get the desired logging level from the config
    log_level = get_logging_level(cfg.general_log_level.value)

    # Set the level for both file and console handlers dynamically
    logging_config['handlers']['file']['level'] = log_level
    logging_config['handlers']['console']['level'] = log_level

    # Set the level for the root logger
    logging_config['loggers']['']['level'] = log_level

    # Apply the logging configuration
    logging.config.dictConfig(logging_config)

    # Optional: Log the current logging level for confirmation
    logging.getLogger().info(f"Logging level set to {cfg.general_log_level.value}")
    logging.getLogger("matplotlib").setLevel(logging.WARNING)
    logging.getLogger("pytesseract").setLevel(logging.WARNING)

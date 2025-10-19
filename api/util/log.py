import logging
import yaml

global LOG_CONFIG
LOG_CONFIG = None


def logger(name: str, level: str = "INFO") -> logging.Logger:
    logger = logging.getLogger(name) 
    logger.setLevel(level.upper())

    # Define ANSI escape sequences for colors
    COLORS = {
        'CRITICAL': '\033[91m',  # Red
        'ERROR': '\033[91m',     # Red
        'WARNING': '\033[93m',   # Yellow
        'INFO': '\033[92m',      # Green
        'DEBUG': '\033[94m',     # Blue
        'RESET': '\033[0m'       # Reset to default color
    }

    # Set up the logging configuration with color formatting
    class ColorFormatter(logging.Formatter):
        def format(self, record):
            levelname = record.levelname
            message = super().format(record)
            color = COLORS.get(levelname, COLORS['RESET'])
            name = f"{color}[{logger.name}]{COLORS['RESET']}:"
            pre = f"{color}{levelname}{COLORS['RESET']}:"
            return f"{pre:17}{name:20}{message}"

    # Add color formatter to the loggers
    formatter = ColorFormatter()
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    logger.handlers.clear() 
    logger.addHandler(handler)

    #logger.log(logger.getEffectiveLevel(), f"LOG LEVEL: {logging.getLevelName(logger.getEffectiveLevel())}")

    return logger
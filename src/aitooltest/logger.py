import sys
import logging

COLORS = {
    'DEBUG': '\033[94m',     # Blue
    'INFO': '\033[92m',      # Green
    'WARNING': '\033[93m',   # Yellow
    'ERROR': '\033[91m',     # Red
    'CRITICAL': '\033[95m',  # Magenta
    'RESET': '\033[0m',      # Reset color
}


class ColoredFormatter(logging.Formatter):
    """custom formatter to add colors based on a log level"""

    def format(self, record: logging.LogRecord) -> str:
        log_color = COLORS.get(record.levelname, COLORS['RESET'])
        reset = COLORS.get('RESET')

        log_fmt = f"{log_color}[%(asctime)s] [%(levelname)s] %(name)s: %(message)s{reset}"
        formatter = logging.Formatter(log_fmt, datefmt="%H:%M:%S")

        return formatter.format(record)


def initialize_logging(level=logging.DEBUG):
    """Initialize a singleton global logger"""
    if getattr(initialize_logging, "_initialized", False):
        return logging.getLogger()

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # Create a console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(ColoredFormatter())

    if root_logger.hasHandlers(): root_logger.handlers.clear()

    root_logger.addHandler(console_handler)
    initialize_logging._initialized = True

    return root_logger

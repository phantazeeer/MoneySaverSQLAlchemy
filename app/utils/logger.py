import logging
from logging.handlers import RotatingFileHandler

import click

from app.config import settings


class ColoredFormatter(logging.Formatter):
    _levelcolors = {
        "DEBUG": "cyan",
        "INFO": "green",
        "WARNING": "yellow",
        "ERROR": "red",
        "CRITICAL": "bright_red",
    }

    def format(self, record):
        msg = super().format(record)
        if record.levelname in self._levelcolors.keys():
            colored_level = click.style(record.levelname, fg=self._levelcolors[record.levelname]) + ":"
            msg = msg.replace(record.levelname, colored_level, 1)

        return msg


def get_logger(module_name: str) -> logging.Logger:
    logger = logging.getLogger(module_name)
    logger.setLevel(settings.LOG_LEVEL)
    console_handler = logging.StreamHandler()
    console_formatter = ColoredFormatter(fmt="%(asctime)s - %(levelname)-8s - %(module)20s - %(message)s", style="%")
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    logging_in_file = settings.LOG_FILE

    if logging_in_file:
        file_handler = RotatingFileHandler(
            filename=logging_in_file,
            encoding="utf-8",
            mode="a",
            maxBytes=1024 * 1024 * 10,
            backupCount=3,
        )
        logger.addHandler(file_handler)

    return logger

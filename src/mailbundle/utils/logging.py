# -*- encoding: utf-8 -*-
import logging
import sys


def setup_log(debug: bool) -> None:
    """
    This function configures the log appropriately for the whole application
    """
    if debug:
        level = logging.DEBUG
    else:
        level = logging.INFO

    log = logging.getLogger("main")
    h = logging.StreamHandler(sys.stdout)
    h.setLevel(level)
    f = get_formatter()
    h.setFormatter(f)
    log.addHandler(h)
    log.setLevel(level)


def get_formatter() -> logging.Formatter:
    """
    This function probes if the proces is in a TTY and returns the appropriate formatter
    """
    if sys.stdout.isatty():
        return ConsoleFormatter()

    return NonTTYFormatter()


class ConsoleFormatter(logging.Formatter):
    grey = "\x1b[38;20m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    _format = "%(levelname)s: %(message)s"
    _dbg = "%(levelname)s: %(message)s (%(filename)s:%(lineno)d)"
    _trace = "TRACE: %(message)s (%(filename)s:%(lineno)d)"

    FORMATTERS = {
        0: logging.Formatter(fmt=f"{grey}{_trace}{reset}"),
        logging.DEBUG: logging.Formatter(fmt=f"{grey}{_dbg}{reset}"),
        logging.INFO: logging.Formatter(fmt=f"{grey}{_format}{reset}"),
        logging.WARNING: logging.Formatter(fmt=f"{yellow}{_format}{reset}"),
        logging.ERROR: logging.Formatter(fmt=f"{red}{_format}{reset}"),
        logging.CRITICAL: logging.Formatter(fmt=f"{bold_red}{_format}{reset}"),
    }

    def format(self, record):
        if record.levelno >= logging.CRITICAL:
            formatter = self.FORMATTERS[logging.CRITICAL]
        elif record.levelno >= logging.ERROR:
            formatter = self.FORMATTERS[logging.ERROR]
        elif record.levelno >= logging.WARNING:
            formatter = self.FORMATTERS[logging.WARNING]
        elif record.levelno >= logging.INFO:
            formatter = self.FORMATTERS[logging.INFO]
        elif record.levelno >= logging.DEBUG:
            formatter = self.FORMATTERS[logging.DEBUG]
        else:
            formatter = self.FORMATTERS[0]

        return formatter.format(record)


class NonTTYFormatter(logging.Formatter):
    _format = logging.Formatter(fmt="%(levelname)s: %(message)s")
    _dbg = logging.Formatter(fmt="%(levelname)s: %(message)s (%(filename)s:%(lineno)d)")

    def format(self, record):
        if record.levelno <= logging.DEBUG:
            return self._dbg.format(record)

        return self._format.format(record)

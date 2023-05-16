import logging


def setup_logger(
    name: str = "default",
    level: int = logging.INFO,
):
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Create console handler with a specific log level
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)

    # Create a formatter and add it to the handler
    formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - '
        '%(filename)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S')
    ch.setFormatter(formatter)

    # Add the handler to the logger
    logger.addHandler(ch)
    return logger

import json
import logging
import logging.config
import os

import bot

logger = logging.getLogger(__name__)


def setup_logging(path):
    """Setup logging configuration from a json file."""
    global logger
    with open(path) as f:
        config = json.load(f)
    
    logging.config.dictConfig(config)
    logger.info(f'Logger correctly initialized from {path}')


def main():
    setup_logging('logging.json')

    token = os.getenv('SHRTURL_TOKEN')
    if token is None:
        raise Exception("Environment variable TOKEN doesn't exist")

    bot.setup(token, 'data.dat')
    bot.start()


if __name__ == '__main__':
    main()

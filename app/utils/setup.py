import logging
from config.database import get_db
from utils.init_db import init_db


def setup():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    logger = logging.getLogger(__name__)
    init_db()
    return logger, next(get_db())
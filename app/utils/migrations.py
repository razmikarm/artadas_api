import logging
from alembic import command
from alembic.config import Config


def apply_migrations():
    logging.basicConfig(level=logging.INFO)
    alembic_logger = logging.getLogger("alembic")
    alembic_logger.setLevel(logging.INFO)

    # Path to your Alembic config file
    alembic_cfg = Config("alembic.ini")
    # Run the migrations
    command.upgrade(alembic_cfg, "head")

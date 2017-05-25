"""
gets the info about the database, might change soon
"""
import os
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()  # pylint: disable=invalid-name


def get_engine_url():
    """Get url to use for sqlalchemy.
    """
    return "postgresql://%s:%s@%s/%s" % (
        os.getenv("FALCON_DB_USER", "DB_USER"),
        os.getenv("FALCON_DB_PASSWORD", "DB_PASSWORD"),
        os.getenv("FALCON_DB_HOST", "DB_HOST"),
        os.getenv("FALCON_DB_NAME", "DB_NAME"),
    )

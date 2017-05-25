"""Database common utils."""
import os
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy import create_engine


def get_engine_url():
    """Get url to use for sqlalchemy."""
    return "postgresql://%s:%s@%s/%s" % (
        os.getenv("FALCON_DB_USER", "DB_USER"),
        os.getenv("FALCON_DB_PASSWORD", "DB_PASSWORD"),
        os.getenv("FALCON_DB_HOST", "DB_HOST"),
        os.getenv("FALCON_DB_NAME", "DB_NAME"),
    )

# Base class for SQLAlchemy
Base = declarative_base()  # pylint: disable=invalid-name

# create session binded to engine
engine = create_engine(get_engine_url())  # pylint: disable=invalid-name
session_factory = sessionmaker(bind=engine)  # pylint: disable=invalid-name
Session = scoped_session(session_factory)  # pylint: disable=invalid-name

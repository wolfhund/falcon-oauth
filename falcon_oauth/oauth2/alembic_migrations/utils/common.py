"""Common routines used by other files in the project.
"""
import os


def get_engine_url():
    """Get url to use for sqlalchemy.
    """
    return "postgresql://%s:%s@%s/%s" % (
        os.getenv("FALCON_DB_USER", "DB_USER"),
        os.getenv("FALCON_DB_PASSWORD", "DB_PASSWORD"),
        os.getenv("FALCON_DB_HOST", "DB_HOST"),
        os.getenv("FALCON_DB_NAME", "DB_NAME"),
    )

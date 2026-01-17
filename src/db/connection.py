import pyodbc
from tkinter import messagebox
import logging

from src.config import config

class DatabaseConnectionError(Exception):
    """Custom exception for database connection failures."""
    pass

def get_connection():
    """
    Creates and returns a new database connection using SQL Authentication.
    Connection parameters are loaded from config.ini.
    """
    try:
        db = config['database']

        # Check that all required keys are present
        required_keys = ['driver', 'server', 'database', 'username', 'password']
        missing_keys = [key for key in required_keys if key not in db or not db[key].strip()]
        if missing_keys:
            raise DatabaseConnectionError(
                f"Missing required configuration in config.ini: {', '.join(missing_keys)}"
            )

        conn_str = (
            f"DRIVER={{{db['driver']}}};"
            f"SERVER={db['server']};"
            f"DATABASE={db['database']};"
            f"UID={db['username']};"
            f"PWD={db['password']};"
            f"Encrypt={db.get('encrypt', 'no')};"
            f"TrustServerCertificate={db.get('trust_server_certificate', 'yes')};"
        )

        con = pyodbc.connect(conn_str)
        con.autocommit = False
        return con

    except DatabaseConnectionError:
        raise
    except pyodbc.OperationalError as e:
        logging.error("Database connection failed", exc_info=True)
        raise DatabaseConnectionError(
            "Failed to connect to the database. Check the server name, login credentials, and SQL Server availability."
        ) from e
    except pyodbc.Error as e:
        logging.error("Unexpected database error", exc_info=True)
        raise DatabaseConnectionError(
            "An unexpected database error occurred."
        ) from e


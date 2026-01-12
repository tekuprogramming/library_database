import pyodbc
from tkinter import messagebox
import logging

from src.config import config

def get_connection():
    """
    Creates and returns a new database connection using pyodbc.

    Connection parameters are loaded from the application configuration
    (config.ini). The function uses Windows Authentication
    (Trusted_Connection) and supports encrypted connections.

    :return: pyodbc.Connection object
    :raises: Exception if the connection cannot be established
    """
    try:
        con = pyodbc.connect(
            f"DRIVER={{{config['database']['driver']}}};"
            f"SERVER={config['database']['server']};"
            f"DATABASE={config['database']['database']};"
            f"Trusted_Connection={config['database']['trusted_connection']};"
            f"Encrypt={config['database']['encrypt']};"
            f"TrustServerCertificate={config['database']['trust_server_certificate']};"
        )
        # Disable autocommit to allow explicit transaction control
        con.autocommit = False
        return con
    except Exception as e:
        # Disable autocommit to allow explicit transaction control
        logging.error(e)
        messagebox.showerror("Connection error", str(e))
        raise

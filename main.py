import pyodbc
import tkinter
from tkinter import ttk, messagebox, filedialog
import configparser
import logging
import csv, json, xml.etree.ElementTree as ET

# config and logging
config = configparser.ConfigParser()
config.read("config.ini")
logging.basicConfig(
    level = getattr(logging, config.get("app", "log_level", fallback="INFO")),
    format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

# connection to SQL
def getcon():
    driver = config.get("database", "driver")
    server = config.get("database", "server")
    database = config.get("database", "database")
    trusted = config.get("database", "trusted_connection")
    encrypt = config.get("database", "encrypt")
    trust_cert = config.get("database", "trust_server_certificate")
    try:
        con = pyodbc.connect(
            f"DRIVER={{{driver}}};"
            f"SERVER={server};"
            f"DATABASE={database};"
            f"Trusted_Connection={trusted};"
            f"Encrypt={encrypt};"
            f"TrustServerCertificate={trust_cert};"
        )
        con.autocommit = False
        return con
    except Exception as e:
        logging.error(e)
        messagebox.showerror("Connection error", str(e))
        raise

class Library_App(tkinter.Tk):
    def __init__(self):
        super().__init__()
        self.title("Library Database")
        self.geometry("800x600")
        nb = ttk.Notebook(self)
        nb.pack(fill="both", expand=True)

library = Library_App()

library.mainloop()
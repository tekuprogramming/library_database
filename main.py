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
        self.book_tab = Book_Tab(nb)
        self.book_tab.refresh()
        nb.add(self.book_tab, text="Books")

class Book_Tab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        # control panel
        tool_bar = ttk.Frame(self)
        tool_bar.pack(fill="x", padx=8, pady=8)
        ttk.Button(tool_bar, text="Add book").pack(side="left", padx=4)

        #table
        columns = ("id", "name", "publisher", "publishment_date", "rating", "binding")
        self.tree = ttk.Treeview(self, columns=columns, show="headings")
        for c, head in zip(columns, ["id", "name", "publisher", "publishment_date", "rating", "binding"]):
            self.tree.heading(c, text=head)
            self.tree.column(c, width=120)
        self.tree.pack(fill="both", expand=True, padx=8, pady=8)

    def refresh(self):
        # cleaning the current columns
        for i in self.tree.get_children():
            self.tree.delete(i)
        try:
            con = getcon()
            cur = con.cursor()
            # command book + author_name
            cur.execute("""
                select b.id, b.name, b.publisher, b.publishment_date, b.rating, b.binding
                from book b
                -- join author a on a.author_id = b.id
            """)
            rows = cur.fetchall()
            for row in rows:
                self.tree.insert("", "end", values=[str(x) if x is not None else "" for x in row])
            cur.close()
            con.close()
        except Exception as e:
            logging.error(e)
            messagebox.showerror("Connection error", str(e))

library = Library_App()


library.mainloop()

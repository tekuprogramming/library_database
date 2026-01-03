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
        ttk.Button(tool_bar, text="Update").pack(side="left", padx=4)

        #table
        columns = ("id", "name", "publisher", "publishment_date", "rating", "binding")
        self.tree = ttk.Treeview(self, columns=columns, show="headings")
        for c, head in zip(columns, ["id", "name", "publisher", "publishment_date", "rating", "binding"]):
            self.tree.heading(c, text=head)
            self.tree.column(c, width=120)
        self.tree.pack(fill="both", expand=True, padx=8, pady=8)

        self.refresh()

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

class Book_Editor(tkinter.Toplevel):
    def __init__(self, book_tab: Book_Tab, mode="create", book_id = None):
        super().__init__(book_tab)
        self.title("Book")
        self.mode = mode
        self.book_id = book_id
        self.geometry("520x520")
        self.resizable(False, False)

        frame = ttk.Frame(self)
        frame.pack(fill="both", expand=True, padx=10, pady=10)
        ttk.Label(frame, text="Book Name").grid(row=0, column=0, sticky="w")
        self.name_e = ttk.Entry(frame)
        self.name_e.grid(row=0, column=1, sticky="w")

        ttk.Label(frame, text="Publisher").grid(row=1, column=0, sticky="w")
        self.publisher = ttk.Combobox(frame, state="readonly")
        self.publisher.grid(row=1, column=1, sticky="w")

        ttk.Label(frame, text="Publishment Date").grid(row=2, column=0, sticky="w")
        self.date = ttk.Combobox(frame, state="readonly")
        self.date.grid(row=2, column=1, sticky="w")

        ttk.Label(frame, text="Rating").grid(row=3, column=0, sticky="w")
        self.rating = ttk.Combobox(frame, state="readonly")
        self.rating.grid(row=3, column=1, sticky="w")

        ttk.Label(frame, text="Binding").grid(row=4, column=0, sticky="w")
        self.binding = ttk.Combobox(frame, state="readonly", values=["hardcover", "paperback", "ebook"])
        self.binding.grid(row=4, column=1, sticky="w")

        # buttons
        buttons = ttk.Frame(self)
        buttons.pack(fill="x", padx=10, pady=10)
        ttk.Button(buttons, text="Save").pack(side="left", padx=5)
        ttk.Button(buttons, text="Cancel").pack(side="right", padx=5)

        # self.publisher = fetchall

library = Library_App()


library.mainloop()


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

def fetch_all(sql, params=None):
    con = getcon()
    try:
        cur = con.cursor()
        cur.execute(sql, params or [])
        rows = cur.fetchall()
        cur.close()
        con.commit()
        return rows
    except pyodbc.Error as e:
        con.rollback()
        logging.error(f"Error: {e}")
        messagebox.showerror("Connection error", str(e))
        return []
    finally:
        con.close()

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

        self.publisher = fetch_all("select id, name from publisher order by name")
        self.publisher2["values"] = [f"{p[0]} - {p[1]}" for p in self.publisher]

        self.author = fetch_all("select id, surname, name, email, is_active from author")
        for i in self.author:
            self.author2.insert("end", f"{i[0]} - {i[1]} {i[2]} {i[3]} {i[4]} {i[5]}")

        if self.mode == "edit" and self.book_id:
            self.load_book()

    def load_book(self):
        rows = fetch_all("select b.name, b.publisher, b.publishment_date, b.rating, b.binding from book b where b.id = ?", (self.book_id,))
        if not rows:
            messagebox.showerror("Error: Book wasn't found")
            return
        name, publisher, publishment_date, rating, binding = rows[0]
        self.name_e.insert(0, name)
        self.publisher_e.insert(0, publisher)
        self.publishment_date_e.insert(0, str(publishment_date) if publishment_date else "")
        self.rating_e.insert(0, str(rating) if rating is not None else "")
        self.binding_e.set(binding)

        for idx, p in enumerate(self.publisher):
            if p[0] == publisher:
                self.publisher2.current(idx)
                break

    def save(self):
        try:
            name = self.name_e.get().strip()
            if not name:
               raise ValueError("Book name cannot be empty")
            pub_val = self.publisher2.get()
            if not pub_val:
                raise ValueError("Publisher cannot be empty")
            publisher_id = int(pub_val.split(" - ")[0])
        
            date_str = self.publishment_date_e.get().strip() or None
            rating = self.rating_e.get()
            binding = self.binding_e.get()

            selected_index = self.author2.curselection()
            author_index = []
            for i in selected_index:
                author_index.append(int(self.author2.get(i).split(" - ")[0]))

            con = getcon()
            try:
                cur = con.cursor()
                if self.mode == "create":
                    cur.execute("insert into book (name, publisher, publishment_date, rating, binding) values (?,?,?,?,?)",
                                (name, publisher_id, date_str, rating, binding))
                con.commit()
                messagebox.showinfo("Book saved", "Book was successfully saved")
            except pyodbc.Error as e:
                con.rollback()
                logging.error(e)
                messagebox.showerror("Connection error", str(e))
            finally:
                con.close()
        except Exception as e:
            messagebox.showerror("Connection error", str(e))

library = Library_App()


library.mainloop()




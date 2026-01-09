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

def validate_binding(binding: str):
    allowed = {"hardcover", "paperback", "ebook"}
    if binding not in allowed:
        raise ValueError(f"Binding should be one of these: {', '.join(allowed)}")

def validate_rating(rating_str: str):
    if rating_str == "" or rating_str is None:
        return None
    try:
        r = float(rating_str)
    except:
        raise ValueError("Rating has to be a number")
    if not (0.0 <= r <= 5.0):
        raise ValueError("Rating has to be in range 0.0–5.0")
    return r

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

def execute_sql(sql, params=None, commit=True):
    con = getcon()
    try:
        cur = con.cursor()
        cur.execute(sql, params or [])
        if commit:
            con.commit()
        cur.close()
        return True
    except pyodbc.Error as e:
        con.rollback()
        logging.error(f"SQL exec error: {e}")
        messagebox.showerror("Execution error", str(e))
        return False
    finally:
        con.close()

class LibraryApp(tkinter.Tk):
    def __init__(self):
        super().__init__()
        self.title("Library Database")
        self.geometry("800x600")
        
        nb = ttk.Notebook(self)
        nb.pack(fill="both", expand=True)
        
        self.book_tab = BookTab(nb)
        self.author_tab = AuthorTab(nb)
        self.import_tab = ImportTab(nb)
        self.report_tab = ReportTab(nb)
        self.settings_tab = SettingsTab(nb)

        nb.add(self.book_tab, text="Books")
        nb.add(self.author_tab, text="Authors")
        nb.add(self.import_tab, text="Import")
        nb.add(self.report_tab, text="Report")
        nb.add(self.settings_tab, text="Settings")

        self.book_tab.refresh()
        self.author_tab.refresh()

class BookTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        # control panel
        tool_bar = ttk.Frame(self)
        tool_bar.pack(fill="x", padx=8, pady=8)
        
        ttk.Button(tool_bar, text="Add book", command=self.add_book_dialog).pack(side="left", padx=4)
        ttk.Button(tool_bar, text="Change selected", command=self.edit_selected_dialog).pack(side="left", padx=4)
        ttk.Button(tool_bar, text="Delete selected", command=self.delete_selected).pack(side="left", padx=4)
        ttk.Button(tool_bar, text="Transfer authorship", command=self.transfer_authorship_dialog).pack(side="left", padx=4)
        ttk.Button(tool_bar, text="Update", command=self.refresh).pack(side="left", padx=4)

        #table
        columns = ("id", "name", "publisher", "publishment_date", "rating", "binding")
        self.tree = ttk.Treeview(self, columns=columns, show="headings")
        for c, head in zip(columns, ["id", "name", "publisher", "publishment_date", "rating", "binding"]):
            self.tree.heading(c, text=head)
            self.tree.column(c, width=120 if c not in "name" else 220)
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

    def add_book_dialog(self):
        BookEditor(self, mode="create")

    def edit_selected_dialog(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("Selection", "Select a book")
            return
        item = self.tree.item(sel[0])["values"]
        book_id = int(item[0])
        BookEditor(self, mode="edit", book_id=book_id)

    def delete_selected(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("Selection", "Select a book")
            return
        item = self.tree.item(sel[0])["values"]
        book_id = int(item[0])
        if not messagebox.askyesno("Confirmation", f"Delete book #{book_id} and its relationships?"):
            return
        con = getcon()
        try:
            cur = con.cursor()
            cur.execute("delete from book_author where book_id = ?", (book_id,))
            cur.execute("delete from book where id = ?", (book_id,))
            con.commit()
            messagebox.showinfo("Done", "The book was deleted")
            self.refresh()
        except pyodbc.Error as e:
            con.rollback()
            logging.error(e)
            messagebox.showerror("Deletion error", str(e))
        finally:
            con.close()

    def transfer_authorship_dialog(self):
        TransferAuthorship(self)

class BookEditor(tkinter.Toplevel):
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
        self.name_e = ttk.Entry(frame, width=40)
        self.name_e.grid(row=0, column=1, sticky="w")

        ttk.Label(frame, text="Publisher").grid(row=1, column=0, sticky="w")
        self.publisher2 = ttk.Combobox(frame, width=37, state="readonly")
        self.publisher2.grid(row=1, column=1, sticky="w")

        ttk.Label(frame, text="Publishment Date (YYYY-MM-DD)").grid(row=2, column=0, sticky="w")
        self.date = ttk.Combobox(frame, width=40)
        self.date.grid(row=2, column=1, sticky="w")

        ttk.Label(frame, text="Rating").grid(row=3, column=0, sticky="w")
        self.rating = ttk.Combobox(frame, width=40)
        self.rating.grid(row=3, column=1, sticky="w")

        ttk.Label(frame, text="Binding").grid(row=4, column=0, sticky="w")
        self.binding = ttk.Combobox(frame, width=37, state="readonly", values=["hardcover", "paperback", "ebook"])
        self.binding.grid(row=4, column=1, sticky="w")

        ttk.Label(frame, text="Author").grid(row=5, column=0, sticky="nw")
        self.author_lb = tkinter.Listbox(frame, selectmode="multiple", width=40, height=8)
        self.author_lb.grid(row=5, column=1, sticky="w")

        # buttons
        buttons = ttk.Frame(self)
        buttons.pack(fill="x", padx=10, pady=10)
        ttk.Button(buttons, text="Save", command=self.save).pack(side="left", padx=5)
        ttk.Button(buttons, text="Destroy", command=self.destroy).pack(side="right", padx=5)

        self.publisher = fetch_all("select id, name from publisher order by name")
        self.publisher2["values"] = [f"{p[0]} - {p[1]}" for p in self.publisher]

        self.author = fetch_all("select id, surname, name from author where is_active=1 order by surname, name")
        for a in self.author:
            self.author_lb.insert("end", f"{a[0]} - {a[1]} {a[2]}")

        if self.mode == "edit" and self.book_id:
            self.load_book()

    def load_book(self):
        rows = fetch_all("select b.name, b.publisher, b.publishment_date, b.rating, b.binding from book b where b.id = ?", (self.book_id,))
        if not rows:
            messagebox.showerror("Error: Book wasn't found")
            self.destroy()
            return
        name, publisher, publishment_date, rating, binding = rows[0]
        self.name_e.insert(0, name)
        self.publisher2.insert(0, publisher)
        self.date.insert(0, str(publishment_date) if publishment_date else "")
        if rating is not None: self.rating.insert(0,
                                                  f"{rating:.2f}")
        self.binding.set(binding)

        for idx, p in enumerate(self.publisher):
            if p[0] == publisher:
                self.publisher2.current(idx)
                break

        links = fetch_all("select author_id from book_author where book_id=? and is_active=1", (self.book_id,))
        active_ids = {l[0] for l in links}
        for i, a in enumerate(self.author):
            if a[0] in active_ids:
                self.author_lb.select_set(i)

    def save(self):
        try:
            name = self.name_e.get().strip()
            if not name:
               raise ValueError("Book name cannot be empty")
            pub_val = self.publisher2.get()
            if not pub_val:
                raise ValueError("Select a publisher")
            publisher_id = int(pub_val.split(" - ")[0])

            date_str = self.date.get().strip() or None
            rating = validate_rating(self.rating.get().strip())
            binding = self.binding.get()
            validate_binding(binding)

            selected_indices = self.author_lb.curselection()
            author_ids = []
            for i in selected_indices:
                val = self.author_lb.get(i)
                if val:
                    author_ids.append(int(val.split(" - ")[0]))

            con = getcon()
            try:
                cur = con.cursor()
                if self.mode == "create":
                    cur.execute("""
                        insert into book (name, publisher, publishment_date, rating, binding)
                        output inserted.id
                        values (?, ?, ?, ?, ?)
                    """, (name, publisher_id, date_str, rating, binding))
                    book_id = cur.fetchone()[0]
                    if book_id is None:
                        raise ValueError("Book ID was not generated")
                    for aid in author_ids:
                        cur.execute(
                            "insert into book_author (author_id, book_id, is_active) values (?, ?, 1)",
                            (aid, book_id)
                        )
                else:
                    cur.execute(
                        "update book set name=?, publisher=?, publishment_date=?, rating=?, binding=? where id=?",
                        (name, publisher_id, date_str, rating, binding, self.book_id)
                    )

                    cur.execute("update book_author set is_active=0 where book_id=?", (self.book_id,))

                    for aid in author_ids:
                        cur.execute(
                            "insert into book_author (author_id, book_id, is_active) values (?, ?, 1)",
                            (aid, self.book_id)
                        )
                con.commit()
                messagebox.showinfo("Book saved", "Book was successfully saved")
                self.master.refresh()
                self.destroy()
            except pyodbc.Error as e:
                con.rollback()
                logging.error(e)
                messagebox.showerror("Connection error", str(e))
            finally:
                con.close()
       except Exception as e:
            messagebox.showerror("Connection error", str(e))

class TransferAuthorship(tkinter.Toplevel):
    def __init__(self, book_tab: BookTab):
        super().__init__(book_tab)
        self.title("Transfer Authorship")
        self.geometry("420x260")
        frame = ttk.Frame(self); frame.pack(fill="both", expand=True, padx=10, pady=10)

        ttk.Label(frame, text="Book").grid(row=0, column=0, sticky="w")
        self.book2 = ttk.Combobox(frame, width=35, state="readonly"); self.book2.grid(row=0, column=1)
        self.book = fetch_all("select id, name from book order by name")
        self.book2["values"] = [f"{b[0]} - {b[1]}" for b in self.book]

        ttk.Label(frame, text="From author").grid(row=1, column=0, sticky="w")
        self.from2 = ttk.Combobox(frame, width=35, state="readonly"); self.from2.grid(row=1, column=1)

        ttk.Label(frame, text="To author").grid(row=2, column=0, sticky="w")
        self.to2 = ttk.Combobox(frame, width=35, state="readonly"); self.to2.grid(row=2, column=1)

        ttk.Button(frame, text="Load book authors", command=self.load_book_authors).grid(row=3, column=0, columnspan=2, pady=6)
        ttk.Button(frame, text="Transfer", command=self.transfer).grid(row=4, column=0, columnspan=2, pady=6)

    def load_book_authors(self):
        val = self.book2.get()
        if not val:
            messagebox.showinfo("Selection", "Select a book")
            return
        book_id = int(val.split(" - ")[0])
        rows = fetch_all("""
            select a.id, concat(a.surname,' ',a.name) as sn
            from author a
            join book_author ba on ba.author_id = a.id
            where ba.book_id=? and ba.is_active=1
            order by a.surname, a.name
        """, (book_id,))
        self.from2["values"] = [f"{r[0]} - {r[1]}" for r in rows]

        authors_all = fetch_all("select id, concat(surname,' ',name) from author where is_active=1 order by surname, name")
        self.to2["values"] = [f"{r[0]} - {r[1]}" for r in authors_all]

    def transfer(self):
        try:
            book_id = int(self.book2.get().split(" - ")[0])
            from_author_id = int(self.from2.get().split(" - ")[0])
            to_author_id = int(self.to2.get().split(" - ")[0])
        except:
            messagebox.showerror("Error", "Fill all the fields")
            return

        con = getcon()
        try:
            cur = con.cursor()

            cur.execute("""
                update book_author set is_active = 0
                where book_id = ? and author_id = ? and is_active = 1
            """, (book_id, from_author_id))

            cur.execute("""
                insert into book_author (author_id, book_id, is_active) values (?, ?, 1)
            """, (to_author_id, book_id))
            con.commit()
            messagebox.showinfo("Done", "Authorship was transferred")
            self.master.refresh()
            self.destroy()
        except pyodbc.Error as e:
            con.rollback()
            logging.error(e)
            messagebox.showerror("Transferring error", str(e))
        finally:
            con.close()

class AuthorTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        tool_bar = ttk.Frame(self); tool_bar.pack(fill="x", padx=8, pady=8)
        ttk.Button(tool_bar, text="Update", command=self.refresh).pack(side="left", padx=4)

        columns = ("id", "surname", "name", "email", "is_active")
        self.tree = ttk.Treeview(self, columns=columns, show="headings")
        for c, hdr in zip(columns, ["id","surname","name","email","active?"]):
            self.tree.heading(c, text=hdr)
            self.tree.column(c, width=150)
        self.tree.pack(fill="both", expand=True, padx=8, pady=8)

    def refresh(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        rows = fetch_all("select id, surname, name, email, is_active from author order by surname, name")
        for r in rows:
            self.tree.insert("", "end", values=[str(x) if x is not None else "" for x in r])

class ImportTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        ttk.Label(self, text="Data Import Into Tables").pack(anchor="w", padx=8, pady=8)

        frame = ttk.Frame(self); frame.pack(fill="x", padx=8, pady=8)
        ttk.Button(frame, text="Publisher import", command=self.import_publishers_csv).pack(side="left", padx=6)
        ttk.Button(frame, text="Author import", command=self.import_authors_json).pack(side="left", padx=6)
        ttk.Button(frame, text="Genre import", command=self.import_genres_xml).pack(side="left", padx=6)

    def import_publishers_csv(self):
        path = filedialog.askopenfilename(title="Publisher CSV", filetypes=[("CSV","*.csv")])
        if not path: return
        con = getcon()
        try:
            with open(path, newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                cur = con.cursor()
                for row in reader:
                    cur.execute("""
                        insert into publisher (name, address, phone_number, email, website)
                        values (?, ?, ?, ?, ?)
                    """, (row.get("name"), row.get("address"), row.get("phone_number"), row.get("email"), row.get("website")))
                con.commit()
            messagebox.showinfo("Done", "CSV import was completed")
        except Exception as e:
            con.rollback()
            logging.error(e)
            messagebox.showerror("CSV import error", str(e))
        finally:
            con.close()

    def import_authors_json(self):
        path = filedialog.askopenfilename(title="Author JSON", filetypes=[("JSON","*.json")])
        if not path: return
        con = getcon()
        try:
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
                cur = con.cursor()
                for a in data:
                    cur.execute("""
                        insert into author (surname, name, email, is_active)
                        values (?, ?, ?, ?)
                    """, (a.get("surname"), a.get("name"), a.get("email"), int(bool(a.get("is_active", True)))))
                con.commit()
            messagebox.showinfo("Done", "JSON import was completed")
        except Exception as e:
            con.rollback()
            logging.error(e)
            messagebox.showerror("JSON import error", str(e))
        finally:
            con.close()

    def import_genres_xml(self):
        path = filedialog.askopenfilename(title="Genre XML", filetypes=[("XML","*.xml")])
        if not path: return
        con = getcon()
        try:
            tree = ET.parse(path)
            root = tree.getroot()
            cur = con.cursor()
            for g in root.findall(".//genre"):
                name = g.get("name") or (g.text or "").strip()
                cur.execute("insert into genre (name) values (?)", (name,))
            con.commit()
            messagebox.showinfo("Done", "XML import was completed")
        except Exception as e:
            con.rollback()
            logging.error(e)
            messagebox.showerror("XML import error", str(e))
        finally:
            con.close()

class ReportTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        tool_bar = ttk.Frame(self); tool_bar.pack(fill="x", padx=8, pady=8)
        ttk.Button(tool_bar, text="Generate A Report", command=self.generate).pack(side="left", padx=4)

        columns = ("publisher", "books_count", "avg_rating", "active_authors")
        self.tree = ttk.Treeview(self, columns=columns, show="headings")
        for c, hdr in zip(columns, ["publisher","of books","average rating","of active authors"]):
            self.tree.heading(c, text=hdr)
            self.tree.column(c, width=200 if c=="publisher" else 150)
        self.tree.pack(fill="both", expand=True, padx=8, pady=8)

    def generate(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        sql = """
            with publisher_books as (
                select p.id as publisher_id, p.name as publisher_name, count(b.id) as books_count,
                       avg(b.rating) as avg_rating
                from publisher p
                left join book b ON b.publisher = p.id
                group by p.id, p.name
            ),
            publisher_authors as (
                select p.id as publisher_id, count(distinct a.id) as active_authors
                from publisher p
                left join book b on b.publisher = p.id
                left join book_author ba on ba.book_id = b.id and ba.is_active = 1
                left join author a on a.id = ba.author_id
                group by p.id
            )
            select pb.publisher_name, pb.books_count, pb.avg_rating, pa.active_authors
            from publisher_books pb
            left join publisher_authors pa on pa.publisher_id = pb.publisher_id
            order by pb.publisher_name
        """
        rows = fetch_all(sql)
        for r in rows:
            self.tree.insert("", "end", values=[str(x) if x is not None else "" for x in r])

class SettingsTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        ttk.Label(self, text="Connection Settings").pack(anchor="w", padx=8, pady=8)

        frame = ttk.Frame(self); frame.pack(fill="x", padx=8, pady=8)
        self.driver_e = ttk.Entry(frame, width=50); self._row(frame, 0, "ODBC Driver", self.driver_e)
        self.server_e = ttk.Entry(frame, width=50); self._row(frame, 1, "Server", self.server_e)
        self.db_e = ttk.Entry(frame, width=50); self._row(frame, 2, "Database", self.db_e)
        self.tc_e = ttk.Entry(frame, width=50); self._row(frame, 3, "Trusted Connection", self.tc_e)
        self.en_e = ttk.Entry(frame, width=50); self._row(frame, 4, "Encrypt", self.en_e)
        self.tsc_e = ttk.Entry(frame, width=50); self._row(frame, 5, "Trust Server Certificate", self.tsc_e)

        ttk.Button(self, text="Save into config.ini", command=self.save).pack(padx=8, pady=8)

        self.driver_e.insert(0, config.get("database","driver",fallback="ODBC Driver 18 for SQL Server"))
        self.server_e.insert(0, config.get("database","server",fallback="localhost\\SQLEXPRESS"))
        self.db_e.insert(0, config.get("database","database",fallback="library"))
        self.tc_e.insert(0, config.get("database","trusted_connection",fallback="yes"))
        self.en_e.insert(0, config.get("database","encrypt",fallback="yes"))
        self.tsc_e.insert(0, config.get("database", "trust_server_certificate", fallback="yes"))

    def _row(self, frame, r, label, entry):
        ttk.Label(frame, text=label).grid(row=r, column=0, sticky="w")
        entry.grid(row=r, column=1, sticky="we", padx=6, pady=4)
        frame.grid_columnconfigure(1, weight=1)

    def save(self):
        try:
            if "database" not in config.sections():
                config.add_section("database")
            config.set("database","driver", self.driver_e.get())
            config.set("database","server", self.server_e.get())
            config.set("database","database", self.db_e.get())
            config.set("database","trusted connection", self.tc_e.get())
            config.set("database","encrypt", self.en_e.get())
            config.set("database", "trust server certificate", self.tsc_e.get())

            with open("config.ini","w",encoding="utf-8") as f:
                config.write(f)
            messagebox.showinfo("Done","The settings were saved. Restart the application to apply them.")
        except Exception as e:
            logging.error(e)
            messagebox.showerror("Settings saving error", str(e))

if __name__ == "__main__":
    app = LibraryApp()
    app.mainloop()





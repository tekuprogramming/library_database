import tkinter
from tkinter import ttk, messagebox

from src.db.repositories.author_repository import AuthorRepository
from src.db.repositories.book_repository import BookRepository
from src.db.repositories.bookauthor_repository import BookAuthorRepository
from src.db.repositories.publisher_repository import PublisherRepository
from src.validation.validators import validate_rating, validate_binding, validate_date


class BookEditor(tkinter.Toplevel):
    """
    Modal dialog window used for creating or editing a book record.

    The dialog allows:
    - entering book details (name, date, rating, binding)
    - selecting a publisher
    - assigning one or more authors to the book
    """
    def __init__(self, book_tab, mode="create", book_id=None):
        """
        Initializes the editor window.

        :param book_tab: Parent BookTab instance (used to refresh data)
        :param mode: "create" for new book, "edit" for editing existing book
        :param book_id: ID of the book to edit (used only in edit mode)
        """
        super().__init__(book_tab)
        self.title("Book")
        self.mode = mode
        self.book_id = book_id
        self.geometry("520x520")
        self.resizable(False, False)

        # Initialize repositories
        self.book_repo = BookRepository()
        self.author_repo = AuthorRepository()
        self.publisher_repo = PublisherRepository()
        self.book_author_repo = BookAuthorRepository()

        # Main content frame
        frame = ttk.Frame(self)
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Book fields
        ttk.Label(frame, text="Book name").grid(row=0, column=0, sticky="w")
        self.name_e = ttk.Entry(frame, width=40); self.name_e.grid(row=0, column=1, sticky="w")

        ttk.Label(frame, text="Publisher").grid(row=1, column=0, sticky="w")
        self.publisher_cb = ttk.Combobox(frame, width=37, state="readonly"); self.publisher_cb.grid(row=1, column=1, sticky="w")

        ttk.Label(frame, text="Publishment date (YYYY-MM-DD)").grid(row=2, column=0, sticky="w")
        self.date = ttk.Entry(frame, width=40); self.date.grid(row=2, column=1, sticky="w")

        ttk.Label(frame, text="Rating").grid(row=3, column=0, sticky="w")
        self.rating = ttk.Entry(frame, width=40); self.rating.grid(row=3, column=1, sticky="w")

        ttk.Label(frame, text="Binding").grid(row=4, column=0, sticky="w")
        self.binding_cb = ttk.Combobox(frame, width=37, state="readonly", values=["hardcover","paperback","ebook"])
        self.binding_cb.grid(row=4, column=1, sticky="w")

        # Author selection
        ttk.Label(frame, text="Author").grid(row=5, column=0, sticky="nw")
        self.author_lb = tkinter.Listbox(frame, selectmode="multiple", width=40, height=8); self.author_lb.grid(row=5, column=1, sticky="w")

        # Buttons
        buttons = ttk.Frame(self); buttons.pack(fill="x", padx=10, pady=10)
        ttk.Button(buttons, text="Save", command=self.save).pack(side="left", padx=5)
        ttk.Button(buttons, text="Close", command=self.destroy).pack(side="right", padx=5)

        # Load data for comboboxes and lists
        self.load_publishers()
        self.load_authors()

        # If editing an existing book, load its data
        if self.mode=="edit" and self.book_id:
            self.load_book()

    def load_publishers(self):
        """
        Loads publishers from the database and fills the publisher combobox.
        """
        self.publishers = self.publisher_repo.fetch_all()
        self.publisher_cb["values"] = [f"{p[0]} - {p[1]}" for p in self.publishers]

    def load_authors(self):
        """
        Loads active authors from the database and fills the author listbox.
        """
        try:
            self.authors = self.author_repo.get_all(active_only=True)
            for a in self.authors:
                self.author_lb.insert("end", f"{a[0]} - {a[1]} {a[2]}")
        except Exception as e:
            messagebox.showerror("Error while loading authors", str(e))

    def load_book(self):
        """
        Loads book data for edit mode and pre-fills the form,
        including currently assigned active authors.
        """
        book = self.book_repo.fetch_by_id(self.book_id)
        if not book:
            messagebox.showerror("Error", "Book not found")
            self.destroy()
            return

        # Fill book fields
        self.name_e.insert(0, book[1])
        self.date.insert(0, book[3].strftime("%Y-%m-%d") if book[3] else "")
        self.rating.insert(0, f"{book[4]:.2f}" if book[4] is not None else "")
        self.binding_cb.set(book[5])

        # Select publisher
        for idx, p in enumerate(self.publishers):
            if p[0] == book[2]:
                self.publisher_cb.current(idx)

        # Select active authors
        active_author_ids = self.book_author_repo.fetch_active_authors(self.book_id)
        for i, a in enumerate(self.authors):
            if a[0] in active_author_ids:
                self.author_lb.select_set(i)


    def save(self):
        """
        Validates input data and saves the book.
        Handles both create and edit modes.
        """
        try:
            name = self.name_e.get().strip()
            if not name: raise ValueError("Book name can't be empty")
            pub_val = self.publisher_cb.get()
            if not pub_val: raise ValueError("Choose a publisher")
            publisher_id = int(pub_val.split(" - ")[0])
            date_str = self.date.get().strip() or None
            rating = validate_rating(self.rating.get().strip())
            binding = self.binding_cb.get(); validate_binding(binding)
            author_ids = [int(self.author_lb.get(i).split(" - ")[0]) for i in self.author_lb.curselection()]
            date_str = validate_date(self.date.get().strip())

            if self.date.get().strip() and date_str is None:
                return
            if self.mode=="create":
                book_id = self.book_repo.insert(name, publisher_id, date_str, rating, binding)
                self.book_author_repo.assign_authors(book_id, author_ids)
            else:
                self.book_repo.update(self.book_id, name, publisher_id, date_str, rating, binding)
                self.book_author_repo.assign_authors(self.book_id, author_ids, overwrite=True)

            messagebox.showinfo("Done","Book saved")
            self.master.refresh()
            self.destroy()
        except Exception as e:
            messagebox.showerror("Error", str(e))



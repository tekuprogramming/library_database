import tkinter
from tkinter import ttk, messagebox

from src.db.repositories.author_repository import AuthorRepository
from src.db.repositories.book_repository import BookRepository
from src.db.repositories.bookauthor_repository import BookAuthorRepository

class TransferAuthorship(tkinter.Toplevel):
    """
    Dialog window used to transfer authorship of a book
    from one author to another.

    The transfer is implemented by:
    - deactivating the original author for the selected book
    - activating or assigning a new author for the same book

    This operation demonstrates a transaction affecting
    multiple records in a many-to-many relationship.
    """
    def __init__(self, book_tab):
        """
        Initializes the transfer dialog.

        :param book_tab: Parent BookTab instance (used to refresh data)
        """
        super().__init__(book_tab)
        self.title("Transfer Authorship")
        self.geometry("420x260")
        self.book_tab = book_tab

        # Initialize repositories
        self.book_repo = BookRepository()
        self.author_repo = AuthorRepository()
        self.book_author_repo = BookAuthorRepository()

        # Main frame
        frame = ttk.Frame(self)
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Book selection
        ttk.Label(frame, text="Book").grid(row=0, column=0, sticky="w")
        self.book_cb = ttk.Combobox(frame, width=35, state="readonly")
        self.book_cb.grid(row=0, column=1)

        # Source author selection
        ttk.Label(frame, text="From author").grid(row=1, column=0, sticky="w")
        self.from_cb = ttk.Combobox(frame, width=35, state="readonly")
        self.from_cb.grid(row=1, column=1)

        # Target author selection
        ttk.Label(frame, text="To author").grid(row=2, column=0, sticky="w")
        self.to_cb = ttk.Combobox(frame, width=35, state="readonly")
        self.to_cb.grid(row=2, column=1)

        # Action buttons
        ttk.Button(frame, text="Load book authors", command=self.load_authors_for_book).grid(row=3, column=0, columnspan=2, pady=6)
        ttk.Button(frame, text="Transfer", command=self.transfer).grid(row=4, column=0, columnspan=2, pady=6)

        # Initial data loading
        self.load_books()
        self.load_all_authors()

    def load_books(self):
        """
        Loads all books from the database and fills the book combobox.
        """
        books = self.book_repo.get_all()
        self.books = books
        self.book_cb["values"] = [f"{b[0]} - {b[1]}" for b in books]

    def load_all_authors(self):
        """
        Loads all active authors from the database
        and fills the target author combobox.
        """
        self.all_authors = self.author_repo.get_all(active_only=True)
        self.to_cb["values"] = [f"{a[0]} - {a[1]} {a[2]}" for a in self.all_authors]

    def load_authors_for_book(self):
        """
        Loads only authors currently assigned to the selected book
        and fills the source author combobox.
        """
        val = self.book_cb.get()
        if not val:
            messagebox.showinfo("Choice", "Choose a book")
            return

        book_id = int(val.split(" - ")[0])
        active_author_ids = self.book_author_repo.fetch_active_authors(book_id)
        authors_in_book = [a for a in self.all_authors if a[0] in active_author_ids]
        self.from_cb["values"] = [f"{a[0]} - {a[1]} {a[2]}" for a in authors_in_book]

    def transfer(self):
        """
        Performs the authorship transfer.

        The original author is deactivated for the book,
        and the new author is assigned or reactivated.
        """
        try:
            book_id = int(self.book_cb.get().split(" - ")[0])
            from_author_id = int(self.from_cb.get().split(" - ")[0])
            to_author_id = int(self.to_cb.get().split(" - ")[0])
        except:
            messagebox.showerror("Error", "Fill all fields")
            return

        try:
            # Deactivate original author
            self.book_author_repo.deactivate_authors_for_author(book_id, from_author_id)
            # Assign or activate new author
            self.book_author_repo.assign_authors(book_id, [to_author_id])

            messagebox.showinfo("Done", "The authorship was transferred")
            self.book_tab.refresh()
            self.destroy()
        except Exception as e:
            messagebox.showerror("Transfer error", str(e))

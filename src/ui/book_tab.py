from tkinter import ttk, messagebox
from src.db.repositories.book_repository import BookRepository
from src.ui.dialogs.book_editor import BookEditor
from src.ui.dialogs.transfer_authorship import TransferAuthorship


class BookTab(ttk.Frame):
    """
    UI tab for managing books in the library database.

    Features:
    - Display all books in a Treeview
    - Add, edit, delete books
    - Transfer authorship between authors
    - Refresh the book list

    All database interactions are handled through BookRepository
    following the Repository (DAO) pattern.
    """

    def __init__(self, parent):
        """
        Initializes the Book tab and its UI components.

        :param parent: Parent widget (Notebook)
        """
        super().__init__(parent)
        # Repository for book-related database operations
        self.repo = BookRepository()

        # Toolbar with actions
        tool_bar = ttk.Frame(self)
        tool_bar.pack(fill="x", padx=8, pady=8)

        ttk.Button(tool_bar, text="Add book", command=self.add_book_dialog).pack(side="left", padx=4)
        ttk.Button(tool_bar, text="Edit selected", command=self.edit_selected_dialog).pack(side="left", padx=4)
        ttk.Button(tool_bar, text="Delete selected", command=self.delete_selected).pack(side="left", padx=4)
        ttk.Button(tool_bar, text="Transfer authorship", command=self.transfer_authorship_dialog).pack(side="left", padx=4)
        ttk.Button(tool_bar, text="Refresh", command=self.refresh).pack(side="left", padx=4)

        # Treeview table for displaying books
        columns = ("id", "name", "publisher", "publishment_date", "rating", "binding")
        self.tree = ttk.Treeview(self, columns=columns, show="headings")
        # Setup headings and column widths
        for c, hdr in zip(columns, ["ID","Name","Publisher","Publishment date","Rating","Binding"]):
            self.tree.heading(c, text=hdr)
            self.tree.column(c, width=120 if c != "name" else 220)
        self.tree.pack(fill="both", expand=True, padx=8, pady=8)

        # Load initial data
        self.refresh()

    def refresh(self):
        """
        Reloads all books from the database and updates the Treeview.

        Converts None or special types (like datetime) to readable strings for display.
        """

        # Clear existing rows
        for i in self.tree.get_children():
            self.tree.delete(i)

        # Load rows from repository
        for row in self.repo.get_all():
            display_row = [
                str(row[0]),  # ID
                row[1] or "",  # ID
                str(row[2]) if row[2] is not None else "",  # Publisher ID
                row[3].strftime("%Y-%m-%d") if row[3] else "",  # Publishment date
                f"{row[4]:.2f}" if row[4] is not None else "",  # Rating
                row[5] or ""  # Binding
            ]
            self.tree.insert("", "end", values=display_row)

    def delete_selected(self):
        """
        Deletes the currently selected book from the database.

        Prompts the user if no selection is made.
        """
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("Choice", "Choose a book")
            return

        book_id = int(self.tree.item(sel[0])["values"][0])
        self.repo.delete(book_id)
        self.refresh()

    def add_book_dialog(self):
        """
        Opens the BookEditor dialog in 'create' mode for adding a new book.
        """
        BookEditor(self, mode="create")

    def edit_selected_dialog(self):
        """
        Opens the BookEditor dialog in 'edit' mode for the selected book.

        Prompts the user if no selection is made.
        """
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("Choice", "Choose a book")
            return
        book_id = int(self.tree.item(sel[0])["values"][0])
        BookEditor(self, mode="edit", book_id=book_id)

    def transfer_authorship_dialog(self):
        """
        Opens the TransferAuthorship dialog to transfer authorship for a selected book.
        """
        TransferAuthorship(self)

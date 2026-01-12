from tkinter import ttk, messagebox
from src.db.repositories.author_repository import AuthorRepository

class AuthorTab(ttk.Frame):
    """
    UI tab responsible for displaying authors stored in the database.

    This tab allows the user to:
    - view all authors
    - refresh the list manually

    Data are loaded exclusively via AuthorRepository
    to follow the Repository (DAO) pattern.
    """
    def __init__(self, parent):
        """
        Initializes the Author tab and its UI components.

        :param parent: Parent widget (Notebook)
        """
        super().__init__(parent)
        # Repository used for author-related database operations
        self.repo = AuthorRepository()

        # Toolbar
        tool_bar = ttk.Frame(self)
        tool_bar.pack(fill="x", padx=8, pady=8)
        ttk.Button(tool_bar, text="Update", command=self.refresh).pack(side="left", padx=4)

        # Author table
        columns = ("id", "surname", "name", "email", "is_active")
        self.tree = ttk.Treeview(self, columns=columns, show="headings")
        for c, hdr in zip(columns, ["ID", "Surname", "Name", "Email", "Active?"]):
            self.tree.heading(c, text=hdr)
            self.tree.column(c, width=150)
        self.tree.pack(fill="both", expand=True, padx=8, pady=8)

        # Initial data load
        self.refresh()

    def refresh(self):
        """
        Reloads all authors from the database
        and updates the Treeview content.
        """

        # Clear existing rows
        for i in self.tree.get_children():
            self.tree.delete(i)
        try:
            rows = self.repo.get_all()
            for r in rows:
                # Convert None values to empty strings for UI safety
                self.tree.insert("", "end", values=[str(x) if x is not None else "" for x in r])
        except Exception as e:
            messagebox.showerror("Error while loading authors", str(e))
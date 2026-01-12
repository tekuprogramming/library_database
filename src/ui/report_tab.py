from tkinter import ttk, messagebox
from src.db.repositories.report_repository import ReportRepository

class ReportTab(ttk.Frame):
    """
    UI tab for generating and displaying reports related to publishers.

    Features:
    - Generates a summary report per publisher
      showing number of books, average rating, and number of active authors
    - Displays results in a Treeview table
    """

    def __init__(self, parent):
        """
        Initializes the Report tab and its UI components.

        :param parent: Parent widget (Notebook)
        """
        super().__init__(parent)
        # Repository for report data
        self.repo = ReportRepository()

        # Toolbar frame for buttons
        tool_bar = ttk.Frame(self)
        tool_bar.pack(fill="x", padx=8, pady=8)
        ttk.Button(tool_bar, text="Generate a report", command=self.generate).pack(side="left", padx=4)

        # Treeview table to display report
        columns = ("publisher", "books_count", "avg_rating", "active_authors")
        self.tree = ttk.Treeview(self, columns=columns, show="headings")
        headers = ["Publisher", "Book count", "Average rating", "Number of active authors"]
        # Configure headings and column widths
        for c, hdr in zip(columns, headers):
            self.tree.heading(c, text=hdr)
            self.tree.column(c, width=200 if c=="publisher" else 150)
        self.tree.pack(fill="both", expand=True, padx=8, pady=8)

    def generate(self):
        """
        Generates the publisher report and fills the Treeview table.

        Steps:
        - Clears any existing rows in the table
        - Calls ReportRepository.get_publisher_report() to fetch data
        - Inserts each row into the Treeview
        - Converts None values to empty strings for display
        - Shows an error messagebox if any exception occurs
        """

        # Clear existing table rows
        for i in self.tree.get_children():
            self.tree.delete(i)
        try:
            # Fetch report data from repository
            rows = self.repo.get_publisher_report()
            # Insert each row into Treeview
            for r in rows:
                self.tree.insert("", "end", values=[str(x) if x is not None else "" for x in r])
        except Exception as e:
            # Display error if fetching report fails
            messagebox.showerror("Report error", str(e))
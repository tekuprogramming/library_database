import tkinter
from tkinter import ttk

from .ui.book_tab import BookTab
from .ui.author_tab import AuthorTab
from .ui.import_tab import ImportTab
from .ui.report_tab import ReportTab
from .ui.settings_tab import SettingsTab

class LibraryApp(tkinter.Tk):
    """
    Main application window for the Library Database.

    This class initializes the main Tkinter window and creates a tabbed interface
    with the following tabs:
    - Books: Manage book records (add, edit, delete, transfer authorship)
    - Authors: Manage authors
    - Import: Import data (publishers, authors, genres) from CSV/JSON/XML
    - Report: Generate reports (e.g., publisher report with book count and ratings)
    - Settings: Configure database connection settings

    Attributes:
        book_tab (BookTab): The Books tab instance
        author_tab (AuthorTab): The Authors tab instance
        import_tab (ImportTab): The Import tab instance
        report_tab (ReportTab): The Report tab instance
        settings_tab (SettingsTab): The Settings tab instance
    """
    def __init__(self):
        super().__init__()
        self.title("Library Database")
        self.geometry("900x600")

        # Create a Notebook widget for tabbed interface
        nb = ttk.Notebook(self)
        nb.pack(fill="both", expand=True)

        # Initialize each tab
        self.book_tab = BookTab(nb)
        self.author_tab = AuthorTab(nb)
        self.import_tab = ImportTab(nb)
        self.report_tab = ReportTab(nb)
        self.settings_tab = SettingsTab(nb)

        # Add tabs to the notebook with titles
        nb.add(self.book_tab, text="Books")
        nb.add(self.author_tab, text="Authors")
        nb.add(self.import_tab, text="Import")
        nb.add(self.report_tab, text="Report")
        nb.add(self.settings_tab, text="Settings")

        # Load initial data for books and authors
        self.book_tab.refresh()
        self.author_tab.refresh()


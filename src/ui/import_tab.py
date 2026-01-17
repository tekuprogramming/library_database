from tkinter import ttk, filedialog, messagebox
import csv, json, xml.etree.ElementTree as ET

from src.db.repositories.author_repository import AuthorRepository
from src.db.repositories.genre_repository import GenreRepository
from src.db.repositories.publisher_repository import PublisherRepository

class ImportTab(ttk.Frame):
    """
    UI tab for importing data into the library database.

    Supports:
    - Importing publishers from CSV
    - Importing authors from JSON
    - Importing genres from XML

    Uses the respective repositories for database operations:
    PublisherRepository, AuthorRepository, GenreRepository
    """
    def __init__(self, parent):
        """
        Initializes the Import tab and its UI components.

        :param parent: Parent widget (Notebook)
        """
        super().__init__(parent)
        # Repositories for each entity type
        self.publisher_repo = PublisherRepository()
        self.author_repo = AuthorRepository()
        self.genre_repo = GenreRepository()

        # Label for tab
        ttk.Label(self, text="Import data into tables").pack(anchor="w", padx=8, pady=8)

        # Buttons frame
        frame = ttk.Frame(self)
        frame.pack(fill="x", padx=8, pady=8)
        # Import buttons
        ttk.Button(frame, text="Import publishers (CSV)", command=self.import_publishers_csv).pack(side="left", padx=6)
        ttk.Button(frame, text="Import authors (JSON)", command=self.import_authors_json).pack(side="left", padx=6)
        ttk.Button(frame, text="Import genres (XML)", command=self.import_genres_xml).pack(side="left", padx=6)

    def import_publishers_csv(self):
        """
        Imports publishers from a CSV file safely.

        - Opens a file dialog for CSV selection.
        - Validates that required fields (name) are present.
        - Skips invalid rows without breaking the import.
        - Shows warnings for skipped rows and info when import completes.
        """
        path = filedialog.askopenfilename(title="Publisher CSV", filetypes=[("CSV", "*.csv")])
        if not path:
            return

        skipped_rows = []
        inserted_count = 0
        try:
            with open(path, newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                publishers = []
                for i, row in enumerate(reader, start=1):
                    # Strip whitespace from all fields
                    row = {k: (v.strip() if v else None) for k, v in row.items()}

                    # Check required field 'name'
                    if not row.get("name"):
                        skipped_rows.append(i)
                        continue  # skip this row entirely

                    publishers.append(row)

                # Insert valid rows
                if publishers:
                    self.publisher_repo.bulk_insert(publishers)
                    inserted_count = len(publishers)

            # Show results
            msg = f"CSV import completed.\nInserted {inserted_count} row(s)."
            if skipped_rows:
                msg += f"\nSkipped rows: {', '.join(map(str, skipped_rows))} (missing 'name')"
            messagebox.showinfo("Done", msg)

        except Exception as e:
            messagebox.showerror("CSV import error", str(e))

    def import_authors_json(self):
        """
        Imports authors from a JSON file.

        - Opens a file dialog for JSON selection
        - Loads JSON data
        - Calls AuthorRepository.bulk_insert() to insert records
        - Shows a messagebox on success or error
        """
        path = filedialog.askopenfilename(title="Author JSON", filetypes=[("JSON","*.json")])
        if not path: return
        try:
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
                self.author_repo.bulk_insert(data)
            messagebox.showinfo("Done","JSON import completed")
        except Exception as e:
            messagebox.showerror("JSON import error", str(e))

    def import_genres_xml(self):
        """
        Imports genres from an XML file.

        - Opens a file dialog for XML selection
        - Parses XML using ElementTree
        - Extracts <genre> elements and their 'name' attributes or text
        - Calls GenreRepository.bulk_insert() to insert records
        - Shows a messagebox on success or error
        """
        path = filedialog.askopenfilename(title="Genre XML", filetypes=[("XML","*.xml")])
        if not path: return
        try:
            tree = ET.parse(path)
            root = tree.getroot()
            # Create list of genre dictionaries for insertion
            genres = [{"name": g.get("name") or (g.text or "").strip()} for g in root.findall(".//genre")]
            self.genre_repo.bulk_insert(genres)
            messagebox.showinfo("Done","XML import completed")
        except Exception as e:
            messagebox.showerror("XML import error", str(e))


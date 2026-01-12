from tkinter import ttk, messagebox
import configparser
import logging

from src.config.config import CONFIG_PATH, config

# Load configuration from config.ini
config = configparser.ConfigParser()
config.read(CONFIG_PATH)

class SettingsTab(ttk.Frame):
    """
    UI tab for editing and saving database connection settings.

    Features:
    - Allows the user to view and edit ODBC driver, server, database, and connection options
    - Saves updated settings back to config.ini
    - Provides default values if the config file is missing entries
    """

    def __init__(self, parent):
        """
        Initializes the Settings tab and its UI components.

        :param parent: Parent widget (Notebook or Frame)
        """
        super().__init__(parent)
        # Header label
        ttk.Label(self, text="Connection settings").pack(anchor="w", padx=8, pady=8)

        # Frame for input fields
        frame = ttk.Frame(self)
        frame.pack(fill="x", padx=8, pady=8)

        # Create entry fields for each configuration option
        self.driver_e = ttk.Entry(frame, width=50); self._row(frame,0,"ODBC Driver",self.driver_e)
        self.server_e = ttk.Entry(frame, width=50); self._row(frame,1,"Server",self.server_e)
        self.db_e = ttk.Entry(frame, width=50); self._row(frame,2,"Database",self.db_e)
        self.tc_e = ttk.Entry(frame, width=50); self._row(frame,3,"Trusted Connection",self.tc_e)
        self.en_e = ttk.Entry(frame, width=50); self._row(frame,4,"Encrypt",self.en_e)
        self.tsc_e = ttk.Entry(frame, width=50); self._row(frame,5,"Trust Server Certificate",self.tsc_e)

        # Save button
        ttk.Button(self, text="Save to config.ini", command=self.save).pack(padx=8, pady=8)

        # Populate entry fields with current values from config (or default if missing)
        self.driver_e.insert(0, config.get("database","driver",fallback="ODBC Driver 18 for SQL Server"))
        self.server_e.insert(0, config.get("database","server",fallback="localhost\\SQLEXPRESS"))
        self.db_e.insert(0, config.get("database","database",fallback="library"))
        self.tc_e.insert(0, config.get("database","trusted_connection",fallback="yes"))
        self.en_e.insert(0, config.get("database","encrypt",fallback="yes"))
        self.tsc_e.insert(0, config.get("database","trust_server_certificate",fallback="yes"))

    def _row(self, frame, r, label, entry):
        """
        Helper method to create a labeled row in the settings form.

        :param frame: Parent frame
        :param r: Row index
        :param label: Label text
        :param entry: Entry widget to place
        """
        ttk.Label(frame, text=label).grid(row=r,column=0,sticky="w")
        entry.grid(row=r,column=1,sticky="we",padx=6,pady=4)
        frame.grid_columnconfigure(1, weight=1)

    def save(self):
        """
        Saves the current input values into config.ini.

        Steps:
        - Adds the [database] section if it doesn't exist
        - Writes each field value into the config
        - Saves the config to disk at CONFIG_PATH
        - Displays info message on success
        - Logs and shows error message if an exception occurs
        """
        try:
            if "database" not in config.sections():
                config.add_section("database")
            # Update config values from entry fields
            config.set("database","driver",self.driver_e.get())
            config.set("database","server",self.server_e.get())
            config.set("database","database",self.db_e.get())
            config.set("database","trusted_connection",self.tc_e.get())
            config.set("database","encrypt",self.en_e.get())
            config.set("database","trust_server_certificate",self.tsc_e.get())
            # Save to file
            with open(CONFIG_PATH,"w",encoding="utf-8") as f:
                config.write(f)
            messagebox.showinfo("Done","Settings were saved. Restart the application.")
        except Exception as e:
            logging.error(e)
            messagebox.showerror("Error while saving", str(e))
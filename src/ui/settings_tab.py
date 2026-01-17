from tkinter import ttk, messagebox
import configparser
import logging

from src.config.config import CONFIG_PATH

# Load configuration from config.ini
config = configparser.ConfigParser()
config.read(CONFIG_PATH)


class SettingsTab(ttk.Frame):
    """
    UI tab for editing and saving database connection settings.

    Uses SQL Authentication (username + password).
    """

    def __init__(self, parent):
        super().__init__(parent)

        ttk.Label(self, text="Connection settings").pack(anchor="w", padx=8, pady=8)

        frame = ttk.Frame(self)
        frame.pack(fill="x", padx=8, pady=8)

        # Database fields
        self.driver_e = ttk.Entry(frame, width=50)
        self._row(frame, 0, "ODBC Driver", self.driver_e)

        self.server_e = ttk.Entry(frame, width=50)
        self._row(frame, 1, "Server", self.server_e)

        self.db_e = ttk.Entry(frame, width=50)
        self._row(frame, 2, "Database", self.db_e)

        self.user_e = ttk.Entry(frame, width=50)
        self._row(frame, 3, "Username", self.user_e)

        self.pass_e = ttk.Entry(frame, width=50, show="*")
        self._row(frame, 4, "Password", self.pass_e)

        self.en_e = ttk.Entry(frame, width=50)
        self._row(frame, 5, "Encrypt", self.en_e)

        self.tsc_e = ttk.Entry(frame, width=50)
        self._row(frame, 6, "Trust Server Certificate", self.tsc_e)

        ttk.Button(self, text="Save to config.ini", command=self.save).pack(padx=8, pady=8)

        # Populate from config.ini
        self.driver_e.insert(0, config.get("database", "driver", fallback="ODBC Driver 18 for SQL Server"))
        self.server_e.insert(0, config.get("database", "server", fallback="localhost"))
        self.db_e.insert(0, config.get("database", "database", fallback="library"))
        self.user_e.insert(0, config.get("database", "username", fallback=""))
        self.pass_e.insert(0, config.get("database", "password", fallback=""))
        self.en_e.insert(0, config.get("database", "encrypt", fallback="no"))
        self.tsc_e.insert(0, config.get("database", "trust_server_certificate", fallback="yes"))

    def _row(self, frame, r, label, entry):
        ttk.Label(frame, text=label).grid(row=r, column=0, sticky="w")
        entry.grid(row=r, column=1, sticky="we", padx=6, pady=4)
        frame.grid_columnconfigure(1, weight=1)

    def save(self):
        try:
            required = {
                "driver": self.driver_e.get().strip(),
                "server": self.server_e.get().strip(),
                "database": self.db_e.get().strip(),
                "username": self.user_e.get().strip(),
                "password": self.pass_e.get().strip()
            }

            missing = [k for k, v in required.items() if not v]
            if missing:
                raise ValueError(f"Missing required field(s): {', '.join(missing)}")

            if "database" not in config:
                config.add_section("database")

            config.set("database", "driver", required["driver"])
            config.set("database", "server", required["server"])
            config.set("database", "database", required["database"])
            config.set("database", "username", required["username"])
            config.set("database", "password", required["password"])
            config.set("database", "encrypt", self.en_e.get().strip())
            config.set("database", "trust_server_certificate", self.tsc_e.get().strip())

            with open(CONFIG_PATH, "w", encoding="utf-8") as f:
                config.write(f)

            messagebox.showinfo("Done", "Settings saved. Restart the application.")

        except Exception as e:
            logging.error("Failed to save settings", exc_info=True)
            messagebox.showerror("Error", str(e))

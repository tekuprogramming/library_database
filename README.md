Library Database Application

Author: Milana Poljanskova
Contact: mila.p.06@seznam.cz
Date: 11.01.2026
School: SPŠE Ječná
Project type: School project - GUI database application (D1 – Repository Pattern)

1. Description

Library Database Application is a desktop application with a graphical interface
built using Python Tkinter. The application manages books, authors, publishers,
genres, and the relationships between them. It supports importing data, 
generating reports, configuring database connections, and managing M:N relationships
between books and authors.

2. Requirements

- Python 3.x
- Microsoft SQL Server (or any RDBMS supported by pyodbc)
- Python libraries:
    • pyodbc
    • tkinter
    • configparser
    • csv
    • json
    • xml.etree.ElementTree

3. Project structure

Project files are organized as follows:

/db                 - SQL script (database.sql)
/src                - Python source code
/src/config         - Configuration helpers
/src/data           - Test data for import (authors.json, genres.xml, publishers.csv)
/src/db             - Database repositories and connection helper (connection.py)
/src/ui             - User interface modules (tabs, dialogs)
/src/validation     - Validation functions
/config.ini         - Database configuration file
/main.py            - Application entry point
/README.md          - This documentation

4. Installation

1. Install Python 3.x if not already installed.
2. Install required Python libraries:
    pip install pyodbc
3. Ensure Microsoft SQL Server is installed and running.
4. Create a database user with appropriate permissions.
5. Run SQL script in `/db` to create the database schema and views:
    - database.sql
6. Import test data using the Import tab in the application:
    - authors.json
    - publishers.csv
    - genres.xml
    Afterwards run the inserts in the SQL script for the other tables.
7. Configure database connection in `config.ini` or in Settings tab:
    - driver
    - server
    - database
    - trusted_connection
    - encrypt
    - trust_server_certificate

5. Running the application

From the project root directory, run:

    python main.py

The application opens with tabs:
- Books
- Authors
- Import
- Report
- Settings

6. Usage

Books Tab:
- Add, edit, delete, and view books
- Assign authors to books
- Transfer authorship between authors (transaction)

Authors Tab:
- View and update authors

Import Tab:
- Import publishers (CSV), authors (JSON), genres (XML)

Report Tab:
- Generate report with aggregated data:
  number of books, average rating, active authors per publisher

Settings Tab:
- Configure database connection

7. Error handling

Error                   | Description                                    | Solution
------------------------|-----------------------------------------------|--------------------------------------------
Database connection      | Wrong credentials or server unavailable       | Check Settings or config.ini and ensure SQL Server is running
Configuration missing    | Missing 'database' section in config.ini     | Add 'database' section with required keys
Invalid input            | Rating out of range (0-5), wrong binding     | Correct the input to valid range or allowed options
Empty required fields    | Mandatory fields not filled (e.g., book name)| Fill all required fields before saving
Import error             | Invalid CSV, JSON, or XML format             | Correct the file format and re-import

8. Notes

- Transactions are used for operations affecting multiple tables (e.g., adding books,
  transferring authorship) to ensure data integrity.
- Views `vw_book_list` and `vw_publisher_report` provide easy access to aggregated data.
- All repository classes follow the Repository pattern (D1).

9. Test scenarios

See the `/src/data` directory for sample import files and `/test` for:
- Test scenario for application launch and database setup
- Test scenarios for functional testing, error handling, and data import

10. License / Credits

This project is a school assignment. All code and data were written by Milana Poljanskova.


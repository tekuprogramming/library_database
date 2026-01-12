from src.db.connection import get_connection

class AuthorRepository:
    """
    Repository class responsible for all database operations
    related to the 'author' table.

    This class encapsulates SQL queries and provides a clean
    interface for working with author data.
    """
    def get_all(self, active_only=False):
        """
        Returns a list of authors from the database.

        :param active_only: If True, only authors marked as active
                            (is_active = 1) are returned.
        :return: List of database rows (id, surname, name, email, is_active)
        """
        con = get_connection()
        cur = con.cursor()
        # Base SQL query
        sql = "select id, surname, name, email, is_active from author"
        # Optional filtering of active authors only
        if active_only:
            sql += " where is_active=1"
        # Sorting authors alphabetically
        sql += " order by surname, name"
        cur.execute(sql)
        rows = cur.fetchall()
        con.close()
        return rows

    def bulk_insert(self, authors):
        """
        Inserts multiple authors into the database in a single operation.

        This method is typically used for importing data
        (e.g. from JSON files).

        :param authors: List of dictionaries with author data.
                        Expected keys:
                        - surname
                        - name
                        - email
                        - is_active (optional, defaults to True)
        """
        con = get_connection()
        cur = con.cursor()
        try:
            # Insert each author separately within one transaction
            for a in authors:
                cur.execute(
                    "insert into author (surname, name, email, is_active) values (?, ?, ?, ?)",
                    (a.get("surname"), a.get("name"), a.get("email"), int(a.get("is_active", True)))
                )
            # Commit transaction if all inserts succeed
            con.commit()
        except Exception as e:
            # Rollback transaction on any error
            con.rollback()
            raise e
        finally:
            # Always close the database connection
            con.close()



from src.db.connection import get_connection

class GenreRepository:
    """
    Repository class responsible for database operations
    related to book genres (table: genre).
    """

    def bulk_insert(self, genres):
        """
        Inserts multiple genres into the database in a single transaction.

        This method is typically used for bulk imports
        (e.g. from CSV or external data sources).

        :param genres: Iterable of dictionaries containing genre data.
                       Expected key: "name"
        """
        con = get_connection()
        try:
            cur = con.cursor()
            for g in genres:
                cur.execute("insert into genre (name) values (?)", (g["name"],))
            con.commit()
        except Exception as e:
            # Roll back all inserts if any error occurs
            con.rollback()
            raise
        finally:
            # Roll back all inserts if any error occurs
            con.close()
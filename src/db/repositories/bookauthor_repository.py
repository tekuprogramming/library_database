from src.db.connection import get_connection

class BookAuthorRepository:
    """
    Repository class handling the many-to-many relationship
    between books and authors (table: book_author).

    The table uses a soft-delete mechanism via the `is_active` flag
    to preserve authorship history.
    """
    def fetch_active_authors(self, book_id):
        """
        Returns a list of active author IDs assigned to a specific book.

        :param book_id: ID of the book
        :return: List of author IDs
        """
        con = get_connection()
        try:
            cur = con.cursor()
            cur.execute("select author_id from book_author where book_id=? and is_active=1", (book_id,))
            rows = cur.fetchall()
            return [r[0] for r in rows]
        finally:
            con.close()

    def assign_authors(self, book_id, author_ids, overwrite=True):
        """
        Assigns authors to a book.

        If overwrite is True, all existing authors for the book
        are first deactivated. Existing relationships are reactivated
        instead of duplicated.

        :param book_id: ID of the book
        :param author_ids: List of author IDs to assign
        :param overwrite: Whether to replace existing assignments
        """
        con = get_connection()
        try:
            cur = con.cursor()
            # Deactivate all current authors if overwrite is enabled
            if overwrite:
                cur.execute("update book_author set is_active=0 where book_id=?", (book_id,))
            for aid in author_ids:
                # Check if relationship already exists
                cur.execute("select id from book_author where book_id=? and author_id=?", (book_id, aid))
                row = cur.fetchone()
                if row:
                    # Reactivate existing relationship
                    cur.execute("update book_author set is_active=1 where id=?", (row[0],))
                else:
                    # Create new relationship
                    cur.execute("insert into book_author (book_id, author_id, is_active) values (?,?,1)", (book_id, aid))
            con.commit()
        except Exception as e:
            con.rollback()
            raise e
        finally:
            con.close()

    def deactivate_authors(self, book_id):
        """
        Deactivates all author relationships for a given book.

        :param book_id: ID of the book
        """
        con = get_connection()
        try:
            cur = con.cursor()
            cur.execute("update book_author set is_active=0 where book_id=?", (book_id,))
            con.commit()
        except Exception as e:
            con.rollback()
            raise e
        finally:
            con.close()

    def deactivate_authors_for_author(self, book_id, author_id):
        """
        Deactivates authorship for a specific author-book pair.

        Used for transferring authorship from one author to another.

        :param book_id: ID of the book
        :param author_id: ID of the author to deactivate
        """
        con = get_connection()
        cur = con.cursor()
        try:
            cur.execute(
                "update book_author set is_active=0 where book_id=? and author_id=? and is_active=1",
                (book_id, author_id)
            )
            con.commit()
        finally:
            con.close()
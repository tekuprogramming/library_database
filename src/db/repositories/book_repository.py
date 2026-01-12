from src.db.connection import get_connection

class BookRepository:
    """
    Repository class responsible for all database operations
    related to the 'book' table.

    This class encapsulates SQL queries and provides
    a clear interface for working with book records.
    """
    def get_all(self):
        """
        Returns all books stored in the database.

        :return: List of database rows:
                 (id, name, publisher, publishment_date, rating, binding)
        """
        con = get_connection()
        cur = con.cursor()
        cur.execute("""
            select id, name, publisher, publishment_date, rating, binding
            from book
            order by name
        """)
        rows = cur.fetchall()
        con.close()
        return rows

    def fetch_by_id(self, book_id):
        """
        Fetches a single book by its ID.

        :param book_id: ID of the book to fetch
        :return: One database row or None if not found
        """
        con = get_connection()
        cur = con.cursor()
        cur.execute("""
            select id, name, publisher, publishment_date, rating, binding
            from book
            where id=?
        """, (book_id,))
        row = cur.fetchone()
        con.close()
        return row

    def insert(self, name, publisher_id, publishment_date, rating, binding):
        """
        Inserts a new book into the database.

        The database-generated ID of the new book is returned.

        :param name: Book title
        :param publisher_id: Foreign key to publisher table
        :param publishment_date: Publication date (YYYY-MM-DD or None)
        :param rating: Book rating (float or None)
        :param binding: Type of binding (hardcover, paperback, ebook)
        :return: ID of the newly created book
        """
        con = get_connection()
        cur = con.cursor()
        cur.execute("""
            insert into book (name, publisher, publishment_date, rating, binding)
            output inserted.id
            values (?, ?, ?, ?, ?)
        """, (name, publisher_id, publishment_date, rating, binding))
        book_id = cur.fetchone()[0]
        con.commit()
        con.close()
        return book_id

    def update(self, book_id, name, publisher_id, publishment_date, rating, binding):
        """
        Updates an existing book record.

        :param book_id: ID of the book to update
        :param name: Updated book title
        :param publisher_id: Updated publisher ID
        :param publishment_date: Updated publishment date
        :param rating: Updated rating
        :param binding: Updated binding type
        """
        con = get_connection()
        cur = con.cursor()
        cur.execute("""
            update book
            set name=?, publisher=?, publishment_date=?, rating=?, binding=?
            where id=?
        """, (name, publisher_id, publishment_date, rating, binding, book_id))
        con.commit()
        con.close()

    def delete(self, book_id):
        """
        Deletes a book from the database.

        Related records in the book_author table
        are removed first to maintain referential integrity.

        :param book_id: ID of the book to delete
        """
        con = get_connection()
        cur = con.cursor()
        # Remove relations between book and authors
        cur.execute("delete from book_author where book_id=?", (book_id,))
        # Remove the book itself
        cur.execute("delete from book where id=?", (book_id,))
        con.commit()
        con.close()

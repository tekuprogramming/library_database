from src.db.connection import get_connection

class PublisherRepository:
    """
    Repository class responsible for all database operations
    related to publishers (table: publisher).
    """
    def fetch_all(self):
        """
        Fetches all publishers from the database.

        :return: List of database rows containing publisher data.
        """
        con = get_connection()
        try:
            cur = con.cursor()
            cur.execute("select id, name, address, phone_number, email, website from publisher order_by name")
            rows = cur.fetchall()
            cur.close()
            con.commit()
            return rows
        finally:
            # Ensure the database connection is always closed
            con.close()

    def fetch_by_id(self, publisher_id: int):
        """
        Fetches a single publisher by its ID.

        :param publisher_id: ID of the publisher
        :return: Database row with publisher data or None if not found
        """
        con = get_connection()
        try:
            cur = con.cursor()
            cur.execute("select id, name, address, phone_number, email, website from publisher where id=?", (publisher_id,))
            row = cur.fetchone()
            cur.close()
            con.commit()
            return row
        finally:
            con.close()

    def insert(self, name: str, address: str = None, phone: str = None, email: str = None, website: str = None):
        """
        Inserts a new publisher into the database.

        :param name: Publisher name (required)
        :param address: Publisher address (optional)
        :param phone: Phone number (optional)
        :param email: Email address (optional)
        :param website: Website URL (optional)
        :return: ID of the newly created publisher
        """
        con = get_connection()
        try:
            cur = con.cursor()
            cur.execute(
                "insert into publisher (name, address, phone_number, email, website) values (?, ?, ?, ?, ?)",
                (name, address, phone, email, website)
            )
            con.commit()
            # Retrieve ID of the inserted record
            cur.execute("select @@identity")
            publisher_id = cur.fetchone()[0]
            return publisher_id
        finally:
            con.close()

    def update(self, publisher_id: int, name: str, address: str = None, phone: str = None, email: str = None, website: str = None):
        """
        Updates an existing publisher.

        :param publisher_id: ID of the publisher to update
        :param name: New publisher name
        :param address: New address (optional)
        :param phone: New phone number (optional)
        :param email: New email address (optional)
        :param website: New website URL (optional)
        """
        con = get_connection()
        try:
            cur = con.cursor()
            cur.execute(
                "update publisher set name=?, address=?, phone_number=?, email=?, website=? where id=?",
                (name, address, phone, email, website, publisher_id)
            )
            con.commit()
        finally:
            con.close()

    def delete(self, publisher_id: int):
        """
        Deletes a publisher from the database.

        :param publisher_id: ID of the publisher to delete
        """
        con = get_connection()
        try:
            cur = con.cursor()
            cur.execute("delete from publisher where id=?", (publisher_id,))
            con.commit()
        finally:
            con.close()

    def bulk_insert(self, publishers):
        """
        Inserts multiple publishers in a single transaction.

        Used mainly for bulk imports (e.g. CSV files).

        :param publishers: Iterable of dictionaries with publisher data.
        """
        con = get_connection()
        cur = con.cursor()
        try:
            for p in publishers:
                cur.execute(
                    "insert into publisher (name, address, phone_number, email, website) values (?, ?, ?, ?, ?)",
                    (p.get("name"), p.get("address"), p.get("phone_number"), p.get("email"), p.get("website"))
                )
            con.commit()
        except Exception as e:
            # Roll back all inserts if any error occurs
            con.rollback()
            raise e
        finally:
            con.close()
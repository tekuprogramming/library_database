from src.db.connection import get_connection

class ReportRepository:
    """
    Repository class responsible for generating read-only reports
    based on aggregated database data.
    """

    def get_publisher_report(self):
        """
        Generates an aggregated report per publisher.

        The report includes:
        - Publisher name
        - Number of books published
        - Average book rating
        - Number of active authors associated with the publisher

        Data is calculated using Common Table Expressions (CTEs)
        for clarity and performance.

        :return: List of database rows with report data
        """
        sql = """
            -- Count books and average rating per publisher
            with publisher_books as (
                select p.id as publisher_id, p.name as publisher_name, 
                       count(b.id) as books_count, avg(b.rating) as avg_rating
                from publisher p
                left join book b on b.publisher = p.id
                group by p.id, p.name
            ),
            -- Count distinct active authors per publisher
            publisher_authors as (
                select p.id as publisher_id, count(distinct a.id) as active_authors
                from publisher p
                left join book b on b.publisher = p.id
                left join book_author ba on ba.book_id = b.id and ba.is_active=1
                left join author a on a.id = ba.author_id
                group by p.id
            )
            -- Final report combining both aggregations
            select pb.publisher_name, pb.books_count, pb.avg_rating, pa.active_authors
            from publisher_books pb
            left join publisher_authors pa on pa.publisher_id = pb.publisher_id
            order by pb.publisher_name
        """
        con = get_connection()
        try:
            cur = con.cursor()
            cur.execute(sql)
            rows = cur.fetchall()
            return rows
        finally:
            # Ensure the database connection is always closed
            con.close()
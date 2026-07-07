import sqlite3


class JobDatabase:

    def __init__(self):

        self.connection = sqlite3.connect(
            "jobs.db"
        )

        self.create_table()


    def create_table(self):

        cursor = self.connection.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS jobs (

                id INTEGER PRIMARY KEY AUTOINCREMENT,

                title TEXT NOT NULL,

                company TEXT,

                url TEXT,

                location TEXT,

                source TEXT,

                match_score INTEGER,

                status TEXT,

                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

            )
        """)

        self.connection.commit()


    def save(self, job, score):

        cursor = self.connection.cursor()

        cursor.execute("""
            INSERT INTO jobs
            (
                title,
                company,
                url,
                location,
                source,
                match_score,
                status
            )

            VALUES (?, ?, ?, ?, ?, ?, ?)

        """,

        (
            job.title,
            job.company,
            job.url,
            job.location,
            job.source,
            score,
            "NEW"
        ))

        self.connection.commit()


    def list_jobs(self):

        cursor = self.connection.cursor()

        cursor.execute(
            "SELECT * FROM jobs ORDER BY match_score DESC"
        )

        return cursor.fetchall()
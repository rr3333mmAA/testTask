# TODO: Check if the database and tables exists before creating it

import psycopg2
from os import getenv

from dotenv import load_dotenv


class Database:
    conn = None
    cur = None

    @classmethod
    def __init__(cls, db_name: str):
        try:
            cls.conn = psycopg2.connect(
                database=db_name.lower(),
                user=getenv("DB_USER"),
                password=getenv("DB_PASSWORD")
            )
            cls.conn.autocommit = True
            cls.cur = cls.conn.cursor()
        except psycopg2.OperationalError as e:
            print(f"Database error: {e}")

    @classmethod
    def create_tables(cls):
        """
        This method creates category and catalog tables in the database
        """
        try:
            # Create category table
            cls.cur.execute("""
                CREATE TABLE category (
                    subcategory varchar PRIMARY KEY,
                    category varchar
                );
            """)

            # Create catalog table
            cls.cur.execute("""
                CREATE TABLE catalog (
                    id serial PRIMARY KEY,
                    amount integer,
                    description varchar,
                    img_path varchar,
                    subcategory varchar,
                    FOREIGN KEY (subcategory) REFERENCES category (subcategory)
                );
            """)

            # Print success message
            print("Tables created successfully")
        except psycopg2.OperationalError as e:
            print(f"Database error: {e}")

    @classmethod
    def close(cls):
        """
        This method closes cursor and connection
        """
        cls.cur.close()
        cls.conn.close()

        # Print success message
        print("Database connection closed")


def init_db(db_name: str):
    try:
        # Connect to an existing database
        load_dotenv()
        conn = psycopg2.connect(
            database="postgres",
            user=getenv("DB_USER"),
            password=getenv("DB_PASSWORD")
        )
        conn.autocommit = True

        # Open a cursor to perform database operations
        cur = conn.cursor()

        # Execute a command: this creates a new database
        cur.execute(f"CREATE DATABASE {db_name};")

        # Close cursor and connection
        cur.close()
        conn.close()

        # Print success message
        print(f"Database {db_name} created successfully")

        Database(db_name)
    except psycopg2.OperationalError as e:
        print(f"Database error: {e}")

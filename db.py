import psycopg2
import json
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
            # Check if the tables exists in the current database
            exists = []
            for table in ["category", "catalog"]:
                cls.cur.execute(f"""
                    SELECT EXISTS (
                        SELECT 1
                        FROM information_schema.tables 
                        WHERE table_name = '{table}'
                    );
                """)
                exists.append(cls.cur.fetchone()[0])

            if not any(exists):
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
                        product varchar,
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

    @classmethod
    def load_starter_catalog(cls):
        """
        This method loads starter catalog data into the database
        """
        try:
            json_catalog = json.load(open("starter_catalog.json"))
            categories = {}
            products = {}

            for category in json_catalog:
                categories[category] = []
                for subcategory in json_catalog[category]:
                    categories[category].append(subcategory)
                    products[subcategory] = json_catalog[category][subcategory]

            # Insert categories into the category table
            for category in categories:
                for subcategory in categories[category]:
                    cls.cur.execute(f"INSERT INTO category (subcategory, category) VALUES ('{subcategory}', '{category}');")

            # Insert products into the catalog table
            for subcategory in products:
                for product in products[subcategory]:
                    cls.cur.execute(f"INSERT INTO catalog (product, amount, description, img_path, subcategory) VALUES ('{product}', {products[subcategory][product]['amount']}, '{products[subcategory][product]['description']}', '{products[subcategory][product]['img_path']}', '{subcategory}');")

            # Print success message
            print("Starter catalog loaded successfully")
        except psycopg2.OperationalError as e:
            print(f"Database error: {e}")

    @classmethod
    def get_categories(cls):
        """
        This method returns all categories from the category table
        """
        try:
            cls.cur.execute("SELECT DISTINCT category FROM category;")
            return [i[0] for i in cls.cur.fetchall()]
        except psycopg2.OperationalError as e:
            print(f"Database error: {e}")

    @classmethod
    def get_subcategories(cls, category: str):
        """
        This method returns all subcategories from the category table
        """
        try:
            cls.cur.execute(f"SELECT subcategory FROM category WHERE category = '{category}';")
            return [i[0] for i in cls.cur.fetchall()]
        except psycopg2.OperationalError as e:
            print(f"Database error: {e}")

    @classmethod
    def get_products(cls, subcategory: str):
        """
        This method returns all products from the catalog table
        """
        try:
            cls.cur.execute(f"SELECT product, amount, description, img_path FROM catalog WHERE subcategory = '{subcategory}';")
            return cls.cur.fetchall()
        except psycopg2.OperationalError as e:
            print(f"Database error: {e}")

    @classmethod
    def get_product(cls, product: str):
        """
        This method returns product from the catalog table
        """
        try:
            cls.cur.execute(f"SELECT product, amount, description, img_path FROM catalog WHERE product = '{product}';")
            return cls.cur.fetchone()
        except psycopg2.OperationalError as e:
            print(f"Database error: {e}")


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

        # Check if the database exists
        cur.execute(f"SELECT 1 FROM pg_database WHERE datname = '{db_name}';")
        exists = cur.fetchone()

        # Create a new database
        if not exists:
            cur.execute(f"CREATE DATABASE {db_name};")

            # Print success message
            print(f"Database {db_name} created successfully")

        # Close cursor and connection
        cur.close()
        conn.close()

        # Initialize Database
        Database(db_name)
    except psycopg2.OperationalError as e:
        print(f"Database error: {e}")
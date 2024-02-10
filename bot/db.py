from os import getenv

import psycopg2
import json

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
            for table in ["category", "catalog", "users", "cart"]:
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
                        quantity integer,
                        description varchar,
                        img_path varchar,
                        subcategory varchar,
                        price integer,
                        FOREIGN KEY (subcategory) REFERENCES category (subcategory)
                    );
                """)

                # Create users table
                cls.cur.execute("""
                    CREATE TABLE users (
                        id serial PRIMARY KEY,
                        user_tgid integer,
                        address varchar
                    );
                """)

                # Create cart table
                cls.cur.execute("""
                    CREATE TABLE cart (
                        id serial PRIMARY KEY,
                        user_tgid integer,
                        product varchar,
                        quantity integer,
                        amount integer
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
                    cls.cur.execute(f"INSERT INTO catalog (product, quantity, description, img_path, subcategory, price) VALUES ('{product}', {products[subcategory][product]['quantity']}, '{products[subcategory][product]['description']}', '{products[subcategory][product]['img_path']}', '{subcategory}', '{products[subcategory][product]['price']}');")

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
            cls.cur.execute(f"SELECT product, quantity, description, img_path FROM catalog WHERE subcategory = '{subcategory}';")
            return cls.cur.fetchall()
        except psycopg2.OperationalError as e:
            print(f"Database error: {e}")

    @classmethod
    def get_product(cls, product: str):
        """
        This method returns product from the catalog table
        """
        try:
            cls.cur.execute(f"SELECT product, quantity, description, img_path, price FROM catalog WHERE product = '{product}';")
            return cls.cur.fetchone()
        except psycopg2.OperationalError as e:
            print(f"Database error: {e}")

    @classmethod
    def add_user(cls, user_tgid: int):
        """
        This method adds user to the users table
        """
        try:
            # Check if the user exists in the users table
            cls.cur.execute(f"SELECT 1 FROM users WHERE user_tgid = {user_tgid};")
            exists = cls.cur.fetchone()
            if not exists:
                # Add user to the users table
                cls.cur.execute(f"INSERT INTO users (user_tgid, address) VALUES ({user_tgid}, 'uknown');")
        except psycopg2.OperationalError as e:
            print(f"Database error: {e}")

    @classmethod
    def get_cart_products(cls, user_tgid: int):
        """
        This method returns all products from the cart table
        """
        try:
            cls.cur.execute(f"SELECT product, SUM(quantity) AS total_quantity FROM cart WHERE user_tgid = {user_tgid} GROUP BY product;")
            return cls.cur.fetchall()
        except psycopg2.OperationalError as e:
            print(f"Database error: {e}")

    @classmethod
    def check_quantity(cls, product: str, quantity: int):
        """
        This method checks if the quantity of product is available
        """
        try:
            cls.cur.execute(f"SELECT quantity FROM catalog WHERE product = '{product}';")
            product_quantity = cls.cur.fetchone()[0]
            return product_quantity >= quantity
        except psycopg2.OperationalError as e:
            print(f"Database error: {e}")

    @classmethod
    def add_to_cart(cls, user_tgid: int, product: str, quantity: int, price: int):
        """
        This method adds product to the cart table
        """
        try:
            cls.cur.execute(f"INSERT INTO cart (user_tgid, product, quantity, amount) VALUES ({user_tgid}, '{product}', {quantity}, {quantity*price});")
        except psycopg2.OperationalError as e:
            print(f"Database error: {e}")

    @classmethod
    def delete_product(cls, user_tgid: int, product: str):
        """
        This method deletes product from the cart table
        """
        try:
            cls.cur.execute(f"DELETE FROM cart WHERE user_tgid = {user_tgid} AND product = '{product}';")
        except psycopg2.OperationalError as e:
            print(f"Database error: {e}")

    @classmethod
    def change_address(cls, user_tgid: int, address: str):
        """
        This method changes user's address in the users table
        """
        try:
            cls.cur.execute(f"UPDATE users SET address = '{address}' WHERE user_tgid = {user_tgid};")
        except psycopg2.OperationalError as e:
            print(f"Database error: {e}")

    @classmethod
    def get_user_amount(cls, user_tgid: int):
        """
        This method returns user's amount from the cart table
        """
        try:
            cls.cur.execute(f"SELECT SUM(amount) FROM cart WHERE user_tgid = {user_tgid};")
            return cls.cur.fetchone()[0]
        except psycopg2.OperationalError as e:
            print(f"Database error: {e}")

    @classmethod
    def clear_cart(cls, user_tgid: int):
        """
        This method clears user's cart in the cart table
        """
        try:
            cls.cur.execute(f"DELETE FROM cart WHERE user_tgid = {user_tgid};")
        except psycopg2.OperationalError as e:
            print(f"Database error: {e}")

    @classmethod
    def update_quantity(cls, user_tgid: int):
        """
        This method updates product's quantity in the catalog table by user's order
        """
        try:
            cls.cur.execute(f"SELECT product, quantity FROM cart WHERE user_tgid = {user_tgid};")
            products = cls.cur.fetchall()
            for product in products:
                cls.cur.execute(f"UPDATE catalog SET quantity = quantity - {product[1]} WHERE product = '{product[0]}';")
        except psycopg2.OperationalError as e:
            print(f"Database error: {e}")

    @classmethod
    def get_user_address(cls, user_tgid: int):
        """
        This method returns user's address from the users table
        """
        try:
            cls.cur.execute(f"SELECT address FROM users WHERE user_tgid = {user_tgid};")
            return cls.cur.fetchone()[0]
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

from os import getenv

import psycopg2
import json

from time import sleep
from dotenv import load_dotenv


class Database:
    conn = None
    cur = None

    @classmethod
    def __init__(cls, db_name: str):
        try:
            cls.conn = psycopg2.connect(
                database=db_name.lower(),
                user=getenv("POSTGRES_USER"),
                password=getenv("POSTGRES_PASSWORD"),
                host=getenv("POSTGRES_HOST")
            )
            cls.conn.autocommit = True
            cls.cur = cls.conn.cursor()
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
        sleep(5)
        try:
            json_catalog = json.load(open("starter_catalog.json"))
            if not json_catalog["init"]:
                categories = {}
                products = {}

                for category in json_catalog:
                    if category != "init":
                        categories[category] = []
                        for subcategory in json_catalog[category]:
                            categories[category].append(subcategory)
                            products[subcategory] = json_catalog[category][subcategory]

                # Insert categories into the category table
                for category in categories:
                    for subcategory in categories[category]:
                        cls.cur.execute(
                            f"INSERT INTO category (subcategory, category) VALUES ('{subcategory}', '{category}');"
                        )

                # Insert products into the catalog table
                for subcategory in products:
                    for product in products[subcategory]:
                        cls.cur.execute(
                            f"INSERT INTO catalog (product, quantity, description, img_path, subcategory, price) "
                            f"VALUES ("
                            f"'{product}',"
                            f" {products[subcategory][product]['quantity']},"
                            f" '{products[subcategory][product]['description']}',"
                            f" '{products[subcategory][product]['img_path']}',"
                            f" '{subcategory}',"
                            f" '{products[subcategory][product]['price']}'"
                            f");"
                        )

                # Update json_catalog["init"] to True
                json_catalog["init"] = True
                with open("starter_catalog.json", "w", encoding='utf8') as file:
                    json.dump(json_catalog, file, indent=4, ensure_ascii=False)

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
            cls.cur.execute(
                f"SELECT product, quantity, description, img_path FROM catalog WHERE subcategory = '{subcategory}';"
            )
            return cls.cur.fetchall()
        except psycopg2.OperationalError as e:
            print(f"Database error: {e}")

    @classmethod
    def get_product(cls, product: str):
        """
        This method returns product from the catalog table
        """
        try:
            cls.cur.execute(
                f"SELECT product, quantity, description, img_path, price FROM catalog WHERE product = '{product}';"
            )
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
            cls.cur.execute(
                f"SELECT product, SUM(quantity) AS total_quantity "
                f"FROM cart WHERE user_tgid = {user_tgid} GROUP BY product;"
            )
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
            cls.cur.execute(
                f"INSERT INTO cart (user_tgid, product, quantity, amount) "
                f"VALUES ({user_tgid}, '{product}', {quantity}, {quantity*price});"
            )
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
                cls.cur.execute(
                    f"UPDATE catalog SET quantity = quantity - {product[1]} WHERE product = '{product[0]}';"
                )
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

    @classmethod
    def get_img_path(cls, product: str):
        """
        This method returns product's img_path from the catalog table
        """
        try:
            cls.cur.execute(f"SELECT img_path FROM catalog WHERE product = '{product}';")
            return cls.cur.fetchone()[0]
        except psycopg2.OperationalError as e:
            print(f"Database error: {e}")


def init_db(db_name: str):
    try:
        # Connect to an existing database
        load_dotenv()
        conn = psycopg2.connect(
            database="postgres",
            user=getenv("POSTGRES_USER"),
            password=getenv("POSTGRES_PASSWORD"),
            host=getenv("POSTGRES_HOST")
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

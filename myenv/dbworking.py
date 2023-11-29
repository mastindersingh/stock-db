import psycopg2
import pandas as pd
from werkzeug.security import generate_password_hash, check_password_hash

def get_db_connection():
    return psycopg2.connect(
        host="ep-royal-thunder-45099107.us-east-1.postgres.vercel-storage.com",
        database="verceldb",
        user="default",
        password="QhYas0zXyE7A",
        port="5432"
    )

def read_stock_purchases():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT ticker, buy_date, buy_price, quantity FROM stock_purchases")
    stock_purchases = cursor.fetchall()
    conn.close()
    return pd.DataFrame(stock_purchases, columns=['Ticker', 'BuyDate', 'BuyPrice', 'Quantity'])

def write_stock_purchases(new_data):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        for _, row in new_data.iterrows():
            print(f"Inserting: {row['Ticker']}, {row['BuyDate']}, {row['BuyPrice']}, {row['Quantity']}")  # Debug print
            cursor.execute(
                "INSERT INTO stock_purchases (ticker, buy_date, buy_price, quantity) VALUES (%s, %s, %s, %s)",
                (row['Ticker'], row['BuyDate'], row['BuyPrice'], row['Quantity'])
            )
        conn.commit()
    except psycopg2.Error as e:
        print(f"Database error: {e}")  # Debug print
    finally:
        conn.close()


def create_user(email, password):
    conn = get_db_connection()
    cursor = conn.cursor()
    hashed_password = generate_password_hash(password)
    try:
        cursor.execute("INSERT INTO users (email, password) VALUES (%s, %s)", (email, hashed_password))
        conn.commit()
    except psycopg2.Error as e:
        print(f"Database error: {e}")
    finally:
        conn.close()

def verify_user(email, password):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT password FROM users WHERE email = %s", (email,))
    user_record = cursor.fetchone()
    conn.close()
    if user_record:
        return check_password_hash(user_record[0], password)
    return False

# Function to add a stock to a user's portfolio
def add_stock_to_user(user_id, stock_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO user_stocks (user_id, stock_id) VALUES (%s, %s)", (user_id, stock_id))
        conn.commit()
    except psycopg2.Error as e:
        print(f"Database error: {e}")
    finally:
        conn.close()

# Function to get a user's stocks
def get_user_stocks(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM user_stocks WHERE user_id = %s", (user_id,))
    stocks = cursor.fetchall()
    conn.close()
    return stocks


def check_user(email, password):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT password FROM users WHERE email = %s", (email,))
        user_record = cursor.fetchone()
        if user_record and check_password_hash(user_record[0], password):
            return True
        else:
            return False
    except psycopg2.Error as e:
        print(f"Database error: {e}")
        return False
    finally:
        conn.close()


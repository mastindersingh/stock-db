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

def read_stock_purchases(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT s.ticker, sp.buy_date, sp.buy_price, sp.quantity 
        FROM stock_purchases sp
        JOIN stocks s ON sp.stock_id = s.id
        WHERE sp.user_id = %s
    """, (user_id,))
    stock_purchases = cursor.fetchall()
    conn.close()
    return pd.DataFrame(stock_purchases, columns=['Ticker', 'BuyDate', 'BuyPrice', 'Quantity'])


def write_stock_purchases(user_id, new_data):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        for _, row in new_data.iterrows():
            ticker = row['Ticker']
            # Check if the stock ticker exists
            cursor.execute("SELECT id FROM stocks WHERE ticker = %s", (ticker,))
            result = cursor.fetchone()

            if result:
                stock_id = result[0]
            else:
                # Insert new stock ticker
                cursor.execute("INSERT INTO stocks (ticker) VALUES (%s) RETURNING id", (ticker,))
                stock_id = cursor.fetchone()[0]

            # Now insert into stock_purchases with the stock_id
            cursor.execute(
                "INSERT INTO stock_purchases (user_id, stock_id, buy_date, buy_price, quantity) VALUES (%s, %s, %s, %s, %s)",
                (user_id, stock_id, row['BuyDate'], row['BuyPrice'], row['Quantity'])
            )
        conn.commit()
    except psycopg2.Error as e:
        print(f"Database error: {e}")
    finally:
        conn.close()







def get_user_id(email):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
        result = cursor.fetchone()
        return result[0] if result else None
    except Exception as e:
        print(f"Error in get_user_id: {e}")
        return None
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

def get_user_stocks(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT s.id, s.ticker, COALESCE(SUM(sp.quantity), 0) as total_quantity
            FROM user_stocks us
            JOIN stocks s ON us.stock_id = s.id
            LEFT JOIN stock_purchases sp ON s.id = sp.stock_id AND sp.user_id = us.user_id
            WHERE us.user_id = %s
            GROUP BY s.id
        """, (user_id,))
        stocks = cursor.fetchall()
        return stocks
    except psycopg2.Error as e:
        print(f"Database error: {e}")
    finally:
        conn.close()



def get_master_user_stocks():
    master_email = 'mastinder@yahoo.com'
    master_user_id = get_user_id(master_email)
    return get_user_stocks(master_user_id) if master_user_id else []


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


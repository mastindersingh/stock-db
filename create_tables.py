import psycopg2
from psycopg2 import sql

def get_db_connection():
    return psycopg2.connect(
        host="ep-royal-thunder-45099107.us-east-1.postgres.vercel-storage.com",
        database="verceldb",
        user="default",
        password="QhYas0zXyE7A",
        port="5432"
    )

def create_tables():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                email VARCHAR(120) UNIQUE NOT NULL,
                password VARCHAR(60) NOT NULL
            );
            CREATE TABLE IF NOT EXISTS stock_purchases (
                id SERIAL PRIMARY KEY,
                ticker VARCHAR(10) NOT NULL,
                buy_date DATE NOT NULL,
                buy_price NUMERIC NOT NULL,
                quantity INTEGER NOT NULL
            );
        """)
        conn.commit()
        print("Tables created successfully.")
    except psycopg2.Error as e:
        print(f"Error creating tables: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    create_tables()


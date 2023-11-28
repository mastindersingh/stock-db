import psycopg2
from werkzeug.security import generate_password_hash

def get_db_connection():
    return psycopg2.connect(
        host="ep-royal-thunder-45099107.us-east-1.postgres.vercel-storage.com",
        database="verceldb",
        user="default",
        password="QhYas0zXyE7A",
        port="5432"
    )

def create_user(email, password):
    conn = get_db_connection()
    cursor = conn.cursor()
    hashed_password = generate_password_hash(password)
    try:
        cursor.execute("INSERT INTO users (email, password) VALUES (%s, %s)", (email, hashed_password))
        conn.commit()
        print("User created successfully.")
    except psycopg2.Error as e:
        print(f"Database error: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    email = input("Enter email: ")
    password = input("Enter password: ")
    create_user(email, password)


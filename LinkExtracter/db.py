import psycopg2

def setup_database():
    try:
        conn = psycopg2.connect(
            dbname="LinkExtracter",
            user="postgres",
            password="Rushi@1826",
            host="localhost"
        )
        print("Database connection established successfully.")
        cursor = conn.cursor()
        # Create table if not exists
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS links (
                id SERIAL PRIMARY KEY,
                url TEXT NOT NULL,
                crawl_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        print("Table 'links' created successfully (if it didn't exist).")
        return conn
    except psycopg2.Error as e:
        print("Error while connecting to PostgreSQL or creating table:", e)
        return None

def get_database_cursor(conn):
    if conn:
        try:
            return conn.cursor()
        except psycopg2.Error as e:
            print("Error while creating a cursor:", e)
            return None
    else:
        print("No database connection available.")
        return None

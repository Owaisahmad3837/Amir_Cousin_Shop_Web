import psycopg2
from config import Config

def get_conn():
    try:
        conn = psycopg2.connect(Config.DATABASE_URL)
        return conn
    except Exception as e:
        print("Database connection error:", e)
        return None
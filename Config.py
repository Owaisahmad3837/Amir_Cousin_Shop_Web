import psycopg2

def get_conn():
    try:
        conn = psycopg2.connect(
            host="localhost",
            user="owais",
            password="owais7383",
            database="Amir_Shop"
        )
        return conn
    except Exception as e:
        print("Connection failed:", e)
        return None
    
    
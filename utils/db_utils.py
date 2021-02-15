import psycopg2, db_auth
from psycopg2 import sql


connection = None
cursor = None


def open_db_connection():
    global connection, cursor
    try:
        connection = psycopg2.connect(
            f"dbname='{db_auth.name}' user='{db_auth.name}' host='{db_auth.host}' password='{db_auth.password}'")
        cursor = connection.cursor()
    except (Exception, psycopg2.Error) as error:
        print("Error while connecting to PostgreSQL", error)


def close_db_connection():
    # closing database connection.
    if connection:
        cursor.close()
        connection.close()
        print("PostgreSQL connection is closed")

def execute_query(query, data):
    open_db_connection()

    cursor.execute(query, data)
    connection.commit()

    close_db_connection()
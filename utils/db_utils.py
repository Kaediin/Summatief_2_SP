import psycopg2, db_auth

connection = None
cursor = None


def open_db_connection():
    global connection, cursor
    try:
        connection = db_auth.getPostgreSQLConnection(psycopg2)
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
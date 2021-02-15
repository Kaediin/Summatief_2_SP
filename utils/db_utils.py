import psycopg2
import utils.db_auth

connection = None
cursor = None


def open_db_connection():
    global connection, cursor
    try:
        connection = utils.db_auth.getPostgreSQLConnection(psycopg2)
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


def fill_products_db(products):
    open_db_connection()
    for product in products:
        try:
            id = product['_id']
            brand = product['brand']
            category = product['category']
            color = product['color']
            deeplink = product['deeplink']
            description = product['description']
            fast_mover = product['fast_mover']
            flavor = product['flavor']
            gender = product['gender']
            herhaalaankopen = product['herhaalaankopen']
            name = product['name']
            predict_out_of_stock_date = product['predict_out_of_stock_date']
            recommendable = product['recommendable']
            size = product['size']
        except:
            print(product)

        try:
            cursor.execute("insert into products (id, brand, category, color, deeplink, description, fast_mover, flavor, gender, herhaalaankopen, name, predict_out_of_stock_date, recommendable, size) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                            "",(id, brand, category, color, deeplink, description,fast_mover, flavor, gender, herhaalaankopen, name, predict_out_of_stock_date, recommendable, size))
        except:
            print(product)
    connection.commit()
    close_db_connection()

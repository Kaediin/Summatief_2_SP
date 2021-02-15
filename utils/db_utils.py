import psycopg2
import utils.db_auth

connection = None
cursor = None


def open_db_connection():
    global connection, cursor
    try:
        connection = utils.db_auth.getPostgreSQLConnection(psycopg2)
        cursor = connection.cursor()
        print("PostgreSQL connection is open")
    except (Exception, psycopg2.Error) as error:
        print("Error while connecting to PostgreSQL", error)


def close_db_connection():
    # closing database connection.
    if connection:
        connection.commit()
        cursor.close()
        connection.close()
        print("PostgreSQL connection is closed")



def fill_db(products):
    open_db_connection()
    for product in products:

        try:
            cursor.execute("insert into products (id, brand, category, color, deeplink, description, fast_mover, flavor, gender, herhaalaankopen, name, predict_out_of_stock_date, recommendable, size) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                            "",(product['_id'], product['brand'], product['category'], product['color'], product['deeplink'], product['description'],product['flavor'], product['flavor'],
                                product['gender'], product['herhaalaankopen'], product['name'], product['predict_out_of_stock_date'], product['recommendable'], product['size']))

        except:
            pass

        try:
            cursor.execute("insert into prices (id, discount, mrsp, selling_price) values (%s, %s, %s, %s)",
                           (product['_id'], product['price']['discount'], product['price']['mrsp'], product['price']['selling_price']))
        except:
            pass

    close_db_connection()


def create_tables():
    open_db_connection()
    cursor.execute("CREATE TABLE prices (id varchar,discount float,mrsp float,selling_price float)")
    cursor.execute("CREATE TABLE products (id varchar,brand varchar, category varchar, color varchar,"
                   "deeplink varchar, description varchar, fast_mover boolean, flavor varchar, gender varchar,"
                   " herhaalaankopen boolean, name varchar, predict_out_of_stock_date date, recommendable boolean, size varchar)")
    cursor.execute("CREATE TABLE categories (id varchar, category varchar, sub_category varchar, sub_sub_category varchar, sub_sub_sub_category varchar)")

    # TODO:
    # create table stock
    # create table properties
    # create table images
    # create table sm

    close_db_connection()
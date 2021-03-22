import psycopg2
import controller.db_auth
from models.product_properties import ProductProperties
from controller.database_predefined_values import tables

connection = None
cursor = None

def instantiate(products, sessions):
    print('Database tables aan het aanmaken')
    create_tables()
    print('Database tables zijn aangemaakt!')

    print('Database producten worden gevuld.. Dit kan even duren')
    fill_db(products, sessions)
    print('Database producten zijn gevuld!')

    print('Relaties worden toegekend')
    assign_relations()
    print('Relaties zijn toegekend!')

def open_db_connection():
    """Opens the connection to the SQL database"""

    global connection, cursor
    try:
        connection = controller.db_auth.getPostgreSQLConnection(psycopg2)
        cursor = connection.cursor()
        # print("PostgreSQL connection is open")
    except (Exception, psycopg2.Error) as error:
        print("Error while connecting to PostgreSQL", error)


def close_db_connection():
    """Closes the connection to the SQL database and commits the queries"""

    # closing database connection.
    if connection:
        connection.commit()
        cursor.close()
        connection.close()
        # print("PostgreSQL connection is closed")


def fill_db(products, sessions):
    """Fill the tables in the SQL database with data from the Mongo database

        :param products: data from the 'products' data file
        :param profiles: data from the 'profiles/visitors' data file
        :param sessions: data from the 'sessions' data file
        """

    open_db_connection()

    product_id_list = []

    n_products = products.count()
    n_sessions = sessions.count()

    count_products = 0
    count_sessions = 0


    for session in sessions:

        try:
            cursor.execute(
                "INSERT INTO orders (session_id, session_start,session_end, buid) VALUES (%s, %s, %s, %s)",
                (str(session['_id']), session['session_start'], session['session_end'], session['buid'][0]))

        except Exception as e:
            print(e)

    close_db_connection()
    open_db_connection()

    for product in products:
        count_products += 1
        if count_products % 10000 == 0 or count_products == n_products or count_products == 1:
            print(f'Products: {count_products}/{n_products}')

        try:
            cursor.execute(
                "insert into products (product_id, brand, category, color, deeplink, description, fast_mover, flavor, gender, herhaalaankopen, name, predict_out_of_stock_date, recommendable, size) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                "", (
                    get_product_property(product, '_id'), get_product_property(product, 'brand'),
                    get_product_property(product, 'category'),
                    get_product_property(product, 'color'),
                    get_product_property(product, 'deeplink'),
                    get_product_property(product, 'description'),
                    get_product_property(product, 'fast_mover'),
                    get_product_property(product, 'flavor'),
                    get_product_property(product, 'gender'),
                    get_product_property(product, 'herhaalaankopen'),
                    get_product_property(product, 'name'),
                    get_product_property(product, 'predict_out_of_stock_date'),
                    get_product_property(product, 'recommendable'),
                    get_product_property(product, 'size')))

            product_id_list.append(product['_id'])

        except KeyError:
            continue
        except psycopg2.errors.UniqueViolation:
            connection.rollback()
            continue
        try:
            product_price = get_product_property(product, 'price')
            if product_price:
                cursor.execute(
                    "insert into product_prices (product_id, discount, mrsp, selling_price) values (%s, %s, %s, %s)",
                    (product['_id'],
                     get_product_property(product_price, 'discount'),
                     get_product_property(product_price, 'mrsp'),
                     get_product_property(product_price, 'selling_price'),
                     ))
            else:
                cursor.execute(
                    "insert into product_prices (product_id, discount, mrsp, selling_price) values (%s, %s, %s, %s)",
                    (product['_id'],
                     None,
                     None,
                     None))
        except (Exception, psycopg2.Error):
            continue

        insert_product_properties(product, cursor)
        try:
            product_sm = product['sm']
            cursor.execute(
                "INSERT INTO product_sm (product_id, last_updated, type, is_active) VALUES (%s, %s, %s, %s)",
                (product['_id'],
                 get_product_property(product_sm, 'last_updated'),
                 get_product_property(product_sm, 'type'),
                 get_product_property(product_sm, 'is_active'),))
        except (Exception, psycopg2.Error):
            continue

        try:
            cursor.execute(
                "INSERT INTO product_categories (product_id, category, sub_category, sub_sub_category, sub_sub_sub_category) VALUES (%s, %s, %s, %s, %s)",
                (product['_id'],
                 get_product_property(product, 'category'),
                 get_product_property(product, 'sub_category'),
                 get_product_property(product, 'sub_sub_category'),
                 get_product_property(product, 'sub_sub_sub_category'))
            )
        except (Exception, psycopg2.Error):
            continue

    for session in sessions:
        count_sessions += 1
        if count_sessions % 10000 == 0 or count_sessions == n_sessions or count_sessions == 1:
            print(f'Sessions: {count_sessions}/{n_sessions}')
        temp_list = []
        temp_list_unique = []

        try:
            for id in session['order']['products']:

                # voer dit alleen uit als het product_id in orders ook in de products tabel zit. Anders kunnen we geen foreign keys toekennen
                if id['id'] not in product_id_list:
                    continue

                temp_list.append(id['id'])

                # we hoeven voor ons algoritme alleen te weten welke producten samen worden gekocht, product hoeveelheden zijn hiervoor niet relevant
            [temp_list_unique.append(e) for e in temp_list if e not in temp_list_unique]

            for id in temp_list_unique:
                try:

                    cursor.execute(
                        "INSERT INTO product_in_order (session_id, product_id) VALUES (%s, %s)",
                        (str(session['_id']), id))
                except (Exception, psycopg2.Error):
                    connection.rollback()
                    continue

        except (Exception, psycopg2.Error):
            pass

    close_db_connection()


def assign_relations():
    """Assigns foreign keys to relevant tables"""

    open_db_connection()

    cursor.execute("ALTER TABLE product_sm ADD FOREIGN KEY (product_id) REFERENCES products(product_id);")
    cursor.execute("ALTER TABLE product_categories ADD FOREIGN KEY (product_id) REFERENCES products(product_id);")
    cursor.execute("ALTER TABLE product_prices ADD FOREIGN KEY (product_id) REFERENCES products(product_id);")
    cursor.execute("ALTER TABLE product_properties ADD FOREIGN KEY (product_id) REFERENCES products(product_id);")
    cursor.execute("ALTER TABLE product_in_order ADD FOREIGN KEY (product_id) REFERENCES products(product_id);")

    close_db_connection()


def insert_product_properties(product, cursor):
    """Special function to fill the product_properties table
        :param product: data from the 'products' data file
        :param cursor: database connection object
        """
    try:
        properties = product['properties']
        pp = ProductProperties(
            get_product_property(properties, 'availability'),
            get_product_property(properties, 'bundel_sku'),
            get_product_property(properties, 'discount'),
            get_product_property(properties, 'doelgroep'),
            get_product_property(properties, 'eenheid'),
            get_product_property(properties, 'factor'),
            get_product_property(properties, 'folder_actief'),
            get_product_property(properties, 'gebruik'),
            get_product_property(properties, 'geschiktvoor'),
            get_product_property(properties, 'geursoort'),
            get_product_property(properties, 'huidconditie'),
            get_product_property(properties, 'huidtype'),
            get_product_property(properties, 'huidtypegezicht'),
            get_product_property(properties, 'inhoud'),
            get_product_property(properties, 'klacht'),
            get_product_property(properties, 'kleur'),
            get_product_property(properties, 'leeftijd'),
            get_product_property(properties, 'mid'),
            get_product_property(properties, 'online_only'),
            get_product_property(properties, 'serie'),
            get_product_property(properties, 'shopcart_promo_item'),
            get_product_property(properties, 'shopcart_promo_price'),
            get_product_property(properties, 'soort'),
            get_product_property(properties, 'soorthaarverzorging'),
            get_product_property(properties, 'soortmondverzorging'),
            get_product_property(properties, 'sterkte'),
            get_product_property(properties, 'stock'),
            get_product_property(properties, 'tax'),
            get_product_property(properties, 'type'),
            get_product_property(properties, 'typehaarkleuring'),
            get_product_property(properties, 'typetandenborstel'),
            get_product_property(properties, 'variant'),
            get_product_property(properties, 'waterproof'),
            get_product_property(properties, 'weekdeal'),
            get_product_property(properties, 'weekdeal_from'),
            get_product_property(properties, 'weekdeal_to')
        )
        try:
            cursor.execute(
                "insert into product_properties (product_id, availability, bundel_sku, discount, doelgroep, eenheid, factor, folder_actief, gebruik, geschiktvoor, geursoort, huidconditie, huidtype, huidtypegezicht, inhoud, klacht, kleur, leeftijd, mid, online_only, serie, shopcart_promo_item, shopcart_promo_price, soort, soorthaarverzorging, soortmondverzorging, sterkte, stock, tax, type, typehaarkleuring, typetandenborstel, variant, waterproof, weekdeal, weekdeal_from, weekdeal_to) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                (product['_id'], pp.availablity, pp.bundel_sku, pp.discount, pp.doelgroep, pp.eenheid, pp.factor,
                 pp.folder_actief, pp.gebruik, pp.geschiktvoor, pp.geursoort, pp.huidconditie, pp.huidtype,
                 pp.huidtypegezicht, pp.inhoud, pp.klacht, pp.kleur, pp.leeftijd, pp.mid, pp.online_only, pp.serie,
                 pp.shopcart_promo_item, pp.shopcart_promo_price, pp.soort, pp.soorthaarverzorging,
                 pp.soortmondverzorging, pp.sterkte, pp.stock, pp.tax, pp.type, pp.typehaarkleuring,
                 pp.typetandenborstel, pp.variant, pp.waterproof, pp.weekdeal, pp.weekdeal_from, pp.weekdeal_to))
        except Exception:
            connection.rollback()
            pass
    except KeyError:
        pass


def create_tables():
    """Creates the tables for the SQL database"""

    open_db_connection()

    for table in tables:
        try:
            cursor.execute(f"CREATE TABLE {table} ({', '.join(map(lambda i: ' '.join(i), tables[table]))})")
        except psycopg2.errors.DuplicateTable:
            connection.rollback()

    close_db_connection()


def retrieve_properties(table, properties, returncols=("*")):
    """Return a list of table entries based on the values of certain columns

    :param table: The table to execute the SQL on (str)
    :param properties: A dict of table columns as keys and their required values
    :param returncols: A list of columns to return (leave empty for *)
    :return: A list of table entries

    Example:
    retrieve_properties("products", {"brand": "Airwick"}, ["product_id", "name"])
    will return a list of product_id's and names corresponding to entries who's brand equals "Airwick
    """
    open_db_connection()
    quoted = lambda w: "'" + w + "'"  # can change, is for adding '' around a word, as f-strings do not like backslashes
    try:
        cursor.execute(
            f"SELECT {', '.join(returncols)} FROM {table} WHERE {' AND '.join([e + ' = ' + quoted(properties[e]) for e in properties])}")
        return cursor.fetchall()
    except Exception:
        pass
    close_db_connection()


def get_product_property(product_data, key):
    """Return the value of a property, returning none if no value is found"""
    try:
        return product_data[key]
    except KeyError:
        return None

import psycopg2
import utils.model_utils as model_utils
import utils.db_auth
from models.product_properties import ProductProperties

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


def fill_db(products, profiles, sessions):
    open_db_connection()

    product_id_list = []

    n_products = products.count()
    n_sessions = sessions.count()
    n_profiles = profiles.count()

    count_products = 0
    count_profiles = 0
    count_sessions = 0

    for product in products:
        count_products += 1
        if count_products % 10000 == 0 or count_products == n_products or count_products == 1:
            print(f'Products: {count_products}/{n_products}')

        try:
            cursor.execute(
                "insert into products (product_id, brand, category, color, deeplink, description, fast_mover, flavor, gender, herhaalaankopen, name, predict_out_of_stock_date, recommendable, size) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                "", ( model_utils.get_product_property(product, '_id'), model_utils.get_product_property(product, 'brand'), model_utils.get_product_property(product, 'category'), model_utils.get_product_property(product, 'color'), model_utils.get_product_property(product, 'deeplink' ),
                     model_utils.get_product_property(product, 'description'), model_utils.get_product_property(product, 'fast_mover'), model_utils.get_product_property(product, 'flavor' ),
                     model_utils.get_product_property(product, 'gender'), model_utils.get_product_property(product, 'herhaalaankopen'), model_utils.get_product_property(product, 'name' ),
                     model_utils.get_product_property(product,'predict_out_of_stock_date' ), model_utils.get_product_property(product, 'recommendable' ), model_utils.get_product_property(product, 'size')))

            product_id_list.append(product['_id'])

        except KeyError as error:
            # print(f'KeyError: {error}')
            continue
        except psycopg2.errors.UniqueViolation as error:
            # print(f'UniqueViolation: {error}')
            connection.rollback()
            continue
        try:
            cursor.execute(
                "insert into product_prices (product_id, discount, mrsp, selling_price) values (%s, %s, %s, %s)",
                (product['_id'], product['price']['discount'], product['price']['mrsp'],
                 product['price']['selling_price']))
        except (Exception, psycopg2.Error) as error:
            continue

            insert_product_properties(product, cursor)
        try:
            cursor.execute(
                "INSERT INTO product_sm (product_id, last_updated, type, is_active) VALUES (%s, %s, %s, %s)",
                (product['_id'], product['sm']['last_updated'], product['sm']['type'], product['sm']['is_active']))
        except (Exception, psycopg2.Error) as error:
            continue

        try:
            cursor.execute(
                "INSERT INTO product_categories (product_id, category, sub_category, sub_sub_category, sub_sub_sub_category) VALUES (%s, %s, %s, %s, %s)",
                (product['_id'], model_utils.get_product_property(product, 'category'),
                 model_utils.get_product_property(product, 'sub_category'),
                 model_utils.get_product_property(product, 'sub_sub_category'),
                 model_utils.get_product_property(product, 'sub_sub_sub_category'))
            )
        except (Exception, psycopg2.Error) as error:
            continue

    for profile in profiles:
        count_profiles += 1
        if count_profiles % 100000 == 0 or count_profiles == n_profiles or count_profiles == 1:
            print(f'Profiles: {count_profiles}/{n_profiles}')

        try:
            profile_id = str(profile['_id'])
            cursor.execute(
                "insert into profiles (profile_id, unique_hash, latest_activity, latest_visit) values (%s, %s, %s, %s)",
                (profile_id,
                 model_utils.get_product_property(profile, 'unique_hash'),
                 model_utils.get_product_property(profile, 'latest_activity'),
                 model_utils.get_product_property(profile, 'latest_visit')))
        except (Exception, psycopg2.Error) as error:
            print(error)
            connection.rollback()
            pass


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

            [temp_list_unique.append(e) for e in temp_list if e not in temp_list_unique]

            for id in temp_list_unique:
                try:

                    cursor.execute(
                        "INSERT INTO product_in_order (session_id, product_id) VALUES (%s, %s)",
                        (str(session['_id']), id))
                except (Exception, psycopg2.Error) as error:
                        print(error)
                        connection.rollback()
                        continue

        except (Exception, psycopg2.Error) as error:
            pass

    close_db_connection()


def assign_relations():
    open_db_connection()


    cursor.execute("ALTER TABLE product_sm ADD FOREIGN KEY (product_id) REFERENCES products(product_id);")
    cursor.execute("ALTER TABLE product_categories ADD FOREIGN KEY (product_id) REFERENCES products(product_id);")
    cursor.execute("ALTER TABLE product_prices ADD FOREIGN KEY (product_id) REFERENCES products(product_id);")
    cursor.execute("ALTER TABLE product_properties ADD FOREIGN KEY (product_id) REFERENCES products(product_id);")
    # cursor.execute("ALTER TABLE product_in_order ADD FOREIGN KEY (product_id) REFERENCES products(product_id);")
    cursor.execute("ALTER TABLE product_in_order ADD FOREIGN KEY (product_id) REFERENCES products(product_id);")


    close_db_connection()


def insert_product_properties(product, cursor):
    try:
        properties = product['properties']
        pp = ProductProperties(
            model_utils.get_product_property(properties, 'availability'),
            model_utils.get_product_property(properties, 'bundel_sku'),
            model_utils.get_product_property(properties, 'discount'),
            model_utils.get_product_property(properties, 'doelgroep'),
            model_utils.get_product_property(properties, 'eenheid'),
            model_utils.get_product_property(properties, 'factor'),
            model_utils.get_product_property(properties, 'folder_actief'),
            model_utils.get_product_property(properties, 'gebruik'),
            model_utils.get_product_property(properties, 'geschiktvoor'),
            model_utils.get_product_property(properties, 'geursoort'),
            model_utils.get_product_property(properties, 'huidconditie'),
            model_utils.get_product_property(properties, 'huidtype'),
            model_utils.get_product_property(properties, 'huidtypegezicht'),
            model_utils.get_product_property(properties, 'inhoud'),
            model_utils.get_product_property(properties, 'klacht'),
            model_utils.get_product_property(properties, 'kleur'),
            model_utils.get_product_property(properties, 'leeftijd'),
            model_utils.get_product_property(properties, 'mid'),
            model_utils.get_product_property(properties, 'online_only'),
            model_utils.get_product_property(properties, 'serie'),
            model_utils.get_product_property(properties, 'shopcart_promo_item'),
            model_utils.get_product_property(properties, 'shopcart_promo_price'),
            model_utils.get_product_property(properties, 'soort'),
            model_utils.get_product_property(properties, 'soorthaarverzorging'),
            model_utils.get_product_property(properties, 'soortmondverzorging'),
            model_utils.get_product_property(properties, 'sterkte'),
            model_utils.get_product_property(properties, 'stock'),
            model_utils.get_product_property(properties, 'tax'),
            model_utils.get_product_property(properties, 'type'),
            model_utils.get_product_property(properties, 'typehaarkleuring'),
            model_utils.get_product_property(properties, 'typetandenborstel'),
            model_utils.get_product_property(properties, 'variant'),
            model_utils.get_product_property(properties, 'waterproof'),
            model_utils.get_product_property(properties, 'weekdeal'),
            model_utils.get_product_property(properties, 'weekdeal_from'),
            model_utils.get_product_property(properties, 'weekdeal_to')
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
        except Exception as e:
            connection.rollback()
            pass
    except KeyError:
        print(f'No properties found for id: {product}')


def create_tables():
    open_db_connection()

    tables = {
        'products': [
            ('product_id', 'varchar PRIMARY KEY'),
            ('brand', 'varchar'),
            ('category', 'varchar'),
            ('color', 'varchar'),
            ('deeplink', 'varchar'),
            ('description', 'varchar'),
            ('fast_mover', 'boolean'),
            ('flavor', 'varchar'),
            ('gender', 'varchar'),
            ('herhaalaankopen', 'boolean'),
            ('name', 'varchar'),
            ('predict_out_of_stock_date', 'varchar'),
            ('recommendable', 'boolean'),
            ('size', 'varchar')
        ],
        'product_prices': [
            ('product_id varchar', 'PRIMARY KEY'),
            ('discount', 'float'),
            ('mrsp', 'float'),
            ('selling_price', 'float')
        ],
        'product_categories': [
            ('product_id', 'varchar PRIMARY KEY'),
            ('category', 'varchar'),
            ('sub_category', 'varchar'),
            ('sub_sub_category', 'varchar'),
            ('sub_sub_sub_category', 'varchar'),
        ],
        'product_properties': [
            ('product_id', 'varchar PRIMARY KEY'),
            ('availability', 'varchar NULL'),
            ('bundel_sku', 'varchar NULL'),
            ('discount', 'varchar NULL'),
            ('doelgroep', 'varchar NULL'),
            ('eenheid', 'varchar NULL'),
            ('factor', 'varchar NULL'),
            ('folder_actief', 'varchar NULL'),
            ('gebruik', 'varchar NULL'),
            ('geschiktvoor', 'varchar NULL'),
            ('geursoort', 'varchar NULL'),
            ('huidconditie', 'varchar NULL'),
            ('huidtype', 'varchar NULL'),
            ('huidtypegezicht', 'varchar NULL'),
            ('inhoud', 'varchar NULL'),
            ('klacht', 'varchar NULL'),
            ('kleur', 'varchar NULL'),
            ('leeftijd', 'varchar NULL'),
            ('mid', 'varchar NULL'),
            ('online_only', 'varchar NULL'),
            ('serie', 'varchar NULL'),
            ('shopcart_promo_item', 'varchar NULL'),
            ('shopcart_promo_price', 'varchar NULL'),
            ('soort', 'varchar NULL'),
            ('soorthaarverzorging', 'varchar NULL'),
            ('soortmondverzorging', 'varchar NULL'),
            ('sterkte', 'varchar NULL'),
            ('stock', 'varchar NULL'),
            ('tax', 'varchar NULL'),
            ('type', 'varchar NULL'),
            ('typehaarkleuring', 'varchar NULL'),
            ('typetandenborstel', 'varchar NULL'),
            ('variant', 'varchar NULL'),
            ('waterproof', 'varchar NULL'),
            ('weekdeal', 'boolean'),
            ('weekdeal_from', 'varchar NULL'),
            ('weekdeal_to', 'varchar NULL')
        ],
        'profiles': [
            ('profile_id', 'varchar PRIMARY KEY'),
            ('unique_hash', 'boolean'),
            ('latest_activity', 'timestamp'),
            ('latest_visit', 'int8')
        ],
        'product_sm': [
            ('product_id', 'varchar PRIMARY KEY'),
            ('last_updated', 'timestamp'),
            ('type', 'varchar'),
            ('is_active', 'boolean')
        ],
        'profile_order': [
            ('profile_id', 'varchar PRIMARY KEY'),
            ('latest', 'timestamp'),
            ('count', 'float'),
            ('first', 'timestamp')
        ],
        'order_id': [
            ('profile_id', 'varchar'),
            ('order_number', 'serial, PRIMARY KEY(profile_id, order_number)'),
            ('order_id', 'float')
        ],
        'product_in_order': [
            ('session_id', 'varchar'),
            ('product_id', 'varchar, PRIMARY KEY(session_id, product_id)')
        ]
    }

    for table in tables:
        try:
            cursor.execute(f"CREATE TABLE {table} ({', '.join(map(lambda i: ' '.join(i), tables[table]))})")
        except psycopg2.errors.DuplicateTable as e:
            connection.rollback()
            print(e)

    close_db_connection()


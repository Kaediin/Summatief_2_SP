import psycopg2
import pymongo
from utils import db_utils as database
from utils import db_auth

client = pymongo.MongoClient(port=27017)
db = db_auth.getMongoDatabase(client)

products = db.products.find({})


def fill_products_db():
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
            database.execute_query("insert into products (id, brand, category, color, deeplink, description, fast_mover, flavor, gender, herhaalaankopen, name, predict_out_of_stock_date, recommendable, size) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                            "",(id, brand, category, color, deeplink, description,fast_mover, flavor, gender, herhaalaankopen, name, predict_out_of_stock_date, recommendable, size))
        except:
            print(product)

def fill_prices_db():

    for product in products:

        try:
            id = product['_id']
            discount = product['price']['discount']
            mrsp = product['price']['mrsp']
            selling_price = product['price']['selling_price']
        except KeyError:
            try:
                mrsp = product['price']['msrp']
            except:
                pass

        try:
            database.execute_query("insert into prices (id, discount, mrsp, selling_price) values (%s, %s, %s, %s)"
                            "",(id, discount, mrsp, selling_price))
        except:
            print(product)

#test
fill_prices_db()
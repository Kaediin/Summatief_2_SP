import psycopg2
import pymongo
from utils import db_utils as database
from utils import db_auth

client = pymongo.MongoClient(port=27017)
db = db_auth.getMongoDatabase(client)

products = db.products.find({})




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
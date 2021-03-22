import pymongo, pprint, json
from controller import database_controller as database
from controller import db_auth

client = pymongo.MongoClient(port=27017)
db = db_auth.getMongoDatabase(client)

products = db.products.find({})
sessions = db.sessions.find({'has_sale': True})
visitors = db.visitors.find({})


database.instantiate(products, sessions, visitors)

print('Demo resultaat ophalen')
result = database.retrieve_properties("products", {"brand": "Andrelon"}, ("product_id", "name"))
pprint.pprint(result)
import pymongo
from utils import db_utils as database
from utils import db_auth

client = pymongo.MongoClient(port=27017)
db = db_auth.getMongoDatabase(client)

products = db.products.find({})
profiles = db.visitors.find({})
sessions = db.sessions.find({'has_sale':True})


print('Database tables aan het aanmaken')
database.create_tables()
print('Database tables zijn aangemaakt!')
print('Database producten worden gevuld.. Dit kan even duren')
database.fill_db(products, profiles, sessions)
print('Database producten zijn gevuld!')
database.assign_relations()
print('Relaties zijn toegekend')

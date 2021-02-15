name = 'lrzfwqzr'
host = 'tai.db.elephantsql.com'
password = 'Y-V1aacmVlN0l3GFKOdSVG2pug_Ekicm'

def getPostgreSQLConnection(psycopg2):
    connection = psycopg2.connect(user="",
                                  password="",
                                  host="127.0.0.1",
                                  port="5432",
                                  database="")
    return connection

def getMongoDatabase(client):
    return client.JouwDatabaseNaam
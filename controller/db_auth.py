def getPostgreSQLConnection(psycopg2):
    connection = psycopg2.connect(user="postgres",
                                  password="Schouten2002",
                                  host="127.0.0.1",
                                  port="5432",
                                  database="postgres")
    return connection

def getMongoDatabase(client):
    return client.ontwikkelomgeving
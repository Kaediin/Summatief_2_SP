import psycopg2
import datetime
from collections import Counter

connection = psycopg2.connect(user="postgres",
                              password="38gAc57ip!",
                              host="127.0.0.1",
                              port="5432",
                              database="postgres")
mycursor = connection.cursor()

#  manually creating the 'seizoens_rec' table with basic SQL
create_table = "DROP TABLE IF EXISTS seizoens_rec CASCADE;" \
               "CREATE TABLE seizoens_rec (session_id varchar PRIMARY KEY, datum date, maand integer NULL, seizoen varchar NULL, product varchar[],  recommendation varchar[])"
mycursor.execute(create_table)

#  manually inserting values into the designated columns
insert_table = "INSERT INTO seizoens_rec (session_id, datum, maand, product)" \
               "SELECT session_id, date(session_start), EXTRACT(MONTH FROM session_start),  products FROM orders;"
mycursor.execute(insert_table)

add_seasons_lente = "UPDATE seizoens_rec SET seizoen = 'Lente' WHERE maand BETWEEN 3 AND 5;"
mycursor.execute(add_seasons_lente)

add_seasons_herfst = "UPDATE seizoens_rec SET seizoen = 'Herfst' WHERE maand BETWEEN 9 AND 11;"
mycursor.execute(add_seasons_herfst)

add_seasons_zomer = "UPDATE seizoens_rec SET seizoen = 'Zomer' WHERE maand BETWEEN 6 AND 8;"
mycursor.execute(add_seasons_zomer)

add_seasons_winter = "UPDATE seizoens_rec SET seizoen = 'Winter' WHERE maand IN (12, 1, 2);"
mycursor.execute(add_seasons_winter)

#  importing the products which where sold during spring season
mycursor.execute("SELECT product FROM seizoens_rec WHERE seizoen = 'Lente'")
data_lente = mycursor.fetchall()
mycursor.execute("SELECT product FROM seizoens_rec WHERE seizoen = 'Herfst'")
data_herfst = mycursor.fetchall()
mycursor.execute("SELECT product FROM seizoens_rec WHERE seizoen = 'Zomer'")
data_zomer = mycursor.fetchall()
mycursor.execute("SELECT product FROM seizoens_rec WHERE seizoen = 'Winter'")
data_winter = mycursor.fetchall()


def top_four_products(data):  # function that searches for the products with the most occurrences within a specific season.
    product_counter = {}
    for product in data:
        try:
            p_id = product[0][0]
            if p_id in product_counter:
                product_counter[p_id] += 1
            else:
                product_counter[p_id] = 1
        except IndexError:
            pass

    popular_product = sorted(product_counter, key=product_counter.get, reverse=True)

    top_4 = popular_product[:4]  # You can change the amount of popular products you wish to observe by changing the slice integer
    return top_4


mycursor.execute("UPDATE seizoens_rec SET recommendation = %s WHERE seizoen = 'Lente'", (top_four_products(data_lente),))

mycursor.execute("UPDATE seizoens_rec SET recommendation = %s WHERE seizoen = 'Herfst'", (top_four_products(data_herfst),))

mycursor.execute("UPDATE seizoens_rec SET recommendation = %s WHERE seizoen = 'Zomer'", (top_four_products(data_zomer),))

mycursor.execute("UPDATE seizoens_rec SET recommendation = %s WHERE seizoen = 'Winter'", (top_four_products(data_winter),))

mycursor.close()
connection.commit()
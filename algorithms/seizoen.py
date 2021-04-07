import psycopg2
import datetime
from collections import Counter
import math

connection = psycopg2.connect(user="postgres",
                              password="38gAc57ip!",
                              host="127.0.0.1",
                              port="5432",
                              database="postgres")
mycursor = connection.cursor()

#   All sql generated code
#   Manually creating the 'seizoens_rec' table with basic SQL
create_table = "DROP TABLE IF EXISTS seizoens_rec CASCADE;" \
               "CREATE TABLE seizoens_rec (session_id varchar PRIMARY KEY, datum date, maand integer NULL," \
               " dag integer NULL, seizoen varchar NULL, feestdagen varchar NULL, product varchar[],  recommendation varchar[])"
mycursor.execute(create_table)

#   Manually inserting values into the designated columns
insert_table = "INSERT INTO seizoens_rec (session_id, datum, maand, dag, product)" \
               "SELECT session_id, date(session_start), EXTRACT(MONTH FROM session_start), EXTRACT(DAY FROM session_start), products FROM orders;"
mycursor.execute(insert_table)

add_seasons_lente = "UPDATE seizoens_rec SET seizoen = 'Lente' WHERE maand BETWEEN 3 AND 5;"
mycursor.execute(add_seasons_lente)

add_seasons_herfst = "UPDATE seizoens_rec SET seizoen = 'Herfst' WHERE maand BETWEEN 9 AND 11;"
mycursor.execute(add_seasons_herfst)

add_seasons_zomer = "UPDATE seizoens_rec SET seizoen = 'Zomer' WHERE maand BETWEEN 6 AND 8;"
mycursor.execute(add_seasons_zomer)

add_seasons_winter = "UPDATE seizoens_rec SET seizoen = 'Winter' WHERE maand IN (12, 1, 2);"
mycursor.execute(add_seasons_winter)

#   System can add more holidays depending on the owner's preference
mycursor.execute("UPDATE seizoens_rec SET feestdagen = 'Kerst' WHERE maand IN (12) AND dag BETWEEN 11 and 26")
mycursor.execute("UPDATE seizoens_rec SET feestdagen = 'Nieuwjaar' WHERE maand IN (12, 1) AND dag BETWEEN 27 and 31")
mycursor.execute("UPDATE seizoens_rec SET feestdagen = 'Pasen' WHERE maand IN (4) AND dag BETWEEN 1 and 5")
mycursor.execute("UPDATE seizoens_rec SET feestdagen = 'Sinterklaas' WHERE maand IN (12) AND dag BETWEEN 1 and 6")

#   importing the products which where sold during spring/autumn/summer/winter season
mycursor.execute("SELECT product FROM seizoens_rec WHERE seizoen = 'Lente'")
data_lente = mycursor.fetchall()
mycursor.execute("SELECT product FROM seizoens_rec WHERE seizoen = 'Herfst'")
data_herfst = mycursor.fetchall()
mycursor.execute("SELECT product FROM seizoens_rec WHERE seizoen = 'Zomer'")
data_zomer = mycursor.fetchall()
mycursor.execute("SELECT product FROM seizoens_rec WHERE seizoen = 'Winter'")
data_winter = mycursor.fetchall()

#   importing the products which where sold during holidays
mycursor.execute("SELECT product FROM seizoens_rec WHERE feestdagen = 'Kerst'")
data_kerst = mycursor.fetchall()
mycursor.execute("SELECT product FROM seizoens_rec WHERE feestdagen = 'Nieuwjaar'")
data_nieuwjaar = mycursor.fetchall()
mycursor.execute("SELECT product FROM seizoens_rec WHERE feestdagen = 'Pasen'")
data_pasen = mycursor.fetchall()
mycursor.execute("SELECT product FROM seizoens_rec WHERE feestdagen = 'Sinterklaas'")
data_sinterklaas = mycursor.fetchall()

#   importing the products which where sold during a specific year
mycursor.execute("SELECT product FROM seizoens_rec WHERE EXTRACT(YEAR FROM datum) = '2017'")
data_2017 = mycursor.fetchall()
mycursor.execute("SELECT product FROM seizoens_rec WHERE EXTRACT(YEAR FROM datum) = '2018'")
data_2018 = mycursor.fetchall()
mycursor.execute("SELECT product FROM seizoens_rec WHERE EXTRACT(YEAR FROM datum) = '2019'")
data_2019 = mycursor.fetchall()

#   importing the products which where sold during a specific year AND specific season
mycursor.execute("SELECT product FROM seizoens_rec WHERE EXTRACT(YEAR FROM datum) = '2017' AND seizoen = 'Lente'")
data_2017_LENTE = mycursor.fetchall()
mycursor.execute("SELECT product FROM seizoens_rec WHERE EXTRACT(YEAR FROM datum) = '2017' AND seizoen = 'Herfst'")
data_2017_HERFST = mycursor.fetchall()
mycursor.execute("SELECT product FROM seizoens_rec WHERE EXTRACT(YEAR FROM datum) = '2017' AND seizoen = 'Zomer'")
data_2017_ZOMER = mycursor.fetchall()
mycursor.execute("SELECT product FROM seizoens_rec WHERE EXTRACT(YEAR FROM datum) = '2017' AND seizoen = 'Winter'")
data_2017_WINTER = mycursor.fetchall()
mycursor.execute("SELECT product FROM seizoens_rec WHERE EXTRACT(YEAR FROM datum) = '2018' AND seizoen = 'Lente'")
data_2018_LENTE = mycursor.fetchall()
mycursor.execute("SELECT product FROM seizoens_rec WHERE EXTRACT(YEAR FROM datum) = '2018' AND seizoen = 'Herfst'")
data_2018_HERFST = mycursor.fetchall()
mycursor.execute("SELECT product FROM seizoens_rec WHERE EXTRACT(YEAR FROM datum) = '2018' AND seizoen = 'Zomer'")
data_2018_ZOMER = mycursor.fetchall()
mycursor.execute("SELECT product FROM seizoens_rec WHERE EXTRACT(YEAR FROM datum) = '2018' AND seizoen = 'Winter'")
data_2018_WINTER = mycursor.fetchall()
mycursor.execute("SELECT product FROM seizoens_rec WHERE EXTRACT(YEAR FROM datum) = '2019'AND seizoen = 'Lente'")   #NULL
data_2019_LENTE = mycursor.fetchall()
mycursor.execute("SELECT product FROM seizoens_rec WHERE EXTRACT(YEAR FROM datum) = '2019'AND seizoen = 'Herfst'")  #NULL
data_2019_HERFST = mycursor.fetchall()
mycursor.execute("SELECT product FROM seizoens_rec WHERE EXTRACT(YEAR FROM datum) = '2019'AND seizoen = 'Zomer'")   #NULL
data_2019_ZOMER = mycursor.fetchall()
mycursor.execute("SELECT product FROM seizoens_rec WHERE EXTRACT(YEAR FROM datum) = '2019'AND seizoen = 'Winter'")
data_2019_WINTER = mycursor.fetchall()


#   function to make a dict with key = product_id & value = occurrences
def counter_year(data):
    x = [i for sublist in data for i in sublist]  # removing brackets
    y = [i for sublist in x for i in sublist]  # removing secondary brackets
    product_counter = Counter(y)
    return product_counter

counter_year(data_2019)

def counter_year_season(data):
    n = [i for sublist in data for i in sublist]
    m = [i for sublist in n for i in sublist]
    product_counter_season = Counter(m)
    return product_counter_season

counter_year(data_2019_WINTER)

sorted_dict = sorted(counter_year(data_2019).items(), key=lambda x: x[1], reverse=True)
sorted_dict_season = sorted(counter_year_season(data_2019_WINTER).items(), key=lambda x: x[1], reverse=True)

#   Visualization dictionary with the stock value, average seasonal value (stock divided by 4) and product_id
for key,val in sorted_dict:
    avg_val = math.ceil(val / 4)
    print('stock.val = {0:4} | div.val = {1:4} | product_id = {2:4} '.format(val, avg_val, key))

#   Visualization dictionary with the stock value and product_id
#for key,val in sorted_dict_season:
#    print('stock.val = {0:4} | product_id = {1:4} '.format(val, key))



#   Function that searches for the products with the most occurrences within a specific season.
def top_four_products(data):
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

#   update execute that will reveal the 4 recommendations in database
mycursor.execute("UPDATE seizoens_rec SET recommendation = %s WHERE seizoen = 'Lente'", (top_four_products(data_lente),))
mycursor.execute("UPDATE seizoens_rec SET recommendation = %s WHERE seizoen = 'Herfst'", (top_four_products(data_herfst),))
mycursor.execute("UPDATE seizoens_rec SET recommendation = %s WHERE seizoen = 'Zomer'", (top_four_products(data_zomer),))
mycursor.execute("UPDATE seizoens_rec SET recommendation = %s WHERE seizoen = 'Winter'", (top_four_products(data_winter),))

mycursor.execute("UPDATE seizoens_rec SET recommendation = %s WHERE feestdagen = 'Kerst'", (top_four_products(data_lente),))
mycursor.execute("UPDATE seizoens_rec SET recommendation = %s WHERE feestdagen = 'Nieuwjaar'", (top_four_products(data_lente),))
mycursor.execute("UPDATE seizoens_rec SET recommendation = %s WHERE feestdagen = 'Pasen'", (top_four_products(data_lente),))
mycursor.execute("UPDATE seizoens_rec SET recommendation = %s WHERE feestdagen = 'Sinterklaas'", (top_four_products(data_lente),))


mycursor.close()
connection.commit()
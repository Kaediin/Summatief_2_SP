import psycopg2
import psycopg2
import controller.db_auth
from models.product_properties import ProductProperties
from controller.database_predefined_values import tables



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

def create_user_orders_rec(name):
    open_db_connection()

    # create table
    cursor.execute(
        f"create table {name}(product_id varchar primary key, rec_1 varchar, rec_2 varchar, rec_3 varchar, rec_4 varchar)"
    )

    cursor.execute(
        "select product_id from products"
    )
    data = cursor.fetchall()
    id_list = []

    # replacing ' with '' so LIKE in the sql statement doesn't fuck up
    id_list = [id[0].replace("'", "''") for id in data]

    rec_list = []

    for count, product_id in enumerate(id_list):
        # using a subquery to fetch the 4 products most often bought together with product "product_id" that don't share the same sub_sub_category

        if name == 'order_recs':

            q = f"""select product_id ,count(product_id) as product_id_count 
                    from product_in_order pio2  
                    where session_id in (select session_id  from product_in_order pio  where product_id like '{product_id}')
                    and product_id not like '{product_id}' 
                    group by product_id  
                    order by product_id_count desc limit 4"""

        elif name == 'order_recs_dif_cat':
            q = f"""select pio2.product_id ,count(pio2.product_id) as product_id_count
                    from product_in_order pio2 inner join product_categories pc on pc.product_id = pio2.product_id
                    where session_id in (select session_id  from product_in_order pio  where product_id like '{product_id}')
                    and sub_sub_category is not null and pio2.product_id not like '{product_id}'
                    and pc.sub_sub_category not in (select sub_sub_category from product_categories pc2 where product_id like '{product_id}')
                    group by pio2.product_id , pc.sub_sub_category
                    order by product_id_count
                    desc limit 4"""

        if name == 'product_recs':

            q = f"""select pio2.product_id ,count(pio2.product_id) as product_id_count
                    from product_in_order pio2 inner join product_categories pc on pc.product_id = pio2.product_id
                    where session_id in (select session_id  from product_in_order pio  where product_id like '{product_id}')
                    and sub_sub_category is not null and pio2.product_id not like '{product_id}'
                    and pc.sub_sub_category in (select sub_sub_category from product_categories pc2 where product_id like '{product_id}')
                    group by pio2.product_id , pc.sub_sub_category
                    order by product_id_count
                    desc limit 4"""

        elif name == 'cart_recs':

           q = f"""select pio2.product_id ,count(pio2.product_id) as product_id_count
                    from product_in_order pio2 inner join product_categories pc on pc.product_id = pio2.product_id
                    where session_id in (select session_id  from product_in_order pio  where product_id like '{product_id}')
                    and sub_sub_category is not null and pio2.product_id not like '{product_id}'
                    and pc.sub_sub_category not in (select sub_sub_category from product_categories pc2 where product_id like '{product_id}')
                    group by pio2.product_id , pc.sub_sub_category
                    order by product_id_count
                    desc limit 4"""


        cursor.execute(q)

        data = cursor.fetchall()
        id_recs = [x[0] for x in data]

        for i in range(4 - (len(id_recs))):
            id_recs.append('NULL')

        for i in range(len(id_recs)):
            if (id_recs[i] != 'NULL'):
                id_recs[i] = f"'{id_recs[i]}'"

        rec_list.append(id_recs)
        cursor.execute(
            f"insert into {name}(product_id,rec_1,rec_2,rec_3,rec_4) values('{product_id}',{id_recs[0]},{id_recs[1]},{id_recs[2]},{id_recs[3]})"
        )

        # commit every 2000 rows
        if count % 2000 == 0:
            close_db_connection()
            open_db_connection()

    close_db_connection()



create_user_orders_rec('cart_recs')
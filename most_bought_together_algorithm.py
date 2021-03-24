import psycopg2
import psycopg2
import controller.db_auth
from models.product_properties import ProductProperties
from controller.database_predefined_values import tables
import operator



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


def create_order_based_recs(rec_amount):
    open_db_connection()

    # create table
    # we track the average of how many times the most bought together items were in the same order as item x, we do this so we have an indication of the accuracy of the recommendation:
    # avg_x_shared_orders = 3 -> weak correlation, avg_x_shared_orders = 200 -> very strong correlation.
    try:
        cursor.execute(
        f"create table order_based_recs (product_id varchar primary key, recommendations varchar[], avg_x_shared_orders int)"
        )
    except:
        connection.rollback()

    connection.commit()

    cursor.execute(
        "select product_id from products"
    )
    data = cursor.fetchall()

    # replacing ' with '' so LIKE in the sql statement doesn't fuck up
    id_list = [id[0].replace("'", "''") for id in data]


    for count, product_id in enumerate(id_list):

        if count%1000==0:
            connection.commit()
            print(f"{count}/{len(id_list)}")

        q = f"""select products
            from orders
            where '{product_id}' like ANY(products) """


        cursor.execute(q)
        data = cursor.fetchall()

        product_list = [product for order in data for product in list(set(order[0])) if product != product_id]

        unique_product_list = list(set(product_list))

        results_dict = {}

        for p_id in unique_product_list:

            results_dict [p_id] = product_list.count(p_id)


        #sort list on what products were bought together most often with product_id x
        sorted_results = sorted(results_dict.items(), key=operator.itemgetter(1))
        sorted_results.reverse()


        recs = [rec[0] for rec in sorted_results][:rec_amount]

        try:
            count_list = [sorted_results[x][1] for x in range(len(recs))]
        except:
            pass

        if len(recs)!=0:
            avg = round(sum(count_list)/len(recs),2)
        else:
            recs = None
            avg = 0

        cursor.execute(
            f"insert into order_based_recs (product_id,recommendations,avg_x_shared_orders) values(%s,%s,%s)",(product_id,recs,avg)
        )


    close_db_connection()



create_order_based_recs(4)
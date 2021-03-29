import operator

import psycopg2

import controller.db_auth
import controller.db_auth


def run(cursor, connection, rec_limit=4):
    try:
        cursor.execute("select count(*) from order_based_recs")
        hasEntries = True if cursor.fetchone()[0] > 0 else False
    except:
        connection.rollback()
        hasEntries = False

    if not hasEntries:
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

        q = f"""select products
                       from orders"""

        cursor.execute(q)
        data = cursor.fetchall()

        for count, product_id in enumerate(id_list):

            data_list = [x[0] for x in data if product_id in x[0]]

            if count % 1000 == 0 or count == 1 or count == len(id_list):
                connection.commit()
                print(f"Recommendations made (most bought together): {count}/{len(id_list)}")

            product_list = [product for order in data_list for product in list(set(order)) if product != product_id]

            unique_product_list = list(set(product_list))

            results_dict = {}

            for p_id in unique_product_list:
                results_dict[p_id] = product_list.count(p_id)

            # sort list on what products were bought together most often with product_id x
            sorted_results = sorted(results_dict.items(), key=operator.itemgetter(1))
            sorted_results.reverse()

            recs = [rec[0] for rec in sorted_results][:rec_limit]

            try:
                count_list = [sorted_results[x][1] for x in range(len(recs))]
            except:
                pass

            if len(recs) != 0:
                avg = round(sum(count_list) / len(recs), 2)
            else:
                recs = None
                avg = 0

            cursor.execute(
                f"insert into order_based_recs (product_id,recommendations,avg_x_shared_orders) values(%s,%s,%s)",
                (product_id, recs, avg)
            )

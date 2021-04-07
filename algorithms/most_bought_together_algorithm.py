import operator

def create_table_most_bought_together(cursor, connection, rec_limit=4):
    """creates a table with recommendations based on what products were bought most often with other prodcuts, and a score based on how often that happened on average"""

    cursor.execute("select count(*) from order_based_recs")
    hasEntries = True if cursor.fetchone()[0] > 0 else False


    if not hasEntries:

        cursor.execute(
            "select product_id from products"
        )
        data = cursor.fetchall()

        # replacing ' with '' so LIKE in the sql statement doesn't crash
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


            count_list = [sorted_results[x][1] for x in range(len(recs))]


            if len(recs) != 0:
                avg = round(sum(count_list) / len(recs), 2)
            else:
                recs = None
                avg = 0

            cursor.execute(
                f"insert into order_based_recs (product_id,recommendations,avg_x_shared_orders) values(%s,%s,%s)",
                (product_id, recs, avg)
            )

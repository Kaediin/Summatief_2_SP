
# def run(cursor, connection):
#     try:
#         cursor.execute("select count(*) from behaviour_recs")
#         hasEntries = True if cursor.fetchone()[0] > 0 else False
#     except:
#         connection.rollback()
#         hasEntries = False
#
#     if not hasEntries:
#         try:
#             cursor.execute("drop table if exists behaviour_recs")
#             cursor.execute("create table behaviour_recs (visitor_id varchar primary key, recommendations varchar[] null)")
#             print("Table created")
#         except psycopg2.errors.DuplicateTable:
#             connection.rollback()
#             print("Table already exists")
#
#         cursor.execute("select visitor_id from visitors where cardinality(buids) != 0")
#         ids = [e[0] for e in cursor.fetchall()]
#
#         c = 0
#         s = time.time()
#         average = []
#         for i in ids:
#             i = i.replace("'", "''")
#             recs = recommend(i, cursor)
#             # cursor.execute("insert into behaviour_recs (visitor_id, recommendations) values (%s, %s)", (i, recs))
#             if c % 100 == 0 and c > 0:  # or c == 1 or c == len(ids):
#                 print(recs)
#                 dt = time.time() - s
#                 average.append(dt)
#                 print(f'Recommendations made (purchasing behaviour): {c}/{len(ids)} - {dt} - AVG: {sum(average) / len(average)}')
#                 s = time.time()
#             c += 1


def recommend(cart, cursor, limit=4):
    cursor.execute("select products from orders where cardinality(products) > 1")
    products = [set(e[0]) for e in cursor.fetchall()]

    cart = set(cart)
    products = sorted([e - cart for e in sorted(products, key=lambda e: len(cart & e))[::-1] if len(e - cart) > 0], key=len)
    result = []

    while len(result) < limit:
        order = products.pop(0)

        for p in order:
            result.append(p)
            if len(result) >= limit:
                break

    return result

    # cursor.execute(f"""
    #                     select v.buids from visitors v
    #                         where visitor_id = '{visitor_id}'
    #                 """)
    # buids = cursor.fetchall()[0][0]
    #
    # products = []
    # for buid in buids:
    #     cursor.execute(f"""
    #                         select unnest(products) from orders
    #                             where buid = '{buid}'
    #                     """)
    #     products.append(cursor.fetchall())
    # return products


# print(recommend(['38815', '34078', '39928'], cur))

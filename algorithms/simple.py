import psycopg2
import random


def run(cursor, connection):
    """
        Drop, then create, the table 'simplerecs', and then fill that table with product ID's and recommended items
    """

    # Check if the table needs to be filled or not
    try:
        cursor.execute("select count(*) from simplerecs")
        hasEntries = True if cursor.fetchone()[0] > 0 else False
    except:
        connection.rollback()
        hasEntries = False

    if not hasEntries:
        # Create the table 'simplerecs'
        try:
            cursor.execute("drop table if exists simplerecs")
            cursor.execute("create table simplerecs (product_id varchar primary key, recommendations varchar[] null)")
            print("Table created")
        except psycopg2.errors.DuplicateTable:
            connection.rollback()
            print("Table already exists")

        cursor.execute("select product_id from product_categories")
        ids = [e[0] for e in cursor.fetchall()]

        # For each product, recommend 4 products and save these in the table 'simplerecs'
        c = 0
        for i in ids:
            i = i.replace("'", "''")
            recs = recommend(i, cursor)
            cursor.execute("insert into simplerecs (product_id, recommendations) values (%s, %s)", (i, recs))
            if c % 1000 == 0 or c == 1 or c == len(ids):
                print(f'Recommendations made (simple): {c}/{len(ids)}')
            c += 1


def recommend(product_id, cursor, limit=4):
    """
        Generate 4 items to recommend based on the given product ID
    """

    # Get the category, sub_category and sub_sub_category associated with the given product ID
    cursor.execute(f"""
                        select p.category, p.sub_category, p.sub_sub_category from product_categories p
                            where p.product_id = '{product_id}'
                    """)
    cat, subcat, subsubcat = [e.replace("'", "''") if e is not None else e for e in cursor.fetchall()[0]]

    # Get all product ID's with the same sub_sub_category, sub_category and category in that order
    cursor.execute(f""" 
                        select t.product_id from (
                            select *, 1 as filter from product_categories pc
                                where pc.sub_sub_category = '{subsubcat}'
                                and pc.product_id != '{product_id}'
                            union 
                            select *, 2 as filter from product_categories pc
                                where pc.sub_category = '{subcat}'
                                and pc.sub_sub_category != '{subsubcat}'
                                and pc.product_id != '{product_id}'
                            union 
                            select *, 3 as filter from product_categories pc
                                where pc.category = '{cat}'
                                and pc.sub_category != '{subcat}'
                                and pc.product_id != '{product_id}'
                            order by filter
                            limit {limit}) as t
                    """)

    # If there are not enough products, fill the rest of the list with random products
    res = [str(r[0]) for r in cursor.fetchall()]
    if len(res) < limit:
        cursor.execute("select product_id from products")
        ids = [e[0] for e in cursor.fetchall()]

        [res.append(e) for e in random.sample(ids, limit) if e not in res and len(res) < limit]
    return res

import psycopg2
import random
# import controller.db_auth


def getPostgreSQLConnection(psycopg2):
    conn = psycopg2.connect(user="postgres",
                            password="johnwilliams",
                            host="127.0.0.1",
                            port="5432",
                            database="spsummatief")
    return conn


connection = getPostgreSQLConnection(psycopg2)
cursor = connection.cursor()


def run():
    """
        Drop, then create, the table 'simplerecs', and then fill that table with product ID's and recommended items
    """
    try:
        cursor.execute("drop table if exists simplerecs")
        cursor.execute("CREATE TABLE simplerecs (product_id varchar PRIMARY KEY, recommendations varchar[] null)")
        print("Table created")
    except psycopg2.errors.DuplicateTable:
        connection.rollback()
        print("Table already exists")

    cursor.execute("select product_id from product_categories where category is not null")
    ids = [e[0] for e in cursor.fetchall()]

    c = 0
    for i in ids:
        i = i.replace("'", "''")
        recs = recommend(i)
        cursor.execute("insert into simplerecs (product_id, recommendations) values (%s, %s)", (i, recs))
        if c % 1000 == 0:
            print(c)
        c += 1


def recommend(i):
    """
        Generate 4 items to recommend based on the given product ID
    """
    cursor.execute(f"""
                        select p.category, p.sub_category, p.sub_sub_category from product_categories p
                            where p.product_id = '{i}'
                    """)
    cat, subcat, subsubcat = [e.replace("'", "''") if e is not None else e for e in cursor.fetchall()[0]]

    cursor.execute(f""" 
                        select t.product_id from (
                            select *, 1 as filter from product_categories pc
                                where pc.sub_sub_category = '{subsubcat}'
                            union 
                            select *, 2 as filter from product_categories pc
                                where pc.sub_category = '{subcat}'
                                and pc.sub_sub_category != '{subsubcat}'
                            union 
                            select *, 3 as filter from product_categories pc
                                where pc.category = '{cat}'
                                and pc.sub_category != '{subcat}'
                            order by filter
                            limit 4) as t
                    """)

    res = [str(r[0]) for r in cursor.fetchall()]
    if len(res) < 4:
        cursor.execute("select product_id from products")
        ids = [e[0] for e in cursor.fetchall()]

        [res.append(e) for e in random.sample(ids, 4) if e not in res and len(res) < 4]
    return res


def getrecs(i):
    """
        Get the recommended items from the database given a product ID
    """
    i = i.replace("'", "''")
    cursor.execute(f"select recommendations from simplerecs where product_id = '{i}'")
    return cursor.fetchall()[0][0]


# run()
print(recommend('31861'))


connection.commit()
cursor.close()
connection.close()

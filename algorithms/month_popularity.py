import operator
import controller.database_controller as database

ids = database.execute_query("""select product_id from products""", "")
price_data = database.execute_query(
    f"""select products
                from orders
                where session_start >= '2017-01-01'
                and session_start < '2019-01-01' """, "")


def test(ids, price_data):
    product_ids = [id[0] for id in ids]

    data = [i for data in price_data for x in data for i in x]

    product_ids_sales = []
    for count, id in enumerate(set(data)):
        product_ids_sales.append([id, data.count(id)])

    return product_ids_sales


year_sales = (test(ids, price_data))

for x in range(1, 13):
    year = 2018
    bot_month = str(x)

    if (x == 12):
        top_month = str(1)
    else:
        top_month = str(x + 1)

    if len(bot_month) == 1:
        bot_month = f"0{bot_month}"

    if len(top_month) == 1:
        top_month = f"0{top_month}"

    bot_date = f"{year}-{bot_month}-01"
    if (top_month == '01'):
        year = year + 1
    top_date = f"{year}-{top_month}-01"

    month_sales = database.execute_query(
        f"""select products
                    from orders
                    where session_start >= '{bot_date}'
                    and session_start < '{top_date}' """, "")

    most_often_sold = test(ids, month_sales)

    list_ding = []
    for x in most_often_sold:
        for i in year_sales:
            if x[0] == i[0]:
                dif = (100 / i[1]) * x[1]
                # print(x[0],dif, (dif/x[1]), bot_date)
                list_ding.append((x[0], dif, x[1]))

    ld = list(reversed(sorted(list_ding, key=lambda x: (x[1], x[2]))))
    ld2 = [pipo for pipo in ld if pipo[2] >15]

    print(ld2)

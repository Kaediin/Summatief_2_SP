import operator
import controller.database_controller as database
from controller.database_predefined_values import sales_per_year

ids = database.execute_query("""select product_id from products""", "")
price_data = database.execute_query(
    f"""select products
                from orders
                where session_start >= '2018-01-01'
                and session_start < '2019-01-01' """, "")


def calculate_yearly_product_sales(price_data):
    data = [i for data in price_data for x in data for i in x]

    product_ids_sales = []
    for count, id in enumerate(set(data)):
        product_ids_sales.append([id, data.count(id)])

    return product_ids_sales


year_sales = sales_per_year
interval = 2

for month in range(1, 13):
    year = 2018
    bottom_month = str(month)

    if month == 12 or month + interval > 12:
        top_month = str(1)
    else:
        top_month = str(month + interval)

    if len(bottom_month) == 1:
        bottom_month = f"0{bottom_month}"

    if len(top_month) == 1:
        top_month = f"0{top_month}"

    bot_date = f"{year}-{bottom_month}-01"
    if top_month == '01':
        year = year + 1
    top_date = f"{year}-{top_month}-01"

    month_sales = database.execute_query(
        f"""select products
                    from orders
                    where session_start >= '{bot_date}'
                    and session_start < '{top_date}' """, "")

    most_often_sold = calculate_yearly_product_sales(month_sales)

    products = []
    for x in most_often_sold:
        for i in year_sales:
            if x[0] == i[0]:
                dif = (100 / i[1]) * x[1]
                products.append((x[0], dif, x[1]))

    sorted_products = list(reversed(sorted(products, key=lambda x: (x[1], x[2]))))
    filtered_sorted_products = [product for product in sorted_products if product[2] > 15]
    filtered_ids = [prod[0] for prod in filtered_sorted_products[:10]]
    print(f'Interval: {bottom_month} - {top_month}', filtered_ids)

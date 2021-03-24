import controller.database_controller as database


def get_recs(visitor_id, limit=4):
    results = database.execute_query("select * from visitor_recs where visitor_id = %s", (visitor_id,))
    all_product_ids = []
    for row in results:
        if row[1] is not None:
            for item in row[1]:
                if item not in all_product_ids:
                    all_product_ids.append(item)
        if row[2] is not None:
            for item in row[2]:
                if item not in all_product_ids:
                    all_product_ids.append(item)

    category_counter = {'main': {}, 'sub': {}, 'sub_sub': {}}
    for id in all_product_ids:
        category_result = database.execute_query("select * from product_categories where product_id = %s", (id,))
        category = category_result[0][1]
        sub_category = category_result[0][2]
        sub_sub_category = category_result[0][3]
        if category in category_counter['main']:
            category_counter['main'][category] += 1
        else:
            category_counter['main'][category] = 1

        if sub_category in category_counter['sub']:
            category_counter['sub'][sub_category] += 1
        else:
            category_counter['sub'][sub_category] = 1

        if sub_sub_category in category_counter['sub_sub']:
            category_counter['sub_sub'][sub_sub_category] += 1
        else:
            category_counter['sub_sub'][sub_sub_category] = 1
    category_counter = {k: v for k, v in
                        reversed(sorted(category_counter['sub_sub'].items(), key=lambda item: item[1]))}

    # TODO: Show 4 of most populat category? Show 1 of each (cat[0], cat[2] etc.) Show Random of most popular cat?
    # TODO: Show not-yet-seen products of most popular category?
    most_popular_category = list(category_counter.keys())[0]
    popular_category_product_ids = database.execute_query(
        "select product_id from product_categories where sub_sub_category = %s limit 4", (most_popular_category,))

    products = []
    for row in popular_category_product_ids:
        products.append(database.execute_query("select * from products where product_id = %s", (row[0],)))

    return products

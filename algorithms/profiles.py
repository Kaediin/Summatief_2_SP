import controller.database_controller as database
import itertools, random


def get_recs(visitor_id):
    products = known_products(visitor_id)
    # products.extend(based_on_orders(visitor_id, products))
    return products


def known_products(visitor_id):
    results = list(database.execute_query(
        "select previously_recommended, viewed_before, similars from visitor_recs where visitor_id = %s",
        (visitor_id,))[0])
    try:
        all_product_ids = tuple(itertools.chain.from_iterable(results))
    except TypeError:
        return []

    category_counter = {'main': {}, 'sub': {}, 'sub_sub': {}}

    cat_results = database.execute_query(
        "select category, sub_category, sub_sub_category from product_categories where product_id in %s",
        (all_product_ids,))

    layers = ['sub_sub', 'sub', 'main']
    products = []
    r_layers = layers.copy()
    r_layers.reverse()
    for row in cat_results:
        for i, layer in enumerate(r_layers):
            if row[i] in category_counter[layer]:
                category_counter[layer][row[i]] += 1
            else:
                category_counter[layer][row[i]] = 1

    for layer in layers:
        try:
            category_counter = {k: v for k, v in
                                reversed(sorted(category_counter[layer].items(), key=lambda item: item[1]))}
            most_popular_category = list(category_counter.keys())[0]
            popular_category_product_ids = database.execute_query(
                "select product_id from product_categories where sub_sub_category = %s",
                (most_popular_category, ))
            popular_category_product_ids = list(itertools.chain.from_iterable(popular_category_product_ids))
            products_results = database.execute_query("select * from products where product_id in %s", (tuple(popular_category_product_ids), ))
            random.shuffle(products_results)
            return products_results
        except Exception as e:
            print(e.args)
            break
    return products

def based_on_orders(vistor_id, products):
    buids = database.execute_query("select buids from visitors where visitor_id = %s", (vistor_id,))[0][0]
    product_ids = set()
    for buid in buids:
        print(buid)
        order_products = database.execute_query("select products from orders where buid = %s", (buid,))
        for p_id in order_products:
            [product_ids.add(e) for e in p_id[0]]

    # get recommendations based on these ids!
    print(product_ids)
    return products
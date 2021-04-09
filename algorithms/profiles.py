import controller.database_controller as database
import itertools, psycopg2
from algorithms import prioritze_discount


def get_recs(visitor_id, limit, only_ids=False):
    """ get recommendations based on visitor id """

    # get related products to a profile """
    profile_columns = list(database.execute_query(
        "select previously_recommended, viewed_before, similars from visitor_recs where visitor_id = %s",
        (visitor_id,))[0])
    try:
        # flatten the lists (profile_columns can conatins list in lists etc.)
        all_product_ids = tuple(itertools.chain.from_iterable(profile_columns))
    except TypeError:
        return []

    # create dict with empty dicts for every category type and keep count
    category_counter = {'main': {}, 'sub': {}, 'sub_sub': {}}


    all_product_ids = list(all_product_ids)

    if(len(all_product_ids)==1):
        all_product_ids.append('')

    if(len(all_product_ids)>0):
        cat_results = database.execute_query(
            f"select category, sub_category, sub_sub_category from product_categories where product_id in {tuple(all_product_ids)}","")
    else:
        cat_results = []

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

    # loop trough category types starting from deepest (starting wiht sub_sub)
    for layer in layers:
        try:
            # Calculate recommendations from the category type and add them to a list
            category_counter = {k: v for k, v in
                                reversed(sorted(category_counter[layer].items(), key=lambda item: item[1]))}
            most_popular_category = list(category_counter.keys())[0]
            popular_category_product_ids = database.execute_query(
                "select product_id from product_categories where sub_sub_category = %s",
                (most_popular_category,))
            popular_category_product_ids = prioritze_discount.prioritize_discount(
                list(itertools.chain.from_iterable(popular_category_product_ids)), limit)
            select_criteria = '*' if only_ids is False else 'product_id'
            products_results = database.execute_query(f"select {select_criteria} from products where product_id in %s",
                                                      (tuple(popular_category_product_ids),))
            return products_results
        except psycopg2.errors.SyntaxError:
            break
    return products

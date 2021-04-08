import controller.database_controller as database
from algorithms import behaviour, prioritze_discount
from page_logic import page_home
from model import convert_to_model
import random


def cart_alg_selection(limit, shopping_cart, profile_id):
    "code that decides what algorithm to use in the shopping cart based on the accuracy of the recommendations, returns *limit* recommendations"

    # get all the ids from the cart
    ids_in_cart = [x[0] for x in shopping_cart]

    # if there is only 1 element in the list Psycopg2 will crash. Hence the statement add a blank string.
    # (does not affect the results)
    if len(ids_in_cart) == 1:
        ids_in_cart.append('')
    if len(ids_in_cart) > 0:
        recs_data = database.execute_query(
            f"select * from order_based_recs where product_id in {tuple(ids_in_cart)}",
            "")
        recs_data = list(reversed(sorted(recs_data, key=lambda x: x[2])))[:limit]
        recs_data_simple = database.execute_query(
            f"select * from simplerecs where product_id in {tuple(ids_in_cart)}",
            "")
        recs_data_behaviour = behaviour.recommend(ids_in_cart, limit)
        print(f'{ids_in_cart}, {recs_data_behaviour}')

        sample_size_limit = 10
        if recs_data[0][2] >= sample_size_limit:
            print('Algorithm: Bought_together')

            recs = list(set([product for rec in recs_data if rec[2] >= sample_size_limit for product in rec[1] if
                             product not in ids_in_cart]))

            recs = prioritze_discount.prioritize_discount(recs, limit)
        else:
            if len(recs_data_behaviour) == limit:
                print('Algorithm: Behaviour')
                recs = recs_data_behaviour
            else:
                print('Algorithm: Simple')
                recs = list(set([z for x in recs_data_simple for z in random.sample(x[1], k=len(x[1]))]))[:limit]

        r_prods = convert_to_model.convert_to_product_list("select * from products where product_id in %s",
                                                           (tuple(recs),))

    else:
        try:
            if profile_id is None:
                raise NameError
            r_prods = page_home.get_profile_recommendations(profile_id, limit=limit)
        except NameError:
            r_prods = [convert_to_model.toProduct(e) for e in database.get_based_on_categories([], limit)]

    return r_prods

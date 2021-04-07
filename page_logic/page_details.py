import controller.database_controller as database
from algorithms import behaviour, prioritze_discount, simple
from page_logic import page_home
from model import convert_to_model
import random


def product_detail_alg_selection(product):
    "code that decides what algorithm to use in the product_details based on the accuracy of the recommendations"

    recs_data = database.execute_query(
        f"select recommendations, weighted_match_rate from property_matching_recs where product_id = '{product.product_id}'",
        "")

    threshold = 50
    # If 50% (threshold value in percentages) of the properties of a product match with others
    # we can you those products. This indicated how much a product has in common with others.
    if recs_data[0][1] > threshold:
        print('Algorithm: property_matching')
        recs = (recs_data[0][0])
        r_products = convert_to_model.convert_to_product_list("select * from products where product_id in %s",
                                                              (tuple(recs),))
    # if this product does have much in common we call the simple algorithm to extend te list to its limit (usually 4)
    else:
        print('Algorithm: simple')
        r_products = simple.get_recommendations(product.product_id)

    return r_products

import controller.database_controller as database
from algorithms import profiles, simple
from page_logic import page_cart


def get_recommendations(profile_id, categories, min_amount, max_amount=34004):
    """ Main function that gets called from HUW.py """
    try:
        """ Try to get profile recs. If there is no profile then get recs based on categories """
        if profile_id is None or len(categories) > 0:
            raise IndexError
        retrieved_ids = get_profile_recommendations(profile_id, limit=max_amount)
        if len(retrieved_ids) < min_amount:
            raise IndexError
    except IndexError:
        """ get recommendation based on categories. Otherwise get random products """
        retrieved_ids = get_recommendations_on_categories_or_random(categories, max_amount)

    return retrieved_ids


def get_profile_recommendations(profile_id, limit=4):
    """ get recommendations based on profile """
    return profiles.get_recs(profile_id, limit)


def get_recommendations_on_categories_or_random(categories, limit):
    """ Get recommendations based on categories if they are not empty. Else return random products """
    return [e for e in database.get_based_on_categories(categories, limit)]


def get_anderen_kochten_ook(comparison_products, rec_limit, profile_id):
    """ get simple recommendations from products if the 'most_bought_together' and 'behaviour' algorithms do not suffice"""
    return page_cart.cart_alg_selection(rec_limit, comparison_products, profile_id)

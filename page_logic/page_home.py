import controller.database_controller as database
from algorithms import profiles, simple


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


def get_anderen_kochten_ook(comparison_products, rec_limit):
    """ get simple recommendations from products """
    recs = []
    for product in comparison_products:
        simple_recs = simple.get_recommendations(product.product_id)
        [recs.append(e) for e in simple_recs if len(recs) != rec_limit]
        if len(recs) == rec_limit:
            return recs

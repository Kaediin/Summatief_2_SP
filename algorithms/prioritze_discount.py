import random
import controller.database_controller as database
def run(recs, limit):
    """Give priority to recommendations with (higher) discounts"""
    if len(recs) > 4:
        # get all product_prices data from the DB
        price_data = database.execute_query(
            f"select * from product_prices",
            "")

        # select all the product prices from the cart where the discount is not none(we exclude None so we can use sorted() later)
        product_prices = [product_price for product_price in price_data if
                          product_price[0] in recs if product_price[1] is not None]

        # randomize the placement of these prices
        product_prices = (random.sample(product_prices, len(product_prices)))

        # sort the prices on discount
        sorted_product_prices = list(reversed(sorted(product_prices, key=lambda x: x[1])))

        # add prices where discount is None
        sorted_product_prices = sorted_product_prices + [product_price for product_price in price_data if
                                                         product_price[0] in recs if product_price[1] is None]

        # select product_ids
        recs = [x[0] for x in sorted_product_prices]

        # return limit product_ids
        return recs[:limit]
    else:
        return recs

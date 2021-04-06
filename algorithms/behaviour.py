def recommend(cart, cursor, limit=4):
    """
        Generate recommendations for items in a shopping cart, based on the similarities between the cart and other orders
    """

    # Get all of the products in all of the orders
    cursor.execute("select products from orders where cardinality(products) > 1")
    products = [set(e[0]) for e in cursor.fetchall()]

    # Sort the list of orders by how similar they are to the cart, and by how much the cart makes up of that order,
    # while simultaneously changing all orders to contain only products not found in the shopping cart
    cart = set(cart)
    products = sorted([e - cart for e in sorted(products, key=lambda e: len(cart & e))[::-1] if len(e - cart) > 0 and len(e & cart) >= 1], key=len)
    result = []

    # Fill the result with items from the changed products list, until the result contains a maximum number of items
    # equal to the given limit
    while len(result) < limit:
        if len(products) == 0:
            break

        order = products.pop(0)

        for p in order:
            if p not in result:
                result.append(p)
                if len(result) >= limit:
                    break

    return result

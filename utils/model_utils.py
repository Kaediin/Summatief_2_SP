def get_product_property(product_data, key):
    """Return the value of a property, returning none if no value is found"""
    try:
        return product_data[key]
    except KeyError:
        return None



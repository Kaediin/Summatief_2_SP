def get_product_property(product_data, key):
    try:
        return product_data[key]
    except KeyError:
        return None



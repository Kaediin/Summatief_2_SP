from model.product import Product
from controller import database_controller as database


def toProduct(tupl):
    # print(tupl)
    if type(tupl) == tuple:
        prod = Product(
            tupl[0],
            tupl[1],
            tupl[2],
            tupl[3],
            tupl[4],
            tupl[5],
            tupl[6],
            tupl[7],
            tupl[8],
            tupl[9],
            tupl[10],
            tupl[11],
            tupl[12],
            tupl[13],
            database.retrieve_properties("product_prices", {"product_id": f"{tupl[0]}"}, ("selling_price",))[0][0],
            database.retrieve_properties("product_prices", {"product_id": f"{tupl[0]}"}, ("discount",))[0][0],
        )

        return prod

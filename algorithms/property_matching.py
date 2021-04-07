import controller.database_controller as database


def fill_table_property_matching(cursor, connection):
    """create and fill a table based on the property_matching() function"""


    cursor.execute("select count(*) from property_matching_recs")
    hasEntries = True if cursor.fetchone()[0] > 0 else False


    if not hasEntries:


        cursor.execute(
            "select product_id from products"
        )
        data = cursor.fetchall()

        price_data = database.execute_query(
            f"""select pc.product_id , doelgroep , eenheid, factor, gebruik, geschiktvoor, geursoort, huidconditie,huidtype , huidtypegezicht , inhoud , klacht , kleur , leeftijd , serie, soort,soorthaarverzorging , soortmondverzorging , sterkte , type, typehaarkleuring , typetandenborstel , variant,waterproof , pc.category, sub_category, sub_sub_category, brand, gender
                                                        from product_properties pp
                                                        inner join product_categories pc on pc.product_id = pp.product_id
                                                        inner join products on products.product_id = pp.product_id """, "")

        # replacing ' with '' so LIKE in the sql statement doesn't crash
        id_list = [id[0].replace("'", "''") for id in data]

        for count, id in enumerate(id_list):
            data = (property_matching(id, 4, price_data))
            recs = data[0]
            weight = data[1]

            cursor.execute(
                f"insert into property_matching_recs (product_id,recommendations,weighted_match_rate) values(%s,%s,%s)",
                (id, recs, weight)
            )
            if count % 500 == 0 or count == len(id_list):
                connection.commit()
                print(f"Recommendations (Property matching): {count}/{len(id_list)}")

def property_matching(product_id, limit, price_data):
    """Look at all relevant product properties to decide the best matching recommendation, returns a list with a list of recs and an average match rate"""

    # column numbers have been divided in different weight classes, product properties have different weight in deciding what to recommend
    w2 = [3, 4, 7, 8, 9, 12, 13, 15, 16, 17, 18, 19, 20, 22, 24, 25, 27]
    w5 = [5, 11, 21, 23, 26, 28]

    try:
        product_id_properties = database.execute_query(
            f"""select pc.product_id , doelgroep , eenheid, factor, gebruik, geschiktvoor, geursoort, huidconditie,huidtype , huidtypegezicht , inhoud , klacht , kleur , leeftijd , serie, soort,soorthaarverzorging , soortmondverzorging , sterkte , type, typehaarkleuring , typetandenborstel , variant,waterproof , pc.category, sub_category, sub_sub_category, brand, gender
                                                               from product_properties pp
                                                               inner join product_categories pc on pc.product_id = pp.product_id
                                                               inner join products on products.product_id = pp.product_id
                                                               where pc.product_id like '{product_id}'""",
            "")[0]
    except IndexError:
        return [None,0]

    if(product_id_properties.count(None)==27):
        return [None,0]

    match_list = []
    for data in price_data:
        match_count = 0
        viable_match_len = 0
        for i in range(len(data)):
            # make sure we don't count None <-> None as a property match
            if not (data[i] is None or product_id_properties[i] is None):
                if data[i] != "}":

                    viable_match_len += 1
                    if data[i] == product_id_properties[i]:

                        if i in w2:
                            match_count += 2
                        elif i in w5:
                            match_count += 5
                        else:
                            match_count += 1
        match_list.append([data[0], match_count])

    # sort on match_count
    match_list = (list(reversed(sorted(match_list, key=lambda x: x[1]))))

    # change match_counts to a %-weighted-match scale
    scale_factor = float(100 / match_list[0][1])
    for index, x in enumerate(match_list):
        match_list[index][1] = round(x[1] * scale_factor, 2)

    # get the product_ids, exclude the best match(itself)
    recommendations = [match_list[1:][x][0] for x in range(limit)]

    avg_match = (round(sum([x[1] for x in match_list[1:limit + 1]]) / limit, 2))
    return [recommendations, avg_match]

# good example id 20157

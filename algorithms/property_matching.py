import controller.database_controller as database


def run(product_id, limit):
    """Look at all relevant product properties to decide the best matching recommendation, returns a list with a list of recs and an average match rate"""

    #column numbers have been divided in different weight classes, product properties have different weight in deciding what to recommend
    w2 = [3, 4, 7, 8, 9, 12, 13, 15, 16, 17, 18, 19, 20, 22,24,25,27]
    w5 = [5, 11, 21, 23,26,28]

    price_data = database.execute_query(f"""select pc.product_id , doelgroep , eenheid, factor, gebruik, geschiktvoor, geursoort, huidconditie,huidtype , huidtypegezicht , inhoud , klacht , kleur , leeftijd , serie, soort,soorthaarverzorging , soortmondverzorging , sterkte , type, typehaarkleuring , typetandenborstel , variant,waterproof , pc.category, sub_category, sub_sub_category, brand, gender
                                            from product_properties pp
                                            inner join product_categories pc on pc.product_id = pp.product_id
                                            inner join products on products.product_id = pp.product_id ""","")

    for data in price_data:
        if data[0] == product_id:
            product_id_properties = data
            break

    match_list = []
    for data in price_data:
        match_count = 0
        viable_match_len = 0
        for i in range(len(data)):
            #make sure we don't count None <-> None as a property match
            if not(data[i] is None or product_id_properties[i] is None):
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

    #sort on match_count
    match_list = (list(reversed(sorted(match_list, key=lambda x: x[1]))))

    #change match_counts to a %-weighted-match scale
    scale_factor = float(100/match_list[0][1])
    for index,x in enumerate(match_list):
        match_list[index][1] = round(x[1]* scale_factor,2)

    #get the product_ids, exclude the best match(itself)
    recommendations = [match_list[1:][x][0] for x in range(limit)]

    avg_match = (round(sum([x[1] for x in match_list[1:limit + 1]]) / limit))
    return [recommendations, avg_match]


#good example id 20157

print(run('20157',4))
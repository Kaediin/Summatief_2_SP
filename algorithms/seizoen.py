import psycopg2
import datetime
from collections import Counter


def get(date1, date2):
    try:
        connection = psycopg2.connect("dbname=postgres user=postgres password='38gAc57ip!'")
        cursor = connection.cursor()

        postgreSQL_select_Query = "SELECT product_id FROM product_categories, sessions WHERE sessions_profiles_id = browser_id AND starttime BETWEEN " + "'" + date1 + "'" + " AND " + "'" + date2 + "'"

        cursor.execute(postgreSQL_select_Query)
        print("Selecting rows table using cursor.fetchall")
        records = cursor.fetchall()
        print(records)

        return records

    except (Exception, psycopg2.Error) as error:
        print("Error while fetching data from PostgreSQL", error)


def insert_into_postgres(table, values):
    try:
        connection = psycopg2.connect("dbname=postgres user=postgres password='38gAc57ip!'")
        cursor = connection.cursor()

        if table == "visitor_id":
            cursor.execute("""INSERT INTO visitor_id VALUES({},{})""".format(values[0], values[1]))

        if table == "session_date":
            cursor.execute("""INSERT INTO session_date VALUES({},{})""".format(values[0], values[1]))

        if table == "most_bought_day":
            cursor.execute("""INSERT INTO most_bought_day VALUES({},{})""".format(values[0], values[1]))

        if table == "most_bought_period":
            cursor.execute("""INSERT INTO most_bought_period VALUES({},{})""".format(values[0], values[1]))

        connection.commit()
        count = cursor.rowcount
        print(count, "Record inserted successfully into table")

    except (Exception, psycopg2.Error) as error:
        print("Failed to insert record into table", error)


def time_periods():
    # Lente         = ("Lente", ("2018-03-01","2018-05-31"))
    # Zomer         = ("Zomer",("2018-06-01","2018-08-31"))
    # Herfst        = ("Herfst", ("2018-09-01", "2018-11-30"))
    # Winter        = ("Winter", ("2017-12-01", "2018-02-28"))
    # Sinterklaas   = ("Sinterklaas", ("2018-11-21", "2018-12-05"))
    # Kerst         = ("Kerst", ("2018-12-10", "2018-12-25"))

    periods = [("Lente", ("2018-03-01", "2018-05-31")), ("Zomer", ("2018-06-01", "2018-08-31")),
               ("Herfst", ("2018-09-01", "2018-11-30")),
               ("Winter", ("2017-12-01", "2018-02-28")), ("Sinterklaas", ("2018-11-21", "2018-12-05")),
               ("Kerst", ("2018-12-10", "2018-12-25"))]

    for i in periods:
        data = get(i[1][0], i[1][1])
        data = [item for item, in data]
        period_name = i[0]

        mostcommon = Counter(data).most_common(10)

        for x in mostcommon:
            insert_into_postgres("most_bought_period", (x[0], "'" + period_name + "'"))


time_periods()


def most_bought_daily():
    #   Je geeft 2 data op van de dagen waartussen je de records wil krijgen
    #   Wil je de records van 1 dag, bijvoorbeeld 2017-12-10 dan doe je get('2017-12-10', '2017-12-11').

    data = get('2017-12-18', '2017-12-19')
    dag = ("2017-12-18")
    data = [item for item, in data]
    print(data)

    #   Dit werkt niet, maar als de op=op voordeelshop nog echt zou opereren zou dit gebruikt kunnen worden
    #   In plaats van handmatig de dag in te voeren
    # dag_ = datetime.date.today()
    # dag_2 = datetime.date.today() + datetime.timedelta(days=1)
    # data_ = get(dag_, dag_2)
    # data_ = [item for item, in data_]

    mostcommon = Counter(data).most_common(3)
    print(mostcommon)
    for x in mostcommon:
        insert_into_postgres("most_bought_day", (x[0], "'" + dag + "'"))


most_bought_daily()

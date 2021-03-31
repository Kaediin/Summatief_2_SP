import psycopg2
import datetime
from collections import Counter


def run(cursor, connection):
    try:
        cursor.execute("select count(*) from seizoen_recs")
        hasEntries = True if cursor.fetchone()[0] > 0 else False
    except:
        connection.rollback()
        hasEntries = False

    if not hasEntries:
        try:
            cursor.execute("drop table if exists seizoen_recs")
            cursor.execute("create table seizoen_recs (visitor_id varchar primary key, session_date int, recommendations varchar[] null)")
            print("Table created")
        except psycopg2.errors.DuplicateTable:
            connection.rollback()
            print("Table already exists")

        cursor.execute("select visitor_id from visitors")

        ids = [e[0] for e in cursor.fetchall()]

        c = 0
        for i in ids:
            i = i.replace("'", "''")



'''

def session_date():
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

'''

import psycopg2
from config import config


def connect(sql, fields, returning):
    """ Connect to database tables """

    conn = None
    try:
        # read connection parameters
        params = config()

        # connect to the PostgreSQL server
        conn = psycopg2.connect(**params)

        # create a cursor
        cur = conn.cursor()

        # execute a statement
        cur.execute(sql, fields)

        conn.commit()
        # display the PostgreSQL database server version
        if returning:
            result = cur.fetchall()
            return [result]
        # close the communication with the PostgreSQL
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
        print(sql)
    finally:
        if conn is not None:
            conn.close()


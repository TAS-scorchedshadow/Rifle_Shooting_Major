import os
import psycopg2


def connect():
    DATABASE_URL = os.environ['DATABASE_URL']
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')


if __name__ == '__main__':
    connect()
import psycopg2

DB_NAME = "dwjfhvlj"
DB_USER = "dwjfhvlj"
DB_PASS = "8thg6lLwJuI00TJrJqd7bUAax05gNZDF"
DB_HOST = "topsy.db.elephantsql.com"
DB_PORT = "5432"

try:
    conn = psycopg2.connect(database=DB_NAME, user=DB_USER, password=DB_PASS,
                            host=DB_HOST, port=DB_PORT)

    print("Database connected successfully")
except:
    print("Database not connected")

cur = conn.cursor()
cur.execute("""

CREATE TABLE shooter
(
ID INT PRIMARY KEY NOT NULL,
NAME TEXT NOT NULL,
EMAIL TEXT NOT NULL

)
""")

conn.commit()
print("Table created successfully")
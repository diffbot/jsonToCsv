import sqlite3

connection = sqlite3.connect('guestbook.db')


with open('schema.sql') as f:
    connection.executescript(f.read())

cur = connection.cursor()

cur.execute("INSERT INTO posts (author, location, message) VALUES (?, ?, ?)",
            (
                'Jerome Choo',
                'Houston, TX',
                "I've always wanted to build a guestbook. But 12 year old Jerome never quite figured it out. Thanks for stopping by!")
            )

connection.commit()
connection.close()
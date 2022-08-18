import json
import sqlite3

connection = sqlite3.connect("/app/myapp/titles.sqlite3")
cursor = connection.cursor()

traffic = json.load(open("/app/fixtures/test.json"))
columns = ["artist", "title", "difficulty", "level", "released"]
for row in traffic:
    keys = tuple(row[c] for c in columns)
    print(keys)
    cursor.execute(
        "insert into titles (artist, title, difficulty, level,released) values(?,?,?,?,?)",
        keys,
    )
    print(f'{row["title"]} data inserted Succefully')

connection.commit()
connection.close()

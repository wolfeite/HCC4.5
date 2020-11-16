import sqlite3
import json
print("创建数据库")
conn = sqlite3.connect("data/db/test.db")
c = conn.cursor()
table = c.execute('''
    create table if not exists corp(id integer not null primary key autoincrement unique,
    name text,
    age int)
''')
print(">>>table", table, type(table), list(table))

c.execute("insert into corp(name,age) values(?,?)", ("wolfe", 25))
c.execute("insert into corp(name,age) values(:caller,:ages)", {"caller": "wolfeite", "ages": 35})

delRes = c.execute("DROP TABLE IF EXISTS corp2;")
print(">>>delRes", delRes, type(delRes), list(delRes))
creRes = c.execute('''create table if not exists corp2 (id,name,age)''')
print(">>>creRes", creRes, type(creRes), list(creRes))

c.execute('''
    create table if not exists corpJson (id int primary key,
    info json)
''')

# c.execute("insert or ignore into corpJson(info) values(?)", ('{"name": "wolfe"}'))
res = c.execute("select * from corpJson")
print(list(res))
for i in res:
    print("数据结果为：", json.loads(i[1])["name"])
conn.commit()
conn.close()

conn = sqlite3.connect("data/db/test.db")
conn.row_factory = sqlite3.Row
conn.execute('''
    create table if not exists login (id integer not null primary key autoincrement unique,
    time DATE DEFAULT (datetime('now','localtime')),
    tel int)
''')

conn.execute("insert into login(tel) values(?)", (137,))

c = conn.cursor()
print(">>c类型", c, type(c))
result = c.execute("select * from login")
print(">>", result, isinstance(result, sqlite3.Cursor))
res = c.fetchone()
print(">>", res["time"], c.rowcount, isinstance(res, sqlite3.Row))
res = c.fetchmany(-1)
print(">>", res[0]["time"], res)
res = c.fetchall()
print(">>查询所有的结果：", res, c.description)
conn.commit()
conn.close()

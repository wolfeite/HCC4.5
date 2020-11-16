# from .sqlite import process
from .sqlite.db import SqliteDb


def test():
    db = SqliteDb("data/db/test.db")
    table = db.model("Les", {
        "id": "integer not null primary key autoincrement unique",
        "name": "text",
        "count": "int"
    })

    table.insert([{
        "name": "化学",
        "count": 2
    }, {
        "name": "物理",
        "count": 5
    }])

    table.update([{"count": 6},{"count": 16}], clause="where name='化学'")

    res = table.find(("count"), clause="where name='物理'")
    print("查询结果：", res)

    table.delete(clause="where id=13")

    db.executor([
        "UPDATE Les SET count = 18 WHERE name = '化学';",
        ("UPDATE Les SET count = ? WHERE name = ?;",(59,"物理"))
    ])
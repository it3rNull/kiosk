import sqlite3
import json
# conn = sqlite3.connect("database.db")
# cur = conn.cursor()
# cur.execute("DROP TABLE orders")
# conn.commit()
# conn.close()
# conn = sqlite3.connect("database.db")
# conn.execute(
#     """
#     CREATE TABLE orders (
#     idx INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
#     table_num INTEGER,
#     menu_name TEXT,
#     price INTEGER,
#     time TEXT
# );
#     """)
# conn.close()

# conn = sqlite3.connect("database.db")
# cur = conn.cursor()
# cur.execute("DROP TABLE payments")
# conn.commit()
# conn.close()

# conn = sqlite3.connect("database.db")
# cur = conn.cursor()
# cur.execute(f"SELECT * FROM orders;")
# rows = cur.fetchall()
# print(rows)
# conn.commit()
# conn.close()

def drop_table():
    conn = sqlite3.connect("database.db")
    cur = conn.cursor()
    cur.execute("DROP TABLE menu")
    conn.commit()
    conn.close()

def create_menu_table():
    conn = sqlite3.connect("database.db")
    cur = conn.cursor()
    cur.execute("CREATE TABLE menu (menu_json TEXT)")
    conn.commit()
    conn.close()
    

def insert_menu():
    conn = sqlite3.connect("database.db")
    cur = conn.cursor()

    json_data = {
        "menus": [
            {
            "name" :"삼겹숙주볶음",
            "price" :13000,
            },
            {
            "name" :"골뱅이소면",
            "price" :12000,
            },
            {
            "name" :"오뎅탕",
            "price" :11000,
            },
            {
            "name" :"닭꼬치",
            "price" :9000,
            },
            {
            "name" :"황도",
            "price" :7000,
            },
            {
            "name" :"소주",
            "price" :4000,
            },
            {
            "name" :"맥주",
            "price" :4000,
            },
            {
            "name" :"토닉",
            "price" :5000,
            },
        ]
    }
    json_data = json.dumps(json_data)
    cur.execute("INSERT INTO menu (menu_json) VALUES (?)", (json_data,))
    conn.commit()
    conn.close()


def table_orders():
    conn = sqlite3.connect("database.db")
    cur = conn.cursor()
    cur.execute("DROP TABLE table_orders")
    cur.execute("CREATE TABLE table_orders (table_num INTEGER, tbl_orders TEXT, total_price INTEGER)")
    for table_num in range(1,41):
        js = {
            "삼겹숙주볶음" : 0,
            "골뱅이소면" : 0,
            "오뎅탕" : 0,
            "닭꼬치" : 0,
            "황도" : 0,
            "소주" : 0,
            "맥주" : 0,
            "토닉" : 0,
        }
        
        cur.execute("INSERT INTO table_orders (table_num, tbl_orders,total_price) VALUES (?,?,?)",(table_num,json.dumps(js),0,))

    conn.commit()
    conn.close()


# conn = sqlite3.connect('database.db')
# cur = conn.cursor()

# table_num = 1  # 예시로 테이블 번호 1로 설정
# cur.execute("UPDATE table_orders SET menu1 = 0, menu2 = 0, menu3 = 0, menu4 = 0, menu5 = 0, total_price = 0 WHERE table_num = ?", (table_num,))

# conn.commit()
# conn.close()


# table_orders 테이블 생성
# cur.execute("CREATE TABLE table_orders (table_num INTEGER PRIMARY KEY, menu1 INTEGER, menu2 INTEGER, menu3 INTEGER, menu4 INTEGER, menu5 INTEGER)")

# # table_num이 1부터 40까지이며 menu1,menu2,menu3,menu4,menu5값은 0인 row들을 추가

drop_table()
create_menu_table()
insert_menu()
table_orders()
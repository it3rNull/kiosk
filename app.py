from flask import Flask, render_template, request,redirect, url_for,send_file
import sqlite3
from flask_socketio import SocketIO, send,emit
from datetime import datetime, timedelta
import json
app = Flask(__name__)
app.config['SECRET_KEY'] = 'it3rNullsec!'
socketio = SocketIO(app)


@app.route('/')
def main():
    return render_template('index.html')


@app.route('/emergency',methods=["POST"])
def emergency():
    price = request.form['price']
    memo = request.form['memo']
    table_num = request.form['table_num']
    print(price,memo)
    now = datetime.now()
    now += timedelta(hours=9)
    time = now.strftime('%Y-%m-%d %H:%M:%S')
    conn = sqlite3.connect("database.db")
    cur = conn.cursor()
    cur.execute("INSERT INTO payments (table_num, total_price, time,memo) VALUES (?, ?, ?,?)", (table_num,price,time,memo))
    conn.commit()
    conn.close()
    return redirect(request.referrer)

@app.route('/download')
def download_file():
    # Replace 'path/to/file' with the actual path to the file you want to download
    file_path = 'resources/output.csv'
    
    # Specify the filename that will be used when the file is downloaded
    filename = 'output.csv'
    
    return send_file(file_path, as_attachment=True, download_name=filename)

@app.route('/orders')
def orders():
    conn = sqlite3.connect("database.db")
    cur = conn.cursor()
    cur.execute(f"SELECT * FROM orders;")
    rows = cur.fetchall()
    conn.commit()
    conn.close()
    return render_template('view.html', orders = rows)

@app.route('/menu/<category>', methods=['GET'])
def menu(category):
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    if category == '음료':
        cur.execute('SELECT * FROM orders WHERE menu_name = ? or menu_name = ?  ',('토닉','황도'))
    else:
        cur.execute('SELECT * FROM orders WHERE menu_name = ?', (category,))
    rows = cur.fetchall()
    conn.close()
    return render_template('view.html',orders=rows)


@app.route('/done')
def done():
    conn = sqlite3.connect("database.db")
    cur = conn.cursor()
    cur.execute(f"SELECT * FROM done_orders;")
    rows = cur.fetchall()
    print(rows)
    conn.commit()
    conn.close()
    return render_template('deleted.html', orders = rows,name='Done')

@app.route('/deleted')
def deleted():
    conn = sqlite3.connect("database.db")
    cur = conn.cursor()
    cur.execute(f"SELECT * FROM deleted_orders;")
    rows = cur.fetchall()
    print(rows)
    conn.commit()
    conn.close()
    return render_template('deleted.html', orders = rows,name='Deleted')

@app.route('/delete/<int:order_id>',methods=["GET","POST"])
def delete_order(order_id):
    if request.method == 'POST': 
        with sqlite3.connect('database.db') as con:
            cur = con.cursor()
            cur.execute("SELECT table_num, menu_name, time FROM orders WHERE idx = ?", (order_id,))
            order = cur.fetchone()
            now = datetime.now()
            now += timedelta(hours=9)
            cur.execute("INSERT INTO deleted_orders (table_num, menu, time,deleted_time) VALUES (?, ?, ?,?)", (order[0],order[1],order[2],now.strftime('%Y-%m-%d %H:%M:%S'),))
            con.commit()

        #orders 테이블에서 해당 주문을 삭제합니다.
        with sqlite3.connect('database.db') as con:
            cur = con.cursor()
            cur.execute("DELETE FROM orders WHERE idx = ?", (order_id,))
            con.commit()

    return redirect(request.referrer)
    #return redirect('/orders')

@app.route('/done_orders/<int:order_id>', methods=['POST'])
def done_orders(order_id):
    #삭제된 주문 정보를 done_orders 테이블에 추가합니다.
    with sqlite3.connect('database.db') as con:
        cur = con.cursor()
        cur.execute("SELECT table_num, menu_name, time FROM orders WHERE idx = ?", (order_id,))
        order = cur.fetchone()
        now = datetime.now()
        now += timedelta(hours=9)
        cur.execute("INSERT INTO done_orders (table_num, menu, time,done_time) VALUES (?, ?, ?,?)", (order[0],order[1],order[2],now.strftime('%Y-%m-%d %H:%M:%S'),))
        con.commit()

    #orders 테이블에서 해당 주문을 삭제합니다.
    with sqlite3.connect('database.db') as con:
        cur = con.cursor()
        cur.execute("DELETE FROM orders WHERE idx = ?", (order_id,))
        con.commit()

    return redirect(request.referrer)
    #return redirect('/orders')

@app.route('/tables')
def tables():
    conn = sqlite3.connect("database.db")
    cur = conn.cursor()
    cur.execute("SELECT total_price FROM table_orders")
    total_price = cur.fetchall()
    sum = 0
    for i in range(0,40):
        sum += total_price[i][0]
    conn.close()
    return render_template('tables.html',total_price=total_price,sum=sum)

@app.route('/kiosk/<int:table_num>')
def kiosk(table_num):
    conn = sqlite3.connect("database.db")
    cur = conn.cursor()
    cur.execute("SELECT * FROM menu")
    menu = json.loads(cur.fetchall()[0][0])
    print(menu)
    cur.execute("SELECT * from table_orders WHERE table_num = ?",(table_num,))
    tmp = cur.fetchall()[0]
    tbl_order = json.loads(tmp[1])
    total_price = tmp[2]
    print(tbl_order,total_price)
    conn.close()
    return render_template('kiosk.html', table_num=table_num, menu=menu,tbl_order=tbl_order,total_price=total_price)

@app.route('/add_order', methods=['POST'])
def add_order():
    table_num = request.form['table_num']
    menu_name = request.form['menu_name']
    price = request.form['price']
    now = datetime.now()
    now += timedelta(hours=9)
    time = now.strftime('%Y-%m-%d %H:%M:%S')
    conn = sqlite3.connect("database.db")
    cur = conn.cursor()
    cur.execute("INSERT INTO orders (table_num, menu_name, price,time) VALUES (?, ?, ?,?)", (table_num, menu_name, price,time))
    cur.execute("SELECT tbl_orders from table_orders WHERE table_num = ?",(table_num,))
    js = json.loads(cur.fetchall()[0][0])
    print('add',js)
    js[menu_name] += 1
    cur.execute("UPDATE table_orders SET tbl_orders = ? , total_price = total_price + ? WHERE table_num = ?",(json.dumps(js),price,table_num,))
    conn.commit()
    conn.close()
    return redirect(request.referrer)

@app.route('/add_chicken', methods=['POST'])
def add_chicken():
    table_num = request.form['table_num']
    menu_name = request.form['menu_name']
    price = int(request.form['price'])
    toppings = request.form.getlist('toppings[]')
    if '토핑추가' in toppings:
        price += 2000
    toppings = ','.join(toppings)
    now = datetime.now()
    now += timedelta(hours=9)
    time = now.strftime('%Y-%m-%d %H:%M:%S')
    conn = sqlite3.connect("database.db")
    cur = conn.cursor()
    cur.execute("INSERT INTO orders (table_num, menu_name, price,time,etc) VALUES (?, ?, ?,?,?)", (table_num, menu_name, price,time,toppings))
    cur.execute("SELECT tbl_orders from table_orders WHERE table_num = ?",(table_num,))
    js = json.loads(cur.fetchall()[0][0])
    print('add',js)
    js[menu_name] += 1
    cur.execute("UPDATE table_orders SET tbl_orders = ? , total_price = total_price + ? WHERE table_num = ?",(json.dumps(js),price,table_num,))
    conn.commit()
    conn.close()
    return redirect(request.referrer)

@app.route('/add_deliver', methods=['POST'])
def add_deliver():
    table_num = request.form['table_num']   
    menu_name = request.form['menu_name']
    price = int(request.form['price'])
    toppings = request.form.getlist('toppings[]')
    if '토핑추가' in toppings:
        price += 2000
    toppings = ','.join(toppings)
    now = datetime.now()
    now += timedelta(hours=9)
    time = now.strftime('%Y-%m-%d %H:%M:%S')
    conn = sqlite3.connect("database.db")
    cur = conn.cursor()
    js = {
        menu_name : 1,
    }
    cur.execute("INSERT INTO orders (table_num, menu_name, price,time,etc) VALUES (?, ?, ?,?,?)", (table_num, menu_name, price,time,toppings))
    cur.execute("INSERT INTO payments (table_num, total_price, time,memo,detail) VALUES (?, ?, ?,?,?)", (table_num,price,time,'포장계산',json.dumps(js)))
    conn.commit()
    conn.close()
    return redirect(request.referrer)
    

@app.route('/inc',methods=['POST'])
def inc():
    table_num = request.form['table_num']
    menu_name = request.form['menu_name']
    price = int(request.form['price'])
    conn = sqlite3.connect("database.db")
    cur = conn.cursor()
    cur.execute("SELECT * from table_orders WHERE table_num = ?",(table_num,))
    tbl = cur.fetchall()[0]
    tmp = json.loads(tbl[1])
    tmp[menu_name] += 1
    ttl = tbl[2]
    ttl += price
    tbl = json.dumps(tmp)
    cur.execute("UPDATE table_orders SET tbl_orders = ?, total_price =? WHERE table_num = ?",(tbl,ttl,table_num,))
    conn.commit()
    conn.close()
    return redirect(request.referrer)

@app.route('/dec',methods=['POST'])
def dec():
    table_num = request.form['table_num']
    menu_name = request.form['menu_name']
    price = int(request.form['price'])
    conn = sqlite3.connect("database.db")
    cur = conn.cursor()
    cur.execute("SELECT * from table_orders WHERE table_num = ?",(table_num,))
    tbl = cur.fetchall()[0]
    tmp = json.loads(tbl[1])
    tmp[menu_name] -= 1
    ttl = tbl[2]
    ttl -= price
    tbl = json.dumps(tmp)
    cur.execute("UPDATE table_orders SET tbl_orders = ?, total_price =? WHERE table_num = ?",(tbl,ttl,table_num,))
    conn.commit()
    conn.close()
    return redirect(request.referrer)


@app.route('/pay',methods=["GET","POST"])
def pay():
    if request.method == 'POST': 
        table_num = request.form['table_num']
        total_price = request.form['total_price']
        now = datetime.now()
        now += timedelta(hours=9)
        time = now.strftime('%Y-%m-%d %H:%M:%S')
        with sqlite3.connect('database.db') as con:
            cur = con.cursor()
            cur.execute("SELECT tbl_orders from table_orders WHERE table_num = ?",(table_num,))
            tmp = cur.fetchone()[0]
            print('hi',tmp)
            cur.execute("INSERT INTO payments (table_num, total_price, time,memo,detail) VALUES (?, ?, ?,?,?)", (table_num,total_price,time,'테이블계산',tmp))
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
            cur.execute("UPDATE table_orders SET tbl_orders = ?, total_price = 0 WHERE table_num = ?", (json.dumps(js),table_num,))
            con.commit()
    return redirect(request.referrer)

@app.route('/payments')
def payments():
    conn = sqlite3.connect("database.db")
    cur = conn.cursor()
    cur.execute("SELECT * FROM payments;")
    rows = cur.fetchall()
    cur.execute("SELECT detail FROM payments;")
    detail = cur.fetchall()
    print(detail)
    cur.execute("SELECT SUM(total_price) FROM payments;")
    sum = cur.fetchone()[0]
    conn.commit()
    conn.close()
    return render_template('payments.html', orders = rows,name='Payments',sum = sum)

@app.route('/pay_details/<time>', methods=['GET'])
def pay_details(time):
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    cur.execute("SELECT detail FROM payments where time = ?",(time,))
    detail = json.loads(cur.fetchone()[0])
    print(detail)
    conn.commit()
    conn.close()
    return render_template('detail.html',js=detail)




if __name__ == '__main__':
    app.run(host='0.0.0.0',port=80)
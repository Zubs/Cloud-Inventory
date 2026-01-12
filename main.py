from flask import Flask, render_template,request,url_for
import mysql.connector

app = Flask(__name__)

# con = mysql.connector.connect(host='localhost', user='root', password='', database='inventory')
con = mysql.connector.connect(
    host="127.0.0.1",
    user="root",
    password="password",  
    database="sample"     
)
cur = con.cursor()

@app.route('/')
def home():
    cur = con.cursor(dictionary=True)

    # 1. Get ALL items to iterate over in the dashboard
    cur.execute("SELECT * FROM items")
    items = cur.fetchall()

    # 2. Get Order Summaries (Still useful for top-level stats)
    cur.execute("SELECT status, COUNT(*) as count FROM orders GROUP BY status")
    order_rows = cur.fetchall()

    # 3. Calculate Totals for the "Stats" section
    order_stats = {row['status']: row['count'] for row in order_rows}
    total_stock = sum(item['quantity'] for item in items)
    total_orders = sum(order_stats.values())

    items_in_production = sum(item['quantity'] for item in items if item['status'] == 'In Production')
    items_ready = sum(item['quantity'] for item in items if item['status'] == 'Ready')

    return render_template(
        'index.html',
        items=items,
        orders=order_stats,
        total_stock=total_stock,
        total_orders=total_orders,
        items_in_production=items_in_production,
        items_ready=items_ready)

# @app.route('/update')
# def update():

#     cur.execute("SELECT * FROM data")
#     data = cur.fetchall()

#     return render_template('update.html', units = data[-1])

@app.route('/update')
def update_page():
    # We need to fetch items here too, so the dropdown menu works!
    cur = con.cursor(dictionary=True)
    cur.execute("SELECT * FROM items")
    items = cur.fetchall()
    con.close()
    
    return render_template('update.html', items=items)

@app.route('/login')
def login():

    return render_template('login.html')

@app.route('/fetch',methods = ['POST'])
def fetch():
    book1 = request.form.get('book1')
    book2 = request.form.get('book2')
    book3 = request.form.get('book3')
    oders = request.form.get('oders')
    pending = request.form.get('pending')
    complete = request.form.get('complete')
    print = request.form.get('print')
    production = request.form.get('production')
    ready = request.form.get('ready')


    cur.execute("""INSERT INTO `data` (`book1`, `book2`, `book3`, `oders`, `oder pending`, `complete oders`, `books in printing`, `books in production`, `books ready`) VALUES ({}, {},{},{},{},{},{},{},{});""".format(book1,book2,book3,oders,pending,complete,print,production,ready))
    con.commit()
    cur.execute("SELECT * FROM data")
    data = cur.fetchall()

    return render_template('index.html', units = data[-1])

@app.route('/validation',methods = ['POST'])
def val():
    email = request.form.get('email')
    passw = request.form.get('password')

    cur.execute("SELECT * FROM data")
    data = cur.fetchall()

    try:
        cur.execute("""INSERT INTO `user` (`user id`,`email`,`password`) VALUES (NULL,{},{});""".format(email,passw))
        con.commit()
    except:
        return render_template('update.html', units = data[-1])

    return render_template('update.html', units = data[-1])

@app.route('/add_user', methods=['POST'])
def add_user():
    name = request.form['name']
    email = request.form['email']
    sql = "INSERT INTO users (name, email) VALUES (%s, %s)"
    val = (name, email)
    cursor.execute(sql, val)
    db.commit()
    return "User added successfully!"

if __name__=='__main__':
    app.run(debug = True)
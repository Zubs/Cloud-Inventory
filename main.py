import os
import boto3
from dotenv import load_dotenv
from flask import Flask, render_template, request, url_for, redirect
import mysql.connector

app = Flask(__name__)

db_config = {
    'host': os.getenv('DB_HOST', '127.0.0.1'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', 'password'),
    'database': os.getenv('DB_DATABASE', 'sample')
}

def get_db_connection():
    conn = mysql.connector.connect(**db_config)
    conn.autocommit = True
    return conn

sns_client = boto3.client(
    'sns',
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
    region_name=os.getenv('AWS_REGION')
)
SNS_TOPIC_ARN = os.getenv('SNS_TOPIC_ARN')

def check_and_alert_low_inventory(item_id, new_quantity):
    """
    Checks if an item's quantity is below threshold (e.g., 5).
    If so, sends an email via AWS SNS.
    """
    THRESHOLD = 5
    
    if int(new_quantity) < THRESHOLD:
        try:
            # Fetch item name for the message
            con = get_db_connection()
            cur = con.cursor(dictionary=True)
            cur.execute("SELECT name FROM items WHERE id = %s", (item_id,))
            item = cur.fetchone()
            con.close()
            
            if item:
                message = f"URGENT: Inventory Low!\n\nItem: {item['name']}\nRemaining Quantity: {new_quantity}\n\nPlease restock immediately."
                
                sns_client.publish(
                    TopicArn=SNS_TOPIC_ARN,
                    Message=message,
                    Subject=f"Low Inventory Alert: {item['name']}"
                )
                print(f"Alert sent for {item['name']}")
                
        except Exception as e:
            print(f"Failed to send SNS alert: {e}")

@app.route('/')
def home():
    con = get_db_connection()
    cur = con.cursor(dictionary=True)

    # 1. Get ALL items to iterate over in the dashboard
    cur.execute("SELECT * FROM items")
    items = cur.fetchall()

    # 2. Get Order Summaries (Still useful for top-level stats)
    cur.execute("SELECT status, COUNT(*) as count FROM orders GROUP BY status")
    order_rows = cur.fetchall()

    con.close()

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

@app.route('/manage')
def manage():
    con = get_db_connection()
    cur = con.cursor(dictionary=True)

    # 1. Fetch Items
    cur.execute("SELECT * FROM items")
    items = cur.fetchall()

    # 2. Fetch Orders (Joined with Item Name for display)
    cur.execute("""
        SELECT orders.id, orders.quantity, orders.status, items.name as item_name 
        FROM orders 
        LEFT JOIN items ON orders.item_id = items.id
    """)
    orders = cur.fetchall()

    # 3. Fetch Users
    cur.execute("SELECT * FROM user")
    users = cur.fetchall()

    con.close()

    return render_template('manage.html', items=items, orders=orders, users=users)

@app.route('/delete_item/<int:id>')
def delete_item(id):
    con = get_db_connection()
    cur = con.cursor()
    try:
        cur.execute("DELETE FROM items WHERE id = %s", (id,))
        con.commit()
    except mysql.connector.Error as err:
        print("Error: ", err) # Handle foreign key constraints if needed

    con.close()
    return redirect(url_for('manage'))

@app.route('/delete_order/<int:id>')
def delete_order(id):
    con = get_db_connection()
    cur = con.cursor()
    cur.execute("DELETE FROM orders WHERE id = %s", (id,))
    con.commit()
    con.close()

    return redirect(url_for('manage'))

@app.route('/delete_user/<int:id>')
def delete_user(id):
    con = get_db_connection()
    cur = con.cursor()
    cur.execute("DELETE FROM user WHERE id = %s", (id,))
    con.commit()
    con.close()

    return redirect(url_for('manage'))

@app.route('/update_item', methods=['POST'])
def update_item():
    id = request.form.get('id')
    name = request.form.get('name')
    quantity = request.form.get('quantity')
    status = request.form.get('status')
    
    con = get_db_connection()
    cur = con.cursor()
    cur.execute("UPDATE items SET name=%s, quantity=%s, status=%s WHERE id=%s", (name, quantity, status, id))
    con.commit()
    con.close()

    check_and_alert_low_inventory(id, quantity)

    return redirect(url_for('manage'))

@app.route('/update_order', methods=['POST'])
def update_order():
    id = request.form.get('id')
    quantity = request.form.get('quantity')
    status = request.form.get('status')
    
    con = get_db_connection()
    cur = con.cursor()
    cur.execute("UPDATE orders SET quantity=%s, status=%s WHERE id=%s", (quantity, status, id))
    con.commit()
    con.close()

    return redirect(url_for('manage'))

@app.route('/update_user', methods=['POST'])
def update_user():
    id = request.form.get('id')
    email = request.form.get('email')
    password = request.form.get('password') # In production, hash this!
    
    con = get_db_connection()
    cur = con.cursor()
    cur.execute("UPDATE user SET email=%s, password=%s WHERE id=%s", (email, password, id))
    con.commit()
    con.close()

    return redirect(url_for('manage'))

@app.route('/add_item', methods=['POST'])
def add_item():
    name = request.form.get('name')
    quantity = request.form.get('quantity')
    status = request.form.get('status')
    
    cur = con.cursor()
    cur.execute("INSERT INTO items (name, quantity, status) VALUES (%s, %s, %s)", (name, quantity, status))
    con.commit()
    con.close()

    return redirect(url_for('manage'))

@app.route('/add_order', methods=['POST'])
def add_order():
    item_id = request.form.get('item_id')
    quantity = request.form.get('quantity')
    status = request.form.get('status')
    
    con = get_db_connection()
    cur = con.cursor(dictionary=True)
    cur.execute("SELECT quantity FROM items WHERE id = %s", (item_id,))
    item = cur.fetchone()

    if item:
        current_stock = item['quantity']
        new_stock = current_stock - int(quantity)

        cur.execute("UPDATE items SET quantity = %s WHERE id = %s", (new_stock, item_id))
        cur.execute("INSERT INTO orders (item_id, quantity, status) VALUES (%s, %s, %s)", (item_id, quantity, status))
        con.commit()

        check_and_alert_low_inventory(item_id, new_stock)

    con.close()

    return redirect(url_for('manage'))

@app.route('/add_user', methods=['POST'])
def add_user():
    email = request.form.get('email')
    password = hash(request.form.get('password'))
    
    con = get_db_connection()
    cur = con.cursor()
    cur.execute("INSERT INTO user (email, password) VALUES (%s, %s)", (email, password))
    con.commit()
    con.close()

    return redirect(url_for('manage'))

if __name__=='__main__':
    app.run(debug = True, host='0.0.0.0', port=5001)
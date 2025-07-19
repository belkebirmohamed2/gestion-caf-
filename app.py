from flask import Flask, render_template, request, redirect, url_for, jsonify
from datetime import datetime
import sqlite3

app = Flask(__name__)



def init_db():
    conn = sqlite3.connect('orders.db')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            table_number INTEGER NOT NULL,
            num_people INTEGER NOT NULL,
            items TEXT NOT NULL,
            total_price REAL NOT NULL,
            timestamp TEXT NOT NULL
        )
    ''')

    conn.commit()
    conn.close()

# دالة لإنشاء قاعدة البيانات إذا لم تكن موجودة
def init_db():
    conn = sqlite3.connect('cafe.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            table_number INTEGER,
            num_people INTEGER,
            items TEXT,
            total_price REAL,
            timestamp TEXT
        )
    ''')
    conn.commit()
    conn.close()

# إنشاء جدول المخزون إذا لم يكن موجوداً
# دالة لإنشاء قاعدة البيانات إذا لم تكن موجودة
# إنشاء جدول المخزون إذا لم يكن موجوداً
def init_db():
    conn = sqlite3.connect('stoke01.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS stock (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_name TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            unit TEXT NOT NULL,
            last_updated TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()


def init_db():
    conn = sqlite3.connect('revenus01.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS revenus (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            description TEXT NOT NULL,
            amount REAL NOT NULL,
            date TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def init_db():
    conn = sqlite3.connect('depenses01.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS depenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            description TEXT NOT NULL,
            amount REAL NOT NULL,
            date TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def init_db():
    conn = sqlite3.connect('daily_summary.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS summary (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            day TEXT NOT NULL,
            revenus REAL DEFAULT 0,
            depenses REAL DEFAULT 0,
            benefices REAL DEFAULT 0
        )
    ''')
    conn.commit()
    conn.close()
# تشغيل إنشاء قاعدة البيانات عند بداية التشغيل
init_db()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/propos')
def propos():
    return render_template('propos.html')

@app.route('/tables')
def tables():
    return render_template('tables.html')

@app.route('/confirm_order', methods=['POST'])
def confirm_order():
    data = request.get_json()
    conn = sqlite3.connect('cafe.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO orders (table_number, num_people, items, total_price, timestamp)
        VALUES (?, ?, ?, ?, ?)
    ''', (
        data['table_number'],
        data['num_people'],
        data['items'],
        data['total_price'],
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))
    conn.commit()
    conn.close()
    return jsonify({"status": "success"})
#@app.route('/menu')
#def menu():
    #return render_template('menu.html')

# صفحة الطلب لطاولة معينة
@app.route('/menu/<int:table_id>', methods=['GET', 'POST'])
def menu(table_id):
    if request.method == 'POST':
        num_people = int(request.form['num_people'])
        selected_items = request.form.getlist('items')
        total_price = float(request.form['total_price'])
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        conn = sqlite3.connect('orders.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO orders (table_number, num_people, items, total_price, timestamp)
            VALUES (?, ?, ?, ?, ?)
        ''', (table_id, num_people, ', '.join(selected_items), total_price, timestamp))
        conn.commit()
        conn.close()

        return redirect(url_for('orders'))

    return render_template('menu.html', table_id=table_id)

# عرض الطلبات المؤكدة
from collections import Counter

def get_sold_products(orders):
    counter = Counter()
    for order in orders:
        # مثال: order['items'] = "قهوة × 2, شاي × 1"
        for item in order['items'].split(','):
            parts = item.strip().split('×')
            if len(parts) == 2:
                name = parts[0].strip()
                try:
                    count = int(parts[1].strip())
                except ValueError:
                    count = 1
                counter[name] += count
    return [{'name': k, 'count': v} for k, v in counter.items()]
@app.route('/orders')
def view_orders():
    conn = sqlite3.connect('cafe.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    # جلب الطلبات الخاصة بيوم اليوم فقط
    today = datetime.now().strftime("%Y-%m-%d")
    c.execute("SELECT * FROM orders WHERE DATE(timestamp) = ?", (today,))
    orders = c.fetchall()

    total = sum(order['total_price'] for order in orders)
    
    # حساب المنتجات المباعة
    sold_products = get_sold_products(orders)
    
    conn.close()
    
    return render_template("orders.html", orders=orders, total=total, sold_products=sold_products)

# ✅ عرض صفحة المخزون
@app.route("/stock")
def stock():
    conn = sqlite3.connect("stoke01.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM stock")
    items = cursor.fetchall()
    conn.close()
    return render_template("stock.html", items=items)

# ✅ إضافة عنصر جديد إلى المخزون
@app.route("/add_stock", methods=["POST"])
def add_stock():
    item_name = request.form["item_name"]
    quantity = int(request.form["quantity"])
    unit = request.form["unit"]
    last_updated = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    conn = sqlite3.connect("stoke01.db")
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO stock (item_name, quantity, unit, last_updated) VALUES (?, ?, ?, ?)",
        (item_name, quantity, unit, last_updated)
    )
    conn.commit()
    conn.close()
    return redirect(url_for("stock"))

# ✅ تعديل كمية عنصر موجود
@app.route("/update_stock/<int:item_id>", methods=["POST"])
def update_stock(item_id):
    new_quantity = int(request.form["new_quantity"])
    last_updated = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    conn = sqlite3.connect("stoke01.db")
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE stock SET quantity = ?, last_updated = ? WHERE id = ?",
        (new_quantity, last_updated, item_id)
    )
    conn.commit()
    conn.close()
    return redirect(url_for("stock"))

# ✅ حذف عنصر من المخزون
@app.route("/delete_stock/<int:item_id>")
def delete_stock(item_id):
    conn = sqlite3.connect("stoke01.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM stock WHERE id = ?", (item_id,))
    conn.commit()
    conn.close()
    return redirect(url_for("stock"))
#مسار الصفحة
@app.route('/revenus')
def revenus():
    conn = sqlite3.connect("revenus01.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM revenus")
    data = cursor.fetchall()
    conn.close()

    total = sum(row[2] for row in data)
    return render_template("revenus.html", revenus=data, total=total)
#إضافة الإيراد
@app.route('/add_revenu', methods=["POST"])
def add_revenu():
    description = request.form["description"]
    amount = float(request.form["amount"])
    date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    conn = sqlite3.connect("revenus01.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO revenus (description, amount, date) VALUES (?, ?, ?)", (description, amount, date))
    conn.commit()
    conn.close()
    return redirect(url_for("revenus"))
#حذف الإيراد
@app.route('/delete_revenu/<int:revenu_id>')
def delete_revenu(revenu_id):
    conn = sqlite3.connect("revenus01.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM revenus WHERE id = ?", (revenu_id,))
    conn.commit()
    conn.close()
    return redirect(url_for("revenus"))

#صفحة المصاريف
@app.route('/depenses')
def depenses():
    conn = sqlite3.connect("depenses01.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM depenses")
    data = cursor.fetchall()
    conn.close()

    total = sum(row[2] for row in data)
    return render_template("depenses.html", depenses=data, total=total)

#إضافة مصروف جديد
@app.route('/add_depense', methods=["POST"])
def add_depense():
    description = request.form["description"]
    amount = float(request.form["amount"])
    date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    conn = sqlite3.connect("depenses01.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO depenses (description, amount, date) VALUES (?, ?, ?)", (description, amount, date))
    conn.commit()
    conn.close()
    return redirect(url_for("depenses"))

#حذف مصروف
@app.route('/delete_depense/<int:depense_id>')
def delete_depense(depense_id):
    conn = sqlite3.connect("depenses01.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM depenses WHERE id = ?", (depense_id,))
    conn.commit()
    conn.close()
    return redirect(url_for("depenses"))


@app.route('/benefices')
def benefices():
    # قراءة الإيرادات
    conn_revenus = sqlite3.connect("revenus01.db")
    cursor_revenus = conn_revenus.cursor()
    cursor_revenus.execute("SELECT SUM(amount) FROM revenus")
    total_revenus = cursor_revenus.fetchone()[0] or 0
    conn_revenus.close()

    # قراءة المصاريف
    conn_depenses = sqlite3.connect("depenses01.db")
    cursor_depenses = conn_depenses.cursor()
    cursor_depenses.execute("SELECT SUM(amount) FROM depenses")
    total_depenses = cursor_depenses.fetchone()[0] or 0
    conn_depenses.close()

    # حساب صافي الأرباح
    benefice_net = total_revenus - total_depenses

    return render_template("benefices.html", revenus=total_revenus, depenses=total_depenses, benefices=benefice_net)

@app.route('/summary')
def summary():
    today = datetime.now().strftime("%Y-%m-%d")

    # قراءة مجموع الإيرادات لهذا اليوم
    conn_revenus = sqlite3.connect("revenus01.db")
    cursor_revenus = conn_revenus.cursor()
    cursor_revenus.execute("SELECT SUM(amount) FROM revenus WHERE DATE(date) = ?", (today,))
    total_revenus = cursor_revenus.fetchone()[0] or 0
    conn_revenus.close()

    # قراءة مجموع المصاريف لهذا اليوم
    conn_depenses = sqlite3.connect("depenses01.db")
    cursor_depenses = conn_depenses.cursor()
    cursor_depenses.execute("SELECT SUM(amount) FROM depenses WHERE DATE(date) = ?", (today,))
    total_depenses = cursor_depenses.fetchone()[0] or 0
    conn_depenses.close()

    benefices = total_revenus - total_depenses

    # فتح قاعدة بيانات summary
    conn = sqlite3.connect("daily_summary.db")
    cursor = conn.cursor()

    # التحقق هل هذا اليوم موجود أصلاً
    cursor.execute("SELECT * FROM summary WHERE day = ?", (today,))
    data = cursor.fetchone()

    # إذا لم يكن موجود، نقوم بإدخاله
    if not data:
        cursor.execute("INSERT INTO summary (day, revenus, depenses, benefices) VALUES (?, ?, ?, ?)",
                       (today, total_revenus, total_depenses, benefices))
        conn.commit()

    # الآن نقرأ كل الجدول لعرضه
    cursor.execute("SELECT * FROM summary ORDER BY day DESC")
    all_summaries = cursor.fetchall()
    conn.close()

    return render_template("summary.html", summaries=all_summaries)

@app.route('/add_summary', methods=["POST"])
def add_summary():
    day = request.form["day"]
    revenus = float(request.form["revenus"])
    depenses = float(request.form["depenses"])
    benefices = revenus - depenses

    conn = sqlite3.connect("daily_summary.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO summary (day, revenus, depenses, benefices) VALUES (?, ?, ?, ?)",
                   (day, revenus, depenses, benefices))
    conn.commit()
    conn.close()
    return redirect(url_for("summary"))

@app.route('/delete_summary/<int:id>')
def delete_summary(id):
    conn = sqlite3.connect("daily_summary.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM summary WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for("summary"))

@app.route('/search_summary', methods=["POST"])
def search_summary():
    day = request.form["search_day"]
    conn = sqlite3.connect("daily_summary.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM summary WHERE day = ?", (day,))
    data = cursor.fetchall()
    conn.close()
    return render_template("summary.html", summaries=data)

if __name__ == '__main__':
    app.run(debug=True)


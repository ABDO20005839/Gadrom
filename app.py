from flask import Flask, render_template, request, redirect, url_for, session
from flask_socketio import SocketIO, emit
from datetime import datetime
import json, os

app = Flask(__name__)
app.secret_key = 'bazooka_secret_2024'
socketio = SocketIO(app, cors_allowed_origins="*")

ORDERS_FILE = 'orders.json'

MENU = [
    {"id": 1,  "name": "عرض الأحد للثلاثاء",    "desc": "6 قطع فرايد تشيكن بدون أجنحة + 2 عيش",               "price": 275, "emoji": "🍗"},
    {"id": 2,  "name": "ديل القرمشة",            "desc": "6قطع بروست+2كول سلو+2خز+2ارز وسط بسماي",            "price": 380, "emoji": "🔥"},
    {"id": 3,  "name": "بوكس فلاش",              "desc": "2ساندوتش سنجل تشيكن اوبرجر+2فرايز",                 "price": 260, "emoji": "📦"},
    {"id": 4,  "name": "فلاش القرمشة",           "desc": "3 قطع +اعيش + كول سلو — خصم 50٪ لفترة محدودة",      "price": 185, "emoji": "⏳"},
    {"id": 5,  "name": "فلاش سكريت",             "desc": "4قطع + 1عيش — عرض مش هيتكرر!",                      "price": 220, "emoji": "🌶️"},
    {"id": 6,  "name": "فلاش ميكس",              "desc": "3قطع فرايد تشيكن + ساندوتش سنجل او ساندوتش بيف",    "price": 299, "emoji": "⭐"},
    {"id": 7,  "name": "فلاش استريس",            "desc": "8قطع استريس+3خز",                                    "price": 299, "emoji": "💥"},
    {"id": 8,  "name": "لمة الصحاب (9 قطعة)",   "desc": "9قطع دجاج+3كول سلو وسط+3خز",                        "price": 525, "emoji": "👥"},
    {"id": 9,  "name": "شير كومبو سنجل",         "desc": "ساندوتش تشكن او بيف + ساندوتش برجر تشكن او بيف",    "price": 200, "emoji": "🤝"},
    {"id": 10, "name": "ملوك السعادة (4قطعة)",  "desc": "4قطع دجاج+ارز+كول سلو وسط+قطعة خز+مشروب",          "price": 270, "emoji": "👑"},
    {"id": 11, "name": "دويتو 1 (6 قطع)",        "desc": "6قطع دجاج+2 كول سلو وسط+2خز",                       "price": 320, "emoji": "🎵"},
    {"id": 12, "name": "كومبو ديل",              "desc": "ساندوتش ديل تشكن او بيف+فرايز وسط+مشروب",           "price": 240, "emoji": "🍔"},
]

CASHIER_USERS = ['escor']   # any password accepted

def load_orders():
    if os.path.exists(ORDERS_FILE):
        with open(ORDERS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_orders(orders):
    with open(ORDERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(orders, f, ensure_ascii=False, indent=2)

# ── Routes ────────────────────────────────────────────────────────────────────

@app.route('/')
def index():
    return render_template('index.html', menu=MENU)

@app.route('/cashtarhar', methods=['GET', 'POST'])
def cashier_login():
    if session.get('cashier'):
        return redirect(url_for('cashier_dashboard'))
    error = None
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        if username in CASHIER_USERS and password:
            session['cashier'] = username
            return redirect(url_for('cashier_dashboard'))
        error = 'اسم المستخدم أو كلمة المرور غير صحيحة'
    return render_template('cashier_login.html', error=error)

@app.route('/cashtarhar/dashboard')
def cashier_dashboard():
    if not session.get('cashier'):
        return redirect(url_for('cashier_login'))
    orders = sorted(load_orders(), key=lambda x: x['id'], reverse=True)
    return render_template('cashier_dashboard.html', orders=orders, cashier=session['cashier'])

@app.route('/cashtarhar/logout')
def cashier_logout():
    session.pop('cashier', None)
    return redirect(url_for('cashier_login'))

# ── Socket.IO Events ──────────────────────────────────────────────────────────

@socketio.on('place_order')
def handle_place_order(data):
    customer_name = data.get('customer_name', '').strip()
    items = data.get('items', [])
    if not customer_name or not items:
        emit('order_error', {'message': 'بيانات ناقصة'})
        return
    orders = load_orders()
    order = {
        'id': len(orders) + 1,
        'customer_name': customer_name,
        'items': items,
        'total': sum(i['price'] * i['qty'] for i in items),
        'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'status': 'pending'
    }
    orders.append(order)
    save_orders(orders)
    emit('order_confirmed', {'order_id': order['id']})
    socketio.emit('new_order', order)          # broadcast to all cashiers

@socketio.on('update_status')
def handle_update_status(data):
    orders = load_orders()
    updated = None
    for o in orders:
        if o['id'] == data['order_id']:
            o['status'] = data['status']
            updated = o
            break
    if updated:
        save_orders(orders)
        socketio.emit('order_status_changed', {'order_id': updated['id'], 'status': updated['status']})
        if updated['status'] == 'done':
            socketio.emit('order_ready', {'order_id': updated['id'], 'customer_name': updated['customer_name']})

@socketio.on('delete_order')
def handle_delete_order(data):
    orders = load_orders()
    orders = [o for o in orders if o['id'] != data['order_id']]
    save_orders(orders)
    socketio.emit('order_deleted', {'order_id': data['order_id']})

if __name__ == '__main__':
    socketio.run(app, debug=True, port=5000)

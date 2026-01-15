import threading
import time
import socket
import speedtest
import requests
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from ping3 import ping

app = Flask(__name__)
app.config['SECRET_KEY'] = 'netwatch-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///netwatch.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
socketio = SocketIO(app, cors_allowed_origins='*', async_mode='threading')

# --- CONFIG ---
TELEGRAM_TOKEN = 'MASUKKAN_TOKEN_DISINI'
TELEGRAM_CHAT_ID = 'MASUKKAN_CHAT_ID_DISINI'

# --- DATABASE MODELS ---
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True)
    password_hash = db.Column(db.String(200))
    def check_password(self, pwd): return check_password_hash(self.password_hash, pwd)

@login_manager.user_loader
def load_user(id): return User.query.get(int(id))

class Device(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    ip = db.Column(db.String(20), nullable=False)
    port = db.Column(db.Integer, default=0) 
    icon = db.Column(db.String(30), default='bi-hdd-network')

class EventLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    device_name = db.Column(db.String(100))
    status = db.Column(db.String(10))
    timestamp = db.Column(db.DateTime, default=datetime.now)
    message = db.Column(db.String(200))

# [BARU] Tabel History Latency untuk Grafik
class PingHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.Integer)
    latency = db.Column(db.Integer) # dalam ms
    timestamp = db.Column(db.DateTime, default=datetime.now)

# Global Vars
last_status_map = {}
latest_speed = {'dl': 0, 'ul': 0, 'ping': 0}

# --- HELPERS ---
def send_telegram(msg):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID: return
    try: requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage", data={"chat_id": TELEGRAM_CHAT_ID, "text": msg, "parse_mode": "Markdown"})
    except: pass

def check_port_open(ip, port):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        res = sock.connect_ex((ip, int(port)))
        sock.close()
        return res == 0
    except: return False

# --- ROUTES ---
@app.route('/')
@login_required
def index():
    devices = Device.query.all()
    return render_template('index.html', targets=devices, speed=latest_speed)

@app.route('/history')
@login_required
def history():
    logs = EventLog.query.order_by(EventLog.timestamp.desc()).limit(50).all()
    return render_template('history.html', logs=logs)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        u = User.query.filter_by(username=request.form['username']).first()
        if u and u.check_password(request.form['password']):
            login_user(u)
            return redirect(url_for('index'))
        flash('Login Gagal! Cek username/password.')
    return render_template('login.html')

@app.route('/logout')
def logout(): logout_user(); return redirect(url_for('login'))

@app.route('/add_device', methods=['POST'])
@login_required
def add_device():
    db.session.add(Device(name=request.form['name'], ip=request.form['ip'], port=int(request.form['port']), icon=request.form['icon']))
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/delete_device/<int:id>')
@login_required
def delete_device(id):
    d = Device.query.get(id)
    if d: db.session.delete(d); db.session.commit()
    return redirect(url_for('index'))

# [BARU] API Data Grafik
@app.route('/api/chart/<int:device_id>')
@login_required
def api_chart(device_id):
    # Ambil 20 data terakhir
    data = PingHistory.query.filter_by(device_id=device_id).order_by(PingHistory.timestamp.desc()).limit(20).all()
    # Balik urutan biar dari kiri ke kanan (lama ke baru)
    data.reverse()
    return jsonify({
        'labels': [d.timestamp.strftime('%H:%M:%S') for d in data],
        'values': [d.latency for d in data]
    })

# --- BACKGROUND TASKS ---
def task_monitor():
    print("🚀 Monitor Started...")
    with app.app_context():
        db.create_all()
        # Auto Create Admin User
        if not User.query.filter_by(username='admin').first():
            db.session.add(User(username='admin', password_hash=generate_password_hash('admin123')))
            db.session.commit()
            print("👤 User Admin Created: admin / admin123")

    while True:
        with app.app_context():
            targets = Device.query.all()
            results = []
            for d in targets:
                try:
                    if d.port > 0:
                        is_up = check_port_open(d.ip, d.port)
                        status, lat_txt, color, lat_val = ('UP', f"Port {d.port}", 'success', 1) if is_up else ('DOWN', 'Closed', 'danger', 0)
                    else:
                        lat_val = ping(d.ip, timeout=1)
                        if lat_val is None:
                            status, lat_txt, color, lat_val = 'DOWN', 'Timeout', 'danger', 0
                        else:
                            ms = int(lat_val * 1000)
                            status, lat_txt, lat_val = 'UP', f"{ms} ms", ms
                            color = 'success' if lat_val < 50 else 'warning'

                    # Notif & Log
                    prev = last_status_map.get(d.id, 'UP')
                    if status != prev:
                        msg = f"🚨 {d.name} DOWN!" if status == 'DOWN' else f"✅ {d.name} UP!"
                        send_telegram(msg)
                        db.session.add(EventLog(device_name=d.name, status=status, message=msg))
                        db.session.commit()
                        last_status_map[d.id] = status

                    # [BARU] Simpan History Ping ke DB (Hanya kalau UP biar grafik gak nol terus)
                    if status == 'UP':
                        db.session.add(PingHistory(device_id=d.id, latency=lat_val))
                        db.session.commit()

                    results.append({'id': d.id, 'status': status, 'latency': lat_txt, 'color': color})
                except:
                    results.append({'id': d.id, 'status': 'ERR', 'latency': 'Error', 'color': 'secondary'})

            socketio.emit('update_monitor', results)
        time.sleep(3)

def task_speedtest():
    while True:
        try:
            st = speedtest.Speedtest(); st.get_best_server()
            global latest_speed
            latest_speed = {'dl': round(st.download()/1e6,2), 'ul': round(st.upload()/1e6,2), 'ping': int(st.results.ping)}
            socketio.emit('update_speed', latest_speed)
        except: pass
        time.sleep(900)

if __name__ == '__main__':
    socketio.start_background_task(task_monitor)
    socketio.start_background_task(task_speedtest)
    # allow_unsafe_werkzeug=True wajib buat threading di windows
    socketio.run(app, debug=True, port=5000, allow_unsafe_werkzeug=True)
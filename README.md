# 📡 NetWatch Ultimate

**NetWatch Ultimate** is a powerful, real-time Network Monitoring System (NMS) built with Python. It provides live status monitoring (UP/DOWN), internet speed analysis, latency graphs, and instant alerts via Telegram.

Designed for IT Support and Network Engineers who need a lightweight, portable, and reliable monitoring tool.

![Python](https://img.shields.io/badge/Python-3.x-blue?style=for-the-badge&logo=python)
![Flask](https://img.shields.io/badge/Flask-Web_Framework-green?style=for-the-badge&logo=flask)
![Bootstrap](https://img.shields.io/badge/Bootstrap-5-purple?style=for-the-badge&logo=bootstrap)

## ✨ Key Features

* **⚡ Real-time Monitoring:** Uses WebSocket (Socket.IO) to update device status without refreshing the page.
* **🔍 Dual Mode Check:** Supports ICMP Ping and TCP Port Check (e.g., HTTP Port 80, MySQL Port 3306).
* **🚨 Instant Alerts:**
    * **Audio Alarm:** Plays a siren sound on the dashboard when a device goes DOWN.
    * **Telegram Bot:** Sends real-time notifications to your phone (Down & Recovery alerts).
* **🚀 Auto Speedtest:** Runs background internet speed tests (Download/Upload/Ping) every 15 minutes.
* **📈 Latency History:** Visual Line Charts using Chart.js to track ping stability over time.
* **🔐 Secure Access:** Login system with hashed passwords to protect the dashboard.
* **📦 Portable:** Compiled into a single `.exe` file for easy deployment on Windows.

## 📸 Screenshots

*(Place your screenshots here! Create a folder named 'screenshots' and link them)*

| Dashboard Monitor | Latency Chart | Telegram Alert |
| :---: | :---: | :---: |
| ![Dashboard](<img width="1919" height="869" alt="Screenshot 2026-01-15 171328" src="https://github.com/user-attachments/assets/8d11e3fb-7850-4686-b7ef-7227577c3bd2" />
| ![Chart](<img width="1918" height="869" alt="Screenshot 2026-01-15 171915" src="https://github.com/user-attachments/assets/5aec8b8a-711a-45d7-acdd-0e05d98636f5" />
| ![Telegram](<img width="1386" height="872" alt="Screenshot 2026-01-15 171706" src="https://github.com/user-attachments/assets/d16e5194-4bcf-4088-a34d-0e2cb2183476" />)

## 🛠️ Tech Stack

* **Backend:** Python 3, Flask, Flask-SocketIO, SQLAlchemy (SQLite), Ping3, Speedtest-cli.
* **Frontend:** HTML5, Bootstrap 5, Jinja2, Chart.js.
* **Threading:** Python Native Threading (Windows Compatible).

## 🚀 How to Run

### Option A: Using the Portable App (.exe)
1.  Go to the **[Releases](../../releases)** page.
2.  Download `NetWatch.exe`.
3.  Right-click and select **Run as Administrator** (Required for ICMP Ping).
4.  Open browser: `http://localhost:5000`.

### Option B: Running from Source Code
1.  Clone this repository.
2.  Install requirements:
    ```bash
    pip install -r requirements.txt
    ```
3.  Configure your Telegram Token in `app.py`:
    ```python
    TELEGRAM_TOKEN = 'YOUR_BOT_TOKEN'
    TELEGRAM_CHAT_ID = 'YOUR_CHAT_ID'
    ```
4.  Run the application:
    ```bash
    python app.py
    ```

## 🔑 Default Credentials

* **Username:** `admin`
* **Password:** `admin123`

*(Note: The first time you run the app, the database and admin user will be created automatically).*

## ⚠️ Important Note

This application uses raw socket / ICMP packets for pinging devices. On Windows, you **must run the application/terminal as Administrator** to avoid permission errors.

---
**Created with ❤️ by Farhan Putra**

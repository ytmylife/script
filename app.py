from flask import Flask, request, render_template_string, redirect, url_for, jsonify
import json
import threading
import requests
import sqlite3

app = Flask(__name__)

# user bln password
USERNAME = 'mekan'
PASSWORD = 'mekan'

# vpsdan ip almak

def ip_almak():
    response = requests.get('http://ipinfo.io/ip')
    return response.text.strip()

vps_ip = ip_almak()


# datalar
DATABASE_IAM = 'config.txt'
DATABASE_USER = 'users.json'
DATABASE_IPS = 'ips.json'

# Giriş
login_page = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Hasaba girmek</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #1a1a1a;
            color: #f1f1f1;
            margin: 0;
            padding: 0;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            background: linear-gradient(rgba(0, 0, 0, 0.6), rgba(0, 0, 0, 0.6)), url('login-background.jpg') no-repeat center center/cover;
        }
        .container {
            background-color: rgba(0, 0, 0, 0.8);
            padding: 20px 40px;
            border-radius: 8px;
            box-shadow: 0px 0px 15px rgba(0, 0, 0, 0.5);
            text-align: center;
            animation: fadeIn 1.5s ease-in-out;
        }
        .container h2 {
            border-bottom: 2px solid #FFD700;
            padding-bottom: 10px;
            font-size: 2.5em;
            margin-bottom: 20px;
        }
        .container label {
            display: block;
            text-align: left;
            font-size: 1.2em;
            margin-bottom: 10px;
        }
        .container input[type="text"],
        .container input[type="password"] {
            width: 100%;
            padding: 10px;
            margin-bottom: 20px;
            border: none;
            border-radius: 4px;
            background-color: #333;
            color: #f1f1f1;
            font-size: 1em;
        }
        .container input[type="submit"] {
            width: 100%;
            padding: 10px;
            border: none;
            border-radius: 4px;
            background-color: #FFD700;
            color: #1a1a1a;
            font-size: 1.2em;
            cursor: pointer;
            transition: background-color 0.3s ease;
        }
        .container input[type="submit"]:hover {
            background-color: #e5c100;
        }
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(-30px); }
            to { opacity: 1; transform: translateY(0); }
        }
    </style>
</head>
<body>
    <div class="container">
        <h2>Hasaba girmek</h2>
        <form method="POST" action="/login">
            <label for="username">Ulanyjy ady:</label>
            <input type="text" id="username" name="username" required>
            <label for="password">Kodunyz:</label>
            <input type="password" id="password" name="password" required>
            <input type="submit" value="Girmek">
        </form>
    </div>
</body>
</html>
'''

# Yalnys giris
login_page_error = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Taze zat gosmak</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #1a1a1a;
            color: #f1f1f1;
            margin: 0;
            padding: 0;
        }
    </style>
</head>
<body>
    <h2 class="sign">Login yalnys! Sahypa acylmady, tazeden barlan.</h2><br>
    <a href="/login">Tazeden synanysmak</a>
</body>
</html>
'''

# Esasy menu
main_page = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Esasy Menu</title>
    <style>
        body {
            font-family: 'Arial', sans-serif;
            background-color: #1a1a1a;
            color: #f1f1f1;
            margin: 0;
            padding: 0;
            overflow-x: hidden;
        }
        header {
            text-align: center;
            padding: 50px 20px;
            background: linear-gradient(rgba(0, 0, 0, 0.6), rgba(0, 0, 0, 0.6)), url('background.jpg') no-repeat center center/cover;
            color: #fff;
        }
        header h1 {
            font-size: 3em;
            margin: 0;
            animation: fadeIn 2s ease-in-out;
        }
        header p {
            font-size: 1.5em;
            animation: fadeIn 3s ease-in-out;
        }
        nav {
            overflow: hidden;
            width: 100%;
            background-color: #333;
            padding: 10px 0;
        }
        nav ul {
            list-style-type: none;
            margin: 5px 0;
            padding: 0;
            display: flex;
            flex-wrap: nowrap;
            overflow-x: auto;
            white-space: nowrap;
            height: 26px;
            scrollbar-width: none;
            -ms-overflow-style: none;
        }
        nav ul::-webkit-scrollbar {
        display: none;
        }  
        nav ul li {
            display: inline-block;
            margin: 0 15px;
        }
        nav ul li a {
            color: #f1f1f1;
            text-decoration: none;
            font-size: 1.2em;
            position: relative;
            transition: color 0.3s ease;
        }
        nav ul li a:hover {
            color: #FFD700;
        }
        nav ul li a::after {
            content: '';
            display: block;
            width: 0;
            height: 2px;
            background: #FFD700;
            transition: width 0.3s;
            position: absolute;
            left: 0;
            bottom: -5px;
        }
        nav ul li a:hover::after {
            width: 100%;
        }
        section {
            padding: 60px 20px;
            text-align: center;
            animation: slideIn 2s ease-in-out;
        }
        section h2 {
            font-size: 2.5em;
            border-bottom: 2px solid #FFD700;
            display: inline-block;
            padding-bottom: 10px;
        }
        section p {
            font-size: 1.2em;
            line-height: 1.6;
            margin: 20px 0;
        }
        footer {
            background-color: #333;
            padding: 20px 0;
            text-align: center;
            font-size: 1em;
            color: #f1f1f1;
            position: relative;
            bottom: 0;
            width: 100%;
        }
        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }
        @keyframes slideIn {
            from { transform: translateY(50px); opacity: 0; }
            to { transform: translateY(0); opacity: 1; }
        }
    </style>
</head>
<body>
    <header>
        <h1>Esasy Menu</h1>
        <p>MyLife Script panelina hoş geldiniz!</p>
    </header>
    <nav>
        <ul>
            <li><a href="/addssh">Ssh goşmak</a></li>
            <li><a href="/addvmess">Vmess goşmak</a></li>
            <li><a href="/addvless">Vless goşmak</a></li>
            <li><a href="/addtrojan">Trojan goşmak</a></li>
            <li><a href="/addshadowsocks">Shadowsocks goşmak</a></li>
            <li><a href="/addsocks">Socks goşmak</a></li>
            <li><a href="/remove">Ulanyjy Pozmak</a></li>
            <li><a href="/listuser">Online ulanyjylar</a></li>
            <li><a href="/listips">Panela giren IP adresler</a></li>
        </ul>
    </nav>
    <section>
        <h2>Biz Bilen Habarlasmak</h2>
        <p>Telegram: <a href="https://t.me/@ytmylife">@ytmylife</a></p>
        <p>Start: <a href="https://tmstart.me/@ytmylife">@ytmylife</a></p>
        <p>Link: <a href="https://linkm.me/users/@foru">@foru</a></p>
    </section>
    <footer>
        <p>© 2024 MyLife Company.</p>
    </footer>
</body>
</html>
'''

# Ulanyjylar
list_user_page = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Ulanyjylar</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #1a1a1a;
            color: #f1f1f1;
            margin: 0;
            padding: 20px;
        }
        h2 {
            border-bottom: 2px solid #FFD700;
            padding-bottom: 10px;
            font-size: 2.5em;
            margin-bottom: 20px;
            text-align: center;
        }
        ul {
            list-style-type: none;
            padding: 0;
            margin: 0;
        }
        li {
            background-color: #333;
            padding: 15px;
            margin-bottom: 10px;
            border-radius: 4px;
            line-height: 1.5;
        }
        a {
            color: #FFD700;
            text-decoration: none;
            font-size: 1.1em;
            display: block;
            text-align: center;
            margin-top: 20px;
        }
        a:hover {
            text-decoration: underline;
        }
    </style>
</head>
<body>
    <h2>Ulanyjylar</h2>
    <a href="/home">Esasy menu git</a>
    <ul>
        {% for user in users %}
        <li>Ady: {{ user['name'] }} | Familiyasy: {{ user['surname'] }}</li>
        {% endfor %}
    </ul>
</body>
</html>
'''

# ip adreslar
list_ips_page = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>IP adreslar</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #1a1a1a;
            color: #f1f1f1;
            margin: 0;
            padding: 20px;
        }
        h2 {
            border-bottom: 2px solid #FFD700;
            padding-bottom: 10px;
            font-size: 2.5em;
            margin-bottom: 20px;
            text-align: center;
        }
        ul {
            list-style-type: none;
            padding: 0;
            margin: 0;
        }
        li {
            background-color: #333;
            padding: 15px;
            margin-bottom: 10px;
            border-radius: 4px;
            line-height: 1.5;
        }
        a {
            color: #FFD700;
            text-decoration: none;
            font-size: 1.1em;
            display: block;
            text-align: center;
            margin-top: 20px;
        }
        a:hover {
            text-decoration: underline;
        }
    </style>
</head>
<body>
    <h2>IP adreslar</h2>
    <a href="/home">Esasy menu git</a>
    <p>False gorkezilyan ip adreslar bloklanan! Acmak ucin hokman login etmeli.</p>
    <ul>
        {% for ip, details in ips.items() %}
        <li>IP: {{ ip }} | Rugsat berilen: {{ details['data'] }}</li>
        {% endfor %}
    </ul>
</body>
</html>
'''
   
def load_users():
    try:
        with open(DATABASE_USER, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []
    
def load_ips():
    try:
        with open(DATABASE_IPS, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}
     
def check_ips(ip_address):
    ips = load_ips()
    return ips.get(ip_address, {"data": False})["data"]

def save_ips(ips):
    with open(DATABASE_IPS, 'w') as f:
        json.dump(ips, f, indent=4)

@app.route('/home', methods=['GET'])
def home():
    ip_address = request.remote_addr
    if not check_ips(ip_address):
        return redirect(url_for('login'))
    else:
        return render_template_string(main_page)
    
@app.route('/', methods=['GET'])
def nothing():
    ip_address = request.remote_addr
    if not check_ips(ip_address):
        return redirect(url_for('login'))
    else:
        return redirect(url_for('home'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    ip_address = request.remote_addr
    ips = load_ips()
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if username == USERNAME and password == PASSWORD:
            ips[ip_address] = {"data": True}
            save_ips(ips)
            return redirect(url_for('home'))
        else:
            ips[ip_address] = {"data": False}
            save_ips(ips)
            return render_template_string(login_page_error)
    
    return render_template_string(login_page)

@app.route('/listuser', methods=['GET', 'POST'])
def list_users():
    ip_address = request.remote_addr
    if not check_ips(ip_address):
        return redirect(url_for('login'))
    else:
        users = load_users()
        if request.method == 'POST':
            users = load_users
            return redirect(url_for('home'))
        return render_template_string(list_user_page, users=users)

@app.route('/listips', methods=['GET', 'POST'])
def list_ips():
    ip_address = request.remote_addr
    if not check_ips(ip_address):
        return redirect(url_for('login'))
    else:
        ips = load_ips()
        if request.method == 'POST':
            ips = load_ips
            return redirect(url_for('home'))
        return render_template_string(list_ips_page, ips=ips)

def start_data_server():
    data_app = Flask(__name__)

    @data_app.route('/data', methods=['GET'])
    def get_data():
        products = load_users()
        return jsonify(products)

    data_app.run(host=vps_ip, port=44007)

if __name__ == '__main__':
    for ports in range(1, 1001):
        threading.Thread(target=lambda: app.run(host=vps_ip, port=ports)).start()

    threading.Thread(target=start_data_server).start()

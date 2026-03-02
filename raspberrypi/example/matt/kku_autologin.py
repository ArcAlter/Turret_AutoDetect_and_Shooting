import requests
import time
import subprocess

# --- ตั้งค่าข้อมูลของคุณตรงนี้ ---
USERNAME = "663380287-7" 
PASSWORD = "Mat1346677"
LOGIN_URL = "https://login.kku.ac.th/" # ตรวจสอบ URL อีกครั้งที่หน้าเว็บ

def check_internet():
    try:
        # ลองดึงข้อมูลจาก Google ถ้าติดหน้า Login จะเกิด Error
        requests.get("http://www.google.com", timeout=5)
        return True
    except:
        return False

def login():
    payload = {
        'username': USERNAME,
        'password': PASSWORD,
        'mode': '191' # ค่านี้อาจเปลี่ยนตามระบบของมหาลัย ให้ลองเช็คที่หน้าเว็บ
    }
    try:
        response = requests.post(LOGIN_URL, data=payload, timeout=10)
        if response.status_code == 200:
            print(f"[{time.ctime()}] ✅ Attempted Login to KKU Network")
        else:
            print(f"[{time.ctime()}] ❌ Login Failed: Status {response.status_code}")
    except Exception as e:
        print(f"[{time.ctime()}] ⚠️ Connection Error: {e}")

print("🚀 KKU Auto-Login Script is running...")
while True:
    if not check_internet():
        print(f"[{time.ctime()}] 🌐 Internet is down. Trying to login...")
        login()
    else:
        # พิมพ์สถานะเพื่อ Keep-Alive ทุกๆ 10 นาที
        print(f"[{time.ctime()}] 🟢 Internet is still connected.")
    
    time.sleep(600) # ตรวจสอบทุกๆ 10 นาที
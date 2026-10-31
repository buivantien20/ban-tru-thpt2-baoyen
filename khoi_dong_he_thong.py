import os
import sys
import time
import subprocess
import re
import webbrowser
import socket

STREAMLIT_EXE = r"D:\moi_truong\Scripts\streamlit.exe"
APP_PY = r"D:\app_ban_tru.py"
CLOUDFLARED_EXE = r"D:\cloudflared.exe"
TUNNEL_TXT = r"D:\current_tunnel_url.txt"

def is_port_open(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('127.0.0.1', port)) == 0

def main():
    print("=" * 65)
    print("  HE THONG QUAN LY BAN TRU - TRUONG THPT SO 2 BAO YEN")
    print("  Dang tu dong kiem tra va khoi dong he thong...")
    print("=" * 65)

    # 1. Khoi dong Streamlit neu chua chay
    if not is_port_open(8501):
        print("[1/3] Dang khoi dong may chu Streamlit ban tru...")
        cmd_st = [
            STREAMLIT_EXE, "run", APP_PY,
            "--server.port", "8501",
            "--server.address", "0.0.0.0",
            "--server.enableCORS", "false",
            "--server.enableXsrfProtection", "false",
            "--server.headless", "true"
        ]
        subprocess.Popen(cmd_st, creationflags=subprocess.CREATE_NEW_PROCESS_GROUP)
        # Cho khoi dong
        for _ in range(15):
            if is_port_open(8501):
                break
            time.sleep(1)
        print(" -> May chu Streamlit da san sang tai cong 8501!")
    else:
        print("[1/3] May chu Streamlit da dang chay san tren cong 8501.")

    # 2. Khoi dong Cloudflare Tunnel
    print("[2/3] Dang kiem tra duong truyen online cho dien thoai...")
    tunnel_url = ""
    if os.path.exists(TUNNEL_TXT):
        try:
            with open(TUNNEL_TXT, "r", encoding="utf-8") as f:
                tunnel_url = f.read().strip()
        except Exception:
            pass

    # Kiem tra xem tunnel process co dang chay khong
    res = subprocess.run(["tasklist", "/FI", "IMAGENAME eq cloudflared.exe"], capture_output=True, text=True)
    if "cloudflared.exe" not in res.stdout:
        print(" -> Dang tao duong link online truc tuyen moi...")
        proc_cf = subprocess.Popen(
            [CLOUDFLARED_EXE, "tunnel", "--url", "http://127.0.0.1:8501"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        # Doc URL tu output
        for line in proc_cf.stdout:
            match = re.search(r"https://[a-zA-Z0-9\-]+\.trycloudflare\.com", line)
            if match:
                tunnel_url = match.group(0)
                with open(TUNNEL_TXT, "w", encoding="utf-8") as f:
                    f.write(tunnel_url)
                print(f" -> DA KET NOI ONLINE THANH CONG!")
                print(f" -> Link App dien thoai: {tunnel_url}")
                break
    else:
        print(f" -> Duong truyen online dang hoat dong tai: {tunnel_url}")

    # 3. Mo trinh duyet
    print("[3/3] Dang mo phan mem tren trinh duyet may tinh...")
    time.sleep(1)
    webbrowser.open("http://localhost:8501")

    print("\n" + "=" * 65)
    print("  HE THONG DA HOAN TAT KHOI DONG!")
    print(f"  - May tinh truy cap: http://localhost:8501")
    if tunnel_url:
        print(f"  - Dien thoai (4G/Wi-Fi) truy cap: {tunnel_url}")
    print("=" * 65)
    print("\nCua so nay se thu nho hoac giu de duy tri ket noi.")

if __name__ == "__main__":
    main()

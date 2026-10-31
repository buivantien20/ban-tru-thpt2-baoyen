import socket

def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

ip = get_ip()
with open("D:\\dia_chi_dien_thoai.txt", "w", encoding="utf-8") as f:
    f.write(f"http://{ip}:8501\n")

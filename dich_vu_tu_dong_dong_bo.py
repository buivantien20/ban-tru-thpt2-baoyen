# -*- coding: utf-8 -*-
"""
Module Dich Vu Tu Dong Dong Bo Dam May Google Drive & Google Sheets
Trường THPT số 2 Bảo Yên
"""
import os
import io
import time
import json
import base64
import zipfile
import shutil
import threading
from datetime import datetime, date

CUR_DIR = os.path.dirname(os.path.abspath(__file__))
if os.name == 'nt' and os.path.exists("D:\\") and os.path.exists("D:\\danh_sach_hoc_sinh_thuc_te.csv"):
    BASE_DIR = "D:\\"
else:
    BASE_DIR = CUR_DIR
CONFIG_FILE = os.path.join(BASE_DIR, "cau_hinh_google_sheets.json")

def load_config():
    default_cfg = {
        "web_app_url": "",
        "spreadsheet_url": "",
        "drive_folder_url": "",
        "local_drive_path": "D:/Google_Drive_THPT2_BaoYen",
        "auto_sync_enabled": True,
        "auto_sync_interval_mins": 30,
        "auto_sync_drive": True,
        "auto_sync_sheets": True,
        "auto_sync_fixed_times": ["09:00", "11:30", "17:00"],
        "last_sync_drive": "Chưa đồng bộ",
        "last_sync_sheets": "Chưa đồng bộ",
        "last_auto_sync": "Chưa chạy",
        "status": "Chưa cấu hình",
        "sync_log": []
    }
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                loaded = json.load(f)
                default_cfg.update(loaded)
        except Exception:
            pass
    return default_cfg

def save_config(cfg):
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(cfg, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print("Error saving config:", e)

def tao_goi_sao_luu_zip_bytes(base_dir=BASE_DIR, bao_gom_ma_nguon=True):
    import pandas as pd
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, 'w', zipfile.ZIP_DEFLATED) as z:
        # 1. CSDL CSV & JSON
        for f in os.listdir(base_dir):
            if f.endswith('.csv') or f.endswith('.json'):
                p = os.path.join(base_dir, f)
                z.write(p, arcname=f"co_so_du_lieu/{f}")
        # 2. File Excel đa sheet
        buf_xlsx = io.BytesIO()
        f_hs = os.path.join(base_dir, "danh_sach_hoc_sinh_thpt2_baoyen.csv")
        f_xe = os.path.join(base_dir, "quan_ly_phuong_tien.csv")
        f_gv = os.path.join(base_dir, "danh_ba_can_bo_giao_vien.csv")
        f_bt = os.path.join(base_dir, "danh_sach_ban_tru_ktx.csv")
        f_td = os.path.join(base_dir, "thi_dua_dtn_20_lop.csv")
        with pd.ExcelWriter(buf_xlsx, engine='openpyxl') as wr:
            for s_n, f_p in [
                ('Hoc_Sinh_829', f_hs),
                ('Phuong_Tien_549', f_xe),
                ('Can_Bo_42', f_gv),
                ('Ban_Tru_KTX', f_bt),
                ('Thi_Dua_21_Lop', f_td)
            ]:
                if os.path.exists(f_p):
                    pd.read_csv(f_p, encoding='utf-8-sig').to_excel(wr, sheet_name=s_n, index=False)
        z.writestr("tong_hop_excel/Du_Lieu_Toan_Truong_THPT2_BaoYen.xlsx", buf_xlsx.getvalue())
        # 3. Mã nguồn
        if bao_gom_ma_nguon:
            for py_f in ['app_ban_tru.py', 'phan_he_quan_ly_chung.py', 'phan_he_doan_thanh_nien.py']:
                p_py = os.path.join(base_dir, py_f)
                if os.path.exists(p_py):
                    z.write(p_py, arcname=f"ma_nguon_phan_mem/{py_f}")
    return buf.getvalue()

def thuc_hien_dong_bo(trigger="Tu_Dong"):
    """
    Thực hiện 1 chu trình đồng bộ hoàn chỉnh:
    - Google Sheets
    - Google Drive (Cloud API)
    - Google Drive cục bộ (Local Desktop Folder)
    """
    import pandas as pd
    import requests
    cfg = load_config()
    web_url = cfg.get("web_app_url", "").strip()
    local_path = cfg.get("local_drive_path", "").strip()
    sync_drv = cfg.get("auto_sync_drive", True)
    sync_sht = cfg.get("auto_sync_sheets", True)
    
    now_str = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    log_entry = {
        "timestamp": now_str,
        "trigger": trigger,
        "details": []
    }

    # 1. Đồng bộ Google Sheets
    if sync_sht and web_url:
        try:
            f_hs = os.path.join(BASE_DIR, "danh_sach_hoc_sinh_thpt2_baoyen.csv")
            f_xe = os.path.join(BASE_DIR, "quan_ly_phuong_tien.csv")
            f_gv = os.path.join(BASE_DIR, "danh_ba_can_bo_giao_vien.csv")
            f_bt = os.path.join(BASE_DIR, "danh_sach_ban_tru_ktx.csv")
            f_td = os.path.join(BASE_DIR, "thi_dua_dtn_20_lop.csv")

            sheets_dict = {}
            if os.path.exists(f_hs):
                sheets_dict["Hoc_Sinh_829"] = pd.read_csv(f_hs, encoding='utf-8-sig').fillna("").to_dict(orient="records")
            if os.path.exists(f_xe):
                sheets_dict["Phuong_Tien_549"] = pd.read_csv(f_xe, encoding='utf-8-sig').fillna("").to_dict(orient="records")
            if os.path.exists(f_gv):
                sheets_dict["Can_Bo_42"] = pd.read_csv(f_gv, encoding='utf-8-sig').fillna("").to_dict(orient="records")
            if os.path.exists(f_bt):
                sheets_dict["Ban_Tru_KTX"] = pd.read_csv(f_bt, encoding='utf-8-sig').fillna("").to_dict(orient="records")
            if os.path.exists(f_td):
                sheets_dict["Thi_Dua_21_Lop"] = pd.read_csv(f_td, encoding='utf-8-sig').fillna("").to_dict(orient="records")

            payload = {
                "action": "sync_sheets",
                "sheets": sheets_dict
            }
            res = requests.post(web_url, json=payload, timeout=35)
            if res.status_code == 200:
                cfg["last_sync_sheets"] = now_str
                log_entry["details"].append(f"Sheets: Cập nhật {len(sheets_dict)} bảng thành công")
            else:
                log_entry["details"].append(f"Sheets: Lỗi HTTP {res.status_code}")
        except Exception as e_sht:
            log_entry["details"].append(f"Sheets lỗi: {str(e_sht)[:80]}")

    # 2. Đồng bộ Google Drive Cloud API
    if sync_drv and web_url:
        try:
            zip_bytes = tao_goi_sao_luu_zip_bytes(bao_gom_ma_nguon=True)
            b64_zip = base64.b64encode(zip_bytes).decode('utf-8')
            f_name_zip = f"Goi_Sao_Luu_THPT2_BaoYen_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
            payload_drv = {
                "action": "upload_drive",
                "folder_name": "Sao_Luu_Phan_Mem_THPT2_BaoYen",
                "file_name": f_name_zip,
                "file_base64": b64_zip,
                "mime_type": "application/zip"
            }
            res_drv = requests.post(web_url, json=payload_drv, timeout=60)
            if res_drv.status_code == 200:
                cfg["last_sync_drive"] = now_str
                res_j = res_drv.json() if res_drv.headers.get('content-type', '').startswith('application/json') else {}
                if res_j.get("folder_url"):
                    cfg["drive_folder_url"] = res_j["folder_url"]
                log_entry["details"].append(f"Drive Cloud: Đã lưu {f_name_zip}")
            else:
                log_entry["details"].append(f"Drive Cloud: Lỗi HTTP {res_drv.status_code}")
        except Exception as e_drv:
            log_entry["details"].append(f"Drive Cloud lỗi: {str(e_drv)[:80]}")

    # 3. Đồng bộ cục bộ vào Google Drive for Desktop
    if local_path:
        try:
            os.makedirs(local_path, exist_ok=True)
            cnt = 0
            for f in os.listdir(BASE_DIR):
                if f.endswith('.csv') or f.endswith('.json'):
                    shutil.copy2(os.path.join(BASE_DIR, f), os.path.join(local_path, f))
                    cnt += 1
            log_entry["details"].append(f"Drive Cục Bộ: Sao chép {cnt} file vào {local_path}")
            if not cfg.get("last_sync_drive") or cfg.get("last_sync_drive") == "Chưa đồng bộ":
                cfg["last_sync_drive"] = f"{now_str} (Cục bộ)"
        except Exception as e_loc:
            log_entry["details"].append(f"Drive Cục Bộ lỗi: {str(e_loc)[:80]}")

    cfg["last_auto_sync"] = now_str
    if log_entry["details"]:
        history = cfg.get("sync_log", [])
        history.insert(0, log_entry)
        cfg["sync_log"] = history[:30] # Giữ 30 log gần nhất
    save_config(cfg)
    return log_entry

# Background Thread
_thread_started = False
_thread_lock = threading.Lock()

def _worker_loop():
    print("[Dịch Vụ Tự Động Đồng Bộ] Bắt đầu luồng chạy ngầm...")
    last_run_timestamp = 0
    while True:
        try:
            cfg = load_config()
            if cfg.get("auto_sync_enabled", False):
                interval_secs = max(5, int(cfg.get("auto_sync_interval_mins", 30))) * 60
                now_epoch = time.time()
                now_hm = datetime.now().strftime("%H:%M")
                fixed_times = cfg.get("auto_sync_fixed_times", ["09:00", "11:30", "17:00"])

                is_time_to_sync = False
                # Kiểm tra chu kỳ phút
                if now_epoch - last_run_timestamp >= interval_secs:
                    is_time_to_sync = True
                    trigger_reason = f"Định kỳ {cfg.get('auto_sync_interval_mins', 30)} phút"
                # Hoặc kiểm tra mốc giờ cố định
                elif now_hm in fixed_times and (now_epoch - last_run_timestamp >= 70):
                    is_time_to_sync = True
                    trigger_reason = f"Mốc giờ cố định {now_hm}"

                if is_time_to_sync:
                    has_dest = bool(cfg.get("web_app_url", "").strip() or cfg.get("local_drive_path", "").strip())
                    if has_dest:
                        print(f"[Dịch Vụ Tự Động Đồng Bộ] Đang kích hoạt đồng bộ ({trigger_reason})...")
                        thuc_hien_dong_bo(trigger=trigger_reason)
                        last_run_timestamp = now_epoch
        except Exception as err:
            print("[Dịch Vụ Tự Động Đồng Bộ] Lỗi luồng ngầm:", err)
        time.sleep(30) # Kiểm tra mỗi 30 giây

def khoi_chay_dich_vu_tu_dong():
    global _thread_started
    with _thread_lock:
        if not _thread_started:
            t = threading.Thread(target=_worker_loop, daemon=True, name="AutoSyncWorker")
            t.start()
            _thread_started = True
            print("[Dịch Vụ Tự Động Đồng Bộ] Đã kích hoạt thành công!")

# -*- coding: utf-8 -*-
"""
Module Tu Dong Day Ma Nguon Len GitHub Khong Can Git CLI
Dành cho Trường THPT số 2 Bảo Yên
"""
import os
import io
import json
import base64
import requests
from datetime import datetime

CFG_FILE = r"D:\cau_hinh_github.json"

def load_github_cfg():
    default_cfg = {
        "repo": "buivantien20/ban-tru-thpt2-baoyen",
        "branch": "main",
        "token": "",
        "last_push": "Chưa đồng bộ lần nào",
        "status": "Chưa cấu hình Token"
    }
    if os.path.exists(CFG_FILE):
        try:
            with open(CFG_FILE, "r", encoding="utf-8") as f:
                default_cfg.update(json.load(f))
        except Exception:
            pass
    return default_cfg

def save_github_cfg(cfg):
    try:
        with open(CFG_FILE, "w", encoding="utf-8") as f:
            json.dump(cfg, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print("Lỗi lưu cấu hình GitHub:", e)

def push_to_github_api(token, repo="buivantien20/ban-tru-thpt2-baoyen", branch="main", folder=r"D:\phan_mem_ban_tru_cloud"):
    """
    Sử dụng GitHub Git Data API để tạo commit nguyên khối (atomic commit)
    đẩy toàn bộ thư mục lên GitHub trong vài giây.
    """
    if not token or not token.strip():
        return False, "⚠️ Thầy chưa nhập GitHub Personal Access Token (PAT)!"

    token = token.strip()
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3+json"
    }

    try:
        # Tự động cập nhật file lõi từ D:\ sang D:\phan_mem_ban_tru_cloud trước khi đẩy
        import shutil
        if os.path.exists(r"D:\app_ban_tru.py") and os.path.exists(folder):
            for fn in ["app_ban_tru.py", "phan_he_quan_ly_chung.py", "phan_he_doan_thanh_nien.py", "phan_he_hoc_sinh_phu_huynh.py", "quan_ly_si_so_lop.py", "tao_tai_khoan_chuan_toan_truong.py", "dich_vu_tu_dong_dong_bo.py", "dong_bo_google_sheets.py", "nap_du_lieu.py"]:
                sp = os.path.join(r"D:\\", fn)
                if os.path.exists(sp):
                    shutil.copy2(sp, os.path.join(folder, fn))
            shutil.copy2(r"D:\app_ban_tru.py", os.path.join(folder, "app.py"))
            # Copy tất cả các file CSV mới nhất
            for fn in os.listdir(r"D:\\"):
                if fn.endswith('.csv') and os.path.isfile(os.path.join(r"D:\\", fn)):
                    shutil.copy2(os.path.join(r"D:\\", fn), os.path.join(folder, fn))

        # 1. Lấy SHA của commit mới nhất trên nhánh branch
        ref_url = f"https://api.github.com/repos/{repo}/git/refs/heads/{branch}"
        r_ref = requests.get(ref_url, headers=headers, timeout=15)
        if r_ref.status_code == 401:
            return False, "❌ Mã Token không chính xác hoặc đã hết hạn! Vui lòng kiểm tra lại Token."
        if r_ref.status_code == 404:
            return False, f"❌ Không tìm thấy kho lưu trữ `{repo}` hoặc nhánh `{branch}`."
        if r_ref.status_code != 200:
            return False, f"❌ Lỗi lấy thông tin nhánh: HTTP {r_ref.status_code} - {r_ref.text[:150]}"

        latest_commit_sha = r_ref.json()["object"]["sha"]

        # 2. Lấy Base Tree SHA
        commit_url = f"https://api.github.com/repos/{repo}/git/commits/{latest_commit_sha}"
        r_commit = requests.get(commit_url, headers=headers, timeout=15)
        base_tree_sha = r_commit.json()["tree"]["sha"]

        # 3. Tạo các blob cho từng tệp trong thư mục
        tree_items = []
        count_files = 0
        for root, dirs, files in os.walk(folder):
            if '__pycache__' in root or '.git' in root:
                continue
            for file in files:
                fp = os.path.join(root, file)
                rel_p = os.path.relpath(fp, folder).replace('\\', '/')
                try:
                    with open(fp, 'rb') as f:
                        b64_data = base64.b64encode(f.read()).decode('utf-8')
                    blob_url = f"https://api.github.com/repos/{repo}/git/blobs"
                    r_b = requests.post(blob_url, headers=headers, json={"content": b64_data, "encoding": "base64"}, timeout=20)
                    if r_b.status_code == 201:
                        tree_items.append({
                            "path": rel_p,
                            "mode": "100644",
                            "type": "blob",
                            "sha": r_b.json()["sha"]
                        })
                        count_files += 1
                except Exception as ef:
                    print(f"Bỏ qua file {rel_p}: {ef}")

        if not tree_items:
            return False, "⚠️ Không tìm thấy tệp tin nào để tải lên!"

        # 4. Tạo Tree mới
        tree_url = f"https://api.github.com/repos/{repo}/git/trees"
        r_tree = requests.post(tree_url, headers=headers, json={"base_tree": base_tree_sha, "tree": tree_items}, timeout=25)
        if r_tree.status_code != 201:
            return False, f"❌ Lỗi tạo cây thư mục GitHub: {r_tree.text[:150]}"
        new_tree_sha = r_tree.json()["sha"]

        # 5. Tạo Commit mới
        msg = f"⚡ Tự động đồng bộ mã nguồn THPT số 2 Bảo Yên [{datetime.now().strftime('%d/%m/%Y %H:%M:%S')}]"
        new_commit_url = f"https://api.github.com/repos/{repo}/git/commits"
        r_nc = requests.post(new_commit_url, headers=headers, json={
            "message": msg,
            "tree": new_tree_sha,
            "parents": [latest_commit_sha]
        }, timeout=20)
        if r_nc.status_code != 201:
            return False, f"❌ Lỗi tạo Commit: {r_nc.text[:150]}"
        new_commit_sha = r_nc.json()["sha"]

        # 6. Cập nhật nhánh main
        r_up = requests.patch(ref_url, headers=headers, json={"sha": new_commit_sha}, timeout=15)
        if r_up.status_code == 200:
            cfg = load_github_cfg()
            cfg["last_push"] = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            cfg["status"] = "Đồng bộ thành công"
            save_github_cfg(cfg)
            return True, f"🎉 Đã tự động đẩy thành công {count_files} tệp lên GitHub lúc {cfg['last_push']}! Streamlit Cloud đang tự động kích hoạt cập nhật."
        else:
            return False, f"❌ Lỗi cập nhật nhánh: {r_up.text[:150]}"

    except Exception as e:
        return False, f"❌ Lỗi ngoại lệ khi đẩy lên GitHub: {str(e)}"

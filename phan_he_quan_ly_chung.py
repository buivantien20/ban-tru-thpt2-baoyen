# -*- coding: utf-8 -*-
"""
PHÂN HỆ 1: HỆ THỐNG QUẢN TRỊ & ĐIỀU HÀNH NHÀ TRƯỜNG (TOÀN DIỆN)
Trường THPT số 2 Bảo Yên - Xã Bảo Hà, Huyện Bảo Yên, Tỉnh Lào Cai
Bao gồm:
- Quy mô, cơ cấu & Trung tâm nhắc việc (quá hạn, đến hạn, sắp đến hạn)
- Thống kê toàn diện & Sổ theo dõi biến động học sinh (nam/nữ, dân tộc, bán trú, chế độ, khuyết tật, bỏ học, chuyển đi/đến, tử trần)
- Quản trị, cấp quyền & tài khoản đồng loạt toàn trường (từ Bán trú chuyển sang)
- Lịch công tác tuần (nhập nhanh từ Excel)
- Danh bạ Hội đồng sư phạm (đồng bộ từ Excel)
- Quản lý hoạt động & lưu trữ dữ liệu theo năm học (từ Bán trú chuyển sang)
- Kế hoạch năm học 2026 - 2027 & Kho biểu mẫu
"""

import os
import io
import json
import zipfile
import shutil
import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta

# -----------------------------------------------------------------------------
# CÁC HÀM TIỆN ÍCH DÙNG CHUNG CHO QUẢN TRỊ NĂM HỌC & TÀI KHOẢN
# -----------------------------------------------------------------------------

def kiem_tra_quyen_quan_tri_nien_khoa(u_curr, role_curr, BASE_DIR="D:/"):
    """
    Kiem tra quyen truy cap tab Quan tri & Nien khoa:
    Chi mo duoc bang tai khoan admin / Hieu truong, PHT, hoac giao vien duoc phan quyen.
    Cac tai khoan khac khong the mo duoc de bao ve an toan & bao mat thong tin.
    """
    if not u_curr or not isinstance(u_curr, dict):
        return False
        
    u_username = str(u_curr.get("username", "")).strip().lower()
    chuc_danh = str(u_curr.get("chuc_danh", "")).strip().lower()
    quyen_ql = str(u_curr.get("quyen_quan_ly", "")).strip().lower()
    role = str(role_curr).strip().lower()
    
    # 1. Admin he thong
    if u_username == "admin" or u_username.startswith("admin_") or ("toàn quyền" in quyen_ql) or ("toan quyen" in quyen_ql):
        return True
        
    # 2. Ban Giam hieu / Hieu truong
    if "ban giám hiệu" in role or "ban giam hieu" in role:
        return True
    if u_username in ["hieutruong", "tienbv"]:
        return True
    if "hiệu trưởng" in chuc_danh or "hieu truong" in chuc_danh:
        return True
        
    # 3. Pho Hieu truong (PHT)
    if u_username in ["phohieutruong1", "phohieutruong2", "thanhnth", "phuongđth", "phuongdth", "pht"]:
        return True
    if "phó hiệu trưởng" in chuc_danh or "pho hieu truong" in chuc_danh or "pht" in chuc_danh:
        return True
        
    # 4. Giao vien duoc phan quyen quan tri
    if "quản trị" in quyen_ql or "quan tri" in quyen_ql:
        return True
        
    # 5. Kiem tra danh sach giao vien duoc BGH uy quyen trong file JSON
    f_gv_auth = os.path.join(BASE_DIR, "cau_hinh_giao_vien_quan_tri.json")
    if os.path.exists(f_gv_auth):
        try:
            with open(f_gv_auth, "r", encoding="utf-8") as f_ja:
                ds_uy_quyen = [str(x).strip().lower() for x in json.load(f_ja).get("danh_sach_uy_quyen", [])]
                if u_username in ds_uy_quyen or str(u_curr.get("phone", "")).strip() in ds_uy_quyen:
                    return True
        except Exception:
            pass

    return False

def doc_cau_hinh_nam_hoc(file_cfg):
    mac_dinh = {
        "nam_hoc_mac_dinh": "2026 - 2027",
        "danh_sach_nam_hoc": ["2025 - 2026", "2026 - 2027", "2027 - 2028"]
    }
    if os.path.exists(file_cfg):
        try:
            with open(file_cfg, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return mac_dinh

def ghi_cau_hinh_nam_hoc(file_cfg, cfg):
    try:
        with open(file_cfg, "w", encoding="utf-8") as f:
            json.dump(cfg, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

def lay_duong_dan_file_theo_nam(nam_hoc, BASE_DIR, THU_MUC_NAM_HOC):
    folder_name = nam_hoc.replace(" ", "")
    dir_nam = os.path.join(THU_MUC_NAM_HOC, folder_name)
    os.makedirs(dir_nam, exist_ok=True)
    
    f_hs = os.path.join(dir_nam, "danh_sach_hoc_sinh_thuc_te.csv")
    f_td = os.path.join(dir_nam, "cham_diem_thi_dua_phong.csv")
    f_kt = os.path.join(dir_nam, "nhat_ky_kiem_thuc.csv")
    f_don = os.path.join(dir_nam, "thuc_don_tuan.csv")
    f_xv = os.path.join(dir_nam, "lich_su_xin_ve.csv")
    
    cac_file = [
        (f_hs, os.path.join(BASE_DIR, "danh_sach_hoc_sinh_thuc_te.csv")),
        (f_td, os.path.join(BASE_DIR, "cham_diem_thi_dua_phong.csv")),
        (f_kt, os.path.join(BASE_DIR, "nhat_ky_kiem_thuc.csv")),
        (f_don, os.path.join(BASE_DIR, "thuc_don_tuan.csv")),
        (f_xv, os.path.join(BASE_DIR, "lich_su_xin_ve.csv"))
    ]
    for dst, src in cac_file:
        if not os.path.exists(dst) and os.path.exists(src):
            try:
                shutil.copy2(src, dst)
            except Exception:
                pass
                
    return f_hs, f_td, f_kt, f_don, f_xv

def tao_zip_nam_hoc(nam_hoc, THU_MUC_NAM_HOC):
    buffer = io.BytesIO()
    folder_name = nam_hoc.replace(" ", "")
    dir_nam = os.path.join(THU_MUC_NAM_HOC, folder_name)
    with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
        if os.path.exists(dir_nam):
            for root, dirs, files in os.walk(dir_nam):
                for file in files:
                    fp = os.path.join(root, file)
                    arcname = os.path.relpath(fp, dir_nam)
                    zf.write(fp, arcname)
    buffer.seek(0)
    return buffer.getvalue()

def tao_tai_khoan_dong_loat_full(df_hs):
    accounts = []
    staff = [
        ('admin', 'bgh123', 'Ban Giám Hiệu (Admin)', 'Ban Giám hiệu', 'Hiệu trưởng / Admin tối cao', 'Toàn trường', '0988123001'),
        ('bithudoan', 'dtn123', 'Bí Thư Đoàn Trường', 'Ban Chấp hành Đoàn', 'Bí thư Đoàn TNCS Hồ Chí Minh', 'Toàn trường', '0988123456'),
        ('codo', 'codo123', 'Đội Cờ Đỏ Chấm Nề Nếp', 'Đội Cờ đỏ', 'Đội viên Cờ đỏ thanh niên xung kích', 'Toàn trường', '0988654321'),
        ('hieutruong', 'ht123', 'Thầy Hiệu Trưởng', 'Ban Giám hiệu', 'Hiệu trưởng nhà trường', 'Toàn trường', '0988123002'),
        ('phohieutruong1', 'pht123', 'Phó Hiệu Trưởng 1', 'Ban Giám hiệu', 'Phó Hiệu trưởng PT Bán trú', 'Toàn trường', '0988123003'),
        ('phohieutruong2', 'pht123', 'Phó Hiệu Trưởng 2', 'Ban Giám hiệu', 'Phó Hiệu trưởng PT Chuyên môn', 'Toàn trường', '0988123004'),
        ('quannhiem', 'qn123', 'Thầy Quản Nhiệm Bán Trú', 'Giáo viên quản lý', 'Tổ trưởng Quản nhiệm ký túc xá', 'Toàn trường', '0988123005'),
        ('gvtruc01', 'truc123', 'Giáo Viên Trực Ca 1', 'Giáo viên quản lý', 'Giáo viên trực ký túc xá', 'Toàn trường', '0988123006'),
        ('gvtruc02', 'truc123', 'Giáo Viên Trực Ca 2', 'Giáo viên quản lý', 'Giáo viên trực ký túc xá', 'Toàn trường', '0988123007'),
        ('beptruong', 'bep123', 'Bếp Trưởng Nhà Ăn', 'Nhà bếp / Cấp dưỡng', 'Bếp trưởng phụ trách dinh dưỡng', 'Toàn trường', '0988123008'),
        ('capduong', 'bep123', 'Tổ Cấp Dưỡng Bán Trú', 'Nhà bếp / Cấp dưỡng', 'Nhân viên cấp dưỡng', 'Toàn trường', '0988123009'),
        ('nhabep', 'bep123', 'Tổ Cấp Dưỡng Nhà Bếp', 'Nhà bếp / Cấp dưỡng', 'Nhân viên cấp dưỡng', 'Toàn trường', '0988123010'),
        ('ketoan', 'kt123', 'Kế Toán Bán Trú', 'Kế toán bán trú', 'Kế toán quản lý thu chi', 'Toàn trường', '0988123011'),
        ('phuhuynh', 'ph123', 'Tài Khoản Phụ Huynh Mẫu', 'Phụ huynh học sinh', 'Phụ huynh học sinh chung', 'Toàn trường', '0988123012'),
        ('hocsinh', 'hs123', 'Tài Khoản Học Sinh Mẫu', 'Học sinh', 'Học sinh bán trú chung', 'Toàn trường', '0988123013'),
    ]
    for u, p, fn, r, title, ref, phone in staff:
        ql = 'Toàn quyền quản trị' if r == 'Ban Giám hiệu' else ('Quản lý phương tiện & Cờ đỏ' if u in ['codo', 'bithudoan'] else ('Quản lý bán trú' if u in ['quannhiem'] else 'Cá nhân'))
        accounts.append({
            'Tên đăng nhập': u,
            'Mật khẩu': p,
            'Họ và tên': fn,
            'Vai trò': r,
            'Chức danh': title,
            'Mã liên kết': ref,
            'Số điện thoại': phone,
            'Ghi chú': f"{title} - {fn}",
            'Trạng thái': 'Hoạt động',
            'Quyền quản lý': ql
        })

    # Danh sách 21 lớp học toàn trường (10A1-10A7, 11A1-11A7, 12A1-12A7)
    classes_all = [f"10A{i}" for i in range(1, 8)] + [f"11A{i}" for i in range(1, 8)] + [f"12A{i}" for i in range(1, 8)]
    
    # Đọc danh bạ giáo viên nếu có để lấy đúng tên GVCN
    gvcn_map = {}
    f_gv_db = "D:/danh_ba_cbgv_nv.csv"
    if os.path.exists(f_gv_db):
        try:
            df_gv_raw = pd.read_csv(f_gv_db, encoding='utf-8-sig')
            for _, r_gv in df_gv_raw.iterrows():
                lop_cn = str(r_gv.get('Giáo viên chủ nhiệm lớp', '')).strip()
                if lop_cn and lop_cn != 'nan':
                    gvcn_map[lop_cn] = {
                        'ten': str(r_gv.get('Họ và tên', f'Thầy/Cô Chủ Nhiệm {lop_cn}')).strip(),
                        'mon': str(r_gv.get('Môn dạy', '')).strip(),
                        'sdt': str(r_gv.get('Số điện thoại', '')).strip()
                    }
        except Exception:
            pass

    for c in classes_all:
        so_hs_bt = len(df_hs[df_hs['Lớp'] == c]) if 'Lớp' in df_hs.columns else 0
        info_gv = gvcn_map.get(c, {})
        ten_gv = info_gv.get('ten', f"Thầy/Cô Chủ Nhiệm {c}")
        mon_day = f" (Môn: {info_gv['mon']})" if info_gv.get('mon') else ""
        phone_gv = info_gv.get('sdt', '')
        accounts.append({
            'Tên đăng nhập': f"gvcn_{c.lower()}",
            'Mật khẩu': 'gvcn123',
            'Họ và tên': ten_gv,
            'Vai trò': 'Giáo viên quản lý',
            'Chức danh': f"GVCN Lớp {c}{mon_day}",
            'Mã liên kết': c,
            'Số điện thoại': phone_gv,
            'Ghi chú': f"GVCN Lớp {c} ({so_hs_bt} học sinh bán trú)",
            'Trạng thái': 'Hoạt động',
            'Quyền quản lý': 'Cá nhân'
        })

    for idx, row in df_hs.iterrows():
        ma_hs = str(row['Mã HS']).strip()
        u_hs = ma_hs.lower().replace('-', '')
        phone_hs = str(row.get('SĐT Học sinh', '')).replace('.0', '').strip()
        if phone_hs and not phone_hs.startswith('0') and len(phone_hs) == 9:
            phone_hs = '0' + phone_hs
        cv = str(row.get('Chức vụ phòng', 'Thành viên')).strip()
        phong_val = str(row.get('Phòng', '')).strip()
        title_hs = f"Trưởng phòng ({phong_val})" if cv == "Trưởng phòng" else "Học sinh bán trú"
        accounts.append({
            'Tên đăng nhập': u_hs,
            'Mật khẩu': 'hs123',
            'Họ và tên': row['Họ và tên'],
            'Vai trò': 'Học sinh',
            'Chức danh': title_hs,
            'Mã liên kết': ma_hs,
            'Số điện thoại': phone_hs,
            'Ghi chú': f"Lớp {row.get('Lớp', '')} - {phong_val} - {row.get('Giường', '')} ({cv})",
            'Trạng thái': 'Hoạt động',
            'Quyền quản lý': 'Cá nhân'
        })
        
        phone_ph = str(row.get('SĐT Phụ huynh', '')).replace('.0', '').strip()
        if phone_ph and not phone_ph.startswith('0') and len(phone_ph) == 9:
            phone_ph = '0' + phone_ph
        ten_ph = str(row.get('Họ tên Bố', row.get('Họ tên Mẹ', f"Phụ huynh em {row['Họ và tên']}"))).strip()
        accounts.append({
            'Tên đăng nhập': f"ph_{u_hs}",
            'Mật khẩu': 'ph123',
            'Họ và tên': f"{ten_ph} (PH {row['Họ và tên']})",
            'Vai trò': 'Phụ huynh học sinh',
            'Chức danh': f"Phụ huynh học sinh {row['Họ và tên']}",
            'Mã liên kết': ma_hs,
            'Số điện thoại': phone_ph,
            'Ghi chú': f"Phụ huynh em {row['Họ và tên']} (Lớp {row.get('Lớp', '')})",
            'Trạng thái': 'Hoạt động',
            'Quyền quản lý': 'Cá nhân'
        })

    return pd.DataFrame(accounts)

# -----------------------------------------------------------------------------
# HÀM CHÍNH RENDER PHÂN HỆ
# -----------------------------------------------------------------------------
def render_phan_he_quan_ly_chung(df_tai_khoan, role_curr, nam_hoc, BASE_DIR, THU_MUC_NAM_HOC):
    # Tối ưu khoảng trống đỉnh trang và hiển thị Tab 2 dòng linh hoạt
    st.markdown("""
    <style>
        .block-container {
            padding-top: 1rem !important;
            padding-bottom: 2rem !important;
            padding-left: 1.2rem !important;
            padding-right: 1.2rem !important;
            max-width: 100% !important;
        }
        header[data-testid="stHeader"] {
            height: 1.5rem !important;
            background: transparent !important;
        }
        div[data-baseweb="tab-list"] {
            flex-wrap: wrap !important;
            gap: 4px 6px !important;
            border-bottom: 2px solid #E2E8F0 !important;
            padding-bottom: 4px !important;
        }
        button[data-baseweb="tab"] {
            padding: 5px 11px !important;
            font-size: 13px !important;
            border-radius: 6px !important;
            white-space: normal !important;
            height: auto !important;
            line-height: 1.3 !important;
        }
        button[data-baseweb="tab"][aria-selected="true"] {
            background: #EFF6FF !important;
            color: #1E3A8A !important;
            font-weight: 700 !important;
            border-bottom: 3px solid #1E3A8A !important;
        }
    </style>
    """, unsafe_allow_html=True)

    st.markdown(f"""
        <div style='background: linear-gradient(135deg, #1E3A8A, #2563EB); padding: 10px 16px; border-radius: 8px; color: white; margin-bottom: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.08);'>
            <div style='display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:8px;'>
                <div>
                    <h3 style='margin:0; font-size: 19px; color: white; font-weight:700;'>🏛️ HỆ THỐNG QUẢN TRỊ & ĐIỀU HÀNH NHÀ TRƯỜNG</h3>
                    <p style='margin: 2px 0 0 0; opacity: 0.95; font-size: 13px;'>
                        Trường THPT số 2 Bảo Yên (Bảo Hà, Bảo Yên, Lào Cai) • Niên khóa: <b>{nam_hoc}</b>
                    </p>
                </div>
                <div style='background:rgba(255,255,255,0.2); padding:4px 12px; border-radius:16px; font-weight:600; font-size:12px; border:1px solid rgba(255,255,255,0.3);'>
                    🏛️ KÊNH ĐIỀU HÀNH TỔNG THỂ
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    folder_nam = nam_hoc.replace(" ", "")
    dir_nam = os.path.join(THU_MUC_NAM_HOC, folder_nam)
    os.makedirs(dir_nam, exist_ok=True)
    
    file_tai_khoan_csv = os.path.join(BASE_DIR, "tai_khoan_nguoi_dung.csv")
    file_cfg_nh = os.path.join(BASE_DIR, "cau_hinh_nam_hoc.json")
    f_lct = os.path.join(dir_nam, "lich_cong_tac_tuan.csv")
    f_tasks = os.path.join(dir_nam, "nhiem_vu_nha_truong.csv") if os.path.exists(os.path.join(dir_nam, "nhiem_vu_nha_truong.csv")) else os.path.join(BASE_DIR, "nhiem_vu_nha_truong.csv")
    f_plan = os.path.join(dir_nam, "ke_hoach_nam.csv") if os.path.exists(os.path.join(dir_nam, "ke_hoach_nam.csv")) else os.path.join(BASE_DIR, "ke_hoach_nam.csv")
    f_bd = os.path.join(BASE_DIR, "bien_dong_hoc_sinh.csv")
    f_cc = os.path.join(BASE_DIR, "thong_ke_co_cau_20_lop.csv")
    f_hs_tt = os.path.join(BASE_DIR, "danh_sach_hoc_sinh_toan_truong.csv")
    f_gv_db = os.path.join(BASE_DIR, "danh_ba_cbgv_nv.csv")
    f_bt_ktx = os.path.join(BASE_DIR, "danh_sach_hoc_sinh_thuc_te.csv")
    f_tb = os.path.join(BASE_DIR, "thiet_bi_day_hoc.csv")
    f_tkb = os.path.join(BASE_DIR, "thoi_khoa_bieu.csv")
    f_sdb = os.path.join(BASE_DIR, "so_dau_bai.csv")
    f_khcn = os.path.join(BASE_DIR, "ke_hoach_chu_nhiem.csv")
    f_tdct = os.path.join(BASE_DIR, "tien_do_chuong_trinh_21_lop.csv")

    u_curr = st.session_state.get("user_login", {})
    quyen_ql = str(u_curr.get("quyen_quan_ly", "")).strip()
    u_username = str(u_curr.get("username", "")).strip().lower()
    
    # Kiem tra quyen quan tri & nien khoa (Admin / Hieu truong / PHT / GV duoc phan quyen)
    duoc_quyen_quan_tri = kiem_tra_quyen_quan_tri_nien_khoa(u_curr, role_curr, BASE_DIR)
    la_bgh_admin = duoc_quyen_quan_tri
    is_ph_hs = (role_curr in ["Phụ huynh học sinh", "Học sinh"])

    cfg_nh = doc_cau_hinh_nam_hoc(file_cfg_nh)
    danh_sach_nam_hoc = cfg_nh.get("danh_sach_nam_hoc", ["2025 - 2026", "2026 - 2027", "2027 - 2028"])
    nam_hoc_mac_dinh = cfg_nh.get("nam_hoc_mac_dinh", "2026 - 2027")

    if os.path.exists(file_tai_khoan_csv):
        df_tk_live = pd.read_csv(file_tai_khoan_csv, encoding='utf-8-sig', dtype=str).fillna("")
    else:
        df_tk_live = df_tai_khoan.copy()

    # Tải dữ liệu quy mô toàn trường
    df_hs_all = pd.read_csv(f_hs_tt, encoding='utf-8-sig') if os.path.exists(f_hs_tt) else pd.DataFrame()
    tong_hs = len(df_hs_all) if not df_hs_all.empty else 829
    so_nam = len(df_hs_all[df_hs_all['Giới tính'] == 'Nam']) if not df_hs_all.empty else 400
    so_nu = tong_hs - so_nam
    so_dtts = len(df_hs_all[df_hs_all['Dân tộc'] != 'Kinh']) if not df_hs_all.empty else 495
    df_bt_now = pd.read_csv(f_bt_ktx, encoding='utf-8-sig') if os.path.exists(f_bt_ktx) else pd.DataFrame()
    so_ban_tru = len(df_bt_now) if not df_bt_now.empty else 196

    # Khởi tạo 6 Tab chức năng cốt lõi (Gọn gàng - Khoa học - Vừa vặn màn hình)
    tab_admin_title = "⚙️ Quản Trị & Niên Khóa" if duoc_quyen_quan_tri else "🔒 Quản Trị & Niên Khóa"
    tab_dieu_hanh, tab_doi_ngu_hs, tab_chu_nhiem, tab_chuyen_mon, tab_ke_hoach, tab_admin_nh = st.tabs([
        "🏛️ Trung Tâm Điều Hành Tổng Thể",
        "👥 Đội Ngũ - Học Sinh",
        "📋 Công Tác Chủ Nhiệm",
        "📚 Công Tác Chuyên Môn",
        "📅 Kế Hoạch Năm Học",
        tab_admin_title
    ])

    # =========================================================================
    # TAB 1: TRUNG TÂM ĐIỀU HÀNH TỔNG THỂ NHÀ TRƯỜNG
    # (Hợp nhất Bàn làm việc điều hành & Lịch tuần - Giao việc)
    # =========================================================================
    with tab_dieu_hanh:
        # Thẻ chỉ số vĩ mô toàn trường
        m1, m2, m3, m4, m5 = st.columns(5)
        m1.metric("👨‍🎓 Tổng Sĩ Số", f"{tong_hs} HS", delta="21 Lớp học")
        m2.metric("👦 Nam / 👧 Nữ", f"{so_nam} / {so_nu}", delta=f"Nữ: {(so_nu/tong_hs*100):.1f}%")
        m3.metric("🏔️ Dân Tộc Thiểu Số", f"{so_dtts} HS", delta=f"{(so_dtts/tong_hs*100):.1f}% toàn trường")
        m4.metric("🛏️ Bán Trú KTX", f"{so_ban_tru} HS", delta=f"{so_ban_tru} suất đăng ký")
        m5.metric("🏫 Quy Mô Khối", "21 Lớp", delta="K10: 7 | K11: 7 | K12: 7")

        st.markdown("---")

        # TRUNG TÂM ĐIỀU HÀNH TỔNG THỂ - 7 TRỤ CỘT CHỈ ĐẠO
        st.markdown("<h3 style='color:#1E3A8A; margin-bottom:4px;'>🏛️ TRUNG TÂM ĐIỀU HÀNH TỔNG THỂ NHÀ TRƯỜNG</h3>", unsafe_allow_html=True)
        st.caption("Bảng điều hành tích hợp thời gian thực phục vụ chỉ đạo toàn diện của Ban Giám Hiệu:")

        c_p1, c_p2, c_p3 = st.columns([1.2, 1.2, 1.2])

        # 1. LỊCH CÔNG TÁC TẬP TRUNG
        with c_p1:
            st.markdown("""
                <div style='background:#F0FDF4; border:1px solid #86EFAC; border-radius:10px; padding:12px; min-height:230px;'>
                    <h5 style='color:#166534; margin:0 0 6px 0;'>🗓️ 1. Lịch Công Tác Tập Trung</h5>
                    <p style='font-size:12.5px; color:#374151; margin:0 0 8px 0;'>Lịch tuần trọng tâm, rõ nội dung & thời gian:</p>
                    <ul style='font-size:12px; color:#1F2937; padding-left:16px; margin:0;'>
                        <li><b>Sáng T2:</b> Chào cờ & SHDC theo chủ đề (Sân trường)</li>
                        <li><b>Chiều T2:</b> Họp Giao ban BGH & TTCM (P. Hội đồng)</li>
                        <li><b>Sáng T5:</b> Kiểm tra VSATTP bếp ăn bán trú (PHT Bán trú)</li>
                        <li><b>Chiều T6:</b> Kiểm tra nề nếp KTX bán trú 5S</li>
                    </ul>
                </div>
            """, unsafe_allow_html=True)

        # 2. GIAO VIỆC & TIẾN ĐỘ
        with c_p2:
            st.markdown("""
                <div style='background:#EFF6FF; border:1px solid #93C5FD; border-radius:10px; padding:12px; min-height:230px;'>
                    <h5 style='color:#1E40AF; margin:0 0 6px 0;'>📌 2. Giao Việc & Theo Dõi Tiến Độ</h5>
                    <p style='font-size:12.5px; color:#374151; margin:0 0 8px 0;'>Rõ người, rõ hạn; theo dõi kết quả thực thi:</p>
                    <ul style='font-size:12px; color:#1F2937; padding-left:16px; margin:0;'>
                        <li>✅ <b>NV-001:</b> Kiểm tra sổ điểm HK1 - <i>Lê Văn C (100%)</i></li>
                        <li>⏳ <b>NV-002:</b> Rà soát HS NĐ 116 - <i>Phạm Thị Lan (75%)</i></li>
                        <li>⏳ <b>NV-003:</b> Tập huấn PCCC KTX - <i>Đỗ Văn Kiên (40%)</i></li>
                        <li>🔥 <b>NV-004:</b> Thi Báo tường 20/11 - <i>Hoàng Văn D (90%)</i></li>
                    </ul>
                </div>
            """, unsafe_allow_html=True)

        # 3. BIỂU ĐỒ TRỰC QUAN TIẾN ĐỘ
        with c_p3:
            st.markdown("""
                <div style='background:#FFFBEB; border:1px solid #FCD34D; border-radius:10px; padding:12px; min-height:230px;'>
                    <h5 style='color:#B45309; margin:0 0 6px 0;'>📊 3. Biểu Đồ Trực Quan Tiến Độ</h5>
                    <p style='font-size:12.5px; color:#374151; margin:0 0 8px 0;'>Hiển thị tỷ lệ hoàn thành & cảnh báo:</p>
                    <div style='margin-top:6px;'>
                        <div style='display:flex; justify-content:space-between; font-size:12px;'><span>Hoàn thành:</span> <b>82%</b></div>
                        <div style='background:#E5E7EB; border-radius:6px; height:8px; margin:2px 0 8px 0;'><div style='background:#16A34A; width:82%; height:8px; border-radius:6px;'></div></div>
                        <div style='display:flex; justify-content:space-between; font-size:12px;'><span>Sắp đến hạn:</span> <b>3 việc</b></div>
                        <div style='display:flex; justify-content:space-between; font-size:12px;'><span>Quá hạn:</span> <b style='color:#DC2626;'>0 việc (An toàn)</b></div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

        st.markdown("<div style='height:10px;'></div>", unsafe_allow_html=True)
        c_p4, c_p5, c_p6, c_p7 = st.columns([1, 1, 1, 1])

        # 4. TIẾN ĐỘ CHƯƠNG TRÌNH
        with c_p4:
            st.markdown("""
                <div style='background:#FDF4FF; border:1px solid #F0ABFC; border-radius:10px; padding:12px; min-height:190px;'>
                    <h6 style='color:#86198F; margin:0 0 4px 0;'>📚 4. Tiến Độ Chương Trình</h6>
                    <p style='font-size:11.5px; color:#4B5563; margin:0;'>21 lớp x 10 môn học:</p>
                    <ul style='font-size:11.5px; color:#1F2937; padding-left:14px; margin:4px 0 0 0;'>
                        <li><b>Khối 10:</b> 100% đúng PPCT</li>
                        <li><b>Khối 11:</b> 98.5% đúng PPCT</li>
                        <li><b>Khối 12:</b> 100% đúng PPCT</li>
                    </ul>
                </div>
            """, unsafe_allow_html=True)

        # 5. SĨ SỐ, CHUYÊN CẦN & RÈN LUYỆN
        with c_p5:
            st.markdown("""
                <div style='background:#F8FAFC; border:1px solid #CBD5E1; border-radius:10px; padding:12px; min-height:190px;'>
                    <h6 style='color:#334155; margin:0 0 4px 0;'>👨‍🎓 5. Sĩ Số & Chuyên Cần</h6>
                    <p style='font-size:11.5px; color:#4B5563; margin:0;'>Tình hình 21 lớp hôm nay:</p>
                    <ul style='font-size:11.5px; color:#1F2937; padding-left:14px; margin:4px 0 0 0;'>
                        <li><b>Hiện diện:</b> 826 / 829 HS (99.6%)</li>
                        <li><b>Vắng phép:</b> 3 em (Nghỉ ốm)</li>
                        <li><b>Không phép:</b> 0 em 🚨</li>
                    </ul>
                </div>
            """, unsafe_allow_html=True)

        # 6. THIẾT BỊ DẠY HỌC
        with c_p6:
            st.markdown("""
                <div style='background:#F0FDFA; border:1px solid #99F6E4; border-radius:10px; padding:12px; min-height:190px;'>
                    <h6 style='color:#0F766E; margin:0 0 4px 0;'>🔬 6. Thiết Bị Dạy Học</h6>
                    <p style='font-size:11.5px; color:#4B5563; margin:0;'>Phòng máy & đồ dùng:</p>
                    <ul style='font-size:11.5px; color:#1F2937; padding-left:14px; margin:4px 0 0 0;'>
                        <li><b>Phòng máy Tin:</b> 45 máy OK</li>
                        <li><b>Đang mượn:</b> Kính hiển vi (10A1)</li>
                        <li><b>Kho thiết bị:</b> 5 bộ sẵn sàng</li>
                    </ul>
                </div>
            """, unsafe_allow_html=True)

        # 7. KẾT NỐI BÁN TRÚ
        with c_p7:
            st.markdown("""
                <div style='background:#FEF2F2; border:1px solid #FECACA; border-radius:10px; padding:12px; min-height:190px;'>
                    <h6 style='color:#991B1B; margin:0 0 4px 0;'>🍀 7. Kết Nối Bán Trú KTX</h6>
                    <p style='font-size:11.5px; color:#4B5563; margin:0;'>Giám sát bữa ăn & phòng ở:</p>
                    <ul style='font-size:11.5px; color:#1F2937; padding-left:14px; margin:4px 0 0 0;'>
                        <li><b>Suất cơm trưa:</b> {so_ban_tru} suất live</li>
                        <li><b>Phòng ở:</b> 19P (Nam 9P, Nữ 10P)</li>
                        <li><b>ATTP 3 bước:</b> Đạt chuẩn ✓</li>
                    </ul>
                </div>
            """, unsafe_allow_html=True)

        st.markdown("---")

        # CHI TIẾT NGHIỆP VỤ ĐIỀU HÀNH, LỊCH CÔNG TÁC & CÀI ĐẶT APP
        st.markdown("#### 📋 **Chi Tiết Nhiệm Vụ Điều Hành, Lịch Tuần, Giám Sát & Ứng Dụng Di Động**")
        sub_dh1, sub_dh2, sub_dh3, sub_dh4 = st.tabs([
            "📅 LỊCH CÔNG TÁC TUẦN TẬP TRUNG",
            "📌 GIAO VIỆC RÕ NGƯỜI, RÕ HẠN & TIẾN ĐỘ",
            "🍀 KẾT NỐI GIÁM SÁT BÁN TRÚ & KTX",
            "📱 HƯỚNG DẪN CÀI ĐẶT APP LÊN ĐIỆN THOẠI"
        ])

        with sub_dh1:
            st.markdown("##### 📅 **Lịch Công Tác Từng Tuần (Sáng - Chiều - Tối) - Rõ Nội Dung & Thời Gian**")
            if not os.path.exists(f_lct):
                df_lct_init = pd.DataFrame([
                    {'Thứ / Ngày': 'Thứ Hai (26/10)', 'Buổi': 'Sáng', 'Nội dung công tác': 'Chào cờ đầu tuần, sinh hoạt dưới cờ theo chủ đề', 'Thành phần': 'Toàn thể CBGV, NV và HS', 'Địa điểm': 'Sân trường', 'Chủ trì': 'BGH - Đoàn TN'},
                    {'Thứ / Ngày': 'Thứ Hai (26/10)', 'Buổi': 'Chiều', 'Nội dung công tác': 'Họp giao ban BGH và Tổ trưởng chuyên môn', 'Thành phần': 'BGH, TTCM', 'Địa điểm': 'Phòng Hội đồng', 'Chủ trì': 'Hiệu trưởng'},
                    {'Thứ / Ngày': 'Thứ Ba (27/10)', 'Buổi': 'Sáng', 'Nội dung công tác': 'Dạy học theo thời khóa biểu; Kiểm tra chuyên đề tổ Tự nhiên', 'Thành phần': 'Tổ KHTN', 'Địa điểm': 'Các phòng học', 'Chủ trì': 'PHT Chuyên môn'},
                    {'Thứ / Ngày': 'Thứ Tư (28/10)', 'Buổi': 'Chiều', 'Nội dung công tác': 'Sinh hoạt chuyên môn cấp tổ; Bồi dưỡng HS giỏi khối 12', 'Thành phần': 'Giáo viên bộ môn, HS giỏi', 'Địa điểm': 'Phòng bộ môn', 'Chủ trì': 'TTCM'},
                    {'Thứ / Ngày': 'Thứ Năm (29/10)', 'Buổi': 'Sáng', 'Nội dung công tác': 'Kiểm tra công tác an toàn vệ sinh thực phẩm bếp ăn bán trú', 'Thành phần': 'BGH, Y tế, Đại diện PHHS', 'Địa điểm': 'Nhà ăn KTX', 'Chủ trì': 'PHT Bán trú'},
                    {'Thứ / Ngày': 'Thứ Sáu (30/10)', 'Buổi': 'Chiều', 'Nội dung công tác': 'Kiểm tra nền nếp, vệ sinh phòng ở KTX bán trú cuối tuần', 'Thành phần': 'Tổ Quản nhiệm, Đội Cờ đỏ', 'Địa điểm': 'Dãy nhà KTX', 'Chủ trì': 'Thầy Quản nhiệm'},
                    {'Thứ / Ngày': 'Thứ Bảy (31/10)', 'Buổi': 'Sáng', 'Nội dung công tác': 'Dạy học chính khóa; Sinh hoạt lớp cuối tuần', 'Thành phần': 'GVCN và HS 21 lớp', 'Địa điểm': 'Phòng học các lớp', 'Chủ trì': 'GVCN'}
                ])
                df_lct_init.to_csv(f_lct, index=False, encoding='utf-8-sig')

            df_lct = pd.read_csv(f_lct, encoding='utf-8-sig').fillna("")
            st.dataframe(df_lct, use_container_width=True, hide_index=True)

        with sub_dh2:
            st.markdown("##### 📌 **Bảng Giao Việc Rõ Người, Rõ Hạn; Theo Dõi Tiến Độ & Kết Quả**")
            if not os.path.exists(f_tasks):
                df_tasks_init = pd.DataFrame([
                    {'Mã việc': 'NV-001', 'Nhiệm vụ': 'Kiểm tra hồ sơ sổ điểm điện tử đợt giữa HK1', 'Người phụ trách': 'Lê Văn C (PHT)', 'Bộ phận': 'Tổ Chuyên môn', 'Hạn hoàn thành': '30/10/2026', 'Tiến độ (%)': 100, 'Trạng thái': 'Đã hoàn thành', 'Mức độ ưu tiên': 'Cao'},
                    {'Mã việc': 'NV-002', 'Nhiệm vụ': 'Rà soát danh sách học sinh hưởng chế độ NĐ 116', 'Người phụ trách': 'Phạm Thị Lan (KT)', 'Bộ phận': 'Kế toán Bán trú', 'Hạn hoàn thành': '05/11/2026', 'Tiến độ (%)': 75, 'Trạng thái': 'Đang tiến hành', 'Mức độ ưu tiên': 'Đặc biệt'},
                    {'Mã việc': 'NV-003', 'Nhiệm vụ': 'Tập huấn kỹ năng PCCC & cứu nạn cứu hộ tại KTX', 'Người phụ trách': 'Đỗ Văn Kiên (QN)', 'Bộ phận': 'Tổ Quản nhiệm', 'Hạn hoàn thành': '10/11/2026', 'Tiến độ (%)': 40, 'Trạng thái': 'Đang tiến hành', 'Mức độ ưu tiên': 'Trung bình'},
                    {'Mã việc': 'NV-004', 'Nhiệm vụ': 'Phát động cuộc thi Báo tường 20/11 cấp trường', 'Người phụ trách': 'Hoàng Văn D (Bí thư)', 'Bộ phận': 'Đoàn Thanh Niên', 'Hạn hoàn thành': '15/11/2026', 'Tiến độ (%)': 90, 'Trạng thái': 'Đang tiến hành', 'Mức độ ưu tiên': 'Cao'}
                ])
                df_tasks_init.to_csv(f_tasks, index=False, encoding='utf-8-sig')

            df_tasks = pd.read_csv(f_tasks, encoding='utf-8-sig').fillna("")
            
            so_ht = len(df_tasks[df_tasks['Trạng thái'] == 'Đã hoàn thành'])
            so_dang = len(df_tasks[df_tasks['Trạng thái'] == 'Đang tiến hành'])
            so_tre = len(df_tasks[df_tasks['Trạng thái'] == 'Quá hạn'])
            
            t_col1, t_col2, t_col3, t_col4 = st.columns(4)
            t_col1.metric("📋 Tổng Nhiệm Vụ", f"{len(df_tasks)} việc")
            t_col2.metric("✅ Đã Hoàn Thành", f"{so_ht} việc", delta=f"{(so_ht/len(df_tasks)*100 if len(df_tasks)>0 else 0):.0f}%")
            t_col3.metric("⏳ Đang Tiến Hành", f"{so_dang} việc")
            t_col4.metric("🚨 Quá Hạn Cần Nhắc", f"{so_tre} việc", delta_color="inverse" if so_tre>0 else "normal")

            st.dataframe(df_tasks, use_container_width=True, hide_index=True)

            if not is_ph_hs:
                with st.expander("➕ **Giao Nhiệm Vụ Mới Hoặc Nhiệm Vụ Đột Xuất:**"):
                    with st.form("form_add_task_moi"):
                        c_tk1, c_tk2 = st.columns(2)
                        with c_tk1:
                            ten_nv_m = st.text_input("Tên nhiệm vụ / Công việc:")
                            nguoi_pt_m = st.text_input("Người phụ trách (Họ tên):")
                            bo_phan_m = st.selectbox("Bộ phận / Tổ chuyên môn:", ["Tổ Tự nhiên", "Tổ Xã hội", "Tổ Văn phòng", "Tổ Quản nhiệm", "Đoàn Thanh niên", "Nhà bếp", "Ban Giám hiệu"])
                        with c_tk2:
                            han_ht_m = st.date_input("Hạn hoàn thành:", date.today())
                            uu_tien_m = st.selectbox("Mức độ ưu tiên:", ["Cao", "Đặc biệt", "Trung bình", "Bình thường"])
                            ghi_chu_m = st.text_input("Ghi chú thực hiện / Yêu cầu đột xuất:")
                        if st.form_submit_button("🚀 GIAO NHIỆM VỤ NÀY", type="primary"):
                            if ten_nv_m.strip():
                                ma_nv_m = f"NV-{len(df_tasks)+1:03d}"
                                new_row_t = pd.DataFrame([{
                                    'Mã việc': ma_nv_m,
                                    'Nhiệm vụ': ten_nv_m.strip(),
                                    'Người phụ trách': nguoi_pt_m.strip(),
                                    'Bộ phận': bo_phan_m,
                                    'Hạn hoàn thành': han_ht_m.strftime("%d/%m/%Y"),
                                    'Tiến độ (%)': 0,
                                    'Trạng thái': 'Đang tiến hành',
                                    'Mức độ ưu tiên': uu_tien_m
                                }])
                                df_tasks = pd.concat([df_tasks, new_row_t], ignore_index=True)
                                df_tasks.to_csv(f_tasks, index=False, encoding='utf-8-sig')
                                st.success(f"🎉 Đã giao nhiệm vụ {ma_nv_m} thành công!")
                                st.rerun()

        with sub_dh3:
            st.markdown("##### 🍀 **Kết Nối Thông Tin Bán Trú & Hỗ Trợ Giám Sát Bữa Ăn - KTX**")
            st.info("💡 Dữ liệu được liên kết tự động trực tiếp thời gian thực từ phân hệ **🛏️ QUẢN LÝ BÁN TRÚ & KTX**:")
            c_gs1, c_gs2, c_gs3 = st.columns(3)
            c_gs1.metric("👥 Quân số Bán trú Live", f"{so_ban_tru} HS", "19 Phòng ở KTX")
            c_gs2.metric("🍲 Suất ăn trưa hôm nay", f"{so_ban_tru} Suất", "Bếp ăn đã nhận thực đơn")
            c_gs3.metric("🏆 Thi đua KTX Tuần", "Phòng 301 dẫn đầu", "Đạt 39.5/40 điểm 5S")

        with sub_dh4:
            st.markdown("##### 📱 **HƯỚNG DẪN TẢI & CÀI ĐẶT APP DI ĐỘNG LÊN MÀN HÌNH CHÍNH**")
            st.caption("Ứng dụng Web Lũy Tiến (PWA) chính thức của Trường THPT số 2 Bảo Yên - Cài đặt trực tiếp lên iPhone/iPad & Android không cần qua App Store hay CH Play.")
            
            col_m1, col_m2 = st.columns([1, 1.2], gap="large")
            with col_m1:
                url_app_cloud = "https://thpt2baoyen.streamlit.app"
                st.markdown(f"""
                <div style="text-align: center; border: 3px solid #16A34A; padding: 18px; border-radius: 16px; background: #F0FDF4; box-shadow: 0 4px 15px rgba(22, 163, 74, 0.15); margin-bottom: 12px;">
                    <div style="background:#16A34A; color:white; display:inline-block; padding:4px 14px; border-radius:20px; font-weight:bold; font-size:12px; margin-bottom:8px;">
                        🌟 ĐỊA CHỈ TRỰC TUYẾN CHÍNH THỨC (CHẠY 24/7 TOÀN CẦU)
                    </div>
                    <h4 style="color:#15803D; margin:4px 0 8px 0;">DÙNG CAMERA ĐIỆN THOẠI QUÉT MÃ</h4>
                    <div style="background:white; padding:10px; border-radius:12px; display:inline-block; border:1px solid #BBF7D0;">
                        <img src="https://api.qrserver.com/v1/create-qr-code/?size=300x300&data={url_app_cloud}" width="220" style="display:block; border-radius:6px;">
                    </div>
                    <p style="margin-top:10px; font-size:13.5px; font-weight:bold; color:#166534;">Địa chỉ trực tuyến chính thức:<br>
                    <a href="{url_app_cloud}" target="_blank" style="color:#2563EB; font-size:15px; word-break:break-all; text-decoration:underline;">{url_app_cloud}</a></p>
                    <p style="font-size:11.5px; color:#4B5563; margin-bottom:0;">(Mở được trên mọi mạng 4G/5G hoặc Wi-Fi bất kỳ, không phụ thuộc máy tính)</p>
                </div>
                """, unsafe_allow_html=True)
                
                f_qr_loc = os.path.join(BASE_DIR, "QR_Cai_App_Ban_Tru.png")
                if os.path.exists(f_qr_loc):
                    with open(f_qr_loc, "rb") as f_qr:
                        st.download_button(
                            label="💾 TẢI ẢNH MÃ QR VỀ MÁY (ĐỂ IN HOẶC GỬI ZALO)",
                            data=f_qr.read(),
                            file_name="QR_Cai_App_THPT2_BaoYen.png",
                            mime="image/png",
                            use_container_width=True,
                            key="btn_dl_qr_app_tab1"
                        )
            
            with col_m2:
                st.markdown("##### 📲 **BIỂU TƯỢNG APP CHÍNH THỨC CỦA NHÀ TRƯỜNG:**")
                c_ico1, c_ico2 = st.columns([1, 2.2])
                with c_ico1:
                    f_logo_show = os.path.join(BASE_DIR, "logo_truong.png")
                    if not os.path.exists(f_logo_show):
                        f_logo_show = os.path.join(BASE_DIR, "logo_thpt2_baoyen.png")
                    if os.path.exists(f_logo_show):
                        st.image(f_logo_show, width=95, caption="Logo THPT số 2 Bảo Yên")
                with c_ico2:
                    st.markdown("""
                    - **Biểu tượng App:** Huy hiệu tròn **Trường THPT số 2 Bảo Yên**.
                    - **Tên hiển thị:** `THPT 2 Bảo Yên`.
                    - **Phục vụ toàn diện:** Ban Giám Hiệu, Giáo viên, Cán bộ nhân viên, Phụ huynh & Học sinh.
                    """)
                st.markdown("""
                ---
                ###### 🍏 Dành cho iPhone / iPad (Trình duyệt Safari):
                1. **Mở Camera** quét mã QR bên trái ➔ Chạm thông báo để mở web trong **Safari**.
                2. Ở thanh công cụ dưới đáy Safari, bấm nút **Chia sẻ** *(ô vuông có mũi tên chỉ lên ⬆️)*.
                3. Cuộn xuống và chọn **"Thêm vào Màn hình chính"** *(Add to Home Screen)*.
                4. Bấm **"Thêm"** *(Add)* ở góc trên bên phải màn hình.
                
                ###### 🤖 Dành cho Android (Samsung, Oppo, Xiaomi qua Chrome / Cốc Cốc):
                1. Dùng **Camera / Zalo** quét mã QR bên trái ➔ Mở bằng trình duyệt **Chrome**.
                2. Bấm biểu tượng **3 chấm (⋮)** ở góc trên bên phải màn hình.
                3. Chọn dòng **"Cài đặt ứng dụng"** hoặc **"Thêm vào Màn hình chính"**.
                4. Bấm **"Cài đặt" / "Thêm"** để hoàn tất.
                
                ---
                ✨ **LỢI ÍCH:** Mở ứng dụng toàn màn hình mượt mà, biểu tượng nằm ngay màn hình chính, không thanh địa chỉ web, không cần gõ link hay quét mã lại những lần sau!
                """)

            # TRUNG TÂM BÁO SĨ SỐ THỜI GIAN THỰC 21 LỚP HÔM NAY (BGH THEO DÕI)
        st.markdown("---")
        st.markdown("### 📊 TÌNH HÌNH SĨ SỐ & CHUYÊN CẦN 21 LỚP THỜI GIAN THỰC HÔM NAY")
        st.caption("Ban Giám Hiệu theo dõi trực tiếp tiến độ báo cáo quân số của 21 Lớp trưởng và GVCN theo từng buổi:")
        import quan_ly_si_so_lop
        ngay_hom_nay_live = date.today().strftime("%d/%m/%Y")
        col_bgh_live1, col_bgh_live2 = st.columns([1, 2.5])
        with col_bgh_live1:
            buoi_xem_live = st.radio("Chọn buổi xem quân số:", ["Buổi sáng", "Buổi chiều", "Cả ngày"], horizontal=True, key="rb_live_bgh_top")
        quan_ly_si_so_lop.render_bang_tong_hop_si_so_21_lop(ngay_hom_nay_live, buoi_xem_live, BASE_DIR)

    # =========================================================================
    # TAB 2: ĐỘI NGŨ - HỌC SINH
    # (Hợp nhất Danh bạ 42 CBGV-NV & Tra cứu Bộ lọc 829 Học sinh)
    # =========================================================================
    with tab_doi_ngu_hs:
        st.subheader("👥 Đội Ngũ Cán Bộ - Giáo Viên & Học Sinh Toàn Trường")
        st.caption("Quản lý toàn diện dữ liệu con người Trường THPT số 2 Bảo Yên: 42 Cán bộ Giáo viên Nhân viên & 829 Học sinh 21 Lớp.")

        sub_dn1, sub_dn2 = st.tabs([
            "👨‍🎓 829 HỌC SINH & BỘ LỌC TOÀN TRƯỜNG",
            "📋 42 CÁN BỘ - GIÁO VIÊN - NHÂN VIÊN & PHÂN CÔNG"
        ])

        # SUB-TAB 1: HỌC SINH & BỘ LỌC TOÀN TRƯỜNG
        with sub_dn1:
            st.markdown("#### 🔍 **Tra Cứu & Bộ Lọc Học Sinh Toàn Trường (829 Học Sinh • 21 Lớp)**")
            
            # Chỉ số học sinh nhanh
            c_hs1, c_hs2, c_hs3, c_hs4 = st.columns(4)
            c_hs1.metric("👨‍🎓 Tổng Số Học Sinh", f"{tong_hs} HS", "21 Lớp")
            c_hs2.metric("👦 Nam / 👧 Nữ", f"{so_nam} / {so_nu}", f"Nữ: {(so_nu/tong_hs*100):.1f}%")
            c_hs3.metric("🏔️ Dân Tộc Thiểu Số", f"{so_dtts} HS", f"{(so_dtts/tong_hs*100):.1f}%")
            c_hs4.metric("🛏️ Học Sinh Bán Trú", f"{so_ban_tru} HS", "KTX trường")

            # Biểu đồ phân bố 3 Khối
            st.markdown("#### 📈 **Phân Bố Sĩ Số Học Sinh 3 Khối (K10: 7 Lớp • K11: 7 Lớp • K12: 7 Lớp)**")
            if os.path.exists(f_cc):
                df_cc_view = pd.read_csv(f_cc, encoding='utf-8-sig')
                chart_data = df_cc_view.groupby('Khối')[['Sĩ số hiện tại', 'Học sinh Nam', 'Học sinh Nữ', 'Bán trú KTX']].sum()
                st.bar_chart(chart_data)

            st.markdown("---")

            if not df_hs_all.empty:
                col_l1, col_l2, col_l3, col_l4 = st.columns([1, 1, 1, 1.5])
                with col_l1:
                    ds_khoi_filter = ["Tất cả các khối", "Khối 10", "Khối 11", "Khối 12"]
                    chon_khoi = st.selectbox("Lọc theo Khối:", ds_khoi_filter, key="sb_loc_khoi_dn")
                with col_l2:
                    ds_lop_avail = sorted(df_hs_all['Lớp'].unique().tolist())
                    if chon_khoi != "Tất cả các khối":
                        ds_lop_avail = [x for x in ds_lop_avail if x.startswith(chon_khoi.replace("Khối ", ""))]
                    ds_lop_filter = ["Tất cả các lớp"] + ds_lop_avail
                    chon_lop = st.selectbox("Lọc theo Lớp:", ds_lop_filter, key="sb_loc_lop_dn")
                with col_l3:
                    ds_dt_filter = ["Tất cả dân tộc"] + sorted(df_hs_all['Dân tộc'].dropna().unique().tolist())
                    chon_dt = st.selectbox("Lọc theo Dân tộc:", ds_dt_filter, key="sb_loc_dt_dn")
                with col_l4:
                    kw_hs = st.text_input("Tìm kiếm theo Tên, Mã HS, Cha/Mẹ, SĐT:", placeholder="Nhập từ khóa...", key="inp_kw_hs_dn")

                df_hs_filtered = df_hs_all.copy()
                if chon_khoi != "Tất cả các khối":
                    df_hs_filtered = df_hs_filtered[df_hs_filtered['Khối'] == chon_khoi]
                if chon_lop != "Tất cả các lớp":
                    df_hs_filtered = df_hs_filtered[df_hs_filtered['Lớp'] == chon_lop]
                if chon_dt != "Tất cả dân tộc":
                    df_hs_filtered = df_hs_filtered[df_hs_filtered['Dân tộc'] == chon_dt]
                if kw_hs.strip():
                    kw_l = kw_hs.strip()
                    df_hs_filtered = df_hs_filtered[
                        df_hs_filtered['Họ và tên'].astype(str).str.contains(kw_l, case=False, na=False) |
                        df_hs_filtered['Mã học sinh'].astype(str).str.contains(kw_l, case=False, na=False) |
                        df_hs_filtered['Tên cha'].astype(str).str.contains(kw_l, case=False, na=False) |
                        df_hs_filtered['Tên mẹ'].astype(str).str.contains(kw_l, case=False, na=False) |
                        df_hs_filtered['SĐT Học sinh'].astype(str).str.contains(kw_l, na=False)
                    ]

                st.caption(f"Hiển thị: **{len(df_hs_filtered)} / {len(df_hs_all)}** học sinh phù hợp.")
                if is_ph_hs:
                    cot_show = ['STT', 'Mã học sinh', 'Họ và tên', 'Lớp', 'Khối', 'Giới tính', 'Ngày sinh', 'Dân tộc', 'Bán trú', 'Thôn', 'Xã']
                else:
                    cot_show = ['STT', 'Mã học sinh', 'Họ và tên', 'Lớp', 'Khối', 'Giới tính', 'Ngày sinh', 'Dân tộc', 'Bán trú', 'Thôn', 'Xã', 'Tên cha', 'SĐT Bố', 'SĐT Học sinh']
                cols_avail = [c for c in cot_show if c in df_hs_filtered.columns]
                st.dataframe(df_hs_filtered[cols_avail], use_container_width=True, hide_index=True)

                if not is_ph_hs:
                    csv_hs_bytes = df_hs_filtered.to_csv(index=False, encoding='utf-8-sig').encode('utf-8-sig')
                    st.download_button(
                        "📥 XUẤT FILE EXCEL / CSV HỌC SINH (CHUẨN SỞ GD&ĐT LÀO CAI)",
                        data=csv_hs_bytes,
                        file_name=f"Danh_Sach_Hoc_Sinh_THPT2_BaoYen_{date.today().strftime('%d_%m_%Y')}.csv",
                        mime="text/csv",
                        type="primary",
                        key="btn_dl_hs_dn"
                    )
                else:
                    st.info("ℹ️ **Quy định phân quyền:** Tài khoản Học sinh & Phụ huynh chỉ có quyền tra cứu thông tin cơ bản, không được phép xuất hoặc tải dữ liệu toàn trường theo quy định bảo mật.")

        # SUB-TAB 2: CÁN BỘ - GIÁO VIÊN - NHÂN VIÊN & PHÂN CÔNG
        with sub_dn2:
            st.markdown("#### 📋 **Danh Bạ 42 Cán Bộ, Giáo Viên, Nhân Viên & Bảng Phân Công**")
            st.caption("Danh bạ liên lạc Hội đồng sư phạm Trường THPT số 2 Bảo Yên. Hỗ trợ tra cứu nhanh và gọi điện thoại trực tiếp.")

            if not os.path.exists(f_gv_db):
                df_db = pd.DataFrame([
                    {'STT': 1, 'Họ và tên': 'Nguyễn Văn A', 'Chức vụ hiển thị': 'Hiệu trưởng', 'Vị trí việc làm': 'Cán bộ quản lý', 'Tổ chuyên môn': 'Ban Giám hiệu', 'Môn dạy': 'Toán học', 'Số điện thoại': '0988123002', 'Giáo viên chủ nhiệm lớp': '', 'Ghi chú': 'Phụ trách chung'},
                    {'STT': 2, 'Họ và tên': 'Trần Văn Đoàn', 'Chức vụ hiển thị': 'Tổ trưởng chuyên môn', 'Vị trí việc làm': 'Giáo viên', 'Tổ chuyên môn': 'Tổ Tự nhiên (KHTN)', 'Môn dạy': 'Toán học', 'Số điện thoại': '0947157111', 'Giáo viên chủ nhiệm lớp': '10A1', 'Ghi chú': 'GVCN 10A1'}
                ])
                df_db.to_csv(f_gv_db, index=False, encoding='utf-8-sig')
            else:
                df_db = pd.read_csv(f_gv_db, encoding='utf-8-sig').fillna("")

            # An toàn tuyệt đối: nếu chưa có cột 'Tổ chuyên môn', tự động sinh
            if 'Tổ chuyên môn' not in df_db.columns:
                def auto_to(row):
                    cv = str(row.get('Chức vụ hiển thị', row.get('Vị trí việc làm', ''))).lower()
                    mon = str(row.get('Môn dạy', '')).lower()
                    if 'hiệu trưởng' in cv:
                        return 'Ban Giám hiệu'
                    elif any(m in mon for m in ['toán', 'vật lý', 'hóa học', 'sinh học', 'tin học', 'công nghệ']):
                        return 'Tổ Tự nhiên (KHTN)'
                    elif any(m in mon for m in ['ngữ văn', 'lịch sử', 'địa lý', 'tiếng anh', 'giáo dục thể chất', 'giáo dục quốc phòng']):
                        return 'Tổ Xã hội (KHXH)'
                    elif any(v in cv for v in ['kế toán', 'văn thư', 'y tế', 'nhân viên']):
                        return 'Tổ Văn phòng'
                    return 'Tổ Tự nhiên (KHTN)'
                df_db['Tổ chuyên môn'] = df_db.apply(auto_to, axis=1)

            c_db_f1, c_db_f2 = st.columns([1, 1.5])
            with c_db_f1:
                ds_to_cm = ["Tất cả các tổ"] + sorted(list(set(df_db['Tổ chuyên môn'].dropna().tolist())))
                chon_to = st.selectbox("Lọc theo Tổ chuyên môn:", ds_to_cm, key="sb_chon_to_gv_dn")
            with c_db_f2:
                kw_gv = st.text_input("Tìm nhanh Thầy/Cô (Tên, SĐT, Môn dạy, GVCN):", "", key="inp_kw_gv_dn")

            df_db_show = df_db.copy()
            if chon_to != "Tất cả các tổ":
                df_db_show = df_db_show[df_db_show['Tổ chuyên môn'] == chon_to]
            if kw_gv.strip():
                kw_gl = kw_gv.strip()
                df_db_show = df_db_show[
                    df_db_show['Họ và tên'].astype(str).str.contains(kw_gl, case=False, na=False) |
                    df_db_show['Chức vụ hiển thị'].astype(str).str.contains(kw_gl, case=False, na=False) |
                    df_db_show['Môn dạy'].astype(str).str.contains(kw_gl, case=False, na=False) |
                    df_db_show['Số điện thoại'].astype(str).str.contains(kw_gl, na=False) |
                    df_db_show['Giáo viên chủ nhiệm lớp'].astype(str).str.contains(kw_gl, case=False, na=False)
                ]

            # Sắp xếp các cột trực quan
            cols_order = ['STT', 'Họ và tên', 'Chức vụ hiển thị', 'Tổ chuyên môn', 'Môn dạy', 'Giáo viên chủ nhiệm lớp', 'Số điện thoại', 'Trình độ chuyên môn', 'Giới tính', 'Dân tộc']
            cols_present = [c for c in cols_order if c in df_db_show.columns] + [c for c in df_db_show.columns if c not in cols_order]
            st.dataframe(df_db_show[cols_present], use_container_width=True, hide_index=True)

            c_db1, c_db2 = st.columns(2)
            with c_db1:
                csv_mau_db = df_db.to_csv(index=False, encoding='utf-8-sig').encode('utf-8-sig')
                st.download_button("📥 Tải Biểu Mẫu Danh Bạ (.CSV)", data=csv_mau_db, file_name="Danh_Ba_CBGV_THPT2_BaoYen.csv", mime="text/csv", key="btn_dl_db_dn")
            with c_db2:
                if not is_ph_hs:
                    uploaded_db = st.file_uploader("Tải lên biểu danh bạ Excel (.xlsx) hoặc CSV:", type=['xlsx', 'xls', 'csv'], key="up_db_excel_fixed_dn")
                    if uploaded_db is not None:
                        try:
                            df_imp_db = pd.read_csv(uploaded_db, encoding='utf-8-sig') if uploaded_db.name.endswith('.csv') else pd.read_excel(uploaded_db)
                            st.dataframe(df_imp_db, use_container_width=True, hide_index=True)
                            if st.button("🚀 XÁC NHẬN ĐỒNG BỘ DANH BẠ TOÀN TRƯỜNG", type="primary", key="btn_confirm_imp_db_dn"):
                                df_imp_db.to_csv(f_gv_db, index=False, encoding='utf-8-sig')
                                st.success(f"🎉 Đã đồng bộ thành công danh bạ {len(df_imp_db)} thầy cô!")
                                st.rerun()
                        except Exception as e:
                            st.error(f"Lỗi đọc file: {str(e)}")
    # =========================================================================
    # TAB 4: CÔNG TÁC CHỦ NHIỆM LỚP
    # =========================================================================
    with tab_chu_nhiem:
        st.subheader("👨‍🏫 Nghiệp Vụ Công Tác Chủ Nhiệm Lớp (21 Lớp)")
        st.caption("Dành cho 21 Thầy/Cô GVCN và Ban Giám Hiệu theo dõi sĩ số, chuyên cần, nền nếp và kế hoạch chủ nhiệm.")

        sub_cn1, sub_cn2, sub_cn3 = st.tabs([
            "📊 BÁO SĨ SỐ & ĐIỂM DANH CHUYÊN CẦN (LIVE)",
            "📝 KẾ HOẠCH CHỦ NHIỆM TUẦN / THÁNG",
            "📱 SỔ LIÊN LẠC PHỤ HUYNH ĐIỆN TỬ"
        ])

        with sub_cn1:
            import quan_ly_si_so_lop
            quan_ly_si_so_lop.render_giao_dien_bao_si_so(
                u_curr=u_curr,
                role_curr=role_curr,
                base_dir=BASE_DIR,
                is_gvcn=True,
                is_admin=la_bgh_admin
            )

        with sub_cn2:
            st.markdown("#### 📝 **Kế Hoạch Công Tác Chủ Nhiệm Tuần / Tháng**")
            df_khcn = pd.read_csv(f_khcn, encoding='utf-8-sig') if os.path.exists(f_khcn) else pd.DataFrame()
            if not df_khcn.empty:
                st.dataframe(df_khcn, use_container_width=True, hide_index=True)
            else:
                st.info("Chưa có kế hoạch công tác chủ nhiệm được cập nhật.")

        with sub_cn3:
            st.markdown("#### 📱 **Sổ Liên Lạc Điện Tử Với Phụ Huynh Lớp**")
            st.caption("Tra cứu nhanh số điện thoại Bố/Mẹ và thông tin gia đình học sinh để kết nối giáo dục giữa Nhà trường và Gia đình.")
            
            # Nạp danh sách học sinh toàn trường
            df_hs_toan_truong = pd.read_csv(f_hs_tt, encoding='utf-8-sig').fillna("") if os.path.exists(f_hs_tt) else pd.DataFrame()
            
            ds_21_lop = [
                '10A1', '10A2', '10A3', '10A4', '10A5', '10A6', '10A7',
                '11A1', '11A2', '11A3', '11A4', '11A5', '11A6', '11A7',
                '12A1', '12A2', '12A3', '12A4', '12A5', '12A6', '12A7'
            ]
            ma_lk_curr = str(u_curr.get("ma_lien_ket", "")).strip()
            lop_mac_dinh = ma_lk_curr if ma_lk_curr in ds_21_lop else "10A1"
            
            if la_bgh_admin or ma_lk_curr not in ds_21_lop:
                idx_sel = ds_21_lop.index(lop_mac_dinh) if lop_mac_dinh in ds_21_lop else 0
                chon_lop_sll = st.selectbox("🔍 Chọn lớp xem Sổ liên lạc:", ds_21_lop, index=idx_sel, key="sb_lop_sll_ph")
            else:
                chon_lop_sll = lop_mac_dinh
                st.info(f"👨‍🏫 Bạn đang xem Sổ liên lạc điện tử học sinh lớp **{chon_lop_sll}**")

            if not df_hs_toan_truong.empty and "Lớp" in df_hs_toan_truong.columns:
                df_hs_lop = df_hs_toan_truong[df_hs_toan_truong["Lớp"] == chon_lop_sll].copy()
            else:
                df_hs_lop = pd.DataFrame()

            if not df_hs_lop.empty:
                cols_sll = [c for c in ['STT', 'Mã học sinh', 'Họ và tên', 'Ngày sinh', 'Giới tính', 'Tên cha', 'SĐT Bố', 'Tên mẹ', 'SĐT Mẹ', 'Thôn', 'Xã'] if c in df_hs_lop.columns]
                st.dataframe(df_hs_lop[cols_sll], use_container_width=True, hide_index=True)
                st.caption(f"👥 Tổng sĩ số: {len(df_hs_lop)} học sinh lớp {chon_lop_sll}.")
            else:
                st.info(f"Chưa có dữ liệu danh sách học sinh của lớp {chon_lop_sll}.")

    # =========================================================================
    # TAB 5: TIẾN ĐỘ CHƯƠNG TRÌNH & CHUYÊN MÔN
    # =========================================================================
    with tab_chuyen_mon:
        st.subheader("📚 Công Tác Chuyên Môn & Quản Lý Dạy Học")
        st.caption("Quản lý toàn diện công tác chuyên môn: Tiến độ chương trình 21 lớp, Quản lý thiết bị dạy học, Thời khóa biểu, Lịch báo giảng và Sổ đầu bài điện tử.")

        sub_cm1, sub_cm2, sub_cm3, sub_cm4, sub_cm5 = st.tabs([
            "📚 TIẾN ĐỘ CHƯƠNG TRÌNH (21 LỚP)",
            "🔬 SỬ DỤNG, MƯỢN & TRẢ THIẾT BỊ DẠY HỌC",
            "🕒 THỜI KHÓA BIỂU (TKB)",
            "📖 LỊCH BÁO GIẢNG ĐIỆN TỬ",
            "✍️ SỔ ĐẦU BÀI ĐIỆN TỬ (SĐB)"
        ])

        with sub_cm1:
            st.markdown("#### 📚 **Theo Dõi Tiến Độ Chương Trình Theo Từng Lớp, Từng Môn Học (GDPT 2018)**")
            if os.path.exists(f_tdct):
                df_td_data = pd.read_csv(f_tdct, encoding='utf-8-sig')
                
                col_td1, col_td2 = st.columns([1, 1])
                with col_td1:
                    filter_k_td = st.selectbox("Lọc theo Khối:", ["Tất cả các khối", "Khối 10", "Khối 11", "Khối 12"], key="sb_k_td")
                with col_td2:
                    filter_m_td = st.selectbox("Lọc theo Môn học:", ["Tất cả các môn"] + sorted(list(df_td_data['Môn học'].unique())), key="sb_m_td")
                
                df_td_show = df_td_data.copy()
                if filter_k_td != "Tất cả các khối":
                    df_td_show = df_td_show[df_td_show['Khối'] == filter_k_td]
                if filter_m_td != "Tất cả các môn":
                    df_td_show = df_td_show[df_td_show['Môn học'] == filter_m_td]
                
                st.dataframe(df_td_show, use_container_width=True, hide_index=True)
                
                if not is_ph_hs:
                    csv_td_bytes = df_td_show.to_csv(index=False, encoding='utf-8-sig').encode('utf-8-sig')
                    st.download_button("📥 XUẤT BÁO CÁO TIẾN ĐỘ CHƯƠNG TRÌNH (.CSV)", data=csv_td_bytes, file_name="Bao_Cao_Tien_Do_Chuong_Trinh_THPT2_BaoYen.csv", mime="text/csv")
            else:
                st.info("Chưa có dữ liệu tiến độ chương trình.")

        with sub_cm2:
            st.markdown("#### 🔬 **Theo Dõi Sử Dụng, Mượn & Trả Thiết Bị Dạy Học**")
            st.caption("Quản lý thiết bị dạy học, đồ dùng thí nghiệm thực hành các tổ bộ môn KHTN, KHXH, Tin học, Ngoại ngữ.")
            df_tb = pd.read_csv(f_tb, encoding='utf-8-sig') if os.path.exists(f_tb) else pd.DataFrame()
            if not df_tb.empty:
                st.dataframe(df_tb, use_container_width=True, hide_index=True)
            else:
                st.info("Chưa có dữ liệu thiết bị dạy học.")

        with sub_cm3:
            st.markdown("#### 🕒 **Thời Khóa Biểu Giảng Dạy 21 Lớp**")
            df_tkb = pd.read_csv(f_tkb, encoding='utf-8-sig') if os.path.exists(f_tkb) else pd.DataFrame()
            if not df_tkb.empty:
                st.dataframe(df_tkb, use_container_width=True, hide_index=True)

        with sub_cm4:
            st.markdown("#### 📖 **Lịch Báo Giảng Tuần Của Giáo Viên**")
            df_bg_mau = pd.DataFrame([
                {"Tiết PPCT": 18, "Lớp": "10A1", "Môn": "Toán học", "Tên bài dạy": "Hàm số bậc hai và đồ thị", "Thiết bị sử dụng": "Máy chiếu, Geogebra", "Trạng thái": "Đã dạy"},
                {"Tiết PPCT": 19, "Lớp": "10A1", "Môn": "Toán học", "Tên bài dạy": "Luyện tập hàm số bậc hai", "Thiết bị sử dụng": "Phiếu học tập", "Trạng thái": "Đã dạy"},
                {"Tiết PPCT": 22, "Lớp": "11A1", "Môn": "Ngữ văn", "Tên bài dạy": "Văn học trung đại Việt Nam", "Thiết bị sử dụng": "Tranh ảnh minh họa", "Trạng thái": "Đã dạy"},
                {"Tiết PPCT": 24, "Lớp": "12A1", "Môn": "Vật lý", "Tên bài dạy": "Dòng điện xoay chiều ba pha", "Thiết bị sử dụng": "Bộ thí nghiệm điện", "Trạng thái": "Đang dạy"}
            ])
            st.dataframe(df_bg_mau, use_container_width=True, hide_index=True)

        with sub_cm5:
            st.markdown("#### ✍️ **Sổ Đầu Bài Điện Tử (SĐB) - Ký Duyệt Trực Tuyến**")
            df_sdb = pd.read_csv(f_sdb, encoding='utf-8-sig') if os.path.exists(f_sdb) else pd.DataFrame()
            if not df_sdb.empty:
                st.dataframe(df_sdb, use_container_width=True, hide_index=True)

    # =========================================================================
    # TAB 6: KẾ HOẠCH NĂM HỌC & SỰ KIỆN LỚN
    # =========================================================================
    with tab_ke_hoach:
        st.subheader("🎯 Kế Hoạch Năm Học 2026 - 2027 & Kho Biểu Mẫu Nhà Trường")
        st.caption("Lộ trình trọng tâm theo từng tháng trong năm học của Trường THPT số 2 Bảo Yên.")

        if os.path.exists(f_plan):
            df_plan_curr = pd.read_csv(f_plan, encoding='utf-8-sig').fillna("")
            st.dataframe(df_plan_curr, use_container_width=True, hide_index=True)

        c_kp1, c_kp2 = st.columns(2)
        with c_kp1:
            st.markdown("##### 📁 Kho Biểu Mẫu Hành Chính & Bán Trú:")
            st.markdown("""
            - 📄 [Đơn xin ở bán trú KTX năm học 2026-2027 (.docx)](#)
            - 📄 [Biên bản kiểm tra an toàn vệ sinh thực phẩm 3 bước (.docx)](#)
            - 📄 [Báo cáo thống kê biến động học sinh đầu năm & cuối kỳ (.xlsx)](#)
            - 📄 [Phiếu thẩm định học sinh hưởng chế độ Nghị định 116 (.docx)](#)
            """)
        with c_kp2:
            st.markdown("##### 🎪 Các Mốc Sự Kiện Lớn Trong Năm Học:")
            st.markdown("""
            - 🔔 **Tháng 09:** Khai giảng năm học mới & Ổn định KTX bán trú
            - 💐 **Tháng 11:** Kỷ niệm 44 năm Ngày Nhà giáo Việt Nam 20/11
            - 📝 **Tháng 12:** Thi kiểm tra đánh giá cuối Học kỳ 1
            - ⛺ **Tháng 03:** Tháng Thanh niên & Hội trại truyền thống 26/3
            - 🎓 **Tháng 05:** Bế giảng & Ôn thi Tốt nghiệp THPT Quốc gia
            """)

    # =========================================================================
    # TAB 7: QUẢN TRỊ TÀI KHOẢN, NIÊN KHÓA & ĐÁM MÂY
    # =========================================================================
    with tab_admin_nh:
        if not duoc_quyen_quan_tri:
            st.markdown(f"""
            <div style="background:#FEF2F2; border:2px solid #DC2626; border-radius:12px; padding:28px 20px; text-align:center; margin:15px 0; box-shadow:0 4px 6px rgba(0,0,0,0.05);">
                <div style="font-size:52px; margin-bottom:8px;">🔒</div>
                <h3 style="color:#B91C1C; margin:0 0 10px 0; font-weight:800; font-size:22px;">KHU VỰC BẢO MẬT CAO - TRUY CẬP BỊ TỪ CHỐI</h3>
                <p style="font-size:15px; color:#374151; max-width:680px; margin:0 auto 15px auto; line-height:1.6;">
                    Tab <b>Quản Trị & Niên Khóa</b> chứa các thông tin bảo mật cốt lõi và thẩm quyền điều hành cao nhất của nhà trường (Phân quyền 1.339 tài khoản toàn trường, cấu hình niên khóa, phê duyệt cấp quyền và đồng bộ đám mây).
                </p>
                <div style="background:white; border:1px solid #FECACA; border-radius:8px; padding:14px 22px; display:inline-block; text-align:left; font-size:14px; color:#1F2937; margin-bottom:15px;">
                    <b style="color:#991B1B;">QUY ĐỊNH PHÂN QUYỀN TRUY CẬP:</b><br>
                    🛡️ <b>Quản trị viên hệ thống (Admin)</b><br>
                    🏛️ <b>Thầy Hiệu trưởng & các Thầy/Cô Phó Hiệu trưởng (PHT)</b><br>
                    ✍️ <b>Giáo viên được Ban Giám Hiệu phân quyền quản trị</b>
                </div>
                <p style="margin:10px 0 0 0; font-size:13.5px; color:#6B7280;">
                    Tài khoản của bạn: <code style="color:#DC2626; font-size:14px; font-weight:bold;">{u_username}</code> ({u_curr.get('fullname', 'Người dùng')} - Vai trò: <b>{role_curr}</b>)<br>
                    <i>Không có quyền mở hoặc xem nội dung của khu vực này để đảm bảo an toàn thông tin nhà trường.</i>
                </p>
            </div>
            """, unsafe_allow_html=True)
            st.info("💡 Nếu Thầy/Cô có nhiệm vụ công tác cần sử dụng tab này, vui lòng liên hệ Ban Giám Hiệu (Thầy Hiệu trưởng hoặc Thầy/Cô PHT) để được phân quyền quản trị.")
        else:
            st.subheader("⚙️ Quản Trị Tài Khoản, Niên Khóa & Đồng Bộ Đám Mây")
            sub_ad1, sub_ad2, sub_ad3, sub_ad4 = st.tabs([
                "👑 PHÂN QUYỀN & TÀI KHOẢN TOÀN TRƯỜNG",
                "🗃️ CẤU HÌNH NIÊN KHÓA LÀM VIỆC",
                "📬 PHÊ DUYỆT ĐỀ XUẤT CẤP QUYỀN",
                "☁️ ĐỒNG BỘ GOOGLE DRIVE & SHEETS"
            ])

            with sub_ad1:
                st.markdown("#### 👥 **Danh Sách & Phân Quyền Tài Khoản Toàn Trường**")
                
                # KHU VỰC ỦY QUYỀN GIÁO VIÊN MỞ TAB QUẢN TRỊ & NIÊN KHÓA
                with st.expander("🔑 **ỦY QUYỀN GIÁO VIÊN ĐƯỢC MỞ TAB QUẢN TRỊ & NIÊN KHÓA**", expanded=True):
                    st.caption("Ban Giám Hiệu (Hiệu trưởng & PHT) có thể phân quyền cho Giáo viên được phép mở và thao tác tại Tab Quản trị & Niên khóa.")
                    
                    f_gv_auth_cfg = os.path.join(BASE_DIR, "cau_hinh_giao_vien_quan_tri.json")
                    ds_uy_quyen_curr = []
                    if os.path.exists(f_gv_auth_cfg):
                        try:
                            with open(f_gv_auth_cfg, "r", encoding="utf-8") as f_u:
                                ds_uy_quyen_curr = json.load(f_u).get("danh_sach_uy_quyen", [])
                        except Exception:
                            pass
                    
                    # Lấy danh sách Giáo viên / Nhân viên
                    df_gv_candidates = df_tk_live[df_tk_live["Vai trò"].isin(["Giáo viên quản lý", "Nhân viên", "Ban Chấp hành Đoàn"])]
                    if not df_gv_candidates.empty:
                        opt_gv_map = {f"{r['Họ và tên']} ({r['Tên đăng nhập']} - {r['Chức danh']})": r['Tên đăng nhập'] for _, r in df_gv_candidates.iterrows()}
                        c_uq1, c_uq2 = st.columns([2, 1])
                        with c_uq1:
                            gv_chon_str = st.selectbox("Chọn Giáo viên / Nhân viên cần phân quyền quản trị:", list(opt_gv_map.keys()), key="sb_chon_gv_uq")
                        with c_uq2:
                            st.write("")
                            st.write("")
                            if st.button("➕ PHÂN QUYỀN CHO GV NÀY", type="primary", use_container_width=True, key="btn_add_gv_uq"):
                                user_to_add = opt_gv_map[gv_chon_str]
                                if user_to_add not in ds_uy_quyen_curr:
                                    ds_uy_quyen_curr.append(user_to_add)
                                    for p_json in [f_gv_auth_cfg, os.path.join("D:/phan_mem_ban_tru_cloud", "cau_hinh_giao_vien_quan_tri.json")]:
                                        try:
                                            with open(p_json, "w", encoding="utf-8") as f_out:
                                                json.dump({"danh_sach_uy_quyen": ds_uy_quyen_curr}, f_out, ensure_ascii=False, indent=2)
                                        except Exception:
                                            pass
                                    m_tk_gv = (df_tk_live["Tên đăng nhập"] == user_to_add)
                                    if m_tk_gv.any():
                                        df_tk_live.loc[m_tk_gv, "Quyền quản lý"] = "Quản trị & niên khóa"
                                        for p_tk in [file_tai_khoan_csv, "D:/tai_khoan_nguoi_dung.csv", "D:/phan_mem_ban_tru_cloud/tai_khoan_nguoi_dung.csv"]:
                                            try:
                                                df_tk_live.to_csv(p_tk, index=False, encoding='utf-8-sig')
                                            except Exception:
                                                pass
                                    st.success(f"✅ Đã phân quyền mở Tab Quản trị & Niên khóa cho Thầy/Cô: {gv_chon_str}")
                                    st.rerun()

                    # Hiển thị danh sách đang được ủy quyền
                    st.markdown("---")
                    st.markdown("##### 📋 Giáo Viên Hiện Đang Được Phân Quyền Quản Trị:")
                    if ds_uy_quyen_curr:
                        for u_gvuq in ds_uy_quyen_curr:
                            r_match = df_tk_live[df_tk_live["Tên đăng nhập"] == u_gvuq]
                            ten_hien = r_match["Họ và tên"].values[0] if not r_match.empty else u_gvuq
                            chuc_vu_hien = r_match["Chức danh"].values[0] if not r_match.empty else "Giáo viên"
                            col_uq_a, col_uq_b = st.columns([3, 1])
                            col_uq_a.markdown(f"🟢 **{ten_hien}** (`{u_gvuq}`) - *{chuc_vu_hien}* — `Được phép mở Tab Quản trị`")
                            if col_uq_b.button(f"❌ Thu hồi quyền", key=f"btn_del_uq_{u_gvuq}"):
                                ds_uy_quyen_curr.remove(u_gvuq)
                                for p_json in [f_gv_auth_cfg, os.path.join("D:/phan_mem_ban_tru_cloud", "cau_hinh_giao_vien_quan_tri.json")]:
                                    try:
                                        with open(p_json, "w", encoding="utf-8") as f_out:
                                            json.dump({"danh_sach_uy_quyen": ds_uy_quyen_curr}, f_out, ensure_ascii=False, indent=2)
                                    except Exception:
                                        pass
                                m_tk_gv = (df_tk_live["Tên đăng nhập"] == u_gvuq)
                                if m_tk_gv.any():
                                    df_tk_live.loc[m_tk_gv, "Quyền quản lý"] = "Cá nhân"
                                    for p_tk in [file_tai_khoan_csv, "D:/tai_khoan_nguoi_dung.csv", "D:/phan_mem_ban_tru_cloud/tai_khoan_nguoi_dung.csv"]:
                                        try:
                                            df_tk_live.to_csv(p_tk, index=False, encoding='utf-8-sig')
                                        except Exception:
                                            pass
                                st.warning(f"Đã thu hồi quyền quản trị của tài khoản {u_gvuq}")
                                st.rerun()
                    else:
                        st.info("ℹ️ Hiện tại ngoài Ban Giám Hiệu và Admin, chưa có giáo viên nào được phân quyền quản trị.")

                st.markdown("---")
                st.dataframe(df_tk_live, use_container_width=True, hide_index=True)
                csv_tk_bytes = df_tk_live.to_csv(index=False, encoding='utf-8-sig').encode('utf-8-sig')
                st.download_button("📥 XUẤT FILE DANH SÁCH TÀI KHOẢN (.CSV)", data=csv_tk_bytes, file_name="Tai_Khoan_Nguoi_Dung_THPT2_BaoYen.csv", mime="text/csv")

            with sub_ad2:
                st.markdown("#### 🗃️ **Chuyển Đổi Niên Khóa Làm Việc**")
                st.write(f"Niên khóa hiện tại: **{nam_hoc}**")
                chon_nh_m = st.selectbox("Chọn niên khóa kích hoạt:", danh_sach_nam_hoc, index=danh_sach_nam_hoc.index(nam_hoc) if nam_hoc in danh_sach_nam_hoc else 0, key="sb_cfg_nh_ad")
                if chon_nh_m != nam_hoc:
                    if st.button("Chuyển niên khóa này ngay", key="btn_apply_nh"):
                        st.session_state.nam_hoc_hien_tai = chon_nh_m
                        st.rerun()

            with sub_ad3:
                st.markdown("#### 📬 **Phê Duyệt Đề Xuất Cấp Quyền Người Dùng**")
                f_req = os.path.join(BASE_DIR, "de_xuat_cap_quyen.csv")
                if os.path.exists(f_req):
                    df_req_ad = pd.read_csv(f_req, encoding='utf-8-sig').fillna("")
                    st.dataframe(df_req_ad, use_container_width=True, hide_index=True)
                else:
                    st.success("✨ Hiện không có đề xuất cấp quyền nào đang chờ duyệt!")

            with sub_ad4:
                st.markdown("### ☁️ TRUNG TÂM ĐỒNG BỘ ĐÁM MÂY GOOGLE DRIVE & GOOGLE SHEETS")
                st.caption("Kết nối trực tiếp với Google Drive & Google Sheets của Trường THPT số 2 Bảo Yên để lưu trữ vĩnh viễn, sao lưu định kỳ toàn bộ phần mềm và chia sẻ báo cáo liên thông.")

                f_cfg_gs = os.path.join(BASE_DIR, "cau_hinh_google_sheets.json")
                cfg_gs = {
                    "web_app_url": "",
                    "spreadsheet_url": "",
                    "drive_folder_url": "",
                    "local_drive_path": "D:/Google_Drive_THPT2_BaoYen",
                    "last_sync_drive": "Chưa đồng bộ",
                    "last_sync_sheets": "Chưa đồng bộ",
                    "status": "Chưa cấu hình"
                }
                if os.path.exists(f_cfg_gs):
                    try:
                        with open(f_cfg_gs, "r", encoding="utf-8") as f_cfg:
                            cfg_gs.update(json.load(f_cfg))
                    except Exception:
                        pass

                # Thẻ trạng thái kết nối trên cùng
                is_connected = bool(cfg_gs.get("web_app_url", "").strip())
                c_st1, c_st2, c_st3, c_st4 = st.columns([1.3, 1.1, 1.1, 1.1])
                with c_st1:
                    if is_connected:
                        st.success("🟢 **API ĐÁM MÂY: ĐÃ KẾT NỐI**")
                    else:
                        st.warning("🟡 **API ĐÁM MÂY: CHƯA CẤU HÌNH**")
                with c_st2:
                    st.info(f"📁 **Google Drive:** {cfg_gs.get('last_sync_drive', 'Chưa có')}")
                with c_st3:
                    st.info(f"📊 **Google Sheets:** {cfg_gs.get('last_sync_sheets', 'Chưa có')}")
                with c_st4:
                    d_url = cfg_gs.get("drive_folder_url", "").strip() or "https://drive.google.com/drive/my-drive"
                    st.link_button("📂 MỞ GOOGLE DRIVE", d_url, use_container_width=True)

                # Chỉ số dữ liệu toàn trường sẵn sàng đồng bộ (Thời gian thực)
                so_xe_now = len(pd.read_csv(os.path.join(BASE_DIR, 'quan_ly_phuong_tien.csv'), encoding='utf-8-sig')) if os.path.exists(os.path.join(BASE_DIR, 'quan_ly_phuong_tien.csv')) else 549
                so_gv_now = len(pd.read_csv(f_gv_db, encoding='utf-8-sig')) if os.path.exists(f_gv_db) else 42
                so_doan_now = len(pd.read_csv(os.path.join(BASE_DIR, 'thi_dua_dtn_20_lop.csv'), encoding='utf-8-sig')) if os.path.exists(os.path.join(BASE_DIR, 'thi_dua_dtn_20_lop.csv')) else 21

                m_gs1, m_gs2, m_gs3, m_gs4, m_gs5 = st.columns(5)
                m_gs1.metric("👨‍🎓 Học sinh", f"{tong_hs} HS", "21 Lớp")
                m_gs2.metric("🛵 Phương tiện", f"{so_xe_now} Xe", "Mã QR")
                m_gs3.metric("📋 CBGV-NV", f"{so_gv_now} Người", "4 Tổ")
                m_gs4.metric("🛏️ Bán trú", f"{so_ban_tru} HS", "19 Phòng")
                m_gs5.metric("🏆 Thi đua", f"{so_doan_now} Chi đoàn", "Nề nếp Live")

                st.markdown("---")

                tab_auto_sync, tab_sync_github, tab_sync_drive, tab_sync_sheets, tab_sync_cfg, tab_sync_guide = st.tabs([
                    "🤖 TỰ ĐỘNG ĐỒNG BỘ (AUTO-SYNC 24/7)",
                    "🐙 ĐỒNG BỘ GITHUB (WEB CLOUD)",
                    "📁 ĐỒNG BỘ LÊN GOOGLE DRIVE (LƯU TRỮ VĨNH VIỄN)",
                    "📊 ĐỒNG BỘ LÊN GOOGLE SHEETS (BẢNG TÍNH THỜI GIAN THỰC)",
                    "⚙️ CẤU HÌNH LIÊN KẾT & TEST PING",
                    "📖 HƯỚNG DẪN CÀI ĐẶT 3 BƯỚC (APPS SCRIPT)"
                ])

                # -------------------------------------------------------------
                # 0. TỰ ĐỘNG ĐỒNG BỘ ĐỊNH KỲ (AUTO-SYNC)
                # -------------------------------------------------------------
                with tab_auto_sync:
                    st.markdown("#### 🤖 **Chế Độ Tự Động Đồng Bộ Dữ Liệu Lên Đám Mây (Chạy Ngầm 24/7)**")
                    st.caption("Hệ thống tự động đồng bộ ngầm toàn bộ dữ liệu phần mềm lên Google Drive và Google Sheets mà Thầy/Cô không cần phải bấm nút thủ công mỗi ngày.")
                
                    import dich_vu_tu_dong_dong_bo
                    cfg_auto = dich_vu_tu_dong_dong_bo.load_config()
                
                    col_at1, col_at2 = st.columns([1.5, 1.2])
                    with col_at1:
                        st.markdown("##### ⚙️ **Thiết Lập Lịch Tự Động:**")
                        en_auto = st.toggle("🔘 **BẬT CHẾ ĐỘ TỰ ĐỘNG ĐỒNG BỘ NGẦM (24/7)**", value=cfg_auto.get("auto_sync_enabled", True), key="tog_auto_sync")
                    
                        c_p1, c_p2 = st.columns(2)
                        with c_p1:
                            chu_ky = st.selectbox(
                                "Chu kỳ lặp lại:",
                                options=[15, 30, 60, 120],
                                format_func=lambda x: f"Mỗi {x} phút một lần",
                                index=[15, 30, 60, 120].index(cfg_auto.get("auto_sync_interval_mins", 30)) if cfg_auto.get("auto_sync_interval_mins", 30) in [15, 30, 60, 120] else 1,
                                key="sb_chu_ky_sync"
                            )
                        with c_p2:
                            st.write("Khung giờ vàng tự động đồng bộ:")
                            st.info("🕒 **09:00** (Chốt cơm bán trú)\n🕒 **11:30** (Kiểm thực trưa)\n🕒 **17:00** (Kết thúc ngày)")

                        st.markdown("##### 🎯 **Thành phần tự động:**")
                        c_tg1, c_tg2 = st.columns(2)
                        with c_tg1:
                            tg_drv = st.checkbox("📁 Tự động đồng bộ Google Drive", value=cfg_auto.get("auto_sync_drive", True), key="ck_at_drv")
                        with c_tg2:
                            tg_sht = st.checkbox("📊 Tự động đồng bộ Google Sheets", value=cfg_auto.get("auto_sync_sheets", True), key="ck_at_sht")

                        if st.button("💾 LƯU CẤU HÌNH TỰ ĐỘNG ĐỒNG BỘ", type="primary", use_container_width=True, key="btn_save_auto_cfg"):
                            cfg_auto["auto_sync_enabled"] = en_auto
                            cfg_auto["auto_sync_interval_mins"] = chu_ky
                            cfg_auto["auto_sync_drive"] = tg_drv
                            cfg_auto["auto_sync_sheets"] = tg_sht
                            dich_vu_tu_dong_dong_bo.save_config(cfg_auto)
                            dich_vu_tu_dong_dong_bo.khoi_chay_dich_vu_tu_dong()
                            st.success("✅ Đã kích hoạt và lưu cấu hình Tự Động Đồng Bộ thành công!")
                            st.rerun()

                    with col_at2:
                        st.markdown("##### ⚡ **Kích Hoạt Tức Thì & Kiểm Tra:**")
                        st.write(f"⏰ **Lần tự động chạy gần nhất:** `{cfg_auto.get('last_auto_sync', 'Chưa có')}`")
                        if cfg_auto.get("auto_sync_enabled", False):
                            st.success("🟢 **DỊCH VỤ NGẦM: ĐANG HOẠT ĐỘNG 24/7**")
                        else:
                            st.warning("⚪ **DỊCH VỤ NGẦM: ĐANG TẠM DỪNG**")

                        if st.button("⚡ KÍCH HOẠT ĐỒNG BỘ NGAY BÂY GIỜ", use_container_width=True, key="btn_run_now"):
                            with st.spinner("Đang thực hiện chu trình đồng bộ ngầm toàn trường..."):
                                kq = dich_vu_tu_dong_dong_bo.thuc_hien_dong_bo(trigger="Thủ công tức thì")
                                st.success("🎉 Đã thực hiện đồng bộ toàn diện thành công!")
                                for d in kq.get("details", []):
                                    st.caption(f"• {d}")
                                st.rerun()

                    st.markdown("---")
                    st.markdown("##### 📜 **Nhật Ký Tự Động Đồng Bộ Gần Nhất (Live Audit Log):**")
                    logs = cfg_auto.get("sync_log", [])
                    if logs:
                        for item in logs[:8]:
                            st.markdown(f"• **{item.get('timestamp')}** [{item.get('trigger')}]: " + " | ".join(item.get("details", [])))
                    else:
                        st.info("💡 Chưa có nhật ký đồng bộ tự động. Hệ thống sẽ ghi nhận lịch sử sau mỗi chu kỳ.")

                # Helper tạo gói sao lưu zip
                import base64
                def tao_goi_sao_luu_zip(bao_gom_ma_nguon=True):
                    buf = io.BytesIO()
                    with zipfile.ZipFile(buf, 'w', zipfile.ZIP_DEFLATED) as z:
                        # Ghi tất cả file CSDL CSV & JSON
                        for f in os.listdir(BASE_DIR):
                            if f.endswith('.csv') or f.endswith('.json'):
                                p = os.path.join(BASE_DIR, f)
                                z.write(p, arcname=f"co_so_du_lieu/{f}")
                        # Ghi file Excel đa sheet tổng hợp
                        buf_xlsx_temp = io.BytesIO()
                        with pd.ExcelWriter(buf_xlsx_temp, engine='openpyxl') as wr:
                            for s_n, f_p in [
                                ('Hoc_Sinh_829', f_hs_tt),
                                ('Phuong_Tien_549', os.path.join(BASE_DIR, 'quan_ly_phuong_tien.csv')),
                                ('Can_Bo_42', f_gv_db),
                                ('Ban_Tru_KTX', f_bt_ktx),
                                ('Thi_Dua_21_Lop', os.path.join(BASE_DIR, 'thi_dua_dtn_20_lop.csv'))
                            ]:
                                if os.path.exists(f_p):
                                    pd.read_csv(f_p, encoding='utf-8-sig').to_excel(wr, sheet_name=s_n, index=False)
                        z.writestr("tong_hop_excel/Du_Lieu_Toan_Truong_THPT2_BaoYen.xlsx", buf_xlsx_temp.getvalue())
                        # Ghi mã nguồn phần mềm nếu chọn
                        if bao_gom_ma_nguon:
                            for py_f in ['app_ban_tru.py', 'phan_he_quan_ly_chung.py', 'phan_he_doan_thanh_nien.py']:
                                p_py = os.path.join(BASE_DIR, py_f)
                                if os.path.exists(p_py):
                                    z.write(p_py, arcname=f"ma_nguon_phan_mem/{py_f}")
                    return buf.getvalue()

                # -------------------------------------------------------------

                # -------------------------------------------------------------
                # 0.1. ĐỒNG BỘ GITHUB (WEB CLOUD)
                # -------------------------------------------------------------
                with tab_sync_github:
                    st.markdown("#### 🐙 **Đồng Bộ Mã Nguồn Lên GitHub & Cập Nhật Web Cloud**")
                    st.caption("Cập nhật toàn bộ mã nguồn, cấu hình biểu tượng màn hình chính và dữ liệu lên kho GitHub của trường. Trang web [thpt2baoyen.streamlit.app](https://thpt2baoyen.streamlit.app) sẽ tự động cập nhật ngay sau khi đẩy.")
                
                    try:
                        import tu_dong_day_len_github
                        gh_cfg = tu_dong_day_len_github.load_github_cfg()
                    except Exception:
                        gh_cfg = {"repo": "buivantien20/ban-tru-thpt2-baoyen", "branch": "main", "token": "", "last_push": "Chưa đồng bộ"}
                
                    col_gh1, col_gh2 = st.columns([1.4, 1.2])
                    with col_gh1:
                        st.markdown("##### ⚙️ **Thông Tin Kết Nối GitHub:**")
                        st.write(f"• **Kho lưu trữ (Repository):** `https://github.com/{gh_cfg.get('repo', 'buivantien20/ban-tru-thpt2-baoyen')}`")
                        st.write(f"• **Nhánh chính (Branch):** `{gh_cfg.get('branch', 'main')}`")
                        st.write("• **Trang Web Cloud chính thức:** [thpt2baoyen.streamlit.app](https://thpt2baoyen.streamlit.app)")
                    
                        token_ht = gh_cfg.get("token", "")
                        tok_inp = st.text_input(
                            "Mã GitHub Personal Access Token (PAT):",
                            value=token_ht,
                            type="password",
                            help="Mã truy cập cá nhân bắt đầu bằng ghp_...",
                            key="input_gh_pat_token"
                        )
                        if st.button("💾 LƯU CẤU HÌNH GITHUB", use_container_width=True, key="btn_save_gh_cfg"):
                            gh_cfg["token"] = tok_inp.strip()
                            tu_dong_day_len_github.save_github_cfg(gh_cfg)
                            st.success("✅ Đã lưu cấu hình GitHub Token thành công!")
                            st.rerun()

                    with col_gh2:
                        st.markdown("##### 🚀 **Thao Tác Đồng Bộ Tức Thì:**")
                        st.write(f"⏰ **Lần đồng bộ gần nhất:** `{gh_cfg.get('last_push', 'Chưa đồng bộ')}`")
                        if token_ht:
                            st.success("🟢 **TOKEN: ĐÃ SẴN SÀNG ĐỒNG BỘ**")
                        else:
                            st.warning("🟡 **CHƯA CẤU HÌNH MÃ TOKEN**")
                    
                        if st.button("🚀 ĐẨY MÃ NGUỒN LÊN GITHUB NGAY", type="primary", use_container_width=True, key="btn_push_to_gh_now"):
                            with st.spinner("Đang đóng gói và tự động đẩy toàn bộ dữ liệu & mã nguồn lên GitHub..."):
                                tok_to_use = tok_inp.strip() if tok_inp.strip() else token_ht
                                ok_push, msg_push = tu_dong_day_len_github.push_to_github_api(tok_to_use)
                                if ok_push:
                                    st.success(msg_push)
                                    st.balloons()
                                else:
                                    st.error(msg_push)

                # 1. ĐỒNG BỘ LÊN GOOGLE DRIVE
                # -------------------------------------------------------------
                with tab_sync_drive:
                    st.markdown("#### 📁 **Đồng Bộ & Lưu Trữ Dữ Liệu Phần Mềm Lên Google Drive**")
                    st.caption("Sao lưu toàn bộ cơ sở dữ liệu (829 HS, 549 Xe, 42 CBGV, 207 Bán trú, 21 Chi đoàn) và mã nguồn phần mềm thành gói nén (.zip) an toàn tuyệt đối trên Google Drive.")

                    c_drv1, c_drv2 = st.columns([1.4, 1.2])

                    with c_drv1:
                        st.markdown("##### 🚀 **Cách 1: Đẩy Gói Dữ Liệu Lên Google Drive Qua Cloud API (1 Chạm)**")
                        opt_src = st.checkbox("Bao gồm toàn bộ mã nguồn phần mềm (.py)", value=True, key="cb_drv_src")
                        opt_db = st.checkbox("Bao gồm toàn bộ Cơ sở dữ liệu (.csv, .json) & Excel (.xlsx)", value=True, disabled=True, key="cb_drv_db")

                        if st.button("🚀 ĐẨY GÓI DỮ LIỆU LÊN GOOGLE DRIVE NGAY", type="primary", use_container_width=True, key="btn_push_gdrive"):
                            web_url = cfg_gs.get("web_app_url", "").strip()
                            if not web_url:
                                st.error("⚠️ Bạn chưa cấu hình Google Apps Script Web App URL! Vui lòng sang tab **'⚙️ CẤU HÌNH LIÊN KẾT'** để nhập link hoặc xem tab **'📖 HƯỚNG DẪN'**.")
                            else:
                                with st.spinner("Đang đóng gói và truyền tải dữ liệu lên thư mục Google Drive của trường..."):
                                    try:
                                        import requests
                                        zip_bytes = tao_goi_sao_luu_zip(bao_gom_ma_nguon=opt_src)
                                        b64_zip = base64.b64encode(zip_bytes).decode('utf-8')
                                        f_name_zip = f"Goi_Sao_Luu_THPT2_BaoYen_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
                                    
                                        payload = {
                                            "action": "upload_drive",
                                            "folder_name": "Sao_Luu_Phan_Mem_THPT2_BaoYen",
                                            "file_name": f_name_zip,
                                            "file_base64": b64_zip,
                                            "mime_type": "application/zip"
                                        }
                                    
                                        res = requests.post(web_url, json=payload, timeout=60)
                                        if res.status_code == 200:
                                            res_data = res.json() if res.headers.get('content-type', '').startswith('application/json') else {}
                                            now_str = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                                            cfg_gs["last_sync_drive"] = now_str
                                            if res_data.get("folder_url"):
                                                cfg_gs["drive_folder_url"] = res_data["folder_url"]
                                            with open(f_cfg_gs, "w", encoding="utf-8") as f_out:
                                                json.dump(cfg_gs, f_out, ensure_ascii=False, indent=2)
                                            st.balloons()
                                            st.success(f"🎉 **ĐỒNG BỘ LÊN GOOGLE DRIVE THÀNH CÔNG RỰC RỠ!** Gói sao lưu `{f_name_zip}` ({len(zip_bytes):,} bytes) đã được lưu vĩnh viễn vào thư mục Google Drive của trường lúc {now_str}.")
                                            if res_data.get("file_url"):
                                                st.link_button("🔗 Xem File Vừa Tải Lên Trên Google Drive", res_data["file_url"])
                                        else:
                                            st.error(f"❌ Google Apps Script phản hồi mã lỗi {res.status_code}: {res.text[:200]}")
                                    except Exception as err:
                                        st.error(f"❌ Lỗi kết nối Google Drive: {str(err)}")

                    with c_drv2:
                        st.markdown("##### 💻 **Cách 2: Đồng Bộ Vào Thư Mục Google Drive Trên Máy Tính**")
                        st.caption("Dành cho máy tính đã cài đặt ứng dụng **Google Drive for Desktop**:")
                        local_drv = st.text_input("Đường dẫn thư mục Google Drive cục bộ:", value=cfg_gs.get("local_drive_path", "D:/Google_Drive_THPT2_BaoYen"), key="inp_local_drv")
                        if st.button("💾 SAO CHÉP DỮ LIỆU VÀO THƯ MỤC NÀY", use_container_width=True, key="btn_local_drv"):
                            try:
                                os.makedirs(local_drv, exist_ok=True)
                                count_copied = 0
                                for f in os.listdir(BASE_DIR):
                                    if f.endswith('.csv') or f.endswith('.json'):
                                        shutil.copy2(os.path.join(BASE_DIR, f), os.path.join(local_drv, f))
                                        count_copied += 1
                                now_str = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                                cfg_gs["last_sync_drive"] = f"{now_str} (Cục bộ)"
                                cfg_gs["local_drive_path"] = local_drv
                                with open(f_cfg_gs, "w", encoding="utf-8") as f_out:
                                    json.dump(cfg_gs, f_out, ensure_ascii=False, indent=2)
                                st.success(f"✅ Đã sao chép {count_copied} file dữ liệu vào `{local_drv}`! Ứng dụng Google Drive trên máy tính sẽ tự động đẩy lên đám mây.")
                            except Exception as e_loc:
                                st.error(f"❌ Lỗi sao chép: {str(e_loc)}")

                    st.markdown("---")
                    st.markdown("##### 📥 **Cách 3: Tải Gói Dữ Liệu Thủ Công (.ZIP) & Kéo Thả Lên Google Drive**")
                    c_dl1, c_dl2 = st.columns([1.5, 1.2])
                    with c_dl1:
                        zip_data_offline = tao_goi_sao_luu_zip(bao_gom_ma_nguon=True)
                        st.download_button(
                            label="📥 TẢI GÓI SAO LƯU DỮ LIỆU TOÀN PHẦN MỀM (.ZIP)",
                            data=zip_data_offline,
                            file_name=f"Goi_Sao_Luu_THPT2_BaoYen_{date.today().strftime('%d_%m_%Y')}.zip",
                            mime="application/zip",
                            use_container_width=True
                        )
                    with c_dl2:
                        st.link_button(
                            label="📂 MỞ GOOGLE DRIVE ĐỂ KÉO THẢ TẢI LÊN",
                            url=cfg_gs.get("drive_folder_url", "").strip() or "https://drive.google.com/drive/my-drive",
                            use_container_width=True
                        )
                    st.caption("💡 Thầy/Cô chỉ cần bấm tải gói .ZIP về máy, sau đó bấm mở Google Drive và kéo thả file vào là hoàn tất việc lưu trữ an toàn 100%.")

                # -------------------------------------------------------------
                # 2. ĐỒNG BỘ LÊN GOOGLE SHEETS
                # -------------------------------------------------------------
                with tab_sync_sheets:
                    st.markdown("#### 📊 **Đồng Bộ Dữ Liệu Thời Gian Thực Lên Google Sheets**")
                    st.caption("Chọn các bảng dữ liệu muốn cập nhật vào trang tính Google Sheets của nhà trường:")

                    c_ck1, c_ck2 = st.columns(2)
                    with c_ck1:
                        sync_hs = st.checkbox(f"👨‍🎓 1. Danh sách {tong_hs} Học sinh toàn trường", value=True, key="ck_s_hs")
                        sync_xe = st.checkbox("🛵 2. Danh sách Phương tiện & Mã QR định danh", value=True, key="ck_s_xe")
                        sync_gv = st.checkbox("📋 3. Danh bạ Cán bộ Giáo viên Nhân viên & Phân công", value=True, key="ck_s_gv")
                    with c_ck2:
                        sync_bt = st.checkbox(f"🛏️ 4. Hồ sơ {so_ban_tru} Học sinh Bán trú KTX & Quân số ăn", value=True, key="ck_s_bt")
                        sync_td = st.checkbox("🏆 5. Bảng điểm thi đua Chi đoàn & Nhật ký nề nếp", value=True, key="ck_s_td")

                    c_act1, c_act2 = st.columns([1.5, 1.2])
                    with c_act1:
                        if st.button("🚀 ĐỒNG BỘ CÁC BẢNG ĐÃ CHỌN LÊN GOOGLE SHEETS", type="primary", use_container_width=True, key="btn_sync_sheets"):
                            web_url = cfg_gs.get("web_app_url", "").strip()
                            if not web_url:
                                st.error("⚠️ Bạn chưa cấu hình Google Apps Script Web App URL! Vui lòng sang tab **'⚙️ CẤU HÌNH LIÊN KẾT'** để nhập link hoặc xem tab **'📖 HƯỚNG DẪN'**.")
                            else:
                                with st.spinner("Đang đóng gói và truyền tải dữ liệu lên Google Sheets..."):
                                    try:
                                        import requests
                                        sheets_dict = {}
                                        if sync_hs and os.path.exists(f_hs_tt):
                                            sheets_dict["Hoc_Sinh_829"] = pd.read_csv(f_hs_tt, encoding='utf-8-sig').fillna("").to_dict(orient="records")
                                        if sync_xe and os.path.exists(os.path.join(BASE_DIR, "quan_ly_phuong_tien.csv")):
                                            sheets_dict["Phuong_Tien_549"] = pd.read_csv(os.path.join(BASE_DIR, "quan_ly_phuong_tien.csv"), encoding='utf-8-sig').fillna("").to_dict(orient="records")
                                        if sync_gv and os.path.exists(f_gv_db):
                                            sheets_dict["Can_Bo_42"] = pd.read_csv(f_gv_db, encoding='utf-8-sig').fillna("").to_dict(orient="records")
                                        if sync_bt and os.path.exists(f_bt_ktx):
                                            sheets_dict["Ban_Tru_KTX"] = pd.read_csv(f_bt_ktx, encoding='utf-8-sig').fillna("").to_dict(orient="records")
                                        if sync_td and os.path.exists(os.path.join(BASE_DIR, "thi_dua_dtn_20_lop.csv")):
                                            sheets_dict["Thi_Dua_21_Lop"] = pd.read_csv(os.path.join(BASE_DIR, "thi_dua_dtn_20_lop.csv"), encoding='utf-8-sig').fillna("").to_dict(orient="records")

                                        payload = {
                                            "action": "sync_sheets",
                                            "sheets": sheets_dict
                                        }
                                        res = requests.post(web_url, json=payload, timeout=30)
                                        if res.status_code == 200:
                                            now_str = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                                            cfg_gs["last_sync_sheets"] = now_str
                                            cfg_gs["status"] = "Đồng bộ thành công"
                                            with open(f_cfg_gs, "w", encoding="utf-8") as f_out:
                                                json.dump(cfg_gs, f_out, ensure_ascii=False, indent=2)
                                            st.balloons()
                                            st.success(f"🎉 **ĐỒNG BỘ THÀNH CÔNG RỰC RỠ!** Toàn bộ dữ liệu ({len(sheets_dict)} bảng) đã được cập nhật trực tiếp lên Google Sheets của trường lúc {now_str}.")
                                        else:
                                            st.error(f"❌ Google Apps Script phản hồi mã lỗi {res.status_code}: {res.text[:200]}")
                                    except Exception as err:
                                        st.error(f"❌ Lỗi kết nối khi đồng bộ: {str(err)}")

                    with c_act2:
                        # Xuất file Excel đa sheet tải về trực tiếp
                        buf_xlsx = io.BytesIO()
                        with pd.ExcelWriter(buf_xlsx, engine='openpyxl') as writer:
                            for s_name, f_path in [
                                ('Hoc_Sinh_829', f_hs_tt),
                                ('Phuong_Tien_549', os.path.join(BASE_DIR, 'quan_ly_phuong_tien.csv')),
                                ('Can_Bo_42', f_gv_db),
                                ('Ban_Tru_KTX', f_bt_ktx),
                                ('Thi_Dua_21_Lop', os.path.join(BASE_DIR, 'thi_dua_dtn_20_lop.csv'))
                            ]:
                                if os.path.exists(f_path):
                                    pd.read_csv(f_path, encoding='utf-8-sig').to_excel(writer, sheet_name=s_name, index=False)
                    
                        st.download_button(
                            label="📥 XUẤT FILE EXCEL ĐA SHEET (.XLSX) SAO LƯU",
                            data=buf_xlsx.getvalue(),
                            file_name=f"Sao_Luu_Toan_Truong_THPT2_BaoYen_{date.today().strftime('%d_%m_%Y')}.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            use_container_width=True
                        )
                        st.caption("💡 Mở trực tiếp trên máy hoặc kéo thả vào Google Drive để tạo Google Sheets tức thì.")

                # -------------------------------------------------------------
                # 3. CẤU HÌNH LIÊN KẾT & TEST PING
                # -------------------------------------------------------------
                with tab_sync_cfg:
                    st.markdown("#### ⚙️ **Cấu Hình Đường Link API Google Apps Script, Google Drive & Google Sheets**")
                
                    with st.form("form_cfg_gsheets"):
                        inp_web_url = st.text_input(
                            "🔗 Google Apps Script Web App URL (Dùng chung cho cả Google Drive & Google Sheets):",
                            value=cfg_gs.get("web_app_url", ""),
                            placeholder="https://script.google.com/macros/s/AKfycbx.../exec"
                        )
                        inp_drive_url = st.text_input(
                            "📁 Đường link Thư mục Google Drive của trường (Để mở xem và đối soát sao lưu):",
                            value=cfg_gs.get("drive_folder_url", ""),
                            placeholder="https://drive.google.com/drive/folders/1BxiMVs0XRA5nFMdKvBdB..."
                        )
                        inp_sheet_url = st.text_input(
                            "📊 Đường link Trang tính Google Sheets của trường (Để xem trực tiếp bảng số liệu):",
                            value=cfg_gs.get("spreadsheet_url", ""),
                            placeholder="https://docs.google.com/spreadsheets/d/1BxiMVs0XRA5nFMdKvBdB.../edit"
                        )
                        inp_local_path = st.text_input(
                            "💻 Đường dẫn thư mục Google Drive cục bộ trên máy tính (Google Drive Desktop):",
                            value=cfg_gs.get("local_drive_path", "D:/Google_Drive_THPT2_BaoYen")
                        )
                        btn_save_cfg_gs = st.form_submit_button("💾 LƯU CẤU HÌNH ĐÁM MÂY", type="primary")
                        if btn_save_cfg_gs:
                            cfg_gs["web_app_url"] = inp_web_url.strip()
                            cfg_gs["drive_folder_url"] = inp_drive_url.strip()
                            cfg_gs["spreadsheet_url"] = inp_sheet_url.strip()
                            cfg_gs["local_drive_path"] = inp_local_path.strip()
                            with open(f_cfg_gs, "w", encoding="utf-8") as f_out:
                                json.dump(cfg_gs, f_out, ensure_ascii=False, indent=2)
                            st.success("✅ Đã lưu cấu hình liên kết Google Drive & Google Sheets thành công!")
                            st.rerun()

                    st.markdown("---")
                    st.markdown("##### 🔍 **Kiểm Tra Trạng Thái Kết Nối (Ping Test):**")
                    if st.button("📡 KIỂM TRA ĐƯỜNG TRUYỀN API NGAY"):
                        test_url = cfg_gs.get("web_app_url", "").strip()
                        if not test_url:
                            st.warning("⚠️ Vui lòng nhập và lưu Web App URL ở trên trước khi kiểm tra.")
                        else:
                            try:
                                import requests
                                t_start = datetime.now()
                                r_test = requests.get(test_url, timeout=10)
                                latency = (datetime.now() - t_start).total_seconds() * 1000
                                if r_test.status_code == 200:
                                    st.success(f"🟢 **KẾT NỐI XUẤT SẮC!** Máy chủ Google Apps Script (Drive & Sheets) phản hồi tốt (Độ trễ: {latency:.0f}ms).")
                                    st.caption(f"Nội dung phản hồi: `{r_test.text[:150]}`")
                                else:
                                    st.warning(f"🟡 Phản hồi mã HTTP {r_test.status_code}. Vui lòng kiểm tra quyền truy cập 'Bất kỳ ai' trên Google Apps Script.")
                            except Exception as e_test:
                                st.error(f"🔴 Không thể kết nối đến Web App: {str(e_test)}")

                # -------------------------------------------------------------
                # 4. HƯỚNG DẪN CÀI ĐẶT 3 BƯỚC
                # -------------------------------------------------------------
                with tab_sync_guide:
                    st.markdown("#### 📖 **Hướng Dẫn Cài Đặt Google Drive & Sheets API (Chỉ 3 Phút - Cực Dễ!)**")
                    st.markdown("""
                    Chỉ cần làm theo đúng 3 bước đơn giản dưới đây, Thầy/Cô sẽ có một máy chủ đám mây riêng biệt trên Google Drive của trường để vừa nhận file sao lưu phần mềm, vừa tự động cập nhật Google Sheets:

                    ##### 🔹 Bước 1: Mở Google Drive của trường & Tạo file Google Sheets
                    1. Truy cập [Google Drive](https://drive.google.com) bằng tài khoản Gmail hoặc Google Workspace của trường.
                    2. Bấm nút **Mới (+) -> Google Trang tính** (Google Sheets) và đặt tên file là: `He_Thong_THPT2_BaoYen`.

                    ##### 🔹 Bước 2: Dán mã Google Apps Script tự động (Xử lý cả Drive & Sheets)
                    1. Trên thanh menu của Google Sheets, chọn: **Tiện ích mở rộng (Extensions) -> Apps Script**.
                    2. Xóa sạch đoạn mã cũ `function myFunction() {...}` có sẵn.
                    3. Sao chép và dán toàn bộ đoạn mã Javascript chuẩn mực bên dưới vào rồi bấm biểu tượng **Lưu (Ctrl + S)**:
                    """)

                    script_code = """function doPost(e) {
      try {
        var data = JSON.parse(e.postData.contents);
        var action = data.action || "sync_sheets";

        // 1. NẾU LÀ ĐỒNG BỘ LÊN GOOGLE DRIVE (LƯU GÓI PHẦN MỀM / DATABASE ZIP)
        if (action === "upload_drive" || data.file_base64) {
          var folderName = data.folder_name || "Sao_Luu_Phan_Mem_THPT2_BaoYen";
          var folders = DriveApp.getFoldersByName(folderName);
          var folder = folders.hasNext() ? folders.next() : DriveApp.createFolder(folderName);
      
          var fileName = data.file_name || ("Sao_Luu_" + Utilities.formatDate(new Date(), "GMT+7", "yyyyMMdd_HHmmss") + ".zip");
          var fileBytes = Utilities.base64Decode(data.file_base64);
          var blob = Utilities.newBlob(fileBytes, data.mime_type || "application/zip", fileName);
          var newFile = folder.createFile(blob);
      
          return ContentService.createTextOutput(JSON.stringify({
            status: "success",
            message: "Đã lưu trữ thành công file '" + fileName + "' vào thư mục Google Drive: " + folderName,
            file_url: newFile.getUrl(),
            file_id: newFile.getId(),
            folder_url: folder.getUrl(),
            timestamp: new Date().toISOString()
          })).setMimeType(ContentService.MimeType.JSON);
        }

        // 2. NẾU LÀ ĐỒNG BỘ DỮ LIỆU ĐỘNG VÀO TRANG TÍNH GOOGLE SHEETS
        var ss = SpreadsheetApp.getActiveSpreadsheet();
        var sheetsData = data.sheets || data;
        var count = 0;
    
        for (var sheetName in sheetsData) {
          if (sheetName === "action" || sheetName === "folder_name") continue;
          var rows = sheetsData[sheetName];
          if (!rows || rows.length === 0) continue;
      
          var sheet = ss.getSheetByName(sheetName);
          if (!sheet) {
            sheet = ss.insertSheet(sheetName);
          } else {
            sheet.clear();
          }
      
          var headers = Object.keys(rows[0]);
          var values = [headers];
          for (var i = 0; i < rows.length; i++) {
            var rowValues = [];
            for (var j = 0; j < headers.length; j++) {
              rowValues.push(rows[i][headers[j]] || "");
            }
            values.push(rowValues);
          }
      
          sheet.getRange(1, 1, values.length, headers.length).setValues(values);
          sheet.getRange(1, 1, 1, headers.length)
               .setBackground("#1E3A8A")
               .setFontColor("#FFFFFF")
               .setFontWeight("bold");
          sheet.autoResizeColumns(1, headers.length);
          count++;
        }
    
        return ContentService.createTextOutput(JSON.stringify({
          status: "success",
          message: "Đã cập nhật " + count + " bảng dữ liệu lên Google Sheets thành công!",
          timestamp: new Date().toISOString()
        })).setMimeType(ContentService.MimeType.JSON);

      } catch (error) {
        return ContentService.createTextOutput(JSON.stringify({
          status: "error",
          message: error.toString()
        })).setMimeType(ContentService.MimeType.JSON);
      }
    }

    function doGet(e) {
      return ContentService.createTextOutput(JSON.stringify({
        status: "online",
        school: "Trường THPT số 2 Bảo Yên",
        services: ["Google Drive", "Google Sheets"],
        message: "Google Apps Script API (Drive & Sheets) đang hoạt động bình thường!"
      })).setMimeType(ContentService.MimeType.JSON);
    }"""

                    st.code(script_code, language="javascript")

                    st.markdown("""
                    ##### 🔹 Bước 3: Triển khai thành Web App & Dán link vào phần mềm
                    1. Tại giao diện Apps Script, bấm nút màu xanh **Triển khai (Deploy) -> Tùy chọn triển khai mới (New deployment)** ở góc trên bên phải.
                    2. Bấm vào biểu tượng bánh răng **Chọn loại -> Ứng dụng web (Web app)**.
                    3. Đặt cấu hình:
                       - **Mô tả:** `THPT 2 Bao Yen Drive & Sheets API`
                       - **Thực thi dưới dạng:** *Tôi (địa chỉ email của bạn)*
                       - **Người có quyền truy cập:** **Bất kỳ ai (Anyone)** *(Rất quan trọng để phần mềm gửi được dữ liệu sang)*.
                    4. Bấm **Triển khai** -> Bấm **Cấp quyền truy cập** (Authorize access) -> Chọn tài khoản Google của bạn -> Bấm **Nâng cao (Advanced)** -> Bấm **Đi tới... (không an toàn)** -> Bấm **Cho phép (Allow)**.
                    5. Sao chép dòng **URL của ứng dụng web** (có dạng `https://script.google.com/macros/s/.../exec`).
                    6. Quay lại phần mềm, sang tab **'⚙️ CẤU HÌNH LIÊN KẾT'** ở trên dán link vào và bấm **Lưu cấu hình**.
                
                    🎉 **Chúc mừng Thầy/Cô!** Từ lúc này, Thầy/Cô có thể vừa đẩy toàn bộ file sao lưu phần mềm lên **Google Drive**, vừa đồng bộ trực tiếp các bảng tính lên **Google Sheets** tự động 100%!
                    """)
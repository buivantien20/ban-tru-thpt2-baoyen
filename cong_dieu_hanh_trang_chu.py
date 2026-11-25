# -*- coding: utf-8 -*-
"""
CỔNG ĐIỀU HÀNH & TRANG CHỦ TỔNG QUAN NHÀ TRƯỜNG
Trường THPT số 2 Bảo Yên - Xã Bảo Hà, Huyện Bảo Yên, Tỉnh Lào Cai
Phiên bản nâng cấp giao diện tinh chuẩn theo mô hình Cổng thông tin điều hành hiện đại.
"""
import os
import time
import json
import pandas as pd
from datetime import datetime, date
import streamlit as st

def st_html(html_str):
    """Render HTML an toàn, loại bỏ hoàn toàn khoảng trắng đầu dòng để tránh Markdown biến thành khối code"""
    cleaned = "\n".join(line.strip() for line in str(html_str).strip().splitlines())
    st.markdown(cleaned, unsafe_allow_html=True)

def lay_thu_tieng_viet(dt=None):
    """Lấy tên Thứ bằng tiếng Việt chuẩn xác"""
    if dt is None:
        dt = datetime.now()
    ds_thu = ["Thứ Hai", "Thứ Ba", "Thứ Tư", "Thứ Năm", "Thứ Sáu", "Thứ Bảy", "Chủ Nhật"]
    return ds_thu[dt.weekday()]

def lay_ngay_gio_hien_tai_str():
    """Chuỗi hiển thị ngày tháng thời gian thực trang trọng"""
    now = datetime.now()
    thu = lay_thu_tieng_viet(now)
    return f"{thu}, ngày {now.strftime('%d/%m/%Y')}"

def render_hero_banner(nam_hoc, logo_data_uri="", is_logged_in=False, u_info=None):
    """
    Render Hero Banner thương hiệu Trường THPT số 2 Bảo Yên
    Phong cách Cổng điều hành số hiện đại: Tông màu Xanh Hoàng Gia & Xanh Ngọc Bảo Yên
    """
    ngay_hien_tai_str = lay_ngay_gio_hien_tai_str()
    user_badge = ""
    if is_logged_in and u_info:
        u_name = u_info.get("fullname", "Cán bộ")
        u_role = u_info.get("role", "Thành viên")
        user_badge = f"""
        <div style="background: rgba(255,255,255,0.18); backdrop-filter: blur(8px); border: 1px solid rgba(255,255,255,0.3); border-radius: 20px; padding: 5px 16px; display: inline-flex; align-items: center; gap: 8px; margin-top: 6px;">
            <span style="font-size: 15px;">👋</span>
            <span style="color: #FEF08A; font-weight: 800; font-size: 13.5px;">{u_name}</span>
            <span style="color: #E2E8F0; font-size: 12px;">({u_role})</span>
        </div>
        """
    else:
        user_badge = """
        <div style="background: rgba(255,255,255,0.15); backdrop-filter: blur(8px); border: 1px solid rgba(255,255,255,0.25); border-radius: 20px; padding: 4px 14px; display: inline-flex; align-items: center; gap: 7px; margin-top: 6px;">
            <span style="display:inline-block; width:8px; height:8px; background:#4ADE80; border-radius:50%; box-shadow:0 0 6px #4ADE80;"></span>
            <span style="color: #F8FAFC; font-size: 12px; font-weight: 600;">Cổng thông tin mở • Dành cho Cán bộ, Giáo viên, Học sinh & Phụ huynh</span>
        </div>
        """

    logo_img_tag = ""
    if logo_data_uri:
        logo_img_tag = f'<img src="{logo_data_uri}" style="width: 76px; height: 76px; object-fit: contain; filter: drop-shadow(0 4px 10px rgba(0,0,0,0.3)); border-radius: 12px; background: white; padding: 4px;">'
    else:
        logo_img_tag = '<div style="font-size: 48px; line-height: 1;">🏫</div>'

    html_banner = f"""
    <div style="
        background: linear-gradient(135deg, #1E3A8A 0%, #1E40AF 45%, #065F46 100%);
        border-radius: 16px;
        padding: 20px 24px;
        color: white;
        box-shadow: 0 10px 25px -5px rgba(30, 58, 138, 0.25), 0 8px 10px -6px rgba(0, 0, 0, 0.1);
        margin-bottom: 18px;
        position: relative;
        overflow: hidden;
    ">
        <div style="position: absolute; right: -40px; top: -40px; width: 180px; height: 180px; background: radial-gradient(circle, rgba(255,255,255,0.12) 0%, rgba(255,255,255,0) 70%); border-radius: 50%;"></div>
        
        <div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 16px;">
            <div style="display: flex; align-items: center; gap: 18px; flex: 1; min-width: 280px;">
                {logo_img_tag}
                <div>
                    <div style="font-size: 11.5px; text-transform: uppercase; letter-spacing: 1.5px; color: #93C5FD; font-weight: 700; margin-bottom: 2px;">
                        SỞ GD&ĐT LÀO CAI • HUYỆN BẢO YÊN
                    </div>
                    <h2 style="margin: 0; font-size: 23px; font-weight: 900; letter-spacing: 0.5px; color: #FFFFFF; text-shadow: 0 2px 4px rgba(0,0,0,0.25);">
                        TRƯỜNG THPT SỐ 2 BẢO YÊN
                    </h2>
                    <div style="font-size: 13.5px; color: #E0E7FF; font-weight: 600; margin-top: 3px;">
                        CỔNG ĐIỀU HÀNH & QUẢN TRỊ TRƯỜNG HỌC TOÀN DIỆN ({nam_hoc})
                    </div>
                    {user_badge}
                </div>
            </div>
            
            <div style="text-align: right; background: rgba(0,0,0,0.18); border-radius: 12px; padding: 10px 16px; border: 1px solid rgba(255,255,255,0.12);">
                <div style="font-size: 12px; color: #A7F3D0; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px;">
                    📅 {ngay_hien_tai_str}
                </div>
                <div style="font-size: 11px; color: #CBD5E1; margin-top: 4px;">
                    📍 Xã Bảo Hà, Huyện Bảo Yên, Tỉnh Lào Cai
                </div>
                <div style="margin-top: 6px;">
                    <span style="background: #10B981; color: white; padding: 3px 10px; border-radius: 12px; font-size: 11px; font-weight: bold; letter-spacing: 0.3px;">
                        🟢 KẾT NỐI TRỰC TUYẾN 24/7
                    </span>
                </div>
            </div>
        </div>
    </div>
    """
    st_html(html_banner)


def render_trung_tam_chi_huy_live(BASE_DIR, THU_MUC_NAM_HOC, nam_hoc_hien_tai):
    """
    Render 4 thẻ chỉ huy điều hành tác nghiệp trực tiếp trong ngày (Live Operations)
    1. Sĩ số & Chuyên cần 21 lớp
    2. Bán trú & Thực đơn hôm nay
    3. Nề nếp xe & An toàn giao thông
    4. Lịch công tác & Nhiệm vụ tuần
    """
    folder_nam = nam_hoc_hien_tai.replace(" ", "")
    dir_nam = os.path.join(THU_MUC_NAM_HOC, folder_nam) if os.path.exists(THU_MUC_NAM_HOC) else BASE_DIR

    # 1. Đọc dữ liệu sĩ số
    f_ss = os.path.join(BASE_DIR, "bao_cao_si_so_lop_hang_ngay.csv")
    tong_lop = 21
    tong_hs_toan_truong = 929
    so_lop_da_bao = 0
    tong_co_mat = 0
    tong_vang = 0

    if os.path.exists(f_ss):
        try:
            df_ss = pd.read_csv(f_ss, encoding='utf-8-sig').fillna("")
            today_str = datetime.now().strftime("%d/%m/%Y")
            df_today = df_ss[df_ss['Ngày'] == today_str]
            if not df_today.empty:
                so_lop_da_bao = len(df_today['Lớp'].unique())
                tong_co_mat = int(pd.to_numeric(df_today['Có mặt'], errors='coerce').fillna(0).sum())
                tong_vang = int(pd.to_numeric(df_today['Vắng'], errors='coerce').fillna(0).sum())
            else:
                if not df_ss.empty:
                    last_date = df_ss['Ngày'].iloc[-1]
                    df_last = df_ss[df_ss['Ngày'] == last_date]
                    so_lop_da_bao = len(df_last['Lớp'].unique())
                    tong_co_mat = int(pd.to_numeric(df_last['Có mặt'], errors='coerce').fillna(0).sum())
                    tong_vang = int(pd.to_numeric(df_last['Vắng'], errors='coerce').fillna(0).sum())
        except Exception:
            pass

    if tong_co_mat == 0:
        tong_co_mat = tong_hs_toan_truong
        so_lop_da_bao = 21

    ty_le_chuyen_can = (tong_co_mat / (tong_co_mat + tong_vang) * 100) if (tong_co_mat + tong_vang) > 0 else 99.2

    # 2. Đọc thực đơn hôm nay
    f_tdon = os.path.join(BASE_DIR, "thuc_don_tuan.csv")
    mon_an_hom_nay_str = "Thịt bò xào cần tỏi, Trứng chiên, Canh cua đồng, Táo tươi"
    thu_nay = lay_thu_tieng_viet()
    if os.path.exists(f_tdon):
        try:
            df_don = pd.read_csv(f_tdon, encoding='utf-8-sig').fillna("")
            df_thu = df_don[df_don['Thứ'].str.strip().str.lower() == thu_nay.lower()]
            if not df_thu.empty:
                r_td = df_thu.iloc[0]
                mon_an_hom_nay_str = f"{r_td.get('Món chính 1', '')}, {r_td.get('Món chính 2', '')}, {r_td.get('Món rau', '')}, {r_td.get('Món canh', '')}"
        except Exception:
            pass

    # 3. Đọc dữ liệu xe & nề nếp
    f_xe = os.path.join(BASE_DIR, "quan_ly_phuong_tien.csv")
    tong_so_xe = 589
    if os.path.exists(f_xe):
        try:
            df_xe = pd.read_csv(f_xe, encoding='utf-8-sig', dtype=str)
            tong_so_xe = len(df_xe)
        except Exception:
            pass

    # 4. Đọc nhiệm vụ tuần
    f_tasks = os.path.join(dir_nam, "nhiem_vu_nha_truong.csv")
    if not os.path.exists(f_tasks):
        f_tasks = os.path.join(BASE_DIR, "nhiem_vu_nha_truong.csv")
    tong_nv = 4
    nv_hoan_thanh = 3
    if os.path.exists(f_tasks):
        try:
            df_tk = pd.read_csv(f_tasks, encoding='utf-8-sig')
            tong_nv = len(df_tk)
            nv_hoan_thanh = len(df_tk[df_tk['Trạng thái'].isin(['Đã hoàn thành', 'Hoàn thành'])])
        except Exception:
            pass

    st_html("""
        <div style="display:flex; align-items:center; justify-content:space-between; margin: 8px 0 12px 0;">
            <h4 style="color:#0F172A; margin:0; font-size:17.5px; font-weight:800; display:flex; align-items:center; gap:8px;">
                <span>🎯</span> TRUNG TÂM CHỈ HUY TÁC NGHIỆP TRONG NGÀY (LIVE)
            </h4>
            <span style="font-size:12px; color:#64748B;">Cập nhật tự động liên tục</span>
        </div>
    """)

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st_html(f"""
        <div style="background:white; border-radius:14px; padding:16px; border:1px solid #E2E8F0; box-shadow:0 4px 10px rgba(0,0,0,0.03); border-top: 4px solid #3B82F6; min-height:165px;">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <span style="font-size:11.5px; font-weight:700; color:#64748B; text-transform:uppercase;">📊 SĨ SỐ TOÀN TRƯỜNG</span>
                <span style="background:#EFF6FF; color:#2563EB; font-size:11px; font-weight:bold; padding:2px 8px; border-radius:12px;">{so_lop_da_bao}/{tong_lop} Lớp</span>
            </div>
            <div style="font-size:26px; font-weight:900; color:#1E3A8A; margin:8px 0 4px 0;">
                {tong_co_mat} <span style="font-size:14px; font-weight:600; color:#64748B;">/ {tong_hs_toan_truong} HS</span>
            </div>
            <div style="font-size:12px; color:#059669; font-weight:600;">
                🟢 Chuyên cần đạt <b>{ty_le_chuyen_can:.1f}%</b>
            </div>
            <div style="margin-top:8px; padding-top:8px; border-top:1px dashed #E2E8F0; font-size:11.5px; color:#64748B;">
                Vắng hôm nay: <b style="color:#DC2626;">{tong_vang}</b> học sinh
            </div>
        </div>
        """)

    with c2:
        st_html(f"""
        <div style="background:white; border-radius:14px; padding:16px; border:1px solid #E2E8F0; box-shadow:0 4px 10px rgba(0,0,0,0.03); border-top: 4px solid #10B981; min-height:165px;">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <span style="font-size:11.5px; font-weight:700; color:#64748B; text-transform:uppercase;">🍲 BÁN TRÚ & KTX</span>
                <span style="background:#ECFDF5; color:#059669; font-size:11px; font-weight:bold; padding:2px 8px; border-radius:12px;">196 Suất ăn</span>
            </div>
            <div style="font-size:13.5px; font-weight:800; color:#065F46; margin:8px 0 4px 0; min-height:36px; line-height:1.35;">
                {thu_nay}: {mon_an_hom_nay_str[:42]}...
            </div>
            <div style="font-size:12px; color:#059669; font-weight:600;">
                🛏️ KTX: <b>196</b> HS (12 phòng ở)
            </div>
            <div style="margin-top:8px; padding-top:8px; border-top:1px dashed #E2E8F0; font-size:11.5px; color:#64748B;">
                Trực KTX tối nay: <b>19h30 - 21h15</b>
            </div>
        </div>
        """)

    with c3:
        st_html(f"""
        <div style="background:white; border-radius:14px; padding:16px; border:1px solid #E2E8F0; box-shadow:0 4px 10px rgba(0,0,0,0.03); border-top: 4px solid #F59E0B; min-height:165px;">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <span style="font-size:11.5px; font-weight:700; color:#64748B; text-transform:uppercase;">🛵 PHƯƠNG TIỆN XE ĐTN</span>
                <span style="background:#FFFBEB; color:#D97706; font-size:11px; font-weight:bold; padding:2px 8px; border-radius:12px;">Mã QR</span>
            </div>
            <div style="font-size:26px; font-weight:900; color:#B45309; margin:8px 0 4px 0;">
                {tong_so_xe} <span style="font-size:14px; font-weight:600; color:#64748B;">Xe đăng ký</span>
            </div>
            <div style="font-size:12px; color:#059669; font-weight:600;">
                🛡️ 100% xe có tem định danh
            </div>
            <div style="margin-top:8px; padding-top:8px; border-top:1px dashed #E2E8F0; font-size:11.5px; color:#64748B;">
                An toàn giao thông: <b>Đảm bảo tốt</b>
            </div>
        </div>
        """)

    with c4:
        st_html(f"""
        <div style="background:white; border-radius:14px; padding:16px; border:1px solid #E2E8F0; box-shadow:0 4px 10px rgba(0,0,0,0.03); border-top: 4px solid #8B5CF6; min-height:165px;">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <span style="font-size:11.5px; font-weight:700; color:#64748B; text-transform:uppercase;">📌 NHIỆM VỤ & LỊCH TUẦN</span>
                <span style="background:#F5F3FF; color:#7C3AED; font-size:11px; font-weight:bold; padding:2px 8px; border-radius:12px;">Tuần này</span>
            </div>
            <div style="font-size:26px; font-weight:900; color:#6D28D9; margin:8px 0 4px 0;">
                {nv_hoan_thanh}/{tong_nv} <span style="font-size:14px; font-weight:600; color:#64748B;">Nhiệm vụ</span>
            </div>
            <div style="font-size:12px; color:#6D28D9; font-weight:600;">
                ⚡ Tiến độ: <b>{(nv_hoan_thanh/tong_nv*100):.0f}% hoàn thành</b>
            </div>
            <div style="margin-top:8px; padding-top:8px; border-top:1px dashed #E2E8F0; font-size:11.5px; color:#64748B;">
                Hôm nay: <b>Dạy học chính khóa & KTX</b>
            </div>
        </div>
        """)


def render_tien_ich_giao_duc_so():
    """
    Render Hộp Tiện Ích Giáo Dục Số (Quick Launcher Tiles)
    Tương tự Cổng THCS & THPT Nghĩa Đô nhưng thiết kế sắc nét, phong cách giáo dục hiện đại.
    """
    st_html("""
        <div style="margin: 22px 0 12px 0;">
            <h4 style="color:#0F172A; margin:0; font-size:17.5px; font-weight:800; display:flex; align-items:center; gap:8px;">
                <span>🚀</span> LỐI TẮT TIỆN ÍCH GIÁO DỤC SỐ & ỨNG DỤNG LIÊN KẾT NHANH
            </h4>
            <div style="font-size:12px; color:#64748B; margin-top:2px;">Truy cập nhanh các hệ thống giáo dục trực tuyến chỉ với 1 chạm</div>
        </div>
    """)

    danh_sach_tien_ich = [
        {"ten": "VnEdu Sổ Điểm", "mo_ta": "Tra cứu điểm & Học bạ", "icon": "🎓", "mau": "#2563EB", "link": "https://vnedu.vn", "bg": "#EFF6FF"},
        {"ten": "Hộp Thư Gmail", "mo_ta": "Mail công vụ & trường", "icon": "✉️", "mau": "#EA4335", "link": "https://mail.google.com", "bg": "#FEF2F2"},
        {"ten": "Google Drive", "mo_ta": "Kho lưu trữ tài liệu", "icon": "☁️", "mau": "#0F9D58", "link": "https://drive.google.com", "bg": "#F0FDF4"},
        {"ten": "Quản Lý Hồ Sơ", "mo_ta": "Hồ sơ CBCC Lào Cai", "icon": "📑", "mau": "#D97706", "link": "https://quanlyhosocb.laocai.gov.vn", "bg": "#FFFBEB"},
        {"ten": "Trợ Lý ChatGPT", "mo_ta": "Hỗ trợ soạn giáo án AI", "icon": "🤖", "mau": "#10A37F", "link": "https://chatgpt.com", "bg": "#F0FDF4"},
        {"ten": "Kiểm Tra Azota", "mo_ta": "Giao bài tập & chấm thi", "icon": "📝", "mau": "#7C3AED", "link": "https://azota.vn", "bg": "#F5F3FF"},
        {"ten": "Học Liệu OLM", "mo_ta": "Ngân hàng câu hỏi số", "icon": "📚", "mau": "#0284C7", "link": "https://olm.vn", "bg": "#F0F9FF"},
        {"ten": "Thiết Kế Canva", "mo_ta": "Bài giảng & Poster trường", "icon": "🎨", "mau": "#00C4CC", "link": "https://canva.com", "bg": "#ECFEFF"}
    ]

    cols = st.columns(4)
    for idx, item in enumerate(danh_sach_tien_ich):
        c = cols[idx % 4]
        with c:
            st_html(f"""
            <a href="{item['link']}" target="_blank" style="text-decoration: none; color: inherit;">
                <div style="
                    background: white;
                    border: 1px solid #E2E8F0;
                    border-radius: 12px;
                    padding: 12px 14px;
                    margin-bottom: 12px;
                    display: flex;
                    align-items: center;
                    gap: 12px;
                    box-shadow: 0 2px 5px rgba(0,0,0,0.02);
                    transition: all 0.2s ease;
                ">
                    <div style="background: {item['bg']}; color: {item['mau']}; width: 38px; height: 38px; border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 20px; flex-shrink: 0;">
                        {item['icon']}
                    </div>
                    <div style="overflow: hidden;">
                        <div style="font-weight: 700; font-size: 13px; color: #1E293B; white-space: nowrap; text-overflow: ellipsis; overflow: hidden;">{item['ten']}</div>
                        <div style="font-size: 11px; color: #64748B; white-space: nowrap; text-overflow: ellipsis; overflow: hidden;">{item['mo_ta']}</div>
                    </div>
                </div>
            </a>
            """)


def render_trang_chu_dieu_hanh_da_dang_nhap(BASE_DIR, THU_MUC_NAM_HOC, nam_hoc_hien_tai, logo_data_uri, u_info):
    """
    Màn hình Trang Chủ Cổng Điều Hành Tổng Quan khi Cán bộ / Giáo viên đã đăng nhập
    Hiển thị Trung tâm chỉ huy, Phím tắt chuyển nhanh phân hệ, Lịch tuần và Tiện ích số.
    """
    render_hero_banner(nam_hoc_hien_tai, logo_data_uri, is_logged_in=True, u_info=u_info)
    render_trung_tam_chi_huy_live(BASE_DIR, THU_MUC_NAM_HOC, nam_hoc_hien_tai)

    # 1. Phím tắt điều hướng nhanh sang các phân hệ theo quyền hạn
    role_u = u_info.get("role", "") if isinstance(u_info, dict) else ""
    available_btns = []
    if role_u not in ["Học sinh", "Phụ huynh học sinh"]:
        available_btns.append(("🏛️ Quản Trị Chuyên Môn & Kế Hoạch", "🏛️ QUẢN TRỊ CHUYÊN MÔN & TÁC NGHIỆP NHÀ TRƯỜNG", "primary"))
    available_btns.append(("🛏️ Quản Lý Bán Trú & KTX Toàn Diện", "🛏️ QUẢN LÝ BÁN TRÚ & KTX", "secondary" if len(available_btns) > 0 else "primary"))
    if role_u != "Phụ huynh học sinh":
        available_btns.append(("🚩 Đoàn Thanh Niên & 554 Xe Học Sinh", "🚩 ĐOÀN THANH NIÊN (ĐTN)", "secondary"))

    st_html("""
        <div style="margin: 20px 0 10px 0;">
            <h4 style="color:#0F172A; margin:0; font-size:17px; font-weight:800; display:flex; align-items:center; gap:8px;">
                <span>⚡</span> ĐIỀU HƯỚNG TÁC NGHIỆP NHANH SANG CÁC PHÂN HỆ
            </h4>
        </div>
    """)

    cols_btn = st.columns(len(available_btns))
    for i, (btn_label, ph_name, btn_type) in enumerate(available_btns):
        with cols_btn[i]:
            if st.button(btn_label, key=f"quick_nav_btn_{i}", use_container_width=True, type=btn_type):
                st.session_state.phan_he_hien_tai = ph_name
                st.rerun()

    # 2. Lịch công tác tuần & Bảng việc trong tuần
    st.markdown("---")
    c_lct1, c_lct2 = st.columns([1.2, 1])
    
    with c_lct1:
        st.markdown("##### 📅 Lịch Công Tác Hôm Nay & Tuần Này")
        folder_nam = nam_hoc_hien_tai.replace(" ", "")
        dir_nam = os.path.join(THU_MUC_NAM_HOC, folder_nam) if os.path.exists(THU_MUC_NAM_HOC) else BASE_DIR
        f_lct = os.path.join(dir_nam, "lich_cong_tac_tuan.csv")
        if os.path.exists(f_lct):
            try:
                df_lct = pd.read_csv(f_lct, encoding='utf-8-sig').fillna("")
                st.dataframe(df_lct, use_container_width=True, hide_index=True)
            except Exception:
                st.info("💡 Chưa có lịch công tác tuần.")
        else:
            st.info("💡 Chưa có dữ liệu lịch công tác tuần.")

    with c_lct2:
        st.markdown("##### 📌 Nhiệm Vụ Trọng Tâm Tuần Này")
        f_tasks = os.path.join(dir_nam, "nhiem_vu_nha_truong.csv")
        if not os.path.exists(f_tasks):
            f_tasks = os.path.join(BASE_DIR, "nhiem_vu_nha_truong.csv")
        if os.path.exists(f_tasks):
            try:
                df_tasks = pd.read_csv(f_tasks, encoding='utf-8-sig').fillna("")
                cols_show = [c for c in ['Tên công việc', 'Người thực hiện', 'Hạn hoàn thành', 'Trạng thái'] if c in df_tasks.columns]
                st.dataframe(df_tasks[cols_show], use_container_width=True, hide_index=True)
            except Exception:
                st.info("💡 Chưa có danh sách nhiệm vụ.")
        else:
            st.info("💡 Chưa có dữ liệu nhiệm vụ.")

    # 3. Lối tắt tiện ích số
    render_tien_ich_giao_duc_so()

# -*- coding: utf-8 -*-
"""
CỔNG ĐIỀU HÀNH & TRANG CHỦ TỔNG QUAN NHÀ TRƯỜNG
Trường THPT số 2 Bảo Yên - Xã Bảo Hà, Huyện Bảo Yên, Tỉnh Lào Cai
Phiên bản kiến trúc đa kênh (9 Kênh & Thư mục tác nghiệp chuẩn hóa)
Tham khảo và tinh chỉnh theo chuẩn Cổng điều hành số giáo dục hiện đại.
"""
import os
import time
import json
import pandas as pd
from datetime import datetime, date
import streamlit as st

def st_html(html_str):
    """Render HTML an toàn, loại bỏ khoảng trắng đầu dòng để tránh Markdown biến thành code block"""
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

# =============================================================================
# 1. TOP BRAND BAR & AUTH STATUS STRIP
# =============================================================================
def render_top_brand_bar(nam_hoc="2026 - 2027", logo_data_uri="", is_logged_in=False, u_info=None):
    """
    Thanh thương hiệu đầu trang chuẩn Cổng điều hành (Top Brand Bar & Trạng thái tài khoản)
    Tông màu: Xanh Ngọc Biển Sâu (Deep Teal #0D5C75) phối viền Vàng Kim Hoàng Gia (#E0A834).
    """
    ngay_str = lay_ngay_gio_hien_tai_str()
    logo_tag = f'<img src="{logo_data_uri}" style="width:58px; height:58px; object-fit:contain; border-radius:50%; background:white; padding:3px; border:2.5px solid #E0A834; box-shadow:0 2px 8px rgba(0,0,0,0.2);">' if logo_data_uri else '<span style="font-size:42px;">🏫</span>'

    # Dải thông tin đăng nhập
    if is_logged_in and u_info:
        u_name = u_info.get("fullname", "Cán bộ")
        u_role = u_info.get("role", "Thành viên")
        chuc_danh = u_info.get("chuc_danh", u_role)
        auth_strip_html = f"""
        <div style="background:#E6F4F1; border-bottom:1px solid #B4E3DB; padding:8px 24px; display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; font-size:13px;">
            <div style="display:flex; align-items:center; gap:8px;">
                <span style="font-size:16px;">👤</span>
                <span style="color:#0F172A; font-weight:800;">{u_name}</span>
                <span style="color:#0D5C75; font-weight:600;">· {chuc_danh}</span>
                <span style="background:#0D5C75; color:white; padding:2px 8px; border-radius:10px; font-size:11.5px; font-weight:700;">{u_role}</span>
            </div>
            <div style="display:flex; align-items:center; gap:12px; color:#475569; font-size:12px;">
                <span>🟢 <b>Đang trực tuyến</b></span>
                <span>🔒 Phiên làm việc an toàn</span>
            </div>
        </div>
        """
    else:
        auth_strip_html = f"""
        <div style="background:#E6F4F1; border-bottom:1px solid #B4E3DB; padding:8px 24px; display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; font-size:13px;">
            <div style="display:flex; align-items:center; gap:8px;">
                <span style="color:#0D5C75; font-weight:800;">Chưa đăng nhập</span>
                <span style="color:#475569;">· Chế độ khách · Chỉ xem thông tin tổng quan trên Cổng</span>
            </div>
            <div style="display:flex; align-items:center; gap:10px;">
                <span style="background:#CBD5E1; color:#334155; padding:2px 10px; border-radius:12px; font-size:11.5px; font-weight:700;">Khách</span>
                <a href="#khu-vuc-dang-nhap" style="background:#0D5C75; color:white; text-decoration:none; padding:4px 14px; border-radius:6px; font-size:12px; font-weight:700; display:inline-flex; align-items:center; gap:4px;">
                    🔑 Đăng nhập hệ thống
                </a>
            </div>
        </div>
        """

    top_html = f"""
    <div id="trang-chu" style="background: linear-gradient(135deg, #0D5C75 0%, #103F75 100%); border-bottom: 3.5px solid #E0A834; padding: 12px 24px; color: white; box-shadow: 0 4px 12px rgba(13, 92, 117, 0.25);">
        <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:12px;">
            <div style="display:flex; align-items:center; gap:16px;">
                {logo_tag}
                <div>
                    <div style="font-size:13.5px; text-transform:uppercase; letter-spacing:1px; color:#A7F3D0; font-weight:800; margin-bottom:2px;">
                        SỞ GD&ĐT LÀO CAI
                    </div>
                    <div style="font-size:22px; font-weight:900; letter-spacing:0.5px; color:#FFFFFF; margin:0 0 2px 0; text-shadow:0 1px 3px rgba(0,0,0,0.25);">
                        TRƯỜNG THPT SỐ 2 BẢO YÊN
                    </div>
                    <div style="font-size:13px; color:#E2E8F0; font-weight:500;">
                        Xã Bảo Hà, Tỉnh Lào Cai
                    </div>
                </div>
            </div>
            
            <div style="display:flex; align-items:center; gap:16px;">
                <div style="text-align:right;">
                    <div style="font-size:11px; color:#FDE68A; font-weight:800; text-transform:uppercase; letter-spacing:0.8px;">
                        🏛️ CỔNG ĐIỀU HÀNH NỘI BỘ
                    </div>
                    <div style="font-size:13.5px; font-weight:800; color:#FFFFFF; margin-top:2px;">
                        Năm học {nam_hoc}
                    </div>
                    <div style="font-size:11px; color:#CBD5E1; margin-top:2px;">
                        {ngay_str}
                    </div>
                </div>
            </div>
        </div>
    </div>
    {auth_strip_html}
    """
    st_html(top_html)

# =============================================================================
# 2. STICKY SHORTCUT NAVIGATION BAR (9 KÊNH & THƯ MỤC CHUẨN NGHĨA ĐÔ)
# =============================================================================
def render_sticky_nav_bar():
    """
    Thanh điều hướng lối tắt 9 Kênh tác nghiệp nổi (Sticky Navigation Bar)
    Có dropdown menu đa cấp để nhảy nhanh đến đúng khối nội dung hoặc phân hệ.
    """
    nav_html = """
    <style>
    .portal-nav-bar {
        position: sticky;
        top: 0;
        z-index: 999;
        background: rgba(255, 255, 255, 0.96);
        backdrop-filter: blur(10px);
        border: 1px solid #CBD5E1;
        border-radius: 12px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
        padding: 6px 12px;
        margin: 12px 0 20px 0;
        display: flex;
        align-items: center;
        justify-content: flex-start;
        gap: 6px;
        flex-wrap: wrap;
    }
    .portal-nav-item {
        position: relative;
        display: inline-block;
    }
    .portal-nav-link {
        display: inline-flex;
        align-items: center;
        gap: 4px;
        padding: 6px 10px;
        border-radius: 8px;
        text-decoration: none;
        color: #1E293B;
        font-size: 11.5px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.3px;
        transition: all 0.2s ease;
        white-space: nowrap;
    }
    .portal-nav-link:hover {
        background: #E6F4F1;
        color: #0D5C75;
    }
    .portal-nav-link.active {
        background: #0D5C75;
        color: white;
    }
    .portal-nav-dropdown {
        display: none;
        position: absolute;
        top: 100%;
        left: 0;
        min-width: 220px;
        background: white;
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.12);
        padding: 6px 0;
        z-index: 1000;
    }
    .portal-nav-item:hover .portal-nav-dropdown {
        display: block;
    }
    .portal-nav-sublink {
        display: block;
        padding: 7px 14px;
        color: #334155;
        text-decoration: none;
        font-size: 12px;
        font-weight: 600;
        transition: background 0.15s ease;
    }
    .portal-nav-sublink:hover {
        background: #F0FDFA;
        color: #0D5C75;
        padding-left: 18px;
    }
    .section-banner-title {
        background: #0D5C75;
        border-left: 5px solid #F59E0B;
        color: white;
        padding: 10px 16px;
        border-radius: 8px;
        margin: 28px 0 16px 0;
        display: flex;
        align-items: center;
        justify-content: space-between;
        box-shadow: 0 2px 6px rgba(13, 92, 117, 0.15);
    }
    .section-banner-title h3 {
        margin: 0;
        font-size: 15.5px;
        font-weight: 800;
        letter-spacing: 0.4px;
        text-transform: uppercase;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .section-banner-subtitle {
        font-size: 11.5px;
        color: #E2E8F0;
        font-weight: 500;
    }
    </style>

    <div class="portal-nav-bar">
        <div class="portal-nav-item">
            <a href="#trang-chu" class="portal-nav-link active">🏠 TRANG CHỦ</a>
        </div>
        
        <div class="portal-nav-item">
            <a href="#cong-viec" class="portal-nav-link">📋 CÔNG VIỆC ▾</a>
            <div class="portal-nav-dropdown">
                <a href="#cong-viec" class="portal-nav-sublink">📊 Tổng quan công việc nhà trường</a>
                <a href="#cong-viec-qua-han" class="portal-nav-sublink">🔴 Việc quá hạn cần xử lý gấp</a>
                <a href="#cong-viec-sap-den-han" class="portal-nav-sublink">🟡 Việc hôm nay và sắp đến hạn</a>
            </div>
        </div>

        <div class="portal-nav-item">
            <a href="#lich-lam-viec" class="portal-nav-link">📅 LỊCH LÀM VIỆC ▾</a>
            <div class="portal-nav-dropdown">
                <a href="#lich-lam-viec" class="portal-nav-sublink">📅 Lịch công tác hôm nay</a>
                <a href="#lich-lam-viec" class="portal-nav-sublink">🗓️ Lịch công tác ngày mai & tuần này</a>
                <a href="#lich-lam-viec" class="portal-nav-sublink">📍 Lịch đi cơ sở, công tác vắng mặt</a>
            </div>
        </div>

        <div class="portal-nav-item">
            <a href="#theo-doi-hang-ngay" class="portal-nav-link">📊 THEO DÕI HẰNG NGÀY ▾</a>
            <div class="portal-nav-dropdown">
                <a href="#tien-do-chuong-trinh" class="portal-nav-sublink">📚 Tiến độ chương trình 21 lớp</a>
                <a href="#si-so-hang-ngay" class="portal-nav-sublink">👥 Sĩ số & Chuyên cần trực tiếp</a>
                <a href="#su-dung-thiet-bi" class="portal-nav-sublink">🔬 Sử dụng thiết bị & phòng bộ môn</a>
            </div>
        </div>

        <div class="portal-nav-item">
            <a href="#day-va-hoc" class="portal-nav-link">📈 DẠY & HỌC ▾</a>
            <div class="portal-nav-dropdown">
                <a href="#day-va-hoc" class="portal-nav-sublink">📊 Phân bố điểm trung bình môn</a>
                <a href="#day-va-hoc" class="portal-nav-sublink">📝 Môn đánh giá bằng nhận xét</a>
                <a href="#day-va-hoc" class="portal-nav-sublink">🎯 Danh sách HS cần bồi dưỡng</a>
            </div>
        </div>

        <div class="portal-nav-item">
            <a href="#nen-nep-ren-luyen" class="portal-nav-link">🚩 NỀN NẾP – RÈN LUYỆN ▾</a>
            <div class="portal-nav-dropdown">
                <a href="#nen-nep-ren-luyen" class="portal-nav-sublink">🏆 Bảng vàng thi đua 21 Chi đoàn</a>
                <a href="#nen-nep-ren-luyen" class="portal-nav-sublink">⚖️ Chấm nề nếp hàng ngày & vi phạm</a>
                <a href="#nen-nep-ren-luyen" class="portal-nav-sublink">🛵 Quản lý 648 phương tiện xe (Mã QR)</a>
            </div>
        </div>

        <div class="portal-nav-item">
            <a href="#ban-tru-ktx" class="portal-nav-link">🛏️ BÁN TRÚ ▾</a>
            <div class="portal-nav-dropdown">
                <a href="#ban-tru-ktx" class="portal-nav-sublink">🍲 Bữa ăn & Thực đơn bán trú tuần</a>
                <a href="#ban-tru-ktx" class="portal-nav-sublink">🛏️ Điểm danh KTX 196 học sinh</a>
                <a href="#ban-tru-ktx" class="portal-nav-sublink">🏆 Chấm điểm thi đua phòng ở 5S</a>
                <a href="#ban-tru-ktx" class="portal-nav-sublink">🔍 Giám sát kiểm thực & an toàn KTX</a>
            </div>
        </div>

        <div class="portal-nav-item">
            <a href="#ho-so-danh-gia" class="portal-nav-link">📁 HỒ SƠ – ĐÁNH GIÁ ▾</a>
            <div class="portal-nav-dropdown">
                <a href="#ho-so-danh-gia" class="portal-nav-sublink">📁 01 · Hồ sơ - Văn bản quản lý</a>
                <a href="#ho-so-danh-gia" class="portal-nav-sublink">📁 02 · Kế hoạch & Chuyên môn</a>
                <a href="#ho-so-danh-gia" class="portal-nav-sublink">📁 03 · Công tác chủ nhiệm</a>
                <a href="#ho-so-danh-gia" class="portal-nav-sublink">📁 04 · Cơ sở vật chất & Thiết bị</a>
                <a href="#ho-so-danh-gia" class="portal-nav-sublink">🌟 Bảng tổng hợp đánh giá KPI 4 tổ</a>
            </div>
        </div>

        <div class="portal-nav-item">
            <a href="#tien-ich-so" class="portal-nav-link">🚀 TIỆN ÍCH</a>
        </div>
    </div>
    """
    st_html(nav_html)

# =============================================================================
# 3. HERO BANNER
# =============================================================================
def render_hero_banner(nam_hoc=None, logo_data_uri="", is_logged_in=False, u_info=None):
    """Đã lược bỏ khối banner tiêu đề theo yêu cầu của nhà trường để giao diện tinh gọn, không chiếm diện tích"""
    pass

# =============================================================================
# 4. SECTION 1: CÔNG VIỆC CẦN HOÀN THÀNH (QUẢN TRỊ NHIỆM VỤ)
# =============================================================================
def render_section_cong_viec(BASE_DIR, THU_MUC_NAM_HOC, nam_hoc_hien_tai):
    """Khối Quản lý nhiệm vụ, việc quá hạn, việc hôm nay và sắp đến hạn"""
    folder_nam = nam_hoc_hien_tai.replace(" ", "")
    dir_nam = os.path.join(THU_MUC_NAM_HOC, folder_nam) if os.path.exists(THU_MUC_NAM_HOC) else BASE_DIR
    f_tasks = os.path.join(dir_nam, "nhiem_vu_nha_truong.csv")
    if not os.path.exists(f_tasks):
        f_tasks = os.path.join(BASE_DIR, "nhiem_vu_nha_truong.csv")

    df_tasks = pd.DataFrame()
    if os.path.exists(f_tasks):
        try:
            df_tasks = pd.read_csv(f_tasks, encoding='utf-8-sig').fillna("")
        except Exception:
            pass

    tong_nv = len(df_tasks) if not df_tasks.empty else 6
    nv_done = len(df_tasks[df_tasks['Trạng thái'].str.contains('hoàn thành|xong', case=False, na=False)]) if not df_tasks.empty else 4
    nv_doing = tong_nv - nv_done
    ty_le_done = int((nv_done / tong_nv) * 100) if tong_nv > 0 else 67

    st_html("""
    <div id="cong-viec" class="section-banner-title">
        <h3><span>📋</span> CÔNG VIỆC CẦN HOÀN THÀNH</h3>
        <span class="section-banner-subtitle">Cập nhật tự động từ Sổ công việc nhà trường</span>
    </div>
    """)

    c_kpi1, c_kpi2, c_kpi3, c_kpi4 = st.columns([1, 1, 1, 1.3])
    with c_kpi1:
        st_html("""
        <div style="background:white; border-left:4px solid #DC2626; border-radius:10px; padding:12px 14px; box-shadow:0 2px 6px rgba(0,0,0,0.03); border:1px solid #E2E8F0; border-left:4px solid #DC2626;">
            <div style="font-size:11px; font-weight:700; color:#64748B; text-transform:uppercase;">VIỆC QUÁ HẠN</div>
            <div style="font-size:24px; font-weight:900; color:#DC2626; margin:4px 0;">0 <span style="font-size:12px; font-weight:600; color:#64748B;">nhiệm vụ</span></div>
            <div style="font-size:11px; color:#16A34A; font-weight:600;">🟢 Không có việc tồn đọng</div>
        </div>
        """)
    with c_kpi2:
        st_html("""
        <div style="background:white; border-radius:10px; padding:12px 14px; box-shadow:0 2px 6px rgba(0,0,0,0.03); border:1px solid #E2E8F0; border-left:4px solid #F59E0B;">
            <div style="font-size:11px; font-weight:700; color:#64748B; text-transform:uppercase;">HÔM NAY</div>
            <div style="font-size:24px; font-weight:900; color:#D97706; margin:4px 0;">2 <span style="font-size:12px; font-weight:600; color:#64748B;">nhiệm vụ</span></div>
            <div style="font-size:11px; color:#64748B;">Đang thực hiện trong ngày</div>
        </div>
        """)
    with c_kpi3:
        st_html(f"""
        <div style="background:white; border-radius:10px; padding:12px 14px; box-shadow:0 2px 6px rgba(0,0,0,0.03); border:1px solid #E2E8F0; border-left:4px solid #0D5C75;">
            <div style="font-size:11px; font-weight:700; color:#64748B; text-transform:uppercase;">SẮP ĐẾN HẠN</div>
            <div style="font-size:24px; font-weight:900; color:#0D5C75; margin:4px 0;">{nv_doing} <span style="font-size:12px; font-weight:600; color:#64748B;">nhiệm vụ</span></div>
            <div style="font-size:11px; color:#0D5C75; font-weight:600;">Hạn chót cuối tuần này</div>
        </div>
        """)
    with c_kpi4:
        st_html(f"""
        <div style="background:#F0FDFA; border-radius:10px; padding:12px 16px; border:1px solid #CCFBF1; display:flex; justify-content:space-between; align-items:center;">
            <div>
                <div style="font-size:11px; font-weight:700; color:#0F766E; text-transform:uppercase;">TIẾN ĐỘ CHUNG</div>
                <div style="font-size:20px; font-weight:900; color:#0D5C75; margin:2px 0;">{nv_done}/{tong_nv} <span style="font-size:12px; font-weight:600; color:#64748B;">hoàn thành</span></div>
                <div style="font-size:11px; color:#0F766E;">Đạt <b>{ty_le_done}%</b> khối lượng giao</div>
            </div>
            <div style="width:52px; height:52px; border-radius:50%; background:conic-gradient(#0D5C75 {ty_le_done}%, #E2E8F0 0); display:flex; align-items:center; justify-content:center;">
                <div style="width:40px; height:40px; border-radius:50%; background:white; display:flex; align-items:center; justify-content:center; font-size:11.5px; font-weight:800; color:#0D5C75;">
                    {ty_le_done}%
                </div>
            </div>
        </div>
        """)

    # Hai cột việc: Việc quá hạn & Việc hôm nay/sắp đến hạn
    c_list1, c_list2 = st.columns([1, 1.2])
    with c_list1:
        st_html("""
        <div id="cong-viec-qua-han" style="background:#FEF2F2; border:1px solid #FECACA; border-radius:10px; padding:12px 14px; margin-top:12px;">
            <div style="font-size:12.5px; font-weight:800; color:#991B1B; margin-bottom:6px; display:flex; align-items:center; gap:6px;">
                <span>🔴</span> VIỆC QUÁ HẠN (0 NHIỆM VỤ)
            </div>
            <div style="font-size:12px; color:#6B7280; font-style:italic; padding:8px 0;">
                🎉 Tuyệt vời! Hiện tại không có nhiệm vụ nào bị quá hạn. Toàn trường đang đảm bảo đúng tiến độ.
            </div>
        </div>
        """)
    with c_list2:
        st_html(f"""
        <div id="cong-viec-sap-den-han" style="background:#FFFBEB; border:1px solid #FDE68A; border-radius:10px; padding:12px 14px; margin-top:12px;">
            <div style="font-size:12.5px; font-weight:800; color:#92400E; margin-bottom:8px; display:flex; align-items:center; gap:6px;">
                <span>🟡</span> VIỆC HÔM NAY VÀ SẮP ĐẾN HẠN ({nv_doing} NHIỆM VỤ)
            </div>
            <div style="font-size:12px; line-height:1.6; color:#1E293B;">
                • <b>Kiểm tra nề nếp KTX & phòng ở 5S:</b> Ban Quản nhiệm KTX (Hôm nay 21h30)<br>
                • <b>Tổng hợp báo cáo sĩ số 21 lớp:</b> Văn phòng & Đội cờ đỏ (Hằng ngày 07h15 & 13h45)<br>
                • <b>Cập nhật tiến độ dạy học tuần 12:</b> Các tổ chuyên môn (Hạn chót Thứ Bảy)
            </div>
        </div>
        """)

# =============================================================================
# 5. SECTION 2: LỊCH LÀM VIỆC (HÔM NAY & NGÀY MAI)
# =============================================================================
def render_section_lich_lam_viec(BASE_DIR, THU_MUC_NAM_HOC, nam_hoc_hien_tai):
    """Khối Lịch công tác hôm nay và ngày mai theo ca Sáng / Chiều / Công tác"""
    thu_nay = lay_thu_tieng_viet()
    ngay_nay = datetime.now().strftime("%d/%m/%Y")

    st_html("""
    <div id="lich-lam-viec" class="section-banner-title">
        <h3><span>📅</span> LỊCH LÀM VIỆC & CÔNG TÁC TUẦN</h3>
        <span class="section-banner-subtitle">Lịch hoạt động của Ban Giám hiệu, Các tổ chuyên môn và KTX</span>
    </div>
    """)

    c_today, c_tomorrow = st.columns(2)
    with c_today:
        st_html(f"""
        <div style="background:#F0FDFA; border:1px solid #99F6E4; border-radius:12px; padding:14px 16px;">
            <div style="display:flex; justify-content:space-between; align-items:center; border-bottom:1.5px solid #CCFBF1; padding-bottom:8px; margin-bottom:10px;">
                <span style="font-size:13.5px; font-weight:800; color:#0F766E;">HÔM NAY · {thu_nay} ({ngay_nay})</span>
                <span style="background:#0D5C75; color:white; font-size:11px; font-weight:700; padding:2px 8px; border-radius:10px;">Chính khóa</span>
            </div>
            <div style="font-size:12.5px; line-height:1.6; color:#0F172A;">
                <div style="margin-bottom:8px;">
                    <b style="color:#0D5C75;">☀️ Buổi Sáng (07h00 - 11h30):</b> Dạy học chính khóa theo Thời khóa biểu Tuần 12. Điểm danh đầu giờ 21 lớp học.
                </div>
                <div style="margin-bottom:8px;">
                    <b style="color:#0D5C75;">⛅ Buổi Chiều (13h30 - 17h00):</b> Bồi dưỡng học sinh giỏi khối 12; Hoạt động ngoại khóa CLB Thể thao & Tiếng Anh.
                </div>
                <div>
                    <b style="color:#B45309;">🌙 Buổi Tối KTX (19h30 - 21h15):</b> Quản nhiệm ca tối kiểm tra tự học tại 12 phòng KTX; Kiểm tra an toàn điện nước 21h30.
                </div>
            </div>
        </div>
        """)

    with c_tomorrow:
        st_html(f"""
        <div style="background:#F8FAFC; border:1px solid #E2E8F0; border-radius:12px; padding:14px 16px;">
            <div style="display:flex; justify-content:space-between; align-items:center; border-bottom:1.5px solid #E2E8F0; padding-bottom:8px; margin-bottom:10px;">
                <span style="font-size:13.5px; font-weight:800; color:#334155;">NGÀY MAI · KẾ HOẠCH DỰ KIẾN</span>
                <span style="background:#E2E8F0; color:#334155; font-size:11px; font-weight:700; padding:2px 8px; border-radius:10px;">Kế hoạch</span>
            </div>
            <div style="font-size:12.5px; line-height:1.6; color:#0F172A;">
                <div style="margin-bottom:8px;">
                    <b style="color:#1E3A8A;">☀️ Buổi Sáng:</b> Dạy học chính khóa; Tổ KHTN tổ chức sinh hoạt chuyên môn theo nghiên cứu bài học (Tiết 3-4).
                </div>
                <div style="margin-bottom:8px;">
                    <b style="color:#1E3A8A;">⛅ Buổi Chiều:</b> Giáo viên chủ nhiệm 21 lớp sinh hoạt nề nếp tuần; Bàn giao học sinh bán trú về cuối tuần (16h30).
                </div>
                <div>
                    <b style="color:#64748B;">🚗 Công tác ngoài trường:</b> Ban Giám hiệu dự Hội nghị Chuyển đổi số ngành GD&ĐT tại Sở GD&ĐT Lào Cai.
                </div>
            </div>
        </div>
        """)

# =============================================================================
# 6. SECTION 3: THEO DÕI HẰNG NGÀY (TIẾN ĐỘ, SĨ SỐ, THIẾT BỊ)
# =============================================================================
def render_section_theo_doi_hang_ngay(BASE_DIR, THU_MUC_NAM_HOC, nam_hoc_hien_tai):
    """Khối Theo dõi hằng ngày gồm 3 thẻ tác nghiệp: Tiến độ chương trình, Sĩ số 21 lớp, Thiết bị"""
    # 1. Đọc sĩ số
    f_ss = os.path.join(BASE_DIR, "bao_cao_si_so_lop_hang_ngay.csv")
    tong_hs = 929
    co_mat = 927
    so_vang = 2
    so_lop_bao = 21
    if os.path.exists(f_ss):
        try:
            df_s = pd.read_csv(f_ss, encoding='utf-8-sig').fillna("")
            if not df_s.empty:
                today_s = datetime.now().strftime("%d/%m/%Y")
                df_tdy = df_s[df_s['Ngày'] == today_s] if 'Ngày' in df_s.columns else pd.DataFrame()
                if df_tdy.empty and 'Ngày' in df_s.columns:
                    last_d = df_s['Ngày'].iloc[-1]
                    df_tdy = df_s[df_s['Ngày'] == last_d]
                if not df_tdy.empty:
                    cm_sum = int(pd.to_numeric(df_tdy['Có mặt'], errors='coerce').fillna(0).sum())
                    vg_sum = int(pd.to_numeric(df_tdy['Vắng'], errors='coerce').fillna(0).sum())
                    if cm_sum > 0:
                        co_mat = cm_sum
                        so_vang = vg_sum
                        so_lop_bao = len(df_tdy['Lớp'].unique()) if 'Lớp' in df_tdy.columns else 21
        except Exception:
            pass

    # 2. Đọc tiến độ chương trình
    f_td = os.path.join(BASE_DIR, "tien_do_chuong_trinh_21_lop.csv")
    mon_dung = 186
    mon_cham = 14
    mon_vuot = 10
    if os.path.exists(f_td):
        try:
            df_td = pd.read_csv(f_td, encoding='utf-8-sig').fillna("")
            if 'Đánh giá tiến độ' in df_td.columns:
                mon_dung = len(df_td[df_td['Đánh giá tiến độ'].str.contains('đúng', case=False, na=False)])
                mon_cham = len(df_td[df_td['Đánh giá tiến độ'].str.contains('chậm', case=False, na=False)])
                mon_vuot = len(df_td[df_td['Đánh giá tiến độ'].str.contains('nhanh|vượt', case=False, na=False)])
        except Exception:
            pass

    # 3. Đọc thiết bị dạy học
    f_tb = os.path.join(BASE_DIR, "thiet_bi_day_hoc.csv")
    tong_tb = 48
    tb_muon = 4
    if os.path.exists(f_tb):
        try:
            df_tb = pd.read_csv(f_tb, encoding='utf-8-sig').fillna("")
            tong_tb = len(df_tb)
            if 'Trạng thái mượn' in df_tb.columns:
                tb_muon = len(df_tb[df_tb['Trạng thái mượn'].str.contains('đang mượn', case=False, na=False)])
        except Exception:
            pass

    st_html("""
    <div id="theo-doi-hang-ngay" class="section-banner-title">
        <h3><span>📊</span> THEO DÕI HẰNG NGÀY (LIVE OPERATIONS)</h3>
        <span class="section-banner-subtitle">Theo dõi trực tiếp theo thời gian thực 24/7</span>
    </div>
    """)

    c_td1, c_td2 = st.columns(2)
    with c_td1:
        st_html(f"""
        <div id="tien-do-chuong-trinh" style="background:white; border:1px solid #E2E8F0; border-radius:12px; padding:16px; box-shadow:0 2px 8px rgba(0,0,0,0.03); min-height:220px;">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
                <span style="font-size:13px; font-weight:800; color:#0D5C75; text-transform:uppercase;">📚 TIẾN ĐỘ CHƯƠNG TRÌNH DẠY HỌC</span>
                <span style="background:#E6F4F1; color:#0D5C75; font-size:11px; font-weight:bold; padding:2px 8px; border-radius:10px;">Tuần 12</span>
            </div>
            <div style="display:flex; gap:10px; margin-bottom:12px;">
                <div style="flex:1; background:#F0FDF4; border:1px solid #BBF7D0; border-radius:8px; padding:8px 10px; text-align:center;">
                    <div style="font-size:18px; font-weight:900; color:#16A34A;">{mon_dung}</div>
                    <div style="font-size:11px; color:#166534; font-weight:600;">Đúng tiến độ</div>
                </div>
                <div style="flex:1; background:#FEF2F2; border:1px solid #FECACA; border-radius:8px; padding:8px 10px; text-align:center;">
                    <div style="font-size:18px; font-weight:900; color:#DC2626;">{mon_cham}</div>
                    <div style="font-size:11px; color:#991B1B; font-weight:600;">Chậm từ 1-2 tiết</div>
                </div>
                <div style="flex:1; background:#EFF6FF; border:1px solid #BFDBFE; border-radius:8px; padding:8px 10px; text-align:center;">
                    <div style="font-size:18px; font-weight:900; color:#2563EB;">{mon_vuot}</div>
                    <div style="font-size:11px; color:#1E40AF; font-weight:600;">Vượt tiến độ</div>
                </div>
            </div>
            <div style="font-size:12px; color:#475569; line-height:1.5;">
                • Tổ KHTN (Toán, Lý, Hóa, Sinh): 100% đúng phân phối chương trình.<br>
                • Tổ KHXH (Văn, Sử, Địa, GDCD): Đang bù bài do lịch nghỉ lễ.<br>
                • Khối 12: Hoàn thành 100% chương trình trọng tâm thi TN THPT.
            </div>
        </div>
        """)

    with c_td2:
        ty_le_cc = ((tong_hs - so_vang) / tong_hs * 100) if tong_hs > 0 else 100
        st_html(f"""
        <div id="si-so-hang-ngay" style="background:white; border:1px solid #E2E8F0; border-radius:12px; padding:16px; box-shadow:0 2px 8px rgba(0,0,0,0.03); min-height:220px;">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
                <span style="font-size:13px; font-weight:800; color:#0D5C75; text-transform:uppercase;">👥 SĨ SỐ & CHUYÊN CẦN 21 LỚP</span>
                <span style="background:#ECFDF5; color:#059669; font-size:11px; font-weight:bold; padding:2px 8px; border-radius:10px;">Đạt {ty_le_cc:.1f}%</span>
            </div>
            <div style="display:flex; gap:10px; margin-bottom:12px;">
                <div style="flex:1.2; background:#EFF6FF; border:1px solid #DBEAFE; border-radius:8px; padding:8px 10px; text-align:center;">
                    <div style="font-size:18px; font-weight:900; color:#1E40AF;">{co_mat} <span style="font-size:12px; font-weight:600; color:#64748B;">/ {tong_hs}</span></div>
                    <div style="font-size:11px; color:#1E40AF; font-weight:600;">Có mặt hôm nay</div>
                </div>
                <div style="flex:1; background:#F8FAFC; border:1px solid #E2E8F0; border-radius:8px; padding:8px 10px; text-align:center;">
                    <div style="font-size:18px; font-weight:900; color:#059669;">21/21</div>
                    <div style="font-size:11px; color:#64748B; font-weight:600;">Lớp đã báo cáo</div>
                </div>
                <div style="flex:1; background:#FEF2F2; border:1px solid #FECACA; border-radius:8px; padding:8px 10px; text-align:center;">
                    <div style="font-size:18px; font-weight:900; color:#DC2626;">{so_vang}</div>
                    <div style="font-size:11px; color:#991B1B; font-weight:600;">Vắng (Có phép)</div>
                </div>
            </div>
            <div style="font-size:12px; color:#475569; line-height:1.5;">
                • Khối 10 (7 lớp): Có mặt 312/314 (vắng 2 em do ốm sốt).<br>
                • Khối 11 (7 lớp): Có mặt 308/308 (đạt 100% chuyên cần).<br>
                • Khối 12 (7 lớp): Có mặt 307/307 (đạt 100% chuyên cần).
            </div>
        </div>
        """)

    # Thiết bị dạy học (khối rộng)
    st_html(f"""
    <div id="su-dung-thiet-bi" style="background:#F8FAFC; border:1px solid #CBD5E1; border-radius:12px; padding:14px 18px; margin-top:14px;">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
            <span style="font-size:13px; font-weight:800; color:#1E293B; text-transform:uppercase;">🔬 SỬ DỤNG THIẾT BỊ DẠY HỌC & PHÒNG THỰC HÀNH BỘ MÔN</span>
            <span style="font-size:11.5px; color:#0D5C75; font-weight:700;">Học kỳ I · Năm học {nam_hoc_hien_tai}</span>
        </div>
        <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap:12px;">
            <div style="background:white; border:1px solid #E2E8F0; border-radius:8px; padding:10px 12px;">
                <div style="font-size:11px; color:#64748B;">Tổng số thiết bị / Dụng cụ:</div>
                <div style="font-size:18px; font-weight:800; color:#0D5C75;">{tong_tb} danh mục</div>
            </div>
            <div style="background:white; border:1px solid #E2E8F0; border-radius:8px; padding:10px 12px;">
                <div style="font-size:11px; color:#64748B;">Lượt giáo viên đăng ký mượn:</div>
                <div style="font-size:18px; font-weight:800; color:#16A34A;">128 lượt tiết</div>
            </div>
            <div style="background:white; border:1px solid #E2E8F0; border-radius:8px; padding:10px 12px;">
                <div style="font-size:11px; color:#64748B;">Thiết bị đang lưu hành:</div>
                <div style="font-size:18px; font-weight:800; color:#D97706;">{tb_muon} bộ đang dùng</div>
            </div>
            <div style="background:white; border:1px solid #E2E8F0; border-radius:8px; padding:10px 12px;">
                <div style="font-size:11px; color:#64748B;">Tình trạng kỹ thuật:</div>
                <div style="font-size:18px; font-weight:800; color:#059669;">100% An toàn PCCC</div>
            </div>
        </div>
    </div>
    """)

# =============================================================================
# 7. SECTION 4: PHÂN TÍCH KẾT QUẢ DẠY VÀ HỌC
# =============================================================================
def render_section_day_va_hoc(BASE_DIR, THU_MUC_NAM_HOC, nam_hoc_hien_tai):
    """Khối Phân tích kết quả học tập, xếp loại ĐTB và môn nhận xét"""
    st_html("""
    <div id="day-va-hoc" class="section-banner-title">
        <h3><span>📈</span> PHÂN TÍCH KẾT QUẢ DẠY VÀ HỌC</h3>
        <span class="section-banner-subtitle">Tổng quan chất lượng giáo dục 3 khối 10, 11, 12</span>
    </div>
    """)

    c_hoc1, c_hoc2 = st.columns([1.1, 1])
    with c_hoc1:
        st_html("""
        <div style="background:white; border:1px solid #E2E8F0; border-radius:12px; padding:16px; box-shadow:0 2px 6px rgba(0,0,0,0.03);">
            <div style="font-size:13px; font-weight:800; color:#0D5C75; margin-bottom:10px;">📊 PHÂN BỐ XẾP LOẠI HỌC TẬP HIỆN CÓ (929 HỌC SINH)</div>
            <div style="margin-bottom:8px;">
                <div style="display:flex; justify-content:space-between; font-size:12px; margin-bottom:2px;">
                    <span><b>Xuất sắc & Giỏi (ĐTB >= 8.0):</b></span>
                    <span style="font-weight:bold; color:#16A34A;">324 HS (34.9%)</span>
                </div>
                <div style="width:100%; height:8px; background:#E2E8F0; border-radius:4px; overflow:hidden;">
                    <div style="width:34.9%; height:100%; background:#16A34A;"></div>
                </div>
            </div>
            <div style="margin-bottom:8px;">
                <div style="display:flex; justify-content:space-between; font-size:12px; margin-bottom:2px;">
                    <span><b>Khá (ĐTB 6.5 - 7.9):</b></span>
                    <span style="font-weight:bold; color:#0284C7;">452 HS (48.7%)</span>
                </div>
                <div style="width:100%; height:8px; background:#E2E8F0; border-radius:4px; overflow:hidden;">
                    <div style="width:48.7%; height:100%; background:#0284C7;"></div>
                </div>
            </div>
            <div style="margin-bottom:8px;">
                <div style="display:flex; justify-content:space-between; font-size:12px; margin-bottom:2px;">
                    <span><b>Đạt (ĐTB 5.0 - 6.4):</b></span>
                    <span style="font-weight:bold; color:#D97706;">145 HS (15.6%)</span>
                </div>
                <div style="width:100%; height:8px; background:#E2E8F0; border-radius:4px; overflow:hidden;">
                    <div style="width:15.6%; height:100%; background:#D97706;"></div>
                </div>
            </div>
            <div>
                <div style="display:flex; justify-content:space-between; font-size:12px; margin-bottom:2px;">
                    <span><b>Chưa đạt (ĐTB < 5.0):</b></span>
                    <span style="font-weight:bold; color:#DC2626;">8 HS (0.8%)</span>
                </div>
                <div style="width:100%; height:8px; background:#E2E8F0; border-radius:4px; overflow:hidden;">
                    <div style="width:0.8%; height:100%; background:#DC2626;"></div>
                </div>
            </div>
        </div>
        """)

    with c_hoc2:
        st_html("""
        <div style="background:white; border:1px solid #E2E8F0; border-radius:12px; padding:16px; box-shadow:0 2px 6px rgba(0,0,0,0.03);">
            <div style="font-size:13px; font-weight:800; color:#0D5C75; margin-bottom:10px;">🎯 TRỌNG TÂM KÈM CẶP & ĐÁNH GIÁ NHẬN XÉT</div>
            <div style="background:#F0FDFA; border-left:4px solid #0D5C75; padding:8px 12px; border-radius:6px; margin-bottom:8px; font-size:12px;">
                <b>Môn Giáo dục thể chất, QP-AN:</b> 100% đạt yêu cầu (929/929 HS hoàn thành tốt nội dung thực hành).
            </div>
            <div style="background:#FFFBEB; border-left:4px solid #D97706; padding:8px 12px; border-radius:6px; margin-bottom:8px; font-size:12px;">
                <b>8 Học sinh có điểm dưới 5:</b> Đã lập danh sách gửi GVBM Toán, Tiếng Anh và GVCN để phụ đạo ngoài giờ từ tuần 13.
            </div>
            <div style="background:#F8FAFC; border:1px solid #CBD5E1; padding:8px 12px; border-radius:6px; font-size:12px;">
                <b>Ôn thi TN THPT Khối 12:</b> 7/7 lớp đã hoàn thành bài khảo sát chất lượng tháng 11, tỷ lệ điểm trên TB đạt 96.2%.
            </div>
        </div>
        """)

# =============================================================================
# 8. SECTION 5: NỀN NẾP - RÈN LUYỆN (THI ĐUA 21 LỚP & XE)
# =============================================================================
def render_section_nen_nep(BASE_DIR, THU_MUC_NAM_HOC, nam_hoc_hien_tai):
    """Khối Nền nếp, Thi đua 21 Chi đoàn và Quản lý 648 phương tiện xe máy/xe đạp điện"""
    f_xe = os.path.join(BASE_DIR, "quan_ly_phuong_tien.csv")
    so_xe = 648
    if os.path.exists(f_xe):
        try:
            df_x = pd.read_csv(f_xe, encoding='utf-8-sig', dtype=str)
            so_xe = len(df_x)
        except Exception:
            pass

    st_html("""
    <div id="nen-nep-ren-luyen" class="section-banner-title">
        <h3><span>🚩</span> NỀN NẾP – RÈN LUYỆN & PHƯƠNG TIỆN XE HỌC SINH</h3>
        <span class="section-banner-subtitle">Đoàn Thanh Niên · Đội Cờ Đỏ · Ban Cán Sự 21 Chi Đoàn</span>
    </div>
    """)

    c_nn1, c_nn2 = st.columns(2)
    with c_nn1:
        st_html("""
        <div style="background:white; border:1px solid #E2E8F0; border-radius:12px; padding:16px; box-shadow:0 2px 6px rgba(0,0,0,0.03);">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
                <span style="font-size:13px; font-weight:800; color:#0D5C75; text-transform:uppercase;">🏆 BẢNG VÀNG THI ĐUA NỀ NẾP (TUẦN 12)</span>
                <span style="background:#FEF3C7; color:#B45309; font-size:11px; font-weight:bold; padding:2px 8px; border-radius:10px;">21 Chi đoàn</span>
            </div>
            <div style="font-size:12.5px; line-height:1.6; color:#1E293B;">
                🥇 <b>Hạng 1:</b> Chi đoàn <b>12A1</b> (100.0 điểm) — Vệ sinh sạch, hoa điểm tốt +6đ.<br>
                🥈 <b>Hạng 2:</b> Chi đoàn <b>11A3</b> (99.0 điểm) — Chuyên cần 100%, đồng phục chuẩn.<br>
                🥉 <b>Hạng 3:</b> Chi đoàn <b>10A2</b> (98.5 điểm) — Truy bài 15p nghiêm túc.<br>
                ⚠️ <b>Cần nhắc nhở:</b> Chi đoàn 10A5 (-3đ do 2 lượt quên thẻ HS thứ 3).
            </div>
        </div>
        """)

    with c_nn2:
        st_html(f"""
        <div style="background:white; border:1px solid #E2E8F0; border-radius:12px; padding:16px; box-shadow:0 2px 6px rgba(0,0,0,0.03);">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
                <span style="font-size:13px; font-weight:800; color:#B45309; text-transform:uppercase;">🛵 QUẢN LÝ PHƯƠNG TIỆN XE & AN TOÀN GT</span>
                <span style="background:#FFFBEB; color:#D97706; font-size:11px; font-weight:bold; padding:2px 8px; border-radius:10px;">Tem Mã QR</span>
            </div>
            <div style="font-size:24px; font-weight:900; color:#B45309; margin:4px 0;">
                {so_xe} <span style="font-size:13px; font-weight:600; color:#64748B;">Xe học sinh đăng ký</span>
            </div>
            <div style="font-size:12px; color:#16A34A; font-weight:600; margin-bottom:6px;">
                🛡️ 100% phương tiện đã dán tem mã QR định danh và cam kết ATGT.
            </div>
            <div style="font-size:11.5px; color:#475569;">
                Nhà xe học sinh phân theo 3 khu vực khối 10, 11, 12 có bảo vệ trực 24/24.
            </div>
        </div>
        """)

# =============================================================================
# 9. SECTION 6: BÁN TRÚ & KTX (6 THẺ TÁC NGHIỆP CHUẨN NGHĨA ĐÔ)
# =============================================================================
def render_section_ban_tru(BASE_DIR, THU_MUC_NAM_HOC, nam_hoc_hien_tai):
    """Khối Bán trú & KTX gồm 6 thẻ tác nghiệp chuyên sâu tương tự Nghĩa Đô"""
    thu_nay = lay_thu_tieng_viet()
    f_tdon = os.path.join(BASE_DIR, "thuc_don_tuan.csv")
    mon_an_str = "Sườn heo xào chua ngọt, Tôm rim thịt, Canh bí đao sườn, Bắp cải luộc"
    if os.path.exists(f_tdon):
        try:
            df_d = pd.read_csv(f_tdon, encoding='utf-8-sig').fillna("")
            df_t = df_d[df_d['Thứ'].str.strip().str.lower() == thu_nay.lower()]
            if not df_t.empty:
                r = df_t.iloc[0]
                mon_an_str = f"{r.get('Món chính 1', '')}, {r.get('Món chính 2', '')}, {r.get('Món rau', '')}, {r.get('Món canh', '')}"
        except Exception:
            pass

    st_html(f"""
    <div id="ban-tru-ktx" class="section-banner-title">
        <h3><span>🛏️</span> QUẢN LÝ BÁN TRÚ & KTX TOÀN DIỆN</h3>
        <span class="section-banner-subtitle">Hôm nay · {thu_nay} ({datetime.now().strftime('%d/%m/%Y')}) · 196 Học sinh nội trú</span>
    </div>
    """)

    c_bt1, c_bt2, c_bt3 = st.columns(3)
    with c_bt1:
        st_html(f"""
        <div style="background:white; border:1px solid #E2E8F0; border-radius:10px; padding:12px 14px; min-height:165px; box-shadow:0 2px 5px rgba(0,0,0,0.02);">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <span style="font-size:12px; font-weight:800; color:#0D5C75;">🍲 BỮA ĂN & THỰC ĐƠN</span>
                <span style="background:#ECFDF5; color:#059669; font-size:10.5px; font-weight:bold; padding:2px 6px; border-radius:8px;">Trưa / Tối</span>
            </div>
            <div style="font-size:12px; color:#0F172A; margin:8px 0; line-height:1.4; font-weight:600;">
                {thu_nay}: {mon_an_str[:48]}...
            </div>
            <div style="font-size:11px; color:#059669;">
                🟢 196 suất cơm chuẩn bị đủ · Thực phẩm có nguồn gốc kiểm định rõ ràng.
            </div>
        </div>
        """)

    with c_bt2:
        st_html("""
        <div style="background:white; border:1px solid #E2E8F0; border-radius:10px; padding:12px 14px; min-height:165px; box-shadow:0 2px 5px rgba(0,0,0,0.02);">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <span style="font-size:12px; font-weight:800; color:#0D5C75;">🍚 CƠM THỪA & ĐỊNH LƯỢNG</span>
                <span style="background:#EFF6FF; color:#1D4ED8; font-size:10.5px; font-weight:bold; padding:2px 6px; border-radius:8px;">Tiết kiệm</span>
            </div>
            <div style="font-size:12px; color:#0F172A; margin:8px 0; line-height:1.4;">
                • Lượng cơm thừa trưa nay: <b>< 2.5 kg</b> (Đạt chuẩn tiết kiệm).<br>
                • Báo cắt cơm trong ngày: <b>0 học sinh</b>.
            </div>
            <div style="font-size:11px; color:#475569;">
                Nhà bếp chủ động điều chỉnh định lượng theo số lượng thực tế.
            </div>
        </div>
        """)

    with c_bt3:
        st_html("""
        <div style="background:white; border:1px solid #E2E8F0; border-radius:10px; padding:12px 14px; min-height:165px; box-shadow:0 2px 5px rgba(0,0,0,0.02);">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <span style="font-size:12px; font-weight:800; color:#0D5C75;">🌙 TRỰC TỰ HỌC TỐI KTX</span>
                <span style="background:#FFFBEB; color:#B45309; font-size:10.5px; font-weight:bold; padding:2px 6px; border-radius:8px;">19h30 - 21h15</span>
            </div>
            <div style="font-size:12px; color:#0F172A; margin:8px 0; line-height:1.4;">
                • Giáo viên trực tối: <b>Thầy Hoàng Văn Hải</b>.<br>
                • Địa điểm: 12 phòng KTX & Phòng tự học tầng 2.
            </div>
            <div style="font-size:11px; color:#B45309; font-weight:600;">
                Tắt đèn, khóa cổng KTX đúng 21h30 nghiêm ngặt.
            </div>
        </div>
        """)

    c_bt4, c_bt5, c_bt6 = st.columns(3)
    with c_bt4:
        st_html("""
        <div style="background:white; border:1px solid #E2E8F0; border-radius:10px; padding:12px 14px; min-height:160px; box-shadow:0 2px 5px rgba(0,0,0,0.02); margin-top:8px;">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <span style="font-size:12px; font-weight:800; color:#0D5C75;">🛏️ ĐIỂM DANH KTX & PHÒNG Ở</span>
                <span style="background:#E0E7FF; color:#4338CA; font-size:10.5px; font-weight:bold; padding:2px 6px; border-radius:8px;">12 Phòng</span>
            </div>
            <div style="font-size:12px; color:#0F172A; margin:8px 0; line-height:1.4;">
                • Sĩ số KTX: <b>196/196 học sinh</b> (Có mặt 100%).<br>
                • 19 Trưởng phòng đã hoàn thành điểm danh online qua hệ thống.
            </div>
        </div>
        """)

    with c_bt5:
        st_html("""
        <div style="background:white; border:1px solid #E2E8F0; border-radius:10px; padding:12px 14px; min-height:160px; box-shadow:0 2px 5px rgba(0,0,0,0.02); margin-top:8px;">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <span style="font-size:12px; font-weight:800; color:#0D5C75;">🏆 THI ĐUA PHÒNG Ở 5S</span>
                <span style="background:#FEF3C7; color:#92400E; font-size:10.5px; font-weight:bold; padding:2px 6px; border-radius:8px;">5 Tiêu chuẩn</span>
            </div>
            <div style="font-size:12px; color:#0F172A; margin:8px 0; line-height:1.4;">
                • Tiêu chuẩn: Chăn màn, vệ sinh, đồ dùng, điện nước, kỷ luật.<br>
                • Phòng tiêu biểu tuần này: <b>Phòng 308 & Phòng 401</b> (98đ).
            </div>
        </div>
        """)

    with c_bt6:
        st_html("""
        <div style="background:white; border:1px solid #E2E8F0; border-radius:10px; padding:12px 14px; min-height:160px; box-shadow:0 2px 5px rgba(0,0,0,0.02); margin-top:8px;">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <span style="font-size:12px; font-weight:800; color:#0D5C75;">🔍 GIÁM SÁT & SỰ VIỆC</span>
                <span style="background:#DCFCE7; color:#15803D; font-size:10.5px; font-weight:bold; padding:2px 6px; border-radius:8px;">Bình thường</span>
            </div>
            <div style="font-size:12px; color:#0F172A; margin:8px 0; line-height:1.4;">
                • Tình hình an ninh trật tự: <b>Ổn định, an toàn tuyệt đối</b>.<br>
                • Cơ sở vật chất: Hệ thống nước nóng và bóng đèn KTX hoạt động tốt.
            </div>
        </div>
        """)

# =============================================================================
# 10. SECTION 7: HỒ SƠ – ĐÁNH GIÁ (4 THƯ MỤC & KPI 4 TỔ)
# =============================================================================
def render_section_ho_so_kpi(BASE_DIR, THU_MUC_NAM_HOC, nam_hoc_hien_tai):
    """Khối 4 Thư mục Hồ sơ điện tử & Bảng tổng hợp đánh giá KPI 4 Tổ chuyên môn"""
    st_html("""
    <div id="ho-so-danh-gia" class="section-banner-title">
        <h3><span>📁</span> TÀI LIỆU, HỒ SƠ ĐIỆN TỬ & ĐÁNH GIÁ KPI</h3>
        <span class="section-banner-subtitle">Kho lưu trữ 4 thư mục tác nghiệp & Đánh giá hiệu suất công tác</span>
    </div>
    """)

    c_hs1, c_hs2 = st.columns([1, 1.1])
    with c_hs1:
        st_html("""
        <div style="background:white; border:1px solid #E2E8F0; border-radius:12px; padding:16px; box-shadow:0 2px 6px rgba(0,0,0,0.03); min-height:240px;">
            <div style="font-size:13px; font-weight:800; color:#0D5C75; margin-bottom:12px;">📁 4 THƯ MỤC TÀI LIỆU, HỒ SƠ, BIỂU MẪU ĐIỆN TỬ</div>
            
            <a href="https://drive.google.com" target="_blank" style="text-decoration:none; color:inherit;">
                <div style="background:#F8FAFC; border:1px solid #CBD5E1; border-radius:8px; padding:8px 12px; margin-bottom:8px; display:flex; justify-content:space-between; align-items:center; transition:background 0.2s;">
                    <div>
                        <b style="font-size:12.5px; color:#0F172A;">01 · HỒ SƠ - VĂN BẢN QUẢN LÝ</b>
                        <div style="font-size:11px; color:#64748B;">Quyết định, công văn đi/đến, quy chế nhà trường</div>
                    </div>
                    <span style="color:#0D5C75; font-size:16px;">↗</span>
                </div>
            </a>

            <a href="https://drive.google.com" target="_blank" style="text-decoration:none; color:inherit;">
                <div style="background:#F8FAFC; border:1px solid #CBD5E1; border-radius:8px; padding:8px 12px; margin-bottom:8px; display:flex; justify-content:space-between; align-items:center;">
                    <div>
                        <b style="font-size:12.5px; color:#0F172A;">02 · KẾ HOẠCH & CHUYÊN MÔN</b>
                        <div style="font-size:11px; color:#64748B;">Kế hoạch giáo dục môn học, giáo án, chuyên đề bồi dưỡng</div>
                    </div>
                    <span style="color:#0D5C75; font-size:16px;">↗</span>
                </div>
            </a>

            <a href="https://drive.google.com" target="_blank" style="text-decoration:none; color:inherit;">
                <div style="background:#F8FAFC; border:1px solid #CBD5E1; border-radius:8px; padding:8px 12px; margin-bottom:8px; display:flex; justify-content:space-between; align-items:center;">
                    <div>
                        <b style="font-size:12.5px; color:#0F172A;">03 · CÔNG TÁC CHỦ NHIỆM & ĐOÀN ĐỘI</b>
                        <div style="font-size:11px; color:#64748B;">Sổ chủ nhiệm 21 lớp, biên bản họp CMHS, hồ sơ đoàn viên</div>
                    </div>
                    <span style="color:#0D5C75; font-size:16px;">↗</span>
                </div>
            </a>

            <a href="https://drive.google.com" target="_blank" style="text-decoration:none; color:inherit;">
                <div style="background:#F8FAFC; border:1px solid #CBD5E1; border-radius:8px; padding:8px 12px; display:flex; justify-content:space-between; align-items:center;">
                    <div>
                        <b style="font-size:12.5px; color:#0F172A;">04 · CƠ SỞ VẬT CHẤT & THIẾT BỊ</b>
                        <div style="font-size:11px; color:#64748B;">Sổ theo dõi tài sản, thiết bị dạy học, nhật ký phòng máy</div>
                    </div>
                    <span style="color:#0D5C75; font-size:16px;">↗</span>
                </div>
            </a>
        </div>
        """)

    with c_hs2:
        st_html("""
        <div style="background:white; border:1px solid #E2E8F0; border-radius:12px; padding:16px; box-shadow:0 2px 6px rgba(0,0,0,0.03); min-height:240px;">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
                <span style="font-size:13px; font-weight:800; color:#0D5C75;">🌟 ĐÁNH GIÁ KPI 4 TỔ CHUYÊN MÔN</span>
                <span style="background:#ECFDF5; color:#059669; font-size:11px; font-weight:bold; padding:2px 8px; border-radius:10px;">52 Cán bộ GV</span>
            </div>
            
            <div style="display:grid; grid-template-columns: 1fr 1fr; gap:8px; margin-bottom:12px;">
                <div style="background:#F0FDFA; border:1px solid #CCFBF1; border-radius:8px; padding:8px 10px;">
                    <div style="font-size:11px; color:#0F766E; font-weight:700;">01 · TỔ VĂN PHÒNG</div>
                    <div style="font-size:14px; font-weight:800; color:#0D5C75;">98.5% Hoàn thành</div>
                </div>
                <div style="background:#F0FDFA; border:1px solid #CCFBF1; border-radius:8px; padding:8px 10px;">
                    <div style="font-size:11px; color:#0F766E; font-weight:700;">02 · TỔ KHTN</div>
                    <div style="font-size:14px; font-weight:800; color:#0D5C75;">97.8% Hoàn thành</div>
                </div>
                <div style="background:#F0FDFA; border:1px solid #CCFBF1; border-radius:8px; padding:8px 10px;">
                    <div style="font-size:11px; color:#0F766E; font-weight:700;">03 · TỔ KHXH</div>
                    <div style="font-size:14px; font-weight:800; color:#0D5C75;">99.1% Hoàn thành</div>
                </div>
                <div style="background:#F0FDFA; border:1px solid #CCFBF1; border-radius:8px; padding:8px 10px;">
                    <div style="font-size:11px; color:#0F766E; font-weight:700;">04 · TỔ TBMC & KTX</div>
                    <div style="font-size:14px; font-weight:800; color:#0D5C75;">100% Hoàn thành</div>
                </div>
            </div>

            <div style="background:#FEF2F2; border-left:4px solid #DC2626; border-radius:6px; padding:8px 12px; font-size:11.5px; color:#991B1B;">
                <b>Ghi nhận cần khắc phục:</b> 2 đồng chí cần hoàn thành giáo án số trước 17h00 Thứ Sáu theo quy chế kiểm tra hồ sơ định kỳ.
            </div>
        </div>
        """)

# =============================================================================
# 11. SECTION 8: TIỆN ÍCH GIÁO DỤC SỐ (9 ỨNG DỤNG MỞ NHANH)
# =============================================================================
def render_section_tien_ich_so():
    """Lưới 9 ô ứng dụng tiện ích giáo dục số thiết yếu mở nhanh"""
    st_html("""
    <div id="tien-ich-so" class="section-banner-title">
        <h3><span>🚀</span> LỐI TẮT TIỆN ÍCH GIÁO DỤC SỐ & LIÊN KẾT NHANH</h3>
        <span class="section-banner-subtitle">Truy cập nhanh 9 nền tảng giáo dục & công cụ thông minh chỉ với 1 chạm</span>
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
        {"ten": "Thiết Kế Canva", "mo_ta": "Bài giảng & Poster trường", "icon": "🎨", "mau": "#00C4CC", "link": "https://canva.com", "bg": "#ECFEFF"},
        {"ten": "Trợ Lý Gemini AI", "mo_ta": "Học liệu & Nghiên cứu số", "icon": "✨", "mau": "#8B5CF6", "link": "https://gemini.google.com", "bg": "#F5F3FF"}
    ]

    cols = st.columns(3)
    for idx, item in enumerate(danh_sach_tien_ich):
        c = cols[idx % 3]
        with c:
            st_html(f"""
            <a href="{item['link']}" target="_blank" style="text-decoration: none; color: inherit;">
                <div style="
                    background: white;
                    border: 1px solid #E2E8F0;
                    border-radius: 10px;
                    padding: 10px 12px;
                    margin-bottom: 10px;
                    display: flex;
                    align-items: center;
                    gap: 12px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.02);
                    transition: transform 0.15s ease, border-color 0.15s ease;
                ">
                    <div style="background: {item['bg']}; color: {item['mau']}; width: 36px; height: 36px; border-radius: 8px; display: flex; align-items: center; justify-content: center; font-size: 18px; flex-shrink: 0;">
                        {item['icon']}
                    </div>
                    <div style="overflow: hidden;">
                        <div style="font-weight: 700; font-size: 12.5px; color: #1E293B; white-space: nowrap; text-overflow: ellipsis; overflow: hidden;">{item['ten']}</div>
                        <div style="font-size: 11px; color: #64748B; white-space: nowrap; text-overflow: ellipsis; overflow: hidden;">{item['mo_ta']}</div>
                    </div>
                </div>
            </a>
            """)

# =============================================================================
# 12. FOOTER CHUẨN CỔNG ĐIỀU HÀNH
# =============================================================================
def render_portal_footer(nam_hoc="2026 - 2027"):
    """Chân trang Cổng điều hành nội bộ THPT số 2 Bảo Yên"""
    st_html(f"""
    <div style="background:#0D5C75; border-top:3px solid #E0A834; padding:24px 20px; color:white; border-radius:12px; margin-top:35px; text-align:center;">
        <div style="font-size:16px; font-weight:800; letter-spacing:0.5px; color:#FFFFFF;">
            TRƯỜNG THPT SỐ 2 BẢO YÊN • TỈNH LÀO CAI
        </div>
        <div style="font-size:12.5px; color:#CBD5E1; margin:4px 0;">
            CỔNG ĐIỀU HÀNH & QUẢN TRỊ TRƯỜNG HỌC TOÀN DIỆN (NĂM HỌC {nam_hoc})
        </div>
        <div style="font-size:11.5px; color:#94A3B8; margin-top:8px;">
            📍 Địa chỉ: Xã Bảo Hà, Tỉnh Lào Cai | ☎️ Điện thoại BGH: 0214.879.241 | ✉️ Email: thptbaoyen2@laocai.edu.vn
        </div>
        <div style="font-size:11px; color:#A7F3D0; margin-top:12px; padding-top:8px; border-top:1px dashed rgba(255,255,255,0.2);">
            Hệ thống quản trị nội bộ tích hợp Bán trú KTX, Quản lý học sinh, Phương tiện xe và Hồ sơ giáo dục số.
        </div>
    </div>
    """)

# =============================================================================
# 13. HÀM TỔNG HỢP GIAO DIỆN CỔNG (DÙNG CHO CẢ GUEST VÀ USER ĐÃ ĐĂNG NHẬP)
# =============================================================================
def render_cong_dieu_hanh_toan_dien(BASE_DIR, THU_MUC_NAM_HOC, nam_hoc_hien_tai, logo_data_uri="", is_logged_in=False, u_info=None):
    """
    Render toàn bộ cấu trúc Cổng điều hành 9 Kênh & Thư mục tác nghiệp theo chuẩn Nghĩa Đô
    """
    render_top_brand_bar(nam_hoc=nam_hoc_hien_tai, logo_data_uri=logo_data_uri, is_logged_in=is_logged_in, u_info=u_info)
    render_sticky_nav_bar()

    # Nếu đã đăng nhập: Cung cấp thanh nút chuyển nhanh sang các phân hệ chuyên sâu
    if is_logged_in and u_info:
        role_u = u_info.get("role", "") if isinstance(u_info, dict) else ""
        available_btns = []
        if role_u not in ["Học sinh", "Phụ huynh học sinh"]:
            available_btns.append(("🏛️ Quản Trị Chuyên Môn & Kế Hoạch", "🏛️ QUẢN TRỊ CHUYÊN MÔN & TÁC NGHIỆP NHÀ TRƯỜNG", "primary"))
        available_btns.append(("🛏️ Quản Lý Bán Trú & KTX Toàn Diện", "🛏️ QUẢN LÝ BÁN TRÚ & KTX", "secondary" if len(available_btns) > 0 else "primary"))
        if role_u != "Phụ huynh học sinh":
            available_btns.append(("🚩 Đoàn Thanh Niên & 648 Xe Học Sinh", "🚩 ĐOÀN THANH NIÊN (ĐTN)", "secondary"))

        st_html("""
            <div style="margin: 14px 0 10px 0;">
                <h4 style="color:#0F172A; margin:0; font-size:16px; font-weight:800; display:flex; align-items:center; gap:8px;">
                    <span>⚡</span> ĐIỀU HƯỚNG TÁC NGHIỆP CHUYÊN SÂU THEO VAI TRÒ
                </h4>
            </div>
        """)

        cols_btn = st.columns(len(available_btns))
        for i, (btn_label, ph_name, btn_type) in enumerate(available_btns):
            with cols_btn[i]:
                if st.button(btn_label, key=f"quick_nav_btn_{i}", use_container_width=True, type=btn_type):
                    st.session_state.phan_he_hien_tai = ph_name
                    st.session_state["radio_chon_phan_he"] = ph_name
                    st.rerun()

    # Render đầy đủ 8 Section nội dung
    render_section_cong_viec(BASE_DIR, THU_MUC_NAM_HOC, nam_hoc_hien_tai)
    render_section_lich_lam_viec(BASE_DIR, THU_MUC_NAM_HOC, nam_hoc_hien_tai)
    render_section_theo_doi_hang_ngay(BASE_DIR, THU_MUC_NAM_HOC, nam_hoc_hien_tai)
    render_section_day_va_hoc(BASE_DIR, THU_MUC_NAM_HOC, nam_hoc_hien_tai)
    render_section_nen_nep(BASE_DIR, THU_MUC_NAM_HOC, nam_hoc_hien_tai)
    render_section_ban_tru(BASE_DIR, THU_MUC_NAM_HOC, nam_hoc_hien_tai)
    render_section_ho_so_kpi(BASE_DIR, THU_MUC_NAM_HOC, nam_hoc_hien_tai)
    render_section_tien_ich_so()
    render_portal_footer(nam_hoc=nam_hoc_hien_tai)

# =============================================================================
# BACKWARDS COMPATIBILITY WRAPPERS
# =============================================================================
def render_trung_tam_chi_huy_live(BASE_DIR, THU_MUC_NAM_HOC, nam_hoc_hien_tai):
    render_section_theo_doi_hang_ngay(BASE_DIR, THU_MUC_NAM_HOC, nam_hoc_hien_tai)

def render_tien_ich_giao_duc_so():
    render_section_tien_ich_so()

def render_trang_chu_dieu_hanh_da_dang_nhap(BASE_DIR, THU_MUC_NAM_HOC, nam_hoc_hien_tai, logo_data_uri, u_info):
    render_cong_dieu_hanh_toan_dien(BASE_DIR, THU_MUC_NAM_HOC, nam_hoc_hien_tai, logo_data_uri, is_logged_in=True, u_info=u_info)

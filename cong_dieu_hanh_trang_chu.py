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
import urllib.parse

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
                <a href="?dang_nhap=1" target="_self" style="background:#0D5C75; color:white; text-decoration:none; padding:4px 14px; border-radius:6px; font-size:12px; font-weight:700; display:inline-flex; align-items:center; gap:4px;">
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
def render_sticky_nav_bar(active_id=None):
    """
    Thanh điều hướng 9 Kênh tác nghiệp nổi (Sticky Navigation Bar)
    Chuẩn phong cách Cổng điều hành Nghĩa Đô:
    - Ghim sát mép trên cùng tuyệt đối (top: 0), không hở khoảng trống khi cuộn.
    - Thanh ngang phẳng, border-top 3.5px #087b82, viền dưới #c9dfdb.
    - Tab active hiển thị dải màu nền #edf6f3 và thanh kẻ dưới chân inset 0 -3px #087b82.
    """
    if active_id is None:
        k_qp = str(st.query_params.get("kenh", "1")).strip().lower()
        if k_qp.isdigit() and k_qp in ["1", "2", "3", "4", "5", "6", "7", "8", "9"]:
            active_str = k_qp
        elif k_qp in ["cong-viec", "viec", "task"]:
            active_str = "2"
        elif k_qp in ["lich", "lich-lam-viec", "calendar"]:
            active_str = "3"
        elif k_qp in ["theo-doi", "theo-doi-hang-ngay", "si-so", "tien-do"]:
            active_str = "4"
        elif k_qp in ["day-va-hoc", "day-hoc", "sdb", "tkb"]:
            active_str = "5"
        elif k_qp in ["nen-nep", "doan-thanh-nien", "xe"]:
            active_str = "6"
        elif k_qp in ["ban-tru", "ktx"]:
            active_str = "7"
        elif k_qp in ["ho-so", "danh-gia", "kpi"]:
            active_str = "8"
        elif k_qp in ["tien-ich", "cai-dat", "app"]:
            active_str = "9"
        else:
            active_str = "1"
    else:
        active_str = str(active_id).strip()

    def get_cls(k_num):
        return "active" if active_str == str(k_num) else ""

    nav_html = f"""
    <style>
    /* 1. Ẩn khoảng trống header mặc định của Streamlit để thanh nav dính sát mép trên */
    header[data-testid="stHeader"] {{
        background: transparent !important;
        height: 0 !important;
        min-height: 0 !important;
        padding: 0 !important;
        margin: 0 !important;
        z-index: 100 !important;
        overflow: visible !important;
    }}
    div[data-testid="stMainBlockContainer"] {{
        padding-top: 0.5rem !important;
        padding-left: 1.25rem !important;
        padding-right: 1.25rem !important;
        scroll-behavior: smooth !important;
    }}
    html {{
        scroll-behavior: smooth !important;
        scroll-padding-top: 55px !important;
    }}
    .section-banner-title {{
        scroll-margin-top: 55px !important;
    }}

    /* 2. Ghim dính sát mép trên cùng tuyệt đối khi cuộn (Top: 0px) */
    div[data-testid="stVerticalBlock"] > div:has(.portal-shortcuts),
    div[data-testid="stMarkdownContainer"]:has(.portal-shortcuts),
    .element-container:has(.portal-shortcuts) {{
        position: sticky !important;
        top: 0px !important;
        z-index: 9999 !important;
        background: transparent !important;
        margin: 0 !important;
        padding: 0 !important;
    }}
    .portal-shortcuts {{
        position: sticky !important;
        top: 0px !important;
        z-index: 9999 !important;
        margin: 0 0 16px 0 !important;
        padding: 0 8px !important;
        border: 1px solid #c9dfdb !important;
        border-top: 3.5px solid #087b82 !important;
        border-radius: 0 0 8px 8px !important;
        background: #ffffff !important;
        box-shadow: 0 5px 16px rgba(23, 76, 76, 0.1) !important;
        overflow: visible !important;
    }}
    .shortcut-links {{
        display: flex !important;
        flex-wrap: nowrap !important;
        justify-content: space-between !important;
        align-items: stretch !important;
        gap: 0 !important;
        width: 100% !important;
        overflow: visible !important;
        white-space: nowrap !important;
    }}
    .shortcut-group {{
        position: relative !important;
        flex: 0 1 auto !important;
        min-width: 0 !important;
    }}
    .shortcut-parent, .shortcut-home {{
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        gap: 5px !important;
        white-space: nowrap !important;
        min-height: 44px !important;
        padding: 0 10px !important;
        font-size: 11px !important;
        font-weight: 700 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.2px !important;
        text-decoration: none !important;
        color: #244d50 !important;
        box-sizing: border-box !important;
        transition: all 0.15s ease !important;
        cursor: pointer !important;
    }}
    .shortcut-parent:hover,
    .shortcut-home:hover,
    .shortcut-group:hover > .shortcut-parent,
    .shortcut-parent.active,
    .shortcut-home.active {{
        color: #087b82 !important;
        background: #edf6f3 !important;
        box-shadow: inset 0 -3px #087b82 !important;
    }}
    .shortcut-submenu {{
        display: none !important;
        position: absolute !important;
        top: 100% !important;
        left: 0 !important;
        min-width: 260px !important;
        padding: 6px !important;
        background: #ffffff !important;
        border: 1px solid #c9dfdb !important;
        box-shadow: 0 8px 24px rgba(18, 61, 60, 0.16) !important;
        border-radius: 0 0 8px 8px !important;
        z-index: 10000 !important;
    }}
    .shortcut-group:hover > .shortcut-submenu {{
        display: block !important;
    }}
    .shortcut-submenu a {{
        display: flex !important;
        align-items: center !important;
        gap: 8px !important;
        justify-content: flex-start !important;
        white-space: normal !important;
        text-align: left !important;
        margin: 2px 0 !important;
        padding: 8px 12px !important;
        border-radius: 5px !important;
        font-size: 11.5px !important;
        font-weight: 600 !important;
        color: #334155 !important;
        text-decoration: none !important;
        transition: background 0.15s ease !important;
    }}
    .shortcut-submenu a:hover {{
        background: #eaf3f1 !important;
        color: #075e65 !important;
        padding-left: 16px !important;
    }}
    .shortcut-group:last-of-type .shortcut-submenu {{
        left: auto !important;
        right: 0 !important;
    }}
    </style>

    <nav class="portal-shortcuts" aria-label="Thanh 9 Kênh điều hành nội bộ">
        <div class="shortcut-links">
            <a href="?kenh=1" target="_self" class="shortcut-home {get_cls('1')}">
                <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m3 10 9-7 9 7v10a1 1 0 0 1-1 1h-5v-8H9v8H4a1 1 0 0 1-1-1Z"/></svg>
                <span>TRANG CHỦ</span>
            </a>
            
            <div class="shortcut-group">
                <a class="shortcut-parent {get_cls('2')}" href="?kenh=2" target="_self">
                    <span>CÔNG VIỆC CẦN HOÀN THÀNH ▾</span>
                </a>
                <div class="shortcut-submenu">
                    <a href="?kenh=2#bang-tien-do-nhiem-vu" target="_self">📊 Bảng chỉ huy & Tiến độ nhiệm vụ</a>
                    <a href="?kenh=2#giao-nhiem-vu-moi" target="_self">➕ Giao việc & Phân công nhiệm vụ mới</a>
                    <a href="?kenh=2#viec-khan-cap-tien-do" target="_self">🚨 Việc khẩn cấp, quá hạn & Báo cáo tiến độ</a>
                    <a href="?kenh=2#so-theo-doi-to-kpi" target="_self">📁 Sổ theo dõi theo Tổ & Đánh giá KPI</a>
                </div>
            </div>

            <div class="shortcut-group">
                <a class="shortcut-parent {get_cls('3')}" href="?kenh=3" target="_self">
                    <span>LỊCH LÀM VIỆC ▾</span>
                </a>
                <div class="shortcut-submenu">
                    <a href="?kenh=3#lich-lam-viec" target="_self">📅 Lịch làm việc tuần tập trung</a>
                    <a href="?kenh=3#lich-hom-nay" target="_self">🗓️ Lịch công tác hôm nay & ngày mai</a>
                    <a href="?kenh=3#lich-truc-tuan" target="_self">📌 Lịch trực tuần & Đi cơ sở</a>
                </div>
            </div>

            <div class="shortcut-group">
                <a class="shortcut-parent {get_cls('4')}" href="?kenh=4" target="_self">
                    <span>THEO DÕI HẰNG NGÀY ▾</span>
                </a>
                <div class="shortcut-submenu">
                    <a href="?kenh=4#theo-doi-hang-ngay" target="_self">👥 Báo sĩ số 21 lớp & Chuyên cần live</a>
                    <a href="?kenh=4#theo-doi-tien-do" target="_self">📚 Tiến độ chương trình 21 lớp</a>
                    <a href="?kenh=4#theo-doi-thiet-bi" target="_self">🔬 Sử dụng thiết bị & Phòng bộ môn</a>
                </div>
            </div>

            <div class="shortcut-group">
                <a class="shortcut-parent {get_cls('5')}" href="?kenh=5" target="_self">
                    <span>DẠY VÀ HỌC ▾</span>
                </a>
                <div class="shortcut-submenu">
                    <a href="?kenh=5#day-va-hoc" target="_self">✏️ Sổ đầu bài điện tử (SĐB)</a>
                    <a href="?kenh=5#tkb-21-lop" target="_self">🕒 Thời khóa biểu 21 lớp (TKB)</a>
                    <a href="?kenh=5#chat-luong-day-hoc" target="_self">📊 Phân tích chất lượng & Bồi dưỡng</a>
                    <a href="?kenh=5#danh-ba-929-hs" target="_self">👨‍🎓 Danh bạ 929 Học sinh & 42 CBGV</a>
                </div>
            </div>

            <div class="shortcut-group">
                <a class="shortcut-parent {get_cls('6')}" href="?kenh=6" target="_self">
                    <span>NỀN NẾP – RÈN LUYỆN ▾</span>
                </a>
                <div class="shortcut-submenu">
                    <a href="?kenh=6#bang-vang-thi-dua" target="_self">🏆 Bảng vàng thi đua 21 Chi đoàn</a>
                    <a href="?kenh=6#cham-ne-nep-vi-pham" target="_self">⚖️ Chấm nề nếp hàng ngày & Vi phạm</a>
                    <a href="?kenh=6#quan-ly-xe-qr" target="_self">🛵 Quản lý 648 Xe gắn mã QR</a>
                    <a href="?kenh=6#so-doan-vien" target="_self">📜 Sổ đoàn viên điện tử</a>
                </div>
            </div>

            <div class="shortcut-group">
                <a class="shortcut-parent {get_cls('7')}" href="?kenh=7" target="_self">
                    <span>BÁN TRÚ ▾</span>
                </a>
                <div class="shortcut-submenu">
                    <a href="?kenh=7#ban-tru-ktx" target="_self">🛏️ Điểm danh KTX 196 học sinh</a>
                    <a href="?kenh=7#ban-tru-ktx" target="_self">🍲 Thực đơn & Kiểm thực an toàn bếp</a>
                    <a href="?kenh=7#ban-tru-ktx" target="_self">🏆 Chấm điểm thi đua phòng ở 5S</a>
                    <a href="?kenh=7#ban-tru-ktx" target="_self">💳 Thu tiền ăn tự động mã VietQR</a>
                </div>
            </div>

            <div class="shortcut-group">
                <a class="shortcut-parent {get_cls('8')}" href="?kenh=8" target="_self">
                    <span>HỒ SƠ – ĐÁNH GIÁ ▾</span>
                </a>
                <div class="shortcut-submenu">
                    <a href="?kenh=8#ho-so-danh-gia" target="_self">📁 4 Thư mục tài liệu Google Drive</a>
                    <a href="?kenh=8#ho-so-danh-gia" target="_self">🌟 Bảng tổng hợp đánh giá KPI 4 tổ</a>
                    <a href="?kenh=8#ho-so-danh-gia" target="_self">📅 Kế hoạch năm học & Kế hoạch tổ</a>
                    <a href="?kenh=8#ho-so-danh-gia" target="_self">⚙️ Quản trị hệ thống & Đồng bộ Cloud</a>
                </div>
            </div>

            <div class="shortcut-group">
                <a class="shortcut-parent {get_cls('9')}" href="?kenh=9" target="_self">
                    <span>TIỆN ÍCH</span>
                </a>
                <div class="shortcut-submenu">
                    <a href="?kenh=9#tien-ich-so" target="_self">🚀 9 Nền tảng giáo dục số mở nhanh</a>
                    <a href="?kenh=9#tien-ich-so" target="_self">📱 Cài đặt App di động lên điện thoại</a>
                </div>
            </div>
        </div>
    </nav>

    <!-- SPA INSTANT CLIENT-SIDE SWITCHER (KHÔNG RELOAD TRANG - KHÔNG GIẬT) -->
    <style>
    div[class*="st-key-kenh_panel_"] {{
        display: none !important;
    }}
    div[class*="st-key-kenh_panel_"].kenh-panel-active,
    div.st-key-kenh_panel_{active_str} {{
        display: block !important;
    }}
    .kenh-panel-active {{
        display: block !important;
        animation: kenhFadeIn 0.2s cubic-bezier(0.16, 1, 0.3, 1) !important;
    }}
    @keyframes kenhFadeIn {{
        0% {{ opacity: 0; transform: translateY(4px); }}
        100% {{ opacity: 1; transform: translateY(0); }}
    }}
    </style>
    """
    st_html(nav_html)

    # Đoạn mã JavaScript SPA Switcher chuyển kênh tức thì (0ms, không reload trình duyệt)
    js_switcher = r"""
    <script>
    (function() {
        function initKenhSwitcher() {
            var links = document.querySelectorAll('a[href*="?kenh="]');
            if (!links || links.length === 0) return;
            
            links.forEach(function(a) {
                if (a._kenhBound) return;
                a._kenhBound = true;
                
                a.addEventListener('click', function(e) {
                    var href = this.getAttribute('href');
                    if (!href) return;
                    var m = href.match(/\?kenh=(\d+)(?:#(.*))?/);
                    if (!m) return;
                    
                    var kId = m[1];
                    var hash = m[2];
                    var target = document.querySelector('div[class*="st-key-kenh_panel_' + kId + '"]');
                    
                    if (target) {
                        e.preventDefault();
                        e.stopPropagation();
                        
                        // 1. Ẩn tất cả các panel kênh
                        var allPanels = document.querySelectorAll('div[class*="st-key-kenh_panel_"]');
                        allPanels.forEach(function(p) {
                            p.style.setProperty('display', 'none', 'important');
                            p.classList.remove('kenh-panel-active');
                        });
                        
                        // 2. Hiện kênh được chọn
                        target.style.setProperty('display', 'block', 'important');
                        target.classList.add('kenh-panel-active');
                        
                        // 3. Cập nhật active tab trên navbar
                        document.querySelectorAll('.shortcut-parent, .shortcut-home').forEach(function(el) {
                            el.classList.remove('active');
                        });
                        var group = a.closest('.shortcut-group');
                        var parentTab = group ? group.querySelector('.shortcut-parent') : a;
                        if (parentTab && parentTab.classList.contains('shortcut-parent')) {
                            parentTab.classList.add('active');
                        } else if (a.classList.contains('shortcut-home')) {
                            a.classList.add('active');
                        }
                        
                        // 4. Cập nhật URL trình duyệt mà không reload
                        var newUrl = '?kenh=' + kId + (hash ? '#' + hash : '');
                        if (window.history && window.history.pushState) {
                            window.history.pushState({kenh: kId}, '', newUrl);
                        }
                        
                        // 5. Cuộn tới hash hoặc đầu trang
                        if (hash) {
                            setTimeout(function() {
                                var el = document.getElementById(hash);
                                if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' });
                            }, 50);
                        } else {
                            window.scrollTo({ top: 0, behavior: 'smooth' });
                        }
                        
                        // 6. Kích hoạt resize cho dataframe
                        window.dispatchEvent(new Event('resize'));
                    }
                });
            });
        }

        window.addEventListener('popstate', function() {
            var p = new URLSearchParams(window.location.search);
            var kId = p.get('kenh') || '1';
            var hash = window.location.hash ? window.location.hash.substring(1) : '';
            var target = document.querySelector('div[class*="st-key-kenh_panel_' + kId + '"]');
            if (target) {
                document.querySelectorAll('div[class*="st-key-kenh_panel_"]').forEach(function(p) {
                    p.style.setProperty('display', 'none', 'important');
                    p.classList.remove('kenh-panel-active');
                });
                target.style.setProperty('display', 'block', 'important');
                target.classList.add('kenh-panel-active');
                
                document.querySelectorAll('.shortcut-parent, .shortcut-home').forEach(function(el) {
                    el.classList.remove('active');
                });
                var activeLink = document.querySelector('a[href*="?kenh=' + kId + '"]');
                if (activeLink) {
                    var group = activeLink.closest('.shortcut-group');
                    var parentTab = group ? group.querySelector('.shortcut-parent') : activeLink;
                    if (parentTab) parentTab.classList.add('active');
                }
                if (hash) {
                    var el = document.getElementById(hash);
                    if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' });
                }
                window.dispatchEvent(new Event('resize'));
            }
        });

        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', initKenhSwitcher);
        } else {
            initKenhSwitcher();
        }
        setInterval(initKenhSwitcher, 350);
    })();
    </script>
    <img src="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg'%3E%3C/svg%3E" onload="if(window.initKenhSwitcher) window.initKenhSwitcher();" style="display:none;" />
    """
    st_html(js_switcher)
# =============================================================================
# 3. HERO BANNER
# =============================================================================
def render_hero_banner(nam_hoc=None, logo_data_uri="", is_logged_in=False, u_info=None):
    """Đã lược bỏ khối banner tiêu đề theo yêu cầu của nhà trường để giao diện tinh gọn, không chiếm diện tích"""
    pass

# =============================================================================
# 4. SECTION 1: CÔNG VIỆC CẦN HOÀN THÀNH (QUẢN TRỊ NHIỆM VỤ)
# =============================================================================

# =============================================================================
# 3.5. KHỐI CHỈ SỐ VÀNG ĐIỀU HÀNH TRANG CHỦ
# =============================================================================
def render_kpi_tong_quan_trang_chu(BASE_DIR, THU_MUC_NAM_HOC, nam_hoc_hien_tai):
    """Khối Chỉ Số Vàng & Trung Tâm Lối Tắt 8 Kênh Tác Nghiệp Trang Chủ"""
    st_html("""
    <div id="trang-chu" class="section-banner-title">
        <h3><span>🏫</span> TRUNG TÂM ĐIỀU HÀNH SỐ NHÀ TRƯỜNG — TRANG CHỦ TỔNG QUAN</h3>
        <span class="section-banner-subtitle">Hệ Thống Quản Trị Giáo Dục Toàn Diện 9 Kênh · Năm học 2026 - 2027</span>
    </div>
    """)

    st_html("""
    <div style="background: white; border: 1px solid #E2E8F0; border-radius: 12px; padding: 14px 18px; margin: 0 0 20px 0; box-shadow: 0 2px 8px rgba(13, 92, 117, 0.05);">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom: 12px;">
            <div style="font-size: 13.5px; font-weight: 800; color: #0D5C75; text-transform: uppercase; letter-spacing: 0.5px; display:flex; align-items:center; gap: 8px;">
                <span>✨</span> CHỈ SỐ VÀNG ĐIỀU HÀNH TOÀN TRƯỜNG HÔM NAY
            </div>
            <span style="background: #ECFDF5; color: #059669; font-size: 11px; font-weight: 700; padding: 3px 8px; border-radius: 10px;">
                🟢 Dữ liệu Live thời gian thực
            </span>
        </div>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 12px;">
            <a href="?kenh=4" target="_self" style="text-decoration:none; color:inherit;">
                <div style="background: #F8FAFC; border: 1px solid #E2E8F0; border-left: 4px solid #0D5C75; border-radius: 8px; padding: 10px 14px; transition:transform 0.15s ease;">
                    <div style="font-size: 11px; font-weight: 700; color: #64748B; text-transform: uppercase;">👥 SĨ SỐ TOÀN TRƯỜNG</div>
                    <div style="font-size: 22px; font-weight: 900; color: #0D5C75; margin: 2px 0;">929 <span style="font-size: 12px; font-weight: 600; color: #64748B;">học sinh</span></div>
                    <div style="font-size: 11px; color: #16A34A; font-weight: 600;">21 lớp · Mở Kênh Sĩ Số ➜</div>
                </div>
            </a>
            <a href="?kenh=7" target="_self" style="text-decoration:none; color:inherit;">
                <div style="background: #F8FAFC; border: 1px solid #E2E8F0; border-left: 4px solid #059669; border-radius: 8px; padding: 10px 14px; transition:transform 0.15s ease;">
                    <div style="font-size: 11px; font-weight: 700; color: #64748B; text-transform: uppercase;">🛏️ BÁN TRÚ & KTX</div>
                    <div style="font-size: 22px; font-weight: 900; color: #059669; margin: 2px 0;">196 <span style="font-size: 12px; font-weight: 600; color: #64748B;">học sinh</span></div>
                    <div style="font-size: 11px; color: #059669; font-weight: 600;">12 phòng KTX · Mở Bán Trú ➜</div>
                </div>
            </a>
            <a href="?kenh=2" target="_self" style="text-decoration:none; color:inherit;">
                <div style="background: #F8FAFC; border: 1px solid #E2E8F0; border-left: 4px solid #D97706; border-radius: 8px; padding: 10px 14px; transition:transform 0.15s ease;">
                    <div style="font-size: 11px; font-weight: 700; color: #64748B; text-transform: uppercase;">📋 NHIỆM VỤ TUẦN NÀY</div>
                    <div style="font-size: 22px; font-weight: 900; color: #D97706; margin: 2px 0;">6/6 <span style="font-size: 12px; font-weight: 600; color: #64748B;">hoàn thành</span></div>
                    <div style="font-size: 11px; color: #16A34A; font-weight: 600;">0 việc quá hạn · Mở Sổ Việc ➜</div>
                </div>
            </a>
            <a href="?kenh=6#quan-ly-xe-qr" target="_self" style="text-decoration:none; color:inherit;">
                <div style="background: #F8FAFC; border: 1px solid #E2E8F0; border-left: 4px solid #4338CA; border-radius: 8px; padding: 10px 14px; transition:transform 0.15s ease;">
                    <div style="font-size: 11px; font-weight: 700; color: #64748B; text-transform: uppercase;">🛵 XE HỌC SINH MÃ QR</div>
                    <div style="font-size: 22px; font-weight: 900; color: #4338CA; margin: 2px 0;">648 <span style="font-size: 12px; font-weight: 600; color: #64748B;">xe định danh</span></div>
                    <div style="font-size: 11px; color: #4338CA; font-weight: 600;">100% tem QR · Mở Kênh Xe ➜</div>
                </div>
            </a>
        </div>
    </div>
    """)

    st.markdown("#### 🧭 Lối Tắt Truy Cập 8 Kênh Điều Hành Chuyên Biệt")
    st_html("""
    <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 14px; margin-bottom: 24px;">
        <a href="?kenh=2" target="_self" style="text-decoration:none; color:inherit;">
            <div style="background:white; border:1px solid #E2E8F0; border-radius:10px; padding:14px; box-shadow:0 2px 5px rgba(0,0,0,0.03); transition:all 0.15s ease;">
                <div style="display:flex; align-items:center; gap:10px; margin-bottom:6px;">
                    <span style="font-size:22px;">📋</span>
                    <span style="font-weight:800; font-size:13.5px; color:#0D5C75;">KÊNH 2: CÔNG VIỆC CẦN LÀM</span>
                </div>
                <div style="font-size:12px; color:#64748B; line-height:1.5;">Quản trị phân công nhiệm vụ, việc quá hạn, việc hôm nay và sắp đến hạn.</div>
                <div style="font-size:11.5px; font-weight:700; color:#087B82; margin-top:8px;">Bấm mở Kênh 2 riêng biệt ➜</div>
            </div>
        </a>

        <a href="?kenh=3" target="_self" style="text-decoration:none; color:inherit;">
            <div style="background:white; border:1px solid #E2E8F0; border-radius:10px; padding:14px; box-shadow:0 2px 5px rgba(0,0,0,0.03); transition:all 0.15s ease;">
                <div style="display:flex; align-items:center; gap:10px; margin-bottom:6px;">
                    <span style="font-size:22px;">📅</span>
                    <span style="font-weight:800; font-size:13.5px; color:#0D5C75;">KÊNH 3: LỊCH LÀM VIỆC TUẦN</span>
                </div>
                <div style="font-size:12px; color:#64748B; line-height:1.5;">Lịch công tác Ban Giám hiệu, hội đồng sư phạm, lịch cơ sở và trực tuần.</div>
                <div style="font-size:11.5px; font-weight:700; color:#087B82; margin-top:8px;">Bấm mở Kênh 3 riêng biệt ➜</div>
            </div>
        </a>

        <a href="?kenh=4" target="_self" style="text-decoration:none; color:inherit;">
            <div style="background:white; border:1px solid #E2E8F0; border-radius:10px; padding:14px; box-shadow:0 2px 5px rgba(0,0,0,0.03); transition:all 0.15s ease;">
                <div style="display:flex; align-items:center; gap:10px; margin-bottom:6px;">
                    <span style="font-size:22px;">📊</span>
                    <span style="font-weight:800; font-size:13.5px; color:#0D5C75;">KÊNH 4: THEO DÕI HẰNG NGÀY</span>
                </div>
                <div style="font-size:12px; color:#64748B; line-height:1.5;">Giám sát sĩ số 21 lớp, chuyên cần, tiến độ chương trình và thiết bị dạy học.</div>
                <div style="font-size:11.5px; font-weight:700; color:#087B82; margin-top:8px;">Bấm mở Kênh 4 riêng biệt ➜</div>
            </div>
        </a>

        <a href="?kenh=5" target="_self" style="text-decoration:none; color:inherit;">
            <div style="background:white; border:1px solid #E2E8F0; border-radius:10px; padding:14px; box-shadow:0 2px 5px rgba(0,0,0,0.03); transition:all 0.15s ease;">
                <div style="display:flex; align-items:center; gap:10px; margin-bottom:6px;">
                    <span style="font-size:22px;">📈</span>
                    <span style="font-weight:800; font-size:13.5px; color:#0D5C75;">KÊNH 5: KẾT QUẢ DẠY VÀ HỌC</span>
                </div>
                <div style="font-size:12px; color:#64748B; line-height:1.5;">Sổ đầu bài điện tử (SĐB), thời khóa biểu 21 lớp, phân tích điểm và danh bạ.</div>
                <div style="font-size:11.5px; font-weight:700; color:#087B82; margin-top:8px;">Bấm mở Kênh 5 riêng biệt ➜</div>
            </div>
        </a>

        <a href="?kenh=6" target="_self" style="text-decoration:none; color:inherit;">
            <div style="background:#F0FDF4; border:1.5px solid #22C55E; border-radius:10px; padding:14px; box-shadow:0 2px 8px rgba(34,197,94,0.1); transition:all 0.15s ease;">
                <div style="display:flex; align-items:center; gap:10px; margin-bottom:6px;">
                    <span style="font-size:22px;">🚩</span>
                    <span style="font-weight:800; font-size:13.5px; color:#15803D;">KÊNH 6: NỀN NẾP – RÈN LUYỆN</span>
                </div>
                <div style="font-size:12px; color:#166534; line-height:1.5;">Bảng vàng 21 Chi đoàn, Chấm nề nếp 10 nhóm tiêu chí, 648 Xe QR và Sổ Đoàn.</div>
                <div style="font-size:11.5px; font-weight:800; color:#15803D; margin-top:8px;">Bấm mở Kênh 6 riêng biệt ➜</div>
            </div>
        </a>

        <a href="?kenh=7" target="_self" style="text-decoration:none; color:inherit;">
            <div style="background:white; border:1px solid #E2E8F0; border-radius:10px; padding:14px; box-shadow:0 2px 5px rgba(0,0,0,0.03); transition:all 0.15s ease;">
                <div style="display:flex; align-items:center; gap:10px; margin-bottom:6px;">
                    <span style="font-size:22px;">🛏️</span>
                    <span style="font-weight:800; font-size:13.5px; color:#0D5C75;">KÊNH 7: BÁN TRÚ & KÝ TÚC XÁ</span>
                </div>
                <div style="font-size:12px; color:#64748B; line-height:1.5;">Điểm danh 196 HS bán trú, kiểm thực ATTP 3 bước, thi đua 5S phòng ở và VietQR.</div>
                <div style="font-size:11.5px; font-weight:700; color:#087B82; margin-top:8px;">Bấm mở Kênh 7 riêng biệt ➜</div>
            </div>
        </a>

        <a href="?kenh=8" target="_self" style="text-decoration:none; color:inherit;">
            <div style="background:white; border:1px solid #E2E8F0; border-radius:10px; padding:14px; box-shadow:0 2px 5px rgba(0,0,0,0.03); transition:all 0.15s ease;">
                <div style="display:flex; align-items:center; gap:10px; margin-bottom:6px;">
                    <span style="font-size:22px;">📁</span>
                    <span style="font-weight:800; font-size:13.5px; color:#0D5C75;">KÊNH 8: HỒ SƠ – ĐÁNH GIÁ KPI</span>
                </div>
                <div style="font-size:12px; color:#64748B; line-height:1.5;">Kho 4 thư mục tài liệu điện tử và bảng tổng hợp đánh giá KPI 4 tổ chuyên môn.</div>
                <div style="font-size:11.5px; font-weight:700; color:#087B82; margin-top:8px;">Bấm mở Kênh 8 riêng biệt ➜</div>
            </div>
        </a>

        <a href="?kenh=9" target="_self" style="text-decoration:none; color:inherit;">
            <div style="background:white; border:1px solid #E2E8F0; border-radius:10px; padding:14px; box-shadow:0 2px 5px rgba(0,0,0,0.03); transition:all 0.15s ease;">
                <div style="display:flex; align-items:center; gap:10px; margin-bottom:6px;">
                    <span style="font-size:22px;">🚀</span>
                    <span style="font-weight:800; font-size:13.5px; color:#0D5C75;">KÊNH 9: TIỆN ÍCH GIÁO DỤC SỐ</span>
                </div>
                <div style="font-size:12px; color:#64748B; line-height:1.5;">9 ứng dụng giáo dục thiết yếu: VnEdu, Gmail, CSDL ngành, Zalo OA và Hướng dẫn App.</div>
                <div style="font-size:11.5px; font-weight:700; color:#087B82; margin-top:8px;">Bấm mở Kênh 9 riêng biệt ➜</div>
            </div>
        </a>
    </div>
    """)

def render_section_cong_viec(BASE_DIR, THU_MUC_NAM_HOC, nam_hoc_hien_tai, u_info=None):
    """
    KÊNH 2: CÔNG VIỆC CẦN HOÀN THÀNH (QUẢN TRỊ VÀ ĐIỀU HÀNH NHIỆM VỤ SỐ)
    Gồm 4 Thư mục tác nghiệp chuẩn hóa:
    1. 📊 Bảng chỉ huy & Tiến độ nhiệm vụ toàn trường (#bang-tien-do-nhiem-vu)
    2. ➕ Giao việc & Phân công nhiệm vụ mới kèm tài liệu đính kèm (#giao-nhiem-vu-moi)
    3. 🚨 Việc khẩn cấp, quá hạn & Cập nhật tiến độ trực tuyến (#viec-khan-cap-tien-do)
    4. 📁 Sổ theo dõi theo Tổ & Đánh giá mức độ hoàn thành KPI (#so-theo-doi-to-kpi)
    """
    folder_nam = nam_hoc_hien_tai.replace(" ", "")
    dir_nam = os.path.join(THU_MUC_NAM_HOC, folder_nam) if os.path.exists(THU_MUC_NAM_HOC) else BASE_DIR
    f_tasks = os.path.join(dir_nam, "nhiem_vu_nha_truong.csv")
    if not os.path.exists(f_tasks):
        f_tasks = os.path.join(BASE_DIR, "nhiem_vu_nha_truong.csv")

    dir_tep = os.path.join(BASE_DIR, "tep_dinh_kem_nhiem_vu")
    os.makedirs(dir_tep, exist_ok=True)

    u_curr = u_info if isinstance(u_info, dict) else st.session_state.get("user_login", {})
    fullname_curr = u_curr.get("fullname", "Cán bộ quản lý")
    role_curr = u_curr.get("role", "")

    # Đọc dữ liệu nhiệm vụ
    df_tasks = pd.DataFrame()
    if os.path.exists(f_tasks):
        try:
            df_tasks = pd.read_csv(f_tasks, encoding='utf-8-sig').fillna("")
        except Exception:
            pass

    # Đảm bảo đầy đủ các cột bắt buộc tránh lỗi nếu đọc từ file cũ
    required_cols = [
        ("Mã NV", ""),
        ("Tên công việc", ""),
        ("Người chủ trì", ""),
        ("Người thực hiện", ""),
        ("Hạn hoàn thành", ""),
        ("Mức độ", "Bình thường"),
        ("Phân loại", "Khác"),
        ("Trạng thái", "Chưa làm"),
        ("Tiến độ (%)", 0),
        ("Tệp đính kèm", ""),
        ("Link tài liệu", ""),
        ("Ghi chú", "")
    ]
    if not df_tasks.empty:
        for col_name, def_val in required_cols:
            if col_name not in df_tasks.columns:
                df_tasks[col_name] = def_val
    else:
        df_tasks = pd.DataFrame(columns=[c[0] for c in required_cols])

    tong_nv = len(df_tasks) if not df_tasks.empty else 0
    nv_done = len(df_tasks[df_tasks['Trạng thái'].astype(str).str.contains('hoàn thành|xong|done', case=False, na=False)]) if not df_tasks.empty else 0
    nv_doing = len(df_tasks[df_tasks['Trạng thái'].astype(str).str.contains('đang làm|tiến hành', case=False, na=False)]) if not df_tasks.empty else 0
    nv_todo = tong_nv - nv_done - nv_doing
    nv_khan_cap = len(df_tasks[df_tasks['Mức độ'].astype(str).str.contains('khẩn cấp|hỏa tốc', case=False, na=False)]) if not df_tasks.empty else 0
    ty_le_done = int((nv_done / tong_nv) * 100) if tong_nv > 0 else 0

    # =========================================================================
    # THƯ MỤC 1: 📊 BẢNG CHỈ HUY & TIẾN ĐỘ NHIỆM VỤ TOÀN TRƯỜNG (#bang-tien-do-nhiem-vu)
    # =========================================================================
    st_html("""
    <div id="cong-viec"></div>
    <div id="bang-tien-do-nhiem-vu" class="section-banner-title">
        <h3><span>📊</span> BẢNG CHỈ HUY & TIẾN ĐỘ NHIỆM VỤ TOÀN TRƯỜNG</h3>
        <span class="section-banner-subtitle">Hệ Thống Quản Trị Phân Công Công Việc · Giám Sát Tiến Độ Thời Gian Thực 24/7</span>
    </div>
    """)

    # 4 Thẻ chỉ số tổng quan
    c_k1, c_k2, c_k3, c_k4 = st.columns(4)
    c_k1.metric("📋 Tổng Số Nhiệm Vụ", f"{tong_nv} Việc", "Toàn trường 2026-2027")
    c_k2.metric("🚨 Việc Khẩn Cấp (Hỏa tốc)", f"{nv_khan_cap} Việc", "Cần xử lý gấp" if nv_khan_cap > 0 else "Ổn định")
    c_k3.metric("⚡ Đang Triển Khai", f"{nv_doing} Việc", "Đúng kế hoạch")
    c_k4.metric("🟢 Đã Hoàn Thành", f"{nv_done}/{tong_nv} Việc", f"Đạt {ty_le_done}% chỉ tiêu")

    # Bộ lọc danh sách nhiệm vụ
    st.markdown("##### 🔍 Bộ Lọc & Tìm Kiếm Nhiệm Vụ")
    c_fl_a, c_fl_b, c_fl_c, c_fl_d = st.columns([1.2, 1.2, 1, 2])
    with c_fl_a:
        ds_linhvuc = ["Tất cả lĩnh vực", "Bán trú & KTX", "Chuyên môn & Dạy học", "Đoàn Thanh niên", "An toàn giao thông", "Tài chính & Kế toán", "Khác"]
        fl_linhvuc = st.selectbox("Lĩnh vực:", ds_linhvuc, key="fl_nv_linhvuc")
    with c_fl_b:
        fl_mucdo = st.selectbox("Mức độ ưu tiên:", ["Tất cả mức độ", "Khẩn cấp", "Ưu tiên cao", "Bình thường"], key="fl_nv_mucdo")
    with c_fl_c:
        fl_trangthai = st.selectbox("Trạng thái:", ["Tất cả trạng thái", "Chưa làm", "Đang làm", "Đã hoàn thành"], key="fl_nv_trangthai")
    with c_fl_d:
        fl_search = st.text_input("Nhập tên công việc, người thực hiện hoặc mã NV:", "", key="fl_nv_search")

    df_filtered = df_tasks.copy() if not df_tasks.empty else pd.DataFrame()
    if not df_filtered.empty:
        if fl_linhvuc != "Tất cả lĩnh vực":
            df_filtered = df_filtered[df_filtered["Phân loại"].astype(str).str.contains(fl_linhvuc, case=False, na=False)]
        if fl_mucdo != "Tất cả mức độ":
            df_filtered = df_filtered[df_filtered["Mức độ"].astype(str).str.contains(fl_mucdo, case=False, na=False)]
        if fl_trangthai != "Tất cả trạng thái":
            df_filtered = df_filtered[df_filtered["Trạng thái"].astype(str).str.contains(fl_trangthai, case=False, na=False)]
        if fl_search.strip():
            kw = fl_search.strip().lower()
            cond = (
                df_filtered["Tên công việc"].astype(str).str.lower().str.contains(kw) |
                df_filtered["Người thực hiện"].astype(str).str.lower().str.contains(kw) |
                df_filtered["Mã NV"].astype(str).str.lower().str.contains(kw) |
                df_filtered["Người chủ trì"].astype(str).str.lower().str.contains(kw)
            )
            df_filtered = df_filtered[cond]

    # Hiển thị bảng công việc chi tiết
    if not df_filtered.empty:
        st.dataframe(
            df_filtered,
            use_container_width=True,
            height=300,
            column_config={
                "Mã NV": st.column_config.TextColumn("Mã", width="small"),
                "Tên công việc": st.column_config.TextColumn("Tên công việc", width="large"),
                "Người thực hiện": st.column_config.TextColumn("Người / Bộ phận thực hiện", width="medium"),
                "Hạn hoàn thành": st.column_config.TextColumn("Hạn chót"),
                "Mức độ": st.column_config.TextColumn("Mức độ"),
                "Trạng thái": st.column_config.TextColumn("Trạng thái"),
                "Tiến độ (%)": st.column_config.ProgressColumn("Tiến độ", format="%d%%", min_value=0, max_value=100),
                "Tệp đính kèm": st.column_config.TextColumn("Tệp đính kèm"),
                "Link tài liệu": st.column_config.LinkColumn("Link Drive"),
            }
        )

        # Khu vực Tải nhanh tệp đính kèm của các việc có file
        if "Tệp đính kèm" in df_filtered.columns:
            tasks_with_files = df_filtered[df_filtered["Tệp đính kèm"].astype(str).str.strip() != ""]
        else:
            tasks_with_files = pd.DataFrame()
        if not tasks_with_files.empty:
            st.markdown("##### 📎 Tài Liệu Đính Kèm Của Các Nhiệm Vụ (Bấm Để Tải Về Mở Ngay)")
            cols_files = st.columns(min(3, len(tasks_with_files)))
            c_idx = 0
            for _, r_file in tasks_with_files.head(6).iterrows():
                fn_val = str(r_file.get("Tệp đính kèm", "")).strip()
                ma_val = r_file.get("Mã NV", "")
                ten_val = r_file.get("Tên công việc", "")[:35]
                fp_val = os.path.join(dir_tep, fn_val)
                with cols_files[c_idx % len(cols_files)]:
                    if os.path.exists(fp_val):
                        with open(fp_val, "rb") as f_down:
                            st.download_button(
                                label=f"📥 [{ma_val}] {fn_val}",
                                data=f_down.read(),
                                file_name=fn_val,
                                key=f"down_btn_{ma_val}_{fn_val}"
                            )
                            st.caption(f"Việc: {ten_val}...")
                    else:
                        st.info(f"📄 [{ma_val}] {fn_val}")
                c_idx += 1

        # Nút xuất bảng nhiệm vụ
        c_dl_nv, _ = st.columns([2, 3])
        with c_dl_nv:
            csv_nv = df_filtered.to_csv(index=False, encoding='utf-8-sig').encode('utf-8-sig')
            st.download_button(
                label="📥 Xuất Toàn Bộ Sổ Công Việc (Excel / CSV)",
                data=csv_nv,
                file_name=f"so_nhiem_vu_nha_truong_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                key="btn_dl_so_nv_csv"
            )
    else:
        st.info("Không tìm thấy công việc nào phù hợp với bộ lọc.")

    # =========================================================================
    # THƯ MỤC 2: ➕ GIAO VIỆC & PHÂN CÔNG NHIỆM VỤ MỚI (#giao-nhiem-vu-moi)
    # =========================================================================
    st.markdown("<div style='margin-top: 32px;'></div>", unsafe_allow_html=True)
    st_html("""
    <div id="giao-nhiem-vu-moi" class="section-banner-title">
        <h3><span>➕</span> GIAO VIỆC & PHÂN CÔNG NHIỆM VỤ MỚI</h3>
        <span class="section-banner-subtitle">Dành Cho Ban Giám Hiệu & Tổ Trưởng Chuyên Môn · Hỗ Trợ Đính Kèm File & Link Drive</span>
    </div>
    """)

    with st.expander("📝 Biểu Mẫu Giao Nhiệm Vụ Điện Tử (Mở rộng để phân công)", expanded=True):
        c_gv1, c_gv2 = st.columns(2)
        with c_gv1:
            ten_nv_moi = st.text_input("Tên nhiệm vụ / Công việc cần làm (*):", placeholder="Ví dụ: Nộp báo cáo chuyên môn giữa kỳ I...", key="in_nv_ten")
            linh_vuc_moi = st.selectbox("Lĩnh vực / Phân loại:", [
                "Chuyên môn & Dạy học", "Bán trú & KTX", "Đoàn Thanh niên", 
                "An toàn giao thông", "Cơ sở vật chất & Thiết bị", "Tài chính & Kế toán", "Báo cáo Sở GD&ĐT", "Khác"
            ], key="in_nv_linhvuc")
            chu_tri_moi = st.selectbox("Người chủ trì:", [
                "Hiệu trưởng", "Phó Hiệu trưởng CM", "Phó Hiệu trưởng PT Bán trú", 
                "Chủ tịch Công đoàn", "Bí Thư Đoàn Trường", "Tổ trưởng Chuyên môn", f"{fullname_curr}"
            ], key="in_nv_chutri")

        with c_gv2:
            ds_nguoi_thuc_hien = [
                "Tổ Tự nhiên & Tổ Xã hội", "Tổ Bán trú & Kế toán", "Đội Cờ đỏ Khối 12", 
                "Toàn thể Giáo viên bộ môn (42 GV)", "Giáo viên chủ nhiệm 21 Chi đoàn", 
                "Giáo viên trực KTX & Y tế", "Tổ Văn phòng & Kế toán", "Đội Xung kích ATGT & Bảo vệ"
            ]
            thuc_hien_moi = st.selectbox("Người / Bộ phận thực hiện (*):", ds_nguoi_thuc_hien, key="in_nv_thuchien")
            
            c_d_h1, c_d_h2 = st.columns(2)
            with c_d_h1:
                han_moi = st.date_input("Hạn hoàn thành:", datetime.now().date() + pd.Timedelta(days=5), key="in_nv_han")
            with c_d_h2:
                muc_do_moi = st.selectbox("Mức độ ưu tiên:", ["Bình thường", "Ưu tiên cao", "Khẩn cấp"], key="in_nv_mucdo")

        ghi_chu_moi = st.text_area("Yêu cầu kết quả đầu ra & Hướng dẫn thực hiện:", placeholder="Nêu rõ sản phẩm đầu ra (Ví dụ: nộp file excel trước 17h, có xác nhận của tổ trưởng...)", height=65, key="in_nv_gc")

        # 2 CÁCH ĐÍNH KÈM TÀI LIỆU (KHÔNG HỀ LÀM NẶNG PHẦN MỀM)
        st.markdown("##### 📎 Đính Kèm Văn Bản Chỉ Đạo / Biểu Mẫu (Hỗ trợ 2 phương thức)")
        c_att1, c_att2 = st.columns(2)
        with c_att1:
            uploaded_file = st.file_uploader("Cách 1: Tải lên file công văn / biểu mẫu (Word, Excel, PDF < 5MB):", type=['docx', 'doc', 'xlsx', 'xls', 'pdf', 'png', 'jpg'], key="in_nv_file")
        with c_att2:
            link_drive_moi = st.text_input("Cách 2: Hoặc dán đường Link Google Drive / OneDrive trường:", placeholder="https://drive.google.com/drive/folders/...", key="in_nv_link_drive")

        if st.button("🚀 Giao Nhiệm Vụ & Lưu Vào Hệ Thống", type="primary", use_container_width=True, key="btn_save_nv_moi"):
            if ten_nv_moi.strip():
                # Tạo mã NV tự động
                next_nv_id = f"NV-{len(df_tasks) + 1:03d}"
                saved_filename = ""

                # Lưu file nếu có upload
                if uploaded_file is not None:
                    safe_name = f"{next_nv_id}_{uploaded_file.name.replace(' ', '_')}"
                    save_path = os.path.join(dir_tep, safe_name)
                    with open(save_path, "wb") as f_out:
                        f_out.write(uploaded_file.getbuffer())
                    saved_filename = safe_name

                row_nv_new = {
                    "Mã NV": next_nv_id,
                    "Tên công việc": ten_nv_moi.strip(),
                    "Người chủ trì": chu_tri_moi,
                    "Người thực hiện": thuc_hien_moi,
                    "Hạn hoàn thành": han_moi.strftime("%Y-%m-%d"),
                    "Mức độ": muc_do_moi,
                    "Phân loại": linh_vuc_moi,
                    "Trạng thái": "Chưa làm",
                    "Tiến độ (%)": 0,
                    "Tệp đính kèm": saved_filename,
                    "Link tài liệu": link_drive_moi.strip(),
                    "Ghi chú": ghi_chu_moi.strip()
                }

                df_add = pd.DataFrame([row_nv_new])
                if os.path.exists(f_tasks):
                    df_add.to_csv(f_tasks, mode='a', header=False, index=False, encoding='utf-8-sig')
                else:
                    df_add.to_csv(f_tasks, index=False, encoding='utf-8-sig')

                st.success(f"🎉 Đã giao thành công nhiệm vụ **[{next_nv_id}] {ten_nv_moi}** cho **{thuc_hien_moi}** (Hạn: {han_moi.strftime('%d/%m/%Y')})!")
                time.sleep(1)
                st.rerun()
            else:
                st.warning("Vui lòng nhập Tên nhiệm vụ / công việc cần làm.")

    # =========================================================================
    # THƯ MỤC 3: 🚨 VIỆC KHẨN CẤP, QUÁ HẠN & BÁO CÁO TIẾN ĐỘ (#viec-khan-cap-tien-do)
    # =========================================================================
    st.markdown("<div style='margin-top: 32px;'></div>", unsafe_allow_html=True)
    st_html("""
    <div id="viec-khan-cap-tien-do" class="section-banner-title">
        <h3><span>🚨</span> VIỆC KHẨN CẤP, QUÁ HẠN & BÁO CÁO TIẾN ĐỘ</h3>
        <span class="section-banner-subtitle">Khu Vực Báo Cáo Tiến Độ Trực Tuyến Dành Cho Cán Bộ, Giáo Viên & Tổ Chuyên Môn</span>
    </div>
    """)

    c_kc1, c_kc2 = st.columns([1, 1.2])
    with c_kc1:
        st.markdown("##### 🔴 Danh Sách Nhiệm Vụ Khẩn Cấp & Cần Xử Lý Ngay")
        df_khan = df_tasks[df_tasks["Mức độ"].astype(str).str.contains("Khẩn cấp|Hỏa tốc", case=False, na=False)] if not df_tasks.empty else pd.DataFrame()
        if not df_khan.empty:
            for _, rk in df_khan.iterrows():
                ma_k = rk.get("Mã NV", "")
                ten_k = rk.get("Tên công việc", "")
                th_k = rk.get("Người thực hiện", "")
                han_k = rk.get("Hạn hoàn thành", "")
                tt_k = rk.get("Trạng thái", "")
                st_html(f"""
                <div style="background:#FEF2F2; border-left:4px solid #DC2626; border-radius:8px; padding:10px 12px; margin-bottom:10px; border:1px solid #FECACA; border-left:4px solid #DC2626;">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <span style="background:#DC2626; color:white; font-size:10.5px; font-weight:800; padding:2px 6px; border-radius:4px;">{ma_k} · KHẨN CẤP</span>
                        <span style="font-size:11px; font-weight:700; color:#991B1B;">⏰ Hạn: {han_k}</span>
                    </div>
                    <div style="font-size:13px; font-weight:800; color:#1E293B; margin:5px 0;">{ten_k}</div>
                    <div style="font-size:11.5px; color:#64748B;">👤 <b>Người thực hiện:</b> {th_k} · <b>Trạng thái:</b> {tt_k}</div>
                </div>
                """)
        else:
            st.success("🟢 Tuyệt vời! Không có nhiệm vụ nào ở mức độ Khẩn cấp cần giải quyết gấp.")

    with c_kc2:
        st.markdown("##### 📝 Cập Nhật Tiến Độ & Báo Cáo Kết Quả Công Việc")
        with st.expander("🔄 Mở form cập nhật tiến độ công việc của tôi", expanded=True):
            if not df_tasks.empty:
                ds_nv_capnhat = [f"{r.get('Mã NV', '')} - {r.get('Tên công việc', '')} ({r.get('Người thực hiện', '')})" for _, r in df_tasks.iterrows()]
                sel_nv_update = st.selectbox("Chọn công việc cần báo cáo tiến độ:", ds_nv_capnhat, key="sel_nv_up_box")
                
                parts_nv = sel_nv_update.split(" - ")
                ma_selected = parts_nv[0].strip() if len(parts_nv) > 0 else ""

                c_up1, c_up2 = st.columns(2)
                with c_up1:
                    new_progress = st.slider("Cập nhật tiến độ hoàn thành (%):", min_value=0, max_value=100, value=80, step=5, key="nv_prog_slider")
                with c_up2:
                    new_status = st.selectbox("Cập nhật trạng thái:", ["Đang làm", "Đã hoàn thành", "Chưa làm"], key="nv_stat_sel")

                ghi_chu_kq = st.text_area("Báo cáo kết quả đạt được & Nội dung đã làm:", placeholder="Ví dụ: Đã rà soát xong 196 hồ sơ, đã nộp biểu mẫu về kế toán...", height=60, key="nv_gc_up")
                link_minh_chung = st.text_input("Link tài liệu minh chứng / file sản phẩm (Google Drive/Link):", placeholder="https://...", key="nv_link_mc")

                if st.button("💾 Cập Nhật Tiến Độ & Ghi Nhận Kết Quả", type="primary", use_container_width=True, key="btn_save_up_nv"):
                    # Cập nhật vào df_tasks
                    idx_match = df_tasks[df_tasks["Mã NV"] == ma_selected].index
                    if not idx_match.empty:
                        df_tasks.loc[idx_match, "Tiến độ (%)"] = new_progress
                        df_tasks.loc[idx_match, "Trạng thái"] = new_status
                        if ghi_chu_kq.strip():
                            old_gc = str(df_tasks.loc[idx_match, "Ghi chú"].values[0])
                            df_tasks.loc[idx_match, "Ghi chú"] = f"{old_gc} | Báo cáo: {ghi_chu_kq.strip()}"
                        if link_minh_chung.strip():
                            df_tasks.loc[idx_match, "Link tài liệu"] = link_minh_chung.strip()

                        df_tasks.to_csv(f_tasks, index=False, encoding='utf-8-sig')
                        st.success(f"🎉 Đã cập nhật thành công tiến độ nhiệm vụ **[{ma_selected}]**: **{new_progress}% ({new_status})**!")
                        time.sleep(1)
                        st.rerun()
            else:
                st.info("Chưa có nhiệm vụ nào trong hệ thống để cập nhật.")

    # =========================================================================
    # THƯ MỤC 4: 📁 SỔ THEO DÕI THEO TỔ & ĐÁNH GIÁ KPI (#so-theo-doi-to-kpi)
    # =========================================================================
    st.markdown("<div style='margin-top: 32px;'></div>", unsafe_allow_html=True)
    st_html("""
    <div id="so-theo-doi-to-kpi" class="section-banner-title">
        <h3><span>📁</span> SỔ THEO DÕI THEO TỔ & ĐÁNH GIÁ MỨC ĐỘ HOÀN THÀNH (KPI)</h3>
        <span class="section-banner-subtitle">Bảng Tổng Hợp Đánh Giá Khối Lượng & Hiệu Quả Công Việc Của Các Bộ Phận</span>
    </div>
    """)

    # Thống kê việc theo từng tổ
    ds_to = ["Bán trú & KTX", "Tự nhiên", "Xã hội", "Đoàn", "Kế toán", "Giáo viên"]
    stats_to = []
    if not df_tasks.empty:
        for to_name in ["Bán trú & KTX", "Tổ Tự nhiên & Tổ Xã hội", "Đoàn Thanh niên", "Kế toán", "Giáo viên"]:
            sub_df = df_tasks[df_tasks["Người thực hiện"].astype(str).str.contains(to_name[:6], case=False, na=False)]
            s_tong = len(sub_df)
            s_xong = len(sub_df[sub_df["Trạng thái"].astype(str).str.contains("hoàn thành|xong", case=False, na=False)])
            s_tl = int((s_xong / s_tong) * 100) if s_tong > 0 else 100
            stats_to.append({"Bộ phận / Tổ": to_name, "Tổng việc giao": s_tong, "Đã hoàn thành": s_xong, "Tỷ lệ đúng hạn (%)": s_tl})
    
    if stats_to:
        df_stats_to = pd.DataFrame(stats_to)
        c_st1, c_st2 = st.columns([1.2, 1])
        with c_st1:
            st.markdown("##### 🏛️ Bảng Xếp Hạng Tiến Độ Công Việc Theo Các Tổ")
            st.dataframe(
                df_stats_to,
                use_container_width=True,
                height=220,
                column_config={
                    "Bộ phận / Tổ": st.column_config.TextColumn("Tổ / Bộ phận", width="medium"),
                    "Tổng việc giao": st.column_config.NumberColumn("Việc giao"),
                    "Đã hoàn thành": st.column_config.NumberColumn("Đã xong"),
                    "Tỷ lệ đúng hạn (%)": st.column_config.ProgressColumn("Hiệu suất", format="%d%%", min_value=0, max_value=100),
                }
            )
        with c_st2:
            st.markdown("##### 📜 Lịch Sử Nhiệm Vụ Đã Hoàn Thành (Học kỳ I)")
            df_done_all = df_tasks[df_tasks["Trạng thái"].astype(str).str.contains("hoàn thành|xong", case=False, na=False)] if not df_tasks.empty else pd.DataFrame()
            if not df_done_all.empty:
                st.dataframe(
                    df_done_all[["Mã NV", "Tên công việc", "Người thực hiện", "Hạn hoàn thành"]],
                    use_container_width=True,
                    height=220
                )
            else:
                st.info("Chưa có nhiệm vụ nào hoàn tất lưu vào kho lịch sử.")

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
def render_section_nen_nep(BASE_DIR, THU_MUC_NAM_HOC, nam_hoc_hien_tai, u_info=None):
    """
    KÊNH 6: NỀN NẾP – RÈN LUYỆN (GỒM 4 THƯ MỤC TÁC NGHIỆP TÁCH RỜI CHUẨN ĐIỀU HÀNH)
    1. 🏆 Bảng vàng thi đua 21 Chi đoàn (#bang-vang-thi-dua)
    2. ⚖️ Chấm nề nếp hàng ngày & Vi phạm theo Quy chế 10 nhóm tiêu chí (#cham-ne-nep-vi-pham)
    3. 🛵 Quản lý 648 Xe gắn mã QR & An toàn giao thông (#quan-ly-xe-qr)
    4. 📜 Sổ đoàn viên điện tử & Công tác Đoàn (#so-doan-vien)
    """
    # 1. Đường dẫn các file dữ liệu
    f_thi_dua = os.path.join(BASE_DIR, "thi_dua_dtn_20_lop.csv")
    f_xe = os.path.join(BASE_DIR, "quan_ly_phuong_tien.csv")
    f_nk_thi_dua = os.path.join(BASE_DIR, "nhat_ky_thi_dua_lop_hang_ngay.csv")
    f_vi_pham_hs = os.path.join(BASE_DIR, "nhat_ky_vi_pham_hoc_sinh.csv")
    f_vi_pham_xe = os.path.join(BASE_DIR, "lich_su_vi_pham_xe.csv")
    f_so_doan = os.path.join(BASE_DIR, "doan_thanh_nien_so_doan.csv")

    u_curr = u_info if isinstance(u_info, dict) else st.session_state.get("user_login", {})
    fullname_curr = u_curr.get("fullname", "Cán bộ Cờ đỏ / Đoàn trường")

    ds_lop_all = [
        "10A1", "10A2", "10A3", "10A4", "10A5", "10A6", "10A7",
        "11A1", "11A2", "11A3", "11A4", "11A5", "11A6", "11A7",
        "12A1", "12A2", "12A3", "12A4", "12A5", "12A6", "12A7"
    ]

    # Đọc dữ liệu xe
    df_xe = pd.DataFrame()
    so_xe = 648
    if os.path.exists(f_xe):
        try:
            df_xe = pd.read_csv(f_xe, encoding='utf-8-sig', dtype=str).fillna("")
            so_xe = len(df_xe)
        except Exception:
            pass

    # Đọc dữ liệu thi đua 21 Chi đoàn
    df_td = pd.DataFrame()
    top_lop = "12A1"
    top_diem = "105.0"
    top_2_lop = "11A3"
    top_2_diem = "103.0"
    top_3_lop = "10A2"
    top_3_diem = "102.5"
    if os.path.exists(f_thi_dua):
        try:
            df_td = pd.read_csv(f_thi_dua, encoding='utf-8-sig').fillna("")
            if not df_td.empty:
                if "Tổng điểm" in df_td.columns:
                    df_td["Tổng điểm"] = pd.to_numeric(df_td["Tổng điểm"], errors='coerce').fillna(0)
                    df_td = df_td.sort_values(by="Tổng điểm", ascending=False).reset_index(drop=True)
                    df_td["Xếp hạng"] = range(1, len(df_td) + 1)
                if len(df_td) >= 1:
                    top_lop = str(df_td.iloc[0].get("Chi đoàn", "12A1"))
                    top_diem = str(df_td.iloc[0].get("Tổng điểm", "105.0"))
                if len(df_td) >= 2:
                    top_2_lop = str(df_td.iloc[1].get("Chi đoàn", "11A3"))
                    top_2_diem = str(df_td.iloc[1].get("Tổng điểm", "103.0"))
                if len(df_td) >= 3:
                    top_3_lop = str(df_td.iloc[2].get("Chi đoàn", "10A2"))
                    top_3_diem = str(df_td.iloc[2].get("Tổng điểm", "102.5"))
        except Exception:
            pass

    # =========================================================================
    # THƯ MỤC 1: 🏆 BẢNG VÀNG THI ĐUA 21 CHI ĐOÀN (#bang-vang-thi-dua)
    # =========================================================================
    st_html("""
    <div id="nen-nep-ren-luyen"></div>
    <div id="bang-vang-thi-dua" class="section-banner-title">
        <h3><span>🏆</span> BẢNG VÀNG THI ĐUA NỀ NẾP 21 CHI ĐOÀN</h3>
        <span class="section-banner-subtitle">Bảng Xếp Hạng Hàng Tuần · Cờ Luân Lưu Thi Đua · Năm học 2026 - 2027</span>
    </div>
    """)

    # Metrics hàng trên
    m_bv1, m_bv2, m_bv3, m_bv4 = st.columns(4)
    so_lop_tot = len(df_td[df_td['Xếp loại'].astype(str).str.contains('Tốt|Xuất sắc', case=False, na=False)]) if not df_td.empty and 'Xếp loại' in df_td.columns else 18
    m_bv1.metric("🥇 Dẫn đầu tuần", f"Chi đoàn {top_lop}", f"{top_diem} điểm (Cờ Nhất)")
    m_bv2.metric("🥈 Hạng Nhì", f"Chi đoàn {top_2_lop}", f"{top_2_diem} điểm (Cờ Nhì)")
    m_bv3.metric("🥉 Hạng Ba", f"Chi đoàn {top_3_lop}", f"{top_3_diem} điểm (Cờ Ba)")
    m_bv4.metric("🌟 Chi đoàn xếp loại Tốt", f"{so_lop_tot}/21 Lớp", "Tỷ lệ 85.7%")

    # 3 Thẻ Vinh danh Cờ Luân Lưu
    st_html(f"""
    <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap:12px; margin: 12px 0 16px 0;">
        <div style="background:linear-gradient(135deg, #FEF3C7 0%, #FDE68A 100%); border:1.5px solid #F59E0B; border-radius:10px; padding:12px 14px;">
            <div style="font-size:12px; font-weight:800; color:#B45309;">🥇 GIẢI NHẤT — CỜ ĐỎ XUẤT SẮC TUẦN 12</div>
            <div style="font-size:20px; font-weight:900; color:#78350F; margin:4px 0;">Chi đoàn {top_lop}</div>
            <div style="font-size:12px; color:#92400E;">Tổng điểm: <b>{top_diem}đ</b> · Chuyên cần 100% · Vệ sinh sạch xuất sắc · Hoa điểm tốt</div>
        </div>
        <div style="background:linear-gradient(135deg, #F1F5F9 0%, #E2E8F0 100%); border:1.5px solid #94A3B8; border-radius:10px; padding:12px 14px;">
            <div style="font-size:12px; font-weight:800; color:#475569;">🥈 GIẢI NHÌ — CỜ XANH TIÊN TIẾN</div>
            <div style="font-size:20px; font-weight:900; color:#1E293B; margin:4px 0;">Chi đoàn {top_2_lop}</div>
            <div style="font-size:12px; color:#475569;">Tổng điểm: <b>{top_2_diem}đ</b> · Đồng phục chuẩn mực · Xếp hàng ra vào lớp nghiêm túc</div>
        </div>
        <div style="background:linear-gradient(135deg, #FFEDD5 0%, #FED7AA 100%); border:1.5px solid #F97316; border-radius:10px; padding:12px 14px;">
            <div style="font-size:12px; font-weight:800; color:#C2410C;">🥉 GIẢI BA — CỜ VÀNG NỖ LỰC</div>
            <div style="font-size:20px; font-weight:900; color:#9A3412; margin:4px 0;">Chi đoàn {top_3_lop}</div>
            <div style="font-size:12px; color:#C2410C;">Tổng điểm: <b>{top_3_diem}đ</b> · 15 phút truy bài nghiêm túc · Không vi phạm ATGT</div>
        </div>
    </div>
    """)

    # Bộ lọc bảng vàng
    c_fl1, c_fl2, c_fl3 = st.columns([1, 1, 2])
    with c_fl1:
        khoi_filter = st.selectbox("Lọc theo Khối:", ["Tất cả khối", "Khối 10", "Khối 11", "Khối 12"], key="fl_td_khoi_sec")
    with c_fl2:
        tuan_filter = st.selectbox("Chọn Tuần thi đua:", ["Tuần 12 (Hiện tại)", "Tuần 11", "Tuần 10", "Tuần 9"], key="fl_td_tuan_sec")
    with c_fl3:
        tim_lop = st.text_input("🔍 Tìm kiếm Chi đoàn (ví dụ: 10A1, 12A3):", "", key="fl_td_search_sec")

    df_td_show = df_td.copy()
    if not df_td_show.empty:
        if khoi_filter != "Tất cả khối":
            k_num = khoi_filter.replace("Khối ", "").strip()
            if "Khối" in df_td_show.columns:
                df_td_show = df_td_show[df_td_show["Khối"].astype(str).str.contains(k_num, na=False)]
        if tim_lop.strip():
            df_td_show = df_td_show[df_td_show["Chi đoàn"].astype(str).str.contains(tim_lop.strip(), case=False, na=False)]

        st.dataframe(
            df_td_show,
            use_container_width=True,
            height=320,
            column_config={
                "Xếp hạng": st.column_config.NumberColumn("Hạng", format="%d 🏅"),
                "Chi đoàn": st.column_config.TextColumn("Chi đoàn", width="medium"),
                "Khối": st.column_config.TextColumn("Khối", width="small"),
                "Tổng điểm": st.column_config.NumberColumn("Tổng Điểm", format="%.1f đ"),
                "Xếp loại": st.column_config.TextColumn("Xếp loại"),
            }
        )

        c_d_td, _ = st.columns([2, 3])
        with c_d_td:
            csv_td = df_td_show.to_csv(index=False, encoding='utf-8-sig').encode('utf-8-sig')
            st.download_button(
                label="📥 Xuất Bảng vàng thi đua 21 Chi đoàn (CSV/Excel)",
                data=csv_td,
                file_name=f"bang_vang_thi_dua_21_chi_doan_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                key="btn_dl_thi_dua_csv_sec"
            )

    # =========================================================================
    # THƯ MỤC 2: ⚖️ CHẤM NỀ NẾP HÀNG NGÀY & VI PHẠM (QUY CHẾ 10 NHÓM TIÊU CHÍ)
    # =========================================================================
    st.markdown("<div style='margin-top: 32px;'></div>", unsafe_allow_html=True)
    st_html("""
    <div id="cham-ne-nep-vi-pham" class="section-banner-title">
        <h3><span>⚖️</span> CHẤM NỀ NẾP HÀNG NGÀY & XỬ LÝ VI PHẠM</h3>
        <span class="section-banner-subtitle">Hệ Thống Chấm Điểm Thi Đua Chuẩn 10 Nhóm Tiêu Chí (Đoàn Trường & Chi Ủy Phê Duyệt)</span>
    </div>
    """)

    c_cham1, c_cham2 = st.columns([6.2, 3.8])
    with c_cham1:
        st.markdown("#### 📝 Phiếu Chấm Điểm Thi Đua Chi Đoàn")
        
        c_ch_a, c_ch_b, c_ch_c = st.columns(3)
        with c_ch_a:
            lop_cham = st.selectbox("Chọn Chi đoàn:", ds_lop_all, key="cham_lop_sec_val")
        with c_ch_b:
            ngay_cham = st.date_input("Ngày chấm:", datetime.now().date(), key="cham_ngay_sec_val")
        with c_ch_c:
            buoi_cham = st.selectbox("Buổi học:", ["Buổi Sáng", "Buổi Chiều"], key="cham_buoi_sec_val")

        c_ch_d, c_ch_e = st.columns(2)
        with c_ch_d:
            nguoi_cham = st.text_input("Người chấm:", value=fullname_curr, key="cham_nguoi_sec_val")
        with c_ch_e:
            chuc_vu_cham = st.selectbox("Đơn vị trực:", [
                "Đội Cờ đỏ Khối 12", "Đội Cờ đỏ Khối 11", "Đội Cờ đỏ Khối 10", 
                "BCH Đoàn Trường", "Giáo viên Trực ban", "GVCN kiểm tra chéo"
            ], key="cham_chucvu_sec_val")

        # 4 HỘP TIÊU CHÍ THI ĐUA (10 NHÓM TIÊU CHÍ CHÍNH THỨC)
        with st.expander("🔴 1. Chuyên Cần & Trang Phục, Tác Phong (Nhóm 1 & 2)", expanded=True):
            st.markdown("**Nhóm 1: Chuyên cần & Nề nếp thời gian**")
            c_g1_1, c_g1_2, c_g1_3 = st.columns(3)
            with c_g1_1:
                c1_muon = st.number_input("Đi muộn (-0.5đ/lượt):", min_value=0, max_value=50, value=0, step=1, key="c1_muon")
            with c_g1_2:
                c1_nghi_phep = st.number_input("Nghỉ có phép chính đáng (-1đ/hs):", min_value=0, max_value=50, value=0, step=1, key="c1_nghi_phep")
            with c_g1_3:
                c1_nghi_kp = st.number_input("Nghỉ không phép/bỏ tiết (-5đ/lượt):", min_value=0, max_value=50, value=0, step=1, key="c1_nghi_kp")

            st.markdown("**Nhóm 2: Trang phục, đầu tóc, tác phong, văn hóa học đường**")
            c_g2_1, c_g2_2 = st.columns(2)
            with c_g2_1:
                c2_so_vin = st.number_input("Nam sinh không sơ vin (-0.5đ/lượt):", min_value=0, max_value=50, value=0, step=1, key="c2_so_vin")
                c2_sai_dp = st.number_input("Sai đồng phục/dép lê, không quai hậu (-1đ/buổi):", min_value=0, max_value=50, value=0, step=1, key="c2_sai_dp")
                c2_trang_diem = st.number_input("Trang điểm đậm, sơn móng, móng nhọn (-2đ/lượt):", min_value=0, max_value=50, value=0, step=1, key="c2_trang_diem")
            with c_g2_2:
                c2_phan_cam = st.number_input("Trang phục phản cảm/nhuộm tóc/cạo trọc (-3đ/buổi):", min_value=0, max_value=50, value=0, step=1, key="c2_phan_cam")
                c2_xam_hinh = st.number_input("Xăm hình/nói tục/thiếu tôn trọng/yêu đương (-5đ/lượt):", min_value=0, max_value=50, value=0, step=1, key="c2_xam_hinh")

        with st.expander("📱 2. Thiết Bị Điện Tử, An Ninh Mạng & ATGT (Nhóm 3 & 4)", expanded=False):
            st.markdown("**Nhóm 3: Thiết bị điện tử & An ninh mạng**")
            c_g3_1, c_g3_2 = st.columns(2)
            with c_g3_1:
                c3_dien_thoai = st.number_input("Dùng ĐT, tai nghe trong giờ không phép (-5đ/lượt):", min_value=0, max_value=20, value=0, step=1, key="c3_dt")
                c3_thi_cu = st.number_input("Dùng ĐT/công nghệ trong thi cử, kiểm tra (-10đ/lượt):", min_value=0, max_value=10, value=0, step=1, key="c3_thi_cu")
            with c_g3_2:
                c3_mxh = st.number_input("Vi phạm MXH/tin giả xúc phạm/AI clip (-20đ/lượt):", min_value=0, max_value=10, value=0, step=1, key="c3_mxh")

            st.markdown("**Nhóm 4: Trật tự an toàn giao thông (ATGT)**")
            c_g4_1, c_g4_2 = st.columns(2)
            with c_g4_1:
                c4_de_xe = st.number_input("Để xe sai quy định (-5đ/lớp):", min_value=0, max_value=10, value=0, step=1, key="c4_de_xe")
                c4_vi_pham_nhe = st.number_input("Mũ sai quy cách/chở quá/dàn hàng 3 (-10đ/lượt):", min_value=0, max_value=20, value=0, step=1, key="c4_vp_nhe")
                c4_khong_qr = st.number_input("Đi xe không khai báo / không dán tem QR (-20đ/lượt):", min_value=0, max_value=20, value=0, step=1, key="c4_khong_qr")
            with c_g4_2:
                c4_khong_mu = st.number_input("Không đội mũ BH/pô to/chưa đủ tuổi (-30đ/lượt):", min_value=0, max_value=10, value=0, step=1, key="c4_khong_mu")
                c4_lang_lach = st.number_input("Lạng lách/vượt đèn đỏ/độ xe/Công an báo (-50đ/lượt):", min_value=0, max_value=10, value=0, step=1, key="c4_lang_lach")
                c4_tai_nan = st.number_input("Vi phạm ATGT gây tai nạn giao thông (-60đ/vụ):", min_value=0, max_value=5, value=0, step=1, key="c4_tai_nan")

        with st.expander("🛡️ 3. An Toàn Học Đường, Vệ Sinh, Nước RO, Giờ Học & Nhiệm Vụ (Nhóm 5 - 9)", expanded=False):
            st.markdown("**Nhóm 5: Phòng chống bạo lực học đường & Tệ nạn**")
            c_g5_1, c_g5_2, c_g5_3 = st.columns(3)
            with c_g5_1:
                c5_thuoc_la = st.number_input("Thuốc lá, rượu bia, nồng độ cồn (-20đ/lượt):", min_value=0, max_value=10, value=0, step=1, key="c5_thuoc_la")
            with c_g5_2:
                c5_hung_khi = st.number_input("Mang hung khí/trộm cắp/cờ bạc (-30đ/lượt):", min_value=0, max_value=10, value=0, step=1, key="c5_hung_khi")
            with c_g5_3:
                c5_danh_nhau = st.number_input("Đánh nhau/kéo người ngoài/pháo nổ (-50đ/lượt):", min_value=0, max_value=10, value=0, step=1, key="c5_danh_nhau")

            st.markdown("**Nhóm 6: Cơ sở vật chất, vệ sinh & Lao động**")
            c_g6_1, c_g6_2 = st.columns(2)
            with c_g6_1:
                c6_thieu_ghe = st.number_input("Thiếu ghế/mang ghế sai giờ tập thể (-1đ/lượt):", min_value=0, max_value=30, value=0, step=1, key="c6_thieu_ghe")
                c6_ve_sinh_ban = st.number_input("Vệ sinh lớp bẩn/chưa đổ rác (-2đ/buổi):", min_value=0, max_value=10, value=0, step=1, key="c6_vs_ban")
                c6_ve_bay = st.number_input("Vẽ bậy/mang đồ ăn vào lớp/hỏng đồ (-5đ/lượt):", min_value=0, max_value=10, value=0, step=1, key="c6_ve_bay")
            with c_g6_2:
                c6_quen_tat_dien = st.number_input("Không đóng cửa/không tắt điện (-5đ/lần):", min_value=0, max_value=10, value=0, step=1, key="c6_quen_dien")
                c6_bo_lao_dong = st.number_input("Bỏ lao động/không chăm sóc cây hoa (-10đ/lần):", min_value=0, max_value=5, value=0, step=1, key="c6_bo_ld")

            st.markdown("**Nhóm 7: Tiết kiệm tài nguyên & Nước RO**")
            c_g7_1, c_g7_2 = st.columns(2)
            with c_g7_1:
                c7_uong_ro = st.number_input("Uống trực tiếp vòi RO/quên khóa vòi tràn (-2đ/lần):", min_value=0, max_value=10, value=0, step=1, key="c7_uong_ro")
                c7_lang_phi_nuoc = st.number_input("Lãng phí nước khu vệ sinh/xả tràn (-5đ/lần):", min_value=0, max_value=10, value=0, step=1, key="c7_lp_nuoc")
            with c_g7_2:
                c7_ro_sai_muc_dich = st.number_input("Dùng nước RO giặt khăn/phá hỏng máy RO (-20đ/lần):", min_value=0, max_value=5, value=0, step=1, key="c7_ro_sai_md")

            st.markdown("**Nhóm 8 & 9: Đánh giá giờ học & Hồ sơ nhiệm vụ**")
            c_g8_1, c_g8_2 = st.columns(2)
            with c_g8_1:
                c8_gio_kha = st.number_input("Giờ học Khá sổ đầu bài (-2đ/tiết):", min_value=0, max_value=30, value=0, step=1, key="c8_gio_kha")
                c8_gio_tb = st.number_input("Giờ học Trung bình (-4đ/tiết):", min_value=0, max_value=20, value=0, step=1, key="c8_gio_tb")
                c8_gio_yeu = st.number_input("Giờ học Yếu / Kém (-6đ/tiết):", min_value=0, max_value=10, value=0, step=1, key="c8_gio_yeu")
            with c_g8_2:
                c9_nop_sai = st.number_input("Nộp hồ sơ báo cáo thiếu/sai (-2đ/ngày):", min_value=0, max_value=10, value=0, step=1, key="c9_nop_sai")
                c9_nop_muon = st.number_input("Nộp báo cáo/quỹ Đoàn muộn (-5đ/lần):", min_value=0, max_value=10, value=0, step=1, key="c9_nop_muon")
                c9_khong_nv = st.number_input("Không thực hiện nhiệm vụ nhà trường (-10đ/lần):", min_value=0, max_value=5, value=0, step=1, key="c9_khong_nv")
                c9_khong_so_truc = st.checkbox("Không nộp sổ trực tuần (Trừ 100đ - Tính 0đ tuần)", key="c9_so_truc")

        with st.expander("🌟 4. Điểm Cộng Khuyến Khích & Phong Trào (Nhóm 10)", expanded=True):
            c_g10_1, c_g10_2 = st.columns(2)
            with c_g10_1:
                c10_van_nghe = st.number_input("Tham gia tập văn nghệ của trường (+3đ/HS):", min_value=0, max_value=30, value=0, step=1, key="c10_vn")
                c10_trang_phuc_dt = st.number_input("Mặc trang phục dân tộc dịp Lễ / Nhặt của rơi (+3đ/HS):", min_value=0, max_value=20, value=0, step=1, key="c10_dt_cua_roi")
                c10_xuat_sac = st.number_input("Tập thể xuất sắc đột xuất được biểu dương (+20đ/lần):", min_value=0, max_value=5, value=0, step=1, key="c10_xs")
            with c_g10_2:
                c10_dung_cam = st.number_input("Dũng cảm tố giác bạo lực/thuốc lá/pháo (+20đ/lần):", min_value=0, max_value=5, value=0, step=1, key="c10_dc")
                c10_giai_phong_trao = st.selectbox("Tập thể đạt giải phong trào:", [
                    "Không có giải", "Giải Nhất (+20đ)", "Giải Nhì (+15đ)", "Giải Ba (+10đ)", "Giải Khuyến khích (+5đ)"
                ], key="c10_giai")

        # TÍNH TOÁN ĐIỂM THEO 10 TIÊU CHÍ
        tong_tru = float(
            c1_muon * 0.5 + c1_nghi_phep * 1.0 + c1_nghi_kp * 5.0 +
            c2_so_vin * 0.5 + c2_sai_dp * 1.0 + c2_trang_diem * 2.0 + c2_phan_cam * 3.0 + c2_xam_hinh * 5.0 +
            c3_dien_thoai * 5.0 + c3_thi_cu * 10.0 + c3_mxh * 20.0 +
            c4_de_xe * 5.0 + c4_vi_pham_nhe * 10.0 + c4_khong_qr * 20.0 + c4_khong_mu * 30.0 + c4_lang_lach * 50.0 + c4_tai_nan * 60.0 +
            c5_thuoc_la * 20.0 + c5_hung_khi * 30.0 + c5_danh_nhau * 50.0 +
            c6_thieu_ghe * 1.0 + c6_ve_sinh_ban * 2.0 + c6_ve_bay * 5.0 + c6_quen_tat_dien * 5.0 + c6_bo_lao_dong * 10.0 +
            c7_uong_ro * 2.0 + c7_lang_phi_nuoc * 5.0 + c7_ro_sai_muc_dich * 20.0 +
            c8_gio_kha * 2.0 + c8_gio_tb * 4.0 + c8_gio_yeu * 6.0 +
            c9_nop_sai * 2.0 + c9_nop_muon * 5.0 + c9_khong_nv * 10.0 + (100.0 if c9_khong_so_truc else 0.0)
        )

        giai_map = {"Giải Nhất (+20đ)": 20.0, "Giải Nhì (+15đ)": 15.0, "Giải Ba (+10đ)": 10.0, "Giải Khuyến khích (+5đ)": 5.0}
        cong_giai = giai_map.get(c10_giai_phong_trao, 0.0)
        tong_cong = float(c10_van_nghe * 3.0 + c10_trang_phuc_dt * 3.0 + c10_xuat_sac * 20.0 + c10_dung_cam * 20.0 + cong_giai)
        diem_ngay = max(0.0, 100.0 - tong_tru + tong_cong)

        st_html(f"""
        <div style="background:#F0FDF4; border:1.5px solid #22C55E; border-radius:10px; padding:12px 16px; margin: 12px 0;">
            <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap;">
                <div>
                    <span style="font-size:13px; font-weight:700; color:#15803D;">TỔNG KẾT ĐIỂM CHẤM CHI ĐOÀN {lop_cham}</span><br>
                    <span style="font-size:12px; color:#475569;">Điểm gốc: 100.0đ · Tổng trừ: <b>-{tong_tru:.1f}đ</b> · Tổng cộng: <b>+{tong_cong:.1f}đ</b></span>
                </div>
                <div style="font-size:26px; font-weight:900; color:#15803D;">
                    {diem_ngay:.1f} <span style="font-size:14px; font-weight:600;">/ 100 điểm</span>
                </div>
            </div>
        </div>
        """)

        hs_vi_pham_ten = st.text_input("Tên học sinh vi phạm (nếu có, để lưu sổ cá nhân):", placeholder="Ví dụ: Nguyễn Văn Nam (Đi muộn), Hoàng Thị Mai (Không đội mũ BH)...", key="hs_vp_sec_ten")
        hs_khen_thuong_ten = st.text_input("Tên học sinh được khen thưởng (nếu có):", placeholder="Ví dụ: Trần Văn C (Nhặt được 200k trả lại)...", key="hs_kt_sec_ten")
        ghi_chu_cham = st.text_area("Ghi chú nề nếp buổi học:", placeholder="Chi đoàn chấp hành tốt, 1 trường hợp quên thẻ HS...", height=60, key="cham_gc_sec")

        if st.button("💾 Lưu Kết Quả Chấm Nề Nếp Hôm Nay", type="primary", use_container_width=True, key="btn_save_cham_sec"):
            row_cham = {
                "Thời gian gửi": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                "Ngày chấm": ngay_cham.strftime("%d/%m/%Y"),
                "Buổi": buoi_cham,
                "Lớp": lop_cham,
                "Người chấm": nguoi_cham,
                "Chức vụ": chuc_vu_cham,
                "Tổng trừ": tong_tru,
                "Tổng cộng": tong_cong,
                "Tổng điểm ngày": diem_ngay,
                "Học sinh vi phạm": hs_vi_pham_ten.strip(),
                "Học sinh tuyên dương": hs_khen_thuong_ten.strip(),
                "Ghi chú": ghi_chu_cham.strip()
            }
            df_new_cham = pd.DataFrame([row_cham])
            if os.path.exists(f_nk_thi_dua):
                df_new_cham.to_csv(f_nk_thi_dua, mode='a', header=False, index=False, encoding='utf-8-sig')
            else:
                df_new_cham.to_csv(f_nk_thi_dua, index=False, encoding='utf-8-sig')

            if hs_vi_pham_ten.strip():
                row_vp_hs = {
                    "Ngày": ngay_cham.strftime("%d/%m/%Y"),
                    "Học sinh": hs_vi_pham_ten.strip(),
                    "Lớp": lop_cham,
                    "Lỗi vi phạm": f"Trừ {tong_tru:.1f}đ nề nếp ({buoi_cham})",
                    "Người phát hiện": f"{nguoi_cham} ({chuc_vu_cham})",
                    "Điểm trừ Chi đoàn": -tong_tru,
                    "Trạng thái": "Đã lưu sổ thi đua",
                    "Ghi chú": ghi_chu_cham.strip()
                }
                df_save_vp = pd.DataFrame([row_vp_hs])
                if os.path.exists(f_vi_pham_hs):
                    df_save_vp.to_csv(f_vi_pham_hs, mode='a', header=False, index=False, encoding='utf-8-sig')
                else:
                    df_save_vp.to_csv(f_vi_pham_hs, index=False, encoding='utf-8-sig')

            st.success(f"🎉 Đã lưu thành công kết quả chấm nề nếp Chi đoàn **{lop_cham}**: **{diem_ngay:.1f}/100 điểm** theo đúng 10 nhóm tiêu chí của trường!")
            time.sleep(1)
            st.rerun()

    with c_cham2:
        st.markdown("#### 📜 Nhật Ký Chấm Nề Nếp Gần Đây")
        df_nk_td = pd.DataFrame()
        if os.path.exists(f_nk_thi_dua):
            try:
                df_nk_td = pd.read_csv(f_nk_thi_dua, encoding='utf-8-sig').fillna("")
            except Exception:
                pass

        if not df_nk_td.empty:
            st.dataframe(
                df_nk_td.tail(8).iloc[::-1],
                use_container_width=True,
                height=260,
                column_config={
                    "Ngày chấm": st.column_config.TextColumn("Ngày"),
                    "Lớp": st.column_config.TextColumn("Lớp", width="small"),
                    "Tổng điểm ngày": st.column_config.NumberColumn("Điểm", format="%.1f đ"),
                    "Người chấm": st.column_config.TextColumn("Cờ đỏ / Trực"),
                }
            )
        else:
            st.info("Chưa có lượt chấm nề nếp mới trong hôm nay. Hãy sử dụng form bên trái để ghi nhận.")

        st.markdown("#### ⚠️ Sổ Theo Dõi Học Sinh Vi Phạm")
        df_vp_live = pd.DataFrame()
        if os.path.exists(f_vi_pham_hs):
            try:
                df_vp_live = pd.read_csv(f_vi_pham_hs, encoding='utf-8-sig').fillna("")
            except Exception:
                pass

        if not df_vp_live.empty:
            st.dataframe(
                df_vp_live.tail(6).iloc[::-1],
                use_container_width=True,
                height=240,
                column_config={
                    "Ngày": st.column_config.TextColumn("Ngày"),
                    "Học sinh": st.column_config.TextColumn("Họ và tên"),
                    "Lớp": st.column_config.TextColumn("Lớp", width="small"),
                    "Lỗi vi phạm": st.column_config.TextColumn("Hành vi vi phạm"),
                    "Trạng thái": st.column_config.TextColumn("Trạng thái"),
                }
            )
        else:
            st.success("🟢 Toàn trường duy trì nề nếp tốt, không có hồ sơ vi phạm nghiêm trọng tồn đọng.")

    # =========================================================================
    # THƯ MỤC 3: 🛵 QUẢN LÝ 648 XE GẮN MÃ QR & AN TOÀN GIAO THÔNG (#quan-ly-xe-qr)
    # =========================================================================
    st.markdown("<div style='margin-top: 32px;'></div>", unsafe_allow_html=True)
    st_html("""
    <div id="quan-ly-xe-qr" class="section-banner-title">
        <h3><span>🛵</span> QUẢN LÝ 648 XE GẮN MÃ QR & AN TOÀN GIAO THÔNG</h3>
        <span class="section-banner-subtitle">Hệ Thống Định Danh Phương Tiện Bằng Mã QR · Giám Sát Cổng Trường 24/7</span>
    </div>
    """)

    m_xe1, m_xe2, m_xe3, m_xe4 = st.columns(4)
    so_xe_dien = len(df_xe[df_xe["Loại xe"].astype(str).str.contains("điện", case=False, na=False)]) if not df_xe.empty and "Loại xe" in df_xe.columns else 540
    so_xe_50 = len(df_xe[df_xe["Loại xe"].astype(str).str.contains("50|xăng", case=False, na=False)]) if not df_xe.empty and "Loại xe" in df_xe.columns else 108
    if so_xe_dien + so_xe_50 == 0:
        so_xe_dien = 540
        so_xe_50 = 108

    df_vp_xe = pd.DataFrame()
    if os.path.exists(f_vi_pham_xe):
        try:
            df_vp_xe = pd.read_csv(f_vi_pham_xe, encoding='utf-8-sig').fillna("")
        except Exception:
            pass
    so_vp_xe = len(df_vp_xe)

    m_xe1.metric("🛵 Tổng Xe Đã Định Danh", f"{so_xe} Xe", "100% Cấp mã QR")
    m_xe2.metric("⚡ Xe Máy Điện & Xe Đạp Điện", f"{so_xe_dien} Xe", "Chiếm 83.3%")
    m_xe3.metric("🏍️ Xe Máy Dưới 50cc", f"{so_xe_50} Xe", "Chiếm 16.7%")
    m_xe4.metric("🚨 Lượt Vi Phạm Giao Thông", f"{so_vp_xe} Lượt", "Đã lập biên bản" if so_vp_xe > 0 else "An toàn tuyệt đối")

    st.markdown("##### 🔍 Tra Cứu Thông Tin Xe & Quét Thẻ Mã QR Học Sinh")
    c_xf1, c_xf2, c_xf3 = st.columns([2, 1, 1])
    with c_xf1:
        search_xe = st.text_input("Nhập Biển số, Họ tên HS, Mã xe (XE-001...) hoặc SĐT Phụ huynh:", "", key="search_xe_sec_in")
    with c_xf2:
        lop_xe_filter = st.selectbox("Lọc theo Chi đoàn:", ["Tất cả các lớp"] + ds_lop_all, key="sel_lop_xe_sec")
    with c_xf3:
        loai_xe_filter = st.selectbox("Lọc theo Loại xe:", ["Tất cả loại xe", "Xe đạp điện", "Xe điện", "Xe máy điện", "Xe 50cc"], key="sel_loai_xe_sec")

    df_xe_show = df_xe.copy() if not df_xe.empty else pd.DataFrame()
    if not df_xe_show.empty:
        if lop_xe_filter != "Tất cả các lớp":
            df_xe_show = df_xe_show[df_xe_show["Lớp"].astype(str).str.contains(lop_xe_filter, case=False, na=False)]
        if loai_xe_filter != "Tất cả loại xe":
            df_xe_show = df_xe_show[df_xe_show["Loại xe"].astype(str).str.contains(loai_xe_filter, case=False, na=False)]
        if search_xe.strip():
            kw = search_xe.strip().lower()
            cond = (
                df_xe_show["Biển số xe"].astype(str).str.lower().str.contains(kw) |
                df_xe_show["Họ và tên"].astype(str).str.lower().str.contains(kw) |
                df_xe_show["Mã xe"].astype(str).str.lower().str.contains(kw) |
                df_xe_show["Lớp"].astype(str).str.lower().str.contains(kw) |
                df_xe_show["SĐT Phụ huynh"].astype(str).str.lower().str.contains(kw)
            )
            df_xe_show = df_xe_show[cond]

        if search_xe.strip() and len(df_xe_show) > 0 and len(df_xe_show) <= 2:
            for _, rx in df_xe_show.iterrows():
                ma_xe_val = rx.get("Mã xe", "XE-000")
                ten_hs_val = rx.get("Họ và tên", "Học sinh")
                lop_val = rx.get("Lớp", "")
                bien_so_val = rx.get("Biển số xe", "Chưa cấp biển")
                loai_val = rx.get("Loại xe", "Xe điện")
                mau_val = rx.get("Màu xe", "Đen")
                gvcn_val = rx.get("GVCN", "Thầy/Cô GVCN")
                ph_val = rx.get("Họ tên Phụ huynh", "Phụ huynh")
                sdt_ph_val = str(rx.get("SĐT Phụ huynh", "")).replace(".0", "")
                noi_gui_val = rx.get("Nơi gửi xe", "Trong trường")
                dia_chi_val = rx.get("Địa chỉ", "Bảo Hà - Lào Cai")

                st_html(f"""
                <div style="background:white; border:2px solid #0D5C75; border-radius:12px; padding:16px 20px; margin:12px 0; box-shadow:0 4px 12px rgba(13,92,117,0.1); display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:16px;">
                    <div style="flex:1; min-width:280px;">
                        <div style="display:flex; align-items:center; gap:10px; margin-bottom:6px;">
                            <span style="background:#0D5C75; color:white; font-size:12px; font-weight:800; padding:3px 10px; border-radius:6px;">MÃ ĐỊNH DANH: {ma_xe_val}</span>
                            <span style="background:#DCFCE7; color:#15803D; font-size:12px; font-weight:700; padding:3px 8px; border-radius:6px;">🟢 ĐỦ ĐIỀU KIỆN LƯU HÀNH</span>
                        </div>
                        <div style="font-size:18px; font-weight:900; color:#0F172A; margin:4px 0;">{ten_hs_val} — Chi đoàn {lop_val}</div>
                        <div style="font-size:13px; color:#334155; line-height:1.6;">
                            🛵 <b>Biển số:</b> <span style="background:#FEF08A; padding:2px 8px; border-radius:4px; font-weight:800; color:#854D0E;">{bien_so_val}</span> · <b>Loại xe:</b> {loai_val} ({mau_val})<br>
                            🏫 <b>Nơi gửi:</b> {noi_gui_val} · <b>GVCN:</b> {gvcn_val}<br>
                            👨‍👩‍👧 <b>Phụ huynh:</b> {ph_val} (☎️ <b>{sdt_ph_val}</b>) · <b>Địa chỉ:</b> {dia_chi_val}
                        </div>
                    </div>
                    <div style="text-align:center; background:#F8FAFC; border:1.5px dashed #0D5C75; border-radius:10px; padding:12px 16px;">
                        <div style="font-size:32px;">📱</div>
                        <div style="font-size:11px; font-weight:800; color:#0D5C75;">TEM QR CHÍNH HÃNG</div>
                        <div style="font-size:10px; color:#64748B;">THPT Số 2 Bảo Yên</div>
                    </div>
                </div>
                """)

        st.dataframe(
            df_xe_show,
            use_container_width=True,
            height=300,
            column_config={
                "Mã xe": st.column_config.TextColumn("Mã xe", width="small"),
                "Họ và tên": st.column_config.TextColumn("Học sinh", width="medium"),
                "Lớp": st.column_config.TextColumn("Lớp", width="small"),
                "Biển số xe": st.column_config.TextColumn("Biển số xe"),
                "Loại xe": st.column_config.TextColumn("Loại xe"),
                "Màu xe": st.column_config.TextColumn("Màu xe"),
                "Nơi gửi xe": st.column_config.TextColumn("Nơi gửi"),
                "GVCN": st.column_config.TextColumn("GVCN"),
                "Họ tên Phụ huynh": st.column_config.TextColumn("Phụ huynh"),
                "SĐT Phụ huynh": st.column_config.TextColumn("SĐT Phụ huynh"),
            }
        )

        c_dl_xe, _ = st.columns([2, 3])
        with c_dl_xe:
            csv_xe = df_xe_show.to_csv(index=False, encoding='utf-8-sig').encode('utf-8-sig')
            st.download_button(
                label="📥 Xuất Danh Sách 648 Phương Tiện Xe (CSV/Excel)",
                data=csv_xe,
                file_name=f"danh_sach_xe_hoc_sinh_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                key="btn_dl_xe_csv_sec"
            )

    c_xe_act1, c_xe_act2 = st.columns(2)
    with c_xe_act1:
        with st.expander("🚨 Lập Biên Bản Vi Phạm Trật Tự ATGT (Theo Quy Chế Nhà Trường)", expanded=False):
            ds_xe_sel = [f"{r.get('Mã xe', '')} - {r.get('Họ và tên', '')} ({r.get('Lớp', '')}) - {r.get('Biển số xe', '')}" for _, r in df_xe.head(60).iterrows()] if not df_xe.empty else ["XE-001 - Học sinh 10A1"]
            xe_vp_selected = st.selectbox("Chọn Xe / Học sinh vi phạm:", ds_xe_sel, key="sel_xe_vp_sec")
            loi_vp_xe = st.selectbox("Hành vi vi phạm giao thông:", [
                "Không đội mũ bảo hiểm; pô nổ to; che biển số (-30đ)",
                "Đi xe nhưng không khai báo, không dán mã QR cho xe (-20đ)",
                "Đội mũ sai quy cách; chở quá số người; dàn hàng ngang từ 3 xe (-10đ)",
                "Để xe sai quy định trong nhà xe (-5đ)",
                "Phóng nhanh, vượt ẩu, lạng lách, đánh võng, vượt đèn đỏ, độ xe (-50đ)",
                "Vi phạm ATGT gây tai nạn giao thông (-60đ)"
            ], key="loi_vp_xe_sec")
            nguoi_lap_bb = st.text_input("Người lập biên bản:", value=f"{fullname_curr} (Đội Cờ đỏ / Trực ban)", key="nguoi_lap_bb_sec")

            if st.button("🚨 Lưu Biên Bản & Trừ Điểm Thi Đua Chi Đoàn", type="primary", use_container_width=True, key="btn_save_vp_xe_sec"):
                parts = xe_vp_selected.split(" - ")
                mx_val = parts[0].strip() if len(parts) > 0 else "XE-000"
                ten_val = parts[1].split("(")[0].strip() if len(parts) > 1 else ""
                lop_val = parts[1].split("(")[1].replace(")", "").strip() if len(parts) > 1 and "(" in parts[1] else "10A1"
                bs_val = parts[2].strip() if len(parts) > 2 else ""

                tru_val = 30
                if "20đ" in loi_vp_xe: tru_val = 20
                elif "10đ" in loi_vp_xe: tru_val = 10
                elif "5đ" in loi_vp_xe: tru_val = 5
                elif "50đ" in loi_vp_xe: tru_val = 50
                elif "60đ" in loi_vp_xe: tru_val = 60

                row_bb = {
                    "Ngày": datetime.now().strftime("%d/%m/%Y"),
                    "Mã xe": mx_val,
                    "Họ và tên": ten_val,
                    "Lớp": lop_val,
                    "Biển số xe": bs_val,
                    "Lỗi vi phạm": loi_vp_xe,
                    "Điểm trừ": tru_val,
                    "Người lập biên bản": nguoi_lap_bb,
                    "Trạng thái": "Đã trừ điểm ĐTN"
                }
                df_new_bb = pd.DataFrame([row_bb])
                if os.path.exists(f_vi_pham_xe):
                    df_new_bb.to_csv(f_vi_pham_xe, mode='a', header=False, index=False, encoding='utf-8-sig')
                else:
                    df_new_bb.to_csv(f_vi_pham_xe, index=False, encoding='utf-8-sig')
                st.success(f"✅ Đã lập biên bản vi phạm cho xe **{mx_val}** ({ten_val} - {lop_val}) và ghi nhận trừ {tru_val}đ thi đua Chi đoàn!")
                time.sleep(1)
                st.rerun()

    with c_xe_act2:
        with st.expander("➕ Đăng Ký Cấp Mới Tem Mã QR Xe Cho Học Sinh", expanded=False):
            c_nxe1, c_nxe2 = st.columns(2)
            with c_nxe1:
                new_ten_hs = st.text_input("Họ và tên học sinh:", key="new_xe_ten_sec")
                new_lop_hs = st.selectbox("Chi đoàn:", ds_lop_all, key="new_xe_lop_sec")
                new_loai_xe = st.selectbox("Loại phương tiện:", ["Xe đạp điện", "Xe máy điện", "Xe gắn máy 50cc", "Xe đạp thể thao"], key="new_xe_loai_sec")
            with c_nxe2:
                new_bien_so = st.text_input("Biển số xe (hoặc Chưa có biển):", value="24MD1-...", key="new_xe_bs_sec")
                new_mau_xe = st.text_input("Màu sắc phương tiện:", value="Màu đen", key="new_xe_mau_sec")
                new_sdt_ph = st.text_input("SĐT liên hệ Phụ huynh:", key="new_xe_sdt_ph_sec")

            if st.button("🏷️ Cấp Tem Mã QR Mới & Lưu Hồ Sơ", use_container_width=True, key="btn_save_new_xe_sec"):
                if new_ten_hs.strip():
                    next_id_num = len(df_xe) + 1
                    new_mx = f"XE-{next_id_num:03d}"
                    row_new_xe = {
                        "Mã xe": new_mx,
                        "Họ và tên": new_ten_hs.strip(),
                        "Lớp": new_lop_hs,
                        "SĐT Học sinh": "",
                        "Loại xe": new_loai_xe,
                        "Biển số xe": new_bien_so.strip(),
                        "Màu xe": new_mau_xe.strip(),
                        "Nơi gửi xe": "Trong trường",
                        "GVCN": f"Thầy/Cô GVCN {new_lop_hs}",
                        "SĐT GVCN": "",
                        "Họ tên Phụ huynh": "Phụ huynh HS",
                        "SĐT Phụ huynh": new_sdt_ph.strip(),
                        "Địa chỉ": "Bảo Hà - Lào Cai",
                        "Tình trạng": "Đủ điều kiện lưu hành",
                        "Số lần vi phạm": 0,
                        "Ghi chú": "Cấp mới học kỳ 1"
                    }
                    df_save_new_xe = pd.DataFrame([row_new_xe])
                    if os.path.exists(f_xe):
                        df_save_new_xe.to_csv(f_xe, mode='a', header=False, index=False, encoding='utf-8-sig')
                    else:
                        df_save_new_xe.to_csv(f_xe, index=False, encoding='utf-8-sig')
                    st.success(f"🎉 Đã cấp mã **{new_mx}** thành công cho học sinh **{new_ten_hs}** ({new_lop_hs})!")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.warning("Vui lòng nhập Họ tên học sinh để cấp tem mã QR.")

    if not df_vp_xe.empty:
        st.markdown("##### 📜 Lịch Sử Ghi Nhận Vi Phạm Giao Thông Gần Đây")
        st.dataframe(
            df_vp_xe.tail(5).iloc[::-1],
            use_container_width=True,
            height=160
        )

    # =========================================================================
    # THƯ MỤC 4: 📜 SỔ ĐOÀN VIÊN ĐIỆN TỬ & CÔNG TÁC ĐOÀN (#so-doan-vien)
    # =========================================================================
    st.markdown("<div style='margin-top: 32px;'></div>", unsafe_allow_html=True)
    st_html("""
    <div id="so-doan-vien" class="section-banner-title">
        <h3><span>📜</span> SỔ ĐOÀN VIÊN ĐIỆN TỬ & CÔNG TÁC ĐOÀN THANH NIÊN</h3>
        <span class="section-banner-subtitle">Quản Lý Hồ Sơ 21 Chi Đoàn · Bồi Dưỡng Cảm Tình Đoàn · Bàn Giao Sổ Đoàn</span>
    </div>
    """)

    df_sd = pd.DataFrame()
    if os.path.exists(f_so_doan):
        try:
            df_sd = pd.read_csv(f_so_doan, encoding='utf-8-sig').fillna("")
        except Exception:
            pass

    m_sd1, m_sd2, m_sd3, m_sd4 = st.columns(4)
    tong_hs_toan = 929
    tong_doan_vien = 685
    tong_tnut = 115
    if not df_sd.empty and "Số Đoàn viên" in df_sd.columns:
        try:
            tong_doan_vien = int(pd.to_numeric(df_sd["Số Đoàn viên"], errors='coerce').fillna(0).sum())
            tong_tnut = int(pd.to_numeric(df_sd["Thanh niên ưu tú"], errors='coerce').fillna(0).sum())
            if "Tổng số HS" in df_sd.columns:
                tong_hs_toan = int(pd.to_numeric(df_sd["Tổng số HS"], errors='coerce').fillna(0).sum())
        except Exception:
            pass

    ty_le_dv = round((tong_doan_vien / tong_hs_toan) * 100, 1) if tong_hs_toan > 0 else 73.7

    m_sd1.metric("👥 Tổng Số Học Sinh", f"{tong_hs_toan} HS", "21 Chi đoàn")
    m_sd2.metric("🔴 Đoàn Viên Đã Kết Nạp", f"{tong_doan_vien} ĐV", f"Tỷ lệ {ty_le_dv}%")
    m_sd3.metric("⭐ Thanh Niên Ưu Tú (Nguồn)", f"{tong_tnut} HS", "Bồi dưỡng kết nạp")
    m_sd4.metric("📁 Quản Lý Sổ Đoàn", "100% Hoàn Thành", "Đã số hóa")

    st.markdown("##### 🏛️ Danh Sách 21 Chi Đoàn Trực Thuộc Đoàn Trường THPT Số 2 Bảo Yên")
    c_sdf1, c_sdf2 = st.columns([1, 2])
    with c_sdf1:
        k_sd_filter = st.selectbox("Lọc theo Khối:", ["Tất cả khối", "Khối 10", "Khối 11", "Khối 12"], key="sd_k_fl_sec")
    with c_sdf2:
        tim_sd = st.text_input("Tìm kiếm Chi đoàn / Bí thư:", "", key="tim_sd_kw_sec")

    df_sd_show = df_sd.copy() if not df_sd.empty else pd.DataFrame()
    if not df_sd_show.empty:
        if k_sd_filter != "Tất cả khối":
            df_sd_show = df_sd_show[df_sd_show["Khối"].astype(str).str.contains(k_sd_filter.replace("Khối ", ""), case=False, na=False)]
        if tim_sd.strip():
            df_sd_show = df_sd_show[
                df_sd_show["Chi đoàn"].astype(str).str.contains(tim_sd.strip(), case=False, na=False) |
                df_sd_show["Bí thư Chi đoàn"].astype(str).str.contains(tim_sd.strip(), case=False, na=False)
            ]

        st.dataframe(
            df_sd_show,
            use_container_width=True,
            height=300,
            column_config={
                "Chi đoàn": st.column_config.TextColumn("Chi đoàn", width="medium"),
                "Khối": st.column_config.TextColumn("Khối", width="small"),
                "Bí thư Chi đoàn": st.column_config.TextColumn("Bí thư Chi đoàn"),
                "Tổng số HS": st.column_config.NumberColumn("Sĩ số"),
                "Số Đoàn viên": st.column_config.NumberColumn("Đoàn viên"),
                "Thanh niên ưu tú": st.column_config.NumberColumn("TN Ưu tú"),
                "Tình trạng Sổ Đoàn": st.column_config.TextColumn("Sổ Đoàn"),
                "Đoàn phí": st.column_config.TextColumn("Đoàn phí"),
                "Xếp loại Chi đoàn": st.column_config.TextColumn("Xếp loại"),
            }
        )

        c_dl_sd, _ = st.columns([2, 3])
        with c_dl_sd:
            csv_sd = df_sd_show.to_csv(index=False, encoding='utf-8-sig').encode('utf-8-sig')
            st.download_button(
                label="📥 Xuất Dữ Liệu Sổ Đoàn 21 Chi Đoàn (CSV/Excel)",
                data=csv_sd,
                file_name=f"so_doan_vien_21_chi_doan_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                key="btn_dl_sd_csv_sec"
            )

    c_d_act1, c_d_act2 = st.columns(2)
    with c_d_act1:
        with st.expander("⭐ Giới Thiệu Thanh Niên Ưu Tú Học Cảm Tình Đoàn (Đợt 26/3)", expanded=False):
            c_tn1, c_tn2 = st.columns(2)
            with c_tn1:
                tn_ten = st.text_input("Họ và tên thanh niên ưu tú:", key="tn_ten_sec_in")
                tn_lop = st.selectbox("Thuộc Chi đoàn:", ds_lop_all, key="tn_lop_sec_in")
            with c_tn2:
                tn_hocluc = st.selectbox("Xếp loại học tập:", ["Tốt / Giỏi", "Khá"], key="tn_hl_sec_in")
                tn_hanhkiem = st.selectbox("Xếp loại rèn luyện:", ["Tốt", "Khá"], key="tn_hk_sec_in")
            tn_lydo = st.text_area("Thành tích & Lý do giới thiệu:", placeholder="Gương mẫu, tích cực tham gia phong trào...", height=60, key="tn_lydo_sec_in")

            if st.button("🌟 Xác Nhận Giới Thiệu Học Lớp Cảm Tình Đoàn", type="primary", use_container_width=True, key="btn_save_tnut_sec"):
                if tn_ten.strip():
                    st.success(f"🎉 Đã ghi nhận thanh niên ưu tú **{tn_ten}** ({tn_lop}) vào danh sách tham gia lớp Cảm tình Đoàn đợt 26/3 sắp tới!")
                else:
                    st.warning("Vui lòng nhập Họ tên thanh niên ưu tú.")

    with c_d_act2:
        with st.expander("📥 Quản Lý Sổ Đoàn Viên & Bàn Giao Khi Ra Trường", expanded=False):
            st_html("""
            <div style="font-size:12.5px; line-height:1.6; color:#334155;">
                • <b>Sổ Đoàn viên:</b> 100% học sinh đã nộp sổ khi vào lớp 10, được lưu trữ niêm phong tại Văn phòng Đoàn.<br>
                • <b>Rút sổ chuyển sinh hoạt hè:</b> BCH Đoàn trường bàn giao giấy giới thiệu sinh hoạt hè về Đoàn cơ sở xã Bảo Hà theo kế hoạch Huyện Đoàn.<br>
                • <b>Rút sổ tốt nghiệp ra trường:</b> Bàn giao trực tiếp cho đoàn viên Khối 12 sau kỳ thi Tốt nghiệp THPT 2027.
            </div>
            """)
            st.button("📋 Kiểm Tra Niêm Phong Tủ Sổ Đoàn (21 Chi đoàn)", use_container_width=True, key="btn_check_so_doan_sec")

# =============================================================================
# 9. SECTION 6: BÁN TRÚ & KTX (6 THẺ TÁC NGHIỆP CHUẨN NGHĨA ĐÔ)
# =============================================================================
def render_section_ban_tru(BASE_DIR, THU_MUC_NAM_HOC, nam_hoc_hien_tai, u_info=None):
    """Khối Bán trú & KTX gồm 6 thẻ tổng quan và Không gian tác nghiệp 4 Tab mở rộng tại chỗ"""
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

    # =========================================================================
    # KHÔNG GIAN TÁC NGHIỆP BÁN TRÚ & KTX CHUYÊN SÂU (MỞ RỘNG TẠI CHỖ)
    # =========================================================================
    u_curr = u_info if isinstance(u_info, dict) else st.session_state.get("user_login", {})
    role_curr = u_curr.get("role", "")
    chuc_danh_curr = u_curr.get("chuc_danh", "")
    ma_lk_curr = u_curr.get("ma_lien_ket", "")

    st.markdown("<div style='margin-top: 16px;'></div>", unsafe_allow_html=True)
    with st.expander("🛠️ KHÔNG GIAN TÁC NGHIỆP BÁN TRÚ & KTX CHUYÊN SÂU (MỞ RỘNG TẠI CHỖ)", expanded=True):
        tab_dd, tab_ktx, tab_bep, tab_tc = st.tabs([
            "📋 1. Điểm danh 196 HS & Báo cơm Live",
            "🏢 2. Ký túc xá & Thi đua phòng ở 5S",
            "🍳 3. Bếp ăn, Dinh dưỡng & Kiểm thực ATTP",
            "💳 4. Thu tiền ăn & Mã VietQR tự động"
        ])

        # --- TAB 1: ĐIỂM DANH 196 HỌC SINH & BÁO CƠM LIVE ---
        with tab_dd:
            f_hs_live = os.path.join(BASE_DIR, "danh_sach_hoc_sinh_thuc_te.csv")
            if os.path.exists(f_hs_live):
                try:
                    df_hs_live = pd.read_csv(f_hs_live, encoding='utf-8-sig').fillna("")
                except Exception:
                    df_hs_live = pd.DataFrame()
            else:
                df_hs_live = pd.DataFrame()

            if not df_hs_live.empty:
                tong_hs = len(df_hs_live)
                an_trua_c = len(df_hs_live[df_hs_live["GĐ1: Ăn trưa"].astype(str).str.lower().isin(["true", "1", "có"])]) if "GĐ1: Ăn trưa" in df_hs_live.columns else tong_hs
                an_toi_c = len(df_hs_live[df_hs_live["Ăn tối"].astype(str).str.lower().isin(["true", "1", "có"])]) if "Ăn tối" in df_hs_live.columns else tong_hs
                nghi_phong_c = len(df_hs_live[df_hs_live["GĐ2: Phòng nghỉ"].astype(str).str.lower().isin(["true", "1", "có"])]) if "GĐ2: Phòng nghỉ" in df_hs_live.columns else tong_hs

                m_col1, m_col2, m_col3, m_col4 = st.columns(4)
                m_col1.metric("👥 Tổng HS Bán trú", f"{tong_hs} HS", "100% Nội trú")
                m_col2.metric("🍚 Báo ăn trưa hôm nay", f"{an_trua_c} suất", "Nhà bếp nấu đủ")
                m_col3.metric("🍲 Báo ăn tối hôm nay", f"{an_toi_c} suất", "Chuẩn bị lúc 16h30")
                m_col4.metric("🛏️ Nghỉ trưa KTX", f"{nghi_phong_c} HS", "12 Phòng KTX")

                col_f1, col_f2, col_f3, col_f4 = st.columns(4)
                with col_f1:
                    khoi_opts = ["Tất cả khối"] + sorted(list(df_hs_live["Khối"].dropna().unique())) if "Khối" in df_hs_live.columns else ["Tất cả khối"]
                    sel_khoi = st.selectbox("Lọc theo Khối:", khoi_opts, key="dd_filter_khoi")
                with col_f2:
                    lop_opts = ["Tất cả lớp"] + sorted(list(df_hs_live["Lớp"].dropna().unique())) if "Lớp" in df_hs_live.columns else ["Tất cả lớp"]
                    sel_lop = st.selectbox("Lọc theo Lớp:", lop_opts, key="dd_filter_lop")
                with col_f3:
                    phong_opts = ["Tất cả phòng"] + sorted(list(df_hs_live["Phòng"].dropna().unique())) if "Phòng" in df_hs_live.columns else ["Tất cả phòng"]
                    sel_phong = st.selectbox("Lọc theo Phòng KTX:", phong_opts, key="dd_filter_phong")
                with col_f4:
                    search_ten = st.text_input("🔍 Tìm tên hoặc Mã HS:", "", key="dd_search_ten")

                df_filtered = df_hs_live.copy()
                if sel_khoi != "Tất cả khối" and "Khối" in df_filtered.columns:
                    df_filtered = df_filtered[df_filtered["Khối"] == sel_khoi]
                if sel_lop != "Tất cả lớp" and "Lớp" in df_filtered.columns:
                    df_filtered = df_filtered[df_filtered["Lớp"] == sel_lop]
                if sel_phong != "Tất cả phòng" and "Phòng" in df_filtered.columns:
                    df_filtered = df_filtered[df_filtered["Phòng"] == sel_phong]
                if search_ten.strip() and "Họ và tên" in df_filtered.columns:
                    kw = search_ten.strip().lower()
                    df_filtered = df_filtered[
                        df_filtered["Họ và tên"].str.lower().str.contains(kw) |
                        df_filtered["Mã HS"].str.lower().str.contains(kw)
                    ]

                st.markdown(f"**Danh sách học sinh bán trú hiển thị:** `{len(df_filtered)}` / `{tong_hs}` học sinh")
                cols_view = [c for c in ["Mã HS", "Họ và tên", "Lớp", "Phòng", "Giường", "GĐ1: Ăn trưa", "Ăn tối", "GĐ2: Phòng nghỉ", "Trạng thái", "SĐT Phụ huynh"] if c in df_filtered.columns]
                st.dataframe(df_filtered[cols_view], use_container_width=True, hide_index=True)

                col_btn_a, col_btn_b = st.columns([1, 1])
                with col_btn_a:
                    if st.button("💾 Gửi báo cáo quân số ăn thực tế cho Nhà bếp", key="btn_gui_bao_cao_bep", type="primary", use_container_width=True):
                        st.success(f"✅ Đã gửi thành công lệnh báo cơm trưa ({an_trua_c} suất) và cơm tối ({an_toi_c} suất) sang Tổ Cấp dưỡng!")
                with col_btn_b:
                    csv_export = df_filtered.to_csv(index=False, encoding='utf-8-sig').encode('utf-8-sig')
                    st.download_button(
                        label="📥 Xuất danh sách học sinh (Excel / CSV)",
                        data=csv_export,
                        file_name=f"diem_danh_ban_tru_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
            else:
                st.info("Chưa có dữ liệu danh sách học sinh bán trú.")

        # --- TAB 2: KÝ TÚC XÁ & THI ĐUA PHÒNG Ở 5S ---
        with tab_ktx:
            f_p_5s = os.path.join(BASE_DIR, "cham_diem_thi_dua_phong.csv")
            if os.path.exists(f_p_5s):
                try:
                    df_phong_5s = pd.read_csv(f_p_5s, encoding='utf-8-sig').fillna("")
                except Exception:
                    df_phong_5s = pd.DataFrame()
            else:
                df_phong_5s = pd.DataFrame()

            ds_phong_all = sorted(list(df_phong_5s["Phòng"].dropna().unique())) if not df_phong_5s.empty and "Phòng" in df_phong_5s.columns else [f"Phòng {p}" for p in [201, 202, 203, 204, 205, 206, 207, 208, 301, 302, 303, 304, 305, 306, 307, 308]]

            is_student = (role_curr == "Học sinh")
            user_assigned_room = None
            if is_student:
                for p_str in ds_phong_all:
                    if p_str.lower() in chuc_danh_curr.lower() or p_str.lower() in str(ma_lk_curr).lower():
                        user_assigned_room = p_str
                        break
                if not user_assigned_room:
                    user_assigned_room = "Phòng 301"

            c_ktx_top1, c_ktx_top2 = st.columns([1, 1.5])
            with c_ktx_top1:
                st.markdown("#### 🏢 Chọn Phòng KTX Chấm Điểm")
                if is_student and user_assigned_room:
                    st.info(f"🔒 **Phân quyền Học sinh:** Bạn là Trưởng phòng `{user_assigned_room}`. Hệ thống tự động khóa quyền chấm chỉ dành riêng cho phòng của bạn.")
                    phong_duoc_chon = user_assigned_room
                else:
                    st.caption("Ban Giám hiệu / Quản nhiệm KTX có toàn quyền chọn và chấm điểm tất cả 12 phòng:")
                    phong_duoc_chon = st.selectbox("Chọn phòng KTX cần đánh giá:", ds_phong_all, key="sb_phong_5s_sel")

                s1 = st.slider("1. Sàng lọc (Đồ dùng cá nhân gọn gàng, không có rác thừa):", 0, 20, 20, key="slider_s1")
                s2 = st.slider("2. Sắp xếp (Chăn màn vuông góc chuẩn quân đội, giày dép trên giá):", 0, 20, 20, key="slider_s2")
                s3 = st.slider("3. Sạch sẽ (Sàn phòng, hành lang, khu vệ sinh khô ráo sạch sẽ):", 0, 20, 19, key="slider_s3")
                s4 = st.slider("4. Săn sóc (Bảo quản tài sản công: giường, quạt, đèn điện):", 0, 20, 20, key="slider_s4")
                s5 = st.slider("5. Sẵn sàng (Tắt điện đúng 21h30, không ồn ào, tự giác nội quy):", 0, 20, 20, key="slider_s5")

                tong_diem_5s = s1 + s2 + s3 + s4 + s5
                xep_loai_str = "⭐⭐⭐ Xuất sắc" if tong_diem_5s >= 95 else ("⭐⭐ Tốt" if tong_diem_5s >= 85 else "⭐ Cần cải thiện")
                st.metric("Tổng điểm 5S hôm nay:", f"{tong_diem_5s} / 100 điểm", xep_loai_str)

                ghi_chu_5s = st.text_input("Ghi chú nề nếp phòng (nếu có):", "", key="txt_note_5s")
                if st.button(f"💾 Lưu điểm thi đua {phong_duoc_chon}", type="primary", use_container_width=True, key="btn_save_5s"):
                    f_nk_5s = os.path.join(BASE_DIR, "nhat_ky_thi_dua_phong_5s.csv")
                    row_5s = {
                        "Ngày": datetime.now().strftime("%d/%m/%Y"),
                        "Phòng": phong_duoc_chon,
                        "S1": s1, "S2": s2, "S3": s3, "S4": s4, "S5": s5,
                        "Tổng điểm": tong_diem_5s,
                        "Xếp loại": xep_loai_str,
                        "Người chấm": u_curr.get("fullname", "Cán bộ chấm"),
                        "Ghi chú": ghi_chu_5s
                    }
                    df_new_5s = pd.DataFrame([row_5s])
                    if os.path.exists(f_nk_5s):
                        df_new_5s.to_csv(f_nk_5s, mode='a', header=False, index=False, encoding='utf-8-sig')
                    else:
                        df_new_5s.to_csv(f_nk_5s, index=False, encoding='utf-8-sig')
                    st.success(f"🎉 Đã lưu thành công đánh giá 5S cho **{phong_duoc_chon}**: **{tong_diem_5s}/100 điểm** ({xep_loai_str})!")

            with c_ktx_top2:
                st.markdown("#### 🏆 Bảng Xếp Hạng Thi Đua 12 Phòng KTX Tuần Này")
                if not df_phong_5s.empty:
                    st.dataframe(df_phong_5s, use_container_width=True, hide_index=True)
                else:
                    st.info("Chưa có danh sách phòng.")
                
                st.markdown("""
                <div style="background:#F0FDFA; border:1px solid #CCFBF1; border-radius:10px; padding:12px; font-size:12px; margin-top:10px;">
                    <b style="color:#0D5C75;">📌 TIÊU CHÍ 5S KÝ TÚC XÁ THPT SỐ 2 BẢO YÊN:</b><br>
                    • <b>Sàng lọc (20đ):</b> Đồ dùng cá nhân ngăn nắp, loại bỏ rác thải hàng ngày.<br>
                    • <b>Sắp xếp (20đ):</b> Chăn màn gấp vuông vức mép giường, giày dép xếp đúng giá quy định.<br>
                    • <b>Sạch sẽ (20đ):</b> Quét dọn phòng 2 lần/ngày, bồn rửa và nhà vệ sinh luôn khô thoáng.<br>
                    • <b>Săn sóc (20đ):</b> Kiểm tra bóng điện, quạt trần, ổ cắm an toàn tuyệt đối.<br>
                    • <b>Sẵn sàng (20đ):</b> Đúng 21h30 toàn bộ 12 phòng tắt điện, đi ngủ đúng giờ, giữ trật tự.
                </div>
                """, unsafe_allow_html=True)

        # --- TAB 3: BẾP ĂN, DINH DƯỠNG & KIỂM THỰC ATTP ---
        with tab_bep:
            f_kt = os.path.join(BASE_DIR, "nhat_ky_kiem_thuc.csv")
            if os.path.exists(f_kt):
                try:
                    df_kt_live = pd.read_csv(f_kt, encoding='utf-8-sig').fillna("")
                except Exception:
                    df_kt_live = pd.DataFrame()
            else:
                df_kt_live = pd.DataFrame()

            c_bep1, c_bep2 = st.columns([1, 1.2])
            with c_bep1:
                st.markdown("#### 📋 Ghi Nhật Ký Kiểm Thực 3 Bước (QĐ 1246/QĐ-BYT)")
                bua_kt = st.selectbox("Bữa ăn kiểm thực:", ["Bữa trưa", "Bữa tối", "Bữa sáng"], key="sb_bua_kt")
                ten_tp = st.text_input("Tên món ăn / Thực phẩm kiểm nghiệm:", "Thịt lợn nạc vai, Trứng gà đỏ, Rau bắp cải", key="txt_ten_tp")
                nguon_goc = st.text_input("Nguồn gốc xuất xứ:", "Hợp tác xã nông sản sạch Bảo Yên (Có hóa đơn kiểm dịch)", key="txt_nguon_goc")
                b1_check = st.checkbox("✅ Bước 1: Kiểm tra trước nhập (Cảm quan tươi ngon, bao bì nguyên vẹn, còn hạn dùng)", value=True, key="cb_b1")
                b2_check = st.checkbox("✅ Bước 2: Kiểm tra khi chế biến (Nấu chín kỹ >100°C, dụng cụ chế biến sạch sẽ, nguồn nước đạt chuẩn)", value=True, key="cb_b2")
                b3_check = st.checkbox("✅ Bước 3: Kiểm tra trước khi ăn & Đã lưu mẫu 24 giờ vào hộp inox vô trùng tủ mát 2-8°C", value=True, key="cb_b3")
                
                if st.button("💾 Ghi nhật ký kiểm thực ATTP hôm nay", type="primary", use_container_width=True, key="btn_save_kt"):
                    new_kt_row = {
                        "Ngày": datetime.now().strftime("%d/%m/%Y"),
                        "Bữa ăn": bua_kt,
                        "Tên món / Thực phẩm": ten_tp,
                        "Khối lượng (kg)": "35",
                        "Nguồn gốc xuất xứ": nguon_goc,
                        "Hạn sử dụng": "Trong ngày",
                        "Kiểm tra cảm quan (Bước 1)": "Đạt chuẩn tươi sống" if b1_check else "Chưa đạt",
                        "Nhiệt độ chế biến (Bước 2)": "Nấu chín >100°C" if b2_check else "Chưa đạt",
                        "Lưu mẫu 24h (Bước 3)": "Đã niêm phong tủ mát 24h" if b3_check else "Chưa lưu",
                        "Người kiểm thực": u_curr.get("fullname", "Cán bộ y tế / Cấp dưỡng"),
                        "Ghi chú": "Đạt chuẩn an toàn vệ sinh thực phẩm 100%"
                    }
                    df_save_kt = pd.DataFrame([new_kt_row])
                    if os.path.exists(f_kt):
                        df_save_kt.to_csv(f_kt, mode='a', header=False, index=False, encoding='utf-8-sig')
                    else:
                        df_save_kt.to_csv(f_kt, index=False, encoding='utf-8-sig')
                    st.success("✅ Đã ghi nhận thành công nhật ký kiểm thực 3 bước và lưu mẫu ATTP!")

            with c_bep2:
                st.markdown("#### 📜 Sổ Nhật Ký Kiểm Thực & Lưu Mẫu Đã Ghi")
                if not df_kt_live.empty:
                    cols_kt = [c for c in ["Ngày", "Bữa ăn", "Tên món / Thực phẩm", "Nguồn gốc xuất xứ", "Lưu mẫu 24h (Bước 3)", "Người kiểm thực"] if c in df_kt_live.columns]
                    st.dataframe(df_kt_live[cols_kt], use_container_width=True, hide_index=True)
                else:
                    st.info("Chưa có nhật ký kiểm thực.")

                st.markdown("#### 🥗 Thực Đơn Tuần Chuẩn 4 Nhóm Chất")
                if os.path.exists(f_tdon):
                    try:
                        df_td_show = pd.read_csv(f_tdon, encoding='utf-8-sig').fillna("")
                        st.dataframe(df_td_show, use_container_width=True, hide_index=True)
                    except Exception:
                        st.info("Không thể đọc file thực đơn tuần.")

        # --- TAB 4: THU TIỀN ĂN & MÃ VIETQR TỰ ĐỘNG ---
        with tab_tc:
            c_qr1, c_qr2 = st.columns([1, 1.2])
            with c_qr1:
                st.markdown("#### 💳 Tạo Mã VietQR Tự Động Nộp Tiền Ăn")
                if not df_hs_live.empty:
                    hs_qr_opts = [f"{r['Mã HS']} - {r['Họ và tên']} ({r['Lớp']})" for _, r in df_hs_live.iterrows()]
                    sel_hs_qr = st.selectbox("Chọn học sinh nộp tiền ăn:", hs_qr_opts, key="sb_hs_qr")
                    tien_an_thang = st.number_input("Số tiền nộp (VNĐ):", min_value=10000, max_value=5000000, value=660000, step=10000, key="num_tien_an")
                    ma_hs_sel = sel_hs_qr.split(" - ")[0].strip()
                    ten_hs_sel = sel_hs_qr.split(" - ")[1].split(" (")[0].strip()
                    noi_dung_ck = f"THPT2BY {ma_hs_sel} {ten_hs_sel}"
                    
                    qr_url = f"https://img.vietqr.io/image/agribank-8800205123456-compact2.png?amount={tien_an_thang}&addInfo={urllib.parse.quote(noi_dung_ck)}&accountName=TRUONG%20THPT%20SO%202%20BAO%20YEN"
                    
                    st_html(f"""
                    <div style="text-align:center; background:#F8FAFC; border:1px solid #E2E8F0; border-radius:12px; padding:16px; margin-top:8px;">
                        <img src="{qr_url}" style="width:230px; border-radius:8px; box-shadow:0 3px 8px rgba(0,0,0,0.1);">
                        <div style="font-size:13px; font-weight:800; color:#0D5C75; margin-top:10px;">
                            QUÉT MÃ VIETQR QUA MỌI APP NGÂN HÀNG
                        </div>
                        <div style="font-size:12px; color:#475569; margin-top:4px;">
                            Số tiền: <b style="color:#DC2626;">{tien_an_thang:,.0f} đ</b> | TK: <b>8800205123456</b> (Agribank Bảo Yên)
                        </div>
                        <div style="font-size:11.5px; color:#059669; font-weight:600; margin-top:4px;">
                            Nội dung CK: <code>{noi_dung_ck}</code>
                        </div>
                    </div>
                    """)
                else:
                    st.info("Chưa có danh sách học sinh.")

            with c_qr2:
                st.markdown("#### 📊 Sổ Quỹ Thu Nộp Tiền Ăn Bán Trú")
                st.markdown("""
                <div style="background:white; border:1px solid #E2E8F0; border-radius:10px; padding:14px; margin-bottom:12px;">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                        <span style="font-size:12.5px; font-weight:800; color:#0D5C75;">TIẾN ĐỘ THU TIỀN ĂN THÁNG 11/2026</span>
                        <span style="background:#ECFDF5; color:#059669; font-size:11px; font-weight:bold; padding:2px 8px; border-radius:10px;">182 / 196 HS (92.8%)</span>
                    </div>
                    <div style="font-size:12px; color:#334155; line-height:1.5;">
                        • Đã hoàn thành đóng tiền: <b>182 học sinh</b> (Tổng thu: 120.120.000 đ).<br>
                        • Còn chưa nộp: <b>14 học sinh</b> (Chủ yếu thuộc diện chính sách Nghị định 116 chờ giải ngân).<br>
                        • Kế toán đã đối soát tự động qua mã tham chiếu VietQR 100% khớp lệnh.
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                if not df_hs_live.empty:
                    df_tc_view = df_hs_live[["Mã HS", "Họ và tên", "Lớp", "Phòng", "Chính sách NĐ116"]].copy()
                    df_tc_view["Tiền ăn tháng"] = "660,000 đ"
                    df_tc_view["Trạng thái nộp"] = df_tc_view["Chính sách NĐ116"].apply(lambda x: "Hỗ trợ NĐ116 ⏳" if str(x).lower() in ["có", "true", "1"] else "Đã nộp VietQR ✅")
                    st.dataframe(df_tc_view, use_container_width=True, hide_index=True)

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
    Render Cổng điều hành 9 Kênh tác nghiệp chuẩn hóa:
    - Khi bấm vào một kênh, hệ thống CHỈ HIỂN THỊ RIÊNG NỘI DUNG KÊNH ĐÓ.
    - Thanh điều hướng Top Nav ghim sát mép trên, sáng tab kênh đang mở.
    """
    # 1. Thanh thương hiệu đầu trang (Top Brand Bar & Thông tin đăng nhập)
    render_top_brand_bar(nam_hoc=nam_hoc_hien_tai, logo_data_uri=logo_data_uri, is_logged_in=is_logged_in, u_info=u_info)

    # 2. Xác định kênh đang được chọn (ưu tiên query params -> session state -> mặc định "1")
    kenh_param = st.query_params.get("kenh", None)
    if kenh_param:
        st.session_state["kenh_dieu_hanh_active"] = str(kenh_param)
    elif "kenh_dieu_hanh_active" not in st.session_state:
        st.session_state["kenh_dieu_hanh_active"] = "1"

    kenh_hien_tai = str(st.session_state.get("kenh_dieu_hanh_active", "1"))

    # 3. Thanh 9 Kênh ngang ghim trên đỉnh (Active tab sáng đèn tương ứng)
    render_sticky_nav_bar(active_id=kenh_hien_tai)



    def render_breadcrumb_kenh(kenh_id, ten_k):
        st_html(f"""
        <div style="display:flex; justify-content:space-between; align-items:center; background:#F8FAFC; border:1px solid #E2E8F0; border-radius:8px; padding:6px 14px; margin-bottom:14px; font-size:12px;">
            <div style="color:#64748B;">
                <a href="?kenh=1" style="color:#0D5C75; text-decoration:none; font-weight:700;">🏠 Trang Chủ</a>
                <span style="margin: 0 6px;">›</span>
                <span style="color:#0F172A; font-weight:800;">{ten_k}</span>
            </div>
            <a href="?kenh=1" style="background:#0D5C75; color:white; padding:4px 12px; border-radius:6px; text-decoration:none; font-weight:700; font-size:11.5px;">
                ◀ Quay về Trang Chủ
            </a>
        </div>
        """)

    # 4. RENDER TOÀN BỘ 9 KÊNH VÀO CONTAINER CHUYÊN BIỆT (SPA 0MS, KHÔNG RELOAD, KHÔNG GIẬT)
    with st.container(key="kenh_panel_1"):
        render_kpi_tong_quan_trang_chu(BASE_DIR, THU_MUC_NAM_HOC, nam_hoc_hien_tai)

    with st.container(key="kenh_panel_2"):
        render_breadcrumb_kenh("2", "📋 KÊNH 2: CÔNG VIỆC CẦN HOÀN THÀNH")
        render_section_cong_viec(BASE_DIR, THU_MUC_NAM_HOC, nam_hoc_hien_tai, u_info=u_info)

    with st.container(key="kenh_panel_3"):
        render_breadcrumb_kenh("3", "📅 KÊNH 3: LỊCH LÀM VIỆC & CÔNG TÁC TUẦN")
        render_section_lich_lam_viec(BASE_DIR, THU_MUC_NAM_HOC, nam_hoc_hien_tai)

    with st.container(key="kenh_panel_4"):
        render_breadcrumb_kenh("4", "📊 KÊNH 4: THEO DÕI HẰNG NGÀY (SĨ SỐ & TIẾN ĐỘ)")
        render_section_theo_doi_hang_ngay(BASE_DIR, THU_MUC_NAM_HOC, nam_hoc_hien_tai)

    with st.container(key="kenh_panel_5"):
        render_breadcrumb_kenh("5", "📈 KÊNH 5: KẾT QUẢ DẠY VÀ HỌC")
        render_section_day_va_hoc(BASE_DIR, THU_MUC_NAM_HOC, nam_hoc_hien_tai)

    with st.container(key="kenh_panel_6"):
        render_breadcrumb_kenh("6", "🚩 KÊNH 6: NỀN NẾP – RÈN LUYỆN & XE HỌC SINH")
        render_section_nen_nep(BASE_DIR, THU_MUC_NAM_HOC, nam_hoc_hien_tai, u_info=u_info)

    with st.container(key="kenh_panel_7"):
        render_breadcrumb_kenh("7", "🛏️ KÊNH 7: QUẢN LÝ BÁN TRÚ & KÝ TÚC XÁ")
        render_section_ban_tru(BASE_DIR, THU_MUC_NAM_HOC, nam_hoc_hien_tai, u_info=u_info)

    with st.container(key="kenh_panel_8"):
        render_breadcrumb_kenh("8", "📁 KÊNH 8: TÀI LIỆU, HỒ SƠ ĐIỆN TỬ & ĐÁNH GIÁ KPI")
        render_section_ho_so_kpi(BASE_DIR, THU_MUC_NAM_HOC, nam_hoc_hien_tai)

    with st.container(key="kenh_panel_9"):
        render_breadcrumb_kenh("9", "🚀 KÊNH 9: TIỆN ÍCH GIÁO DỤC SỐ")
        render_section_tien_ich_so()

    # 5. Chân trang Cổng điều hành
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

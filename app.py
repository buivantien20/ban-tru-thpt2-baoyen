import streamlit as st
import pandas as pd
from datetime import date, datetime
import os
import socket
import urllib.parse
import base64
from PIL import Image

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

FILE_LOGO = os.path.join(BASE_DIR, "logo_192.png")
logo_pil = Image.open(FILE_LOGO) if os.path.exists(FILE_LOGO) else "🏫"

# Đọc base64 của logo để nhúng biểu tượng Web App (Apple Touch Icon & Android Favicon)
def lay_logo_base64(duong_dan):
    try:
        with open(duong_dan, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")
    except Exception:
        return ""

logo_b64 = lay_logo_base64(FILE_LOGO)
logo_data_uri = f"data:image/png;base64,{logo_b64}" if logo_b64 else ""

# ========================================================
# 1. CẤU HÌNH HỆ THỐNG QUẢN LÝ BÁN TRÚ THPT SỐ 2 BẢO YÊN
# ========================================================
st.set_page_config(
    page_title="Bán Trú - THPT số 2 Bảo Yên",
    page_icon=logo_pil,
    layout="wide",
    initial_sidebar_state="expanded"
)

FILE_DU_LIEU_THUC_TE = os.path.join(BASE_DIR, "danh_sach_hoc_sinh_thuc_te.csv")
FILE_TAI_KHOAN = os.path.join(BASE_DIR, "tai_khoan_nguoi_dung.csv")
FILE_THI_DUA = os.path.join(BASE_DIR, "cham_diem_thi_dua_phong.csv")
FILE_KIEM_THUC = os.path.join(BASE_DIR, "nhat_ky_kiem_thuc.csv")
FILE_THUC_DON = os.path.join(BASE_DIR, "thuc_don_tuan.csv")
FILE_XIN_VE = os.path.join(BASE_DIR, "lich_su_xin_ve.csv")
FILE_TUNNEL = os.path.join(BASE_DIR, "current_tunnel_url.txt")

# Hàm lấy IP chuẩn xác
def lay_ip_may_tinh():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
        s.close()
        if ip and not ip.startswith("127."):
            return ip
    except Exception:
        pass
    try:
        hostname = socket.gethostname()
        ip_list = socket.gethostbyname_ex(hostname)[2]
        for ip_cand in ip_list:
            if not ip_cand.startswith("127.") and not ip_cand.startswith("169.254"):
                return ip_cand
    except Exception:
        pass
    return "127.0.0.1"

ip_hien_tai = lay_ip_may_tinh()
duong_dan_app_mobile = f"http://{ip_hien_tai}:8501"

# Đọc link online cloudflare nếu có
duong_dan_online = ""
if os.path.exists(FILE_TUNNEL):
    try:
        with open(FILE_TUNNEL, "r", encoding="utf-8") as f:
            duong_dan_online = f.read().strip()
    except Exception:
        pass

# CSS giao diện tối ưu di động và thẻ trực quan kèm biểu tượng App
st.markdown(f"""
<style>
    @media (max-width: 768px) {{
        .main-header {{ font-size: 20px !important; }}
        .stMetric {{ padding: 4px !important; }}
        div[data-testid="stHorizontalBlock"] {{ flex-wrap: wrap !important; }}
    }}
    .badge-bgh {{ background-color: #DC2626; color: white; padding: 3px 10px; border-radius: 12px; font-weight: bold; font-size: 13px; }}
    .badge-qn {{ background-color: #2563EB; color: white; padding: 3px 10px; border-radius: 12px; font-weight: bold; font-size: 13px; }}
    .badge-kt {{ background-color: #059669; color: white; padding: 3px 10px; border-radius: 12px; font-weight: bold; font-size: 13px; }}
    .badge-bep {{ background-color: #D97706; color: white; padding: 3px 10px; border-radius: 12px; font-weight: bold; font-size: 13px; }}
    .badge-ph {{ background-color: #7C3AED; color: white; padding: 3px 10px; border-radius: 12px; font-weight: bold; font-size: 13px; }}
    .badge-hs {{ background-color: #0284C7; color: white; padding: 3px 10px; border-radius: 12px; font-weight: bold; font-size: 13px; }}
</style>

<script>
(function() {{
    try {{
        const head = window.parent.document.head;
        const logoUri = "{logo_data_uri}";
        if (logoUri) {{
            // Cài đặt icon Apple Touch Icon cho iOS (iPhone Safari)
            let appleIcon = head.querySelector('link[rel="apple-touch-icon"]');
            if (!appleIcon) {{
                appleIcon = window.parent.document.createElement('link');
                appleIcon.rel = 'apple-touch-icon';
                appleIcon.setAttribute('sizes', '192x192');
                head.appendChild(appleIcon);
            }}
            appleIcon.href = logoUri;

            // Cài đặt icon cho Android Chrome
            let favIcon = head.querySelector('link[rel="icon"]');
            if (!favIcon) {{
                favIcon = window.parent.document.createElement('link');
                favIcon.rel = 'icon';
                head.appendChild(favIcon);
            }}
            favIcon.href = logoUri;
            favIcon.setAttribute('type', 'image/png');

            // Đặt tên ứng dụng khi ghim ra màn hình chính
            let appTitle = head.querySelector('meta[name="apple-mobile-web-app-title"]');
            if (!appTitle) {{
                appTitle = window.parent.document.createElement('meta');
                appTitle.name = 'apple-mobile-web-app-title';
                head.appendChild(appTitle);
            }}
            appTitle.content = "Bán Trú THPT 2";
        }}
    }} catch(e) {{
        console.error(e);
    }}
}})();
</script>
""", unsafe_allow_html=True)

# ========================================================
# 2. KHỞI TẠO VÀ ĐỒNG BỘ DỮ LIỆU
# ========================================================
if not os.path.exists(FILE_DU_LIEU_THUC_TE):
    st.error("Chưa tìm thấy file dữ liệu thực tế tại D:\\danh_sach_hoc_sinh_thuc_te.csv")
    st.stop()

# Đọc danh sách học sinh
if "ds_hoc_sinh_live" not in st.session_state:
    df_load = pd.read_csv(FILE_DU_LIEU_THUC_TE, encoding='utf-8-sig').fillna("")
    if "GĐ1: Ăn trưa" in df_load.columns:
        df_load["GĐ1: Ăn trưa"] = df_load["GĐ1: Ăn trưa"].astype(bool)
    if "Ăn tối" not in df_load.columns:
        df_load["Ăn tối"] = df_load["GĐ1: Ăn trưa"]
    else:
        df_load["Ăn tối"] = df_load["Ăn tối"].astype(bool)
    if "GĐ2: Phòng nghỉ" in df_load.columns:
        df_load["GĐ2: Phòng nghỉ"] = df_load["GĐ2: Phòng nghỉ"].astype(bool)
    st.session_state.ds_hoc_sinh_live = df_load.to_dict('records')

df_current = pd.DataFrame(st.session_state.ds_hoc_sinh_live).fillna("")
if "Ăn tối" not in df_current.columns:
    df_current["Ăn tối"] = df_current["GĐ1: Ăn trưa"]
    st.session_state.ds_hoc_sinh_live = df_current.to_dict('records')

# Đọc tài khoản
if not os.path.exists(FILE_TAI_KHOAN):
    df_tk_init = pd.DataFrame([
        {"Tên đăng nhập": "admin", "Mật khẩu": "bgh123", "Họ và tên": "Ban Giám Hiệu", "Vai trò": "Ban Giám hiệu", "Ghi chú": "Admin tối cao", "Trạng thái": "Hoạt động"},
        {"Tên đăng nhập": "quannhiem", "Mật khẩu": "qn123", "Họ và tên": "Thầy Quản Nhiệm", "Vai trò": "Giáo viên quản lý", "Ghi chú": "Trực ký túc xá", "Trạng thái": "Hoạt động"},
        {"Tên đăng nhập": "ketoan", "Mật khẩu": "kt123", "Họ và tên": "Kế Toán Bán Trú", "Vai trò": "Kế toán bán trú", "Ghi chú": "Thu chi & thực đơn", "Trạng thái": "Hoạt động"},
        {"Tên đăng nhập": "nhabep", "Mật khẩu": "bep123", "Họ và tên": "Tổ Nuôi Dưỡng", "Vai trò": "Nhà bếp / Cấp dưỡng", "Ghi chú": "Kiểm thực 3 bước", "Trạng thái": "Hoạt động"},
        {"Tên đăng nhập": "phuhuynh", "Mật khẩu": "ph123", "Họ và tên": "Phụ Huynh Học Sinh", "Vai trò": "Phụ huynh học sinh", "Ghi chú": "Cổng phụ huynh", "Trạng thái": "Hoạt động"},
        {"Tên đăng nhập": "hocsinh", "Mật khẩu": "hs123", "Họ và tên": "Học Sinh Bán Trú", "Vai trò": "Học sinh", "Ghi chú": "Cổng học sinh", "Trạng thái": "Hoạt động"},
    ])
    df_tk_init.to_csv(FILE_TAI_KHOAN, index=False, encoding='utf-8-sig')

df_tai_khoan = pd.read_csv(FILE_TAI_KHOAN, encoding='utf-8-sig').fillna("")

# Quản lý phiên đăng nhập
if "user_login" not in st.session_state:
    st.session_state.user_login = {
        "logged_in": False,
        "username": "",
        "fullname": "",
        "role": ""
    }

# ========================================================
# 2.1. MÀN HÌNH ĐĂNG NHẬP BẮT BUỘC (NẾU CHƯA ĐĂNG NHẬP)
# ========================================================
if not st.session_state.user_login.get("logged_in", False):
    col_l1, col_l2, col_l3 = st.columns([1, 2, 1])
    with col_l2:
        st.markdown("<div style='text-align:center; padding:10px 0;'>", unsafe_allow_html=True)
        if os.path.exists(FILE_LOGO):
            st.image(FILE_LOGO, width=115)
        st.markdown("""
            <h2 style='color:#1E3A8A; margin-top:5px; margin-bottom:2px;'>TRƯỜNG THPT SỐ 2 BẢO YÊN</h2>
            <h4 style='color:#DC2626; margin-top:0;'>HỆ THỐNG QUẢN LÝ BÁN TRÚ (2026 - 2027)</h4>
            <p style='color:#4B5563; font-size:14px;'>Quý Thầy/Cô, Phụ huynh và Học sinh vui lòng đăng nhập để truy cập.</p>
        </div>
        """, unsafe_allow_html=True)
        
        with st.form("form_dang_nhap_he_thong"):
            st.markdown("### 🔐 ĐĂNG NHẬP HỆ THỐNG")
            ten_dn = st.text_input("👤 Tên đăng nhập:", placeholder="Nhập tên đăng nhập (VD: admin, quannhiem, phuhuynh...)")
            mat_khau = st.text_input("🔑 Mật khẩu:", type="password", placeholder="Nhập mật khẩu được cấp...")
            btn_login = st.form_submit_button("🚀 ĐĂNG NHẬP VÀO HỆ THỐNG", type="primary", use_container_width=True)
            
            if btn_login:
                ten_clean = ten_dn.strip().lower()
                mk_clean = mat_khau.strip()
                if not ten_clean or not mk_clean:
                    st.warning("⚠️ Vui lòng nhập đầy đủ tên đăng nhập và mật khẩu.")
                else:
                    df_tk_check = pd.read_csv(FILE_TAI_KHOAN, encoding='utf-8-sig').fillna("")
                    user_found = df_tk_check[df_tk_check["Tên đăng nhập"].str.lower() == ten_clean]
                    if not user_found.empty:
                        row_u = user_found.iloc[0]
                        if str(row_u["Mật khẩu"]) == mk_clean:
                            if row_u.get("Trạng thái") == "Khóa":
                                st.error("❌ Tài khoản này hiện đang bị tạm khóa. Vui lòng liên hệ Ban Giám Hiệu!")
                            else:
                                st.session_state.user_login = {
                                    "logged_in": True,
                                    "username": row_u["Tên đăng nhập"],
                                    "fullname": row_u["Họ và tên"],
                                    "role": row_u["Vai trò"]
                                }
                                st.success(f"🎉 Đăng nhập thành công! Xin chào {row_u['Họ và tên']}.")
                                st.rerun()
                        else:
                            st.error("❌ Mật khẩu không chính xác! Vui lòng kiểm tra lại.")
                    else:
                        st.error(f"❌ Tài khoản '{ten_dn}' không tồn tại trong hệ thống. Vui lòng kiểm tra lại!")

        with st.expander("💡 **DANH SÁCH TÀI KHOẢN VÀ MẬT KHẨU MẪU ĐƯỢC CẤP:**", expanded=True):
            st.markdown("""
            | Vai trò người dùng | Tên đăng nhập | Mật khẩu ban đầu |
            | :--- | :---: | :---: |
            | **👑 Ban Giám Hiệu** *(Quản trị toàn quyền)* | `admin` | `bgh123` |
            | **👨‍🏫 Giáo viên Quản lý** *(Điểm danh, nề nếp)* | `quannhiem` | `qn123` |
            | **💰 Kế Toán Bán Trú** *(Thực đơn, thu phí)* | `ketoan` | `kt123` |
            | **🍳 Tổ Cấp Dưỡng / Nhà Bếp** *(Suất ăn, kiểm thực)* | `nhabep` | `bep123` |
            | **👨‍👩‍👧 Phụ Huynh Học Sinh** *(Theo dõi con, cắt cơm)* | `phuhuynh` | `ph123` |
            | **🎒 Học Sinh Bán Trú** *(Báo về nhà, báo xuống trường)* | `hocsinh` | `hs123` |
            """)
    st.stop()

# ========================================================
# 3. THANH BÊN (SIDEBAR): KHI ĐÃ ĐĂNG NHẬP THÀNH CÔNG
# ========================================================
with st.sidebar:
    if os.path.exists(FILE_LOGO):
        st.image(FILE_LOGO, width=95)
    else:
        st.image("https://cdn-icons-png.flaticon.com/512/2997/2997295.png", width=65)
    st.markdown("### **THPT SỐ 2 BẢO YÊN**")
    st.caption("Trường THPT số 2 Bảo Yên - Lào Cai (2026-2027)")
    
    st.markdown("---")
    st.markdown("#### 🔐 **THÔNG TIN ĐĂNG NHẬP**")
    
    u_curr = st.session_state.user_login
    role_curr = u_curr["role"]
    
    # Hiển thị huy hiệu vai trò
    badge_color = {
        "Ban Giám hiệu": "badge-bgh",
        "Giáo viên quản lý": "badge-qn",
        "Kế toán bán trú": "badge-kt",
        "Nhà bếp / Cấp dưỡng": "badge-bep",
        "Phụ huynh học sinh": "badge-ph",
        "Học sinh": "badge-hs"
    }.get(role_curr, "badge-bgh")
    
    st.markdown(f"👤 Người dùng: **{u_curr['fullname']}**")
    st.markdown(f"Vai trò: <span class='{badge_color}'>{role_curr}</span>", unsafe_allow_html=True)
    
    # Nút đăng xuất tài khoản
    if st.button("🚪 ĐĂNG XUẤT (THOÁT RA)", type="secondary", use_container_width=True):
        st.session_state.user_login = {
            "logged_in": False,
            "username": "",
            "fullname": "",
            "role": ""
        }
        st.rerun()
    
    # Nếu là Ban Giám Hiệu, hỗ trợ công cụ xem nhanh các giao diện khác để quản trị
    if role_curr == "Ban Giám hiệu":
        with st.expander("🔄 **Xem nhanh giao diện vai trò khác:**", expanded=False):
            danh_sach_vai_tro = [
                "👑 Ban Giám hiệu (Admin)",
                "👨‍🏫 Giáo viên quản lý",
                "💰 Kế toán bán trú",
                "🍳 Nhà bếp / Cấp dưỡng",
                "👨‍👩‍👧 Phụ huynh học sinh",
                "🎒 Học sinh"
            ]
            chon_role_nhanh = st.selectbox("Chọn vai trò:", danh_sach_vai_tro, index=0)
            if st.button("Chuyển xem ngay", use_container_width=True):
                role_map = {
                    "👑 Ban Giám hiệu (Admin)": ("admin", "Ban Giám Hiệu", "Ban Giám hiệu"),
                    "👨‍🏫 Giáo viên quản lý": ("quannhiem", "Thầy Quản Nhiệm Bán Trú", "Giáo viên quản lý"),
                    "💰 Kế toán bán trú": ("ketoan", "Kế Toán Bán Trú", "Kế toán bán trú"),
                    "🍳 Nhà bếp / Cấp dưỡng": ("nhabep", "Tổ Cấp Dưỡng Nhà Bếp", "Nhà bếp / Cấp dưỡng"),
                    "👨‍👩‍👧 Phụ huynh học sinh": ("phuhuynh", "Phụ Huynh Học Sinh", "Phụ huynh học sinh"),
                    "🎒 Học sinh": ("hocsinh", "Học Sinh Bán Trú", "Học sinh")
                }
                u_name, f_name, r_name = role_map[chon_role_nhanh]
                st.session_state.user_login = {
                    "logged_in": True,
                    "username": u_name,
                    "fullname": f_name,
                    "role": r_name
                }
                st.rerun()

    st.markdown("---")
    ngay_lam_viec = st.date_input("📅 Ngày làm việc:", date.today())
    
    # Bộ lọc phòng ở (áp dụng chung)
    ds_day = ["Tất cả (Khu Nam & Nữ)", "Dãy Nam (9 phòng - 95 HS)", "Dãy Nữ (10 phòng - 112 HS)"]
    chon_day = st.radio("🏢 Khu vực phòng ở:", ds_day)
    
    if "Dãy Nam" in chon_day:
        df_filter_room = df_current[df_current["Dãy nhà"] == "Dãy Nam"]
    elif "Dãy Nữ" in chon_day:
        df_filter_room = df_current[df_current["Dãy nhà"] == "Dãy Nữ"]
    else:
        df_filter_room = df_current
        
    ds_phong = ["Tất cả các phòng"] + sorted(list(df_filter_room["Phòng"].dropna().unique()))
    chon_phong = st.selectbox("🚪 Chọn Phòng:", ds_phong)
    
    tu_khoa = st.text_input("🔍 Tìm nhanh (Tên, SĐT, Bố/Mẹ):", "")

# Áp dụng bộ lọc
df_hien_thi = df_filter_room.copy()
if chon_phong != "Tất cả các phòng":
    df_hien_thi = df_hien_thi[df_hien_thi["Phòng"] == chon_phong]

if tu_khoa:
    df_hien_thi = df_hien_thi[
        df_hien_thi["Họ và tên"].str.contains(tu_khoa, case=False, na=False) |
        df_hien_thi["Họ tên Bố"].str.contains(tu_khoa, case=False, na=False) |
        df_hien_thi["Họ tên Mẹ"].str.contains(tu_khoa, case=False, na=False) |
        df_hien_thi["SĐT Phụ huynh"].astype(str).str.contains(tu_khoa, na=False) |
        df_hien_thi["SĐT Học sinh"].astype(str).str.contains(tu_khoa, na=False) |
        df_hien_thi["Lớp"].str.contains(tu_khoa, case=False, na=False)
    ]

# Tổng số liệu
tong_hs_khu_vuc = len(df_hien_thi)
so_nam = len(df_hien_thi[df_hien_thi["Giới tính"] == "Nam"])
so_nu = len(df_hien_thi[df_hien_thi["Giới tính"] == "Nữ"])

# Học sinh có mặt tại trường thời gian thực (Trạng thái == "Tại trường")
so_tai_truong = len(df_hien_thi[df_hien_thi["Trạng thái"] == "Tại trường"])

# Số suất ăn 2 bữa thời gian thực
so_suat_an_trua = int(df_hien_thi["GĐ1: Ăn trưa"].sum()) if tong_hs_khu_vuc > 0 else 0
so_suat_an_toi = int(df_hien_thi["Ăn tối"].sum()) if ("Ăn tối" in df_hien_thi.columns and tong_hs_khu_vuc > 0) else so_suat_an_trua

# Nghỉ tại phòng
so_nghi_phong = int(df_hien_thi["GĐ2: Phòng nghỉ"].sum()) if tong_hs_khu_vuc > 0 else 0

# Phân loại học sinh vắng:
# 1. Học sinh đã về nhà / gia đình đón (Hợp lệ)
mask_ve_nha = df_hien_thi["Trạng thái"].str.contains("về nhà|ở nhà|Xin về", case=False, na=False)
so_ve_nha = len(df_hien_thi[mask_ve_nha])

# 2. Học sinh vắng do GIÁO VIÊN QUẢN LÝ BÁO (Ốm Y tế, Vắng có phép, Vắng không phép)
mask_gv_bao_vang = df_hien_thi["Trạng thái"].str.contains("GV báo|Ốm|không phép|Vắng có phép", case=False, na=False)
so_gv_bao_vang = len(df_hien_thi[mask_gv_bao_vang])

# ========================================================
# 4. HEADER CHÍNH
# ========================================================
col_h1, col_h2 = st.columns([3, 1])
with col_h1:
    col_lg, col_tt = st.columns([1, 6])
    with col_lg:
        if os.path.exists(FILE_LOGO):
            st.image(FILE_LOGO, width=80)
    with col_tt:
        st.markdown("<h2 style='margin:0; padding:0; color:#1E3A8A;'>🏫 QUẢN LÝ BÁN TRÚ - THPT SỐ 2 BẢO YÊN</h2>", unsafe_allow_html=True)
        st.markdown(f"**Năm học 2026 - 2027** | Ngày: **{ngay_lam_viec.strftime('%d/%m/%Y')}** | Vai trò: `<span class='{badge_color}'>{role_curr}</span>`", unsafe_allow_html=True)

with col_h2:
    link_hien = duong_dan_online if duong_dan_online else duong_dan_app_mobile
    st.success(f"📱 **Link App Điện Thoại:**\n`{link_hien}`")

st.markdown("#### 📊 **QUÂN SỐ THỜI GIAN THỰC & SUẤT ĂN HAI BỮA (TRƯA - TỐI)**")
c_m1, c_m2, c_m3, c_m4 = st.columns(4)
c_m1.metric("👥 Sĩ Số Bán Trú", f"{tong_hs_khu_vuc} HS", delta=f"Nam: {so_nam} | Nữ: {so_nu}")
c_m2.metric("🟢 Tại Trường (Live)", f"{so_tai_truong} HS", delta=f"{so_tai_truong}/{tong_hs_khu_vuc} ({(so_tai_truong/tong_hs_khu_vuc*100 if tong_hs_khu_vuc>0 else 0):.1f}%)")
c_m3.metric("🍲 Suất Cơm Trưa", f"{so_suat_an_trua} suất", delta=f"{so_suat_an_trua}/{tong_hs_khu_vuc}" if so_suat_an_trua==tong_hs_khu_vuc else f"-{tong_hs_khu_vuc - so_suat_an_trua} cắt trưa", delta_color="normal" if so_suat_an_trua==tong_hs_khu_vuc else "inverse")
c_m4.metric("🍛 Suất Cơm Tối", f"{so_suat_an_toi} suất", delta=f"{so_suat_an_toi}/{tong_hs_khu_vuc}" if so_suat_an_toi==tong_hs_khu_vuc else f"-{tong_hs_khu_vuc - so_suat_an_toi} cắt tối", delta_color="normal" if so_suat_an_toi==tong_hs_khu_vuc else "inverse")

c_m5, c_m6, c_m7 = st.columns(3)
c_m5.metric("🛏️ Nghỉ Tại Phòng", f"{so_nghi_phong} HS", delta=f"{so_nghi_phong}/{tong_hs_khu_vuc}")
c_m6.metric("🚗 Học Sinh Đã Về Nhà", f"{so_ve_nha} em", delta="Gia đình đón / Xin về", delta_color="off")
c_m7.metric("🚨 GV Quản Lý Báo Vắng", f"{so_gv_bao_vang} em", delta="Cần kiểm tra ngay!" if so_gv_bao_vang > 0 else "Nề nếp tốt 100%", delta_color="inverse" if so_gv_bao_vang > 0 else "normal")

# Bảng cảnh báo học sinh vắng do giáo viên quản lý báo
if so_gv_bao_vang > 0:
    st.error(f"🚨 **DANH SÁCH {so_gv_bao_vang} HỌC SINH VẮNG DO GIÁO VIÊN QUẢN LÝ BÁO (THỜI GIAN THỰC):**")
    df_gv_show = df_hien_thi[mask_gv_bao_vang][["Phòng", "Giường", "Họ và tên", "Lớp", "Trạng thái", "Ghi chú nề nếp", "Họ tên Bố", "Họ tên Mẹ", "SĐT Phụ huynh"]]
    st.dataframe(df_gv_show, use_container_width=True, hide_index=True)

if so_ve_nha > 0:
    with st.expander(f"🚗 Danh sách {so_ve_nha} học sinh đã về nhà / gia đình đón an toàn:", expanded=False):
        df_vn_show = df_hien_thi[mask_ve_nha][["Phòng", "Giường", "Họ và tên", "Lớp", "Trạng thái", "Họ tên Bố", "Họ tên Mẹ", "SĐT Phụ huynh"]]
        st.dataframe(df_vn_show, use_container_width=True, hide_index=True)

st.markdown("---")

# ========================================================
# 5. ĐIỀU HƯỚNG THEO PHÂN QUYỀN VAI TRÒ
# ========================================================

# --------------------------------------------------------
# VAI TRÒ 1: BAN GIÁM HIỆU (ADMIN TỐI CAO)
# --------------------------------------------------------
if role_curr == "Ban Giám hiệu":
    tab_admin_tk, tab_hs_crud, tab_bgh_bc, tab_dd, tab_thi_dua, tab_bep, tab_kt, tab_td, tab_cai_dat = st.tabs([
        "👑 CẤP QUYỀN & TÀI KHOẢN",
        "➕ THÊM / BỚT HỌC SINH",
        "📊 DASHBOARD ĐIỀU HÀNH",
        "📋 ĐIỂM DANH 2 GIAI ĐOẠN",
        "🏆 THI ĐUA 19 PHÒNG",
        "🍳 BẾP ĂN & KIỂM THỰC",
        "💰 KẾ TOÁN & VIETQR",
        "🥗 PHÊ DUYỆT THỰC ĐƠN",
        "📱 CÀI ĐẶT APP DI ĐỘNG"
    ])
    
    # --- PHÂN QUYỀN TÀI KHOẢN ---
    with tab_admin_tk:
        st.subheader("👑 Quản Trị, Cấp Quyền & Chỉnh Sửa Phân Quyền Tài Khoản (Dành Cho BGH)")
        st.caption("Tài khoản Ban Giám Hiệu (Admin) có toàn quyền chỉnh sửa vai trò, thay đổi quyền hạn, đổi mật khẩu và cấp tài khoản mới cho các thành viên.")
        
        # Đọc dữ liệu tài khoản mới nhất
        df_tai_khoan = pd.read_csv(FILE_TAI_KHOAN, encoding='utf-8-sig').fillna("")
        
        c_edit_tk, c_add_tk = st.columns([1, 1])
        
        with c_edit_tk:
            st.markdown("#### 🛠️ 1. CHỈNH SỬA PHÂN QUYỀN & ĐỔI MẬT KHẨU:")
            ds_users = df_tai_khoan["Tên đăng nhập"].tolist()
            user_duoc_chon = st.selectbox("Chọn tài khoản cần chỉnh sửa quyền:", ds_users, key="sel_user_edit")
            
            row_u = df_tai_khoan[df_tai_khoan["Tên đăng nhập"] == user_duoc_chon].iloc[0]
            
            with st.form("form_chinh_sua_quyen"):
                st.text_input("Tên đăng nhập (Username):", value=user_duoc_chon, disabled=True)
                edit_fullname = st.text_input("Họ và tên người sử dụng:", value=str(row_u["Họ và tên"]))
                
                ds_roles = [
                    "Ban Giám hiệu", "Giáo viên quản lý", "Kế toán bán trú",
                    "Nhà bếp / Cấp dưỡng", "Phụ huynh học sinh", "Học sinh"
                ]
                role_idx = ds_roles.index(row_u["Vai trò"]) if row_u["Vai trò"] in ds_roles else 1
                edit_role = st.selectbox("Vai trò phân quyền:", ds_roles, index=role_idx)
                
                edit_pass = st.text_input("Mật khẩu truy cập (sửa để cấp mật khẩu mới):", value=str(row_u["Mật khẩu"]))
                
                ds_trang_thai = ["Hoạt động", "Tạm khóa"]
                tt_idx = 0 if row_u.get("Trạng thái") == "Hoạt động" else (1 if row_u.get("Trạng thái") == "Tạm khóa" else 0)
                edit_status = st.selectbox("Trạng thái tài khoản:", ds_trang_thai, index=tt_idx)
                
                edit_note = st.text_input("Ghi chú / Nhiệm vụ phụ trách:", value=str(row_u.get("Ghi chú", "")))
                
                btn_save_edit = st.form_submit_button("💾 LƯU THAY ĐỔI PHÂN QUYỀN CHO TÀI KHOẢN NÀY", type="primary", use_container_width=True)
                
                if btn_save_edit:
                    idx_u = df_tai_khoan[df_tai_khoan["Tên đăng nhập"] == user_duoc_chon].index[0]
                    df_tai_khoan.at[idx_u, "Họ và tên"] = edit_fullname.strip()
                    df_tai_khoan.at[idx_u, "Vai trò"] = edit_role
                    df_tai_khoan.at[idx_u, "Mật khẩu"] = edit_pass.strip()
                    df_tai_khoan.at[idx_u, "Trạng thái"] = edit_status
                    df_tai_khoan.at[idx_u, "Ghi chú"] = edit_note.strip()
                    
                    df_tai_khoan.to_csv(FILE_TAI_KHOAN, index=False, encoding='utf-8-sig')
                    st.success(f"✅ Đã cập nhật thành công phân quyền cho tài khoản '{user_duoc_chon}'!")
                    st.rerun()

        with c_add_tk:
            st.markdown("#### ➕ 2. CẤP TÀI KHOẢN MỚI CHO THÀNH VIÊN:")
            with st.form("form_them_tai_khoan"):
                new_user = st.text_input("Tên đăng nhập mới (VD: gv_linh, hs_002...):")
                new_pass = st.text_input("Mật khẩu ban đầu:", value="123456")
                new_fullname = st.text_input("Họ và tên người dùng (VD: Cô Nguyễn Thị Linh):")
                new_role = st.selectbox("Vai trò phân quyền:", [
                    "Giáo viên quản lý", "Kế toán bán trú", "Nhà bếp / Cấp dưỡng", "Phụ huynh học sinh", "Học sinh", "Ban Giám hiệu"
                ])
                new_note = st.text_input("Ghi chú nhiệm vụ phụ trách (VD: Phụ trách dãy phòng nữ...):")
                btn_tao_tk = st.form_submit_button("✨ CẤP TÀI KHOẢN MỚI", type="primary", use_container_width=True)
                
                if btn_tao_tk:
                    clean_u = new_user.strip().lower()
                    if clean_u and new_pass and new_fullname:
                        if clean_u in df_tai_khoan["Tên đăng nhập"].str.lower().values:
                            st.error(f"❌ Tên đăng nhập '{clean_u}' đã tồn tại!")
                        else:
                            dong_moi = pd.DataFrame([{
                                "Tên đăng nhập": clean_u,
                                "Mật khẩu": new_pass.strip(),
                                "Họ và tên": new_fullname.strip(),
                                "Vai trò": new_role,
                                "Ghi chú": new_note.strip(),
                                "Trạng thái": "Hoạt động"
                            }])
                            df_tk_up = pd.concat([df_tai_khoan, dong_moi], ignore_index=True)
                            df_tk_up.to_csv(FILE_TAI_KHOAN, index=False, encoding='utf-8-sig')
                            st.success(f"✅ Đã tạo thành công tài khoản: {clean_u} ({new_fullname} - {new_role})")
                            st.rerun()
                    else:
                        st.warning("Vui lòng điền đầy đủ tên đăng nhập, mật khẩu và họ tên.")
            
            st.markdown("#### ❌ Xóa Tài Khoản Khỏi Hệ Thống:")
            ds_user_del = [u for u in df_tai_khoan["Tên đăng nhập"].tolist() if u != "admin"]
            if ds_user_del:
                c_del1, c_del2 = st.columns([2, 1])
                with c_del1:
                    chon_del = st.selectbox("Chọn tài khoản cần xóa:", ds_user_del, key="sel_user_del")
                with c_del2:
                    st.markdown("<div style='height:28px;'></div>", unsafe_allow_html=True)
                    if st.button("Xác nhận xóa", type="secondary", use_container_width=True):
                        df_tai_khoan = df_tai_khoan[df_tai_khoan["Tên đăng nhập"] != chon_del]
                        df_tai_khoan.to_csv(FILE_TAI_KHOAN, index=False, encoding='utf-8-sig')
                        st.success(f"Đã xóa tài khoản {chon_del}")
                        st.rerun()

        st.markdown("---")
        st.markdown("#### 📋 3. BẢNG DANH SÁCH & CHỈNH SỬA NHANH TẤT CẢ TÀI KHOẢN (TRỰC TIẾP TRÊN BẢNG):")
        st.caption("Thầy/Cô có thể bấm chuột trực tiếp vào từng ô trong bảng dưới đây để sửa nhanh Họ tên, Vai trò, Mật khẩu, hoặc Khóa/Mở tài khoản, sau đó bấm nút 'Lưu tất cả' bên dưới.")
        
        edited_df_tk = st.data_editor(
            df_tai_khoan,
            column_config={
                "Tên đăng nhập": st.column_config.TextColumn("Tên đăng nhập", disabled=True),
                "Vai trò": st.column_config.SelectboxColumn("Vai trò phân quyền", options=[
                    "Ban Giám hiệu", "Giáo viên quản lý", "Kế toán bán trú", "Nhà bếp / Cấp dưỡng", "Phụ huynh học sinh", "Học sinh"
                ]),
                "Trạng thái": st.column_config.SelectboxColumn("Trạng thái", options=["Hoạt động", "Tạm khóa"]),
                "Mật khẩu": st.column_config.TextColumn("Mật khẩu"),
                "Họ và tên": st.column_config.TextColumn("Họ và tên"),
                "Ghi chú": st.column_config.TextColumn("Ghi chú / Nhiệm vụ")
            },
            use_container_width=True,
            hide_index=True,
            key="grid_edit_tk"
        )
        
        if st.button("💾 LƯU TẤT CẢ THAY ĐỔI TRÊN BẢNG VÀO FILE HỆ THỐNG", type="primary", use_container_width=True):
            edited_df_tk.to_csv(FILE_TAI_KHOAN, index=False, encoding='utf-8-sig')
            st.success("🎉 Đã lưu toàn bộ các thay đổi phân quyền vào cơ sở dữ liệu hệ thống thành công!")
            st.rerun()

    # --- THÊM / BỚT HỌC SINH ---
    with tab_hs_crud:
        st.subheader("➕ Bổ Sung Hoặc Rút Hồ Sơ Học Sinh Bán Trú")
        st.caption("Cập nhật biến động học sinh vào/ra bán trú theo chỉ đạo của Ban Giám Hiệu.")
        
        c_hs1, c_hs2 = st.columns([1, 1])
        with c_hs1:
            st.markdown("#### ➕ Thêm Học Sinh Vào Bán Trú:")
            with st.form("form_them_hs"):
                col_in1, col_in2 = st.columns(2)
                with col_in1:
                    ma_hs_moi = st.text_input("Mã học sinh:", value=f"HS{len(df_current)+1:04d}")
                    ten_hs_moi = st.text_input("Họ và tên học sinh:")
                    gioi_tinh_moi = st.selectbox("Giới tính:", ["Nam", "Nữ"])
                    lop_moi = st.selectbox("Lớp:", ["10A1", "10A2", "10A3", "11A1", "11A2", "11A3", "12A1", "12A2", "12A3"])
                    dan_toc_moi = st.selectbox("Dân tộc:", ["Dao", "Tày", "H'Mông", "Kinh", "Xa Phó", "Giáy", "Nùng", "Thái", "Phù Lá"])
                    chinh_sach_moi = st.selectbox("Chính sách NĐ 116:", ["Hưởng NĐ 116", "Tự túc"])
                with col_in2:
                    day_moi = "Dãy Nam" if gioi_tinh_moi == "Nam" else "Dãy Nữ"
                    st.text_input("Dãy nhà phân bổ:", value=day_moi, disabled=True)
                    phong_moi = st.text_input("Xếp vào phòng (VD: Phòng 301):", value="Phòng 301" if gioi_tinh_moi=="Nam" else "Phòng 401")
                    giuong_moi = st.text_input("Vị trí giường:", value="Giường 1")
                    bo_moi = st.text_input("Họ tên Bố:")
                    me_moi = st.text_input("Họ tên Mẹ:")
                    sdt_ph_moi = st.text_input("SĐT Phụ huynh:")
                    thon_xa_moi = st.text_input("Thôn, Xã thường trú:", value="Bảo Hà, Bảo Yên")
                    
                btn_luu_hs = st.form_submit_button("Thêm Học Sinh Vào Cơ Sở Dữ Liệu", type="primary")
                if btn_luu_hs:
                    if ten_hs_moi:
                        khoi_moi = f"Khối {lop_moi[:2]}"
                        dong_hs = {
                            "Mã HS": ma_hs_moi, "Phòng": phong_moi, "Giường": giuong_moi,
                            "Dãy nhà": day_moi, "Họ và tên": ten_hs_moi, "Lớp": lop_moi,
                            "Khối": khoi_moi, "Giới tính": gioi_tinh_moi, "Dân tộc": dan_toc_moi,
                            "Chính sách NĐ116": chinh_sach_moi, "Thôn": thon_xa_moi, "Xã": "Bảo Yên",
                            "Họ tên Bố": bo_moi, "Họ tên Mẹ": me_moi, "SĐT Phụ huynh": sdt_ph_moi,
                            "SĐT Học sinh": "", "Cách trường (KM)": 15, "Ghi chú nề nếp": "",
                            "Trạng thái": "Tại trường", "GĐ1: Ăn trưa": True, "GĐ2: Phòng nghỉ": True
                        }
                        df_up_hs = pd.DataFrame(st.session_state.ds_hoc_sinh_live)
                        df_up_hs = pd.concat([df_up_hs, pd.DataFrame([dong_hs])], ignore_index=True)
                        st.session_state.ds_hoc_sinh_live = df_up_hs.to_dict('records')
                        df_up_hs.to_csv(FILE_DU_LIEU_THUC_TE, index=False, encoding='utf-8-sig')
                        st.success(f"✅ Đã thêm học sinh {ten_hs_moi} vào {phong_moi} thành công!")
                        st.rerun()
                    else:
                        st.warning("Vui lòng nhập họ và tên học sinh.")
                        
        with c_hs2:
            st.markdown("#### ❌ Rút Hồ Sơ / Xóa Học Sinh Ra Khỏi Bán Trú:")
            hs_list_names = df_current["Họ và tên"].tolist()
            hs_can_xoa = st.selectbox("Chọn học sinh cần rút hồ sơ:", hs_list_names)
            ly_do_rut = st.text_input("Lý do rút khỏi bán trú:", "Chuyển trường / Về nhà ở trọ tự túc")
            
            if st.button("Xác nhận rút hồ sơ học sinh này", type="secondary"):
                df_up_hs = pd.DataFrame(st.session_state.ds_hoc_sinh_live)
                df_up_hs = df_up_hs[df_up_hs["Họ và tên"] != hs_can_xoa]
                st.session_state.ds_hoc_sinh_live = df_up_hs.to_dict('records')
                df_up_hs.to_csv(FILE_DU_LIEU_THUC_TE, index=False, encoding='utf-8-sig')
                st.success(f"Đã rút hồ sơ học sinh {hs_can_xoa} ra khỏi danh sách bán trú!")
                st.rerun()

    # --- DASHBOARD BGH ---
    with tab_bgh_bc:
        st.subheader("📊 Báo Cáo Chuyên Cần & Tổng Hợp Điều Hành")
        col_b1, col_b2 = st.columns(2)
        with col_b1:
            st.markdown("#### 🏢 Quân số ăn theo từng Khối lớp")
            thong_ke_khoi = df_current.groupby("Khối")[["GĐ1: Ăn trưa", "GĐ2: Phòng nghỉ"]].sum().reset_index()
            thong_ke_khoi.columns = ["Khối Lớp", "Suất Ăn Trưa (GĐ1)", "Có Mặt Phòng (GĐ2)"]
            st.dataframe(thong_ke_khoi, use_container_width=True, hide_index=True)
            
            st.markdown("#### 🏢 Thống kê theo Dãy phòng")
            thong_ke_day = df_current.groupby("Dãy nhà")[["GĐ1: Ăn trưa", "GĐ2: Phòng nghỉ"]].sum().reset_index()
            thong_ke_day.columns = ["Khu Vực", "Suất Ăn Trưa", "Có Mặt Nghỉ Trưa"]
            st.dataframe(thong_ke_day, use_container_width=True, hide_index=True)
            
        with col_b2:
            st.markdown("#### 🚨 Học sinh vắng ăn / vắng phòng hôm nay")
            ds_vang = df_current[df_current["GĐ1: Ăn trưa"] == False][["Phòng", "Giường", "Họ và tên", "Lớp", "Trạng thái", "Họ tên Bố", "Họ tên Mẹ", "SĐT Phụ huynh"]]
            if len(ds_vang) > 0:
                st.dataframe(ds_vang, use_container_width=True, hide_index=True)
                st.warning(f"⚠️ Có {len(ds_vang)} học sinh đang vắng. Quản nhiệm đã liên hệ gia đình!")
            else:
                st.success("🎉 Toàn bộ học sinh bán trú đi học và ăn cơm đầy đủ 100%!")

    # --- ĐIỂM DANH ---
    with tab_dd:
        st.subheader("📋 Bảng Điểm Danh 2 Giai Đoạn & 2 Bữa Ăn Thời Gian Thực")
        cot_dd = ["Mã HS", "Phòng", "Giường", "Họ và tên", "Lớp", "GĐ1: Ăn trưa", "Ăn tối", "GĐ2: Phòng nghỉ", "Trạng thái", "Họ tên Bố", "Họ tên Mẹ", "SĐT Phụ huynh", "Ghi chú nề nếp"]
        cot_edit = st.data_editor(
            df_hien_thi[cot_dd],
            column_config={
                "GĐ1: Ăn trưa": st.column_config.CheckboxColumn("🍲 Ăn Trưa [✓]", default=True),
                "Ăn tối": st.column_config.CheckboxColumn("🍛 Ăn Tối [✓]", default=True),
                "GĐ2: Phòng nghỉ": st.column_config.CheckboxColumn("🛏️ Phòng Nghỉ [✓]", default=True),
                "Trạng thái": st.column_config.SelectboxColumn("Trạng thái", options=[
                    "Tại trường", "Đã về nhà an toàn", "GV báo: Ốm tại phòng Y tế", "GV báo: Vắng có phép", "GV báo: Vắng không phép 🚨"
                ])
            },
            disabled=["Mã HS", "Phòng", "Giường", "Họ và tên", "Lớp", "Họ tên Bố", "Họ tên Mẹ", "SĐT Phụ huynh"],
            hide_index=True,
            use_container_width=True
        )
        if st.button("💾 LƯU DỮ LIỆU ĐIỂM DANH", type="primary", key="save_dd_bgh"):
            df_cap_nhat = pd.DataFrame(st.session_state.ds_hoc_sinh_live)
            for idx, row in cot_edit.iterrows():
                ma = row["Mã HS"]
                df_cap_nhat.loc[df_cap_nhat["Mã HS"] == ma, "GĐ1: Ăn trưa"] = row["GĐ1: Ăn trưa"]
                df_cap_nhat.loc[df_cap_nhat["Mã HS"] == ma, "Ăn tối"] = row["Ăn tối"]
                df_cap_nhat.loc[df_cap_nhat["Mã HS"] == ma, "GĐ2: Phòng nghỉ"] = row["GĐ2: Phòng nghỉ"]
                df_cap_nhat.loc[df_cap_nhat["Mã HS"] == ma, "Trạng thái"] = row["Trạng thái"]
                df_cap_nhat.loc[df_cap_nhat["Mã HS"] == ma, "Ghi chú nề nếp"] = row["Ghi chú nề nếp"]
            st.session_state.ds_hoc_sinh_live = df_cap_nhat.to_dict('records')
            df_cap_nhat.to_csv(FILE_DU_LIEU_THUC_TE, index=False, encoding='utf-8-sig')
            st.success("✅ Đã đồng bộ điểm danh 2 bữa ăn và trạng thái chuyên cần thành công!")

    # --- THI ĐUA 19 PHÒNG ---
    with tab_thi_dua:
        st.subheader("🏆 Đánh Giá & Bảng Vàng Thi Đua Nề Nếp 19 Phòng Bán Trú")
        if os.path.exists(FILE_THI_DUA):
            df_td_load = pd.read_csv(FILE_THI_DUA, encoding='utf-8-sig')
            st.dataframe(df_td_load, use_container_width=True, hide_index=True)
            top1 = df_td_load.sort_values(by="Tổng điểm", ascending=False).iloc[0]
            st.success(f"🌟 **PHÒNG DẪN ĐẦU TUẦN NÀY:** **{top1['Phòng']} ({top1['Dãy nhà']})** đạt **{top1['Tổng điểm']}/40 điểm** - Xếp loại: {top1['Xếp loại']}")

    # --- BẾP ĂN & KIỂM THỰC ---
    with tab_bep:
        st.subheader("🍳 Báo Cáo Bếp Ăn & Kiểm Thực Ba Bước")
        tong_an = int(df_current["GĐ1: Ăn trưa"].sum())
        st.info(f"Tổng suất ăn nấu hôm nay: **{tong_an} suất** (Khu Nam: {int(df_current[df_current['Dãy nhà']=='Dãy Nam']['GĐ1: Ăn trưa'].sum())} | Khu Nữ: {int(df_current[df_current['Dãy nhà']=='Dãy Nữ']['GĐ1: Ăn trưa'].sum())})")
        if os.path.exists(FILE_KIEM_THUC):
            df_kt_load = pd.read_csv(FILE_KIEM_THUC, encoding='utf-8-sig')
            st.dataframe(df_kt_load, use_container_width=True, hide_index=True)

    # --- KẾ TOÁN & VIETQR ---
    with tab_kt:
        st.subheader("💰 Quản Lý Biểu Phí & Cổng Thanh Toán VietQR Tự Động")
        st.caption("Tự động tính tiền ăn dựa trên ngày ăn thực tế và khấu trừ các ngày báo cắt cơm trước 08:00 sáng.")
        
        c_fee1, c_fee2 = st.columns([1, 1])
        with c_fee1:
            dinh_muc_ngay = st.number_input("Định mức tiền ăn / ngày (VNĐ):", value=30000, step=1000)
            so_ngay_thang = st.number_input("Số ngày bán trú trong tháng:", value=22, step=1)
            tien_chuan = dinh_muc_ngay * so_ngay_thang
            st.markdown(f"**Mức thu chuẩn 1 học sinh / tháng:** `{tien_chuan:,.0f} VNĐ`")
            
            # Chọn học sinh để tạo phiếu thu VietQR
            hs_vietqr = st.selectbox("Chọn học sinh phát hành mã VietQR:", df_current["Họ và tên"].tolist(), key="bgh_vqr")
            row_vqr = df_current[df_current["Họ và tên"] == hs_vietqr].iloc[0]
            
            so_ngay_nghi = 1 if row_vqr["Trạng thái"] == "Xin về nhà" else 0
            tien_phai_dong = (so_ngay_thang - so_ngay_nghi) * dinh_muc_ngay
            st.markdown(f"- Học sinh: **{row_vqr['Họ và tên']}** (Lớp: {row_vqr['Lớp']} - {row_vqr['Phòng']})")
            st.markdown(f"- Số ngày báo nghỉ hợp lệ được trừ: **{so_ngay_nghi} ngày**")
            st.markdown(f"- **TỔNG TIỀN PHẢI ĐÓNG:** <span style='font-size:18px;color:#DC2626;font-weight:bold;'>{tien_phai_dong:,.0f} VNĐ</span>", unsafe_allow_html=True)
            
        with c_fee2:
            st.markdown("#### 📱 Mã VietQR Động Cho Phụ Huynh Quét Đóng Tiền:")
            noi_dung_ck = f"THPT2BY {row_vqr['Mã HS']} {row_vqr['Họ và tên']} Dong tien an thang 10"
            noi_dung_url = urllib.parse.quote(noi_dung_ck)
            vietqr_img_url = f"https://img.vietqr.io/image/agribank-8800205123456-compact2.png?amount={tien_phai_dong}&addInfo={noi_dung_url}&accountName=THPT%20SO%202%20BAO%20YEN"
            st.image(vietqr_img_url, width=280)
            st.caption("Phụ huynh quét mã này trên bất kỳ ứng dụng ngân hàng nào (Agribank, BIDV, Vietinbank...) tiền sẽ tự điền đúng tên con và lớp.")

    # --- THỰC ĐƠN TUẦN ---
    with tab_td:
        st.subheader("🥗 Phê Duyệt Thực Đơn Tuần Chuẩn Dinh Dưỡng THPT")
        if os.path.exists(FILE_THUC_DON):
            df_td_view = pd.read_csv(FILE_THUC_DON, encoding='utf-8-sig')
            st.dataframe(df_td_view, use_container_width=True, hide_index=True)
            if st.button("✅ BAN GIÁM HIỆU PHÊ DUYỆT THỰC ĐƠN NÀY", type="primary"):
                st.success("🎉 Đã phê duyệt thực đơn tuần! Thực đơn đã công khai trên App của phụ huynh và học sinh.")

    # --- CÀI APP ---
    with tab_cai_dat:
        st.subheader("📱 Mở Phần Mềm Trực Tiếp Trên Điện Thoại Di Động")
        col_m1, col_m2 = st.columns(2)
        with col_m1:
            if duong_dan_online:
                st.markdown(f"""
                <div style="text-align: center; border: 2px solid #16A34A; padding: 18px; border-radius: 12px; background: #F0FDF4; margin-bottom: 15px;">
                    <span style="background:#16A34A; color:white; padding:4px 12px; border-radius:20px; font-weight:bold; font-size:12px;">🌟 MỞ TRỰC TUYẾN (DÙNG 4G HOẶC WI-FI BẤT KỲ)</span>
                    <h4 style="color:#15803D; margin-top:10px;">DÙNG CAMERA ĐIỆN THOẠI QUÉT MÃ</h4>
                    <img src="https://api.qrserver.com/v1/create-qr-code/?size=250x250&data={duong_dan_online}" width="200" style="border-radius:8px; box-shadow:0 2px 5px rgba(0,0,0,0.1);">
                    <p style="margin-top:10px; font-size:15px; font-weight:bold; color:#166534;">Địa chỉ trực tuyến:<br>
                    <a href="{duong_dan_online}" target="_blank" style="color:#2563EB; font-size:16px; word-break:break-all;">{duong_dan_online}</a></p>
                </div>
                """, unsafe_allow_html=True)
            st.markdown(f"""
            <div style="text-align: center; border: 2px dashed #2563EB; padding: 18px; border-radius: 12px; background: #F8FAFC;">
                <span style="background:#2563EB; color:white; padding:4px 12px; border-radius:20px; font-weight:bold; font-size:12px;">📶 DÙNG MẠNG WI-FI NỘI BỘ</span>
                <p style="margin-top:10px; font-size:14px; font-weight:bold; color:#1E3A8A;">Địa chỉ: <br><span style="color:#DC2626; font-size:16px;">{duong_dan_app_mobile}</span></p>
            </div>
            """, unsafe_allow_html=True)
        with col_m2:
            st.markdown("### 📲 BIỂU TƯỢNG APP CHÍNH THỨC CỦA TRƯỜNG:")
            c_ico1, c_ico2 = st.columns([1, 2])
            with c_ico1:
                if os.path.exists(FILE_LOGO):
                    st.image(FILE_LOGO, width=100, caption="Logo THPT số 2 Bảo Yên")
            with c_ico2:
                st.markdown("""
                - **Biểu tượng App:** Mang đúng huy hiệu chính thức của **Trường THPT số 2 Bảo Yên**.
                - **Tên hiển thị trên điện thoại:** `Bán Trú THPT 2`.
                """)
            st.markdown("""
            #### 🍎 Hướng dẫn trên iPhone (Safari):
            1. Bấm nút **Chia sẻ** (ô vuông có mũi tên ⬆️ ở đáy màn hình).
            2. Cuộn xuống chọn **"Thêm vào Màn hình chính"** (Add to Home Screen).
            3. Bấm **Thêm** (Add) ở góc trên bên phải.
            
            ---
            #### 🤖 Hướng dẫn trên Android (Chrome / Cốc Cốc):
            1. Bấm dấu **3 chấm (⋮)** ở góc trên bên phải màn hình.
            2. Chọn dòng **"Thêm vào Màn hình chính"** (hoặc "Cài đặt ứng dụng").
            3. Bấm **Thêm** để xác nhận.
            """)

# --------------------------------------------------------
# VAI TRÒ 2: GIÁO VIÊN QUẢN LÝ (QUẢN NHIỆM BÁN TRÚ)
# --------------------------------------------------------
elif role_curr == "Giáo viên quản lý":
    tab_dd, tab_thi_dua, tab_xin_ve, tab_tra_cuu, tab_cai_dat = st.tabs([
        "📋 ĐIỂM DANH 2 GIAI ĐOẠN",
        "🏆 CHẤM THI ĐUA NỀ NẾP 19 PHÒNG",
        "🚗 QUẢN LÝ XIN VỀ / XUỐNG TRƯỜNG",
        "🔎 TRA CỨU HỒ SƠ & GỌI BỐ MẸ",
        "📱 CÀI ĐẶT APP DI ĐỘNG"
    ])
    
    with tab_dd:
        st.subheader(f"📋 Bảng Điểm Danh Hai Bữa & Nề Nếp Phòng - {chon_phong}")
        cot_dd = ["Mã HS", "Phòng", "Giường", "Họ và tên", "Lớp", "GĐ1: Ăn trưa", "Ăn tối", "GĐ2: Phòng nghỉ", "Trạng thái", "Họ tên Bố", "Họ tên Mẹ", "SĐT Phụ huynh", "Ghi chú nề nếp"]
        cot_edit = st.data_editor(
            df_hien_thi[cot_dd],
            column_config={
                "GĐ1: Ăn trưa": st.column_config.CheckboxColumn("🍲 Ăn Trưa [✓]", default=True),
                "Ăn tối": st.column_config.CheckboxColumn("🍛 Ăn Tối [✓]", default=True),
                "GĐ2: Phòng nghỉ": st.column_config.CheckboxColumn("🛏️ Phòng Nghỉ [✓]", default=True),
                "Trạng thái": st.column_config.SelectboxColumn("Trạng thái", options=[
                    "Tại trường", "Đã về nhà an toàn", "GV báo: Ốm tại phòng Y tế", "GV báo: Vắng có phép", "GV báo: Vắng không phép 🚨"
                ])
            },
            disabled=["Mã HS", "Phòng", "Giường", "Họ và tên", "Lớp", "Họ tên Bố", "Họ tên Mẹ", "SĐT Phụ huynh"],
            hide_index=True,
            use_container_width=True
        )
        if st.button("💾 LƯU DỮ LIỆU ĐIỂM DANH", type="primary", key="save_dd_qn"):
            df_cap_nhat = pd.DataFrame(st.session_state.ds_hoc_sinh_live)
            for idx, row in cot_edit.iterrows():
                ma = row["Mã HS"]
                df_cap_nhat.loc[df_cap_nhat["Mã HS"] == ma, "GĐ1: Ăn trưa"] = row["GĐ1: Ăn trưa"]
                df_cap_nhat.loc[df_cap_nhat["Mã HS"] == ma, "Ăn tối"] = row["Ăn tối"]
                df_cap_nhat.loc[df_cap_nhat["Mã HS"] == ma, "GĐ2: Phòng nghỉ"] = row["GĐ2: Phòng nghỉ"]
                df_cap_nhat.loc[df_cap_nhat["Mã HS"] == ma, "Trạng thái"] = row["Trạng thái"]
                df_cap_nhat.loc[df_cap_nhat["Mã HS"] == ma, "Ghi chú nề nếp"] = row["Ghi chú nề nếp"]
            st.session_state.ds_hoc_sinh_live = df_cap_nhat.to_dict('records')
            df_cap_nhat.to_csv(FILE_DU_LIEU_THUC_TE, index=False, encoding='utf-8-sig')
            st.success("✅ Đã lưu điểm danh 2 bữa ăn và cập nhật báo vắng thành công!")

    with tab_thi_dua:
        st.subheader("🏆 Chấm Điểm Thi Đua Nề Nếp & Vệ Sinh 19 Phòng Bán Trú (5S)")
        st.caption("Giáo viên quản nhiệm đi kiểm tra các phòng: Chấm điểm vệ sinh, gấp chăn màn, giờ giấc và bảo quản tài sản.")
        
        df_td_current = pd.read_csv(FILE_THI_DUA, encoding='utf-8-sig') if os.path.exists(FILE_THI_DUA) else pd.DataFrame()
        
        c_td1, c_td2 = st.columns([1, 2])
        with c_td1:
            st.markdown("#### 📝 Nhập Điểm Phòng:")
            phong_cham = st.selectbox("Chọn phòng chấm điểm:", sorted(list(df_current["Phòng"].unique())))
            day_phong_cham = "Dãy Nam" if "3" in phong_cham or "205" in phong_cham else "Dãy Nữ"
            
            d_vesinh = st.slider("1. Vệ sinh phòng ngủ (quét sàn, rác):", 0, 10, 9)
            d_chanman = st.slider("2. Gấp chăn màn ngay ngắn:", 0, 10, 9)
            d_nenep = st.slider("3. Nề nếp giờ giấc, trật tự trưa/tối:", 0, 10, 10)
            d_taisan = st.slider("4. Bảo quản tài sản (điện, quạt, giường):", 0, 10, 10)
            ghi_chu_cham = st.text_input("Ghi chú khen thưởng / nhắc nhở:", "")
            
            tong_d = d_vesinh + d_chanman + d_nenep + d_taisan
            if tong_d >= 36:
                xep_loai = "Xuất sắc"
            elif tong_d >= 30:
                xep_loai = "Tốt"
            elif tong_d >= 20:
                xep_loai = "Đạt"
            else:
                xep_loai = "Cần chấn chỉnh"
                
            st.markdown(f"**Tổng điểm:** <span style='font-size:20px;font-weight:bold;color:#16A34A;'>{tong_d}/40 điểm</span> - Xếp loại: **{xep_loai}**", unsafe_allow_html=True)
            
            if st.button("Lưu Điểm Chấm Phòng Này", type="primary"):
                # Cập nhật vào df_td_current
                ngay_str = ngay_lam_viec.strftime("%d/%m/%Y")
                mask = (df_td_current["Phòng"] == phong_cham)
                if mask.any():
                    df_td_current.loc[mask, "Vệ sinh (10đ)"] = d_vesinh
                    df_td_current.loc[mask, "Chăn màn (10đ)"] = d_chanman
                    df_td_current.loc[mask, "Nề nếp (10đ)"] = d_nenep
                    df_td_current.loc[mask, "Tài sản (10đ)"] = d_taisan
                    df_td_current.loc[mask, "Tổng điểm"] = tong_d
                    df_td_current.loc[mask, "Xếp loại"] = xep_loai
                    df_td_current.loc[mask, "Ghi chú"] = ghi_chu_cham
                    df_td_current.loc[mask, "Ngày"] = ngay_str
                else:
                    new_row = pd.DataFrame([{
                        "Ngày": ngay_str, "Phòng": phong_cham, "Dãy nhà": day_phong_cham,
                        "Vệ sinh (10đ)": d_vesinh, "Chăn màn (10đ)": d_chanman, "Nề nếp (10đ)": d_nenep,
                        "Tài sản (10đ)": d_taisan, "Tổng điểm": tong_d, "Xếp loại": xep_loai,
                        "Người chấm": u_curr["fullname"], "Ghi chú": ghi_chu_cham
                    }])
                    df_td_current = pd.concat([df_td_current, new_row], ignore_index=True)
                df_td_current.to_csv(FILE_THI_DUA, index=False, encoding='utf-8-sig')
                st.success(f"✅ Đã lưu kết quả thi đua của {phong_cham}!")
                st.rerun()

        with c_td2:
            st.markdown("#### 🏆 Bảng Xếp Hạng Thi Đua Hiện Tại:")
            if not df_td_current.empty:
                st.dataframe(df_td_current.sort_values(by="Tổng điểm", ascending=False), use_container_width=True, hide_index=True)

    with tab_xin_ve:
        st.subheader("🚗 Quản Lý Học Sinh Xin Về Nhà & Báo Xuống Trường")
        st.caption("Quản nhiệm kiểm soát chặt chẽ học sinh về gia đình và khi quay lại trường.")
        
        c_xv1, c_xv2 = st.columns([1, 1])
        with c_xv1:
            st.markdown("#### 📝 Ghi Nhận Học Sinh Xin Về:")
            with st.form("form_ghi_xin_ve"):
                hs_xv = st.selectbox("Chọn học sinh xin về:", df_current["Họ và tên"].tolist())
                ly_do_xv = st.selectbox("Lý do:", ["Về cuối tuần", "Việc gia đình có tang/hiếu", "Ốm về nhà điều trị", "Lý do khác"])
                nguoi_don_xv = st.text_input("Người đón / Phương tiện (VD: Bố đón xe máy / Xe khách):")
                cat_com = st.checkbox("Cắt suất cơm kể từ buổi này", value=True)
                btn_luu_xv = st.form_submit_button("Xác Nhận Cho Học Sinh Về", type="primary")
                
                if btn_luu_xv:
                    # Ghi vào lịch sử
                    row_h = df_current[df_current["Họ và tên"] == hs_xv].iloc[0]
                    dong_xv = {
                        "Thời gian": datetime.now().strftime("%d/%m/%Y %H:%M"),
                        "Mã HS": row_h["Mã HS"], "Họ và tên": hs_xv, "Lớp": row_h["Lớp"],
                        "Phòng": row_h["Phòng"], "Hình thức": "Xin về nhà",
                        "Lý do": ly_do_xv, "Người đón / SĐT": nguoi_don_xv,
                        "Người duyệt": u_curr["fullname"], "Trạng thái": "Đang ở nhà"
                    }
                    df_xv_old = pd.read_csv(FILE_XIN_VE, encoding='utf-8-sig') if os.path.exists(FILE_XIN_VE) else pd.DataFrame()
                    df_xv_new = pd.concat([df_xv_old, pd.DataFrame([dong_xv])], ignore_index=True)
                    df_xv_new.to_csv(FILE_XIN_VE, index=False, encoding='utf-8-sig')
                    
                    # Cập nhật trạng thái học sinh
                    df_up_hs = pd.DataFrame(st.session_state.ds_hoc_sinh_live)
                    df_up_hs.loc[df_up_hs["Họ và tên"] == hs_xv, "Trạng thái"] = "Xin về nhà"
                    if cat_com:
                        df_up_hs.loc[df_up_hs["Họ và tên"] == hs_xv, "GĐ1: Ăn trưa"] = False
                        df_up_hs.loc[df_up_hs["Họ và tên"] == hs_xv, "GĐ2: Phòng nghỉ"] = False
                    st.session_state.ds_hoc_sinh_live = df_up_hs.to_dict('records')
                    df_up_hs.to_csv(FILE_DU_LIEU_THUC_TE, index=False, encoding='utf-8-sig')
                    st.success(f"✅ Đã ghi nhận học sinh {hs_xv} về nhà an toàn!")
                    st.rerun()

        with c_xv2:
            st.markdown("#### 🏫 Xác Nhận Học Sinh Đã Xuống Trường:")
            ds_hs_dang_o_nha = df_current[df_current["Trạng thái"] == "Xin về nhà"]["Họ và tên"].tolist()
            if ds_hs_dang_o_nha:
                hs_xuong = st.selectbox("Chọn học sinh đã xuống trường:", ds_hs_dang_o_nha)
                if st.button("✅ Xác Nhận Đã Xuống Trường An Toàn", type="primary"):
                    df_up_hs = pd.DataFrame(st.session_state.ds_hoc_sinh_live)
                    df_up_hs.loc[df_up_hs["Họ và tên"] == hs_xuong, "Trạng thái"] = "Tại trường"
                    df_up_hs.loc[df_up_hs["Họ và tên"] == hs_xuong, "GĐ1: Ăn trưa"] = True
                    df_up_hs.loc[df_up_hs["Họ và tên"] == hs_xuong, "GĐ2: Phòng nghỉ"] = True
                    st.session_state.ds_hoc_sinh_live = df_up_hs.to_dict('records')
                    df_up_hs.to_csv(FILE_DU_LIEU_THUC_TE, index=False, encoding='utf-8-sig')
                    st.success(f"🎉 Đã đón học sinh {hs_xuong} trở lại trường, khôi phục suất ăn!")
                    st.rerun()
            else:
                st.info("Hiện không có học sinh nào đang ở nhà.")
                
            st.markdown("#### 📜 Sổ Theo Dõi Ra / Vào:")
            if os.path.exists(FILE_XIN_VE):
                st.dataframe(pd.read_csv(FILE_XIN_VE, encoding='utf-8-sig'), use_container_width=True, hide_index=True)

    with tab_tra_cuu:
        st.subheader("🔎 Tra Cứu Hồ Sơ & Thông Tin Liên Hệ Bố / Mẹ")
        hs_duoc_chon = st.selectbox("Chọn hoặc gõ tên học sinh để xem hồ sơ liên hệ:", df_current["Họ và tên"].tolist(), key="qn_search")
        row_hs = df_current[df_current["Họ và tên"] == hs_duoc_chon].iloc[0]
        
        c_card1, c_card2 = st.columns([1, 1])
        with c_card1:
            st.markdown(f"""
            <div style="background:#EFF6FF; border-left:5px solid #2563EB; padding:15px; border-radius:8px;">
                <h4 style="color:#1E40AF; margin-top:0;">🎓 {row_hs['Họ và tên']} ({row_hs['Giới tính']})</h4>
                <p><b>Mã HS:</b> <code>{row_hs['Mã HS']}</code> | <b>Lớp:</b> <b>{row_hs['Lớp']}</b></p>
                <p><b>Phòng ở:</b> <b>{row_hs['Phòng']}</b> - Giường: <b>{row_hs['Giường']}</b> ({row_hs['Dãy nhà']})</p>
                <p><b>Địa chỉ:</b> Thôn {row_hs['Thôn']}, Xã {row_hs['Xã']} (Cách trường: {row_hs['Cách trường (KM)']} KM)</p>
                <p><b>Hoàn cảnh:</b> <span style="color:#DC2626;">{row_hs['Ghi chú nề nếp']}</span></p>
            </div>
            """, unsafe_allow_html=True)
        with c_card2:
            st.markdown(f"""
            <div style="background:#F0FDF4; border-left:5px solid #16A34A; padding:15px; border-radius:8px;">
                <h4 style="color:#15803D; margin-top:0;">📞 LIÊN HỆ PHỤ HUYNH</h4>
                <p>👨 <b>Họ tên Bố:</b> {row_hs['Họ tên Bố']}</p>
                <p>👩 <b>Họ tên Mẹ:</b> {row_hs['Họ tên Mẹ']}</p>
                <p>☎️ <b>SĐT Bố/Mẹ:</b> <a href="tel:{row_hs['SĐT Phụ huynh']}" style="font-size:18px;font-weight:bold;color:#2563EB;">{row_hs['SĐT Phụ huynh']}</a></p>
                <p>📱 <b>SĐT Học sinh:</b> <a href="tel:{row_hs['SĐT Học sinh']}">{row_hs['SĐT Học sinh']}</a></p>
                <p>📍 <b>Trạng thái:</b> <b>{row_hs['Trạng thái']}</b></p>
            </div>
            """, unsafe_allow_html=True)

    with tab_cai_dat:
        st.subheader("📱 Mở Phần Mềm Trực Tiếp Trên Điện Thoại Di Động")
        st.success(f"Link Online: `{duong_dan_online}` | Link Wi-Fi: `{duong_dan_app_mobile}`")

# --------------------------------------------------------
# VAI TRÒ 3: NHÀ BẾP / TỔ CẤP DƯỠNG
# --------------------------------------------------------
elif role_curr == "Nhà bếp / Cấp dưỡng":
    tab_suat_an, tab_kiem_thuc, tab_thuc_don, tab_mua_tp = st.tabs([
        "🍳 CHỐT SUẤT ĂN HÀNG NGÀY",
        "🥩 KIỂM THỰC BA BƯỚC & LƯU MẪU 24H",
        "🥗 THỰC ĐƠN BÁN TRÚ",
        "📝 ĐỀ XUẤT NGUYÊN LIỆU THỰC PHẨM"
    ])
    
    with tab_suat_an:
        st.subheader("🍳 Báo Cáo Suất Ăn Hai Bữa Gửi Tổ Nuôi Dưỡng (Trưa & Tối)")
        tong_trua = int(df_current["GĐ1: Ăn trưa"].sum())
        tong_toi = int(df_current["Ăn tối"].sum()) if "Ăn tối" in df_current.columns else tong_trua
        nam_trua = int(df_current[df_current["Dãy nhà"] == "Dãy Nam"]["GĐ1: Ăn trưa"].sum())
        nu_trua = int(df_current[df_current["Dãy nhà"] == "Dãy Nữ"]["GĐ1: Ăn trưa"].sum())
        nam_toi = int(df_current[df_current["Dãy nhà"] == "Dãy Nam"]["Ăn tối"].sum()) if "Ăn tối" in df_current.columns else nam_trua
        nu_toi = int(df_current[df_current["Dãy nhà"] == "Dãy Nữ"]["Ăn tối"].sum()) if "Ăn tối" in df_current.columns else nu_trua
        
        c_bep1, c_bep2 = st.columns(2)
        with c_bep1:
            st.markdown(f"""
            <div style="background:#EFF6FF; border-left:5px solid #2563EB; padding:15px; border-radius:10px;">
                <h4 style="margin-top:0; color:#1E40AF;">🍲 1. SUẤT CƠM BỮA TRƯA: {tong_trua} SUẤT</h4>
                <p>• <b>Khu Nam (9 phòng):</b> <b>{nam_trua} suất</b> (Sĩ số 95)</p>
                <p>• <b>Khu Nữ (10 phòng):</b> <b>{nu_trua} suất</b> (Sĩ số 112)</p>
                <p>• <b>Số suất cắt / vắng trưa:</b> <span style="color:#DC2626; font-weight:bold;">{207 - tong_trua} suất</span></p>
                <p style="font-size:12px; color:#4B5563;">Chốt quân số trước 08:00 sáng hàng ngày.</p>
            </div>
            """, unsafe_allow_html=True)
            
        with c_bep2:
            st.markdown(f"""
            <div style="background:#FEF3C7; border-left:5px solid #D97706; padding:15px; border-radius:10px;">
                <h4 style="margin-top:0; color:#B45309;">🍛 2. SUẤT CƠM BỮA TỐI: {tong_toi} SUẤT</h4>
                <p>• <b>Khu Nam (9 phòng):</b> <b>{nam_toi} suất</b> (Sĩ số 95)</p>
                <p>• <b>Khu Nữ (10 phòng):</b> <b>{nu_toi} suất</b> (Sĩ số 112)</p>
                <p>• <b>Số suất cắt / vắng tối:</b> <span style="color:#DC2626; font-weight:bold;">{207 - tong_toi} suất</span></p>
                <p style="font-size:12px; color:#4B5563;">Chốt quân số trước 16:00 chiều hàng ngày.</p>
            </div>
            """, unsafe_allow_html=True)
        
    with tab_kiem_thuc:
        st.subheader("🥩 Nhật Ký Kiểm Thực Ba Bước & Lưu Mẫu Thức Ăn (Theo QĐ Bộ Y Tế)")
        c_kt1, c_kt2 = st.columns([1, 2])
        with c_kt1:
            st.markdown("#### ➕ Ghi Nhật Ký Kiểm Thực:")
            with st.form("form_kiem_thuc"):
                bua_an = st.selectbox("Bữa ăn:", ["Bữa trưa", "Bữa tối", "Bữa sáng"])
                mon_an = st.text_input("Tên món / Thực phẩm (VD: Thịt lợn, Rau cải...):")
                khoi_luong = st.number_input("Khối lượng (kg / quả):", value=20.0, step=0.5)
                nguon_goc = st.text_input("Nguồn gốc xuất xứ:", "Cơ sở cung ứng Bảo Yên")
                han_dung = st.text_input("Hạn sử dụng / Độ tươi:", "Trong ngày")
                buoc1 = st.selectbox("Bước 1: Cảm quan nguyên liệu:", ["Tốt - Tươi sống đạt chuẩn", "Không đạt"])
                buoc2 = st.selectbox("Bước 2: Chế biến (Nhiệt độ):", ["Nấu chín sôi >100°C", "Đạt chuẩn"])
                buoc3 = st.selectbox("Bước 3: Lưu mẫu 24h:", ["Đã lưu mẫu hộp kín tủ mát 24h", "Chưa lưu mẫu"])
                btn_luu_kt = st.form_submit_button("Lưu Biên Bản Kiểm Thực", type="primary")
                
                if btn_luu_kt and mon_an:
                    dong_kt = {
                        "Ngày": ngay_lam_viec.strftime("%d/%m/%Y"), "Bữa ăn": bua_an,
                        "Tên món / Thực phẩm": mon_an, "Khối lượng (kg)": khoi_luong,
                        "Nguồn gốc xuất xứ": nguon_goc, "Hạn sử dụng": han_dung,
                        "Kiểm tra cảm quan (Bước 1)": buoc1, "Nhiệt độ chế biến (Bước 2)": buoc2,
                        "Lưu mẫu 24h (Bước 3)": buoc3, "Người kiểm thực": u_curr["fullname"],
                        "Ghi chú": "Đạt chuẩn ATTP"
                    }
                    df_kt_old = pd.read_csv(FILE_KIEM_THUC, encoding='utf-8-sig') if os.path.exists(FILE_KIEM_THUC) else pd.DataFrame()
                    df_kt_new = pd.concat([df_kt_old, pd.DataFrame([dong_kt])], ignore_index=True)
                    df_kt_new.to_csv(FILE_KIEM_THUC, index=False, encoding='utf-8-sig')
                    st.success(f"✅ Đã ghi biên bản kiểm thực món: {mon_an}!")
                    st.rerun()

        with c_kt2:
            st.markdown("#### 📋 Sổ Nhật Ký Kiểm Thực:")
            if os.path.exists(FILE_KIEM_THUC):
                st.dataframe(pd.read_csv(FILE_KIEM_THUC, encoding='utf-8-sig'), use_container_width=True, hide_index=True)

    with tab_thuc_don:
        st.subheader("🥗 Thực Đơn Bán Trú Tuần")
        if os.path.exists(FILE_THUC_DON):
            st.dataframe(pd.read_csv(FILE_THUC_DON, encoding='utf-8-sig'), use_container_width=True, hide_index=True)

    with tab_mua_tp:
        st.subheader("📝 Đề Xuất Nguyên Liệu Thực Phẩm Ngày Mai")
        st.text_area("Danh sách thực phẩm cần nhập cho ngày mai (Gạo, thịt lợn, thịt gà, rau xanh, gia vị...):",
                     "- Gạo Khang Dân: 50 kg\n- Thịt ba chỉ lợn tươi: 25 kg\n- Trứng vịt lộn / gà: 210 quả\n- Rau muống sạch: 35 bó\n- Dầu ăn Tường An: 5 lít", height=150)
        st.button("Gửi Đề Xuất Lên Kế Toán & Ban Giám Hiệu", type="primary")

# --------------------------------------------------------
# VAI TRÒ 4: KẾ TOÁN BÁN TRÚ
# --------------------------------------------------------
elif role_curr == "Kế toán bán trú":
    tab_thu_phi, tab_len_td, tab_doi_soat = st.tabs([
        "💰 QUẢN LÝ BIỂU PHÍ & MÃ VIETQR ĐỘNG",
        "🥗 LÊN THỰC ĐƠN TUẦN / THÁNG",
        "📊 ĐỐI SOÁT CÔNG NỢ & TIỀN ĂN"
    ])
    
    with tab_thu_phi:
        st.subheader("💰 Quản Lý Thu Phí & Tạo Mã VietQR Cho Từng Học Sinh")
        c_k1, c_k2 = st.columns([1, 1])
        with c_k1:
            dinh_muc_ngay = st.number_input("Định mức tiền ăn / ngày (VNĐ):", value=30000, step=1000, key="kt_dm")
            so_ngay_thang = st.number_input("Số ngày bán trú trong tháng:", value=22, step=1, key="kt_sn")
            
            hs_kt = st.selectbox("Chọn học sinh xuất phiếu báo tiền:", df_current["Họ và tên"].tolist(), key="kt_hs_select")
            row_kt = df_current[df_current["Họ và tên"] == hs_kt].iloc[0]
            
            so_ngay_nghi = 1 if row_kt["Trạng thái"] == "Xin về nhà" else 0
            tien_phai_dong = (so_ngay_thang - so_ngay_nghi) * dinh_muc_ngay
            
            st.markdown(f"""
            <div style="background:#FEF3C7; padding:15px; border-radius:8px; border-left:4px solid #D97706;">
                <h4 style="margin-top:0; color:#B45309;">PHIẾU BÁO TIỀN ĂN BÁN TRÚ THÁNG 10</h4>
                <p>Học sinh: <b>{row_kt['Họ và tên']}</b> - Lớp: <b>{row_kt['Lớp']}</b> ({row_kt['Phòng']})</p>
                <p>Số ngày ăn thực tế: <b>{so_ngay_thang - so_ngay_nghi} ngày</b> (Khấu trừ báo cắt cơm: {so_ngay_nghi} ngày)</p>
                <p style="font-size:18px; font-weight:bold; color:#B91C1C;">SỐ TIỀN PHẢI NỘP: {tien_phai_dong:,.0f} VNĐ</p>
            </div>
            """, unsafe_allow_html=True)
            
        with c_k2:
            st.markdown("#### 📱 Mã VietQR Thanh Toán Động:")
            noi_dung_ck = f"THPT2BY {row_kt['Mã HS']} {row_kt['Họ và tên']} Dong tien an thang 10"
            noi_dung_url = urllib.parse.quote(noi_dung_ck)
            vietqr_img_url = f"https://img.vietqr.io/image/agribank-8800205123456-compact2.png?amount={tien_phai_dong}&addInfo={noi_dung_url}&accountName=THPT%20SO%202%20BAO%20YEN"
            st.image(vietqr_img_url, width=280)
            st.caption("Mã QR này được gửi trực tiếp về App Phụ Huynh để phụ huynh quét mã chuyển khoản.")

    with tab_len_td:
        st.subheader("🥗 Lên Thực Đơn Bán Trú Tuần")
        if os.path.exists(FILE_THUC_DON):
            df_td_kt = pd.read_csv(FILE_THUC_DON, encoding='utf-8-sig')
            td_edit = st.data_editor(df_td_kt, use_container_width=True, hide_index=True)
            if st.button("Lưu Thực Đơn Mới & Trình BGH Phê Duyệt", type="primary"):
                td_edit.to_csv(FILE_THUC_DON, index=False, encoding='utf-8-sig')
                st.success("✅ Đã lưu thực đơn và chuyển sang trạng thái chờ BGH phê duyệt!")

    with tab_doi_soat:
        st.subheader("📊 Bảng Đối Soát Tiền Ăn Toàn Trường")
        df_ds = df_current[["Mã HS", "Phòng", "Họ và tên", "Lớp", "Trạng thái", "SĐT Phụ huynh"]].copy()
        df_ds["Số ngày ăn"] = 22
        df_ds.loc[df_ds["Trạng thái"] == "Xin về nhà", "Số ngày ăn"] = 21
        df_ds["Tiền phải nộp (VNĐ)"] = df_ds["Số ngày ăn"] * 30000
        df_ds["Tình trạng đóng"] = "Chưa đóng"
        st.dataframe(df_ds, use_container_width=True, hide_index=True)
        st.markdown(f"**Tổng tiền dự thu toàn trường (207 học sinh):** `{df_ds['Tiền phải nộp (VNĐ)'].sum():,.0f} VNĐ`")

# --------------------------------------------------------
# VAI TRÒ 5: PHỤ HUYNH HỌC SINH
# --------------------------------------------------------
elif role_curr == "Phụ huynh học sinh":
    st.subheader("👨‍👩‍👧 CỔNG THÔNG TIN PHỤ HUYNH BÁN TRÚ")
    st.caption("Theo dõi tình hình ăn, ngủ, học tập của con tại ký túc xá và thanh toán tiền bán trú thuận tiện.")
    
    # Chọn con em mình
    con_em = st.selectbox("Chọn con em của quý phụ huynh:", df_current["Họ và tên"].tolist())
    row_con = df_current[df_current["Họ và tên"] == con_em].iloc[0]
    
    # Thẻ thông tin nhanh của con
    c_ph1, c_ph2 = st.columns([1, 1])
    with c_ph1:
        st.markdown(f"""
        <div style="background:#F3E8FF; border-left:5px solid #7C3AED; padding:15px; border-radius:10px;">
            <h3 style="margin-top:0; color:#6B21A8;">🎓 {row_con['Họ và tên']}</h3>
            <p><b>Lớp:</b> {row_con['Lớp']} | <b>Phòng ở:</b> <b>{row_con['Phòng']}</b> (Giường: {row_con['Giường']})</p>
            <p><b>Dãy:</b> {row_con['Dãy nhà']} | <b>Chính sách NĐ 116:</b> {row_con['Chính sách NĐ116']}</p>
            <p><b>Cán bộ quản nhiệm trực:</b> Thầy Quản Nhiệm (SĐT: <a href="tel:0988123456">0988.123.456</a>)</p>
        </div>
        """, unsafe_allow_html=True)
        
    with c_ph2:
        an_trang_thai = "🟢 Đã vào ăn cơm trưa" if row_con["GĐ1: Ăn trưa"] else "🔴 Vắng ăn / Cắt cơm"
        nghi_trang_thai = "🟢 Có mặt tại phòng ngủ" if row_con["GĐ2: Phòng nghỉ"] else "🔴 Vắng mặt tại phòng"
        st.markdown(f"""
        <div style="background:#ECFDF5; border-left:5px solid #059669; padding:15px; border-radius:10px;">
            <h4 style="margin-top:0; color:#065F46;">📍 ĐIỂM DANH HÔM NAY ({ngay_lam_viec.strftime('%d/%m/%Y')}):</h4>
            <p>1. Bữa ăn trưa (GĐ1): <b>{an_trang_thai}</b></p>
            <p>2. Nghỉ trưa tại phòng (GĐ2): <b>{nghi_trang_thai}</b></p>
            <p>Trạng thái: <span style="color:#2563EB; font-weight:bold;">{row_con['Trạng thái']}</span></p>
        </div>
        """, unsafe_allow_html=True)
        
    st.markdown("---")
    
    tab_ph_cat, tab_ph_ve, tab_ph_qr, tab_ph_td = st.tabs([
        "🥣 BÁO CẮT CƠM (TRƯỚC 08:00)",
        "🚗 BÁO CON XIN VỀ / XUỐNG TRƯỜNG",
        "💳 ĐÓNG TIỀN ĂN QUA MÃ VIETQR",
        "🥗 THỰC ĐƠN BỮA ĂN CỦA CON"
    ])
    
    with tab_ph_cat:
        st.markdown("#### 🥣 Báo Cắt Cơm Bán Trú Cho Con")
        st.info("⏰ **Quy định:** Phụ huynh vui lòng gửi yêu cầu cắt cơm **trước 08:00 sáng**. Hệ thống sẽ tự động trừ tiền ăn và báo nhà bếp giảm nấu.")
        with st.form("form_ph_cat_com"):
            ngay_cat = st.date_input("Ngày xin cắt cơm:", date.today())
            bua_cat = st.selectbox("Bữa cắt:", ["Bữa trưa hôm nay", "Cả ngày hôm nay", "Từ ngày mai"])
            ly_do_cat = st.text_input("Lý do:", "Gia đình có việc đón cháu về ăn cơm")
            btn_ph_cat = st.form_submit_button("Gửi Yêu Cầu Cắt Cơm Xuống Bếp", type="primary")
            
            if btn_ph_cat:
                df_up_hs = pd.DataFrame(st.session_state.ds_hoc_sinh_live)
                df_up_hs.loc[df_up_hs["Họ và tên"] == con_em, "GĐ1: Ăn trưa"] = False
                st.session_state.ds_hoc_sinh_live = df_up_hs.to_dict('records')
                df_up_hs.to_csv(FILE_DU_LIEU_THUC_TE, index=False, encoding='utf-8-sig')
                st.success(f"✅ Đã báo cắt cơm thành công cho cháu {con_em} ngày {ngay_cat.strftime('%d/%m/%Y')}! Suất ăn đã được khấu trừ.")
                st.rerun()

    with tab_ph_ve:
        st.markdown("#### 🚗 Báo Xin Cho Con Về Nhà / Báo Đã Xuống Trường")
        c_v1, c_v2 = st.columns(2)
        with c_v1:
            st.markdown("##### 1. Xin Cho Con Về:")
            nguoi_don = st.text_input("Họ tên phụ huynh đón:")
            gio_don = st.time_input("Dự kiến giờ đón:")
            if st.button("Xác Nhận Đón Con Về", type="secondary"):
                st.success(f"Đã gửi thông báo đến Thầy Quản Nhiệm: Bố/Mẹ sẽ đón cháu {con_em} lúc {gio_don.strftime('%H:%M')}.")
        with c_v2:
            st.markdown("##### 2. Báo Con Đã Xuống Trường:")
            if st.button("✅ Báo Cháu Đã Lên Đến Trường An Toàn", type="primary"):
                st.success(f"Cảm ơn phụ huynh đã thông báo. Quản nhiệm đã tiếp nhận cháu {con_em} tại trường!")

    with tab_ph_qr:
        st.markdown("#### 💳 Nộp Tiền Bán Trú Qua Mã VietQR Ngân Hàng")
        tien_phai_dong = 21 * 30000
        st.markdown(f"Số tiền cần đóng tháng 10: <span style='font-size:22px;color:#DC2626;font-weight:bold;'>{tien_phai_dong:,.0f} VNĐ</span>", unsafe_allow_html=True)
        noi_dung_ck = f"THPT2BY {row_con['Mã HS']} {row_con['Họ và tên']} Dong tien an thang 10"
        noi_dung_url = urllib.parse.quote(noi_dung_ck)
        vietqr_img_url = f"https://img.vietqr.io/image/agribank-8800205123456-compact2.png?amount={tien_phai_dong}&addInfo={noi_dung_url}&accountName=THPT%20SO%202%20BAO%20YEN"
        st.image(vietqr_img_url, width=300)
        st.caption("Quý phụ huynh mở app Agribank/Vietinbank/BIDV... và quét mã để nộp tiền tự động.")

    with tab_ph_td:
        st.markdown("#### 🥗 Thực Đơn Tuần Này Của Con Tại Trường")
        if os.path.exists(FILE_THUC_DON):
            st.dataframe(pd.read_csv(FILE_THUC_DON, encoding='utf-8-sig'), use_container_width=True, hide_index=True)

# --------------------------------------------------------
# VAI TRÒ 6: HỌC SINH BÁN TRÚ
# --------------------------------------------------------
elif role_curr == "Học sinh":
    st.subheader("🎒 CỔNG THÔNG TIN HỌC SINH BÁN TRÚ")
    
    hs_ten = st.selectbox("Chọn tên em (để đăng nhập / xác nhận):", df_current["Họ và tên"].tolist())
    row_hs_self = df_current[df_current["Họ và tên"] == hs_ten].iloc[0]
    
    trang_thai_hien_tai = row_hs_self["Trạng thái"]
    if "về" in trang_thai_hien_tai.lower() or "nhà" in trang_thai_hien_tai.lower():
        badge_tt = "<span style='background:#DC2626; color:white; padding:4px 12px; border-radius:15px; font-weight:bold;'>🏠 Em đang ở nhà</span>"
    else:
        badge_tt = "<span style='background:#16A34A; color:white; padding:4px 12px; border-radius:15px; font-weight:bold;'>🟢 Em đang tại trường</span>"
    
    st.markdown(f"""
    <div style="background:#E0F2FE; border-left:5px solid #0284C7; padding:15px; border-radius:10px; margin-bottom:15px;">
        <h3 style="margin-top:0; color:#0369A1;">👋 Xin chào: {row_hs_self['Họ và tên']}</h3>
        <p><b>Lớp:</b> {row_hs_self['Lớp']} | <b>Phòng ở:</b> <span style="font-size:18px; font-weight:bold; color:#DC2626;">{row_hs_self['Phòng']}</span> (Giường: <b>{row_hs_self['Giường']}</b>) | <b>Dãy:</b> {row_hs_self['Dãy nhà']}</p>
        <p><b>Dân tộc:</b> {row_hs_self['Dân tộc']} | <b>Chính sách NĐ 116:</b> {row_hs_self['Chính sách NĐ116']} | <b>Hiện tại:</b> {badge_tt}</p>
    </div>
    """, unsafe_allow_html=True)
    
    tab_hs_baove, tab_hs_ban, tab_hs_td, tab_hs_com = st.tabs([
        "🚗 BÁO VỀ NHÀ / XUỐNG TRƯỜNG",
        "👥 CÁC BẠN CÙNG PHÒNG",
        "🏆 BẢNG XẾP HẠNG THI ĐUA PHÒNG EM",
        "🥗 HÔM NAY ĂN MÓN GÌ?"
    ])
    
    with tab_hs_baove:
        st.markdown("### 🚗 Xác Nhận Tác Nghiệp: Đã Về Nhà Hoặc Đã Xuống Trường")
        st.caption("Các em học sinh bấm nút dưới đây để thông báo cho Thầy Cô Quản nhiệm và Ban Giám Hiệu biết em đã về nhà an toàn hoặc đã quay lại trường.")
        
        c_hs_ve, c_hs_xuong = st.columns([1, 1])
        
        with c_hs_ve:
            st.markdown("""
            <div style="background:#FEF2F2; border:2px solid #DC2626; padding:18px; border-radius:12px; text-align:center;">
                <h4 style="color:#B91C1C; margin-top:0;">🏠 1. BÁO ĐÃ VỀ ĐẾN NHÀ AN TOÀN</h4>
                <p style="font-size:13px; color:#4B5563;">Dùng khi em rời ký túc xá về nhà (cuối tuần, nghỉ lễ hoặc ốm về nhà).</p>
            </div>
            """, unsafe_allow_html=True)
            
            with st.form("form_hs_bao_ve"):
                ly_do_ve = st.selectbox("Lý do về nhà:", ["Về cuối tuần", "Về nghỉ lễ", "Việc gia đình có việc bận", "Ốm về nhà điều trị"])
                phuong_tien_ve = st.text_input("Ai đón / Đi bằng gì:", placeholder="VD: Bố đón xe máy / Xe khách Bảo Hà")
                btn_hs_ve = st.form_submit_button("🏡 XÁC NHẬN: EM ĐÃ VỀ ĐẾN NHÀ AN TOÀN", type="primary", use_container_width=True)
                
                if btn_hs_ve:
                    gio_str = datetime.now().strftime("%d/%m/%Y %H:%M")
                    # Ghi lịch sử
                    dong_xv = {
                        "Thời gian": gio_str,
                        "Mã HS": row_hs_self["Mã HS"], "Họ và tên": hs_ten, "Lớp": row_hs_self["Lớp"],
                        "Phòng": row_hs_self["Phòng"], "Hình thức": "Học sinh báo về nhà",
                        "Lý do": ly_do_ve, "Người đón / SĐT": phuong_tien_ve if phuong_tien_ve else "Tự về",
                        "Người duyệt": "Học sinh tự báo qua App", "Trạng thái": "Đã về nhà an toàn"
                    }
                    df_xv_old = pd.read_csv(FILE_XIN_VE, encoding='utf-8-sig') if os.path.exists(FILE_XIN_VE) else pd.DataFrame()
                    df_xv_new = pd.concat([df_xv_old, pd.DataFrame([dong_xv])], ignore_index=True)
                    df_xv_new.to_csv(FILE_XIN_VE, index=False, encoding='utf-8-sig')
                    
                    # Cập nhật danh sách học sinh live
                    df_up_hs = pd.DataFrame(st.session_state.ds_hoc_sinh_live)
                    df_up_hs.loc[df_up_hs["Họ và tên"] == hs_ten, "Trạng thái"] = "Đã về nhà an toàn"
                    df_up_hs.loc[df_up_hs["Họ và tên"] == hs_ten, "GĐ1: Ăn trưa"] = False
                    df_up_hs.loc[df_up_hs["Họ và tên"] == hs_ten, "GĐ2: Phòng nghỉ"] = False
                    st.session_state.ds_hoc_sinh_live = df_up_hs.to_dict('records')
                    df_up_hs.to_csv(FILE_DU_LIEU_THUC_TE, index=False, encoding='utf-8-sig')
                    
                    st.success(f"🎉 Cảm ơn em {hs_ten}! Thầy Cô Quản nhiệm đã nhận được tin báo em về đến nhà an toàn.")
                    st.rerun()

        with c_hs_xuong:
            st.markdown("""
            <div style="background:#F0FDF4; border:2px solid #16A34A; padding:18px; border-radius:12px; text-align:center;">
                <h4 style="color:#15803D; margin-top:0;">🏫 2. BÁO ĐÃ XUỐNG TRƯỜNG AN TOÀN</h4>
                <p style="font-size:13px; color:#4B5563;">Dùng khi em từ nhà đã quay trở lại ký túc xá trường học.</p>
            </div>
            """, unsafe_allow_html=True)
            
            with st.form("form_hs_bao_xuong"):
                phuong_tien_xuong = st.text_input("Phương tiện di chuyển:", placeholder="VD: Bố mẹ chở xuống / Đi xe buýt")
                btn_hs_xuong = st.form_submit_button("🎒 XÁC NHẬN: EM ĐÃ XUỐNG TRƯỜNG AN TOÀN", type="primary", use_container_width=True)
                
                if btn_hs_xuong:
                    gio_str = datetime.now().strftime("%d/%m/%Y %H:%M")
                    # Ghi lịch sử
                    dong_xv = {
                        "Thời gian": gio_str,
                        "Mã HS": row_hs_self["Mã HS"], "Họ và tên": hs_ten, "Lớp": row_hs_self["Lớp"],
                        "Phòng": row_hs_self["Phòng"], "Hình thức": "Học sinh báo xuống trường",
                        "Lý do": "Trở lại trường học tập", "Người đón / SĐT": phuong_tien_xuong if phuong_tien_xuong else "Tự đi",
                        "Người duyệt": "Học sinh tự báo qua App", "Trạng thái": "Tại trường"
                    }
                    df_xv_old = pd.read_csv(FILE_XIN_VE, encoding='utf-8-sig') if os.path.exists(FILE_XIN_VE) else pd.DataFrame()
                    df_xv_new = pd.concat([df_xv_old, pd.DataFrame([dong_xv])], ignore_index=True)
                    df_xv_new.to_csv(FILE_XIN_VE, index=False, encoding='utf-8-sig')
                    
                    # Cập nhật danh sách học sinh live
                    df_up_hs = pd.DataFrame(st.session_state.ds_hoc_sinh_live)
                    df_up_hs.loc[df_up_hs["Họ và tên"] == hs_ten, "Trạng thái"] = "Tại trường"
                    df_up_hs.loc[df_up_hs["Họ và tên"] == hs_ten, "GĐ1: Ăn trưa"] = True
                    df_up_hs.loc[df_up_hs["Họ và tên"] == hs_ten, "GĐ2: Phòng nghỉ"] = True
                    st.session_state.ds_hoc_sinh_live = df_up_hs.to_dict('records')
                    df_up_hs.to_csv(FILE_DU_LIEU_THUC_TE, index=False, encoding='utf-8-sig')
                    
                    st.success(f"🎉 Chào mừng em {hs_ten} đã trở lại trường! Suất cơm và giường nghỉ của em đã sẵn sàng.")
                    st.rerun()

        st.markdown("---")
        st.markdown(f"#### 📜 Lịch Sử Ra / Vào Của Riêng Em ({hs_ten}):")
        if os.path.exists(FILE_XIN_VE):
            df_lich_su_full = pd.read_csv(FILE_XIN_VE, encoding='utf-8-sig')
            df_lich_su_em = df_lich_su_full[df_lich_su_full["Họ và tên"] == hs_ten]
            if not df_lich_su_em.empty:
                st.dataframe(df_lich_su_em, use_container_width=True, hide_index=True)
            else:
                st.info("Chưa có lượt ghi nhận ra/vào nào trước đây.")
                
    with tab_hs_ban:
        st.markdown(f"#### 🚪 Danh Sách Thành Viên {row_hs_self['Phòng']}:")
        ban_cung_phong = df_current[df_current["Phòng"] == row_hs_self["Phòng"]][["Giường", "Họ và tên", "Lớp", "Dân tộc", "Trạng thái"]]
        st.dataframe(ban_cung_phong, use_container_width=True, hide_index=True)
        
    with tab_hs_td:
        st.markdown("#### 🏆 Kết Quả Thi Đua Phòng Em So Với Toàn Trường:")
        if os.path.exists(FILE_THI_DUA):
            df_td_hs = pd.read_csv(FILE_THI_DUA, encoding='utf-8-sig')
            st.dataframe(df_td_hs.sort_values(by="Tổng điểm", ascending=False), use_container_width=True, hide_index=True)
            
    with tab_hs_com:
        st.markdown("#### 🍲 Thực Đơn Bữa Cơm Hôm Nay:")
        if os.path.exists(FILE_THUC_DON):
            st.dataframe(pd.read_csv(FILE_THUC_DON, encoding='utf-8-sig'), use_container_width=True, hide_index=True)

import secrets
import random
import streamlit as st
import pandas as pd
from datetime import date, datetime
import os
import socket
import urllib.parse
import base64
import json
import shutil
import zipfile
import io
from PIL import Image
from phan_he_quan_ly_chung import render_phan_he_quan_ly_chung
from phan_he_doan_thanh_nien import render_phan_he_doan_thanh_nien, tao_anh_qr_base64
from dong_bo_google_sheets import render_tab_google_sheets
try:
    import dich_vu_tu_dong_dong_bo
    dich_vu_tu_dong_dong_bo.khoi_chay_dich_vu_tu_dong()
except Exception:
    pass

# Xác định thư mục gốc làm việc (chạy tốt trên cả Windows máy trường và Cloud)
CUR_DIR = os.path.dirname(os.path.abspath(__file__))
if os.path.exists("D:\\danh_sach_hoc_sinh_thuc_te.csv") or (os.name == 'nt' and os.path.exists("D:\\")):
    BASE_DIR = "D:\\"
else:
    BASE_DIR = CUR_DIR

FILE_LOGO = os.path.join(BASE_DIR, "logo_192.png") if os.path.exists(os.path.join(BASE_DIR, "logo_192.png")) else (
    "D:\\logo_192.png" if os.path.exists("D:\\logo_192.png") else os.path.join(CUR_DIR, "logo_192.png")
)
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
    page_title="THPT số 2 Bảo Yên - Quản Trị Trường Học Toàn Diện",
    page_icon=logo_pil,
    layout="wide",
    initial_sidebar_state="expanded"
)

# Thư mục dữ liệu phân theo từng năm học
THU_MUC_NAM_HOC = os.path.join(BASE_DIR, "du_lieu_nam_hoc")
os.makedirs(THU_MUC_NAM_HOC, exist_ok=True)
FILE_CAU_HINH_NAM_HOC = os.path.join(THU_MUC_NAM_HOC, "cau_hinh_nam_hoc.json")

def doc_cau_hinh_nam_hoc():
    mac_dinh = {
        "nam_hoc_mac_dinh": "2026 - 2027",
        "danh_sach_nam_hoc": ["2025 - 2026", "2026 - 2027", "2027 - 2028"]
    }
    if os.path.exists(FILE_CAU_HINH_NAM_HOC):
        try:
            with open(FILE_CAU_HINH_NAM_HOC, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return mac_dinh

def ghi_cau_hinh_nam_hoc(cfg):
    try:
        with open(FILE_CAU_HINH_NAM_HOC, "w", encoding="utf-8") as f:
            json.dump(cfg, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

def lay_duong_dan_file_theo_nam(nam_hoc):
    folder_name = nam_hoc.replace(" ", "")
    dir_nam = os.path.join(THU_MUC_NAM_HOC, folder_name)
    os.makedirs(dir_nam, exist_ok=True)
    
    f_hs = os.path.join(dir_nam, "danh_sach_hoc_sinh_thuc_te.csv")
    f_td = os.path.join(dir_nam, "cham_diem_thi_dua_phong.csv")
    f_kt = os.path.join(dir_nam, "nhat_ky_kiem_thuc.csv")
    f_don = os.path.join(dir_nam, "thuc_don_tuan.csv")
    f_xv = os.path.join(dir_nam, "lich_su_xin_ve.csv")
    
    # Tự động sao chép từ file gốc nếu thư mục năm học chưa có
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

def tao_zip_nam_hoc(nam_hoc):
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

# Khởi tạo phiên làm việc năm học
cfg_nh = doc_cau_hinh_nam_hoc()
danh_sach_nam_hoc = cfg_nh.get("danh_sach_nam_hoc", ["2025 - 2026", "2026 - 2027", "2027 - 2028"])
nam_hoc_mac_dinh = cfg_nh.get("nam_hoc_mac_dinh", "2026 - 2027")

if "nam_hoc_hien_tai" not in st.session_state:
    st.session_state.nam_hoc_hien_tai = nam_hoc_mac_dinh

# 5 file dữ liệu theo năm học được chọn
FILE_DU_LIEU_THUC_TE, FILE_THI_DUA, FILE_KIEM_THUC, FILE_THUC_DON, FILE_XIN_VE = lay_duong_dan_file_theo_nam(st.session_state.nam_hoc_hien_tai)

FILE_TAI_KHOAN = os.path.join(BASE_DIR, "tai_khoan_nguoi_dung.csv") if os.path.exists(os.path.join(BASE_DIR, "tai_khoan_nguoi_dung.csv")) else "D:\\tai_khoan_nguoi_dung.csv"
FILE_TUNNEL = os.path.join(BASE_DIR, "current_tunnel_url.txt") if os.path.exists(os.path.join(BASE_DIR, "current_tunnel_url.txt")) else "D:\\current_tunnel_url.txt"

# Hàm khởi tạo và cấp tài khoản đồng loạt cho toàn trường
def tao_tai_khoan_dong_loat_full(df_hs):
    try:
        import tao_tai_khoan_chuan_toan_truong
        import importlib
        importlib.reload(tao_tai_khoan_chuan_toan_truong)
        tao_tai_khoan_chuan_toan_truong.tao_tai_khoan()
        if os.path.exists(FILE_TAI_KHOAN):
            return pd.read_csv(FILE_TAI_KHOAN, encoding='utf-8-sig', dtype=str).fillna("")
    except Exception as e:
        print("Lỗi tao_tai_khoan_dong_loat_full:", e)
    return pd.DataFrame()

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

# Địa chỉ chính thức duy nhất trên đám mây (Cloud 24/7 toàn cầu - Khóa link cố định)
URL_APP_CHINH_THUC = "https://thpt2baoyen.streamlit.app"
duong_dan_online = URL_APP_CHINH_THUC
duong_dan_app_mobile = URL_APP_CHINH_THUC

# CSS giao diện tối ưu di động và thẻ trực quan kèm biểu tượng App
st.markdown("""
<style>
    /* 1. Xóa sạch khoảng trắng thừa phía trên cùng màn hình */
    .block-container {
        padding-top: 0.8rem !important;
        padding-bottom: 2rem !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
        max-width: 100% !important;
    }
    header[data-testid="stHeader"] {
        height: 1.2rem !important;
        background: transparent !important;
    }
    #MainMenu { visibility: hidden !important; }
    footer { visibility: hidden !important; }

    /* 2. Danh sách Tab nhỏ gọn, tự động xuống 2 dòng, không tràn màn hình */
    div[data-baseweb="tab-list"] {
        flex-wrap: wrap !important;
        gap: 4px 6px !important;
        border-bottom: 2px solid #E2E8F0 !important;
        padding-bottom: 4px !important;
        overflow-x: visible !important;
    }
    button[data-baseweb="tab"] {
        padding: 4px 9px !important;
        font-size: 12.5px !important;
        border-radius: 6px !important;
        white-space: normal !important;
        height: auto !important;
        min-height: 32px !important;
        line-height: 1.25 !important;
        background-color: #F8FAFC !important;
        border: 1px solid #E2E8F0 !important;
        margin: 2px !important;
    }
    button[data-baseweb="tab"][aria-selected="true"] {
        background-color: #EFF6FF !important;
        color: #1E3A8A !important;
        font-weight: 700 !important;
        border: 1.5px solid #3B82F6 !important;
        border-bottom: 3px solid #1E3A8A !important;
    }

    @media (max-width: 768px) {
        .main-header { font-size: 19px !important; }
        .stMetric { padding: 3px !important; }
        div[data-testid="stHorizontalBlock"] { flex-wrap: wrap !important; }
        button[data-baseweb="tab"] {
            padding: 3px 7px !important;
            font-size: 11.5px !important;
            min-height: 28px !important;
        }
    }
    .badge-bgh { background-color: #DC2626; color: white; padding: 3px 10px; border-radius: 12px; font-weight: bold; font-size: 13px; }
    .badge-qn { background-color: #2563EB; color: white; padding: 3px 10px; border-radius: 12px; font-weight: bold; font-size: 13px; }
    .badge-kt { background-color: #059669; color: white; padding: 3px 10px; border-radius: 12px; font-weight: bold; font-size: 13px; }
    .badge-bep { background-color: #D97706; color: white; padding: 3px 10px; border-radius: 12px; font-weight: bold; font-size: 13px; }
    .badge-ph { background-color: #7C3AED; color: white; padding: 3px 10px; border-radius: 12px; font-weight: bold; font-size: 13px; }
    .badge-hs { background-color: #0284C7; color: white; padding: 3px 10px; border-radius: 12px; font-weight: bold; font-size: 13px; }
</style>
<script>
(function() {
    try {
        const head = window.parent.document.head;
        const logoUri = "/app/static/apple-touch-icon.png";
        const logoFallback = "/apple-touch-icon.png";

        // 1. Apple Touch Icon cho iPhone Safari khi Thêm vào Màn hình chính
        let appleIcon = head.querySelector('link[rel="apple-touch-icon"]');
        if (!appleIcon) {
            appleIcon = window.parent.document.createElement('link');
            appleIcon.rel = 'apple-touch-icon';
            appleIcon.setAttribute('sizes', '192x192');
            head.appendChild(appleIcon);
        }
        appleIcon.href = logoUri;

        let appleIconPre = head.querySelector('link[rel="apple-touch-icon-precomposed"]');
        if (!appleIconPre) {
            appleIconPre = window.parent.document.createElement('link');
            appleIconPre.rel = 'apple-touch-icon-precomposed';
            head.appendChild(appleIconPre);
        }
        appleIconPre.href = logoUri;

        // 2. Favicon logo truong tren trinh duyet
        let favIcon = head.querySelector('link[rel="icon"]');
        if (!favIcon) {
            favIcon = window.parent.document.createElement('link');
            favIcon.rel = 'icon';
            head.appendChild(favIcon);
        }
        favIcon.href = logoUri;
        favIcon.setAttribute('type', 'image/png');

        // 3. PWA Web Manifest cho Android & may tinh
        let manifestLink = head.querySelector('link[rel="manifest"]');
        if (!manifestLink) {
            manifestLink = window.parent.document.createElement('link');
            manifestLink.rel = 'manifest';
            head.appendChild(manifestLink);
        }
        manifestLink.href = '/app/static/site.webmanifest';

        // 4. Apple Web App Title
        let appCapable = head.querySelector('meta[name="apple-mobile-web-app-capable"]');
        if (!appCapable) {
            appCapable = window.parent.document.createElement('meta');
            appCapable.name = 'apple-mobile-web-app-capable';
            head.appendChild(appCapable);
        }
        appCapable.content = 'yes';

        let appTitle = head.querySelector('meta[name="apple-mobile-web-app-title"]');
        if (!appTitle) {
            appTitle = window.parent.document.createElement('meta');
            appTitle.name = 'apple-mobile-web-app-title';
            head.appendChild(appTitle);
        }
        appTitle.content = "THPT 2 Bảo Yên";
    } catch(e) {
        console.error(e);
    }
})();
</script>
""", unsafe_allow_html=True)

# ========================================================
# 2. KHỞI TẠO VÀ ĐỒNG BỘ DỮ LIỆU
# ========================================================
# Đọc danh sách học sinh theo năm học
if "ds_hoc_sinh_live" not in st.session_state or st.session_state.get("nam_hoc_loaded") != st.session_state.nam_hoc_hien_tai:
    if os.path.exists(FILE_DU_LIEU_THUC_TE):
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
    else:
        st.session_state.ds_hoc_sinh_live = []
    st.session_state.nam_hoc_loaded = st.session_state.nam_hoc_hien_tai

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

# ========================================================
# 2. XỬ LÝ GHI NHỚ ĐĂNG NHẬP & XÁC THỰC CON NGƯỜI
# ========================================================
FILE_PHIEN_GHI_NHO = os.path.join(BASE_DIR, "phien_dang_nhap_ghi_nho.json")

def doc_phien_ghi_nho():
    if os.path.exists(FILE_PHIEN_GHI_NHO):
        try:
            with open(FILE_PHIEN_GHI_NHO, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}

def luu_phien_ghi_nho(token, user_row):
    data = doc_phien_ghi_nho()
    data[token] = {
        "username": str(user_row["Tên đăng nhập"]).strip(),
        "fullname": str(user_row["Họ và tên"]).strip(),
        "role": str(user_row["Vai trò"]).strip(),
        "chuc_danh": str(user_row.get("Chức danh", user_row["Vai trò"])).strip(),
        "ma_lien_ket": str(user_row.get("Mã liên kết", "")).strip(),
        "phone": str(user_row.get("Số điện thoại", "")).strip(),
        "quyen_quan_ly": str(user_row.get("Quyền quản lý", "Cá nhân")).strip(),
        "saved_at": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    }
    for d_save in [BASE_DIR, 'D:/phan_mem_ban_tru_cloud', 'd:/OneDrive/Hô sơ cá nhan/Học AI']:
        if os.path.exists(d_save):
            try:
                p = os.path.join(d_save, "phien_dang_nhap_ghi_nho.json")
                with open(p, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
            except Exception:
                pass

def xoa_phien_ghi_nho(token):
    data = doc_phien_ghi_nho()
    if token in data:
        del data[token]
        for d_save in [BASE_DIR, 'D:/phan_mem_ban_tru_cloud', 'd:/OneDrive/Hô sơ cá nhan/Học AI']:
            if os.path.exists(d_save):
                try:
                    p = os.path.join(d_save, "phien_dang_nhap_ghi_nho.json")
                    with open(p, "w", encoding="utf-8") as f:
                        json.dump(data, f, ensure_ascii=False, indent=2)
                except Exception:
                    pass

# Kiểm tra tài khoản đã ghi nhớ trên thiết bị
token_curr = st.query_params.get("token", "")
tai_khoan_ghi_nho = None

if token_curr:
    phien_all = doc_phien_ghi_nho()
    if token_curr in phien_all:
        u_info = phien_all[token_curr]
        user_matches = df_tai_khoan[df_tai_khoan["Tên đăng nhập"].str.lower() == str(u_info["username"]).lower()]
        if not user_matches.empty:
            row_match = user_matches.iloc[0]
            if str(row_match.get("Trạng thái", "")) != "Tạm khóa":
                tai_khoan_ghi_nho = row_match
            else:
                xoa_phien_ghi_nho(token_curr)
        else:
            xoa_phien_ghi_nho(token_curr)

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
    col_l1, col_l2 = st.columns([1.15, 1], gap="medium")
    with col_l1:
        c_head1, c_head2 = st.columns([1, 4])
        with c_head1:
            if os.path.exists(FILE_LOGO):
                st.image(FILE_LOGO, width=85)
        with c_head2:
            st.markdown(f"""
                <h3 style='color:#1E3A8A; margin:0;'>TRƯỜNG THPT SỐ 2 BẢO YÊN</h3>
                <h5 style='color:#DC2626; margin:2px 0 0 0;'>HỆ THỐNG QUẢN TRỊ TRƯỜNG HỌC TOÀN DIỆN ({st.session_state.nam_hoc_hien_tai})</h5>
                <p style='color:#6B7280; font-size:13px; margin:0;'>Cổng tích hợp: Quản lý chung • Bán trú & KTX • Đoàn Thanh Niên</p>
            """, unsafe_allow_html=True)
        st.markdown("<hr style='margin: 10px 0;'>", unsafe_allow_html=True)
        
        # Cho phép chọn năm học ngay tại màn hình đăng nhập
        c_nh_l1, c_nh_l2 = st.columns([1, 1])
        with c_nh_l1:
            st.caption("📅 **NĂM HỌC ĐANG TRUY CẬP:**")
        with c_nh_l2:
            chon_nh_login = st.selectbox(
                "Chọn năm học:",
                options=danh_sach_nam_hoc,
                index=danh_sach_nam_hoc.index(st.session_state.nam_hoc_hien_tai) if st.session_state.nam_hoc_hien_tai in danh_sach_nam_hoc else 0,
                key="login_select_nam_hoc",
                label_visibility="collapsed"
            )
            if chon_nh_login != st.session_state.nam_hoc_hien_tai:
                st.session_state.nam_hoc_hien_tai = chon_nh_login
                st.rerun()
        
        if tai_khoan_ghi_nho is not None:
            # Tạo mã bảo mật 4 chữ số ngẫu nhiên nếu chưa có
            if "ma_captcha_xac_thuc" not in st.session_state:
                st.session_state.ma_captcha_xac_thuc = str(random.randint(1000, 9999))
            
            st.markdown(f"""
                <div style='background:#F0FDF4; border:2px solid #86EFAC; border-radius:12px; padding:15px; margin-bottom:15px;'>
                    <div style='display:flex; align-items:center; gap:10px;'>
                        <span style='font-size:28px;'>👋</span>
                        <div>
                            <h4 style='color:#15803D; margin:0;'>Chào mừng trở lại, {tai_khoan_ghi_nho['Họ và tên']}!</h4>
                            <p style='color:#1E293B; font-size:13.5px; margin:2px 0 0 0;'>
                                🏷️ Vai trò: <b>{tai_khoan_ghi_nho['Vai trò']}</b> | 👤 Tài khoản: <code>{tai_khoan_ghi_nho['Tên đăng nhập']}</code>
                            </p>
                        </div>
                    </div>
                    <div style='margin-top:8px; padding-top:8px; border-top:1px dashed #BBF7D0; font-size:12px; color:#166534;'>
                        🔒 Tài khoản đã được ghi nhớ an toàn trên thiết bị này. Bạn không cần phải nhập lại mật khẩu.
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            with st.form("form_xac_nhan_con_nguoi"):
                st.markdown("#### 🛡️ XÁC THỰC BẢO MẬT (XÁC MINH CON NGƯỜI)")
                st.caption("Để đảm bảo an toàn cho dữ liệu nhà trường, vui lòng nhập mã bảo vệ 4 chữ số hiển thị bên dưới để vào app:")
                
                # Hiển thị mã bảo mật 4 số to, rõ, đẹp
                st.markdown(f"""
                    <div style='text-align:center; padding:14px; background:#F8FAFC; border:1.5px dashed #94A3B8; border-radius:10px; margin:10px 0;'>
                        <span style='font-size:12px; color:#64748B; font-weight:bold; letter-spacing:1px; display:block; margin-bottom:6px;'>MÃ XÁC THỰC CON NGƯỜI:</span>
                        <div style='display:inline-block; background:linear-gradient(135deg, #1E3A8A, #059669); color:white; font-family:"Courier New", monospace; font-size:32px; font-weight:900; letter-spacing:12px; padding:8px 24px; border-radius:8px; box-shadow:0 3px 6px rgba(0,0,0,0.15);'>
                            {st.session_state.ma_captcha_xac_thuc}
                        </div>
                    </div>
                """, unsafe_allow_html=True)
                
                ma_nhap = st.text_input("🔢 Nhập 4 chữ số trên:", max_chars=4, placeholder="Nhập 4 số hiển thị ở trên...")
                btn_xac_nhan = st.form_submit_button("🚀 XÁC NHẬN & VÀO ỨNG DỤNG NGAY", type="primary", use_container_width=True)
                
                if btn_xac_nhan:
                    if ma_nhap.strip() == st.session_state.ma_captcha_xac_thuc:
                        st.session_state.is_admin_mode = (tai_khoan_ghi_nho["Vai trò"] == "Ban Giám hiệu" or tai_khoan_ghi_nho["Tên đăng nhập"] == "admin" or "Toàn quyền" in str(tai_khoan_ghi_nho.get("Quyền quản lý", "")))
                        st.session_state.user_login = {
                            "logged_in": True,
                            "username": tai_khoan_ghi_nho["Tên đăng nhập"],
                            "fullname": tai_khoan_ghi_nho["Họ và tên"],
                            "role": tai_khoan_ghi_nho["Vai trò"],
                            "chuc_danh": tai_khoan_ghi_nho.get("Chức danh", tai_khoan_ghi_nho["Vai trò"]),
                            "ma_lien_ket": str(tai_khoan_ghi_nho.get("Mã liên kết", "")).strip(),
                            "phone": str(tai_khoan_ghi_nho.get("Số điện thoại", "")).strip(),
                            "quyen_quan_ly": str(tai_khoan_ghi_nho.get("Quyền quản lý", "Cá nhân")).strip()
                        }
                        st.session_state.ma_captcha_xac_thuc = str(random.randint(1000, 9999))
                        st.success(f"🎉 Xác thực thành công! Xin chào {tai_khoan_ghi_nho['Họ và tên']}.")
                        st.rerun()
                    else:
                        st.error("❌ Mã xác thực chưa chính xác! Vui lòng nhập đúng 4 chữ số hiển thị ở trên.")
                        st.session_state.ma_captcha_xac_thuc = str(random.randint(1000, 9999))
            
            c_sub1, c_sub2 = st.columns(2)
            with c_sub1:
                if st.button("🔄 Đổi mã bảo mật khác", use_container_width=True):
                    st.session_state.ma_captcha_xac_thuc = str(random.randint(1000, 9999))
                    st.rerun()
            with c_sub2:
                if st.button("🚪 Đăng nhập tài khoản khác", type="secondary", use_container_width=True):
                    xoa_phien_ghi_nho(token_curr)
                    if "token" in st.query_params:
                        del st.query_params["token"]
                    st.components.v1.html("""
                        <script>
                            try { window.parent.localStorage.removeItem('thpt2_saved_token'); } catch(e) {}
                            try { localStorage.removeItem('thpt2_saved_token'); } catch(e) {}
                        </script>
                    """, height=0, width=0)
                    st.rerun()
        else:
            with st.form("form_dang_nhap_he_thong"):
                st.markdown("#### 🔐 ĐĂNG NHẬP HỆ THỐNG")
                ten_dn = st.text_input("👤 Tên đăng nhập:", placeholder="Nhập tên đăng nhập (VD: admin, quannhiem, phuhuynh...)")
                mat_khau = st.text_input("🔑 Mật khẩu:", type="password", placeholder="Nhập mật khẩu được cấp...")
                
                ghi_nho_tk = st.checkbox(
                    "💾 Ghi nhớ đăng nhập trên thiết bị này (Lần sau chỉ cần xác nhận mã)",
                    value=True,
                    help="Khi bật tính năng này, lần sau vào lại app bạn sẽ không cần phải gõ lại tên và mật khẩu."
                )
                
                btn_login = st.form_submit_button("🚀 ĐĂNG NHẬP VÀO HỆ THỐNG", type="primary", use_container_width=True)
                
                if btn_login:
                    ten_clean = ten_dn.strip().lower()
                    mk_clean = mat_khau.strip()
                    if not ten_clean or not mk_clean:
                        st.warning("⚠️ Vui lòng nhập đầy đủ tên đăng nhập và mật khẩu.")
                    else:
                        df_tk_check = pd.read_csv(FILE_TAI_KHOAN, encoding='utf-8-sig').fillna("")
                        sdt_clean = ten_clean.replace(".", "").replace(" ", "").replace("-", "")
                        sdt_no_0 = sdt_clean.lstrip("0")
                        sdt_with_0 = "0" + sdt_no_0
                        mask_u = (df_tk_check["Tên đăng nhập"].str.lower() == ten_clean)
                        if "Số điện thoại" in df_tk_check.columns:
                            col_sdt_clean = df_tk_check["Số điện thoại"].astype(str).str.replace(".0", "").str.strip()
                            mask_u = mask_u | col_sdt_clean.isin([sdt_clean, sdt_no_0, sdt_with_0])
                        if "Mã liên kết" in df_tk_check.columns:
                            mask_u = mask_u | (df_tk_check["Mã liên kết"].astype(str).str.lower().str.replace("-", "") == ten_clean.replace("-", ""))
                        
                        user_found = df_tk_check[mask_u]
                        if not user_found.empty:
                            row_u = user_found.iloc[0]
                            if str(row_u["Mật khẩu"]).strip() == mk_clean:
                                if str(row_u.get("Trạng thái", "")) == "Tạm khóa":
                                    st.error("❌ Tài khoản này hiện đang bị tạm khóa. Vui lòng liên hệ Ban Giám Hiệu!")
                                else:
                                    if ghi_nho_tk:
                                        new_token = secrets.token_hex(16)
                                        luu_phien_ghi_nho(new_token, row_u)
                                        st.query_params["token"] = new_token
                                        st.components.v1.html(f"""
                                            <script>
                                                try {{ window.parent.localStorage.setItem('thpt2_saved_token', '{new_token}'); }} catch(e) {{}}
                                                try {{ localStorage.setItem('thpt2_saved_token', '{new_token}'); }} catch(e) {{}}
                                            </script>
                                        """, height=0, width=0)
                                    
                                    st.session_state.is_admin_mode = (row_u["Vai trò"] == "Ban Giám hiệu" or row_u["Tên đăng nhập"] == "admin" or "Toàn quyền" in str(row_u.get("Quyền quản lý", "")))
                                    st.session_state.user_login = {
                                        "logged_in": True,
                                        "username": row_u["Tên đăng nhập"],
                                        "fullname": row_u["Họ và tên"],
                                        "role": row_u["Vai trò"],
                                        "chuc_danh": row_u.get("Chức danh", row_u["Vai trò"]),
                                        "ma_lien_ket": str(row_u.get("Mã liên kết", "")).strip(),
                                        "phone": str(row_u.get("Số điện thoại", "")).strip(),
                                        "quyen_quan_ly": str(row_u.get("Quyền quản lý", "Cá nhân")).strip()
                                    }
                                    st.success(f"🎉 Đăng nhập thành công! Xin chào {row_u['Họ và tên']}.")
                                    st.rerun()
                            else:
                                st.error("❌ Mật khẩu không chính xác! Vui lòng kiểm tra lại.")
                        else:
                            st.error(f"❌ Tài khoản hoặc số điện thoại '{ten_dn}' không tồn tại. Vui lòng kiểm tra lại!")


        with st.expander("💡 **HƯỚNG DẪN TÀI KHOẢN ĐĂNG NHẬP THEO TỪNG VỊ TRÍ:**", expanded=False):
            st.markdown("""
            | Vị trí / Đối tượng | Tên đăng nhập mẫu | Mật khẩu ban đầu |
            | :--- | :---: | :---: |
            | **👑 Hiệu Trưởng / BGH** | `hieutruong` hoặc `admin` | `ht123` / `bgh123` |
            | **👑 Phó Hiệu Trưởng (Bán trú / CM)** | `phohieutruong1` / `phohieutruong2` | `pht123` |
            | **🚩 Bí Thư & Ban Chấp Hành Đoàn** | `bithudoan` | `dtn123` |
            | **🚩 Đội Cờ Đỏ Chấm Nề Nếp** | `codo` | `codo123` |
            | **👨‍🏫 Giáo viên Quản nhiệm / Trực KTX** | `quannhiem` / `gvtruc01` / `gvtruc02` | `qn123` / `truc123` |
            | **👨‍🏫 Giáo viên Chủ nhiệm (21 Lớp)** | `gvcn_10a1`, `gvcn_10a2`, `gvcn_11a1`... | `gvcn123` |
            | **🍳 Bếp Trưởng & Tổ Cấp Dưỡng** | `beptruong` / `capduong` / `nhabep` | `bep123` |
            | **💰 Kế Toán Bán Trú** | `ketoan` | `kt123` |
            | **🎒 Học sinh Bán trú KTX** | Mã HS (VD: `hsn001`, `hsu001`) hoặc SĐT HS | `hs123` |
            | **👨‍👩‍👧 Phụ huynh Học sinh** | **Số điện thoại Bố/Mẹ** hoặc `ph_hsn001`... | `ph123` |
            """)

    with col_l2:
        link_qr_cai_app = duong_dan_online.split('?')[0] if duong_dan_online else duong_dan_app_mobile
        st.markdown(f"""
        <div style="border: 2px solid #16A34A; padding: 18px; border-radius: 14px; background: #F0FDF4; box-shadow: 0 4px 12px rgba(22, 163, 74, 0.12); text-align: center;">
            <div style="background:#16A34A; color:white; display:inline-block; padding:4px 14px; border-radius:20px; font-weight:bold; font-size:12px; margin-bottom:8px;">
                📱 CÀI ĐẶT APP LÊN ĐIỆN THOẠI
            </div>
            <h4 style="color:#15803D; margin:4px 0 8px 0;">DÙNG CAMERA ĐIỆN THOẠI QUÉT MÃ</h4>
            <div style="background:white; padding:10px; border-radius:10px; display:inline-block; border:1px solid #BBF7D0;">
                <img src="https://api.qrserver.com/v1/create-qr-code/?size=280x280&data={link_qr_cai_app}" width="210" style="display:block; border-radius:6px;">
            </div>
            <p style="margin-top:8px; font-size:13px; font-weight:bold; color:#166534; margin-bottom:4px;">
                Địa chỉ đám mây 24/7 (4G / Wi-Fi toàn cầu):<br>
                <a href="{link_qr_cai_app}" target="_blank" style="color:#2563EB; font-size:14px; word-break:break-all; text-decoration:underline;">{link_qr_cai_app}</a>
            </p>
            <div style="text-align: left; background: white; padding: 10px 14px; border-radius: 8px; border: 1px solid #E2E8F0; font-size: 12px; line-height: 1.5; color: #1E293B; margin-top: 8px;">
                <b>📲 CÁCH CÀI THÀNH APP MÀN HÌNH CHÍNH (30s):</b><br>
                🍏 <b>iPhone (Safari):</b> Quét mã ➜ Bấm nút <b>Chia sẻ</b> ⬆️ ở đáy ➜ Chọn <b>"Thêm vào MH chính"</b>.<br>
                🤖 <b>Android (Chrome):</b> Quét mã ➜ Bấm <b>3 chấm ⋮</b> góc trên ➜ Chọn <b>"Cài đặt ứng dụng"</b>.
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        file_qr_local = "D:\\QR_Cai_App_Ban_Tru.png"
        if os.path.exists(file_qr_local):
            with open(file_qr_local, "rb") as f_qr:
                st.download_button(
                    label="💾 Tải ảnh QR này về máy (gửi Zalo / In ấn)",
                    data=f_qr.read(),
                    file_name="QR_Cai_App_Ban_Tru_THPT2_BaoYen.png",
                    mime="image/png",
                    use_container_width=True
                )
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
    st.caption(f"Trường THPT số 2 Bảo Yên - Lào Cai ({st.session_state.nam_hoc_hien_tai})")
    
    st.markdown("---")
    st.markdown("#### 📅 **NĂM HỌC**")
    chon_nh_sb = st.selectbox(
        "Năm học làm việc:",
        options=danh_sach_nam_hoc,
        index=danh_sach_nam_hoc.index(st.session_state.nam_hoc_hien_tai) if st.session_state.nam_hoc_hien_tai in danh_sach_nam_hoc else 0,
        key="sb_select_nam_hoc"
    )
    if chon_nh_sb != st.session_state.nam_hoc_hien_tai:
        st.session_state.nam_hoc_hien_tai = chon_nh_sb
        st.rerun()

    if st.session_state.nam_hoc_hien_tai != nam_hoc_mac_dinh:
        st.warning(f"📂 Hồ sơ lưu trữ: **{st.session_state.nam_hoc_hien_tai}**")

    st.markdown("---")
    st.markdown("#### 🏛️ **PHÂN HỆ HỆ THỐNG**")
    ds_phan_he = [
        "🏛️ HỆ THỐNG QUẢN TRỊ & ĐIỀU HÀNH NHÀ TRƯỜNG",
        "🛏️ QUẢN LÝ BÁN TRÚ & KTX",
        "🚩 ĐOÀN THANH NIÊN (ĐTN)"
    ]
    if "phan_he_hien_tai" not in st.session_state:
        st.session_state.phan_he_hien_tai = "🛏️ QUẢN LÝ BÁN TRÚ & KTX"

    chon_phan_he_sb = st.radio(
        "Chọn phân hệ:",
        ds_phan_he,
        index=ds_phan_he.index(st.session_state.phan_he_hien_tai) if st.session_state.phan_he_hien_tai in ds_phan_he else 0,
        key="radio_chon_phan_he"
    )
    if chon_phan_he_sb != st.session_state.phan_he_hien_tai:
        st.session_state.phan_he_hien_tai = chon_phan_he_sb
        st.rerun()
    
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
        "Học sinh": "badge-hs",
        "Ban Chấp hành Đoàn": "badge-bep",
        "Đội Cờ đỏ": "badge-bgh"
    }.get(role_curr, "badge-bgh")
    
    chuc_danh_hien = u_curr.get("chuc_danh", role_curr)
    ma_lk_hien = u_curr.get("ma_lien_ket", "")
    
    st.markdown(f"👤 Người dùng: **{u_curr['fullname']}**")
    st.markdown(f"📌 Chức danh: **{chuc_danh_hien}**")
    if ma_lk_hien and ma_lk_hien != "Toàn trường":
        st.markdown(f"🔗 Liên kết: `{ma_lk_hien}`")
    st.markdown(f"Vai trò: <span class='{badge_color}'>{role_curr}</span>", unsafe_allow_html=True)
    
    # ⚙️ CHỨC NĂNG CÁ NHÂN HÓA & ĐỔI MẬT KHẨU DÀNH CHO MỌI TÀI KHOẢN (BGH, GVCN, BẾP, PHỤ HUYNH, HỌC SINH)
    u_username = u_curr["username"]
    df_tk_pw_check = pd.read_csv(FILE_TAI_KHOAN, encoding='utf-8-sig', dtype=str).fillna("")
    user_row_curr = df_tk_pw_check[df_tk_pw_check["Tên đăng nhập"] == u_username]
    is_default_pw = False
    curr_phone = u_curr.get("phone", "")
    curr_fullname = u_curr.get("fullname", "")
    
    if not user_row_curr.empty:
        pw_now = str(user_row_curr.iloc[0]["Mật khẩu"]).strip()
        curr_phone = str(user_row_curr.iloc[0].get("Số điện thoại", "")).replace(".0", "").strip()
        curr_fullname = str(user_row_curr.iloc[0].get("Họ và tên", curr_fullname)).strip()
        default_list = ['bgh123', 'ht123', 'pht123', 'qn123', 'truc123', 'gvcn123', 'bep123', 'kt123', 'hs123', 'ph123']
        if pw_now in default_list:
            is_default_pw = True

    if is_default_pw:
        st.warning("🔔 **Nhắc nhở an toàn:** Bạn đang dùng mật khẩu ban đầu. Hãy đổi mật khẩu bên dưới để cá nhân hóa và bảo vệ tài khoản nhé!")

    with st.expander("⚙️ **Cá Nhân Hóa & Tài Khoản Của Tôi:**", expanded=is_default_pw):
        tab_pw, tab_prof, tab_req_role, tab_my_veh = st.tabs(["🔑 Đổi mật khẩu", "👤 Thông tin cá nhân", "📝 Đề xuất quyền", "🛵 Xe của tôi"])
        with tab_pw:
            st.caption("🔒 Tự đặt mật khẩu riêng để bảo vệ tài khoản cá nhân của bạn:")
            with st.form("form_doi_mat_khau_ca_nhan"):
                pw_cu = st.text_input("Mật khẩu hiện tại:", type="password", placeholder="Nhập mật khẩu đang dùng...")
                pw_moi = st.text_input("Mật khẩu mới:", type="password", placeholder="Nhập mật khẩu mới (tối thiểu 4 ký tự)...")
                pw_xac_nhan = st.text_input("Xác nhận mật khẩu mới:", type="password", placeholder="Nhập lại mật khẩu mới...")
                btn_save_pw = st.form_submit_button("💾 LƯU MẬT KHẨU MỚI", type="primary", use_container_width=True)
                
                if btn_save_pw:
                    df_tk_pw = pd.read_csv(FILE_TAI_KHOAN, encoding='utf-8-sig', dtype=str).fillna("")
                    idx_user = df_tk_pw[df_tk_pw["Tên đăng nhập"] == u_username].index
                    
                    if idx_user.empty:
                        st.error("❌ Không tìm thấy thông tin tài khoản để đổi mật khẩu!")
                    else:
                        curr_real_pw = str(df_tk_pw.loc[idx_user[0], "Mật khẩu"]).strip()
                        if pw_cu.strip() != curr_real_pw:
                            st.error("❌ Mật khẩu hiện tại không chính xác!")
                        elif len(pw_moi.strip()) < 4:
                            st.error("⚠️ Mật khẩu mới quá ngắn! Vui lòng nhập tối thiểu 4 ký tự.")
                        elif pw_moi.strip() != pw_xac_nhan.strip():
                            st.error("❌ Mật khẩu mới và mật khẩu xác nhận không trùng khớp!")
                        else:
                            new_pw_clean = pw_moi.strip()
                            df_tk_pw.loc[idx_user[0], "Mật khẩu"] = new_pw_clean
                            df_tk_pw.to_csv(FILE_TAI_KHOAN, index=False, encoding='utf-8-sig')
                            
                            # Đồng bộ sang các vị trí khác
                            for dest_dir in ['D:/phan_mem_ban_tru_cloud', 'd:/OneDrive/Hô sơ cá nhan/Học AI']:
                                p_sync = os.path.join(dest_dir, 'tai_khoan_nguoi_dung.csv')
                                if os.path.exists(dest_dir):
                                    try:
                                        df_tk_pw.to_csv(p_sync, index=False, encoding='utf-8-sig')
                                    except Exception:
                                        pass
                                        
                            st.success("🎉 Đổi mật khẩu thành công! Mật khẩu mới đã được kích hoạt.")
                            st.balloons()
                            st.rerun()

        with tab_prof:
            st.caption("📱 Cập nhật số điện thoại & thông tin cá nhân của CHÍNH BẠN:")
            st.info("🔒 **Quy tắc phân quyền:** Bạn chỉ có thể sửa thông tin của chính mình. Chỉ Ban Giám Hiệu hoặc người được Admin cấp quyền quản lý mới có quyền chỉnh sửa người khác.")
            with st.form("form_cap_nhat_thong_tin"):
                sdt_moi = st.text_input("Số điện thoại liên hệ:", value=curr_phone, placeholder="VD: 0912345678")
                ten_moi = st.text_input("Họ và tên hiển thị:", value=curr_fullname)
                st.text_input("Tên đăng nhập:", value=u_username, disabled=True)
                st.text_input("Vai trò hiện tại:", value=role_curr, disabled=True)
                btn_save_prof = st.form_submit_button("💾 LƯU THÔNG TIN CỦA TÔI", use_container_width=True)
                
                if btn_save_prof:
                    df_tk_pw = pd.read_csv(FILE_TAI_KHOAN, encoding='utf-8-sig', dtype=str).fillna("")
                    idx_user = df_tk_pw[df_tk_pw["Tên đăng nhập"] == u_username].index
                    if not idx_user.empty:
                        clean_sdt = sdt_moi.strip().replace(" ", "").replace(".", "")
                        df_tk_pw.loc[idx_user[0], "Số điện thoại"] = clean_sdt
                        if ten_moi.strip():
                            df_tk_pw.loc[idx_user[0], "Họ và tên"] = ten_moi.strip()
                            st.session_state.user_login["fullname"] = ten_moi.strip()
                        st.session_state.user_login["phone"] = clean_sdt
                        df_tk_pw.to_csv(FILE_TAI_KHOAN, index=False, encoding='utf-8-sig')
                        for dest_dir in ['D:/phan_mem_ban_tru_cloud', 'd:/OneDrive/Hô sơ cá nhan/Học AI']:
                            p_sync = os.path.join(dest_dir, 'tai_khoan_nguoi_dung.csv')
                            if os.path.exists(dest_dir):
                                try:
                                    df_tk_pw.to_csv(p_sync, index=False, encoding='utf-8-sig')
                                except Exception:
                                    pass
                        st.success("🎉 Cập nhật thông tin cá nhân thành công!")
                        st.rerun()

        with tab_req_role:
            st.caption("📝 Gửi đề xuất cấp quyền tới Ban Giám Hiệu / Admin:")
            f_req = os.path.join(BASE_DIR, "de_xuat_cap_quyen.csv")
            if os.path.exists(f_req):
                df_req = pd.read_csv(f_req, encoding='utf-8-sig', dtype=str).fillna("")
            else:
                df_req = pd.DataFrame(columns=["Mã yêu cầu", "Tên đăng nhập", "Họ và tên", "Quyền xin cấp", "Lý do", "Ngày gửi", "Trạng thái"])
            
            my_reqs = df_req[df_req["Tên đăng nhập"] == u_username]
            if not my_reqs.empty:
                st.markdown("**Các đề xuất bạn đã gửi:**")
                for _, r_rq in my_reqs.iterrows():
                    tt = r_rq['Trạng thái']
                    c_tt = "🟢" if tt == "Đã duyệt" else ("🔴" if tt == "Từ chối" else "🟡")
                    st.caption(f"{c_tt} **{r_rq['Mã yêu cầu']}**: {r_rq['Quyền xin cấp']} ({tt}) - Ngày gửi: {r_rq['Ngày gửi']}")
                st.markdown("---")

            with st.form("form_de_xuat_cap_quyen_cb"):
                opt_quyen = [
                    "Quản lý phương tiện & Xe cộ",
                    "Đội Cờ đỏ / Ban Chấp hành Đoàn",
                    "Quản lý công việc & Lịch công tác tuần",
                    "Ban Quản lý KTX & Bán trú",
                    "Quản lý bếp ăn & Suất ăn",
                    "Toàn quyền quản trị (Admin)"
                ]
                quyen_muon_xin = st.selectbox("Quyền muốn đề xuất cấp:", opt_quyen)
                ly_do_xin = st.text_area("Lý do / Phân công nhiệm vụ:", placeholder="Nhập lý do hoặc phân công của nhà trường để BGH phê duyệt...")
                btn_gui_dx = st.form_submit_button("📤 GỬI ĐỀ XUẤT CẤP QUYỀN", type="primary", use_container_width=True)
                if btn_gui_dx:
                    if not ly_do_xin.strip():
                        st.warning("Vui lòng ghi rõ lý do xin cấp quyền.")
                    else:
                        ma_moi = f"YC-{len(df_req) + 1:03d}"
                        ngay_nay = date.today().strftime("%d/%m/%Y")
                        new_row_rq = pd.DataFrame([{
                            "Mã yêu cầu": ma_moi,
                            "Tên đăng nhập": u_username,
                            "Họ và tên": u_curr.get("fullname", ""),
                            "Quyền xin cấp": quyen_muon_xin,
                            "Lý do": ly_do_xin.strip(),
                            "Ngày gửi": ngay_nay,
                            "Trạng thái": "Chờ duyệt"
                        }])
                        df_req = pd.concat([df_req, new_row_rq], ignore_index=True)
                        for d_sync in [f_req, os.path.join(BASE_DIR, "de_xuat_cap_quyen.csv"), os.path.join("D:/phan_mem_ban_tru_cloud", "de_xuat_cap_quyen.csv"), os.path.join("d:/OneDrive/Hô sơ cá nhan/Học AI", "de_xuat_cap_quyen.csv")]:
                            try:
                                df_req.to_csv(d_sync, index=False, encoding='utf-8-sig')
                            except Exception:
                                pass
                        st.success(f"🎉 Đã gửi đề xuất ({ma_moi}) tới Ban Giám Hiệu thành công!")
                        st.rerun()

        with tab_my_veh:
            st.caption("🛵 Quản lý phương tiện cá nhân & Mã QR của bạn:")
            f_xe = os.path.join(BASE_DIR, "quan_ly_phuong_tien.csv")
            if os.path.exists(f_xe):
                df_xe_all = pd.read_csv(f_xe, encoding='utf-8-sig', dtype=str).fillna("")
            else:
                df_xe_all = pd.DataFrame()
            
            u_name = u_curr.get("fullname", "")
            u_phone = str(u_curr.get("phone", "")).replace(".0", "").strip()
            u_ref = str(u_curr.get("ma_lien_ket", "")).strip()
            
            mask_my = pd.Series([False] * len(df_xe_all))
            if not df_xe_all.empty:
                mask_my = (df_xe_all['Họ và tên'] == u_name) | (df_xe_all['Mã xe'] == u_ref)
                if u_phone:
                    col_p = df_xe_all['SĐT Học sinh'].astype(str).str.replace(".0", "").str.strip()
                    mask_my = mask_my | col_p.isin([u_phone, u_phone.lstrip('0'), '0' + u_phone.lstrip('0')])
            
            my_xe = df_xe_all[mask_my] if not df_xe_all.empty else pd.DataFrame()
            if not my_xe.empty:
                r_my = my_xe.iloc[0]
                st.markdown(f"**Biển số:** `{r_my['Biển số xe']}` | **Loại xe:** {r_my['Loại xe']}")
                st.markdown(f"**Nơi gửi:** {r_my['Nơi gửi xe']} | **Số lần vi phạm:** `{r_my['Số lần vi phạm']}`")
                
                # Hiển thị mã QR thẻ xe
                txt_qr_my = phan_he_doan_thanh_nien.tao_noi_dung_qr_xe(r_my)
                img_qr_my = tao_anh_qr_base64(txt_qr_my)
                st.markdown(f"""
                    <div style='text-align:center; background:#F0FDF4; border:1px solid #10B981; border-radius:8px; padding:10px; margin:8px 0;'>
                        <p style='color:#059669; font-weight:bold; margin:0; font-size:12px;'>MÃ QR XE CỦA BẠN</p>
                        <img src="{img_qr_my}" width="140" style="margin:5px 0;">
                        <p style='color:#1E3A8A; font-weight:bold; margin:0;'>{r_my['Biển số xe']}</p>
                    </div>
                """, unsafe_allow_html=True)
                
                with st.form("form_update_xe_sb"):
                    my_bs_sb = st.text_input("Biển số xe:", value=str(r_my['Biển số xe']))
                    my_loai_sb = st.selectbox("Loại xe:", ["Xe máy điện", "Xe đạp điện", "Xe máy <50cc", "Xe đạp"], index=["Xe máy điện", "Xe đạp điện", "Xe máy <50cc", "Xe đạp"].index(r_my['Loại xe']) if r_my['Loại xe'] in ["Xe máy điện", "Xe đạp điện", "Xe máy <50cc", "Xe đạp"] else 0)
                    my_mau_sb = st.text_input("Màu xe / Nhãn hiệu:", value=str(r_my['Màu xe']))
                    my_noigui_sb = st.selectbox("Nơi gửi xe:", ["Nhà xe KTX Bán trú", "Nhà xe Học sinh Khu A", "Nhà xe Học sinh Khu B"], index=0)
                    my_sdt_sb = st.text_input("SĐT liên hệ xe:", value=str(r_my['SĐT Học sinh']))
                    if st.form_submit_button("💾 LƯU CẬP NHẬT XE CỦA TÔI", use_container_width=True):
                        idx_xe_sb = r_my.name
                        df_xe_all.loc[idx_xe_sb, 'Biển số xe'] = my_bs_sb.strip()
                        df_xe_all.loc[idx_xe_sb, 'Loại xe'] = my_loai_sb
                        df_xe_all.loc[idx_xe_sb, 'Màu xe'] = my_mau_sb.strip()
                        df_xe_all.loc[idx_xe_sb, 'Nơi gửi xe'] = my_noigui_sb
                        df_xe_all.loc[idx_xe_sb, 'SĐT Học sinh'] = my_sdt_sb.strip()
                        for d_sync in [f_xe, os.path.join(BASE_DIR, "quan_ly_phuong_tien.csv"), os.path.join("D:/phan_mem_ban_tru_cloud", "quan_ly_phuong_tien.csv"), os.path.join("d:/OneDrive/Hô sơ cá nhan/Học AI", "quan_ly_phuong_tien.csv")]:
                            try:
                                df_xe_all.to_csv(d_sync, index=False, encoding='utf-8-sig')
                            except Exception:
                                pass
                        st.success("🎉 Cập nhật thông tin xe thành công!")
                        st.rerun()
            else:
                st.info("💡 Bạn chưa đăng ký phương tiện trên hệ thống. Hãy đăng ký thông tin xe dưới đây:")
                with st.form("form_reg_new_xe"):
                    reg_bs = st.text_input("Biển số xe (VD: 24MD1-123.45):")
                    reg_loai = st.selectbox("Loại xe:", ["Xe máy điện", "Xe đạp điện", "Xe máy <50cc", "Xe đạp"])
                    reg_mau = st.text_input("Màu xe / Nhãn hiệu:")
                    reg_noigui = st.selectbox("Nơi gửi xe:", ["Nhà xe KTX Bán trú", "Nhà xe Học sinh Khu A", "Nhà xe Học sinh Khu B"])
                    if st.form_submit_button("✨ ĐĂNG KÝ PHƯƠNG TIỆN MỚI", type="primary", use_container_width=True):
                        if not reg_bs.strip():
                            st.warning("Vui lòng nhập biển số xe.")
                        else:
                            ma_xe_moi = f"XE-{len(df_xe_all) + 1:03d}"
                            dong_xe_moi = pd.DataFrame([{
                                'Mã xe': ma_xe_moi,
                                'Họ và tên': u_name,
                                'Lớp': u_curr.get('ma_lien_ket', '10A1'),
                                'SĐT Học sinh': u_phone,
                                'Loại xe': reg_loai,
                                'Biển số xe': reg_bs.strip(),
                                'Màu xe': reg_mau.strip(),
                                'Nơi gửi xe': reg_noigui,
                                'GVCN': 'Thầy/Cô GVCN',
                                'SĐT GVCN': '0988123001',
                                'Họ tên Phụ huynh': 'Phụ huynh ' + u_name,
                                'SĐT Phụ huynh': u_phone,
                                'Địa chỉ': 'Bảo Hà, Bảo Yên',
                                'Tình trạng': 'Đủ điều kiện lưu hành',
                                'Số lần vi phạm': 0,
                                'Ghi chú': 'Cá nhân tự khai báo'
                            }])
                            df_xe_all = pd.concat([df_xe_all, dong_xe_moi], ignore_index=True)
                            for d_sync in [f_xe, os.path.join(BASE_DIR, "quan_ly_phuong_tien.csv"), os.path.join("D:/phan_mem_ban_tru_cloud", "quan_ly_phuong_tien.csv"), os.path.join("d:/OneDrive/Hô sơ cá nhan/Học AI", "quan_ly_phuong_tien.csv")]:
                                try:
                                    df_xe_all.to_csv(d_sync, index=False, encoding='utf-8-sig')
                                except Exception:
                                    pass
                            st.success(f"🎉 Đã đăng ký phương tiện ({reg_bs.strip()}) thành công!")
                            st.rerun()

    # Nút đăng xuất tài khoản
    if st.button("🚪 ĐĂNG XUẤT (THOÁT RA)", type="secondary", use_container_width=True):
        token_to_del = st.query_params.get("token", "")
        if token_to_del:
            xoa_phien_ghi_nho(token_to_del)
            del st.query_params["token"]
        st.components.v1.html("""
            <script>
                try { window.parent.localStorage.removeItem('thpt2_saved_token'); } catch(e) {}
                try { localStorage.removeItem('thpt2_saved_token'); } catch(e) {}
            </script>
        """, height=0, width=0)
        st.session_state.user_login = {
            "logged_in": False,
            "username": "",
            "fullname": "",
            "role": ""
        }
        st.rerun()
    
    # Đảm bảo nhận diện Admin tối cao để cho phép chuyển linh hoạt mọi vai trò
    if role_curr == "Ban Giám hiệu" or u_curr.get("username") == "admin" or "Toàn quyền" in str(u_curr.get("quyen_quan_ly", "")):
        st.session_state.is_admin_mode = True

    if st.session_state.get("is_admin_mode", False):
        st.markdown("---")
        with st.expander("🔄 **CHUYỂN VAI TRÒ ĐỂ TRẢI NGHIỆM (ADMIN):**", expanded=(role_curr != "Ban Giám hiệu")):
            danh_sach_vai_tro = [
                "👑 Ban Giám hiệu (Toàn quyền Admin)",
                "👨‍🏫 Giáo viên chủ nhiệm (GVCN Lớp 10A1)",
                "👮 Giáo viên Quản nhiệm KTX Bán trú",
                "🚩 Bí thư Đoàn trường / BCH Đoàn",
                "⚖️ Đội Cờ đỏ chấm nề nếp",
                "💰 Kế toán bán trú",
                "🍳 Nhà bếp / Cấp dưỡng",
                "👨‍👩‍👧 Phụ huynh học sinh",
                "🎒 Học sinh bán trú (Trưởng phòng 301)"
            ]
            role_map = {
                "👑 Ban Giám hiệu (Toàn quyền Admin)": {
                    "username": "admin", "fullname": "Ban Giám Hiệu", "role": "Ban Giám hiệu", "chuc_danh": "Ban Giám Hiệu", "quyen_quan_ly": "Toàn quyền", "ma_lien_ket": "Toàn trường"
                },
                "👨‍🏫 Giáo viên chủ nhiệm (GVCN Lớp 10A1)": {
                    "username": "gvcn10a1", "fullname": "Thầy Trần Văn Đoàn (GVCN 10A1)", "role": "Giáo viên quản lý", "chuc_danh": "GVCN Lớp 10A1", "ma_lien_ket": "10A1", "quyen_quan_ly": "Cá nhân"
                },
                "👮 Giáo viên Quản nhiệm KTX Bán trú": {
                    "username": "quannhiem", "fullname": "Thầy Đỗ Văn Kiên (Tổ trưởng Quản nhiệm)", "role": "Giáo viên quản lý", "chuc_danh": "Tổ trưởng Quản nhiệm KTX", "ma_lien_ket": "Toàn trường", "quyen_quan_ly": "Ban Quản lý KTX & Bán trú"
                },
                "🚩 Bí thư Đoàn trường / BCH Đoàn": {
                    "username": "doantruong", "fullname": "Thầy Hoàng Văn D (Bí thư Đoàn)", "role": "Ban Chấp hành Đoàn", "chuc_danh": "Bí thư Đoàn trường", "ma_lien_ket": "Toàn trường", "quyen_quan_ly": "Đội Cờ đỏ / Ban Chấp hành Đoàn"
                },
                "⚖️ Đội Cờ đỏ chấm nề nếp": {
                    "username": "codo", "fullname": "Đội Cờ Đỏ Học Sinh", "role": "Đội Cờ đỏ", "chuc_danh": "Cờ đỏ toàn trường", "ma_lien_ket": "Toàn trường", "quyen_quan_ly": "Đội Cờ đỏ / Ban Chấp hành Đoàn"
                },
                "💰 Kế toán bán trú": {
                    "username": "ketoan", "fullname": "Cô Phạm Thị Lan (Kế toán)", "role": "Kế toán bán trú", "chuc_danh": "Kế toán bán trú", "ma_lien_ket": "Toàn trường", "quyen_quan_ly": "Cá nhân"
                },
                "🍳 Nhà bếp / Cấp dưỡng": {
                    "username": "nhabep", "fullname": "Tổ Cấp Dưỡng Nhà Bếp", "role": "Nhà bếp / Cấp dưỡng", "chuc_danh": "Tổ cấp dưỡng", "ma_lien_ket": "Toàn trường", "quyen_quan_ly": "Quản lý bếp ăn & Suất ăn"
                },
                "👨‍👩‍👧 Phụ huynh học sinh": {
                    "username": "phuhuynh", "fullname": "Phụ Huynh Em Nguyễn Thị Thanh Thảo", "role": "Phụ huynh học sinh", "chuc_danh": "Phụ huynh học sinh 10A1", "ma_lien_ket": "HS0001", "quyen_quan_ly": "Cá nhân"
                },
                "🎒 Học sinh bán trú (Trưởng phòng 301)": {
                    "username": "hocsinh", "fullname": "Em Nguyễn Thị Thanh Thảo", "role": "Học sinh", "chuc_danh": "Trưởng phòng (Phòng 301)", "ma_lien_ket": "HS0001", "quyen_quan_ly": "Cá nhân"
                }
            }
            chon_role_nhanh = st.selectbox("Chọn vai trò trải nghiệm:", danh_sach_vai_tro, index=0)
            if st.button("🚀 Chuyển xem & thực hiện ngay", use_container_width=True, type="primary"):
                info_new = role_map[chon_role_nhanh]
                st.session_state.user_login = {
                    "logged_in": True,
                    **info_new
                }
                st.rerun()

            if role_curr != "Ban Giám hiệu":
                if st.button("⬅️ Quay lại quyền Ban Giám Hiệu (Admin)", use_container_width=True):
                    st.session_state.user_login = {
                        "logged_in": True,
                        "username": "admin",
                        "fullname": "Ban Giám Hiệu",
                        "role": "Ban Giám hiệu",
                        "chuc_danh": "Ban Giám Hiệu",
                        "quyen_quan_ly": "Toàn quyền"
                    }
                    st.rerun()


# ========================================================
# Hiển thị thanh thông báo trải nghiệm dành cho Admin khi đang đóng vai trò khác
if st.session_state.get("is_admin_mode", False) and role_curr != "Ban Giám hiệu":
    c_w1, c_w2 = st.columns([3, 1])
    with c_w1:
        st.info(f"🔄 **CHẾ ĐỘ TRẢI NGHIỆM DÀNH CHO ADMIN:** Bạn đang xem và thao tác thử nghiệm với vai trò **{role_curr}** ({u_curr['fullname']}). Toàn bộ chức năng đã được mở đầy đủ để trải nghiệm.")
    with c_w2:
        if st.button("⬅️ Quay lại Admin", key="btn_top_back_bgh", type="primary", use_container_width=True):
            st.session_state.user_login = {
                "logged_in": True,
                "username": "admin",
                "fullname": "Ban Giám Hiệu",
                "role": "Ban Giám hiệu",
                "chuc_danh": "Ban Giám Hiệu",
                "quyen_quan_ly": "Toàn quyền"
            }
            st.rerun()

# 4. ĐIỀU HƯỚNG THEO PHÂN HỆ HỆ THỐNG
# ========================================================
if "QUẢN TRỊ" in st.session_state.phan_he_hien_tai or "QUẢN LÝ CHUNG" in st.session_state.phan_he_hien_tai or "ĐIỀU HÀNH" in st.session_state.phan_he_hien_tai:
    import phan_he_quan_ly_chung
    import importlib
    importlib.reload(phan_he_quan_ly_chung)
    phan_he_quan_ly_chung.render_phan_he_quan_ly_chung(df_tai_khoan, role_curr, st.session_state.nam_hoc_hien_tai, BASE_DIR, THU_MUC_NAM_HOC)
    st.stop()
elif st.session_state.phan_he_hien_tai == "🚩 ĐOÀN THANH NIÊN (ĐTN)":
    import phan_he_doan_thanh_nien
    import importlib
    importlib.reload(phan_he_doan_thanh_nien)
    phan_he_doan_thanh_nien.render_phan_he_doan_thanh_nien(df_tai_khoan, role_curr, st.session_state.nam_hoc_hien_tai, BASE_DIR, THU_MUC_NAM_HOC)
    st.stop()

# ========================================================
# HÀM HIỂN THỊ HƯỚNG DẪN CÀI ĐẶT APP DI ĐỘNG (DÙNG CHUNG)
# ========================================================
def hien_thi_tab_cai_dat_app(duong_dan_online, duong_dan_app_mobile):
    st.subheader("📱 HƯỚNG DẪN TẢI & CÀI ĐẶT APP BÁN TRÚ LÊN ĐIỆN THOẠI")
    col_m1, col_m2 = st.columns([1, 1.2], gap="large")
    with col_m1:
        st.markdown(f"""
        <div style="text-align: center; border: 3px solid #16A34A; padding: 20px; border-radius: 16px; background: #F0FDF4; box-shadow: 0 4px 15px rgba(22, 163, 74, 0.15); margin-bottom: 15px;">
            <div style="background:#16A34A; color:white; display:inline-block; padding:5px 16px; border-radius:20px; font-weight:bold; font-size:12px; margin-bottom:10px;">
                🌟 ĐỊA CHỈ ĐÁM MÂY CHÍNH THỨC (CHẠY 24/7 TOÀN CẦU)
            </div>
            <h4 style="color:#15803D; margin:5px 0 10px 0;">DÙNG CAMERA ĐIỆN THOẠI QUÉT MÃ</h4>
            <div style="background:white; padding:12px; border-radius:12px; display:inline-block; border:1px solid #BBF7D0;">
                <img src="https://api.qrserver.com/v1/create-qr-code/?size=300x300&data={duong_dan_online}" width="230" style="display:block; border-radius:6px;">
            </div>
            <p style="margin-top:10px; font-size:14px; font-weight:bold; color:#166534;">Địa chỉ trực tuyến chính thức:<br>
            <a href="{duong_dan_online}" target="_blank" style="color:#2563EB; font-size:16px; word-break:break-all; text-decoration:underline;">{duong_dan_online}</a></p>
            <p style="font-size:12px; color:#4B5563; margin-bottom:0;">(Mở được trên mọi mạng 4G/5G hoặc Wi-Fi bất kỳ, không phụ thuộc máy tính)</p>
        </div>
        """, unsafe_allow_html=True)
        
        file_qr_local = "D:\\QR_Cai_App_Ban_Tru.png"
        if os.path.exists(file_qr_local):
            with open(file_qr_local, "rb") as f_qr:
                st.download_button(
                    label="💾 TẢI ẢNH MÃ QR VỀ MÁY (ĐỂ IN HOẶC GỬI ZALO)",
                    data=f_qr.read(),
                    file_name="QR_Cai_App_Ban_Tru_THPT2_BaoYen.png",
                    mime="image/png",
                    use_container_width=True
                )
    with col_m2:
        st.markdown("### 📲 BIỂU TƯỢNG APP CHÍNH THỨC CỦA TRƯỜNG:")
        c_ico1, c_ico2 = st.columns([1, 2])
        with c_ico1:
            if os.path.exists(FILE_LOGO):
                st.image(FILE_LOGO, width=95, caption="Logo THPT số 2 Bảo Yên")
        with c_ico2:
            st.markdown("""
            - **Biểu tượng App:** Huy hiệu **Trường THPT số 2 Bảo Yên**.
            - **Tên App trên điện thoại:** `THPT 2 Bảo Yên`.
            """)
        st.markdown("""
        ---
        #### 🍏 Dành cho iPhone / iPad (Trình duyệt Safari):
        1. **Mở Camera** quét mã QR bên trái ➜ Chạm vào thông báo để mở web.
        2. Ở thanh dưới cùng Safari, bấm nút **Chia sẻ** *(ô vuông có mũi tên chỉ lên ⬆️)*.
        3. Cuộn xuống và chọn **"Thêm vào Màn hình chính"** *(Add to Home Screen)*.
        4. Bấm **"Thêm"** *(Add)* ở góc trên bên phải.
        
        ---
        #### 🤖 Dành cho Android (Samsung, Oppo, Xiaomi qua Chrome / Cốc Cốc):
        1. Dùng **Camera / Zalo** quét mã QR bên trái ➜ Mở bằng Chrome.
        2. Bấm dấu **3 chấm (⋮)** ở góc trên bên phải màn hình.
        3. Chọn dòng **"Cài đặt ứng dụng"** hoặc **"Thêm vào Màn hình chính"**.
        4. Bấm **"Cài đặt" / "Thêm"** để xác nhận.
        
        ---
        ✨ **LỢI ÍCH:** Mở ra dùng toàn màn hình mượt mà, không có thanh địa chỉ web, không cần gõ link hay quét mã lại những lần sau!
        """)

# ========================================================
# 4. HEADER CHÍNH: TIÊU ĐỀ KÊNH BÁN TRÚ
# ========================================================
col_h1, col_h2 = st.columns([3, 1])
with col_h1:
    col_lg, col_tt = st.columns([1, 6])
    with col_lg:
        if os.path.exists(FILE_LOGO):
            st.image(FILE_LOGO, width=80)
    with col_tt:
        st.markdown("<h2 style='margin:0; padding:0; color:#1E3A8A;'>🏫 QUẢN LÝ BÁN TRÚ - THPT SỐ 2 BẢO YÊN</h2>", unsafe_allow_html=True)
        st.markdown(f"**Năm học: {st.session_state.nam_hoc_hien_tai}** | Vai trò: `<span class='{badge_color}'>{role_curr}</span>`", unsafe_allow_html=True)

with col_h2:
    link_hien = duong_dan_online if duong_dan_online else duong_dan_app_mobile
    st.success(f"📱 **Link App 24/7:**\n`{link_hien}`")

# ========================================================
# BỘ LỌC ĐIỀU HÀNH 4 TIÊU CHÍ (NGAY DƯỚI TÊN KÊNH)
# ========================================================
with st.container():
    st.markdown("<div style='background:#F8FAFC; border:1px solid #E2E8F0; border-radius:10px; padding:12px 16px; margin:10px 0;'>", unsafe_allow_html=True)
    col_f1, col_f2, col_f3, col_f4 = st.columns([1.1, 1.4, 1.3, 1.8])
    with col_f1:
        ngay_lam_viec = st.date_input("📅 Ngày làm việc:", date.today(), key="main_ngay_lv")
    with col_f2:
        so_hs_nam = len(df_current[df_current["Dãy nhà"] == "Dãy Nam"])
        so_hs_nu = len(df_current[df_current["Dãy nhà"] == "Dãy Nữ"])
        ds_day = ["Tất cả (Khu Nam & Nữ)", f"Dãy Nam (9 phòng - {so_hs_nam} HS)", f"Dãy Nữ (10 phòng - {so_hs_nu} HS)"]
        chon_day = st.selectbox("🏢 Khu vực phòng:", ds_day, key="main_chon_day")
    with col_f3:
        if "Dãy Nam" in chon_day:
            df_filter_room = df_current[df_current["Dãy nhà"] == "Dãy Nam"]
        elif "Dãy Nữ" in chon_day:
            df_filter_room = df_current[df_current["Dãy nhà"] == "Dãy Nữ"]
        else:
            df_filter_room = df_current
        ds_phong = ["Tất cả các phòng"] + sorted(list(df_filter_room["Phòng"].dropna().unique()))
        chon_phong = st.selectbox("🚪 Chọn Phòng:", ds_phong, key="main_chon_phong")
    with col_f4:
        tu_khoa = st.text_input("🔍 Tìm nhanh học sinh:", "", placeholder="Tên HS, SĐT, Bố/Mẹ...", key="main_tu_khoa")
    st.markdown("</div>", unsafe_allow_html=True)

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
        df_hien_thi["Chức vụ phòng"].astype(str).str.contains(tu_khoa, case=False, na=False) |
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


def tao_excel_phieu_bao_com(df_all, ngay_lv):
    """Tạo file Excel Phiếu Báo Cơm chuẩn cho Bếp ăn và Ban Giám Hiệu"""
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        # Sheet 1: Bảng tổng hợp theo 19 phòng
        ds_phong_all = sorted(list(df_all["Phòng"].dropna().unique()))
        rows_th = []
        for p in ds_phong_all:
            df_p = df_all[df_all["Phòng"] == p]
            day_p = df_p["Dãy nhà"].iloc[0] if "Dãy nhà" in df_p.columns and len(df_p) > 0 else ""
            si_so = len(df_p)
            trua = int(df_p["GĐ1: Ăn trưa"].sum()) if "GĐ1: Ăn trưa" in df_p.columns else 0
            toi = int(df_p["Ăn tối"].sum()) if "Ăn tối" in df_p.columns else trua
            cat_trua = max(0, si_so - trua)
            cat_toi = max(0, si_so - toi)
            rows_th.append({
                "Phòng KTX": p,
                "Khu Vực": day_p,
                "Sĩ Số Phòng": si_so,
                "Suất Ăn Trưa": trua,
                "Cắt Cơm Trưa": cat_trua,
                "Suất Ăn Tối": toi,
                "Cắt Cơm Tối": cat_toi,
                "Ghi Chú": "Đủ 100%" if cat_trua == 0 and cat_toi == 0 else f"Vắng trưa:{cat_trua}, tối:{cat_toi}"
            })
        df_th = pd.DataFrame(rows_th)
        df_th.to_excel(writer, sheet_name="Tong_Hop_19_Phong", index=False)
        
        # Sheet 2: Danh sách học sinh vắng / cắt cơm hôm nay
        mask_v = (df_all["GĐ1: Ăn trưa"] == False) | (df_all["Ăn tối"] == False) | (df_all["Trạng thái"] != "Tại trường")
        df_v = df_all[mask_v][["Phòng", "Giường", "Họ và tên", "Lớp", "GĐ1: Ăn trưa", "Ăn tối", "Trạng thái", "Họ tên Bố", "Họ tên Mẹ", "SĐT Phụ huynh", "Ghi chú nề nếp"]].copy()
        df_v.rename(columns={"GĐ1: Ăn trưa": "Ăn Trưa (Có/Không)", "Ăn tối": "Ăn Tối (Có/Không)"}, inplace=True)
        df_v.to_excel(writer, sheet_name="Danh_Sach_Cat_Com", index=False)
        
        # Sheet 3: Danh sách toàn trường
        cols_tt = [c for c in ["Mã HS", "Phòng", "Giường", "Họ và tên", "Giới tính", "Lớp", "Dãy nhà", "GĐ1: Ăn trưa", "Ăn tối", "GĐ2: Phòng nghỉ", "Trạng thái", "SĐT Phụ huynh"] if c in df_all.columns]
        df_all[cols_tt].to_excel(writer, sheet_name="Chi_Tiet_Toan_Truong", index=False)
        
    return buffer.getvalue()

# --------------------------------------------------------
# VAI TRÒ 1: BAN GIÁM HIỆU (ADMIN TỐI CAO)
# --------------------------------------------------------
if role_curr == "Ban Giám hiệu":
    # 4 Phân hệ nghiệp vụ Bán trú & KTX chuẩn hóa dành cho BGH
    tab_cluster1, tab_cluster2, tab_cluster3, tab_cluster4 = st.tabs([
        f"📋 HỒ SƠ {len(df_current)} HS & ĐIỂM DANH BÁO CƠM",
        "🏢 KÝ TÚC XÁ & THI ĐUA PHÒNG Ở",
        "🍳 BẾP ĂN, DINH DƯỠNG & KIỂM THỰC",
        "💰 TÀI CHÍNH BÁN TRÚ & KẾ TOÁN"
    ])

    # --- CỤM 1: HỒ SƠ & ĐIỂM DANH ---
    with tab_cluster1:
        sub_c1_dd, sub_c1_crud = st.tabs([
            "📋 Điểm Danh 2 Giai Đoạn & Báo Cáo Chuyên Cần",
            "➕ Bổ Sung Hoặc Rút Hồ Sơ Bán Trú"
        ])
        with sub_c1_dd:
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


            # ========================================================
            # TÍNH NĂNG 1: KHỐI DUYỆT ĐƠN XIN VỀ / BÁO CẮT CƠM TỪ PHỤ HUYNH & HỌC SINH
            # ========================================================
            if os.path.exists(FILE_XIN_VE):
                try:
                    df_xv_live = pd.read_csv(FILE_XIN_VE, encoding='utf-8-sig')
                except Exception:
                    df_xv_live = pd.DataFrame()
            else:
                df_xv_live = pd.DataFrame()

            if not df_xv_live.empty and "Trạng thái" in df_xv_live.columns:
                df_cho_duyet = df_xv_live[df_xv_live["Trạng thái"].str.contains("Chờ duyệt|Chờ BGH|Chờ QN", case=False, na=False)]
            else:
                df_cho_duyet = pd.DataFrame()

            if not df_cho_duyet.empty:
                st.markdown(f"""
                <div style="background:#FFFBEB; border:2px solid #F59E0B; border-radius:10px; padding:14px; margin:10px 0 16px 0;">
                    <h4 style="color:#B45309; margin:0 0 8px 0;">🚨 CÓ {len(df_cho_duyet)} ĐƠN XIN NGHỈ / CẮT CƠM TỪ PHỤ HUYNH CẦN DUYỆT:</h4>
                    <p style="font-size:12.5px; color:#4B5563; margin:0;">Thầy/Cô duyệt đơn để hệ thống tự động trừ suất ăn của nhà bếp và cập nhật trạng thái an toàn cho học sinh.</p>
                </div>
                """, unsafe_allow_html=True)
                
                for idx_xv, row_xv in df_cho_duyet.iterrows():
                    c_d1, c_d2, c_d3, c_d4 = st.columns([2.5, 2.5, 1.3, 1.2])
                    with c_d1:
                        st.markdown(f"**🎒 {row_xv.get('Họ và tên', '')}** (Lớp: `{row_xv.get('Lớp', '')}` - {row_xv.get('Phòng', '')})")
                        st.caption(f"⏰ Gửi lúc: {row_xv.get('Thời gian', '')} | Người đón: {row_xv.get('Người đón / SĐT', 'Gia đình đón')}")
                    with c_d2:
                        st.markdown(f"**Lý do:** *{row_xv.get('Lý do', 'Xin về gia đình')}*")
                        st.caption("Hình thức: Cắt cơm & Về nhà an toàn")
                    with c_d3:
                        if st.button("✅ DUYỆT ĐƠN", key=f"btn_dy_{idx_xv}", type="primary", use_container_width=True):
                            # 1. Cập nhật file xin về
                            df_xv_live.loc[idx_xv, "Trạng thái"] = "Đã duyệt (Về nhà)"
                            df_xv_live.loc[idx_xv, "Người duyệt"] = u_curr.get("fullname", "BGH/Quản Nhiệm")
                            df_xv_live.to_csv(FILE_XIN_VE, index=False, encoding='utf-8-sig')
                            
                            # 2. Tự động cắt cơm và chuyển trạng thái học sinh
                            df_up_hs = pd.DataFrame(st.session_state.ds_hoc_sinh_live)
                            ten_hs = row_xv.get('Họ và tên', '')
                            df_up_hs.loc[df_up_hs["Họ và tên"] == ten_hs, "Trạng thái"] = "Xin về nhà"
                            df_up_hs.loc[df_up_hs["Họ và tên"] == ten_hs, "GĐ1: Ăn trưa"] = False
                            df_up_hs.loc[df_up_hs["Họ và tên"] == ten_hs, "Ăn tối"] = False
                            df_up_hs.loc[df_up_hs["Họ và tên"] == ten_hs, "GĐ2: Phòng nghỉ"] = False
                            st.session_state.ds_hoc_sinh_live = df_up_hs.to_dict('records')
                            df_up_hs.to_csv(FILE_DU_LIEU_THUC_TE, index=False, encoding='utf-8-sig')
                            st.success(f"🎉 Đã duyệt cho em **{ten_hs}**! Nhà bếp đã tự động trừ suất ăn.")
                            st.rerun()
                    with c_d4:
                        if st.button("❌ TỪ CHỐI", key=f"btn_tc_{idx_xv}", use_container_width=True):
                            df_xv_live.loc[idx_xv, "Trạng thái"] = "Từ chối duyệt"
                            df_xv_live.loc[idx_xv, "Người duyệt"] = u_curr.get("fullname", "BGH/Quản Nhiệm")
                            df_xv_live.to_csv(FILE_XIN_VE, index=False, encoding='utf-8-sig')
                            st.warning(f"Đã từ chối đơn của em {row_xv.get('Họ và tên', '')}.")
                            st.rerun()
                st.markdown("---")

            # ========================================================
            # TÍNH NĂNG 2 & 3: BỘ CÔNG CỤ 1-CHẠM & PHIẾU BÁO CƠM CHUẨN A4
            # ========================================================
            st.markdown("#### ☀️ **LỆNH BÁO CƠM NHÀ BẾP (08:00 - 08:30) & PHIẾU BÁO CƠM 3 BÊN**")
            st.caption("Khung giờ vàng 08:00 - 08:30: Quản nhiệm bấm nút 1-chạm '🟢 ĐIỂM DANH ĐỦ 100%' hoặc loại trừ học sinh vắng/nghỉ; xuất Phiếu Báo Cơm ký nhận 3 bên (Nhà bếp nhận - Quản nhiệm lập - BGH ký duyệt).")
            col_act1, col_act2, col_act3 = st.columns([1.6, 1.8, 1.6])
            
            with col_act1:
                lbl_all_btn = f"🟢 ĐIỂM DANH ĐỦ 100% ({len(df_hien_thi)} HS)"
                if st.button(lbl_all_btn, type="secondary", use_container_width=True, help="Tự động tích có mặt ăn trưa, ăn tối, nghỉ trưa cho toàn bộ học sinh đang lọc"):
                    df_cap_nhat = pd.DataFrame(st.session_state.ds_hoc_sinh_live)
                    ds_ma_hien_thi = df_hien_thi["Mã HS"].tolist()
                    for ma_hs in ds_ma_hien_thi:
                        df_cap_nhat.loc[df_cap_nhat["Mã HS"] == ma_hs, "GĐ1: Ăn trưa"] = True
                        df_cap_nhat.loc[df_cap_nhat["Mã HS"] == ma_hs, "Ăn tối"] = True
                        df_cap_nhat.loc[df_cap_nhat["Mã HS"] == ma_hs, "GĐ2: Phòng nghỉ"] = True
                        df_cap_nhat.loc[df_cap_nhat["Mã HS"] == ma_hs, "Trạng thái"] = "Tại trường"
                    st.session_state.ds_hoc_sinh_live = df_cap_nhat.to_dict('records')
                    df_cap_nhat.to_csv(FILE_DU_LIEU_THUC_TE, index=False, encoding='utf-8-sig')
                    st.success(f"🎉 Đã điểm danh CÓ MẶT 100% cho {len(ds_ma_hien_thi)} học sinh thành công!")
                    st.rerun()

            with col_act2:
                # Nút xuất file Excel báo cơm trực tiếp
                excel_bytes = tao_excel_phieu_bao_com(df_current, ngay_lam_viec)
                ten_file_excel = f"Phieu_Bao_Com_THPT2_BaoYen_{ngay_lam_viec.strftime('%Y%m%d')}.xlsx"
                st.download_button(
                    label=f"📥 TẢI FILE EXCEL BÁO CƠM BẾP ({ngay_lam_viec.strftime('%d/%m')})",
                    data=excel_bytes,
                    file_name=ten_file_excel,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True,
                    help="Tải file Excel đầy đủ 3 sheet để gửi Zalo cho Nhà bếp hoặc lưu trữ kế toán"
                )

            with col_act3:
                mo_phieu_in = st.checkbox("📄 XEM MẪU IN PHIẾU BÁO CƠM (A4)", value=False, key="ck_mo_phieu_a4")

            # MẪU IN PHIẾU BÁO CƠM CHUẨN A4
            if mo_phieu_in:
                so_suat_trua_tt = int(df_current["GĐ1: Ăn trưa"].sum()) if "GĐ1: Ăn trưa" in df_current.columns else 0
                so_suat_toi_tt = int(df_current["Ăn tối"].sum()) if "Ăn tối" in df_current.columns else so_suat_trua_tt
                so_cat_trua_tt = max(0, len(df_current) - so_suat_trua_tt)
                so_cat_toi_tt = max(0, len(df_current) - so_suat_toi_tt)
                
                st.markdown(f"""
                <div style="background:white; border:2px solid #1E3A8A; border-radius:12px; padding:24px; margin:12px 0; font-family:'Times New Roman', Times, serif; color:#0F172A; box-shadow:0 4px 14px rgba(0,0,0,0.06);">
                    <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:12px;">
                        <div style="text-align:center;">
                            <span style="font-size:12px;">SỞ GIÁO DỤC VÀ ĐÀO TẠO LÀO CAI</span><br>
                            <b style="font-size:13.5px; color:#1E3A8A;">TRƯỜNG THPT SỐ 2 BẢO YÊN</b><br>
                            <span style="font-size:11.5px; text-decoration:underline;">TỔ BÁN TRÚ & CẤP DƯỠNG</span>
                        </div>
                        <div style="text-align:center;">
                            <b style="font-size:12.5px;">CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM</b><br>
                            <span style="font-size:12px; font-weight:bold; text-decoration:underline;">Độc lập - Tự do - Hạnh phúc</span><br>
                            <span style="font-size:11.5px; font-style:italic;">Bảo Yên, ngày {ngay_lam_viec.strftime('%d')} tháng {ngay_lam_viec.strftime('%m')} năm {ngay_lam_viec.strftime('%Y')}</span>
                        </div>
                    </div>
                    
                    <h3 style="text-align:center; color:#1E3A8A; margin:12px 0 4px 0; letter-spacing:0.5px;">PHIẾU BÁO CƠM BÁN TRÚ HÀNG NGÀY</h3>
                    <p style="text-align:center; font-style:italic; font-size:12.5px; margin:0 0 14px 0;">(Kèm theo nhật ký kiểm thực và sổ chốt suất ăn ký túc xá)</p>
                    
                    <table style="width:100%; border-collapse:collapse; margin-bottom:14px; font-size:13px;">
                        <tr style="background:#F1F5F9;">
                            <th style="border:1px solid #CBD5E1; padding:8px; text-align:left;">Chỉ Số Tổng Hợp Quân Số</th>
                            <th style="border:1px solid #CBD5E1; padding:8px; text-align:center; width:130px;">Bữa Trưa</th>
                            <th style="border:1px solid #CBD5E1; padding:8px; text-align:center; width:130px;">Bữa Tối</th>
                            <th style="border:1px solid #CBD5E1; padding:8px; text-align:center; width:130px;">Ghi Chú</th>
                        </tr>
                        <tr>
                            <td style="border:1px solid #CBD5E1; padding:7px;"><b>1. Tổng sĩ số học sinh bán trú:</b></td>
                            <td style="border:1px solid #CBD5E1; padding:7px; text-align:center;"><b>{len(df_current)} HS</b></td>
                            <td style="border:1px solid #CBD5E1; padding:7px; text-align:center;"><b>{len(df_current)} HS</b></td>
                            <td style="border:1px solid #CBD5E1; padding:7px; text-align:center;">19 Phòng KTX</td>
                        </tr>
                        <tr>
                            <td style="border:1px solid #CBD5E1; padding:7px; color:#15803D;"><b>2. Số suất ăn thực tế (Nấu cơm):</b></td>
                            <td style="border:1px solid #CBD5E1; padding:7px; text-align:center; color:#15803D; font-weight:bold; font-size:14px;">{so_suat_trua_tt} suất</td>
                            <td style="border:1px solid #CBD5E1; padding:7px; text-align:center; color:#15803D; font-weight:bold; font-size:14px;">{so_suat_toi_tt} suất</td>
                            <td style="border:1px solid #CBD5E1; padding:7px; text-align:center; color:#15803D;">Bếp xuất kho</td>
                        </tr>
                        <tr>
                            <td style="border:1px solid #CBD5E1; padding:7px; color:#DC2626;"><b>3. Số suất cắt / vắng ăn:</b></td>
                            <td style="border:1px solid #CBD5E1; padding:7px; text-align:center; color:#DC2626; font-weight:bold;">{so_cat_trua_tt} suất</td>
                            <td style="border:1px solid #CBD5E1; padding:7px; text-align:center; color:#DC2626; font-weight:bold;">{so_cat_toi_tt} suất</td>
                            <td style="border:1px solid #CBD5E1; padding:7px; text-align:center; color:#DC2626;">Khấu trừ tiền ăn</td>
                        </tr>
                    </table>

                    <div style="display:flex; justify-content:space-between; margin-top:28px; text-align:center; font-size:13px;">
                        <div style="width:30%;">
                            <b>ĐẠI DIỆN BẾP ĂN</b><br>
                            <span style="font-size:11.5px; font-style:italic;">(Ký và ghi rõ họ tên)</span>
                            <div style="height:55px;"></div>
                            <b>Tổ Cấp Dưỡng</b>
                        </div>
                        <div style="width:30%;">
                            <b>GIÁO VIÊN TRỰC BÁN TRÚ</b><br>
                            <span style="font-size:11.5px; font-style:italic;">(Ký và ghi rõ họ tên)</span>
                            <div style="height:55px;"></div>
                            <b>Thầy Quản Nhiệm</b>
                        </div>
                        <div style="width:30%;">
                            <b>HIỆU TRƯỞNG / BGH</b><br>
                            <span style="font-size:11.5px; font-style:italic;">(Phê duyệt)</span>
                            <div style="height:55px;"></div>
                            <b>Ban Giám Hiệu</b>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            st.subheader("📋 Bảng Điểm Danh 2 Giai Đoạn & 2 Bữa Ăn Thời Gian Thực")
            cot_dd = ["Mã HS", "Phòng", "Giường", "Họ và tên", "Chức vụ phòng", "Lớp", "GĐ1: Ăn trưa", "Ăn tối", "GĐ2: Phòng nghỉ", "Trạng thái", "SĐT Học sinh", "SĐT Phụ huynh", "Ghi chú nề nếp"]
            cot_edit = st.data_editor(
                df_hien_thi[cot_dd],
                column_config={
                    "Chức vụ phòng": st.column_config.TextColumn("Chức vụ", help="Trưởng phòng hoặc Thành viên"),
                    "SĐT Học sinh": st.column_config.TextColumn("SĐT Học Sinh"),
                    "SĐT Phụ huynh": st.column_config.TextColumn("SĐT Phụ Huynh"),
                    "GĐ1: Ăn trưa": st.column_config.CheckboxColumn("🍲 Ăn Trưa [✓]", default=True),
                    "Ăn tối": st.column_config.CheckboxColumn("🍛 Ăn Tối [✓]", default=True),
                    "GĐ2: Phòng nghỉ": st.column_config.CheckboxColumn("🛏️ Phòng Nghỉ [✓]", default=True),
                    "Trạng thái": st.column_config.SelectboxColumn("Trạng thái", options=[
                        "Tại trường", "Đã về nhà an toàn", "GV báo: Ốm tại phòng Y tế", "GV báo: Vắng có phép", "GV báo: Vắng không phép 🚨"
                    ])
                },
                disabled=["Mã HS", "Phòng", "Giường", "Họ và tên", "Chức vụ phòng", "Lớp", "SĐT Học sinh", "SĐT Phụ huynh"],
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


        with sub_c1_crud:
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



    # --- CỤM 2: KÝ TÚC XÁ & THI ĐUA PHÒNG ---
    with tab_cluster2:
        sub_c2_td, sub_c2_sodo = st.tabs([
            "🏆 Đánh Giá & Bảng Vàng Thi Đua Nề Nếp 19 Phòng",
            "🏢 Sơ Đồ & Danh Sách Phòng KTX (Dãy Nam 9P - Dãy Nữ 10P)"
        ])
        with sub_c2_td:
            st.subheader("🏆 Đánh Giá & Bảng Vàng Thi Đua Nề Nếp 19 Phòng Bán Trú")
            if os.path.exists(FILE_THI_DUA):
                df_td_load = pd.read_csv(FILE_THI_DUA, encoding='utf-8-sig')
                st.dataframe(df_td_load, use_container_width=True, hide_index=True)
                top1 = df_td_load.sort_values(by="Tổng điểm", ascending=False).iloc[0]
                st.success(f"🌟 **PHÒNG DẪN ĐẦU TUẦN NÀY:** **{top1['Phòng']} ({top1['Dãy nhà']})** đạt **{top1['Tổng điểm']}/40 điểm** - Xếp loại: {top1['Xếp loại']}")


        with sub_c2_sodo:
            st.subheader("🏢 Sơ Đồ Phân Bổ Học Sinh Bán Trú 19 Phòng Ở")
            c_sd1, c_sd2 = st.columns(2)
            with c_sd1:
                st.markdown(f"#### 👦 **DÃY NAM (9 PHÒNG - {so_hs_nam} HỌC SINH)**")
                df_nam_p = df_current[df_current['Dãy nhà'] == 'Dãy Nam']
                st.dataframe(df_nam_p[['Phòng', 'Giường', 'Họ và tên', 'Lớp', 'Chức vụ phòng', 'Trạng thái']], use_container_width=True, hide_index=True)
            with c_sd2:
                st.markdown(f"#### 👧 **DÃY NỮ (10 PHÒNG - {so_hs_nu} HỌC SINH)**")
                df_nu_p = df_current[df_current['Dãy nhà'] == 'Dãy Nữ']
                st.dataframe(df_nu_p[['Phòng', 'Giường', 'Họ và tên', 'Lớp', 'Chức vụ phòng', 'Trạng thái']], use_container_width=True, hide_index=True)

    # --- CỤM 3: BẾP ĂN & KIỂM THỰC ---
    with tab_cluster3:
        sub_c3_kt, sub_c3_td = st.tabs([
            "🍳 Báo Cáo Bếp Ăn & Kiểm Thực Ba Bước ATTP",
            "🥗 Phê Duyệt Thực Đơn Tuần Chuẩn Dinh Dưỡng"
        ])
        with sub_c3_kt:
            st.subheader("🍳 Báo Cáo Bếp Ăn & Kiểm Thực Ba Bước")
            tong_an = int(df_current["GĐ1: Ăn trưa"].sum())
            st.info(f"Tổng suất ăn nấu hôm nay: **{tong_an} suất** (Khu Nam: {int(df_current[df_current['Dãy nhà']=='Dãy Nam']['GĐ1: Ăn trưa'].sum())} | Khu Nữ: {int(df_current[df_current['Dãy nhà']=='Dãy Nữ']['GĐ1: Ăn trưa'].sum())})")
            if os.path.exists(FILE_KIEM_THUC):
                df_kt_load = pd.read_csv(FILE_KIEM_THUC, encoding='utf-8-sig')
                st.dataframe(df_kt_load, use_container_width=True, hide_index=True)


        with sub_c3_td:
            st.subheader("🥗 Phê Duyệt Thực Đơn Tuần Chuẩn Dinh Dưỡng THPT")
            if os.path.exists(FILE_THUC_DON):
                df_td_view = pd.read_csv(FILE_THUC_DON, encoding='utf-8-sig')
                st.dataframe(df_td_view, use_container_width=True, hide_index=True)
                if st.button("✅ BAN GIÁM HIỆU PHÊ DUYỆT THỰC ĐƠN NÀY", type="primary"):
                    st.success("🎉 Đã phê duyệt thực đơn tuần! Thực đơn đã công khai trên App của phụ huynh và học sinh.")



    # --- CỤM 4: TÀI CHÍNH BÁN TRÚ & KẾ TOÁN ---
    with tab_cluster4:
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

        st.markdown("---")
        st.markdown("""
            <div style="background:#F0F9FF; border:1px solid #BAE6FD; border-radius:12px; padding:15px; margin-top:10px;">
                <h5 style="color:#0369A1; margin:0 0 6px 0;">🏛️ THÔNG BÁO QUY HOẠCH HỆ THỐNG ĐỒNG BỘ TOÀN TRƯỜNG:</h5>
                <ul style="color:#0C4A6E; font-size:13px; margin:0; padding-left:18px;">
                    <li><b>📱 Hướng dẫn tải & cài đặt App di động (PWA):</b> Đã được chuyển về <b>🏛️ TRUNG TÂM ĐIỀU HÀNH TỔNG THỂ NHÀ TRƯỜNG (Tab 1)</b> để toàn bộ Thầy Cô, PHHS và Học sinh toàn trường cùng sử dụng chung một chuẩn ứng dụng.</li>
                    <li><b>☁️ Đồng bộ đám mây Google Drive & Google Sheets:</b> Đã được tích hợp trọn vẹn tại <b>👑 QUẢN TRỊ TÀI KHOẢN, NIÊN KHÓA & ĐÁM MÂY (Tab 6)</b> với đầy đủ 5 bảng biểu toàn diện (829 HS, 549 Xe, 42 CBGV, 207 Bán trú, 21 Chi đoàn).</li>
                </ul>
            </div>
        """, unsafe_allow_html=True)
        
        c_nav1, c_nav2 = st.columns(2)
        with c_nav1:
            if st.button("👉 Xem Hướng Dẫn Cài Đặt App Tại Trung Tâm Điều Hành", key="btn_goto_app_guide", use_container_width=True):
                st.session_state.phan_he_hien_tai = "🏛️ HỆ THỐNG QUẢN TRỊ & ĐIỀU HÀNH NHÀ TRƯỜNG"
                st.rerun()
        with c_nav2:
            if st.button("👉 Mở Trung Tâm Đồng Bộ Đám Mây Google Sheets (Kênh 1)", key="btn_goto_gsheets_k1", use_container_width=True):
                st.session_state.phan_he_hien_tai = "🏛️ HỆ THỐNG QUẢN TRỊ & ĐIỀU HÀNH NHÀ TRƯỜNG"
                st.rerun()



# --------------------------------------------------------
# VAI TRÒ 2: GIÁO VIÊN QUẢN LÝ (QUẢN NHIỆM BÁN TRÚ)
# --------------------------------------------------------
elif role_curr == "Giáo viên quản lý":
    ma_lk_curr = u_curr.get("ma_lien_ket", "")
    chuc_danh_curr = u_curr.get("chuc_danh", "")
    classes_list = sorted(df_current["Lớp"].unique().tolist()) if "Lớp" in df_current.columns else []
    is_gvcn = (ma_lk_curr in classes_list) or ("chủ nhiệm" in str(chuc_danh_curr).lower())
    
    if is_gvcn:
        lop_gvcn = ma_lk_curr if ma_lk_curr in classes_list else classes_list[0]
        df_lop = df_current[df_current["Lớp"] == lop_gvcn]
        
        st.subheader(f"👨‍🏫 BẢNG ĐIỀU HÀNH BÁN TRÚ - GIÁO VIÊN CHỦ NHIỆM LỚP {lop_gvcn}")
        st.caption(f"Chào mừng Thầy/Cô **{u_curr['fullname']}**! Hệ thống hiển thị riêng dữ liệu {len(df_lop)} học sinh bán trú của lớp {lop_gvcn}.")
        
        c_lop1, c_lop2, c_lop3, c_lop4 = st.columns(4)
        c_lop1.metric("👥 Sĩ Số Bán Trú Lớp", f"{len(df_lop)} HS")
        c_lop2.metric("🟢 Tại Trường (Live)", f"{len(df_lop[df_lop['Trạng thái'] == 'Tại trường'])} HS")
        c_lop3.metric("🍲 Ăn Trưa", f"{int(df_lop['GĐ1: Ăn trưa'].sum())} suất")
        c_lop4.metric("🍛 Ăn Tối", f"{int(df_lop['Ăn tối'].sum())} suất")
        
        tab_lop_dd, tab_lop_ph, tab_lop_td, tab_lop_all, tab_cai_dat = st.tabs([
            f"📋 ĐIỂM DANH & BÁO VẮNG LỚP {lop_gvcn}",
            f"📞 DANH BẠ PHỤ HUYNH LỚP {lop_gvcn}",
            f"🏆 THI ĐUA PHÒNG CỦA LỚP {lop_gvcn}",
            "🌐 XEM DỮ LIỆU TOÀN TRƯỜNG",
            "📱 CÀI ĐẶT APP DI ĐỘNG"
        ])
        
        with tab_lop_dd:
            st.markdown(f"#### 📋 Điểm Danh Hai Bữa & Trạng Thái Học Sinh Lớp {lop_gvcn}")
            cot_dd_lop = ["Mã HS", "Phòng", "Giường", "Họ và tên", "GĐ1: Ăn trưa", "Ăn tối", "GĐ2: Phòng nghỉ", "Trạng thái", "Ghi chú nề nếp"]
            cot_edit_lop = st.data_editor(
                df_lop[cot_dd_lop],
                column_config={
                    "GĐ1: Ăn trưa": st.column_config.CheckboxColumn("🍲 Ăn Trưa [✓]", default=True),
                    "Ăn tối": st.column_config.CheckboxColumn("🍛 Ăn Tối [✓]", default=True),
                    "GĐ2: Phòng nghỉ": st.column_config.CheckboxColumn("🛏️ Phòng Nghỉ [✓]", default=True),
                    "Trạng thái": st.column_config.SelectboxColumn("Trạng thái", options=[
                        "Tại trường", "Đã về nhà an toàn", "GV báo: Ốm tại phòng Y tế", "GV báo: Vắng có phép", "GV báo: Vắng không phép 🚨"
                    ])
                },
                disabled=["Mã HS", "Phòng", "Giường", "Họ và tên"],
                hide_index=True,
                use_container_width=True,
                key="edit_dd_gvcn"
            )
            if st.button("💾 LƯU ĐIỂM DANH CHO HỌC SINH LỚP NÀY", type="primary", key="btn_save_gvcn"):
                df_cap_nhat = pd.DataFrame(st.session_state.ds_hoc_sinh_live)
                for idx, row in cot_edit_lop.iterrows():
                    ma = row["Mã HS"]
                    df_cap_nhat.loc[df_cap_nhat["Mã HS"] == ma, "GĐ1: Ăn trưa"] = row["GĐ1: Ăn trưa"]
                    df_cap_nhat.loc[df_cap_nhat["Mã HS"] == ma, "Ăn tối"] = row["Ăn tối"]
                    df_cap_nhat.loc[df_cap_nhat["Mã HS"] == ma, "GĐ2: Phòng nghỉ"] = row["GĐ2: Phòng nghỉ"]
                    df_cap_nhat.loc[df_cap_nhat["Mã HS"] == ma, "Trạng thái"] = row["Trạng thái"]
                    df_cap_nhat.loc[df_cap_nhat["Mã HS"] == ma, "Ghi chú nề nếp"] = row["Ghi chú nề nếp"]
                st.session_state.ds_hoc_sinh_live = df_cap_nhat.to_dict('records')
                df_cap_nhat.to_csv(FILE_DU_LIEU_THUC_TE, index=False, encoding='utf-8-sig')
                st.success(f"✅ Đã lưu điểm danh học sinh lớp {lop_gvcn} thành công!")
                st.rerun()

        with tab_lop_ph:
            st.markdown(f"#### 📞 Danh Bạ Bố Mẹ Học Sinh Bán Trú Lớp {lop_gvcn}")
            st.dataframe(df_lop[["Mã HS", "Họ và tên", "Phòng", "Giường", "Họ tên Bố", "Họ tên Mẹ", "SĐT Phụ huynh", "Dân tộc", "Thôn", "Xã"]], use_container_width=True, hide_index=True)
            
        with tab_lop_td:
            st.markdown(f"#### 🏆 Điểm Thi Đua Các Phòng Ký Túc Xá Có Học Sinh Lớp {lop_gvcn}")
            phong_lop = df_lop["Phòng"].unique().tolist()
            if os.path.exists(FILE_THI_DUA):
                df_td_all = pd.read_csv(FILE_THI_DUA, encoding='utf-8-sig')
                df_td_lop = df_td_all[df_td_all["Phòng"].isin(phong_lop)]
                if not df_td_lop.empty:
                    st.dataframe(df_td_lop, use_container_width=True, hide_index=True)
                else:
                    st.info(f"Các phòng {', '.join(phong_lop)} chưa có lượt chấm nề nếp hôm nay.")
            else:
                st.info("Chưa có dữ liệu thi đua.")
                
        with tab_lop_all:
            st.markdown("#### 🌐 Xem Danh Sách Bán Trú Toàn Trường (19 Phòng)")
            st.dataframe(df_current[["Mã HS", "Họ và tên", "Lớp", "Phòng", "Giường", "Trạng thái", "GĐ1: Ăn trưa", "Ăn tối"]], use_container_width=True, hide_index=True)
            
        with tab_cai_dat:
            hien_thi_tab_cai_dat_app(duong_dan_online, duong_dan_app_mobile)
            
    else:
        # Giao diện Tổ trực quản nhiệm KTX (19 phòng)
        tab_dd, tab_thi_dua, tab_xin_ve, tab_tra_cuu, tab_cai_dat = st.tabs([
            "📋 ĐIỂM DANH 2 GIAI ĐOẠN",
            "🏆 CHẤM THI ĐUA NỀ NẾP 19 PHÒNG",
            "🚗 QUẢN LÝ XIN VỀ / XUỐNG TRƯỜNG",
            "🔎 TRA CỨU HỒ SƠ & GỌI BỐ MẸ",
            "📱 CÀI ĐẶT APP DI ĐỘNG"
        ])
    
        with tab_dd:
            st.subheader(f"📋 Bảng Điểm Danh Hai Bữa & Nề Nếp Phòng - {chon_phong}")
            cot_dd = ["Mã HS", "Phòng", "Giường", "Họ và tên", "Chức vụ phòng", "Lớp", "GĐ1: Ăn trưa", "Ăn tối", "GĐ2: Phòng nghỉ", "Trạng thái", "SĐT Học sinh", "SĐT Phụ huynh", "Ghi chú nề nếp"]
            cot_edit = st.data_editor(
                df_hien_thi[cot_dd],
                column_config={
                    "Chức vụ phòng": st.column_config.TextColumn("Chức vụ"),
                    "SĐT Học sinh": st.column_config.TextColumn("SĐT Học Sinh"),
                    "SĐT Phụ huynh": st.column_config.TextColumn("SĐT Phụ Huynh"),
                    "GĐ1: Ăn trưa": st.column_config.CheckboxColumn("🍲 Ăn Trưa [✓]", default=True),
                    "Ăn tối": st.column_config.CheckboxColumn("🍛 Ăn Tối [✓]", default=True),
                    "GĐ2: Phòng nghỉ": st.column_config.CheckboxColumn("🛏️ Phòng Nghỉ [✓]", default=True),
                    "Trạng thái": st.column_config.SelectboxColumn("Trạng thái", options=[
                        "Tại trường", "Đã về nhà an toàn", "GV báo: Ốm tại phòng Y tế", "GV báo: Vắng có phép", "GV báo: Vắng không phép 🚨"
                    ])
                },
                disabled=["Mã HS", "Phòng", "Giường", "Họ và tên", "Chức vụ phòng", "Lớp", "SĐT Học sinh", "SĐT Phụ huynh"],
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
            hien_thi_tab_cai_dat_app(duong_dan_online, duong_dan_app_mobile)

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
        
        so_nam_live = len(df_current[df_current["Dãy nhà"] == "Dãy Nam"])
        so_nu_live = len(df_current[df_current["Dãy nhà"] == "Dãy Nữ"])
        tong_hs_live = len(df_current)
        cat_trua_live = max(0, tong_hs_live - tong_trua)
        cat_toi_live = max(0, tong_hs_live - tong_toi)
        
        c_bep1, c_bep2 = st.columns(2)
        with c_bep1:
            st.markdown(f"""
            <div style="background:#EFF6FF; border-left:5px solid #2563EB; padding:15px; border-radius:10px;">
                <h4 style="margin-top:0; color:#1E40AF;">🍲 1. SUẤT CƠM BỮA TRƯA: {tong_trua} SUẤT</h4>
                <p>• <b>Khu Nam (9 phòng):</b> <b>{nam_trua} suất</b> (Sĩ số {so_nam_live})</p>
                <p>• <b>Khu Nữ (10 phòng):</b> <b>{nu_trua} suất</b> (Sĩ số {so_nu_live})</p>
                <p>• <b>Số suất cắt / vắng trưa:</b> <span style="color:#DC2626; font-weight:bold;">{cat_trua_live} suất</span></p>
                <p style="font-size:12px; color:#4B5563;">Chốt quân số trước 08:00 sáng hàng ngày.</p>
            </div>
            """, unsafe_allow_html=True)
            
        with c_bep2:
            st.markdown(f"""
            <div style="background:#FEF3C7; border-left:5px solid #D97706; padding:15px; border-radius:10px;">
                <h4 style="margin-top:0; color:#B45309;">🍛 2. SUẤT CƠM BỮA TỐI: {tong_toi} SUẤT</h4>
                <p>• <b>Khu Nam (9 phòng):</b> <b>{nam_toi} suất</b> (Sĩ số {so_nam_live})</p>
                <p>• <b>Khu Nữ (10 phòng):</b> <b>{nu_toi} suất</b> (Sĩ số {so_nu_live})</p>
                <p>• <b>Số suất cắt / vắng tối:</b> <span style="color:#DC2626; font-weight:bold;">{cat_toi_live} suất</span></p>
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
        st.markdown(f"**Tổng tiền dự thu toàn trường ({len(df_ds)} học sinh):** `{df_ds['Tiền phải nộp (VNĐ)'].sum():,.0f} VNĐ`")

# --------------------------------------------------------
# --------------------------------------------------------
# VAI TRÒ 5: PHỤ HUYNH HỌC SINH (CHỈ XEM & SỬA THÔNG TIN CON EM MÌNH)
# --------------------------------------------------------
elif role_curr == "Phụ huynh học sinh":
    import phan_he_hoc_sinh_phu_huynh
    import importlib
    importlib.reload(phan_he_hoc_sinh_phu_huynh)
    phan_he_hoc_sinh_phu_huynh.render_cong_phu_huynh(
        u_curr, df_current, ngay_lam_viec, BASE_DIR, 
        FILE_DU_LIEU_THUC_TE, FILE_THI_DUA, FILE_KIEM_THUC, 
        FILE_THUC_DON, FILE_XIN_VE, FILE_TAI_KHOAN
    )

# --------------------------------------------------------
# VAI TRÒ 6: HỌC SINH BÁN TRÚ, TRƯỞNG PHÒNG & BAN CÁN SỰ (LỚP TRƯỞNG, BÍ THƯ)
# --------------------------------------------------------
elif role_curr == "Học sinh":
    import phan_he_hoc_sinh_phu_huynh
    import importlib
    importlib.reload(phan_he_hoc_sinh_phu_huynh)
    phan_he_hoc_sinh_phu_huynh.render_cong_hoc_sinh(
        u_curr, df_current, ngay_lam_viec, BASE_DIR, 
        FILE_DU_LIEU_THUC_TE, FILE_THI_DUA, FILE_KIEM_THUC, 
        FILE_THUC_DON, FILE_XIN_VE, FILE_TAI_KHOAN, 
        THU_MUC_NAM_HOC, st.session_state.nam_hoc_hien_tai
    )

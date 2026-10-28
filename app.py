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
from phan_he_doan_thanh_nien import render_phan_he_doan_thanh_nien

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
    accounts = []
    
    # 1. BGH & Cán bộ nhân viên quản lý
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
        accounts.append({
            'Tên đăng nhập': u,
            'Mật khẩu': p,
            'Họ và tên': fn,
            'Vai trò': r,
            'Chức danh': title,
            'Mã liên kết': ref,
            'Số điện thoại': phone,
            'Ghi chú': f"{title} - {fn}",
            'Trạng thái': 'Hoạt động'
        })

    # 2. GVCN 20 lớp
    classes = sorted(df_hs['Lớp'].unique().tolist()) if 'Lớp' in df_hs.columns else []
    for c in classes:
        so_hs_lop = len(df_hs[df_hs['Lớp'] == c])
        accounts.append({
            'Tên đăng nhập': f"gvcn_{c.lower()}",
            'Mật khẩu': 'gvcn123',
            'Họ và tên': f"Thầy/Cô Chủ Nhiệm {c}",
            'Vai trò': 'Giáo viên quản lý',
            'Chức danh': f"Giáo viên chủ nhiệm lớp {c}",
            'Mã liên kết': c,
            'Số điện thoại': '',
            'Ghi chú': f"GVCN Lớp {c} ({so_hs_lop} học sinh bán trú)",
            'Trạng thái': 'Hoạt động'
        })

    # 3. 207 Học sinh bán trú
    for idx, row in df_hs.iterrows():
        ma_hs = str(row['Mã HS']).strip()
        u_hs = ma_hs.lower().replace('-', '')
        phone_hs = str(row.get('SĐT Học sinh', '')).replace('.0', '').strip()
        if phone_hs and not phone_hs.startswith('0') and len(phone_hs) == 9:
            phone_hs = '0' + phone_hs
        accounts.append({
            'Tên đăng nhập': u_hs,
            'Mật khẩu': 'hs123',
            'Họ và tên': row['Họ và tên'],
            'Vai trò': 'Học sinh',
            'Chức danh': 'Học sinh bán trú',
            'Mã liên kết': ma_hs,
            'Số điện thoại': phone_hs,
            'Ghi chú': f"Lớp {row.get('Lớp', '')} - Phòng {row.get('Phòng', '')} - Giường {row.get('Giường', '')}",
            'Trạng thái': 'Hoạt động'
        })

    # 4. 207 Phụ huynh học sinh
    for idx, row in df_hs.iterrows():
        ma_hs = str(row['Mã HS']).strip()
        u_ph = 'ph_' + ma_hs.lower().replace('-', '')
        phone_ph = str(row.get('SĐT Phụ huynh', '')).replace('.0', '').strip()
        if phone_ph and not phone_ph.startswith('0') and len(phone_ph) == 9:
            phone_ph = '0' + phone_ph
            
        ten_ph = f"PH em {row['Họ và tên']}"
        bo = str(row.get('Họ tên Bố', '')).strip()
        me = str(row.get('Họ tên Mẹ', '')).strip()
        ten_bo_me = bo if bo and bo != 'nan' else (me if me and me != 'nan' else ten_ph)
        
        accounts.append({
            'Tên đăng nhập': u_ph,
            'Mật khẩu': 'ph123',
            'Họ và tên': f"{ten_bo_me} (PH {row['Họ và tên']})",
            'Vai trò': 'Phụ huynh học sinh',
            'Chức danh': f"Phụ huynh học sinh {row['Họ và tên']}",
            'Mã liên kết': ma_hs,
            'Số điện thoại': phone_ph,
            'Ghi chú': f"Phụ huynh em {row['Họ và tên']} (Lớp {row.get('Lớp', '')})",
            'Trạng thái': 'Hoạt động'
        })
        
    return pd.DataFrame(accounts)

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

# Địa chỉ chính thức trên đám mây (Cloud 24/7 toàn cầu)
URL_APP_CHINH_THUC = "https://thpt2baoyen.streamlit.app"
duong_dan_online = URL_APP_CHINH_THUC
if os.path.exists(FILE_TUNNEL):
    try:
        with open(FILE_TUNNEL, "r", encoding="utf-8") as f:
            tunnel_doc = f.read().strip()
            if tunnel_doc and tunnel_doc.startswith("http"):
                duong_dan_online = tunnel_doc
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
        
        with st.form("form_dang_nhap_he_thong"):
            st.markdown("#### 🔐 ĐĂNG NHẬP HỆ THỐNG")
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
                    # Hỗ trợ đăng nhập bằng:
                    # 1. Tên đăng nhập
                    # 2. Số điện thoại (bỏ qua dấu chấm hoặc khoảng trắng)
                    # 3. Mã học sinh liên kết (VD: HSN-001)
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
                                st.session_state.user_login = {
                                    "logged_in": True,
                                    "username": row_u["Tên đăng nhập"],
                                    "fullname": row_u["Họ và tên"],
                                    "role": row_u["Vai trò"],
                                    "chuc_danh": row_u.get("Chức danh", row_u["Vai trò"]),
                                    "ma_lien_ket": str(row_u.get("Mã liên kết", "")).strip(),
                                    "phone": str(row_u.get("Số điện thoại", "")).strip()
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
            | **👨‍🏫 Giáo viên Chủ nhiệm (20 Lớp)** | `gvcn_10a1`, `gvcn_10a2`, `gvcn_11a1`... | `gvcn123` |
            | **🍳 Bếp Trưởng & Tổ Cấp Dưỡng** | `beptruong` / `capduong` / `nhabep` | `bep123` |
            | **💰 Kế Toán Bán Trú** | `ketoan` | `kt123` |
            | **🎒 207 Học sinh Bán trú** | Mã HS (VD: `hsn001`, `hsu001`) hoặc SĐT HS | `hs123` |
            | **👨‍👩‍👧 207 Phụ huynh Học sinh** | **Số điện thoại Bố/Mẹ** hoặc `ph_hsn001`... | `ph123` |
            """)

    with col_l2:
        st.markdown(f"""
        <div style="border: 2px solid #16A34A; padding: 18px; border-radius: 14px; background: #F0FDF4; box-shadow: 0 4px 12px rgba(22, 163, 74, 0.12); text-align: center;">
            <div style="background:#16A34A; color:white; display:inline-block; padding:4px 14px; border-radius:20px; font-weight:bold; font-size:12px; margin-bottom:8px;">
                📱 CÀI ĐẶT APP LÊN ĐIỆN THOẠI
            </div>
            <h4 style="color:#15803D; margin:4px 0 8px 0;">DÙNG CAMERA ĐIỆN THOẠI QUÉT MÃ</h4>
            <div style="background:white; padding:10px; border-radius:10px; display:inline-block; border:1px solid #BBF7D0;">
                <img src="https://api.qrserver.com/v1/create-qr-code/?size=280x280&data={duong_dan_online}" width="210" style="display:block; border-radius:6px;">
            </div>
            <p style="margin-top:8px; font-size:13px; font-weight:bold; color:#166534; margin-bottom:4px;">
                Địa chỉ đám mây 24/7 (4G / Wi-Fi toàn cầu):<br>
                <a href="{duong_dan_online}" target="_blank" style="color:#2563EB; font-size:14px; word-break:break-all; text-decoration:underline;">{duong_dan_online}</a>
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
    st.markdown("#### 📅 **NĂM HỌC BÁN TRÚ**")
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
        "🛏️ QUẢN LÝ BÁN TRÚ & KTX",
        "🏛️ QUẢN LÝ CHUNG & NHÀ TRƯỜNG",
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

    with st.expander("⚙️ **Cá Nhân Hóa & Đổi Mật Khẩu:**", expanded=is_default_pw):
        tab_pw, tab_prof = st.tabs(["🔑 Đổi mật khẩu", "👤 SĐT & Họ tên"])
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
            st.caption("📱 Cập nhật số điện thoại cá nhân (để sau này có thể dùng chính SĐT này để đăng nhập):")
            with st.form("form_cap_nhat_thong_tin"):
                sdt_moi = st.text_input("Số điện thoại liên hệ:", value=curr_phone, placeholder="VD: 0912345678")
                ten_moi = st.text_input("Họ và tên hiển thị:", value=curr_fullname)
                btn_save_prof = st.form_submit_button("💾 LƯU THÔNG TIN CÁ NHÂN", use_container_width=True)
                
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

    if st.session_state.phan_he_hien_tai == "🛏️ QUẢN LÝ BÁN TRÚ & KTX":
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
    else:
        df_filter_room = df_current
        chon_phong = "Tất cả các phòng"
        tu_khoa = ""

# ========================================================
# 4. ĐIỀU HƯỚNG THEO PHÂN HỆ HỆ THỐNG
# ========================================================
if st.session_state.phan_he_hien_tai == "🏛️ QUẢN LÝ CHUNG & NHÀ TRƯỜNG":
    render_phan_he_quan_ly_chung(df_tai_khoan, role_curr, st.session_state.nam_hoc_hien_tai, BASE_DIR, THU_MUC_NAM_HOC)
    st.stop()
elif st.session_state.phan_he_hien_tai == "🚩 ĐOÀN THANH NIÊN (ĐTN)":
    render_phan_he_doan_thanh_nien(df_tai_khoan, role_curr, st.session_state.nam_hoc_hien_tai, BASE_DIR, THU_MUC_NAM_HOC)
    st.stop()

# ========================================================
# PHÂN HỆ: QUẢN LÝ BÁN TRÚ & KÝ TÚC XÁ (GIAO DIỆN HIỆN TẠI)
# ========================================================
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

# Hàm hiển thị hướng dẫn cài đặt App điện thoại dùng chung cho các vai trò
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
            - **Tên App trên điện thoại:** `Bán Trú THPT 2`.
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
        st.markdown(f"**Năm học: {st.session_state.nam_hoc_hien_tai}** | Ngày: **{ngay_lam_viec.strftime('%d/%m/%Y')}** | Vai trò: `<span class='{badge_color}'>{role_curr}</span>`", unsafe_allow_html=True)

with col_h2:
    link_hien = duong_dan_online if duong_dan_online else duong_dan_app_mobile
    st.success(f"📱 **Link App 24/7:**\n`{link_hien}`")

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
    tab_admin_tk, tab_nam_hoc, tab_hs_crud, tab_bgh_bc, tab_dd, tab_thi_dua, tab_bep, tab_kt, tab_td, tab_cai_dat = st.tabs([
        "👑 CẤP QUYỀN & TÀI KHOẢN",
        "📅 QUẢN LÝ NĂM HỌC",
        "➕ THÊM / BỚT HỌC SINH",
        "📊 DASHBOARD ĐIỀU HÀNH",
        "📋 ĐIỂM DANH 2 GIAI ĐOẠN",
        "🏆 THI ĐUA 19 PHÒNG",
        "🍳 BẾP ĂN & KIỂM THỰC",
        "💰 KẾ TOÁN & VIETQR",
        "🥗 PHÊ DUYỆT THỰC ĐƠN",
        "📱 CÀI ĐẶT APP DI ĐỘNG"
    ])
    
    # --- PHÂN QUYỀN & CẤP TÀI KHOẢN ĐỒNG LOẠT ---
    with tab_admin_tk:
        st.subheader("👑 Quản Trị, Cấp Quyền & Cấp Tài Khoản Đồng Loạt Toàn Trường")
        st.caption("Ban Giám Hiệu có toàn quyền cấp tài khoản hàng loạt cho BGH, GV Trực, GVCN, Nhà bếp, Học sinh & Phụ huynh, phân quyền theo đúng từng vị trí.")
        
        # Đọc dữ liệu tài khoản mới nhất
        df_tai_khoan = pd.read_csv(FILE_TAI_KHOAN, encoding='utf-8-sig').fillna("")
        
        sub_tk1, sub_tk2, sub_tk3 = st.tabs([
            "⚡ CẤP TÀI KHOẢN ĐỒNG LOẠT",
            "🛠️ CHỈNH SỬA & CẤP MỚI CÁ NHÂN",
            "📋 DANH SÁCH TẤT CẢ TÀI KHOẢN & XUẤT FILE"
        ])
        
        with sub_tk1:
            st.markdown("#### ⚡ **BỘ CÔNG CỤ CẤP TÀI KHOẢN TỰ ĐỘNG ĐỒNG LOẠT CHO TOÀN TRƯỜNG**")
            st.info("💡 Hệ thống tự động quét **danh sách 207 học sinh bán trú thực tế** và **20 lớp học** để sinh đầy đủ tài khoản cá nhân, mật khẩu ban đầu và phân quyền đúng vị trí cho từng người.")
            
            # Thống kê nhanh số lượng tài khoản theo vai trò
            c_tk_m1, c_tk_m2, c_tk_m3, c_tk_m4, c_tk_m5 = st.columns(5)
            cnt_bgh = len(df_tai_khoan[df_tai_khoan["Vai trò"] == "Ban Giám hiệu"])
            cnt_gv = len(df_tai_khoan[df_tai_khoan["Vai trò"] == "Giáo viên quản lý"])
            cnt_bep = len(df_tai_khoan[df_tai_khoan["Vai trò"].str.contains("bếp|toán", case=False, na=False)])
            cnt_hs = len(df_tai_khoan[df_tai_khoan["Vai trò"] == "Học sinh"])
            cnt_ph = len(df_tai_khoan[df_tai_khoan["Vai trò"] == "Phụ huynh học sinh"])
            
            c_tk_m1.metric("👑 BGH & Quản Trị", f"{cnt_bgh} TK", delta="Hiệu trưởng / PHT")
            c_tk_m2.metric("👨‍🏫 GV Quản Lý & GVCN", f"{cnt_gv} TK", delta="20 GVCN + 3 Trực")
            c_tk_m3.metric("🍳 Bếp & Kế Toán", f"{cnt_bep} TK", delta="3 Bếp + 1 Kế toán")
            c_tk_m4.metric("🎒 Học Sinh Bán Trú", f"{cnt_hs} TK", delta=f"{cnt_hs} học sinh")
            c_tk_m5.metric("👨‍👩‍👧 Phụ Huynh Học Sinh", f"{cnt_ph} TK", delta=f"{cnt_ph} phụ huynh")
            
            st.markdown("---")
            c_btn_all1, c_btn_all2 = st.columns([1.5, 1])
            with c_btn_all1:
                st.markdown("##### 🚀 **Cấp Trọn Gói Toàn Trường:**")
                if st.button("⚡ ĐỒNG BỘ & CẤP TOÀN BỘ TÀI KHOẢN TOÀN TRƯỜNG (447 TÀI KHOẢN)", type="primary", use_container_width=True):
                    df_new_all = tao_tai_khoan_dong_loat_full(df_current)
                    df_new_all.to_csv(FILE_TAI_KHOAN, index=False, encoding='utf-8-sig')
                    for dest_dir in ['D:/phan_mem_ban_tru_cloud', 'd:/OneDrive/Hô sơ cá nhan/Học AI']:
                        p = os.path.join(dest_dir, 'tai_khoan_nguoi_dung.csv')
                        if os.path.exists(dest_dir):
                            try:
                                df_new_all.to_csv(p, index=False, encoding='utf-8-sig')
                            except Exception:
                                pass
                    st.success(f"🎉 Đã khởi tạo và đồng bộ thành công toàn bộ {len(df_new_all)} tài khoản cho toàn trường!")
                    st.rerun()
                    
            with c_btn_all2:
                st.markdown("##### 📥 **Xuất Danh Sách Ra Máy:**")
                csv_tk_bytes = df_tai_khoan.to_csv(index=False, encoding='utf-8-sig').encode('utf-8-sig')
                st.download_button(
                    label="💾 TẢI FILE DANH SÁCH TÀI KHOẢN (.CSV / EXCEL)",
                    data=csv_tk_bytes,
                    file_name="Danh_Sach_Tai_Khoan_Dang_Nhap_THPT2_BaoYen.csv",
                    mime="text/csv",
                    use_container_width=True
                )
            
            st.markdown("---")
            st.markdown("##### ⚙️ **Quy Định Mật Khẩu Ban Đầu Cho Từng Khối:**")
            st.markdown("""
            - 👑 **Hiệu Trưởng / BGH:** `admin` (MK: `bgh123`), `hieutruong` (MK: `ht123`), `phohieutruong1` (MK: `pht123`).
            - 👨‍🏫 **Giáo viên Quản nhiệm / Trực KTX:** `quannhiem` (MK: `qn123`), `gvtruc01`, `gvtruc02` (MK: `truc123`).
            - 👨‍🏫 **Giáo viên Chủ nhiệm (20 Lớp):** `gvcn_10a1`, `gvcn_10a2`, `gvcn_11a1`... (MK: `gvcn123`).
            - 🍳 **Nhà Bếp & Kế Toán:** `beptruong`, `capduong` (MK: `bep123`), `ketoan` (MK: `kt123`).
            - 🎒 **207 Học Sinh Bán Trú:** Mã HS (VD: `hsn001`, `hsu001`...) hoặc SĐT (MK: `hs123`).
            - 👨‍👩‍👧 **207 Phụ Huynh Học Sinh:** Số điện thoại của Bố/Mẹ hoặc mã `ph_hsn001` (MK: `ph123`).
            """)
            
        with sub_tk2:
            c_edit_tk, c_add_tk = st.columns([1, 1], gap="medium")
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
                    
                    edit_title = st.text_input("Chức danh hiển thị:", value=str(row_u.get("Chức danh", "")))
                    edit_ref = st.text_input("Mã liên kết (Mã HS hoặc Lớp):", value=str(row_u.get("Mã liên kết", "")))
                    edit_phone = st.text_input("Số điện thoại (dùng để đăng nhập hoặc liên lạc):", value=str(row_u.get("Số điện thoại", "")))
                    edit_pass = st.text_input("Mật khẩu truy cập (sửa để cấp mật khẩu mới):", value=str(row_u["Mật khẩu"]))
                    
                    ds_trang_thai = ["Hoạt động", "Tạm khóa"]
                    tt_idx = 0 if row_u.get("Trạng thái") == "Hoạt động" else (1 if row_u.get("Trạng thái") == "Tạm khóa" else 0)
                    edit_status = st.selectbox("Trạng thái tài khoản:", ds_trang_thai, index=tt_idx)
                    
                    edit_note = st.text_input("Ghi chú / Nhiệm vụ phụ trách:", value=str(row_u.get("Ghi chú", "")))
                    
                    btn_save_edit = st.form_submit_button("💾 LƯU THAY ĐỔI CHO TÀI KHOẢN NÀY", type="primary", use_container_width=True)
                    
                    if btn_save_edit:
                        idx_u = df_tai_khoan[df_tai_khoan["Tên đăng nhập"] == user_duoc_chon].index[0]
                        df_tai_khoan.at[idx_u, "Họ và tên"] = edit_fullname.strip()
                        df_tai_khoan.at[idx_u, "Vai trò"] = edit_role
                        df_tai_khoan.at[idx_u, "Chức danh"] = edit_title.strip()
                        df_tai_khoan.at[idx_u, "Mã liên kết"] = edit_ref.strip()
                        df_tai_khoan.at[idx_u, "Số điện thoại"] = edit_phone.strip()
                        df_tai_khoan.at[idx_u, "Mật khẩu"] = edit_pass.strip()
                        df_tai_khoan.at[idx_u, "Trạng thái"] = edit_status
                        df_tai_khoan.at[idx_u, "Ghi chú"] = edit_note.strip()
                        
                        df_tai_khoan.to_csv(FILE_TAI_KHOAN, index=False, encoding='utf-8-sig')
                        st.success(f"✅ Đã cập nhật thành công tài khoản '{user_duoc_chon}'!")
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
                    new_title = st.text_input("Chức danh:")
                    new_ref = st.text_input("Mã liên kết (Mã HS hoặc Lớp):")
                    new_phone = st.text_input("Số điện thoại:")
                    new_note = st.text_input("Ghi chú nhiệm vụ phụ trách:")
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
                                    "Chức danh": new_title.strip(),
                                    "Mã liên kết": new_ref.strip(),
                                    "Số điện thoại": new_phone.strip(),
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
                ds_user_del = [u for u in df_tai_khoan["Tên đăng nhập"].tolist() if u not in ["admin", "hieutruong"]]
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

        with sub_tk3:
            st.markdown("#### 📋 **DANH SÁCH TOÀN BỘ TÀI KHOẢN TRONG HỆ THỐNG**")
            
            c_flt1, c_flt2 = st.columns([1, 2])
            with c_flt1:
                loc_role = st.selectbox("Lọc theo nhóm vai trò:", ["Tất cả", "Ban Giám hiệu", "Giáo viên quản lý", "Nhà bếp / Cấp dưỡng", "Kế toán bán trú", "Học sinh", "Phụ huynh học sinh"], key="flt_tk_role")
            with c_flt2:
                tim_tk = st.text_input("🔍 Tìm kiếm theo tên đăng nhập, họ tên, lớp hoặc số điện thoại:", "", key="search_tk_input")
                
            df_tk_view = df_tai_khoan.copy()
            if loc_role != "Tất cả":
                df_tk_view = df_tk_view[df_tk_view["Vai trò"] == loc_role]
            if tim_tk.strip():
                kw = tim_tk.strip().lower()
                m_kw = (df_tk_view["Tên đăng nhập"].str.lower().str.contains(kw, na=False) |
                        df_tk_view["Họ và tên"].str.lower().str.contains(kw, na=False) |
                        df_tk_view["Ghi chú"].str.lower().str.contains(kw, na=False))
                if "Số điện thoại" in df_tk_view.columns:
                    m_kw = m_kw | df_tk_view["Số điện thoại"].astype(str).str.contains(kw, na=False)
                df_tk_view = df_tk_view[m_kw]
                
            st.caption(f"Hiển thị: **{len(df_tk_view)}** tài khoản phù hợp.")
            
            cot_hien_tk = ["Tên đăng nhập", "Mật khẩu", "Họ và tên", "Vai trò", "Chức danh", "Mã liên kết", "Số điện thoại", "Trạng thái", "Ghi chú"]
            cot_hien_tk = [c for c in cot_hien_tk if c in df_tk_view.columns]
            
            edited_df_tk = st.data_editor(
                df_tk_view[cot_hien_tk],
                column_config={
                    "Tên đăng nhập": st.column_config.TextColumn("Tên đăng nhập", disabled=True),
                    "Vai trò": st.column_config.SelectboxColumn("Vai trò phân quyền", options=[
                        "Ban Giám hiệu", "Giáo viên quản lý", "Kế toán bán trú", "Nhà bếp / Cấp dưỡng", "Phụ huynh học sinh", "Học sinh"
                    ]),
                    "Trạng thái": st.column_config.SelectboxColumn("Trạng thái", options=["Hoạt động", "Tạm khóa"]),
                    "Mật khẩu": st.column_config.TextColumn("Mật khẩu"),
                    "Họ và tên": st.column_config.TextColumn("Họ và tên"),
                    "Chức danh": st.column_config.TextColumn("Chức danh"),
                    "Số điện thoại": st.column_config.TextColumn("Số điện thoại")
                },
                use_container_width=True,
                hide_index=True,
                key="grid_edit_tk"
            )
            
            if st.button("💾 LƯU CÁC THAY ĐỔI TRÊN BẢNG VÀO FILE HỆ THỐNG", type="primary", use_container_width=True, key="save_grid_tk"):
                # Cập nhật lại vào df_tai_khoan gốc
                for idx, row in edited_df_tk.iterrows():
                    u = row["Tên đăng nhập"]
                    idx_goc = df_tai_khoan[df_tai_khoan["Tên đăng nhập"] == u].index
                    if not idx_goc.empty:
                        for col in edited_df_tk.columns:
                            df_tai_khoan.loc[idx_goc[0], col] = row[col]
                df_tai_khoan.to_csv(FILE_TAI_KHOAN, index=False, encoding='utf-8-sig')
                st.success("🎉 Đã lưu các thay đổi phân quyền vào cơ sở dữ liệu hệ thống thành công!")
                st.rerun()

    # --- QUẢN LÝ NĂM HỌC ---
    with tab_nam_hoc:
        st.subheader("📅 Quản Lý Hoạt Động & Lưu Trữ Dữ Liệu Theo Năm Học")
        st.caption("Ban Giám Hiệu theo dõi, lưu trữ dữ liệu theo từng năm học riêng biệt, khởi tạo năm học mới khi sang khóa mới và tải sao lưu trọn gói.")
        
        col_nh1, col_nh2 = st.columns([1.1, 1], gap="large")
        
        with col_nh1:
            st.markdown("#### 📋 **DANH SÁCH CÁC NĂM HỌC TRONG HỆ THỐNG**")
            
            # Thống kê từng năm học
            ds_thong_ke_nh = []
            for nh in danh_sach_nam_hoc:
                f_hs, _, _, _, _ = lay_duong_dan_file_theo_nam(nh)
                so_hs_nh = 0
                if os.path.exists(f_hs):
                    try:
                        df_nh_tmp = pd.read_csv(f_hs, encoding='utf-8-sig')
                        so_hs_nh = len(df_nh_tmp)
                    except Exception:
                        pass
                
                trang_thai_nh = "⭐ Năm học hiện hành" if nh == nam_hoc_mac_dinh else "📂 Lưu trữ lịch sử"
                dang_chon = "🟢 Đang làm việc" if nh == st.session_state.nam_hoc_hien_tai else "⚪"
                
                ds_thong_ke_nh.append({
                    "Năm học": nh,
                    "Sĩ số": f"{so_hs_nh} HS",
                    "Trạng thái": trang_thai_nh,
                    "Đang chọn": dang_chon
                })
            
            st.dataframe(pd.DataFrame(ds_thong_ke_nh), use_container_width=True, hide_index=True)
            
            st.markdown("---")
            st.markdown("#### ⭐ **THIẾT LẬP NĂM HỌC HIỆN HÀNH (MẶC ĐỊNH TOÀN TRƯỜNG):**")
            st.caption("Năm học này sẽ được tự động mở khi mọi người truy cập vào phần mềm.")
            
            c_set1, c_set2 = st.columns([2, 1])
            with c_set1:
                nh_chon_md = st.selectbox("Chọn năm học làm mặc định:", danh_sach_nam_hoc, index=danh_sach_nam_hoc.index(nam_hoc_mac_dinh) if nam_hoc_mac_dinh in danh_sach_nam_hoc else 0, key="tab_nh_select_md")
            with c_set2:
                st.write("")
                st.write("")
                if st.button("LƯU MẶC ĐỊNH", type="primary", use_container_width=True, key="btn_save_nh_md"):
                    cfg_update = doc_cau_hinh_nam_hoc()
                    cfg_update["nam_hoc_mac_dinh"] = nh_chon_md
                    ghi_cau_hinh_nam_hoc(cfg_update)
                    st.success(f"✅ Đã đặt năm học **{nh_chon_md}** làm mặc định thành công!")
                    st.rerun()

            st.markdown("---")
            st.markdown(f"#### 💾 **SAO LƯU TRỌN GÓI HỒ SƠ NĂM HỌC: {st.session_state.nam_hoc_hien_tai}**")
            st.caption("Tải về một file ZIP chứa toàn bộ 5 file dữ liệu (Học sinh, Điểm danh, Thi đua 19 phòng, Thực đơn, Kiểm thực 3 bước) để lưu trữ theo quy định của Ngành.")
            
            zip_bytes = tao_zip_nam_hoc(st.session_state.nam_hoc_hien_tai)
            ten_file_zip = f"Ho_So_Ban_Tru_{st.session_state.nam_hoc_hien_tai.replace(' ', '')}_THPT2_BaoYen.zip"
            st.download_button(
                label=f"💾 TẢI VỀ TOÀN BỘ DỮ LIỆU NĂM HỌC {st.session_state.nam_hoc_hien_tai} (.ZIP)",
                data=zip_bytes,
                file_name=ten_file_zip,
                mime="application/zip",
                use_container_width=True,
                key="btn_dl_zip_nh"
            )

        with col_nh2:
            st.markdown("#### ➕ **KHỞI TẠO NĂM HỌC MỚI**")
            st.info("💡 Khi bước sang năm học mới (Ví dụ: `2027 - 2028`), Ban Giám Hiệu khởi tạo năm học tại đây. Hệ thống sẽ giữ nguyên dữ liệu các năm cũ và tạo không gian làm việc mới độc lập!")
            
            with st.form("form_tao_nam_hoc_moi"):
                nh_moi_input = st.text_input("📝 Tên năm học mới:", placeholder="Ví dụ: 2027 - 2028")
                
                kieu_khoi_tao = st.radio(
                    "Phương thức khởi tạo dữ liệu học sinh:",
                    [
                        f"Sao chép danh sách học sinh từ năm học {st.session_state.nam_hoc_hien_tai} sang (để chỉnh sửa lên lớp)",
                        "Khởi tạo danh sách trắng (Trống) để nhập/tải lên danh sách học sinh mới"
                    ]
                )
                
                dat_lam_mac_dinh = st.checkbox("Đặt ngay làm năm học hiện hành của toàn trường", value=True)
                
                btn_tao_nh = st.form_submit_button("🚀 BẮT ĐẦU NĂM HỌC MỚI", type="primary", use_container_width=True)
                
                if btn_tao_nh:
                    nh_moi_clean = nh_moi_input.strip()
                    if not nh_moi_clean or len(nh_moi_clean) < 4:
                        st.error("⚠️ Vui lòng nhập đúng định dạng năm học (Ví dụ: 2027 - 2028).")
                    elif nh_moi_clean in danh_sach_nam_hoc:
                        st.error(f"⚠️ Năm học '{nh_moi_clean}' đã tồn tại trong hệ thống rồi!")
                    else:
                        cfg_update = doc_cau_hinh_nam_hoc()
                        if nh_moi_clean not in cfg_update["danh_sach_nam_hoc"]:
                            cfg_update["danh_sach_nam_hoc"].append(nh_moi_clean)
                        if dat_lam_mac_dinh:
                            cfg_update["nam_hoc_mac_dinh"] = nh_moi_clean
                        ghi_cau_hinh_nam_hoc(cfg_update)
                        
                        # Tạo thư mục và file cho năm học mới
                        folder_name = nh_moi_clean.replace(" ", "")
                        dir_nam_moi = os.path.join(THU_MUC_NAM_HOC, folder_name)
                        os.makedirs(dir_nam_moi, exist_ok=True)
                        
                        f_hs_new = os.path.join(dir_nam_moi, "danh_sach_hoc_sinh_thuc_te.csv")
                        f_td_new = os.path.join(dir_nam_moi, "cham_diem_thi_dua_phong.csv")
                        f_kt_new = os.path.join(dir_nam_moi, "nhat_ky_kiem_thuc.csv")
                        f_don_new = os.path.join(dir_nam_moi, "thuc_don_tuan.csv")
                        f_xv_new = os.path.join(dir_nam_moi, "lich_su_xin_ve.csv")
                        
                        if "Sao chép" in kieu_khoi_tao:
                            f_hs_old, f_td_old, f_kt_old, f_don_old, f_xv_old = lay_duong_dan_file_theo_nam(st.session_state.nam_hoc_hien_tai)
                            if os.path.exists(f_hs_old):
                                shutil.copy2(f_hs_old, f_hs_new)
                            if os.path.exists(f_don_old):
                                shutil.copy2(f_don_old, f_don_new)
                        else:
                            df_hs_mau = pd.DataFrame(columns=[
                                "Mã HS", "Phòng", "Giường", "Họ và tên", "Giới tính", "Lớp", "Dãy nhà",
                                "GĐ1: Ăn trưa", "Ăn tối", "GĐ2: Phòng nghỉ", "Trạng thái", "Ghi chú nề nếp",
                                "Họ tên Bố", "Họ tên Mẹ", "SĐT Phụ huynh", "SĐT Học sinh", "Địa chỉ thôn bản", "Xã"
                            ])
                            df_hs_mau.to_csv(f_hs_new, index=False, encoding='utf-8-sig')
                        
                        # Khởi tạo các file rỗng chuẩn cho năm mới
                        pd.DataFrame(columns=["Ngày", "Phòng", "Dãy", "Vệ sinh", "Chăn màn", "Giờ giấc", "Tài sản", "Tổng điểm", "Xếp loại", "Người chấm", "Ghi chú"]).to_csv(f_td_new, index=False, encoding='utf-8-sig')
                        pd.DataFrame(columns=["Ngày", "Bữa ăn", "Món ăn", "Nhà cung cấp", "Hạn dùng", "Cảm quan B1", "Chế biến B2", "Lưu mẫu 24h B3", "Nhiệt độ tủ", "Người kiểm tra", "Kết luận"]).to_csv(f_kt_new, index=False, encoding='utf-8-sig')
                        pd.DataFrame(columns=["Thời gian", "Mã HS", "Họ và tên", "Phòng", "Lớp", "Loại", "Lý do", "Người đón / Phương tiện", "Người phê duyệt", "Ghi chú"]).to_csv(f_xv_new, index=False, encoding='utf-8-sig')
                        
                        # Chuyển sang năm học mới ngay
                        st.session_state.nam_hoc_hien_tai = nh_moi_clean
                        if "ds_hoc_sinh_live" in st.session_state:
                            del st.session_state["ds_hoc_sinh_live"]
                            
                        st.success(f"🎉 Khởi tạo thành công năm học mới **{nh_moi_clean}**! Hệ thống đã tự động chuyển sang năm học này.")
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
        hien_thi_tab_cai_dat_app(duong_dan_online, duong_dan_app_mobile)

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
    
    # Xác định con em của phụ huynh (tự động theo mã liên kết nếu đăng nhập cá nhân)
    ma_lk_curr = u_curr.get("ma_lien_ket", "")
    if ma_lk_curr and ma_lk_curr in df_current["Mã HS"].values:
        row_con = df_current[df_current["Mã HS"] == ma_lk_curr].iloc[0]
        con_em = row_con["Họ và tên"]
        st.success(f"👋 Kính chào Quý Phụ huynh em: **{con_em}** - Lớp **{row_con['Lớp']}** - Phòng **{row_con['Phòng']}** (Giường **{row_con['Giường']}**)")
    else:
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
    
    # Xác định danh tính học sinh (tự động theo mã liên kết nếu đăng nhập cá nhân)
    ma_lk_curr = u_curr.get("ma_lien_ket", "")
    if ma_lk_curr and ma_lk_curr in df_current["Mã HS"].values:
        row_hs_self = df_current[df_current["Mã HS"] == ma_lk_curr].iloc[0]
        hs_ten = row_hs_self["Họ và tên"]
        st.success(f"👋 Chào mừng em: **{hs_ten}** - Lớp **{row_hs_self['Lớp']}** - Phòng **{row_hs_self['Phòng']}** (Giường **{row_hs_self['Giường']}**)")
    else:
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

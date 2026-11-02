# -*- coding: utf-8 -*-
"""
MODULE QUẢN LÝ SĨ SỐ & ĐIỂM DANH CHUYÊN CẦN 21 LỚP THỜI GIAN THỰC
Trường THPT số 2 Bảo Yên - Lào Cai
Phục vụ:
1. Lớp trưởng & Ban cán sự 21 lớp (Báo sĩ số lớp Sáng / Chiều / Cả ngày)
2. Giáo viên chủ nhiệm (GVCN) 21 lớp (Điểm danh chuyên cần lớp mình)
3. Ban Giám Hiệu (Hiệu trưởng, PHT) theo dõi trực tiếp thời gian thực toàn trường
"""

import os
import re
import json
from datetime import datetime, date
import pandas as pd
import streamlit as st

BASE_MODULE_DIR = os.path.dirname(os.path.abspath(__file__))
FILE_SI_SO_CSV = os.path.join(BASE_MODULE_DIR, "bao_cao_si_so_lop_hang_ngay.csv") if os.path.exists(os.path.join(BASE_MODULE_DIR, "bao_cao_si_so_lop_hang_ngay.csv")) else ("D:/bao_cao_si_so_lop_hang_ngay.csv" if os.path.exists("D:/") else os.path.join(BASE_MODULE_DIR, "bao_cao_si_so_lop_hang_ngay.csv"))
FILE_CLOUD_SI_SO = os.path.join("D:/phan_mem_ban_tru_cloud", "bao_cao_si_so_lop_hang_ngay.csv") if os.path.exists("D:/phan_mem_ban_tru_cloud") else FILE_SI_SO_CSV
FILE_TOAN_TRUONG = os.path.join(BASE_MODULE_DIR, "danh_sach_hoc_sinh_toan_truong.csv") if os.path.exists(os.path.join(BASE_MODULE_DIR, "danh_sach_hoc_sinh_toan_truong.csv")) else ("D:/danh_sach_hoc_sinh_toan_truong.csv" if os.path.exists("D:/") else os.path.join(BASE_MODULE_DIR, "danh_sach_hoc_sinh_toan_truong.csv"))

COT_BAO_CAO = [
    "Mã báo cáo",
    "Ngày",
    "Buổi",
    "Lớp",
    "Tổng sĩ số",
    "Có mặt",
    "Vắng",
    "Danh sách vắng",
    "Chi tiết vắng JSON",
    "Người báo cáo",
    "Vai trò",
    "Thời gian cập nhật",
    "Ghi chú"
]

DS_21_LOP = [
    "10A1", "10A2", "10A3", "10A4", "10A5", "10A6", "10A7",
    "11A1", "11A2", "11A3", "11A4", "11A5", "11A6", "11A7",
    "12A1", "12A2", "12A3", "12A4", "12A5", "12A6", "12A7"
]

LY_DO_VANG_DEFAULT = [
    "Nghỉ ốm 🤒",
    "Gia đình có việc (có phép) 📝",
    "Vắng có phép 📄",
    "Vắng không phép ⚠️",
    "Đi viện / Khám bệnh 🏥",
    "Lý do khác..."
]

def lay_du_lieu_si_so(base_dir="D:/"):
    """Đọc dữ liệu báo cáo sĩ số thời gian thực từ CSV"""
    f_path = os.path.join(base_dir, "bao_cao_si_so_lop_hang_ngay.csv") if os.path.exists(os.path.join(base_dir, "bao_cao_si_so_lop_hang_ngay.csv")) else FILE_SI_SO_CSV
    if os.path.exists(f_path):
        try:
            return pd.read_csv(f_path, encoding='utf-8-sig', dtype=str).fillna("")
        except Exception:
            pass
    return pd.DataFrame(columns=COT_BAO_CAO)

def luu_du_lieu_si_so(df_save, base_dir="D:/"):
    """Lưu và đồng bộ dữ liệu báo cáo sĩ số đa nơi"""
    targets = [
        FILE_SI_SO_CSV,
        FILE_CLOUD_SI_SO,
        os.path.join(base_dir, "bao_cao_si_so_lop_hang_ngay.csv")
    ]
    for target in targets:
        try:
            os.makedirs(os.path.dirname(target), exist_ok=True)
            df_save.to_csv(target, index=False, encoding='utf-8-sig')
        except Exception:
            pass

def lay_danh_sach_hoc_sinh_lop(lop_str, base_dir="D:/"):
    """Lấy danh sách học sinh chuẩn theo lớp từ danh_sach_hoc_sinh_toan_truong.csv"""
    f_tt = os.path.join(base_dir, "danh_sach_hoc_sinh_toan_truong.csv") if os.path.exists(os.path.join(base_dir, "danh_sach_hoc_sinh_toan_truong.csv")) else FILE_TOAN_TRUONG
    if os.path.exists(f_tt):
        try:
            df_all = pd.read_csv(f_tt, encoding='utf-8-sig', dtype=str).fillna("")
            df_lop = df_all[df_all["Lớp"].str.strip().str.upper() == lop_str.strip().upper()].copy()
            if not df_lop.empty:
                return df_lop.sort_values(by="STT", key=lambda col: pd.to_numeric(col, errors='coerce')).reset_index(drop=True)
        except Exception:
            pass
    return pd.DataFrame()

def trich_xuat_lop_tu_user(u_curr):
    """Tự động nhận diện lớp của Lớp trưởng hoặc GVCN"""
    if not u_curr or not isinstance(u_curr, dict):
        return None
    
    # 1. Kiểm tra Mã liên kết
    ma_lk = str(u_curr.get("ma_lien_ket", "")).strip().upper()
    if ma_lk in DS_21_LOP:
        return ma_lk
        
    # 2. Kiểm tra Tên đăng nhập
    username = str(u_curr.get("username", "")).strip()
    m_u = re.search(r'1[0-2]A[1-7]', username, re.IGNORECASE)
    if m_u:
        return m_u.group(0).upper()
        
    # 3. Kiểm tra Chức danh
    chuc_danh = str(u_curr.get("chuc_danh", "")).strip()
    m_cd = re.search(r'1[0-2]A[1-7]', chuc_danh, re.IGNORECASE)
    if m_cd:
        return m_cd.group(0).upper()
        
    # 4. Kiểm tra Họ và tên
    fullname = str(u_curr.get("fullname", "")).strip()
    m_fn = re.search(r'1[0-2]A[1-7]', fullname, re.IGNORECASE)
    if m_fn:
        return m_fn.group(0).upper()
        
    return None

def render_giao_dien_bao_si_so(u_curr, role_curr, base_dir="D:/", is_bcs=False, is_gvcn=False, is_admin=False):
    """
    Giao diện Báo sĩ số lớp & Tích học sinh vắng kèm lý do thời gian thực.
    Được tích hợp dùng chung cho Lớp trưởng, GVCN và BGH.
    """
    st.markdown("""
        <div style='background: linear-gradient(135deg, #0D9488, #059669); padding: 12px 18px; border-radius: 10px; color: white; margin-bottom: 14px;'>
            <div style='display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:8px;'>
                <div>
                    <h3 style='margin:0; font-size: 19px; color: white; font-weight:800;'>📊 BÁO SĨ SỐ LỚP & ĐIỂM DANH CHUYÊN CẦN THỜI GIAN THỰC</h3>
                    <p style='margin: 3px 0 0 0; opacity: 0.95; font-size: 13px;'>
                        Cập nhật quân số buổi sáng, buổi chiều hoặc cả ngày • Tích vắng kèm lý do • Đồng bộ trực tiếp về Ban Giám Hiệu
                    </p>
                </div>
                <div style='background:rgba(255,255,255,0.25); padding:4px 12px; border-radius:14px; font-weight:bold; font-size:12px;'>
                    🔴 LIVE REAL-TIME
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # 1. Xác định lớp học và quyền hạn
    lop_mac_dinh = trich_xuat_lop_tu_user(u_curr)
    u_username = str(u_curr.get("username", "")).strip()
    u_fullname = str(u_curr.get("fullname", "Người dùng")).strip()
    quyen_ql = str(u_curr.get("quyen_quan_ly", "")).strip().lower()

    la_bgh_hoac_admin = (role_curr in ["Ban Giám hiệu", "Quản trị viên"]) or (u_username == "admin") or ("toàn quyền" in quyen_ql)

    c_top1, c_top2, c_top3 = st.columns([1.2, 1.2, 1.6])
    
    with c_top1:
        if la_bgh_hoac_admin or (not lop_mac_dinh):
            idx_lop_sel = DS_21_LOP.index(lop_mac_dinh) if lop_mac_dinh in DS_21_LOP else 0
            lop_chon = st.selectbox("🏫 Chọn Lớp học:", DS_21_LOP, index=idx_lop_sel, key="sb_lop_si_so")
        else:
            lop_chon = lop_mac_dinh
            st.markdown(f"🏫 **Lớp phụ trách:**")
            st.markdown(f"<div style='background:#E0F2FE; color:#0369A1; font-size:16px; font-weight:bold; padding:7px 12px; border-radius:6px; border:1px solid #BAE6FD;'>Lớp {lop_chon}</div>", unsafe_allow_html=True)

    with c_top2:
        ngay_chon = st.date_input("📅 Ngày điểm danh:", value=date.today(), key="dt_ngay_si_so")
        ngay_str = ngay_chon.strftime("%d/%m/%Y")

    with c_top3:
        buoi_chon = st.radio(
            "⏰ Chọn buổi học:",
            ["🌅 Buổi sáng", "☀️ Buổi chiều", "📅 Cả ngày"],
            horizontal=True,
            key="rb_buoi_si_so"
        )

    # Chuẩn hóa tên buổi
    if "sáng" in buoi_chon.lower():
        ten_buoi_chuan = "Buổi sáng"
        ma_buoi_code = "SANG"
    elif "chiều" in buoi_chon.lower():
        ten_buoi_chuan = "Buổi chiều"
        ma_buoi_code = "CHIEU"
    else:
        ten_buoi_chuan = "Cả ngày"
        ma_buoi_code = "CANGAY"

    # Lấy danh sách học sinh của lớp
    df_hs_lop = lay_danh_sach_hoc_sinh_lop(lop_chon, base_dir)
    tong_si_so = len(df_hs_lop) if not df_hs_lop.empty else 40

    # Đọc dữ liệu lịch sử báo cáo để kiểm tra xem đã báo chưa
    df_si_so_all = lay_du_lieu_si_so(base_dir)
    ma_bao_cao_key = f"BCSS-{ngay_chon.strftime('%Y%m%d')}-{lop_chon}-{ma_buoi_code}"
    
    da_bao_cao = False
    row_bc_hien_tai = None
    ds_vang_da_luu = []
    chi_tiet_vang_da_luu = {}

    if not df_si_so_all.empty:
        m_bc = (df_si_so_all["Ngày"] == ngay_str) & (df_si_so_all["Lớp"] == lop_chon) & (df_si_so_all["Buổi"] == ten_buoi_chuan)
        if m_bc.any():
            da_bao_cao = True
            row_bc_hien_tai = df_si_so_all[m_bc].iloc[-1]
            try:
                raw_json = row_bc_hien_tai.get("Chi tiết vắng JSON", "{}")
                chi_tiet_vang_da_luu = json.loads(raw_json) if raw_json else {}
                ds_vang_da_luu = list(chi_tiet_vang_da_luu.keys())
            except Exception:
                pass

    # Hiển thị thông báo tình trạng đã báo / chưa báo
    if da_bao_cao:
        co_mat_old = row_bc_hien_tai.get("Có mặt", str(tong_si_so))
        vang_old = row_bc_hien_tai.get("Vắng", "0")
        nguoi_bao_old = row_bc_hien_tai.get("Người báo cáo", "Chưa rõ")
        gio_bao_old = row_bc_hien_tai.get("Thời gian cập nhật", "")
        ds_vang_str_old = row_bc_hien_tai.get("Danh sách vắng", "Không có ai vắng")

        st.markdown(f"""
        <div style="background:#F0FDF4; border:1.5px solid #22C55E; border-radius:8px; padding:12px 16px; margin-bottom:12px;">
            <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap;">
                <span style="font-weight:bold; color:#15803D; font-size:14.5px;">
                    🟢 ĐÃ GHI NHẬN BÁO SĨ SỐ THỜI GIAN THỰC ({ten_buoi_chuan} - {ngay_str})
                </span>
                <span style="font-size:12.5px; color:#4B5563;">
                    🕒 Cập nhật: <b>{gio_bao_old}</b> | Người báo: <b>{nguoi_bao_old}</b>
                </span>
            </div>
            <p style="margin:4px 0 0 0; font-size:13.5px; color:#166534;">
                Quân số: Có mặt <b>{co_mat_old}/{tong_si_so}</b> HS (Vắng: <b>{vang_old}</b> HS) • <i>Chi tiết vắng:</i> {ds_vang_str_old}
            </p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.info(f"⏳ **Chưa ghi nhận báo cáo:** Lớp **{lop_chon}** chưa có dữ liệu báo sĩ số cho **{ten_buoi_chuan} ngày {ngay_str}**. Vui lòng kiểm diện và bấm Lưu bên dưới.")

    st.markdown("---")

    # 2. KHU VỰC TÍCH HỌC SINH VẮNG & CHỌN LÝ DO
    st.markdown("#### ✍️ Kiểm Diện & Tích Học Sinh Vắng:")
    
    # Tạo danh sách options học sinh: "STT. Họ tên [Mã HS]"
    hs_options = []
    hs_dict = {}
    if not df_hs_lop.empty:
        for _, r_h in df_hs_lop.iterrows():
            stt_str = f"{int(r_h['STT']):02d}" if str(r_h.get('STT', '')).isdigit() else str(r_h.get('STT', ''))
            label_hs = f"{stt_str}. {r_h['Họ và tên']} (Mã: {r_h['Mã học sinh']})"
            hs_options.append(label_hs)
            hs_dict[label_hs] = r_h

    # Khởi tạo mặc định học sinh vắng nếu đã có báo cáo trước đó
    default_selected_labels = []
    if da_bao_cao and ds_vang_da_luu:
        for opt in hs_options:
            for v_name in ds_vang_da_luu:
                if v_name.lower() in opt.lower():
                    default_selected_labels.append(opt)

    # Nút thao tác nhanh
    col_btn1, col_btn2 = st.columns([1, 1])
    with col_btn1:
        st.caption("💡 Tích chọn các học sinh vắng trong buổi học (để trống nếu lớp đi đủ 100%):")
    with col_btn2:
        pass

    # Multiselect tích chọn học sinh vắng
    hs_vang_duoc_chon = st.multiselect(
        "🔴 Danh sách học sinh vắng mặt:",
        options=hs_options,
        default=default_selected_labels,
        placeholder="Gõ tên hoặc số thứ tự học sinh để chọn nhanh...",
        key=f"ms_hs_vang_{lop_chon}_{ma_buoi_code}"
    )

    so_vang_hien_tai = len(hs_vang_duoc_chon)
    so_co_mat_hien_tai = tong_si_so - so_vang_hien_tai
    ty_le_co_mat = (so_co_mat_hien_tai / tong_si_so * 100) if tong_si_so > 0 else 100.0

    # 3 THẺ CHỈ SỐ THỜI GIAN THỰC
    st.markdown("<div style='margin-top:10px;'></div>", unsafe_allow_html=True)
    m_col1, m_col2, m_col3 = st.columns(3)
    m_col1.metric("👥 Tổng Sĩ Số Lớp", f"{tong_si_so} HS", delta="Quân số biên chế")
    m_col2.metric("🟢 Có Mặt Thực Tế", f"{so_co_mat_hien_tai} HS", delta=f"{ty_le_co_mat:.1f}% chuyên cần")
    m_col3.metric("🔴 Vắng Mặt", f"{so_vang_hien_tai} HS", delta="Nghỉ học", delta_color="inverse")

    # FORM NHẬP LÝ DO CHO TỪNG HỌC SINH VẮNG
    chi_tiet_ly_do_vang = {}
    if hs_vang_duoc_chon:
        st.markdown("##### 📝 Chi Tiết Lý Do Vắng Của Từng Học Sinh:")
        for idx_v, hs_label in enumerate(hs_vang_duoc_chon):
            r_info = hs_dict.get(hs_label, {})
            ten_hs_vang = r_info.get("Họ và tên", hs_label)
            ma_hs_vang = r_info.get("Mã học sinh", "")
            sdt_bo = r_info.get("SĐT Bố", "")
            sdt_me = r_info.get("SĐT Mẹ", "")
            sdt_lh = sdt_bo if sdt_bo else (sdt_me if sdt_me else "Chưa có")

            prev_data = chi_tiet_vang_da_luu.get(ten_hs_vang, {})
            prev_lydo = prev_data.get("ly_do", LY_DO_VANG_DEFAULT[0])
            prev_note = prev_data.get("ghi_chu", "")

            idx_ld_df = LY_DO_VANG_DEFAULT.index(prev_lydo) if prev_lydo in LY_DO_VANG_DEFAULT else 0

            with st.container():
                c_v1, c_v2, c_v3 = st.columns([1.5, 1.2, 1.3])
                with c_v1:
                    st.markdown(f"**{idx_v + 1}. 🔴 {ten_hs_vang}**")
                    st.caption(f"Mã: {ma_hs_vang} • SĐT PH: 📞 {sdt_lh}")
                with c_v2:
                    ly_do_sel = st.selectbox(
                        "Lý do vắng:",
                        LY_DO_VANG_DEFAULT,
                        index=idx_ld_df,
                        key=f"sb_lydo_{lop_chon}_{ma_buoi_code}_{idx_v}"
                    )
                with c_v3:
                    ghi_chu_ly_do = st.text_input(
                        "Ghi chú chi tiết:",
                        value=prev_note,
                        placeholder="VD: Sốt cao, gia đình có tang, khám ở viện...",
                        key=f"txt_note_{lop_chon}_{ma_buoi_code}_{idx_v}"
                    )

                chi_tiet_ly_do_vang[ten_hs_vang] = {
                    "ma_hs": ma_hs_vang,
                    "ly_do": ly_do_sel,
                    "ghi_chu": ghi_chu_ly_do.strip(),
                    "sdt_ph": sdt_lh
                }
    else:
        st.success("🎉 **LỚP ĐI HỌC ĐỦ 100%:** Hiện tại không có học sinh nào vắng mặt!")

    # Ghi chú chung
    ghi_chu_buoi_hoc = st.text_input(
        "📝 Ghi chú chung buổi học (nếu có):",
        value=row_bc_hien_tai.get("Ghi chú", "") if da_bao_cao and row_bc_hien_tai is not None else "",
        placeholder="VD: 02 học sinh đi muộn 15 phút tiết 1, nề nếp lớp ổn định...",
        key=f"txt_ghichu_chung_{lop_chon}_{ma_buoi_code}"
    )

    st.markdown("---")

    # NÚT BÁO SĨ SỐ THỜI GIAN THỰC
    c_sub1, c_sub2 = st.columns([1.5, 1])
    with c_sub1:
        btn_xac_nhan = st.button(
            "💾 XÁC NHẬN BÁO SĨ SỐ THỜI GIAN THỰC",
            type="primary",
            use_container_width=True,
            key=f"btn_save_si_so_{lop_chon}_{ma_buoi_code}"
        )
    with c_sub2:
        if da_bao_cao:
            st.caption(f"✅ Đã có dữ liệu. Bấm nút để **Cập nhật lại** theo thời gian thực.")
        else:
            st.caption(f"⚡ Dữ liệu sẽ lập tức được gửi trực tiếp lên **Trung tâm điều hành Ban Giám Hiệu**.")

    if btn_xac_nhan:
        # Xây dựng danh sách vắng dạng văn bản
        ds_vang_items = []
        for h_ten, v_info in chi_tiet_ly_do_vang.items():
            ld_clean = v_info["ly_do"].split(" ")[0] if " " in v_info["ly_do"] else v_info["ly_do"]
            if v_info["ghi_chu"]:
                ds_vang_items.append(f"{h_ten} ({v_info['ly_do']} - {v_info['ghi_chu']})")
            else:
                ds_vang_items.append(f"{h_ten} ({v_info['ly_do']})")

        ds_vang_text = "; ".join(ds_vang_items) if ds_vang_items else "Không có học sinh vắng"

        vai_tro_bao = "Lớp trưởng" if is_bcs else ("GVCN" if is_gvcn else (role_curr if role_curr else "Cán bộ trường"))
        nguoi_bao_ghi = f"{u_fullname} ({vai_tro_bao})"

        thoi_gian_live = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

        # Cập nhật hoặc thêm mới vào DataFrame
        m_ton_tai = (df_si_so_all["Ngày"] == ngay_str) & (df_si_so_all["Lớp"] == lop_chon) & (df_si_so_all["Buổi"] == ten_buoi_chuan)
        
        dong_moi = {
            "Mã báo cáo": ma_bao_cao_key,
            "Ngày": ngay_str,
            "Buổi": ten_buoi_chuan,
            "Lớp": lop_chon,
            "Tổng sĩ số": str(tong_si_so),
            "Có mặt": str(so_co_mat_hien_tai),
            "Vắng": str(so_vang_hien_tai),
            "Danh sách vắng": ds_vang_text,
            "Chi tiết vắng JSON": json.dumps(chi_tiet_ly_do_vang, ensure_ascii=False),
            "Người báo cáo": nguoi_bao_ghi,
            "Vai trò": vai_tro_bao,
            "Thời gian cập nhật": thoi_gian_live,
            "Ghi chú": ghi_chu_buoi_hoc.strip()
        }

        if m_ton_tai.any():
            idx_update = df_si_so_all[m_ton_tai].index[0]
            for col_k, val_v in dong_moi.items():
                df_si_so_all.loc[idx_update, col_k] = val_v
        else:
            df_si_so_all = pd.concat([df_si_so_all, pd.DataFrame([dong_moi])], ignore_index=True)

        luu_du_lieu_si_so(df_si_so_all, base_dir)

        # Mẫu tin nhắn Zalo chuẩn sao chép nhanh
        mau_zalo = (
            f"📌 BÁO CÁO SĨ SỐ THỜI GIAN THỰC\n"
            f"Trường THPT số 2 Bảo Yên - Ngày: {ngay_str}\n"
            f"🏫 Lớp: {lop_chon} | {ten_buoi_chuan}\n"
            f"👥 Sĩ số: {so_co_mat_hien_tai}/{tong_si_so} (Vắng: {so_vang_hien_tai})\n"
        )
        if ds_vang_items:
            mau_zalo += "🔴 Danh sách vắng:\n"
            for i_z, item_z in enumerate(ds_vang_items, 1):
                mau_zalo += f"  {i_z}. {item_z}\n"
        else:
            mau_zalo += "🟢 Lớp đi học đủ 100%\n"
        if ghi_chu_buoi_hoc.strip():
            mau_zalo += f"💬 Ghi chú: {ghi_chu_buoi_hoc.strip()}\n"
        mau_zalo += f"✍️ Người báo: {nguoi_bao_ghi} ({thoi_gian_live})"

        st.success(f"🎉 ĐÃ CẬP NHẬT THÀNH CÔNG BÁO CÁO SĨ SỐ LỚP {lop_chon} ({ten_buoi_chuan} - {ngay_str}) LÚC {thoi_gian_live}!")
        st.balloons()

        # Hiển thị mẫu tin sao chép Zalo
        with st.expander("📋 **Mẫu Tin Báo Cáo Nhanh (Sao chép gửi Zalo Nhà trường / BGH)**", expanded=True):
            st.text_area("Nội dung báo cáo chuẩn hóa:", value=mau_zalo, height=140)

        st.rerun()

    # =========================================================================
    # 4. BẢNG TỔNG HỢP SĨ SỐ THỜI GIAN THỰC 21 LỚP HÔM NAY (LIVE DASHBOARD)
    # =========================================================================
    st.markdown("---")
    st.markdown(f"### 📋 Bảng Tổng Hợp Sĩ Số Thời Gian Thực 21 Lớp Toàn Trường ({ten_buoi_chuan} - {ngay_str})")
    render_bang_tong_hop_si_so_21_lop(ngay_str, ten_buoi_chuan, base_dir)


def render_bang_tong_hop_si_so_21_lop(ngay_str, ten_buoi_chuan, base_dir="D:/"):
    """Hiển thị bảng tổng hợp thời gian thực sĩ số 21 lớp trong ngày cho BGH và GVCN theo dõi"""
    df_si_so_all = lay_du_lieu_si_so(base_dir)
    f_tt = os.path.join(base_dir, "danh_sach_hoc_sinh_toan_truong.csv") if os.path.exists(os.path.join(base_dir, "danh_sach_hoc_sinh_toan_truong.csv")) else FILE_TOAN_TRUONG
    df_tt_all = pd.read_csv(f_tt, encoding='utf-8-sig', dtype=str).fillna("") if os.path.exists(f_tt) else pd.DataFrame()

    records_21_lop = []
    tong_hs_toan_truong = 0
    tong_co_mat_toan_truong = 0
    tong_vang_toan_truong = 0
    so_lop_da_bao = 0

    for lop_item in DS_21_LOP:
        si_so_goc = len(df_tt_all[df_tt_all["Lớp"] == lop_item]) if not df_tt_all.empty else 40
        tong_hs_toan_truong += si_so_goc

        # Tìm báo cáo của lớp
        m_row = (df_si_so_all["Ngày"] == ngay_str) & (df_si_so_all["Lớp"] == lop_item) & (df_si_so_all["Buổi"] == ten_buoi_chuan) if not df_si_so_all.empty else pd.Series([False])
        if m_row.any():
            so_lop_da_bao += 1
            r_data = df_si_so_all[m_row].iloc[-1]
            co_mat_val = int(r_data.get("Có mặt", si_so_goc))
            vang_val = int(r_data.get("Vắng", 0))
            tong_co_mat_toan_truong += co_mat_val
            tong_vang_toan_truong += vang_val

            records_21_lop.append({
                "Lớp": lop_item,
                "Sĩ số": si_so_goc,
                "Có mặt": co_mat_val,
                "Vắng": vang_val,
                "Tỷ lệ": f"{(co_mat_val / si_so_goc * 100):.1f}%" if si_so_goc > 0 else "100%",
                "Chi tiết vắng": r_data.get("Danh sách vắng", "Không có"),
                "Người báo cáo": r_data.get("Người báo cáo", ""),
                "Thời gian": r_data.get("Thời gian cập nhật", ""),
                "Trạng thái": "🟢 Đã báo cáo"
            })
        else:
            records_21_lop.append({
                "Lớp": lop_item,
                "Sĩ số": si_so_goc,
                "Có mặt": "-",
                "Vắng": "-",
                "Tỷ lệ": "-",
                "Chi tiết vắng": "-",
                "Người báo cáo": "-",
                "Thời gian": "-",
                "Trạng thái": "⏳ Chờ báo cáo"
            })

    # Thống kê nhanh toàn trường
    c_st1, c_st2, c_st3, c_st4 = st.columns(4)
    c_st1.metric("🏫 Tiến Độ Báo Cáo", f"{so_lop_da_bao}/21 Lớp", delta=f"{(so_lop_da_bao/21*100):.1f}% hoàn thành")
    c_st2.metric("👥 Tổng Học Sinh Đã Báo", f"{tong_co_mat_toan_truong + tong_vang_toan_truong} HS", delta=f"{tong_hs_toan_truong} toàn trường")
    c_st3.metric("🟢 Tổng Có Mặt", f"{tong_co_mat_toan_truong} HS", delta="Đang học tại trường")
    c_st4.metric("🔴 Tổng Vắng Mặt", f"{tong_vang_toan_truong} HS", delta="Cần theo dõi", delta_color="inverse")

    df_view_21 = pd.DataFrame(records_21_lop)
    st.dataframe(df_view_21, use_container_width=True, hide_index=True)

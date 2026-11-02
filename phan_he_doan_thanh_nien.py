# -*- coding: utf-8 -*-
"""
PHÂN HỆ 3: ĐOÀN THANH NIÊN (ĐTN) & QUẢN LÝ PHƯƠNG TIỆN TOÀN TRƯỜNG
Trường THPT số 2 Bảo Yên - Xã Bảo Hà, Huyện Bảo Yên, Tỉnh Lào Cai
"""

import os
import io
import base64
import streamlit as st
import pandas as pd
from datetime import datetime, date

try:
    import qrcode
    from PIL import Image
    HAS_QRCODE = True
except Exception:
    HAS_QRCODE = False

_CACHE_QR_B64 = {}

def dinh_dang_sdt(s):
    """Chuẩn hóa số điện thoại dạng 10 số"""
    if pd.isna(s):
        return "Chưa cập nhật"
    s_str = str(s).replace('.0', '').strip()
    if not s_str or s_str.lower() == 'nan':
        return "Chưa cập nhật"
    if len(s_str) == 9 and not s_str.startswith('0'):
        return '0' + s_str
    return s_str

def lay_mo_ta_mau_xe(r):
    """Mô tả màu sắc và hãng xe chi tiết theo mô tả"""
    if r is None or not hasattr(r, "get"):
        return "Theo thực tế lưu hành"
    mau = str(r.get('Màu xe', '')).strip()
    hang = str(r.get('Hãng xe', '')).strip()
    if mau and mau.lower() != 'nan' and hang and hang.lower() != 'nan':
        return f"{mau} ({hang})"
    elif mau and mau.lower() != 'nan':
        return mau
    elif hang and hang.lower() != 'nan':
        return f"Hãng {hang}"
    else:
        return "Theo thực tế lưu hành"

def tao_noi_dung_qr_xe(r):
    """Tạo nội dung mã hóa vào mã QR định dạng tinh gọn chuẩn ban đầu, siêu dễ quét, bổ sung loại & màu xe"""
    if r is None or not hasattr(r, "get"):
        return ""
    
    ma_xe = str(r.get('Mã xe', '')).strip()
    bien_so = str(r.get('Biển số xe', '')).strip()
    ten_hs = str(r.get('Họ và tên', '')).strip()
    lop = str(r.get('Lớp', '')).strip()
    sdt_hs = dinh_dang_sdt(r.get('SĐT Học sinh', ''))
    if sdt_hs == "Chưa cập nhật":
        sdt_hs = "Chưa có"

    # Xử lý gọn loại xe & màu xe
    loai_xe = str(r.get('Loại xe', '')).strip()
    mo_ta_mau = lay_mo_ta_mau_xe(r)
    if loai_xe and mo_ta_mau and mo_ta_mau != "Theo thực tế lưu hành":
        loai_mau = f"{loai_xe} - {mo_ta_mau}"
    elif loai_xe:
        loai_mau = loai_xe
    elif mo_ta_mau and mo_ta_mau != "Theo thực tế lưu hành":
        loai_mau = mo_ta_mau
    else:
        loai_mau = "Xe học sinh"

    # Lấy thông tin Nơi để xe / Nơi gửi xe
    noi_de_raw = str(r.get('Nơi để xe', r.get('Nơi gửi xe', ''))).strip()
    if not noi_de_raw or noi_de_raw.lower() == 'nan':
        noi_de_xe = "Trong trường"
    elif noi_de_raw.lower() == 'trong trường':
        noi_de_xe = "Trong trường"
    else:
        noi_de_xe = noi_de_raw

    ten_ph = str(r.get('Họ tên Phụ huynh', '')).strip()
    if not ten_ph or ten_ph.lower() == 'nan':
        ten_ph = "Phụ huynh"
    sdt_ph = dinh_dang_sdt(r.get('SĐT Phụ huynh', ''))
    
    if sdt_ph and sdt_ph != "Chưa cập nhật":
        ph_str = f"PH: {ten_ph} ({sdt_ph})"
    else:
        ph_str = f"PH: {ten_ph}"

    return (
        f"THPT SỐ 2 BẢO YÊN\n"
        f"Mã xe: {ma_xe} - Biển: {bien_so}\n"
        f"HS: {ten_hs} - {lop}\n"
        f"SĐT: {sdt_hs}\n"
        f"Loại/Màu xe: {loai_mau}\n"
        f"Nơi để xe: {noi_de_xe}\n"
        f"{ph_str}"
    )

def tao_anh_qr_base64(text_data):
    """Tạo ảnh QR code dạng base64 từ chuỗi dữ liệu (tự động căn chỉnh kích thước & lưu cache)"""
    if text_data in _CACHE_QR_B64:
        return _CACHE_QR_B64[text_data]
    if HAS_QRCODE:
        try:
            qr = qrcode.QRCode(
                version=None,
                error_correction=qrcode.constants.ERROR_CORRECT_M,
                box_size=4,
                border=2
            )
            qr.add_data(text_data)
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")
            buf = io.BytesIO()
            img.save(buf, format="PNG")
            b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
            res = f"data:image/png;base64,{b64}"
            _CACHE_QR_B64[text_data] = res
            return res
        except Exception:
            pass
    # Fallback dùng QR Server API
    import urllib.parse
    encoded = urllib.parse.quote(text_data)
    res = f"https://api.qrserver.com/v1/create-qr-code/?size=250x250&data={encoded}"
    _CACHE_QR_B64[text_data] = res
    return res

def tao_html_in_tem_qr(df_in, tieu_de_pham_vi):
    """Tạo mã HTML hoàn chỉnh chuẩn khổ giấy A4 để in tem decal dán xe học sinh"""
    html_items = []
    for idx, r in df_in.iterrows():
        txt_qr = tao_noi_dung_qr_xe(r)
        img_qr = tao_anh_qr_base64(txt_qr)
        mo_ta_mau = lay_mo_ta_mau_xe(r)
        sdt_hs = dinh_dang_sdt(r.get('SĐT Học sinh', ''))
        noi_de_raw = str(r.get('Nơi để xe', r.get('Nơi gửi xe', ''))).strip()
        noi_de_xe = "Trong trường" if (not noi_de_raw or noi_de_raw.lower() in ['nan', 'trong trường']) else noi_de_raw
        sdt_ph = dinh_dang_sdt(r.get('SĐT Phụ huynh', ''))
        ten_ph = str(r.get('Họ tên Phụ huynh', 'Chưa cập nhật')).strip()
        if not ten_ph or ten_ph.lower() == 'nan':
            ten_ph = "Chưa cập nhật"
        
        item_html = f"""
        <div class="sticker">
            <div class="sticker-header">
                <div class="school-name">TRƯỜNG THPT SỐ 2 BẢO YÊN</div>
                <div class="sticker-code">{r['Mã xe']} • {r['Lớp']}</div>
            </div>
            <div class="sticker-body">
                <div class="qr-col">
                    <img class="qr-img" src="{img_qr}" alt="QR">
                </div>
                <div class="info-col">
                    <div class="plate-number">{r['Biển số xe']}</div>
                    <div class="info-line">👤 <b>HS:</b> {r['Họ và tên']}</div>
                    <div class="info-line">📱 <b>SĐT:</b> {sdt_hs}</div>
                    <div class="info-line">🛵 <b>Loại:</b> {r['Loại xe']}</div>
                    <div class="info-line">🎨 <b>Màu:</b> {mo_ta_mau}</div>
                    <div class="info-line">📍 <b>Nơi để:</b> {noi_de_xe}</div>
                    <div class="info-line">👨‍👩‍👧 <b>PH:</b> {ten_ph} ({sdt_ph})</div>
                </div>
            </div>
            <div class="sticker-footer">
                Quét mã QR bằng điện thoại để kiểm tra thông tin • Năm học 2026 - 2027
            </div>
        </div>
        """
        html_items.append(item_html)
        
    all_stickers = "\n".join(html_items)
    
    return f"""<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="utf-8">
<title>Tem Mã QR Xe - {tieu_de_pham_vi} - THPT Số 2 Bảo Yên</title>
<style>
    @page {{
        size: A4 portrait;
        margin: 8mm;
    }}
    * {{
        box-sizing: border-box;
        -webkit-print-color-adjust: exact !important;
        print-color-adjust: exact !important;
    }}
    body {{
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        margin: 0;
        padding: 10px;
        background: #F3F4F6;
    }}
    .no-print {{
        background: linear-gradient(135deg, #059669, #10B981);
        color: white;
        padding: 16px 24px;
        margin-bottom: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);
        display: flex;
        justify-content: space-between;
        align-items: center;
    }}
    .btn-print {{
        background: #F59E0B;
        color: #111827;
        font-weight: bold;
        border: none;
        padding: 10px 22px;
        border-radius: 6px;
        cursor: pointer;
        font-size: 15px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.15);
    }}
    .btn-print:hover {{
        background: #D97706;
    }}
    .grid-container {{
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 8mm;
    }}
    .sticker {{
        border: 2px dashed #059669;
        background: white;
        border-radius: 8px;
        padding: 9px 12px;
        page-break-inside: avoid;
        break-inside: avoid;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        min-height: 52mm;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }}
    .sticker-header {{
        border-bottom: 1.5px solid #059669;
        padding-bottom: 4px;
        margin-bottom: 6px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }}
    .school-name {{
        font-size: 11.5px;
        font-weight: 800;
        color: #065F46;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }}
    .sticker-code {{
        background: #D1FAE5;
        color: #065F46;
        font-weight: bold;
        font-size: 11px;
        padding: 2px 8px;
        border-radius: 4px;
    }}
    .sticker-body {{
        display: flex;
        gap: 12px;
        align-items: center;
    }}
    .qr-col {{
        flex: 0 0 102px;
        text-align: center;
    }}
    .qr-img {{
        width: 100px;
        height: 100px;
        display: block;
        border: 1px solid #E5E7EB;
        border-radius: 4px;
    }}
    .info-col {{
        flex: 1;
        font-size: 11px;
        line-height: 1.38;
        color: #1F2937;
    }}
    .plate-number {{
        font-size: 15.5px;
        font-weight: 900;
        color: #1E3A8A;
        letter-spacing: 0.5px;
        margin-bottom: 3px;
    }}
    .info-line {{
        margin-bottom: 2px;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }}
    .sticker-footer {{
        border-top: 1px dashed #D1D5DB;
        margin-top: 5px;
        padding-top: 3px;
        font-size: 9px;
        color: #6B7280;
        text-align: center;
        font-style: italic;
    }}
    @media print {{
        body {{
            background: white;
            padding: 0;
        }}
        .no-print {{
            display: none !important;
        }}
        .grid-container {{
            gap: 6mm;
        }}
        .sticker {{
            box-shadow: none;
        }}
    }}
</style>
</head>
<body>
    <div class="no-print">
        <div>
            <h2 style="margin:0; font-size:18px;">📄 MẪU IN TEM MÃ QR XE - {tieu_de_pham_vi}</h2>
            <p style="margin:4px 0 0 0; opacity:0.95; font-size:13px;">Trường THPT số 2 Bảo Yên • Tổng cộng: <b>{len(df_in)} tem</b> • Khổ in: Giấy A4 / Decal</p>
        </div>
        <button class="btn-print" onclick="window.print()">🖨️ BẤM VÀO ĐÂY ĐỂ IN (CTRL + P)</button>
    </div>
    <div class="grid-container">
        {all_stickers}
    </div>
</body>
</html>
"""

def render_phan_he_doan_thanh_nien(df_tai_khoan, role_curr, nam_hoc, BASE_DIR, THU_MUC_NAM_HOC):
    st.markdown("""
        <div style='background: linear-gradient(135deg, #DC2626, #B91C1C); padding: 10px 16px; border-radius: 8px; color: white; margin-bottom: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.08);'>
            <h3 style='margin:0; font-size: 19px; color: white; font-weight:700;'>🚩 ĐOÀN THANH NIÊN (ĐTN) & NỀ NẾP HỌC SINH</h3>
            <p style='margin: 4px 0 0 0; opacity: 0.95; font-size: 14px;'>
                Đoàn TNCS Hồ Chí Minh - Trường THPT số 2 Bảo Yên • Năm học: <b>{}</b>
            </p>
        </div>
    """.format(nam_hoc), unsafe_allow_html=True)

    folder_nam = nam_hoc.replace(" ", "")
    dir_nam = os.path.join(THU_MUC_NAM_HOC, folder_nam)
    os.makedirs(dir_nam, exist_ok=True)
    
    f_dtn_td = os.path.join(dir_nam, "thi_dua_dtn_20_lop.csv")
    f_dtn_dv = os.path.join(dir_nam, "danh_sach_doan_vien.csv")
    f_xe = os.path.join(dir_nam, "quan_ly_phuong_tien.csv") if os.path.exists(os.path.join(dir_nam, "quan_ly_phuong_tien.csv")) else os.path.join(BASE_DIR, "quan_ly_phuong_tien.csv")
    f_vp = os.path.join(BASE_DIR, "lich_su_vi_pham_xe.csv")

    u_curr = st.session_state.get("user_login", {})
    u_username = u_curr.get("username", "")
    
    # Kiểm tra quyền quản lý phương tiện: Admin, BGH, Đoàn trường, Cờ đỏ, Ban Cán sự (Lớp trưởng, Bí thư)
    quyen_ql = str(u_curr.get("quyen_quan_ly", "")).strip()
    chuc_danh_str = str(u_curr.get("chuc_danh", "")).lower()
    is_bcs = ("ban cán sự" in quyen_ql.lower()) or ("cờ đỏ" in quyen_ql.lower()) or ("lớp trưởng" in chuc_danh_str) or ("bí thư" in chuc_danh_str)
    la_quan_tri_xe = (role_curr in ["Ban Giám hiệu", "Ban Chấp hành Đoàn", "Đội Cờ đỏ"]) or ("Quản lý phương tiện" in quyen_ql) or ("Toàn quyền" in quyen_ql) or u_curr.get("quyen_quan_ly_xe", False) or is_bcs
    is_ph_hs = (role_curr in ["Phụ huynh học sinh", "Học sinh"]) and not is_bcs

    tab_bang_vang, tab_cham_diem, tab_bcs_si_so, tab_bcs_xe, tab_phuong_tien, tab_phong_trao_dv = st.tabs([
        "🏆 Bảng Vàng Thi Đua 21 Lớp",
        "⚖️ Chấm Điểm & Nề Nếp Live",
        "📊 LỚP TRƯỞNG: BÁO SĨ SỐ LỚP (SÁNG / CHIỀU / CẢ NGÀY)",
        "🛵 BAN CÁN SỰ: ĐÁNH GIÁ VI PHẠM PHƯƠNG TIỆN",
        "🛵 Quản Lý Phương Tiện & Mã QR",
        "🎯 Phong Trào & Sổ Đoàn"
    ])

    # -------------------------------------------------------------------------
    # TAB 1: BẢNG VÀNG THI ĐUA 21 CHI ĐOÀN
    # -------------------------------------------------------------------------
    with tab_bang_vang:
        st.subheader("🏆 Bảng Xếp Hạng Thi Đua Nề Nếp Các Chi Đoàn")
        st.caption("Tổng hợp tự động từ kết quả chấm nề nếp hàng ngày của Đội Cờ Đỏ và vi phạm phương tiện.")

        if os.path.exists(f_dtn_td):
            df_td = pd.read_csv(f_dtn_td, encoding='utf-8-sig').fillna("")
            for col in ['Điểm gốc', 'Chuyên cần', 'Đồng phục', 'Vệ sinh', 'Truy bài', 'Xếp hàng', 'Điểm cộng', 'Điểm trừ', 'Tổng điểm']:
                if col in df_td.columns:
                    df_td[col] = pd.to_numeric(df_td[col], errors='coerce').fillna(0)

            df_td['Xếp hạng'] = df_td['Tổng điểm'].rank(ascending=False, method='min').astype(int)
            df_td = df_td.sort_values(by=['Tổng điểm', 'Điểm cộng'], ascending=[False, False])

            # Top 3 vinh danh cờ luân lưu
            if len(df_td) >= 3:
                top1, top2, top3 = df_td.iloc[0], df_td.iloc[1], df_td.iloc[2]
                col_top1, col_top2, col_top3 = st.columns(3)
                with col_top1:
                    st.markdown(f"""
                        <div style='background:#FEF3C7; border:2px solid #F59E0B; border-radius:10px; padding:15px; text-align:center;'>
                            <h3 style='color:#B45309; margin:0;'>🥇 HẠNG NHẤT</h3>
                            <h2 style='color:#D97706; margin:5px 0;'>Chi đoàn {top1['Chi đoàn']}</h2>
                            <p style='font-size:18px; font-weight:bold; color:#1E3A8A; margin:0;'>{top1['Tổng điểm']} Điểm</p>
                            <span style='background:#F59E0B; color:white; padding:2px 8px; border-radius:10px; font-size:12px;'>🚩 CỜ XUẤT SẮC TUẦN</span>
                        </div>
                    """, unsafe_allow_html=True)
                with col_top2:
                    st.markdown(f"""
                        <div style='background:#F3F4F6; border:2px solid #9CA3AF; border-radius:10px; padding:15px; text-align:center;'>
                            <h3 style='color:#4B5563; margin:0;'>🥈 HẠNG NHÌ</h3>
                            <h2 style='color:#374151; margin:5px 0;'>Chi đoàn {top2['Chi đoàn']}</h2>
                            <p style='font-size:18px; font-weight:bold; color:#1E3A8A; margin:0;'>{top2['Tổng điểm']} Điểm</p>
                            <span style='background:#9CA3AF; color:white; padding:2px 8px; border-radius:10px; font-size:12px;'>🚩 CỜ XẾP THỨ NHÌ</span>
                        </div>
                    """, unsafe_allow_html=True)
                with col_top3:
                    st.markdown(f"""
                        <div style='background:#FFFBEB; border:2px solid #D97706; border-radius:10px; padding:15px; text-align:center;'>
                            <h3 style='color:#92400E; margin:0;'>🥉 HẠNG BA</h3>
                            <h2 style='color:#B45309; margin:5px 0;'>Chi đoàn {top3['Chi đoàn']}</h2>
                            <p style='font-size:18px; font-weight:bold; color:#1E3A8A; margin:0;'>{top3['Tổng điểm']} Điểm</p>
                            <span style='background:#D97706; color:white; padding:2px 8px; border-radius:10px; font-size:12px;'>🚩 CỜ XẾP THỨ BA</span>
                        </div>
                    """, unsafe_allow_html=True)

            st.markdown("---")
            chon_khoi = st.selectbox("🔍 Lọc theo khối:", ["Tất cả 21 Chi đoàn", "Khối 10", "Khối 11", "Khối 12"])
            df_view = df_td.copy()
            if chon_khoi != "Tất cả 21 Chi đoàn":
                df_view = df_view[df_view['Khối'] == chon_khoi.replace("Khối ", "")]

            st.dataframe(
                df_view[['Xếp hạng', 'Chi đoàn', 'Khối', 'Điểm gốc', 'Điểm cộng', 'Điểm trừ', 'Tổng điểm', 'Xếp loại', 'Ghi chú']],
                use_container_width=True,
                hide_index=True
            )

            if not is_ph_hs:
                csv_td_bytes = df_td.to_csv(index=False, encoding='utf-8-sig').encode('utf-8-sig')
                st.download_button(
                    label="📥 TẢI BẢNG XẾP HẠNG THI ĐUA ĐTN (EXCEL / CSV)",
                    data=csv_td_bytes,
                    file_name=f"bang_thi_dua_dtn_thpt2_baoyen_{folder_nam}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
            else:
                st.info("ℹ️ Bảng vàng thi đua 21 Chi đoàn được công khai để học sinh và phụ huynh cùng theo dõi và khích lệ nề nếp rèn luyện.")

    # -------------------------------------------------------------------------
    # TAB 2: CHẤM ĐIỂM NỀ NẾP TUẦN
    # -------------------------------------------------------------------------
    # TAB 2: CHẤM ĐIỂM NỀ NẾP & CỜ ĐỎ
    # -------------------------------------------------------------------------
    with tab_cham_diem:
        st.subheader("⚖️ Chấm Điểm Nề Nếp & Đánh Giá Rèn Luyện Học Sinh (Thời Gian Thực)")
        st.caption("Dành cho Ban Chấp Hành Đoàn Trường, Đội Cờ Đỏ và Giáo viên chủ nhiệm theo dõi nề nếp toàn trường.")

        sub_cd_lop, sub_cd_hs = st.tabs([
            "✍️ CHẤM ĐIỂM THI ĐUA 21 CHI ĐOÀN",
            "🔍 THEO DÕI & ĐÁNH GIÁ TỪNG HỌC SINH (LIVE)"
        ])

        with sub_cd_lop:
            if os.path.exists(f_dtn_td):
                df_td_edit = pd.read_csv(f_dtn_td, encoding='utf-8-sig').fillna("")
                ds_lop = sorted(list(df_td_edit['Chi đoàn'].unique()))

                if is_ph_hs:
                    st.info("ℹ️ **Quy định phân quyền:** Chức năng chấm điểm thi đua nề nếp chỉ dành cho Ban Chấp Hành Đoàn Trường và Đội Cờ Đỏ. Học sinh và phụ huynh xem bảng nề nếp chi tiết bên dưới:")
                    st.dataframe(df_td_edit[['Chi đoàn', 'Khối', 'Tổng điểm', 'Xếp loại', 'Điểm trừ', 'Điểm cộng', 'Ghi chú']], use_container_width=True, hide_index=True)
                else:
                    with st.form("form_cham_diem_dtn"):
                        c_lop, c_tuan = st.columns([1, 1])
                        with c_lop:
                            lop_duoc_chon = st.selectbox("Chọn Chi đoàn chấm điểm:", ds_lop)
                        with c_tuan:
                            tuan_cham = st.selectbox("Tuần thi đua:", [f"Tuần {i}" for i in range(1, 38)], index=8)

                        st.markdown("##### 📌 Các tiêu chí trừ điểm vi phạm nề nếp:")
                        c_p1, c_p2, c_p3 = st.columns(3)
                        with c_p1:
                            tru_chuyen_can = st.number_input("Chuyên cần (nghỉ KP -5đ, đi muộn -2đ):", min_value=0, max_value=50, value=0, step=1)
                            tru_dong_phuc = st.number_input("Đồng phục, thẻ HS (-2đ/lượt):", min_value=0, max_value=50, value=0, step=1)
                        with c_p2:
                            tru_ve_sinh = st.number_input("Vệ sinh lớp, trực nhật (-3đ):", min_value=0, max_value=50, value=0, step=1)
                            tru_truy_bai = st.number_input("15 phút truy bài đầu giờ (-2đ):", min_value=0, max_value=50, value=0, step=1)
                        with c_p3:
                            tru_xep_hang = st.number_input("Xếp hàng chào cờ / thể dục (-2đ):", min_value=0, max_value=50, value=0, step=1)
                            tru_khac = st.number_input("Vi phạm khác (điện thoại, trật tự...):", min_value=0, max_value=50, value=0, step=1)

                        st.markdown("##### 🌟 Điểm thưởng cộng thêm:")
                        c_b1, c_b2 = st.columns(2)
                        with c_b1:
                            cong_hoa_diem = st.number_input("Hoa điểm tốt (+2đ/bông):", min_value=0, max_value=50, value=0, step=1)
                        with c_b2:
                            cong_phong_trao = st.number_input("Phong trào, văn nghệ, thể thao (+5đ):", min_value=0, max_value=50, value=0, step=1)

                        ghi_chu_vp = st.text_input("Ghi chú chi tiết vi phạm (nếu có):", placeholder="VD: 2 HS đi muộn thứ 3; 1 HS quên thẻ...")

                        btn_luu_diem = st.form_submit_button("💾 LƯU ĐIỂM THI ĐUA CHI ĐOÀN", type="primary", use_container_width=True)
                        if btn_luu_diem:
                            idx_match = df_td_edit[df_td_edit['Chi đoàn'] == lop_duoc_chon].index
                            if not idx_match.empty:
                                idx_l = idx_match[0]
                                tong_tru = int(tru_chuyen_can + tru_dong_phuc + tru_ve_sinh + tru_truy_bai + tru_xep_hang + tru_khac)
                                tong_cong = int(cong_hoa_diem + cong_phong_trao)
                                tong_diem_moi = 100 + tong_cong - tong_tru
                            
                                df_td_edit.loc[idx_l, 'Điểm cộng'] = tong_cong
                                df_td_edit.loc[idx_l, 'Điểm trừ'] = tong_tru
                                df_td_edit.loc[idx_l, 'Tổng điểm'] = tong_diem_moi
                                df_td_edit.loc[idx_l, 'Xếp loại'] = "Tốt" if tong_diem_moi >= 95 else ("Khá" if tong_diem_moi >= 85 else "Trung bình")
                                if ghi_chu_vp.strip():
                                    df_td_edit.loc[idx_l, 'Ghi chú'] = ghi_chu_vp.strip()

                                df_td_edit.to_csv(f_dtn_td, index=False, encoding='utf-8-sig')
                                st.success(f"🎉 Đã cập nhật thành công điểm thi đua cho Chi đoàn {lop_duoc_chon}! Tổng điểm: {tong_diem_moi} điểm.")
                                st.rerun()

        with sub_cd_hs:
            st.markdown("#### 🔍 **Theo Dõi, Thống Kê Đánh Giá Từng Học Sinh Vi Phạm Thời Gian Thực**")
            f_hs_vp = os.path.join(BASE_DIR, "nhat_ky_vi_pham_hoc_sinh.csv")
            if not os.path.exists(f_hs_vp):
                df_hs_vp_init = pd.DataFrame([
                    {"Ngày": "28/10/2026", "Học sinh": "Nguyễn Văn Nam", "Lớp": "10A1", "Lỗi vi phạm": "Đi học muộn (15p)", "Người phát hiện": "Cờ đỏ (Khối 12)", "Điểm trừ Chi đoàn": -2, "Trạng thái": "Đã thông báo GVCN", "Ghi chú": "Nhắc nhở lần 1"},
                    {"Ngày": "28/10/2026", "Học sinh": "Hoàng Thị Mai", "Lớp": "10A3", "Lỗi vi phạm": "Không đội mũ bảo hiểm xe điện", "Người phát hiện": "Cờ đỏ cổng trường", "Điểm trừ Chi đoàn": -5, "Trạng thái": "Đã trừ điểm thi đua", "Ghi chú": "Phối hợp Đội xe QR"},
                    {"Ngày": "29/10/2026", "Học sinh": "Lê Tuấn Tú", "Lớp": "11A2", "Lỗi vi phạm": "Quên thẻ học sinh", "Người phát hiện": "Cờ đỏ cổng trường", "Điểm trừ Chi đoàn": -2, "Trạng thái": "Đã thông báo GVCN", "Ghi chú": "Đã bổ sung thẻ"},
                    {"Ngày": "29/10/2026", "Học sinh": "Đặng Văn Hùng", "Lớp": "12A1", "Lỗi vi phạm": "Sử dụng điện thoại trong giờ học", "Người phát hiện": "Đội xung kích Đoàn", "Điểm trừ Chi đoàn": -5, "Trạng thái": "BGH đã làm việc", "Ghi chú": "Tạm giữ điện thoại trả phụ huynh"}
                ])
                df_hs_vp_init.to_csv(f_hs_vp, index=False, encoding='utf-8-sig')

            df_hs_vp = pd.read_csv(f_hs_vp, encoding='utf-8-sig').fillna("")
            st.dataframe(df_hs_vp, use_container_width=True, hide_index=True)

            if not is_ph_hs:
                with st.expander("➕ **Đội Cờ Đỏ Ghi Nhận Lỗi Vi Phạm Của Học Sinh Mới:**"):
                    with st.form("form_add_hs_vp"):
                        c_vp1, c_vp2 = st.columns(2)
                        with c_vp1:
                            hs_ten_vp = st.text_input("Họ và tên học sinh vi phạm:")
                            hs_lop_vp = st.selectbox("Lớp học:", [f"10A{i}" for i in range(1, 8)] + [f"11A{i}" for i in range(1, 8)] + [f"12A{i}" for i in range(1, 8)])
                            loi_vp = st.selectbox("Lỗi vi phạm:", ["Đi học muộn", "Không đội mũ bảo hiểm xe máy/xe đạp điện", "Không mặc đồng phục / quên thẻ", "Vệ sinh bẩn / vứt rác bừa bãi", "Sử dụng điện thoại trái phép", "Vi phạm khác"])
                        with c_vp2:
                            diem_tru_val = st.number_input("Điểm trừ thi đua Chi đoàn:", value=2, min_value=1, max_value=20)
                            nguoi_ghi_vp = st.text_input("Người phát hiện (Cờ đỏ / Đoàn trường):", value=u_curr.get("fullname", "Cờ đỏ"))
                            ghi_chu_vp_hs = st.text_input("Biện pháp xử lý / Ghi chú:")
                        if st.form_submit_button("🚨 GHI NHẬN VI PHẠM & TỰ ĐỘNG THÔNG BÁO GVCN", type="primary"):
                            if hs_ten_vp.strip():
                                new_vp_row = pd.DataFrame([{
                                    "Ngày": date.today().strftime("%d/%m/%Y"),
                                    "Học sinh": hs_ten_vp.strip(),
                                    "Lớp": hs_lop_vp,
                                    "Lỗi vi phạm": loi_vp,
                                    "Người phát hiện": nguoi_ghi_vp,
                                    "Điểm trừ Chi đoàn": -diem_tru_val,
                                    "Trạng thái": "Đã thông báo GVCN",
                                    "Ghi chú": ghi_chu_vp_hs.strip()
                                }])
                                df_hs_vp = pd.concat([df_hs_vp, new_vp_row], ignore_index=True)
                                df_hs_vp.to_csv(f_hs_vp, index=False, encoding='utf-8-sig')
                                st.success(f"🎉 Đã ghi nhận vi phạm của em {hs_ten_vp} (Lớp {hs_lop_vp}) thành công!")
                                st.rerun()

    # -------------------------------------------------------------------------
    # TAB 3: LỚP TRƯỞNG: BÁO SĨ SỐ LỚP (SÁNG / CHIỀU / CẢ NGÀY)
    # -------------------------------------------------------------------------
    with tab_bcs_si_so:
        st.subheader("📊 Báo Cáo Sĩ Số Lớp (Sáng / Chiều / Cả Ngày) - Dành Cho Lớp Trưởng & Ban Cán Sự")
        st.caption("Cập nhật sĩ số lớp học theo thời gian thực gửi trực tiếp về Ban Giám Hiệu, Đoàn Trường và Giáo viên chủ nhiệm.")
        import quan_ly_si_so_lop
        quan_ly_si_so_lop.render_giao_dien_bao_si_so(
            u_curr=u_curr,
            role_curr=role_curr if 'role_curr' in locals() else "Ban Chấp hành Đoàn",
            base_dir=BASE_DIR,
            is_bcs=is_bcs,
            is_gvcn=("chủ nhiệm" in chuc_danh_str),
            is_admin=la_quan_tri_xe
        )

    # -------------------------------------------------------------------------
    # TAB 4: BAN CÁN SỰ: ĐÁNH GIÁ VI PHẠM PHƯƠNG TIỆN
    # -------------------------------------------------------------------------
    with tab_bcs_xe:
        st.subheader("🛵 Ban Cán Sự: Kiểm Tra & Đánh Giá Vi Phạm Phương Tiện")
        st.caption("Dành cho Lớp trưởng, Bí thư chi đoàn và Đội Cờ đỏ ghi nhận các trường hợp vi phạm nề nếp phương tiện xe toàn trường.")
        
        f_xe_bcs = os.path.join(BASE_DIR, "quan_ly_phuong_tien.csv") if os.path.exists(os.path.join(BASE_DIR, "quan_ly_phuong_tien.csv")) else "D:/quan_ly_phuong_tien.csv"
        df_xe_bcs = pd.read_csv(f_xe_bcs, encoding='utf-8-sig', dtype=str).fillna("") if os.path.exists(f_xe_bcs) else pd.DataFrame()
        
        if not df_xe_bcs.empty:
            ds_lop_list = ["Tất cả các lớp", "10A1", "10A2", "10A3", "10A4", "10A5", "10A6", "10A7", "11A1", "11A2", "11A3", "11A4", "11A5", "11A6", "11A7", "12A1", "12A2", "12A3", "12A4", "12A5", "12A6", "12A7"]
            col_bcs_x1, col_bcs_x2 = st.columns([1, 2])
            with col_bcs_x1:
                lop_loc_xe = st.selectbox("Lọc xe theo lớp:", ds_lop_list, key="sb_loc_xe_bcs_dtn")
            with col_bcs_x2:
                tim_kw_xe = st.text_input("🔍 Tìm kiếm xe (Mã xe / Biển số / Tên HS):", placeholder="VD: 24-AA, Lê Văn...", key="txt_kw_xe_bcs_dtn")

            df_xe_show_bcs = df_xe_bcs.copy()
            if lop_loc_xe != "Tất cả các lớp":
                df_xe_show_bcs = df_xe_show_bcs[df_xe_show_bcs["Lớp"] == lop_loc_xe]
            if tim_kw_xe.strip():
                kw = tim_kw_xe.strip().lower()
                df_xe_show_bcs = df_xe_show_bcs[
                    df_xe_show_bcs["Mã xe"].str.lower().str.contains(kw) |
                    df_xe_show_bcs["Biển số xe"].str.lower().str.contains(kw) |
                    df_xe_show_bcs["Họ và tên"].str.lower().str.contains(kw)
                ]
            st.dataframe(df_xe_show_bcs[["Mã xe", "Họ và tên", "Lớp", "Biển số xe", "Loại xe", "Màu xe", "Nơi gửi xe", "Số lần vi phạm"]], use_container_width=True, hide_index=True)

            # Form đánh giá và ghi nhận vi phạm xe
            st.markdown("---")
            st.markdown("##### 🚨 Ghi nhận lỗi vi phạm xe & Chuyển trừ điểm thi đua chi đoàn:")
            with st.form("form_bcs_danh_gia_xe_dtn"):
                c_vp1, c_vp2 = st.columns([1.5, 1])
                with c_vp1:
                    ds_xe_opt = [f"{r['Mã xe']} - {r['Biển số xe']} - {r['Họ và tên']} ({r['Lớp']})" for idx, r in df_xe_show_bcs.iterrows()] if not df_xe_show_bcs.empty else []
                    if not ds_xe_opt:
                        ds_xe_opt = [f"{r['Mã xe']} - {r['Biển số xe']} - {r['Họ và tên']} ({r['Lớp']})" for idx, r in df_xe_bcs.iterrows()]
                    xe_vp_sel = st.selectbox("Chọn xe vi phạm:", ds_xe_opt, key="sb_xe_vp_bcs_dtn")
                with c_vp2:
                    loi_bcs_vp = st.selectbox("Hành vi vi phạm:", [
                        "Không đội mũ bảo hiểm (-5đ)",
                        "Đi xe máy phân khối lớn (>50cc) khi chưa đủ tuổi (-20đ)",
                        "Chở quá số người quy định (-5đ)",
                        "Đi xe dàn hàng ngang / Lạng lách (-10đ)",
                        "Không có gương chiếu hậu (-2đ)",
                        "Gửi xe sai nơi quy định / Không dán tem xe (-3đ)",
                        "Vi phạm trật tự an toàn giao thông khác (-5đ)"
                    ], key="sb_loi_bcs_dtn")
                
                ghi_chu_bcs = st.text_input("Ghi chú chi tiết (thời điểm, địa điểm vi phạm):", placeholder="VD: Gửi xe sai vị trí quy định tại nhà xe học sinh sáng nay...", key="txt_gc_bcs_dtn")
                btn_submit_bcs_vp = st.form_submit_button("🚨 XÁC NHẬN ĐÁNH GIÁ VI PHẠM & TRỪ ĐIỂM CHI ĐOÀN", type="primary", use_container_width=True)
                
                if btn_submit_bcs_vp and xe_vp_sel:
                    ma_xe_sel = xe_vp_sel.split(" - ")[0].strip()
                    r_xe_match = df_xe_bcs[df_xe_bcs['Mã xe'] == ma_xe_sel]
                    if not r_xe_match.empty:
                        r_x = r_xe_match.iloc[0]
                        lop_x = r_x['Lớp']
                        diem_tru_val = 5
                        if "(-20đ)" in loi_bcs_vp:
                            diem_tru_val = 20
                        elif "(-10đ)" in loi_bcs_vp:
                            diem_tru_val = 10
                        elif "(-3đ)" in loi_bcs_vp:
                            diem_tru_val = 3
                        elif "(-2đ)" in loi_bcs_vp:
                            diem_tru_val = 2
                        
                        # 1. Trừ điểm thi đua chi đoàn
                        if os.path.exists(f_dtn_td):
                            df_td_curr = pd.read_csv(f_dtn_td, encoding='utf-8-sig').fillna("")
                            idx_lop_m = df_td_curr[df_td_curr['Chi đoàn'] == lop_x].index
                            if not idx_lop_m.empty:
                                il = idx_lop_m[0]
                                c_tru = int(pd.to_numeric(df_td_curr.loc[il, 'Điểm trừ'], errors='coerce') or 0)
                                c_tong = int(pd.to_numeric(df_td_curr.loc[il, 'Tổng điểm'], errors='coerce') or 100)
                                df_td_curr.loc[il, 'Điểm trừ'] = c_tru + diem_tru_val
                                df_td_curr.loc[il, 'Tổng điểm'] = c_tong - diem_tru_val
                                df_td_curr.loc[il, 'Ghi chú'] = str(df_td_curr.loc[il, 'Ghi chú']) + f"; Ban cán sự báo vi phạm xe: {r_x['Họ và tên']} ({r_x['Biển số xe']})"
                                df_td_curr.to_csv(f_dtn_td, index=False, encoding='utf-8-sig')

                        # 2. Tăng số lần vi phạm xe
                        idx_x_all = df_xe_bcs[df_xe_bcs['Mã xe'] == ma_xe_sel].index
                        if not idx_x_all.empty:
                            ix = idx_x_all[0]
                            cur_lan = int(pd.to_numeric(df_xe_bcs.loc[ix, 'Số lần vi phạm'], errors='coerce') or 0)
                            df_xe_bcs.loc[ix, 'Số lần vi phạm'] = cur_lan + 1
                            df_xe_bcs.loc[ix, 'Tình trạng'] = 'Nhắc nhở nề nếp'
                            for d_save in [f_xe, os.path.join(BASE_DIR, 'quan_ly_phuong_tien.csv'), os.path.join('D:/phan_mem_ban_tru_cloud', 'quan_ly_phuong_tien.csv')]:
                                try:
                                    df_xe_bcs.to_csv(d_save, index=False, encoding='utf-8-sig')
                                except Exception:
                                    pass

                        # 3. Ghi vào lịch sử vi phạm
                        df_vp_new = pd.DataFrame([{
                            'Ngày': date.today().strftime('%d/%m/%Y'),
                            'Mã xe': ma_xe_sel,
                            'Họ và tên': r_x['Họ và tên'],
                            'Lớp': lop_x,
                            'Biển số xe': r_x['Biển số xe'],
                            'Lỗi vi phạm': loi_bcs_vp,
                            'Điểm trừ': diem_tru_val,
                            'Người lập biên bản': u_curr.get('fullname', 'Ban Cán Sự'),
                            'Ghi chú': ghi_chu_bcs,
                            'Trạng thái': 'Đã trừ điểm ĐTN'
                        }])
                        df_vp_all = pd.concat([pd.read_csv(f_vp, encoding='utf-8-sig'), df_vp_new], ignore_index=True) if os.path.exists(f_vp) else df_vp_new
                        df_vp_all.to_csv(f_vp, index=False, encoding='utf-8-sig')
                        st.success(f"🎉 Đã ghi nhận vi phạm thành công cho xe {r_x['Biển số xe']} ({r_x['Họ và tên']} - Lớp {lop_x})! Chi đoàn đã bị trừ {diem_tru_val} điểm.")
                        st.rerun()
        else:
            st.info("💡 Chưa có dữ liệu phương tiện xe trong cơ sở dữ liệu.")

    # -------------------------------------------------------------------------
    # TAB 5: QUẢN LÝ PHƯƠNG TIỆN & MÃ QR
    # -------------------------------------------------------------------------
    with tab_phuong_tien:
        st.subheader("🛵 Quản Lý Phương Tiện, Cấp Mã QR & Xử Lý Vi Phạm Nề Nếp")
        st.caption("Quản lý danh sách xe học sinh toàn trường, cấp tem mã QR định danh và tự động liên kết trừ điểm thi đua Chi đoàn khi vi phạm.")

        if os.path.exists(f_xe):
            df_xe_all = pd.read_csv(f_xe, encoding='utf-8-sig', dtype=str).fillna("")
            for c_phone in ['SĐT Học sinh', 'SĐT Phụ huynh', 'SĐT GVCN']:
                if c_phone in df_xe_all.columns:
                    df_xe_all[c_phone] = df_xe_all[c_phone].astype(str).str.replace('.0', '', regex=False).str.strip()
                    df_xe_all[c_phone] = df_xe_all[c_phone].apply(lambda x: '0' + x if (len(x) == 9 and not x.startswith('0') and x != 'nan') else ('' if x == 'nan' else x))
        else:
            df_xe_all = pd.DataFrame()

        # Đảm bảo các cột cốt lõi luôn tồn tại để không bao giờ bị KeyError
        required_cols = [
            'Mã xe', 'Biển số xe', 'Họ và tên', 'Lớp', 'Loại xe', 'Màu xe', 
            'Nơi gửi xe', 'SĐT Học sinh', 'GVCN', 'SĐT GVCN', 
            'Họ tên Phụ huynh', 'SĐT Phụ huynh', 'Địa chỉ', 'Tình trạng', 
            'Số lần vi phạm', 'Ghi chú'
        ]
        for col in required_cols:
            if col not in df_xe_all.columns:
                df_xe_all[col] = ""

        sub_xe1, sub_xe2, sub_xe3, sub_xe4 = st.tabs([
            "📋 Danh sách phương tiện",
            "🔍 Quét mã QR & Xử lý vi phạm",
            "🖨️ IN TEM MÃ QR (LỚP / KHỐI / TRƯỜNG)",
            "📂 Nhập nhanh xe từ Excel"
        ])

        # -------------------------------------------------------------
        # 1. DANH SÁCH PHƯƠNG TIỆN & BỘ LỌC
        # -------------------------------------------------------------
        with sub_xe1:
            c_xe_m1, c_xe_m2, c_xe_m3, c_xe_m4 = st.columns(4)
            with c_xe_m1:
                st.metric("🛵 Tổng phương tiện", f"{len(df_xe_all)} Xe", "Đã đăng ký")
            with c_xe_m2:
                col_loai_s = df_xe_all['Loại xe'].astype(str)
                so_dien = len(df_xe_all[col_loai_s.str.contains('điện', case=False, na=False)])
                st.metric("⚡ Xe máy/đạp điện", f"{so_dien} Xe")
            with c_xe_m3:
                so_50cc = len(df_xe_all[col_loai_s.str.contains('50cc', case=False, na=False)])
                st.metric("🏍️ Xe máy <50cc", f"{so_50cc} Xe")
            with c_xe_m4:
                so_vp = len(df_xe_all[df_xe_all['Số lần vi phạm'].astype(str) != "0"])
                st.metric("⚠️ Xe từng vi phạm", f"{so_vp} Xe", delta_color="inverse")

            st.markdown("---")
            
            c_f1, c_f2, c_f3 = st.columns([1, 1, 1.5])
            with c_f1:
                ds_lop_xe = ["Tất cả các lớp"] + sorted(list(df_xe_all['Lớp'].unique())) if not df_xe_all.empty else []
                loc_lop_xe = st.selectbox("Lọc theo lớp:", ds_lop_xe)
            with c_f2:
                ds_loai_xe = ["Tất cả loại xe", "Xe máy điện", "Xe đạp điện", "Xe máy <50cc", "Xe đạp"]
                loc_loai_xe = st.selectbox("Lọc loại xe:", ds_loai_xe)
            with c_f3:
                tim_xe = st.text_input("🔍 Tìm theo biển số xe, tên HS, SĐT, phụ huynh:", "")

            df_show_xe = df_xe_all.copy()
            if loc_lop_xe != "Tất cả các lớp":
                df_show_xe = df_show_xe[df_show_xe['Lớp'] == loc_lop_xe]
            if loc_loai_xe != "Tất cả loại xe":
                df_show_xe = df_show_xe[df_show_xe['Loại xe'] == loc_loai_xe]
            if tim_xe:
                df_show_xe = df_show_xe[
                    df_show_xe['Biển số xe'].astype(str).str.contains(tim_xe, case=False, na=False) |
                    df_show_xe['Họ và tên'].str.contains(tim_xe, case=False, na=False) |
                    df_show_xe['SĐT Học sinh'].astype(str).str.contains(tim_xe, na=False) |
                    df_show_xe['Họ tên Phụ huynh'].str.contains(tim_xe, case=False, na=False) |
                    df_show_xe['SĐT Phụ huynh'].astype(str).str.contains(tim_xe, na=False)
                ]

            if is_ph_hs:
                cot_xe_view = ['Mã xe', 'Biển số xe', 'Họ và tên', 'Lớp', 'Loại xe', 'Màu xe', 'Nơi gửi xe', 'Số lần vi phạm', 'Tình trạng']
            else:
                cot_xe_view = ['Mã xe', 'Biển số xe', 'Họ và tên', 'Lớp', 'Loại xe', 'Màu xe', 'Nơi gửi xe', 'SĐT Học sinh', 'GVCN', 'SĐT GVCN', 'Họ tên Phụ huynh', 'SĐT Phụ huynh', 'Số lần vi phạm', 'Tình trạng']
            st.dataframe(
                df_show_xe[[c for c in cot_xe_view if c in df_show_xe.columns]],
                use_container_width=True,
                hide_index=True
            )

            # Chỉnh sửa thông tin xe
            if la_quan_tri_xe:
                with st.expander("✏️ **Quản Trị Viên: Chỉnh sửa thông tin phương tiện toàn trường:**", expanded=False):
                    ds_ma_xe = df_xe_all['Mã xe'].tolist() if not df_xe_all.empty else []
                    xe_chon_edit = st.selectbox("Chọn xe cần chỉnh sửa thông tin:", ds_ma_xe)
                    if xe_chon_edit:
                        row_xe = df_xe_all[df_xe_all['Mã xe'] == xe_chon_edit].iloc[0]
                        with st.form("form_edit_xe_admin"):
                            ce1, ce2 = st.columns(2)
                            with ce1:
                                edit_bs = st.text_input("Biển số xe:", value=str(row_xe['Biển số xe']))
                                edit_loai = st.selectbox("Loại xe:", ["Xe máy điện", "Xe đạp điện", "Xe máy <50cc", "Xe đạp"], index=["Xe máy điện", "Xe đạp điện", "Xe máy <50cc", "Xe đạp"].index(row_xe['Loại xe']) if row_xe['Loại xe'] in ["Xe máy điện", "Xe đạp điện", "Xe máy <50cc", "Xe đạp"] else 0)
                                edit_mau = st.text_input("Màu xe / Nhãn hiệu:", value=str(row_xe['Màu xe']))
                            with ce2:
                                edit_noigui = st.selectbox("Nơi gửi xe:", ["Nhà xe KTX Bán trú", "Nhà xe Học sinh Khu A", "Nhà xe Học sinh Khu B"], index=0)
                                edit_tinhtrang = st.selectbox("Tình trạng lưu hành:", ["Đủ điều kiện lưu hành", "Đang tạm giữ", "Nhắc nhở nề nếp"], index=0)
                                edit_solan_vp = st.number_input("Số lần vi phạm:", min_value=0, max_value=20, value=int(row_xe.get('Số lần vi phạm', 0)))
                            
                            if st.form_submit_button("💾 LƯU THAY ĐỔI THÔNG TIN XE", type="primary", use_container_width=True):
                                idx_xe = df_xe_all[df_xe_all['Mã xe'] == xe_chon_edit].index[0]
                                df_xe_all.loc[idx_xe, 'Biển số xe'] = edit_bs.strip()
                                df_xe_all.loc[idx_xe, 'Loại xe'] = edit_loai
                                df_xe_all.loc[idx_xe, 'Màu xe'] = edit_mau.strip()
                                df_xe_all.loc[idx_xe, 'Nơi gửi xe'] = edit_noigui
                                df_xe_all.loc[idx_xe, 'Tình trạng'] = edit_tinhtrang
                                df_xe_all.loc[idx_xe, 'Số lần vi phạm'] = edit_solan_vp
                                
                                for d_save in [f_xe, os.path.join(BASE_DIR, 'quan_ly_phuong_tien.csv'), os.path.join('D:/phan_mem_ban_tru_cloud', 'quan_ly_phuong_tien.csv'), os.path.join('d:/OneDrive/Hô sơ cá nhan/Học AI', 'quan_ly_phuong_tien.csv')]:
                                    try:
                                        df_xe_all.to_csv(d_save, index=False, encoding='utf-8-sig')
                                    except Exception:
                                        pass
                                st.success(f"🎉 Đã cập nhật thành công thông tin xe {xe_chon_edit} ({edit_bs})!")
                                st.rerun()
            else:
                # Cá nhân chỉ được chỉnh sửa phương tiện của chính mình
                st.info("🔒 **Phân quyền cá nhân:** Bạn chỉ có quyền xem và chỉnh sửa thông tin phương tiện của **CHÍNH MÌNH**. Để chỉnh sửa thông tin phương tiện của người khác, bạn cần được Admin / Ban Giám Hiệu cấp quyền quản lý phương tiện.")
                u_name = u_curr.get("fullname", "")
                u_phone = str(u_curr.get("phone", "")).replace(".0", "").strip()
                u_ref = str(u_curr.get("ma_lien_ket", "")).strip()
                
                mask_my_xe = (df_xe_all['Họ và tên'] == u_name) | (df_xe_all['Mã xe'] == u_ref)
                if u_phone:
                    col_p = df_xe_all['SĐT Học sinh'].astype(str).str.replace(".0", "").str.strip()
                    mask_my_xe = mask_my_xe | col_p.isin([u_phone, u_phone.lstrip('0'), '0' + u_phone.lstrip('0')])
                
                my_xe_df = df_xe_all[mask_my_xe]
                if not my_xe_df.empty:
                    xe_my_row = my_xe_df.iloc[0]
                    with st.expander(f"🛵 **Chỉnh sửa phương tiện của chính bạn ({xe_my_row['Biển số xe']} - {xe_my_row['Họ và tên']}):**", expanded=True):
                        with st.form("form_edit_xe_ca_nhan"):
                            cme1, cme2 = st.columns(2)
                            with cme1:
                                my_bs = st.text_input("Biển số xe của bạn:", value=str(xe_my_row['Biển số xe']))
                                my_loai = st.selectbox("Loại xe:", ["Xe máy điện", "Xe đạp điện", "Xe máy <50cc", "Xe đạp"], index=["Xe máy điện", "Xe đạp điện", "Xe máy <50cc", "Xe đạp"].index(xe_my_row['Loại xe']) if xe_my_row['Loại xe'] in ["Xe máy điện", "Xe đạp điện", "Xe máy <50cc", "Xe đạp"] else 0)
                                my_mau = st.text_input("Màu xe / Nhãn hiệu:", value=str(xe_my_row['Màu xe']))
                            with cme2:
                                my_noigui = st.selectbox("Nơi gửi xe:", ["Nhà xe KTX Bán trú", "Nhà xe Học sinh Khu A", "Nhà xe Học sinh Khu B"], index=0)
                                my_sdt = st.text_input("Số điện thoại liên hệ:", value=str(xe_my_row['SĐT Học sinh']))
                            
                            if st.form_submit_button("💾 LƯU THAY ĐỔI XE CỦA BẠN", type="primary", use_container_width=True):
                                idx_my_xe = xe_my_row.name
                                df_xe_all.loc[idx_my_xe, 'Biển số xe'] = my_bs.strip()
                                df_xe_all.loc[idx_my_xe, 'Loại xe'] = my_loai
                                df_xe_all.loc[idx_my_xe, 'Màu xe'] = my_mau.strip()
                                df_xe_all.loc[idx_my_xe, 'Nơi gửi xe'] = my_noigui
                                df_xe_all.loc[idx_my_xe, 'SĐT Học sinh'] = my_sdt.strip()
                                
                                for d_save in [f_xe, os.path.join(BASE_DIR, 'quan_ly_phuong_tien.csv'), os.path.join('D:/phan_mem_ban_tru_cloud', 'quan_ly_phuong_tien.csv'), os.path.join('d:/OneDrive/Hô sơ cá nhan/Học AI', 'quan_ly_phuong_tien.csv')]:
                                    try:
                                        df_xe_all.to_csv(d_save, index=False, encoding='utf-8-sig')
                                    except Exception:
                                        pass
                                st.success(f"🎉 Đã cập nhật thành công thông tin xe của bạn ({my_bs})!")
                                st.rerun()
                else:
                    st.info("💡 Bạn chưa có phương tiện nào liên kết với tài khoản này. Bạn có thể đăng ký tại mục **'Xe của tôi'** trong menu tài khoản cá nhân ở thanh bên trái!")

        # -------------------------------------------------------------
        # 2. QUÉT MÃ QR & XỬ LÝ VI PHẠM (CHUYỂN THẲNG SANG ĐTN)
        # -------------------------------------------------------------
        with sub_xe2:
            st.markdown("#### 🔍 Tra Cứu Thẻ Xe, Quét Mã QR & Xử Lý Vi Phạm")
            st.caption("Đội Cờ đỏ hoặc Thầy Cô kiểm tra phương tiện tại cổng trường hoặc bãi gửi xe.")

            c_tra1, c_tra2 = st.columns([1.5, 1])
            with c_tra1:
                tim_quet = st.text_input("📷 Quét mã QR / Nhập Biển số, Mã xe, Tên HS để tra cứu nhanh:", placeholder="VD: 24-AA 214.50, XE-001, Thanh Thảo, 0971...", key="tim_nhanh_xe_st2")
            with c_tra2:
                loc_lop_tra = st.selectbox("Lọc danh sách theo lớp:", ["Tất cả các lớp"] + sorted(list(df_xe_all['Lớp'].unique())), key="loc_lop_tra_st2")

            df_pool = df_xe_all.copy()
            if loc_lop_tra != "Tất cả các lớp":
                df_pool = df_pool[df_pool['Lớp'] == loc_lop_tra]
            if tim_quet.strip():
                kw = tim_quet.strip()
                df_pool = df_pool[
                    df_pool['Biển số xe'].astype(str).str.contains(kw, case=False, na=False) |
                    df_pool['Mã xe'].astype(str).str.contains(kw, case=False, na=False) |
                    df_pool['Họ và tên'].astype(str).str.contains(kw, case=False, na=False) |
                    df_pool['SĐT Học sinh'].astype(str).str.contains(kw, na=False)
                ]

            ds_tim_xe = [f"{r['Mã xe']} - {r['Biển số xe']} - {r['Họ và tên']} ({r['Lớp']})" for idx, r in df_pool.iterrows()]
            if not ds_tim_xe:
                st.warning("⚠️ Không tìm thấy phương tiện nào khớp với từ khóa tìm kiếm. Hiển thị toàn bộ danh sách để bạn chọn:")
                ds_tim_xe = [f"{r['Mã xe']} - {r['Biển số xe']} - {r['Họ và tên']} ({r['Lớp']})" for idx, r in df_xe_all.iterrows()]
                
            if not ds_tim_xe:
                st.info("💡 Chưa có dữ liệu phương tiện nào để hiển thị.")
                row_xe_tra = None
            else:
                xe_lookup = st.selectbox("Chọn xe cần tra cứu / lập biên bản vi phạm:", ds_tim_xe, index=0)
                if not xe_lookup and len(ds_tim_xe) > 0:
                    xe_lookup = ds_tim_xe[0]
                xe_lookup_str = str(xe_lookup or "").strip()
                ma_xe_tra = xe_lookup_str.split(" - ")[0].strip() if " - " in xe_lookup_str else xe_lookup_str
                df_match = df_xe_all[df_xe_all['Mã xe'] == ma_xe_tra]
                row_xe_tra = df_match.iloc[0] if not df_match.empty else (df_xe_all.iloc[0] if not df_xe_all.empty else None)

            if row_xe_tra is not None:
                mo_ta_mau_tra = lay_mo_ta_mau_xe(row_xe_tra)
                sdt_hs_tra = dinh_dang_sdt(row_xe_tra.get('SĐT Học sinh', ''))
                sdt_ph_tra = dinh_dang_sdt(row_xe_tra.get('SĐT Phụ huynh', ''))
                sdt_gv_tra = dinh_dang_sdt(row_xe_tra.get('SĐT GVCN', ''))
                ten_ph_tra = str(row_xe_tra.get('Họ tên Phụ huynh', 'Chưa cập nhật')).strip()
                if not ten_ph_tra or ten_ph_tra.lower() == 'nan':
                    ten_ph_tra = "Chưa cập nhật"
                text_qr = tao_noi_dung_qr_xe(row_xe_tra)
                qr_img_data = tao_anh_qr_base64(text_qr)
    
                c_q1, c_q2 = st.columns([1, 1.3])
                with c_q1:
                    st.markdown(f"""
                        <div style='background:white; border:2px solid #059669; border-radius:12px; padding:15px; text-align:center;'>
                            <div style='background:#059669; color:white; font-weight:800; font-size:12px; padding:4px 8px; border-radius:6px; margin-bottom:8px;'>
                                🏫 TRƯỜNG THPT SỐ 2 BẢO YÊN
                            </div>
                            <h4 style='color:#065F46; margin:0;'>TEM MÃ QR ĐỊNH DANH XE</h4>
                            <p style='color:#4B5563; font-size:12px; margin:4px 0 8px 0;'>Dán tại yếm xe hoặc chắn bùn</p>
                            <img src="{qr_img_data}" width="180" style="border:1px solid #E5E7EB; border-radius:8px; margin:5px 0;">
                            <p style='font-size:18px; font-weight:900; color:#1E3A8A; margin:6px 0 2px 0;'>{row_xe_tra['Biển số xe']}</p>
                            <p style='font-size:14px; font-weight:bold; color:#111827; margin:0;'>{row_xe_tra['Họ và tên']} - Lớp {row_xe_tra['Lớp']}</p>
                            <span style='background:#10B981; color:white; padding:3px 10px; border-radius:12px; font-size:12px; display:inline-block; margin-top:6px;'>{row_xe_tra['Loại xe']} • {mo_ta_mau_tra}</span>
                        </div>
                    """, unsafe_allow_html=True)
    
                with c_q2:
                    st.markdown(f"""
                        <div style='background:#F0FDF4; border:2px solid #BBF7D0; border-radius:12px; padding:16px;'>
                            <h4 style='color:#166534; margin:0;'>🏷️ THẺ THÔNG TIN PHƯƠNG TIỆN</h4>
                            <p style='color:#059669; font-size:12px; margin:2px 0 8px 0;'>Đầy đủ dữ liệu quản lý nề nếp & an toàn giao thông</p>
                            <hr style='margin:8px 0;'>
                            <p>🏫 <b>Tên trường:</b> <span style='color:#065F46; font-weight:bold;'>Trường THPT số 2 Bảo Yên</span></p>
                            <p>👤 <b>Họ tên học sinh:</b> <span style='color:#1E3A8A; font-size:16px; font-weight:bold;'>{row_xe_tra['Họ và tên']}</span> (Lớp <b>{row_xe_tra['Lớp']}</b>)</p>
                            <p>📱 <b>Số điện thoại HS:</b> <a href='tel:{sdt_hs_tra}' style='font-weight:bold; color:#2563EB;'>{sdt_hs_tra}</a></p>
                            <p>🛵 <b>Biển số xe:</b> <code style='font-size:15px; font-weight:bold; color:#1E3A8A;'>{row_xe_tra['Biển số xe']}</code> | <b>Mã xe:</b> <code>{row_xe_tra['Mã xe']}</code></p>
                            <p>🏷️ <b>Loại xe:</b> <span style='font-weight:bold;'>{row_xe_tra['Loại xe']}</span></p>
                            <p>🎨 <b>Màu xe (theo mô tả):</b> <span style='font-weight:bold; color:#92400E;'>{mo_ta_mau_tra}</span></p>
                            <p>🏢 <b>Nơi gửi xe:</b> {row_xe_tra['Nơi gửi xe']}</p>
                            <hr style='margin:8px 0;'>
                            <p>👨‍👩‍👧 <b>Họ tên Phụ huynh:</b> <span style='font-weight:bold;'>{ten_ph_tra}</span></p>
                            <p>📞 <b>Số điện thoại PH:</b> <a href='tel:{sdt_ph_tra}' style='font-weight:bold; color:#059669;'>{sdt_ph_tra}</a></p>
                            <p>👨‍🏫 <b>GVCN:</b> {row_xe_tra['GVCN']} - 📞 <a href='tel:{sdt_gv_tra}'>{sdt_gv_tra}</a></p>
                            <p>📍 <b>Địa chỉ:</b> {row_xe_tra['Địa chỉ']}</p>
                            <p>⚠️ <b>Lịch sử vi phạm:</b> <span style='color:red; font-weight:bold;'>{row_xe_tra['Số lần vi phạm']} lần</span></p>
                        </div>
                    """, unsafe_allow_html=True)
    
                    if la_quan_tri_xe:
                        st.markdown("##### 🚨 Ghi nhận lỗi vi phạm & Chuyển trừ điểm thi đua ĐTN:")
                        with st.form("form_lap_bien_ban_vp"):
                            loi_vp = st.selectbox("Chọn lỗi vi phạm an toàn giao thông / nề nếp:", [
                                "Không đội mũ bảo hiểm (-5đ)",
                                "Đi xe máy phân khối lớn (>50cc) khi chưa đủ tuổi (-20đ)",
                                "Chở quá số người quy định (-5đ)",
                                "Đi xe dàn hàng ngang / Lạng lách (-10đ)",
                                "Không có gương chiếu hậu (-2đ)",
                                "Gửi xe sai nơi quy định / Không dán tem xe (-3đ)",
                                "Vi phạm trật tự an toàn giao thông khác (-5đ)"
                            ])
                            ghi_chu_loi = st.text_input("Ghi chú chi tiết (thời điểm, địa điểm vi phạm):", placeholder="VD: Không đội mũ bảo hiểm tại cổng trường lúc 07:10 sáng...")
                        
                            btn_tru_diem = st.form_submit_button("🚨 XÁC NHẬN VI PHẠM & TRỪ ĐIỂM THI ĐUA LỚP", type="primary", use_container_width=True)
                            if btn_tru_diem:
                                # 1. Trừ điểm thi đua ĐTN của lớp đó
                                diem_tru_val = 5
                                if "(-20đ)" in loi_vp:
                                    diem_tru_val = 20
                                elif "(-10đ)" in loi_vp:
                                    diem_tru_val = 10
                                elif "(-3đ)" in loi_vp:
                                    diem_tru_val = 3
                                elif "(-2đ)" in loi_vp:
                                    diem_tru_val = 2
                                
                                lop_vp = row_xe_tra['Lớp']
                                if os.path.exists(f_dtn_td):
                                    df_td_curr = pd.read_csv(f_dtn_td, encoding='utf-8-sig').fillna("")
                                    idx_lop_match = df_td_curr[df_td_curr['Chi đoàn'] == lop_vp].index
                                    if not idx_lop_match.empty:
                                        i_l = idx_lop_match[0]
                                        curr_tru = int(pd.to_numeric(df_td_curr.loc[i_l, 'Điểm trừ'], errors='coerce') or 0)
                                        curr_tong = int(pd.to_numeric(df_td_curr.loc[i_l, 'Tổng điểm'], errors='coerce') or 100)
                                    
                                        df_td_curr.loc[i_l, 'Điểm trừ'] = curr_tru + diem_tru_val
                                        df_td_curr.loc[i_l, 'Tổng điểm'] = curr_tong - diem_tru_val
                                        df_td_curr.loc[i_l, 'Ghi chú'] = str(df_td_curr.loc[i_l, 'Ghi chú']) + f"; Trừ {diem_tru_val}đ lỗi xe: {row_xe_tra['Họ và tên']} ({row_xe_tra['Biển số xe']})"
                                        df_td_curr.to_csv(f_dtn_td, index=False, encoding='utf-8-sig')
    
                                # 2. Tăng số lần vi phạm của xe
                                match_idxs = df_xe_all[df_xe_all['Mã xe'] == ma_xe_tra].index
                                if not match_idxs.empty:
                                    idx_xe_vp = match_idxs[0]
                                    cur_lan = int(pd.to_numeric(df_xe_all.loc[idx_xe_vp, 'Số lần vi phạm'], errors='coerce') or 0)
                                    df_xe_all.loc[idx_xe_vp, 'Số lần vi phạm'] = cur_lan + 1
                                    df_xe_all.loc[idx_xe_vp, 'Tình trạng'] = 'Nhắc nhở nề nếp'
                                    df_xe_all.to_csv(f_xe, index=False, encoding='utf-8-sig')
    
                                # 3. Ghi vào lịch sử vi phạm
                                df_vp_new = pd.DataFrame([{
                                    'Ngày': date.today().strftime('%d/%m/%Y'),
                                    'Mã xe': ma_xe_tra,
                                    'Họ và tên': row_xe_tra['Họ và tên'],
                                    'Lớp': lop_vp,
                                    'Biển số xe': row_xe_tra['Biển số xe'],
                                    'Lỗi vi phạm': loi_vp,
                                    'Điểm trừ': diem_tru_val,
                                    'Người lập biên bản': u_curr.get('fullname', 'Đội Cờ đỏ'),
                                    'Trạng thái': 'Đã trừ điểm ĐTN'
                                }])
                                df_vp_all = pd.concat([pd.read_csv(f_vp, encoding='utf-8-sig'), df_vp_new], ignore_index=True) if os.path.exists(f_vp) else df_vp_new
                                df_vp_all.to_csv(f_vp, index=False, encoding='utf-8-sig')
    
                                st.success(f"🎉 Đã lập biên bản thành công! Đã tự động trừ {diem_tru_val} điểm thi đua nề nếp của Chi đoàn {lop_vp}.")
                                st.rerun()
                    else:
                        st.info("ℹ️ **Phân quyền:** Chức năng lập biên bản vi phạm và trừ điểm thi đua chỉ dành cho Đội Cờ Đỏ và Ban Chấp Hành Đoàn Trường. Học sinh và phụ huynh xem thẻ tra cứu ở chế độ chỉ xem.")
            else:
                st.info("💡 Chưa có thông tin phương tiện để hiển thị chi tiết hoặc lập biên bản.")

        # -------------------------------------------------------------
        # 3. CẤP & IN MÃ QR ĐỒNG LOẠT
        with sub_xe3:
            if is_ph_hs:
                st.markdown("#### 🖨️ In Tem Mã QR Xe Của Chính Bạn (Khổ Tem Decal Cá Nhân)")
                st.caption("Mã QR định danh dán lên yếm xe hoặc chắn bùn để ra vào cổng trường và điểm danh gửi xe an toàn.")
                
                u_name = u_curr.get("fullname", "")
                u_ref = str(u_curr.get("ma_lien_ket", "")).strip()
                u_phone = str(u_curr.get("phone", "")).replace(".0", "").strip()
                
                mask_my_xe = (df_xe_all['Họ và tên'].astype(str).str.strip().str.lower() == u_name.strip().lower()) | (df_xe_all['Mã xe'].astype(str).str.strip() == u_ref) | (df_xe_all['Biển số xe'].astype(str).str.strip() == u_ref)
                if u_phone:
                    col_p = df_xe_all['SĐT Học sinh'].astype(str).str.replace(".0", "").str.strip()
                    mask_my_xe = mask_my_xe | col_p.isin([u_phone, u_phone.lstrip('0'), '0' + u_phone.lstrip('0')])
                my_xe_df = df_xe_all[mask_my_xe]
                
                if not my_xe_df.empty:
                    r_my = my_xe_df.iloc[0]
                    c_ptem1, c_ptem2 = st.columns([1, 1.4])
                    with c_ptem1:
                        txt_my_qr = tao_noi_dung_qr_xe(r_my)
                        img_my_qr = tao_anh_qr_base64(txt_my_qr)
                        mo_ta_my = lay_mo_ta_mau_xe(r_my)
                        st.markdown(f"""
                            <div style='border:2px solid #059669; border-radius:12px; padding:15px; background:white; text-align:center;'>
                                <div style='background:#059669; color:white; font-weight:800; font-size:12px; padding:4px 8px; border-radius:6px; margin-bottom:8px;'>
                                    TRƯỜNG THPT SỐ 2 BẢO YÊN
                                </div>
                                <h4 style='color:#065F46; margin:0;'>TEM MÃ QR ĐỊNH DANH XE</h4>
                                <img src="{img_my_qr}" width="180" style="margin:8px auto; display:block; border:1px solid #E5E7EB; border-radius:8px;">
                                <p style='font-size:18px; font-weight:900; color:#1E3A8A; margin:4px 0;'>{r_my['Biển số xe']}</p>
                                <p style='font-size:14px; font-weight:bold; margin:0;'>{r_my['Họ và tên']} - Lớp {r_my['Lớp']}</p>
                                <p style='font-size:12px; color:#4B5563; margin:4px 0;'>{r_my['Loại xe']} • {mo_ta_my}</p>
                            </div>
                        """, unsafe_allow_html=True)
                    with c_ptem2:
                        st.markdown(f"##### 🖨️ **Tải Mẫu In Tem Decal Cho Xe {r_my['Biển số xe']}:**")
                        html_my_single = tao_html_in_tem_qr(my_xe_df.head(1), f"Xe Cá Nhân: {r_my['Họ và tên']}")
                        st.download_button(
                            "🖨️ BẤM VÀO ĐÂY ĐỂ TẢI FILE IN TEM MÃ QR XE CỦA BẠN",
                            data=html_my_single.encode('utf-8'),
                            file_name=f"Tem_QR_Xe_{r_my['Biển số xe']}.html",
                            mime="text/html",
                            type="primary",
                            use_container_width=True
                        )
                        st.caption("Sau khi tải file về, mở file bằng trình duyệt và bấm **Ctrl + P** để in trực tiếp tem ra máy in decal.")
                        st.info("ℹ️ **Lưu ý phân quyền:** Học sinh và Phụ huynh chỉ có quyền in tem mã QR cho phương tiện của **CHÍNH MÌNH**. Để xuất danh sách hoặc in tem hàng loạt cho học sinh khác, bạn cần được Admin / Ban Giám Hiệu cấp quyền quản lý phương tiện.")
                else:
                    st.info("💡 Bạn chưa có phương tiện liên kết với tài khoản này. Vui lòng đăng ký tại mục **'Xe của tôi'** ở thanh bên trái.")
            else:
            
                st.markdown("#### 🖨️ Cấp Mã QR & In Tem Xe Đồng Loạt Toàn Trường")
                st.caption("Hệ thống tự động sinh mã QR cho toàn bộ phương tiện đã đăng ký để nhà trường in tem decal dán lên xe học sinh.")

                st.markdown("#### 🖨️ Thiết Kế Biểu Mẫu, Xem Trước & Xuất File In Tem Mã QR Xe")
                st.caption("Hệ thống tự động sinh mã QR đầy đủ thông tin, hỗ trợ xuất file in tem decal / A4 chuyên nghiệp theo Lớp, theo Khối hoặc Toàn trường. Xem tối đa 100 mã QR trực tiếp trên màn hình.")

                # Bộ lọc phạm vi: Theo Lớp, Theo Khối, Toàn trường
                c_scope1, c_scope2, c_scope3 = st.columns([1.2, 1.5, 1.3])
                with c_scope1:
                    pham_vi_in = st.radio("Chọn phạm vi in tem:", ["🏫 Theo Lớp", "🏛️ Theo Khối", "🌐 Toàn trường"], horizontal=True, key="rad_pv_in")
            
                with c_scope2:
                    if pham_vi_in == "🏫 Theo Lớp":
                        ds_lop_in = sorted(list(df_xe_all['Lớp'].unique())) if not df_xe_all.empty else []
                        chon_lop_in = st.selectbox("Chọn lớp in tem xe:", ds_lop_in, key="sel_lop_in_tem")
                        df_in_xe = df_xe_all[df_xe_all['Lớp'] == chon_lop_in].copy()
                        tieu_de_pv = f"Lớp {chon_lop_in}"
                        file_suffix = f"Lop_{chon_lop_in}"
                    elif pham_vi_in == "🏛️ Theo Khối":
                        chon_khoi_in = st.selectbox("Chọn khối lớp in tem xe:", ["Khối 10", "Khối 11", "Khối 12"], key="sel_khoi_in_tem")
                        k_prefix = chon_khoi_in.replace("Khối ", "")
                        df_in_xe = df_xe_all[df_xe_all['Lớp'].astype(str).str.startswith(k_prefix)].copy()
                        tieu_de_pv = f"{chon_khoi_in} ({df_in_xe['Lớp'].nunique()} lớp - {len(df_in_xe)} xe)"
                        file_suffix = f"Khoi_{k_prefix}"
                    else:
                        df_in_xe = df_xe_all.copy()
                        tieu_de_pv = f"Toàn Trường (21 Lớp - {len(df_in_xe)} Xe)"
                        file_suffix = "Toan_Truong"

                with c_scope3:
                    loc_loai_in = st.selectbox("Lọc theo loại xe:", ["Tất cả loại xe", "Xe máy điện", "Xe đạp điện", "Xe máy <50cc", "Xe đạp"], key="sel_loai_in")
                    if loc_loai_in != "Tất cả loại xe":
                        df_in_xe = df_in_xe[df_in_xe['Loại xe'] == loc_loai_in]

                # Thống kê nhanh phạm vi in
                so_tem_in = len(df_in_xe)
                so_trang_a4 = max(1, (so_tem_in + 7) // 8) # 8 tem / trang A4
            
                c_m_in1, c_m_in2, c_m_in3, c_m_in4 = st.columns(4)
                c_m_in1.metric("🛵 Tổng số tem cần in", f"{so_tem_in} Tem", tieu_de_pv)
                c_m_in2.metric("📄 Khổ giấy dự kiến", f"{so_trang_a4} Trang A4", "8 tem/trang (Decal 2 cột)")
                c_m_in3.metric("🏫 Số lớp trong phạm vi", f"{df_in_xe['Lớp'].nunique()} Lớp")
                c_m_in4.metric("⚡ Phương tiện điện", f"{len(df_in_xe[df_in_xe['Loại xe'].astype(str).str.contains('điện', case=False, na=False)])} Xe")

                st.markdown("---")
            
                # NÚT XUẤT FILE IN & TẢI DỮ LIỆU
                c_btn_in1, c_btn_in2 = st.columns([1.5, 1])
                with c_btn_in1:
                    st.markdown("##### 🖨️ **1. Xuất Biểu Mẫu In Tem Mã QR (HTML Chuẩn A4 / Decal):**")
                    html_tem_xe = tao_html_in_tem_qr(df_in_xe, tieu_de_pv)
                    st.download_button(
                        label=f"🖨️ TẢI FILE IN TEM MÃ QR ({so_tem_in} TEM) - KHỔ A4 DECAL",
                        data=html_tem_xe.encode('utf-8'),
                        file_name=f"Tem_Ma_QR_Xe_{file_suffix}_THPT2_BaoYen.html",
                        mime="text/html",
                        type="primary",
                        use_container_width=True
                    )
                    st.caption("💡 Mở file HTML vừa tải bằng trình duyệt (Chrome, Edge, Cốc Cốc) và bấm **In (Ctrl + P)** để in trực tiếp tem ra máy in decal.")
                
                with c_btn_in2:
                    st.markdown("##### 📥 **2. Xuất Danh Sách Phương Tiện Excel / CSV:**")
                    csv_in_bytes = df_in_xe.to_csv(index=False, encoding='utf-8-sig').encode('utf-8-sig')
                    st.download_button(
                        label=f"💾 TẢI DANH SÁCH {so_tem_in} XE (.CSV / EXCEL)",
                        data=csv_in_bytes,
                        file_name=f"Danh_Sach_Xe_{file_suffix}_THPT2_BaoYen.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
                    st.caption("File chứa đầy đủ số điện thoại HS, PH, GVCN, loại xe, màu xe, nơi gửi.")

                st.markdown("---")

                # XEM TRƯỚC MÃ QR TRÊN MÀN HÌNH - HIỂN THỊ TỐI ĐA 100 MÃ
                st.markdown("#### 👀 **Xem Trước Tem Mã QR Trực Tiếp Trên Màn Hình (Tối Đa 100 Mã):**")
            
                c_pg1, c_pg2 = st.columns([1.2, 2])
                with c_pg1:
                    limit_view = st.selectbox("Số lượng mã QR hiển thị mỗi trang:", [30, 60, 100], index=2, key="sel_limit_view_qr")
            
                total_pages = max(1, (so_tem_in + limit_view - 1) // limit_view)
                with c_pg2:
                    page_view = st.selectbox(
                        f"Chọn trang hiển thị (Tối đa {limit_view} mã/trang - Tổng {total_pages} trang):",
                        list(range(1, total_pages + 1)),
                        format_func=lambda x: f"Trang {x}/{total_pages} (Từ tem #{(x-1)*limit_view + 1} đến tem #{min(x*limit_view, so_tem_in)})",
                        key="sel_page_view_qr"
                    )

                start_i = (page_view - 1) * limit_view
                end_i = min(start_i + limit_view, so_tem_in)
                df_page_view = df_in_xe.iloc[start_i:end_i]

                st.info(f"Đang hiển thị **{len(df_page_view)} mã QR** (từ xe thứ {start_i + 1} đến {end_i} trong tổng số {so_tem_in} xe của phạm vi **{tieu_de_pv}**). Bạn có thể quét trực tiếp bằng camera điện thoại hoặc Zalo ngay trên màn hình!")

                # Lưới hiển thị tem xe 3 cột đẹp mắt
                cols_grid = st.columns(3)
                for idx_local, (idx_row, r) in enumerate(df_page_view.iterrows()):
                    with cols_grid[idx_local % 3]:
                        txt_qr_item = tao_noi_dung_qr_xe(r)
                        img_qr_item = tao_anh_qr_base64(txt_qr_item)
                        mo_ta_mau_item = lay_mo_ta_mau_xe(r)
                        sdt_hs_item = dinh_dang_sdt(r.get('SĐT Học sinh', ''))
                        sdt_ph_item = dinh_dang_sdt(r.get('SĐT Phụ huynh', ''))
                        ten_ph_item = str(r.get('Họ tên Phụ huynh', 'Chưa cập nhật')).strip()
                        if not ten_ph_item or ten_ph_item.lower() == 'nan':
                            ten_ph_item = "Chưa cập nhật"
                        
                        st.markdown(f"""
                            <div style='border:2px solid #059669; border-radius:10px; padding:12px; margin-bottom:15px; background:white; box-shadow:0 2px 4px rgba(0,0,0,0.06); text-align:center;'>
                                <div style='background:#059669; color:white; font-weight:800; font-size:11.5px; padding:3px 6px; border-radius:4px; margin-bottom:6px;'>
                                    TRƯỜNG THPT SỐ 2 BẢO YÊN
                                </div>
                                <div style='display:flex; justify-content:space-between; font-size:12px; margin-bottom:4px;'>
                                    <span style='font-weight:bold; color:#065F46;'>Mã: {r['Mã xe']}</span>
                                    <span style='background:#D1FAE5; color:#065F46; font-weight:bold; padding:1px 6px; border-radius:4px;'>Lớp {r['Lớp']}</span>
                                </div>
                                <img src="{img_qr_item}" width="140" style="margin:4px auto; display:block; border:1px solid #E5E7EB; border-radius:6px;">
                                <div style='margin-top:4px;'>
                                    <p style='margin:0; font-weight:900; color:#1E3A8A; font-size:16px;'>{r['Biển số xe']}</p>
                                    <p style='margin:2px 0; font-weight:bold; color:#111827; font-size:13px;'>{r['Họ và tên']}</p>
                                    <p style='margin:1px 0; font-size:11.5px; color:#4B5563;'>📱 SĐT HS: <b>{sdt_hs_item}</b></p>
                                    <p style='margin:1px 0; font-size:11.5px; color:#4B5563;'>🛵 {r['Loại xe']} • 🎨 {mo_ta_mau_item}</p>
                                    <p style='margin:1px 0; font-size:11px; color:#6B7280;'>👨‍👩‍👧 PH: {ten_ph_item} ({sdt_ph_item})</p>
                                </div>
                            </div>
                        """, unsafe_allow_html=True)

        
        # -------------------------------------------------------------
        # 4. NHẬP NHANH PHƯƠNG TIỆN TỪ EXCEL
        # -------------------------------------------------------------
        with sub_xe4:
            st.markdown("#### 📂 Nhập Danh Sách Sử Dụng Phương Tiện Nhanh Từ File Excel")
            st.caption("Cho phép Đoàn trường hoặc giáo viên nhập hàng loạt hàng trăm xe từ file Excel của trường.")

            df_mau_xe = pd.DataFrame([
                {'Mã xe': 'XE-001', 'Họ và tên': 'Bàn Hải Phong', 'Lớp': '10A1', 'SĐT Học sinh': '0971909148', 'Loại xe': 'Xe máy điện', 'Biển số xe': '24MD1-100.10', 'Màu xe': 'Đỏ đen', 'Nơi gửi xe': 'Nhà xe KTX Bán trú', 'GVCN': 'Thầy/Cô GVCN 10A1', 'SĐT GVCN': '0988123001', 'Họ tên Phụ huynh': 'Bàn Văn Trịnh', 'SĐT Phụ huynh': '0867106916', 'Địa chỉ': 'Khe Bàn, Bảo Hà', 'Tình trạng': 'Đủ điều kiện lưu hành', 'Số lần vi phạm': 0, 'Ghi chú': ''}
            ])
            csv_mau_xe = df_mau_xe.to_csv(index=False, encoding='utf-8-sig').encode('utf-8-sig')
            st.download_button("📥 Tải Biểu Mẫu Excel Phương Tiện Mẫu", data=csv_mau_xe, file_name="Mau_Danh_Sach_Phuong_Tien_THPT2_BaoYen.csv", mime="text/csv")

            if not la_quan_tri_xe:
                st.warning("🔒 **Giới hạn phân quyền:** Chức năng nạp danh sách xe hàng loạt từ file Excel chỉ dành riêng cho Admin, Đoàn Trường và Quản trị viên được phân quyền.")
            else:
                uploaded_xe_file = st.file_uploader("Chọn file Excel / CSV phương tiện:", type=['xlsx', 'xls', 'csv'], key="up_xe_excel")
                if uploaded_xe_file is not None:
                    try:
                        if uploaded_xe_file.name.endswith('.csv'):
                            df_imp_xe = pd.read_csv(uploaded_xe_file, encoding='utf-8-sig')
                        else:
                            df_imp_xe = pd.read_excel(uploaded_xe_file)
                        
                        st.markdown("##### 👀 Xem trước danh sách xe từ file:")
                        st.dataframe(df_imp_xe, use_container_width=True, hide_index=True)
                        
                        if st.button("🚀 XÁC NHẬN NẠP TOÀN BỘ PHƯƠNG TIỆN VÀO HỆ THỐNG", type="primary", use_container_width=True):
                            df_imp_xe.to_csv(f_xe, index=False, encoding='utf-8-sig')
                            for d_sync in [BASE_DIR, 'D:/phan_mem_ban_tru_cloud', 'd:/OneDrive/Hô sơ cá nhan/Học AI']:
                                p_sync = os.path.join(d_sync, 'quan_ly_phuong_tien.csv')
                                try:
                                    df_imp_xe.to_csv(p_sync, index=False, encoding='utf-8-sig')
                                except Exception:
                                    pass
                            st.success(f"🎉 Nạp thành công {len(df_imp_xe)} phương tiện vào hệ thống!")
                            st.rerun()
                    except Exception as e:
                        st.error(f"Lỗi đọc file: {str(e)}")

    # -------------------------------------------------------------------------
    # TAB 4: PHONG TRÀO ĐOÀN & SỔ ĐOÀN VIÊN
    # -------------------------------------------------------------------------
    with tab_phong_trao_dv:
        sub_pt, sub_dv = st.tabs([
            "🎪 Kế Hoạch Hoạt Động & Sự Kiện Thanh Niên",
            "🎗️ Quản Lý Đoàn Viên & Sổ Đoàn 21 Chi Đoàn"
        ])
        with sub_pt:
            st.subheader("🎪 Kế Hoạch Hoạt Động & Sự Kiện Thanh Niên")
            phong_trao_list = [
                {"Thời gian": "Tháng 10 - 11", "Tên hoạt động": "Hội thi làm Báo tường & Phong trào 'Hoa điểm tốt dâng Thầy Cô'", "Mục đích": "Chào mừng Ngày Nhà giáo Việt Nam 20/11", "Đơn vị thực hiện": "21 Chi đoàn toàn trường", "Trạng thái": "Đang diễn ra 🔥"},
                {"Thời gian": "Tháng 12", "Tên hoạt động": "Chiến dịch Tình nguyện Mùa Đông & Chăm sóc Nghĩa trang Liệt sĩ", "Mục đích": "Kỷ niệm ngày thành lập QĐND Việt Nam 22/12", "Đơn vị thực hiện": "BCH Đoàn trường & Đội TNV", "Trạng thái": "Sắp diễn ra"},
                {"Thời gian": "Tháng 01", "Tên hoạt động": "Chương trình 'Tết ấm tình thương' tặng quà học sinh khó khăn", "Mục đích": "Hỗ trợ học sinh nghèo vượt khó đón Tết", "Đơn vị thực hiện": "Đoàn trường & Quỹ Bán trú", "Trạng thái": "Kế hoạch"},
                {"Thời gian": "Tháng 03", "Tên hoạt động": "Tháng Thanh niên & Hội trại truyền thống 26/3", "Mục đích": "Kỷ niệm 96 năm Ngày thành lập Đoàn TNCS HCM", "Đơn vị thực hiện": "Toàn thể CB, ĐVTN toàn trường", "Trạng thái": "Trọng điểm ⭐"}
            ]
            st.dataframe(pd.DataFrame(phong_trao_list), use_container_width=True, hide_index=True)

        # =========================================================================
        # TAB 5: QUẢN LÝ PHƯƠNG TIỆN & MÃ QR XE (TÍNH NĂNG MỚI ĐẶC SẮC)
        with sub_dv:
            st.subheader("🎗️ Quản Lý Đoàn Viên & Sổ Đoàn 21 Chi Đoàn")
            if os.path.exists(f_dtn_dv):
                df_dv_curr = pd.read_csv(f_dtn_dv, encoding='utf-8-sig').fillna("")
                c_dv1, c_dv2, c_dv3 = st.columns(3)
                with c_dv1:
                    tong_hs = df_dv_curr['Tổng số HS'].sum() if 'Tổng số HS' in df_dv_curr.columns else 840
                    st.metric("👨‍🎓 Tổng học sinh", f"{tong_hs} Em")
                with c_dv2:
                    tong_dv = df_dv_curr['Số Đoàn viên'].sum() if 'Số Đoàn viên' in df_dv_curr.columns else 420
                    ty_le_dv = round((tong_dv / tong_hs) * 100, 1) if tong_hs > 0 else 0
                    st.metric("🎗️ Số lượng Đoàn viên", f"{tong_dv} ĐV", f"{ty_le_dv}% đoàn viên")
                with c_dv3:
                    tong_tnut = df_dv_curr['Thanh niên ưu tú'].sum() if 'Thanh niên ưu tú' in df_dv_curr.columns else 100
                    st.metric("🌟 Thanh niên ưu tú", f"{tong_tnut} Em", "Chờ kết nạp")

                st.markdown("---")
                st.dataframe(df_dv_curr, use_container_width=True, hide_index=True)

        # -------------------------------------------------------------------------
        # TAB 4: KẾ HOẠCH & PHONG TRÀO

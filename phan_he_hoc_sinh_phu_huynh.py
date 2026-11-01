# -*- coding: utf-8 -*-
"""
PHÂN HỆ CỔNG THÔNG TIN HỌC SINH & PHỤ HUYNH
Trường THPT số 2 Bảo Yên - Năm học chuẩn
Thực hiện chính xác 3 yêu cầu cốt lõi của Ban Giám Hiệu:
1. Quyền riêng tư (RBAC): Chỉ xem và chỉnh sửa thông tin của chính mình.
2. Học sinh Trưởng phòng: Chấm điểm thi đua phòng & Báo số lượng, tích vắng phòng theo 4 thời điểm trong ngày (kèm thời gian, lý do vắng).
3. Lớp trưởng & Bí thư: Chấm thi đua, báo vắng phòng KTX & Đánh giá học sinh vi phạm phương tiện.
"""

import os
import sys
import re
import urllib.parse
from datetime import datetime, date
import pandas as pd
import streamlit as st

def clean_phone_str(p):
    if not p or pd.isna(p):
        return ""
    s = str(p).replace(".0", "").strip()
    s = re.sub(r'\D', '', s)
    if s and not s.startswith("0") and len(s) == 9:
        s = "0" + s
    return s

def dong_bo_file_da_noi(df_data, file_paths):
    """Lưu dữ liệu và tự động đồng bộ sang tất cả các thư mục cloud và backup"""
    for fp in file_paths:
        try:
            folder = os.path.dirname(fp)
            if folder and not os.path.exists(folder):
                os.makedirs(folder, exist_ok=True)
            df_data.to_csv(fp, index=False, encoding='utf-8-sig')
        except Exception:
            pass

# =============================================================================
# 1. CỔNG DÀNH CHO PHỤ HUYNH HỌC SINH (CHỈ XEM & SỬA CON EM CỦA CHÍNH MÌNH)
# =============================================================================
def render_cong_phu_huynh(u_curr, df_current, ngay_lam_viec, BASE_DIR, FILE_DU_LIEU_THUC_TE, FILE_THI_DUA, FILE_KIEM_THUC, FILE_THUC_DON, FILE_XIN_VE, FILE_TAI_KHOAN):
    st.markdown("""
        <div style='background: linear-gradient(135deg, #7C3AED, #6D28D9); padding: 12px 18px; border-radius: 10px; color: white; margin-bottom: 12px;'>
            <h3 style='margin:0; font-size: 20px; color: white;'>👨‍👩‍👧 CỔNG THÔNG TIN PHỤ HUYNH BÁN TRÚ</h3>
            <p style='margin: 4px 0 0 0; opacity: 0.95; font-size: 13.5px;'>
                Theo dõi an toàn bữa ăn, giấc ngủ, học tập của con tại Ký túc xá • THPT số 2 Bảo Yên
            </p>
        </div>
    """, unsafe_allow_html=True)

    # 1.1. BẢO MẬT & KIỂM SOÁT QUYỀN RIÊNG TƯ (RBAC)
    ma_lk_curr = str(u_curr.get("ma_lien_ket", "")).strip()
    u_phone = clean_phone_str(u_curr.get("phone", "")).lstrip("0")
    
    row_con = None
    if ma_lk_curr and ma_lk_curr in df_current["Mã HS"].values:
        row_con = df_current[df_current["Mã HS"] == ma_lk_curr].iloc[0]
    elif u_phone:
        col_sdt_ph = df_current["SĐT Phụ huynh"].astype(str).str.replace(".0", "").str.strip().str.lstrip("0")
        match_ph = df_current[col_sdt_ph == u_phone]
        if not match_ph.empty:
            row_con = match_ph.iloc[0]

    if row_con is None:
        st.warning(f"⚠️ **Thông báo an toàn:** Tài khoản phụ huynh `{u_curr.get('username')}` chưa liên kết với hồ sơ học sinh bán trú nào. Để bảo mật dữ liệu học sinh toàn trường, quý phụ huynh vui lòng liên hệ Thầy Quản nhiệm KTX hoặc Ban Giám Hiệu để được hỗ trợ!")
        return

    con_em = str(row_con["Họ và tên"]).strip()
    st.success(f"👋 Kính chào Quý Phụ huynh em: **{con_em}** — Lớp: **{row_con['Lớp']}** — Phòng KTX: **{row_con['Phòng']}** (Giường: **{row_con['Giường']}**)")

    # 1.2. THẺ TỔNG QUAN TÌNH TRẠNG CỦA CON HÔM NAY
    c_ph1, c_ph2 = st.columns([1, 1])
    with c_ph1:
        st.markdown(f"""
        <div style="background:#F5F3FF; border-left:5px solid #7C3AED; padding:15px; border-radius:10px;">
            <h3 style="margin-top:0; color:#5B21B6;">🎓 {row_con['Họ và tên']}</h3>
            <p><b>Lớp:</b> {row_con['Lớp']} | <b>Phòng KTX:</b> <span style="font-size:16px; font-weight:bold; color:#7C3AED;">{row_con['Phòng']}</span> (Giường: {row_con['Giường']})</p>
            <p><b>Dãy nhà:</b> {row_con['Dãy nhà']} | <b>Chính sách NĐ 116:</b> {row_con['Chính sách NĐ116']}</p>
            <p><b>Quản nhiệm KTX trực:</b> Thầy Quản Nhiệm (📞 <a href="tel:0988123005" style="color:#7C3AED; font-weight:bold;">0988.123.005</a>)</p>
        </div>
        """, unsafe_allow_html=True)

    with c_ph2:
        an_trang_thai = "🟢 Đã vào ăn cơm trưa" if row_con.get("GĐ1: Ăn trưa", True) else "🔴 Vắng ăn trưa / Cắt cơm"
        nghi_trang_thai = "🟢 Có mặt tại phòng nghỉ" if row_con.get("GĐ2: Phòng nghỉ", True) else "🔴 Vắng mặt tại phòng"
        st.markdown(f"""
        <div style="background:#ECFDF5; border-left:5px solid #059669; padding:15px; border-radius:10px;">
            <h4 style="margin-top:0; color:#065F46;">📍 ĐIỂM DANH HÔM NAY ({ngay_lam_viec.strftime('%d/%m/%Y')}):</h4>
            <p>1. Bữa ăn trưa (GĐ1): <b>{an_trang_thai}</b></p>
            <p>2. Nghỉ trưa tại phòng (GĐ2): <b>{nghi_trang_thai}</b></p>
            <p>Trạng thái hiện tại: <span style="color:#2563EB; font-weight:bold;">{row_con['Trạng thái']}</span></p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # 1.3. CÁC TÁC NGHIỆP PHỤ HUYNH
    tab_ph_cat, tab_ph_ve, tab_ph_qr, tab_ph_td, tab_ph_edit = st.tabs([
        "🥣 BÁO CẮT CƠM (TRƯỚC 08:00)",
        "🚗 BÁO CON XIN VỀ / XUỐNG TRƯỜNG",
        "💳 ĐÓNG TIỀN ĂN QUA MÃ VIETQR",
        "🥗 THỰC ĐƠN BỮA ĂN CỦA CON",
        "👤 CHỈNH SỬA THÔNG TIN PHỤ HUYNH & HỌC SINH"
    ])

    with tab_ph_cat:
        st.markdown("#### 🥣 Báo Cắt Cơm Bán Trú Cho Con")
        st.info("⏰ **Quy định:** Quý phụ huynh vui lòng gửi thông báo cắt cơm **trước 08:00 sáng**. Nhà bếp sẽ giảm nấu đúng suất và bộ phận kế toán sẽ khấu trừ tiền ăn ngày hôm đó cho gia đình.")
        with st.form("form_ph_cat_com"):
            ngay_cat = st.date_input("Ngày xin cắt cơm:", date.today())
            bua_cat = st.selectbox("Bữa cắt:", ["Bữa trưa hôm nay", "Bữa tối hôm nay", "Cả ngày hôm nay", "Từ ngày mai"])
            ly_do_cat = st.text_input("Lý do cắt cơm:", "Gia đình có việc đón cháu về ăn cơm")
            btn_ph_cat = st.form_submit_button("📤 GỬI BÁO CÁO CẮT CƠM CHO NHÀ BẾP & QUẢN NHIỆM", type="primary")

            if btn_ph_cat:
                dong_cat_ph = {
                    "Thời gian": datetime.now().strftime("%d/%m/%Y %H:%M"),
                    "Mã HS": row_con.get("Mã HS", ""), "Họ và tên": con_em, "Lớp": row_con.get("Lớp", ""),
                    "Phòng": row_con.get("Phòng", ""), "Hình thức": f"Báo cắt cơm ({bua_cat})",
                    "Lý do": ly_do_cat, "Người đón / SĐT": u_curr.get("fullname", "Phụ huynh"),
                    "Người duyệt": "Chờ duyệt", "Trạng thái": "Chờ duyệt ⏳"
                }
                df_xv_cur = pd.read_csv(FILE_XIN_VE, encoding='utf-8-sig') if os.path.exists(FILE_XIN_VE) else pd.DataFrame()
                df_xv_cur = pd.concat([df_xv_cur, pd.DataFrame([dong_cat_ph])], ignore_index=True)
                df_xv_cur.to_csv(FILE_XIN_VE, index=False, encoding='utf-8-sig')

                st.success(f"✅ Đã gửi đơn báo cắt cơm cho cháu {con_em} ngày {ngay_cat.strftime('%d/%m/%Y')} thành công! Thầy Quản Nhiệm sẽ phê duyệt và báo nhà bếp khấu trừ ngay.")
                st.balloons()
                st.rerun()

    with tab_ph_ve:
        st.markdown("#### 🚗 Báo Xin Cho Con Về Nhà / Báo Đã Xuống Trường")
        c_v1, c_v2 = st.columns(2)
        with c_v1:
            st.markdown("##### 1. Xin Cho Con Về Nhà:")
            with st.form("form_ph_xin_ve"):
                nguoi_don = st.text_input("Họ tên người đón:", value=u_curr.get("fullname", ""))
                gio_don = st.text_input("Thời gian đón:", value=datetime.now().strftime("%H:%M ngày %d/%m/%Y"))
                ly_do_ve = st.selectbox("Lý do về:", ["Về cuối tuần", "Về nghỉ lễ", "Việc gia đình", "Ốm về nhà điều trị"])
                if st.form_submit_button("🏡 Xác Nhận Báo Đón Con Về", type="secondary"):
                    dong_xv = {
                        "Thời gian": datetime.now().strftime("%d/%m/%Y %H:%M"),
                        "Mã HS": row_con.get("Mã HS", ""), "Họ và tên": con_em, "Lớp": row_con.get("Lớp", ""),
                        "Phòng": row_con.get("Phòng", ""), "Hình thức": "Phụ huynh báo đón về",
                        "Lý do": f"{ly_do_ve} ({gio_don})", "Người đón / SĐT": f"{nguoi_don} ({u_curr.get('phone', '')})",
                        "Người duyệt": "Phụ huynh tự báo qua App", "Trạng thái": "Đã về nhà an toàn"
                    }
                    df_xv_old = pd.read_csv(FILE_XIN_VE, encoding='utf-8-sig') if os.path.exists(FILE_XIN_VE) else pd.DataFrame()
                    df_xv_new = pd.concat([df_xv_old, pd.DataFrame([dong_xv])], ignore_index=True)
                    df_xv_new.to_csv(FILE_XIN_VE, index=False, encoding='utf-8-sig')

                    # Cập nhật danh sách học sinh live
                    df_current.loc[df_current["Mã HS"] == row_con["Mã HS"], "Trạng thái"] = "Đã về nhà an toàn"
                    df_current.loc[df_current["Mã HS"] == row_con["Mã HS"], "GĐ1: Ăn trưa"] = False
                    df_current.loc[df_current["Mã HS"] == row_con["Mã HS"], "GĐ2: Phòng nghỉ"] = False
                    dong_bo_file_da_noi(df_current, [FILE_DU_LIEU_THUC_TE, "D:/danh_sach_hoc_sinh_thuc_te.csv", "D:/phan_mem_ban_tru_cloud/danh_sach_hoc_sinh_thuc_te.csv"])
                    st.success(f"✅ Đã gửi thông báo đến Thầy Quản Nhiệm: Gia đình đón cháu {con_em} lúc {gio_don}.")
                    st.rerun()

        with c_v2:
            st.markdown("##### 2. Báo Con Đã Xuống Trường An Toàn:")
            st.caption("Bấm nút dưới đây khi cháu đã đến trường để Ký túc xá bố trí suất cơm và chỗ ngủ:")
            if st.button("🎒 BÁO CHÁU ĐÃ LÊN ĐẾN TRƯỜNG AN TOÀN", type="primary", use_container_width=True):
                dong_xv = {
                    "Thời gian": datetime.now().strftime("%d/%m/%Y %H:%M"),
                    "Mã HS": row_con.get("Mã HS", ""), "Họ và tên": con_em, "Lớp": row_con.get("Lớp", ""),
                    "Phòng": row_con.get("Phòng", ""), "Hình thức": "Phụ huynh báo con xuống trường",
                    "Lý do": "Trở lại trường học tập", "Người đón / SĐT": u_curr.get('fullname', ''),
                    "Người duyệt": "Phụ huynh xác nhận qua App", "Trạng thái": "Tại trường"
                }
                df_xv_old = pd.read_csv(FILE_XIN_VE, encoding='utf-8-sig') if os.path.exists(FILE_XIN_VE) else pd.DataFrame()
                df_xv_new = pd.concat([df_xv_old, pd.DataFrame([dong_xv])], ignore_index=True)
                df_xv_new.to_csv(FILE_XIN_VE, index=False, encoding='utf-8-sig')

                df_current.loc[df_current["Mã HS"] == row_con["Mã HS"], "Trạng thái"] = "Tại trường"
                df_current.loc[df_current["Mã HS"] == row_con["Mã HS"], "GĐ1: Ăn trưa"] = True
                df_current.loc[df_current["Mã HS"] == row_con["Mã HS"], "GĐ2: Phòng nghỉ"] = True
                dong_bo_file_da_noi(df_current, [FILE_DU_LIEU_THUC_TE, "D:/danh_sach_hoc_sinh_thuc_te.csv", "D:/phan_mem_ban_tru_cloud/danh_sach_hoc_sinh_thuc_te.csv"])
                st.success(f"🎉 Cảm ơn quý phụ huynh đã thông báo. Quản nhiệm KTX đã tiếp nhận cháu {con_em} tại trường an toàn!")
                st.rerun()

    with tab_ph_qr:
        st.markdown("#### 💳 Nộp Tiền Bán Trú Qua Mã VietQR Ngân Hàng")
        tien_phai_dong = 21 * 30000
        st.markdown(f"Số tiền dự kiến đóng tháng này: <span style='font-size:22px;color:#DC2626;font-weight:bold;'>{tien_phai_dong:,.0f} VNĐ</span>", unsafe_allow_html=True)
        noi_dung_ck = f"THPT2BY {row_con['Mã HS']} {con_em} Tien ban tru"
        noi_dung_url = urllib.parse.quote(noi_dung_ck)
        vietqr_img_url = f"https://img.vietqr.io/image/agribank-8800205123456-compact2.png?amount={tien_phai_dong}&addInfo={noi_dung_url}&accountName=THPT%20SO%202%20BAO%20YEN"
        st.image(vietqr_img_url, width=300)
        st.caption("Quý phụ huynh mở app Ngân hàng (Agribank, BIDV, VietinBank...) quét mã QR để chuyển khoản nhanh, không cần gõ số tài khoản.")

    with tab_ph_td:
        st.markdown("#### 🥗 Thực Đơn Tuần Này Của Con Tại Nhà Ăn Trường")
        if os.path.exists(FILE_THUC_DON):
            df_td_v = pd.read_csv(FILE_THUC_DON, encoding='utf-8-sig')
            st.dataframe(df_td_v, use_container_width=True, hide_index=True)

    with tab_ph_edit:
        st.markdown("#### 👤 Chỉnh Sửa & Cập Nhật Hồ Sơ Của Quý Phụ Huynh")
        st.info("🔒 **Quyền riêng tư:** Quý phụ huynh chỉ có quyền xem và cập nhật thông tin của chính mình và con em mình. Thông tin sẽ được đồng bộ trực tiếp vào cơ sở dữ liệu nhà trường.")
        with st.form("form_edit_phuhuynh_profile"):
            c_e1, c_e2 = st.columns(2)
            with c_e1:
                ten_bo_moi = st.text_input("Họ tên Bố:", value=str(row_con.get("Họ tên Bố", "")).replace("nan", ""))
                ten_me_moi = st.text_input("Họ tên Mẹ:", value=str(row_con.get("Họ tên Mẹ", "")).replace("nan", ""))
                sdt_ph_moi = st.text_input("Số điện thoại Phụ huynh liên hệ:", value=clean_phone_str(row_con.get("SĐT Phụ huynh", "")))
            with c_e2:
                thon_moi = st.text_input("Thôn / Bản:", value=str(row_con.get("Thôn", "")).replace("nan", ""))
                xa_moi = st.text_input("Xã / Thị trấn:", value=str(row_con.get("Xã", "")).replace("nan", ""))
                pw_ph_moi = st.text_input("Đổi mật khẩu mới (bỏ trống nếu giữ nguyên):", type="password")

            if st.form_submit_button("💾 LƯU THAY ĐỔI THÔNG TIN HỒ SƠ", type="primary", use_container_width=True):
                idx_con = df_current[df_current["Mã HS"] == row_con["Mã HS"]].index[0]
                if ten_bo_moi.strip():
                    df_current.loc[idx_con, "Họ tên Bố"] = ten_bo_moi.strip()
                if ten_me_moi.strip():
                    df_current.loc[idx_con, "Họ tên Mẹ"] = ten_me_moi.strip()
                if sdt_ph_moi.strip():
                    df_current.loc[idx_con, "SĐT Phụ huynh"] = clean_phone_str(sdt_ph_moi)
                if thon_moi.strip():
                    df_current.loc[idx_con, "Thôn"] = thon_moi.strip()
                if xa_moi.strip():
                    df_current.loc[idx_con, "Xã"] = xa_moi.strip()

                dong_bo_file_da_noi(df_current, [FILE_DU_LIEU_THUC_TE, "D:/danh_sach_hoc_sinh_thuc_te.csv", "D:/phan_mem_ban_tru_cloud/danh_sach_hoc_sinh_thuc_te.csv"])

                # Cập nhật bảng tài khoản
                if os.path.exists(FILE_TAI_KHOAN):
                    df_tk = pd.read_csv(FILE_TAI_KHOAN, encoding='utf-8-sig', dtype=str).fillna("")
                    m_tk = (df_tk["Tên đăng nhập"] == u_curr.get("username", "")) | (df_tk["Mã liên kết"] == row_con["Mã HS"])
                    if m_tk.any():
                        if sdt_ph_moi.strip():
                            df_tk.loc[m_tk, "Số điện thoại"] = clean_phone_str(sdt_ph_moi)
                        if pw_ph_moi.strip() and len(pw_ph_moi.strip()) >= 4:
                            df_tk.loc[m_tk, "Mật khẩu"] = pw_ph_moi.strip()
                        dong_bo_file_da_noi(df_tk, [FILE_TAI_KHOAN, "D:/tai_khoan_nguoi_dung.csv", "D:/phan_mem_ban_tru_cloud/tai_khoan_nguoi_dung.csv"])

                st.success("🎉 Đã cập nhật thành công thông tin hồ sơ của gia đình! Cảm ơn quý phụ huynh.")
                st.rerun()


# =============================================================================
# 2. CỔNG DÀNH CHO HỌC SINH (RBAC + TRƯỞNG PHÒNG + BAN CÁN SỰ LỚP TRƯỞNG & BÍ THƯ)
# =============================================================================
def render_cong_hoc_sinh(u_curr, df_current, ngay_lam_viec, BASE_DIR, FILE_DU_LIEU_THUC_TE, FILE_THI_DUA, FILE_KIEM_THUC, FILE_THUC_DON, FILE_XIN_VE, FILE_TAI_KHOAN, THU_MUC_NAM_HOC, nam_hoc_hien_tai):
    st.markdown("""
        <div style='background: linear-gradient(135deg, #0284C7, #0369A1); padding: 12px 18px; border-radius: 10px; color: white; margin-bottom: 12px;'>
            <h3 style='margin:0; font-size: 20px; color: white;'>🎒 CỔNG THÔNG TIN HỌC SINH THPT SỐ 2 BẢO YÊN</h3>
            <p style='margin: 4px 0 0 0; opacity: 0.95; font-size: 13.5px;'>
                Hệ thống nề nếp, điểm danh bán trú, thi đua KTX & quản lý phương tiện an toàn giao thông
            </p>
        </div>
    """, unsafe_allow_html=True)

    # 2.1. BẢO MẬT & KIỂM SOÁT QUYỀN RIÊNG TƯ (RBAC)
    ma_lk_curr = str(u_curr.get("ma_lien_ket", "")).strip()
    u_username = str(u_curr.get("username", "")).strip().lower()
    u_phone = clean_phone_str(u_curr.get("phone", "")).lstrip("0")
    quyen_ql = str(u_curr.get("quyen_quan_ly", "")).strip()
    chuc_danh = str(u_curr.get("chuc_danh", "")).strip()

    # Nhận diện vai trò đặc nhiệm
    is_truong_phong = ("trưởng phòng" in chuc_danh.lower()) or ("trưởng phòng" in quyen_ql.lower())
    is_bcs = ("lớp trưởng" in chuc_danh.lower()) or ("bí thư" in chuc_danh.lower()) or ("ban cán sự" in quyen_ql.lower()) or ("cờ đỏ" in quyen_ql.lower())

    row_hs_self = None
    if ma_lk_curr and ma_lk_curr in df_current["Mã HS"].values:
        row_hs_self = df_current[df_current["Mã HS"] == ma_lk_curr].iloc[0]
    elif u_username:
        # Thử tìm theo mã HS không dấu gạch
        col_mhs_clean = df_current["Mã HS"].astype(str).str.lower().str.replace("-", "")
        m_u = df_current[col_mhs_clean == u_username]
        if not m_u.empty:
            row_hs_self = m_u.iloc[0]
        elif u_phone:
            col_sdt_hs = df_current["SĐT Học sinh"].astype(str).str.replace(".0", "").str.strip().str.lstrip("0")
            m_p = df_current[col_sdt_hs == u_phone]
            if not m_p.empty:
                row_hs_self = m_p.iloc[0]

    # Nếu vẫn chưa tìm thấy trong bán trú (ví dụ tài khoản Lớp trưởng/Bí thư chung hoặc HS ngoại trú)
    hs_ten = u_curr.get("fullname", "Học sinh")
    lop_em = ma_lk_curr if (ma_lk_curr and len(ma_lk_curr) <= 5) else "Toàn trường"
    phong_em = "Không ở bán trú"

    if row_hs_self is not None:
        hs_ten = row_hs_self["Họ và tên"]
        lop_em = row_hs_self["Lớp"]
        phong_em = row_hs_self["Phòng"]

    # Huy hiệu chức danh
    badge_role_html = ""
    if is_truong_phong:
        badge_role_html = f"<span style='background:#DC2626; color:white; padding:3px 10px; border-radius:12px; font-weight:bold; font-size:12px; margin-left:8px;'>👑 TRƯỞNG PHÒNG ({phong_em})</span>"
    elif is_bcs:
        badge_role_html = f"<span style='background:#F59E0B; color:#111827; padding:3px 10px; border-radius:12px; font-weight:bold; font-size:12px; margin-left:8px;'>🚩 BAN CÁN SỰ & CỜ ĐỎ ({chuc_danh})</span>"

    st.markdown(f"#### 👋 Xin chào em: **{hs_ten}** — Lớp: **{lop_em}** {badge_role_html}", unsafe_allow_html=True)

    # Hiển thị thẻ thông tin nhanh
    if row_hs_self is not None:
        trang_thai_hien_tai = row_hs_self.get("Trạng thái", "Tại trường")
        if "về" in trang_thai_hien_tai.lower() or "nhà" in trang_thai_hien_tai.lower():
            badge_tt = "<span style='background:#DC2626; color:white; padding:3px 10px; border-radius:15px; font-weight:bold;'>🏠 Em đang ở nhà</span>"
        else:
            badge_tt = "<span style='background:#16A34A; color:white; padding:3px 10px; border-radius:15px; font-weight:bold;'>🟢 Em đang tại trường</span>"

        st.markdown(f"""
        <div style="background:#F0F9FF; border-left:5px solid #0284C7; padding:12px 16px; border-radius:8px; margin-bottom:15px;">
            <b>Phòng KTX:</b> <span style="font-size:16px; font-weight:bold; color:#0369A1;">{row_hs_self['Phòng']}</span> (Giường: <b>{row_hs_self['Giường']}</b>) | <b>Dãy:</b> {row_hs_self['Dãy nhà']} | <b>Chính sách NĐ 116:</b> {row_hs_self['Chính sách NĐ116']} | <b>Trạng thái:</b> {badge_tt}
        </div>
        """, unsafe_allow_html=True)

    # 2.2. DANH SÁCH TAB ĐƯỢC CẤP QUYỀN ĐỘC QUYỀN
    # Tạo danh sách tabs động theo đúng đặc nhiệm
    list_tab_names = []
    
    # Tab thường dùng cho bán trú
    if row_hs_self is not None:
        list_tab_names.append("🚗 BÁO VỀ NHÀ / XUỐNG TRƯỜNG")
        list_tab_names.append("👥 THÀNH VIÊN PHÒNG KTX")

    # Nhiệm vụ Trưởng phòng & Ban Cán Sự (Yêu cầu 2 & 3)
    if is_truong_phong or is_bcs:
        list_tab_names.append("🏢 ĐIỂM DANH & TÍCH VẮNG PHÒNG KTX")
        list_tab_names.append("🏆 CHẤM ĐIỂM THI ĐUA PHÒNG 5S")

    # Nhiệm vụ Đánh giá phương tiện xe (Yêu cầu 3 dành cho Lớp trưởng, Bí thư & Cờ đỏ)
    if is_bcs:
        list_tab_names.append("🛵 BAN CÁN SỰ: ĐÁNH GIÁ VI PHẠM PHƯƠNG TIỆN")

    # Tab cá nhân hóa
    list_tab_names.append("👤 CHỈNH SỬA THÔNG TIN CÁ NHÂN CỦA EM")
    list_tab_names.append("🥗 THỰC ĐƠN HÔM NAY")

    rendered_tabs = st.tabs(list_tab_names)
    tab_map = dict(zip(list_tab_names, rendered_tabs))

    # =========================================================================
    # TAB: BÁO VỀ NHÀ / XUỐNG TRƯỜNG
    # =========================================================================
    if "🚗 BÁO VỀ NHÀ / XUỐNG TRƯỜNG" in tab_map and row_hs_self is not None:
        with tab_map["🚗 BÁO VỀ NHÀ / XUỐNG TRƯỜNG"]:
            st.markdown("### 🚗 Xác Nhận Tác Nghiệp: Đã Về Nhà Hoặc Đã Xuống Trường")
            c_hs_ve, c_hs_xuong = st.columns([1, 1])

            with c_hs_ve:
                st.markdown("""
                <div style="background:#FEF2F2; border:2px solid #DC2626; padding:15px; border-radius:10px; text-align:center;">
                    <h4 style="color:#B91C1C; margin:0 0 6px 0;">🏠 1. BÁO ĐÃ VỀ ĐẾN NHÀ AN TOÀN</h4>
                    <p style="font-size:12.5px; color:#4B5563; margin:0;">Dùng khi em rời KTX về nhà (cuối tuần, nghỉ lễ hoặc ốm về nhà).</p>
                </div>
                """, unsafe_allow_html=True)
                with st.form("form_hs_bao_ve_tab"):
                    ly_do_ve = st.selectbox("Lý do về nhà:", ["Về cuối tuần", "Về nghỉ lễ", "Việc gia đình", "Ốm về nhà điều trị"])
                    phuong_tien_ve = st.text_input("Ai đón / Đi bằng gì:", placeholder="VD: Bố đón xe máy / Đi xe buýt Bảo Hà")
                    if st.form_submit_button("🏡 XÁC NHẬN: EM ĐÃ VỀ ĐẾN NHÀ AN TOÀN", type="primary", use_container_width=True):
                        dong_xv = {
                            "Thời gian": datetime.now().strftime("%d/%m/%Y %H:%M"),
                            "Mã HS": row_hs_self["Mã HS"], "Họ và tên": hs_ten, "Lớp": row_hs_self["Lớp"],
                            "Phòng": row_hs_self["Phòng"], "Hình thức": "Học sinh báo về nhà",
                            "Lý do": ly_do_ve, "Người đón / SĐT": phuong_tien_ve if phuong_tien_ve else "Tự về",
                            "Người duyệt": "Học sinh tự báo qua App", "Trạng thái": "Đã về nhà an toàn"
                        }
                        df_xv_old = pd.read_csv(FILE_XIN_VE, encoding='utf-8-sig') if os.path.exists(FILE_XIN_VE) else pd.DataFrame()
                        df_xv_new = pd.concat([df_xv_old, pd.DataFrame([dong_xv])], ignore_index=True)
                        df_xv_new.to_csv(FILE_XIN_VE, index=False, encoding='utf-8-sig')

                        df_current.loc[df_current["Mã HS"] == row_hs_self["Mã HS"], "Trạng thái"] = "Đã về nhà an toàn"
                        df_current.loc[df_current["Mã HS"] == row_hs_self["Mã HS"], "GĐ1: Ăn trưa"] = False
                        df_current.loc[df_current["Mã HS"] == row_hs_self["Mã HS"], "GĐ2: Phòng nghỉ"] = False
                        dong_bo_file_da_noi(df_current, [FILE_DU_LIEU_THUC_TE, "D:/danh_sach_hoc_sinh_thuc_te.csv", "D:/phan_mem_ban_tru_cloud/danh_sach_hoc_sinh_thuc_te.csv"])
                        st.success(f"🎉 Cảm ơn em {hs_ten}! Thầy Cô Quản nhiệm đã nhận được tin báo em về đến nhà an toàn.")
                        st.rerun()

            with c_hs_xuong:
                st.markdown("""
                <div style="background:#F0FDF4; border:2px solid #16A34A; padding:15px; border-radius:10px; text-align:center;">
                    <h4 style="color:#15803D; margin:0 0 6px 0;">🏫 2. BÁO ĐÃ XUỐNG TRƯỜNG AN TOÀN</h4>
                    <p style="font-size:12.5px; color:#4B5563; margin:0;">Dùng khi em từ nhà đã quay trở lại Ký túc xá trường học.</p>
                </div>
                """, unsafe_allow_html=True)
                with st.form("form_hs_bao_xuong_tab"):
                    phuong_tien_xuong = st.text_input("Phương tiện di chuyển:", placeholder="VD: Bố mẹ chở xuống / Đi xe máy điện")
                    if st.form_submit_button("🎒 XÁC NHẬN: EM ĐÃ XUỐNG TRƯỜNG AN TOÀN", type="primary", use_container_width=True):
                        dong_xv = {
                            "Thời gian": datetime.now().strftime("%d/%m/%Y %H:%M"),
                            "Mã HS": row_hs_self["Mã HS"], "Họ và tên": hs_ten, "Lớp": row_hs_self["Lớp"],
                            "Phòng": row_hs_self["Phòng"], "Hình thức": "Học sinh báo xuống trường",
                            "Lý do": "Trở lại trường học tập", "Người đón / SĐT": phuong_tien_xuong if phuong_tien_xuong else "Tự đi",
                            "Người duyệt": "Học sinh tự báo qua App", "Trạng thái": "Tại trường"
                        }
                        df_xv_old = pd.read_csv(FILE_XIN_VE, encoding='utf-8-sig') if os.path.exists(FILE_XIN_VE) else pd.DataFrame()
                        df_xv_new = pd.concat([df_xv_old, pd.DataFrame([dong_xv])], ignore_index=True)
                        df_xv_new.to_csv(FILE_XIN_VE, index=False, encoding='utf-8-sig')

                        df_current.loc[df_current["Mã HS"] == row_hs_self["Mã HS"], "Trạng thái"] = "Tại trường"
                        df_current.loc[df_current["Mã HS"] == row_hs_self["Mã HS"], "GĐ1: Ăn trưa"] = True
                        df_current.loc[df_current["Mã HS"] == row_hs_self["Mã HS"], "GĐ2: Phòng nghỉ"] = True
                        dong_bo_file_da_noi(df_current, [FILE_DU_LIEU_THUC_TE, "D:/danh_sach_hoc_sinh_thuc_te.csv", "D:/phan_mem_ban_tru_cloud/danh_sach_hoc_sinh_thuc_te.csv"])
                        st.success(f"🎉 Chào mừng em {hs_ten} đã trở lại trường! Suất cơm và giường KTX của em đã sẵn sàng.")
                        st.rerun()

    # =========================================================================
    # TAB: THÀNH VIÊN PHÒNG KTX
    # =========================================================================
    if "👥 THÀNH VIÊN PHÒNG KTX" in tab_map and row_hs_self is not None:
        with tab_map["👥 THÀNH VIÊN PHÒNG KTX"]:
            st.markdown(f"#### 🚪 Danh Sách Các Bạn Cùng Phòng: **{row_hs_self['Phòng']}**")
            ban_cung_phong = df_current[df_current["Phòng"] == row_hs_self["Phòng"]][["Giường", "Mã HS", "Họ và tên", "Lớp", "Dân tộc", "Chức vụ phòng", "Trạng thái"]]
            st.dataframe(ban_cung_phong, use_container_width=True, hide_index=True)

    # =========================================================================
    # TAB: ĐIỂM DANH & TÍCH VẮNG PHÒNG KTX (YÊU CẦU 2 & 3: TRƯỞNG PHÒNG & BAN CÁN SỰ)
    # =========================================================================
    if "🏢 ĐIỂM DANH & TÍCH VẮNG PHÒNG KTX" in tab_map:
        with tab_map["🏢 ĐIỂM DANH & TÍCH VẮNG PHÒNG KTX"]:
            st.markdown("### 🏢 Điểm Danh & Báo Cáo Sĩ Số, Tích Vắng Phòng KTX")
            st.caption("Dành cho Học sinh Trưởng phòng và Ban Cán sự Lớp (Lớp trưởng, Bí thư) theo dõi nề nếp phòng ở các thời điểm trong ngày.")

            # Xác định phòng cần điểm danh
            ds_cac_phong = sorted(list(df_current["Phòng"].unique()))
            if is_truong_phong and row_hs_self is not None and row_hs_self["Phòng"] in ds_cac_phong:
                idx_def_p = ds_cac_phong.index(row_hs_self["Phòng"])
                phong_dd = st.selectbox("Chọn phòng KTX cần điểm danh:", ds_cac_phong, index=idx_def_p)
            else:
                phong_dd = st.selectbox("Chọn phòng KTX cần điểm danh:", ds_cac_phong)

            # 4 Thời điểm trong ngày theo đúng yêu cầu
            thoi_diem_dd = st.selectbox(
                "⏰ Chọn thời điểm điểm danh trong ngày:",
                [
                    "🌅 Sáng sớm (06:00 - 06:30): Báo thức, thể dục & dọn dẹp",
                    "☀️ Buổi trưa (11:30 - 12:30): Ăn cơm trưa & Nghỉ trưa KTX",
                    "🌆 Buổi tối (17:30 - 18:30): Ăn cơm tối & Điểm danh buổi tối",
                    "🌙 Ban đêm (21:30 - 22:00): Tắt đèn KTX đi ngủ"
                ]
            )

            df_thanh_vien = df_current[df_current["Phòng"] == phong_dd].copy()
            si_so = len(df_thanh_vien)

            st.markdown(f"##### 📋 Danh Sách Thành Viên {phong_dd} (Sĩ số: **{si_so} học sinh**):")
            st.caption("Tích chọn các bạn vắng mặt và ghi rõ thời gian vắng, lý do vắng để gửi về Thầy Quản nhiệm & Nhà bếp:")

            with st.form("form_diem_danh_phong_live"):
                danh_sach_vang = []
                co_mat_count = 0

                for idx, r_mem in df_thanh_vien.iterrows():
                    m_hs = r_mem["Mã HS"]
                    t_hs = r_mem["Họ và tên"]
                    g_hs = r_mem.get("Giường", "")
                    l_hs = r_mem.get("Lớp", "")

                    c_ck1, c_ck2, c_ck3 = st.columns([1.5, 1.2, 1.5])
                    with c_ck1:
                        st.markdown(f"🛏️ **{g_hs}** — **{t_hs}** ({l_hs})")
                        is_vang = st.checkbox(f"❌ BÁO VẮNG EM NÀY", key=f"vang_{m_hs}")
                    with c_ck2:
                        tg_vang = st.text_input("Thời gian vắng:", value="Cả buổi" if is_vang else "", key=f"tg_{m_hs}", placeholder="VD: 11h30-13h, cả ngày...")
                    with c_ck3:
                        ly_do_v = st.selectbox("Lý do vắng:", ["Có mặt", "Về nhà cuối tuần", "Gia đình có việc đón", "Ốm tại phòng Y tế", "Đi học bồi dưỡng / học thêm", "Vắng chưa rõ lý do"], index=1 if is_vang else 0, key=f"ld_{m_hs}")

                    if is_vang:
                        danh_sach_vang.append({
                            "Mã HS": m_hs,
                            "Họ và tên": t_hs,
                            "Lớp": l_hs,
                            "Giường": g_hs,
                            "Thời gian vắng": tg_vang.strip() if tg_vang.strip() else "Cả buổi",
                            "Lý do vắng": ly_do_v
                        })
                    else:
                        co_mat_count += 1

                so_vang = len(danh_sach_vang)
                st.markdown("---")
                st.markdown(f"📊 **TỔNG KẾT NHANH:** Sĩ số phòng: **{si_so}** | Có mặt: <b style='color:#16A34A;'>{co_mat_count}</b> | Vắng mặt: <b style='color:#DC2626;'>{so_vang}</b>", unsafe_allow_html=True)
                ghi_chu_chung = st.text_input("Ghi chú thêm của người điểm danh (nếu có):", placeholder="VD: Phòng trực nhật sạch sẽ; các bạn có mặt đúng giờ...")

                btn_gui_dd = st.form_submit_button("📤 GỬI BÁO CÁO ĐIỂM DANH CHO THẦY QUẢN NHIỆM & NHÀ BẾP", type="primary", use_container_width=True)

                if btn_gui_dd:
                    file_nhat_ky_dd = os.path.join(BASE_DIR, "nhat_ky_diem_danh_phong.csv")
                    chi_tiet_str = "; ".join([f"{v['Họ và tên']} ({v['Giường']}, {v['Lớp']}): Vắng lúc {v['Thời gian vắng']} - Lý do: {v['Lý do vắng']}" for v in danh_sach_vang]) if danh_sach_vang else "Có mặt đủ 100%"

                    dong_nhat_ky = {
                        "Thời gian gửi": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                        "Ngày": ngay_lam_viec.strftime("%d/%m/%Y"),
                        "Thời điểm": thoi_diem_dd.split(":")[0].strip(),
                        "Phòng": phong_dd,
                        "Người báo": f"{u_curr.get('fullname')} ({chuc_danh})",
                        "Sĩ số phòng": si_so,
                        "Số có mặt": co_mat_count,
                        "Số vắng": so_vang,
                        "Chi tiết vắng": chi_tiet_str,
                        "Ghi chú": ghi_chu_chung.strip()
                    }

                    df_nk_old = pd.read_csv(file_nhat_ky_dd, encoding='utf-8-sig') if os.path.exists(file_nhat_ky_dd) else pd.DataFrame()
                    df_nk_new = pd.concat([df_nk_old, pd.DataFrame([dong_nhat_ky])], ignore_index=True)
                    dong_bo_file_da_noi(df_nk_new, [file_nhat_ky_dd, "D:/nhat_ky_diem_danh_phong.csv", "D:/phan_mem_ban_tru_cloud/nhat_ky_diem_danh_phong.csv"])

                    # Cập nhật trạng thái từng bạn vắng vào danh sách live
                    for v in danh_sach_vang:
                        m_v = v["Mã HS"]
                        df_current.loc[df_current["Mã HS"] == m_v, "Trạng thái"] = f"Vắng ({v['Lý do vắng']})"
                        if "trưa" in thoi_diem_dd.lower():
                            df_current.loc[df_current["Mã HS"] == m_v, "GĐ1: Ăn trưa"] = False
                            df_current.loc[df_current["Mã HS"] == m_v, "GĐ2: Phòng nghỉ"] = False
                        elif "đêm" in thoi_diem_dd.lower():
                            df_current.loc[df_current["Mã HS"] == m_v, "GĐ2: Phòng nghỉ"] = False

                    dong_bo_file_da_noi(df_current, [FILE_DU_LIEU_THUC_TE, "D:/danh_sach_hoc_sinh_thuc_te.csv", "D:/phan_mem_ban_tru_cloud/danh_sach_hoc_sinh_thuc_te.csv"])

                    st.success(f"🎉 Đã gửi thành công báo cáo điểm danh {phong_dd}! Thầy Quản nhiệm KTX và Nhà bếp đã tiếp nhận ngay tức thì.")
                    st.rerun()

            # Bảng nhật ký điểm danh phòng
            st.markdown("---")
            st.markdown("##### 📜 Lịch Sử Báo Điểm Danh Phòng Gần Nhất:")
            file_nhat_ky_dd = os.path.join(BASE_DIR, "nhat_ky_diem_danh_phong.csv")
            if os.path.exists(file_nhat_ky_dd):
                df_nk_view = pd.read_csv(file_nhat_ky_dd, encoding='utf-8-sig').fillna("")
                df_nk_phong = df_nk_view[df_nk_view["Phòng"] == phong_dd] if "Phòng" in df_nk_view.columns else df_nk_view
                if not df_nk_phong.empty:
                    st.dataframe(df_nk_phong.tail(10), use_container_width=True, hide_index=True)
                else:
                    st.info(f"Chưa có bản ghi điểm danh nào cho {phong_dd}.")

    # =========================================================================
    # TAB: CHẤM ĐIỂM THI ĐUA PHÒNG 5S (YÊU CẦU 2 & 3: TRƯỞNG PHÒNG & BAN CÁN SỰ)
    # =========================================================================
    if "🏆 CHẤM ĐIỂM THI ĐUA PHÒNG 5S" in tab_map:
        with tab_map["🏆 CHẤM ĐIỂM THI ĐUA PHÒNG 5S"]:
            st.markdown("### 🏆 Chấm Điểm Thi Đua Nếp Sống 5S Ký Túc Xá")
            st.caption("Tiêu chuẩn 5S: Sàng lọc - Sắp xếp - Sạch sẽ - Săn sóc - Sẵn sàng • Góp phần xây dựng Ký túc xá văn minh, an toàn.")

            ds_cac_phong = sorted(list(df_current["Phòng"].unique()))
            if is_truong_phong and row_hs_self is not None and row_hs_self["Phòng"] in ds_cac_phong:
                phong_cham = st.selectbox("Chọn phòng chấm thi đua:", ds_cac_phong, index=ds_cac_phong.index(row_hs_self["Phòng"]), key="sb_phong_cham_td")
            else:
                phong_cham = st.selectbox("Chọn phòng chấm thi đua:", ds_cac_phong, key="sb_phong_cham_td")

            with st.form("form_cham_thi_dua_phong_5s"):
                st.markdown("##### 📌 Đánh giá 5 tiêu chí nếp sống KTX (Mỗi tiêu chí tối đa 20 điểm):")
                c_td1, c_td2 = st.columns(2)
                with c_td1:
                    d_ve_sinh = st.slider("1. Vệ sinh sàn phòng, hành lang, khu vệ sinh sạch sẽ:", 0, 20, 18)
                    d_chan_man = st.slider("2. Gấp chăn màn vuông vắn, xếp gối gọn gàng trên giường:", 0, 20, 19)
                    d_do_dung = st.slider("3. Sắp xếp giá dép, bàn học, sách vở ngăn nắp:", 0, 20, 18)
                with c_td2:
                    d_dien_nuoc = st.slider("4. An toàn điện nước, tắt quạt, tắt đèn khi ra khỏi phòng:", 0, 20, 20)
                    d_trat_tu = st.slider("5. Chấp hành giờ giấc tự học, giữ trật tự giờ ngủ đêm:", 0, 20, 19)
                    d_tru_loi = st.number_input("Điểm trừ vi phạm (nếu có lỗi mất trật tự, hút thuốc...):", min_value=0, max_value=50, value=0, step=1)

                tong_diem = max(0, d_ve_sinh + d_chan_man + d_do_dung + d_dien_nuoc + d_trat_tu - d_tru_loi)
                xep_loai = "Xuất sắc 🌟" if tong_diem >= 95 else ("Tốt 🟢" if tong_diem >= 85 else ("Khá 🟡" if tong_diem >= 70 else "Cần cố gắng 🔴"))

                st.markdown(f"#### 🎯 Tổng điểm phòng: <b style='color:#DC2626;'>{tong_diem} / 100 điểm</b> — Xếp loại: <b>{xep_loai}</b>", unsafe_allow_html=True)
                nhan_xet_td = st.text_input("Nhận xét / Đề xuất của người chấm:", placeholder="VD: Phòng gọn gàng, chăn màn gấp rất đẹp...")

                if st.form_submit_button("💾 LƯU KẾT QUẢ CHẤM ĐIỂM THI ĐUA PHÒNG", type="primary", use_container_width=True):
                    file_td_log = os.path.join(BASE_DIR, "nhat_ky_cham_thi_dua_phong.csv")
                    dong_td = {
                        "Thời gian": datetime.now().strftime("%d/%m/%Y %H:%M"),
                        "Phòng": phong_cham,
                        "Người chấm": f"{u_curr.get('fullname')} ({chuc_danh})",
                        "Vệ sinh": d_ve_sinh, "Chăn màn": d_chan_man, "Đồ dùng": d_do_dung,
                        "Điện nước": d_dien_nuoc, "Trật tự": d_trat_tu, "Điểm trừ": d_tru_loi,
                        "Tổng điểm": tong_diem, "Xếp loại": xep_loai, "Nhận xét": nhan_xet_td.strip()
                    }
                    df_td_old = pd.read_csv(file_td_log, encoding='utf-8-sig') if os.path.exists(file_td_log) else pd.DataFrame()
                    df_td_new = pd.concat([df_td_old, pd.DataFrame([dong_td])], ignore_index=True)
                    dong_bo_file_da_noi(df_td_new, [file_td_log, "D:/nhat_ky_cham_thi_dua_phong.csv", "D:/phan_mem_ban_tru_cloud/nhat_ky_cham_thi_dua_phong.csv"])

                    st.success(f"🎉 Đã lưu kết quả thi đua 5S cho {phong_cham}! Tổng điểm: {tong_diem} điểm ({xep_loai}).")
                    st.rerun()

    # =========================================================================
    # TAB: ĐÁNH GIÁ VI PHẠM PHƯƠNG TIỆN (YÊU CẦU 3: LỚP TRƯỞNG & BÍ THƯ & CỜ ĐỎ)
    # =========================================================================
    if "🛵 BAN CÁN SỰ: ĐÁNH GIÁ VI PHẠM PHƯƠNG TIỆN" in tab_map:
        with tab_map["🛵 BAN CÁN SỰ: ĐÁNH GIÁ VI PHẠM PHƯƠNG TIỆN"]:
            st.markdown("### 🛵 Ban Cán Sự Lớp & Cờ Đỏ: Kiểm Tra & Đánh Giá Vi Phạm Phương Tiện")
            st.caption("Tra cứu phương tiện xe toàn trường (549 xe), kiểm tra tem mã QR định danh và lập biên bản xử lý vi phạm nề nếp an toàn giao thông.")

            f_xe = os.path.join(BASE_DIR, "quan_ly_phuong_tien.csv") if os.path.exists(os.path.join(BASE_DIR, "quan_ly_phuong_tien.csv")) else "D:/quan_ly_phuong_tien.csv"
            f_vp = os.path.join(BASE_DIR, "lich_su_vi_pham_xe.csv") if os.path.exists(os.path.join(BASE_DIR, "lich_su_vi_pham_xe.csv")) else "D:/lich_su_vi_pham_xe.csv"

            if os.path.exists(f_xe):
                df_xe_all = pd.read_csv(f_xe, encoding='utf-8-sig', dtype=str).fillna("")
            else:
                df_xe_all = pd.DataFrame()

            c_tra1, c_tra2 = st.columns([1.5, 1])
            with c_tra1:
                tim_xe_kw = st.text_input("🔍 Nhập Biển số, Mã xe (XE-...), hoặc Tên HS để tìm nhanh:", placeholder="VD: 24-AA 253.20, XE-526, Lê Văn Thưởng, 12A7...", key="tim_xe_bcs")
            with c_tra2:
                loc_lop_xe = st.selectbox("Lọc theo lớp:", ["Tất cả các lớp"] + sorted(list(df_xe_all['Lớp'].unique())) if not df_xe_all.empty else ["Tất cả"], key="loc_lop_bcs")

            df_xe_filter = df_xe_all.copy()
            if loc_lop_xe != "Tất cả các lớp" and not df_xe_filter.empty:
                df_xe_filter = df_xe_filter[df_xe_filter['Lớp'] == loc_lop_xe]
            if tim_xe_kw.strip() and not df_xe_filter.empty:
                kw = tim_xe_kw.strip()
                df_xe_filter = df_xe_filter[
                    df_xe_filter['Biển số xe'].astype(str).str.contains(kw, case=False, na=False) |
                    df_xe_filter['Mã xe'].astype(str).str.contains(kw, case=False, na=False) |
                    df_xe_filter['Họ và tên'].astype(str).str.contains(kw, case=False, na=False) |
                    df_xe_filter['SĐT Học sinh'].astype(str).str.contains(kw, na=False)
                ]

            ds_xe_opt = [f"{r['Mã xe']} - {r['Biển số xe']} - {r['Họ và tên']} ({r['Lớp']})" for idx, r in df_xe_filter.iterrows()] if not df_xe_filter.empty else []
            if not ds_xe_opt and not df_xe_all.empty:
                st.warning("⚠️ Không tìm thấy xe theo từ khóa trên. Đang hiển thị danh sách toàn trường:")
                ds_xe_opt = [f"{r['Mã xe']} - {r['Biển số xe']} - {r['Họ và tên']} ({r['Lớp']})" for idx, r in df_xe_all.iterrows()]

            if ds_xe_opt:
                xe_duoc_chon = st.selectbox("👉 Chọn xe cần kiểm tra / lập biên bản vi phạm:", ds_xe_opt, key="sb_xe_duoc_chon_bcs")
                ma_xe_sel = xe_duoc_chon.split(" - ")[0].strip()
                row_xe_view = df_xe_all[df_xe_all["Mã xe"] == ma_xe_sel].iloc[0]

                # Hiển thị thẻ xe chuẩn
                noi_de_xe_val = str(row_xe_view.get("Nơi gửi xe", row_xe_view.get("Nơi để xe", "Trong trường"))).strip()
                if not noi_de_xe_val or noi_de_xe_val.lower() in ['nan', 'trong trường']:
                    noi_de_xe_val = "Trong trường"

                sdt_hs_val = clean_phone_str(row_xe_view.get("SĐT Học sinh", ""))
                sdt_ph_val = clean_phone_str(row_xe_view.get("SĐT Phụ huynh", ""))
                sdt_gv_val = clean_phone_str(row_xe_view.get("SĐT GVCN", ""))

                c_vx1, c_vx2 = st.columns([1, 1.3])
                with c_vx1:
                    st.markdown(f"""
                    <div style='background:white; border:2px solid #059669; border-radius:12px; padding:15px; text-align:center;'>
                        <div style='background:#059669; color:white; font-weight:800; font-size:12px; padding:3px 8px; border-radius:6px; margin-bottom:8px;'>
                            TRƯỜNG THPT SỐ 2 BẢO YÊN
                        </div>
                        <h4 style='color:#065F46; margin:0;'>THẺ ĐỊNH DANH PHƯƠNG TIỆN</h4>
                        <p style='font-size:22px; font-weight:900; color:#1E3A8A; margin:8px 0 4px 0;'>{row_xe_view['Biển số xe']}</p>
                        <p style='font-size:15px; font-weight:bold; color:#111827; margin:0;'>{row_xe_view['Họ và tên']} — Lớp {row_xe_view['Lớp']}</p>
                        <span style='background:#10B981; color:white; padding:3px 12px; border-radius:12px; font-size:12px; display:inline-block; margin-top:8px;'>{row_xe_view['Loại xe']} • {row_xe_view['Màu xe']}</span>
                        <div style='margin-top:10px; padding-top:8px; border-top:1px dashed #E5E7EB; font-size:13px;'>
                            📍 <b>Nơi để xe:</b> <span style='font-weight:bold; color:#B45309;'>{noi_de_xe_val}</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                with c_vx2:
                    st.markdown(f"""
                    <div style='background:#F8FAFC; border:1.5px solid #CBD5E1; border-radius:12px; padding:14px; font-size:13.5px;'>
                        <h4 style='color:#1E3A8A; margin:0 0 6px 0;'>📋 THÔNG TIN QUẢN LÝ PHƯƠNG TIỆN</h4>
                        <p style='margin:3px 0;'>👤 <b>Chủ xe:</b> {row_xe_view['Họ và tên']} (Lớp <b>{row_xe_view['Lớp']}</b>)</p>
                        <p style='margin:3px 0;'>📱 <b>SĐT Học sinh:</b> <a href='tel:{sdt_hs_val}'>{sdt_hs_val}</a></p>
                        <p style='margin:3px 0;'>👨‍👩‍👧 <b>Phụ huynh:</b> {row_xe_view['Họ tên Phụ huynh']} (📞 <a href='tel:{sdt_ph_val}'>{sdt_ph_val}</a>)</p>
                        <p style='margin:3px 0;'>👨‍🏫 <b>GVCN Lớp:</b> {row_xe_view['GVCN']} (📞 <a href='tel:{sdt_gv_val}'>{sdt_gv_val}</a>)</p>
                        <p style='margin:3px 0;'>🏢 <b>Nơi gửi xe:</b> <b style='color:#059669;'>{noi_de_xe_val}</b></p>
                        <p style='margin:3px 0;'>⚠️ <b>Số lần vi phạm trước đây:</b> <b style='color:red;'>{row_xe_view.get('Số lần vi phạm', 0)} lần</b></p>
                    </div>
                    """, unsafe_allow_html=True)

                # Form Lập biên bản vi phạm
                st.markdown("---")
                st.markdown("##### 🚨 Lập Biên Bản Vi Phạm Phương Tiện (Ban Cán Sự & Cờ Đỏ):")
                with st.form("form_lap_bb_xe_bcs"):
                    c_bb1, c_bb2 = st.columns(2)
                    with c_bb1:
                        loi_xe_chon = st.multiselect(
                            "Chọn các lỗi vi phạm nề nếp / ATGT:",
                            [
                                "Không đội mũ bảo hiểm khi điều khiển xe",
                                "Đi xe phân khối lớn (>50cc) khi chưa đủ tuổi",
                                "Chở quá số người quy định (kẹp 3, kẹp 4)",
                                "Để xe sai nơi quy định (không xếp đúng khu vực lớp)",
                                "Chưa dán tem mã QR định danh của nhà trường",
                                "Xe không có gương chiếu hậu bên trái",
                                "Thay đổi kết cấu xe / ống pô gây ồn",
                                "Lạng lách, phóng nhanh trong sân trường / cổng trường"
                            ],
                            default=["Không đội mũ bảo hiểm khi điều khiển xe"]
                        )
                    with c_bb2:
                        diem_tru_dtn = st.number_input("Điểm trừ thi đua Chi đoàn:", min_value=0, max_value=50, value=5, step=1)
                        ghi_chu_bb = st.text_input("Ghi chú chi tiết / Minh chứng:", placeholder="VD: Bị ghi nhận lúc 07h10 tại cổng trường...")

                    btn_lap_bb = st.form_submit_button("🚨 LẬP BIÊN BẢN VI PHẠM & BÁO CÁO ĐOÀN TRƯỜNG", type="primary", use_container_width=True)

                    if btn_lap_bb:
                        if not loi_xe_chon:
                            st.warning("⚠️ Vui lòng chọn ít nhất một lỗi vi phạm!")
                        else:
                            loi_str = "; ".join(loi_xe_chon)
                            nguoi_lap = f"{u_curr.get('fullname')} ({chuc_danh})"

                            dong_vp = {
                                "Ngày": datetime.now().strftime("%d/%m/%Y"),
                                "Mã xe": row_xe_view["Mã xe"],
                                "Họ và tên": row_xe_view["Họ và tên"],
                                "Lớp": row_xe_view["Lớp"],
                                "Biển số xe": row_xe_view["Biển số xe"],
                                "Lỗi vi phạm": loi_str,
                                "Điểm trừ": -int(diem_tru_dtn),
                                "Người lập biên bản": nguoi_lap,
                                "Trạng thái": "Ban Cán sự ghi nhận"
                            }

                            df_vp_old = pd.read_csv(f_vp, encoding='utf-8-sig') if os.path.exists(f_vp) else pd.DataFrame()
                            df_vp_new = pd.concat([df_vp_old, pd.DataFrame([dong_vp])], ignore_index=True)
                            dong_bo_file_da_noi(df_vp_new, [f_vp, "D:/lich_su_vi_pham_xe.csv", "D:/phan_mem_ban_tru_cloud/lich_su_vi_pham_xe.csv"])

                            # Tăng số lần vi phạm của xe
                            idx_xe_vp = df_xe_all[df_xe_all["Mã xe"] == row_xe_view["Mã xe"]].index[0]
                            sl_hien_tai = int(row_xe_view.get("Số lần vi phạm", 0)) if str(row_xe_view.get("Số lần vi phạm", 0)).isdigit() else 0
                            df_xe_all.loc[idx_xe_vp, "Số lần vi phạm"] = sl_hien_tai + 1
                            dong_bo_file_da_noi(df_xe_all, [f_xe, "D:/quan_ly_phuong_tien.csv", "D:/phan_mem_ban_tru_cloud/quan_ly_phuong_tien.csv"])

                            st.success(f"🎉 Đã lập biên bản vi phạm cho xe {row_xe_view['Biển số xe']} ({row_xe_view['Họ và tên']} - Lớp {row_xe_view['Lớp']})! Đã chuyển thông tin về Đoàn trường và GVCN.")
                            st.rerun()

            # Danh sách các biên bản vi phạm gần đây
            st.markdown("---")
            st.markdown("##### 📜 Lịch Sử Lập Biên Bản Vi Phạm Phương Tiện:")
            if os.path.exists(f_vp):
                df_vp_show = pd.read_csv(f_vp, encoding='utf-8-sig').fillna("")
                st.dataframe(df_vp_show.tail(10), use_container_width=True, hide_index=True)

    # =========================================================================
    # TAB: CHỈNH SỬA THÔNG TIN CÁ NHÂN CỦA EM
    # =========================================================================
    if "👤 CHỈNH SỬA THÔNG TIN CÁ NHÂN CỦA EM" in tab_map:
        with tab_map["👤 CHỈNH SỬA THÔNG TIN CÁ NHÂN CỦA EM"]:
            st.markdown("#### 👤 Chỉnh Sửa & Cập Nhật Hồ Sơ Cá Nhân Của Em")
            st.caption("🔒 Em chỉ có quyền chỉnh sửa thông tin cá nhân và phương tiện của chính mình.")

            sdt_hs_cur = clean_phone_str(row_hs_self.get("SĐT Học sinh", "")) if row_hs_self is not None else clean_phone_str(u_curr.get("phone", ""))
            
            with st.form("form_edit_hoc_sinh_profile"):
                c_he1, c_he2 = st.columns(2)
                with c_he1:
                    sdt_hs_moi = st.text_input("Số điện thoại của em:", value=sdt_hs_cur, placeholder="VD: 0988...")
                    pw_hs_moi = st.text_input("Mật khẩu mới (bỏ trống nếu giữ nguyên):", type="password")
                with c_he2:
                    st.caption("🛵 Thông tin xe cá nhân:")
                    noi_de_xe_moi = st.selectbox("Nơi để xe của em:", ["Trong trường", "Gửi ngoài trường (Dũng Toan)", "Gửi ngoài trường (Cổng phụ)", "Đi bộ / Không đi xe"])

                if st.form_submit_button("💾 LƯU THAY ĐỔI THÔNG TIN CỦA EM", type="primary", use_container_width=True):
                    # Cập nhật vào danh sách bán trú nếu có
                    if row_hs_self is not None:
                        idx_hs_u = df_current[df_current["Mã HS"] == row_hs_self["Mã HS"]].index[0]
                        if sdt_hs_moi.strip():
                            df_current.loc[idx_hs_u, "SĐT Học sinh"] = clean_phone_str(sdt_hs_moi)
                        dong_bo_file_da_noi(df_current, [FILE_DU_LIEU_THUC_TE, "D:/danh_sach_hoc_sinh_thuc_te.csv", "D:/phan_mem_ban_tru_cloud/danh_sach_hoc_sinh_thuc_te.csv"])

                    # Cập nhật vào bảng tài khoản
                    if os.path.exists(FILE_TAI_KHOAN):
                        df_tk = pd.read_csv(FILE_TAI_KHOAN, encoding='utf-8-sig', dtype=str).fillna("")
                        m_tk = (df_tk["Tên đăng nhập"] == u_username)
                        if ma_lk_curr:
                            m_tk = m_tk | (df_tk["Mã liên kết"] == ma_lk_curr)
                        if m_tk.any():
                            if sdt_hs_moi.strip():
                                df_tk.loc[m_tk, "Số điện thoại"] = clean_phone_str(sdt_hs_moi)
                            if pw_hs_moi.strip() and len(pw_hs_moi.strip()) >= 4:
                                df_tk.loc[m_tk, "Mật khẩu"] = pw_hs_moi.strip()
                            dong_bo_file_da_noi(df_tk, [FILE_TAI_KHOAN, "D:/tai_khoan_nguoi_dung.csv", "D:/phan_mem_ban_tru_cloud/tai_khoan_nguoi_dung.csv"])

                    st.success("🎉 Đã cập nhật thành công thông tin hồ sơ của em!")
                    st.rerun()

    # =========================================================================
    # TAB: THỰC ĐƠN HÔM NAY
    # =========================================================================
    if "🥗 THỰC ĐƠN HÔM NAY" in tab_map:
        with tab_map["🥗 THỰC ĐƠN HÔM NAY"]:
            st.markdown("#### 🍲 Thực Đơn Bữa Ăn Hôm Nay Tại Ký Túc Xá:")
            if os.path.exists(FILE_THUC_DON):
                df_td_v = pd.read_csv(FILE_THUC_DON, encoding='utf-8-sig')
                st.dataframe(df_td_v, use_container_width=True, hide_index=True)

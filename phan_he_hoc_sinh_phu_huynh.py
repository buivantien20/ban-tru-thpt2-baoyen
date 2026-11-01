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
        da_dd_con = bool(row_con.get("Đã điểm danh", False))
        if not da_dd_con and not row_con.get("GĐ1: Ăn trưa", False):
            an_trang_thai = "⏳ Chờ quản nhiệm điểm danh (08:00 - 08:30)"
            nghi_trang_thai = "⏳ Chờ quản nhiệm điểm danh trưa (11:30 - 12:30)"
            tt_live_ph = "Chờ điểm danh ⏳"
        else:
            an_trang_thai = "🟢 Đã vào ăn cơm trưa" if row_con.get("GĐ1: Ăn trưa", False) else "🔴 Vắng ăn trưa / Cắt cơm"
            nghi_trang_thai = "🟢 Có mặt tại phòng nghỉ" if row_con.get("GĐ2: Phòng nghỉ", False) else "🔴 Vắng mặt tại phòng"
            tt_live_ph = row_con.get('Trạng thái', 'Tại trường')

        st.markdown(f"""
        <div style="background:#ECFDF5; border-left:5px solid #059669; padding:15px; border-radius:10px;">
            <h4 style="margin-top:0; color:#065F46;">📍 ĐIỂM DANH HÔM NAY ({ngay_lam_viec.strftime('%d/%m/%Y')}):</h4>
            <p>1. Bữa ăn trưa (GĐ1): <b>{an_trang_thai}</b></p>
            <p>2. Nghỉ trưa tại phòng (GĐ2): <b>{nghi_trang_thai}</b></p>
            <p>Trạng thái hiện tại: <span style="color:#2563EB; font-weight:bold;">{tt_live_ph}</span></p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # 1.3. CÁC TÁC NGHIỆP PHỤ HUYNH
    tab_ph_cat, tab_ph_ve, tab_ph_qr, tab_ph_td, tab_ph_edit = st.tabs([
        "🥣 BÁO CẮT CƠM (06:30 - 07:30)",
        "🚗 BÁO CON XIN VỀ / XUỐNG TRƯỜNG",
        "💳 ĐÓNG TIỀN ĂN QUA MÃ VIETQR",
        "🥗 THỰC ĐƠN BỮA ĂN CỦA CON",
        "👤 CHỈNH SỬA THÔNG TIN PHỤ HUYNH & HỌC SINH"
    ])

    with tab_ph_cat:
        st.markdown("#### 🥣 Báo Cắt Cơm Bán Trú Cho Con")
        st.info("⏰ **Khung giờ vàng (06:30 - 07:30 sáng):** Quý phụ huynh vui lòng gửi thông báo cắt cơm trong khung giờ **06:30 - 07:30 (Hạn chót trước 08:00)** để Thầy Quản nhiệm tổng hợp rà soát và kịp thời xuất Lệnh báo cơm cho nhà bếp lúc 08:00. Nhà bếp sẽ giảm nấu đúng suất và kế toán khấu trừ tiền ăn cho gia đình.")
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
        da_dd_self = bool(row_hs_self.get("Đã điểm danh", False))
        trang_thai_hien_tai = str(row_hs_self.get("Trạng thái", "Chờ điểm danh ⏳"))
        if not da_dd_self and not row_hs_self.get("GĐ1: Ăn trưa", False):
            badge_tt = "<span style='background:#6B7280; color:white; padding:3px 10px; border-radius:15px; font-weight:bold;'>⏳ Chờ điểm danh</span>"
        elif "về" in trang_thai_hien_tai.lower() or "nhà" in trang_thai_hien_tai.lower():
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

    # Nhiệm vụ Báo sĩ số lớp & Đánh giá xe (Dành cho Lớp trưởng, Bí thư & Ban cán sự)
    if is_bcs:
        list_tab_names.append("📊 LỚP TRƯỞNG: BÁO SĨ SỐ LỚP (SÁNG / CHIỀU / CẢ NGÀY)")
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

            # 4 Khung giờ trọng điểm trong ngày theo đúng quy định của Nhà trường
            thoi_diem_dd = st.selectbox(
                "⏰ Chọn khung giờ trọng điểm trong ngày (Golden Hours):",
                [
                    "🌅 05:30 - 06:00 | THỂ DỤC & VỆ SINH PHÒNG: Kiểm tra 5S, báo vắng sáng sớm (ốm Y tế / đã về tối qua)",
                    "⏰ 06:30 - 07:30 | CHỐT CẮT CƠM & XIN VỀ (HẠN CHÓT): Rà soát vắng trước khi Quản nhiệm ra lệnh báo cơm",
                    "☀️ 11:30 - 12:30 | BUỔI TRƯA: Giờ ăn cơm trưa & Nghỉ trưa KTX tại phòng",
                    "🌆 17:30 - 18:30 | BUỔI TỐI: Giờ ăn cơm tối & Điểm danh tự học",
                    "🌙 21:30 - 22:00 | ĐIỂM DANH ĐÊM & TẮT ĐÈN: Sĩ số ngủ đêm 19 phòng (Báo ngay nếu vắng bất thường)"
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
                st.info("ℹ️ **Lưu ý:** Số liệu quân số có mặt và vắng mặt chính thức sẽ được hệ thống tính toán và ghi nhận sau khi Trưởng phòng bấm nút Gửi bên dưới (không hiển thị ngầm định trước).")
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
    # TAB: BÁO SĨ SỐ LỚP HỌC (DÀNH CHO LỚP TRƯỞNG & BAN CÁN SỰ)
    # =========================================================================
    if "📊 LỚP TRƯỞNG: BÁO SĨ SỐ LỚP (SÁNG / CHIỀU / CẢ NGÀY)" in tab_map:
        with tab_map["📊 LỚP TRƯỞNG: BÁO SĨ SỐ LỚP (SÁNG / CHIỀU / CẢ NGÀY)"]:
            import quan_ly_si_so_lop
            quan_ly_si_so_lop.render_giao_dien_bao_si_so(
                u_curr=u_curr,
                role_curr=role_curr if 'role_curr' in locals() else "Học sinh",
                base_dir=BASE_DIR,
                is_bcs=True,
                is_gvcn=False,
                is_admin=False
            )

    # =========================================================================
    # TAB: BAN CÁN SỰ: ĐÁNH GIÁ VI PHẠM PHƯƠNG TIỆN
    # =========================================================================
    if "🛵 BAN CÁN SỰ: ĐÁNH GIÁ VI PHẠM PHƯƠNG TIỆN" in tab_map:
        with tab_map["🛵 BAN CÁN SỰ: ĐÁNH GIÁ VI PHẠM PHƯƠNG TIỆN"]:
            st.markdown("#### 🛵 Ban Cán Sự: Kiểm Tra & Ghi Nhận Vi Phạm Phương Tiện")
            st.caption("Dành cho Lớp trưởng, Bí thư chi đoàn và Đội Cờ đỏ ghi nhận các trường hợp vi phạm nề nếp phương tiện xe.")
            f_xe_bcs = os.path.join(BASE_DIR, "quan_ly_phuong_tien.csv") if os.path.exists(os.path.join(BASE_DIR, "quan_ly_phuong_tien.csv")) else "D:/quan_ly_phuong_tien.csv"
            df_xe_bcs = pd.read_csv(f_xe_bcs, encoding='utf-8-sig', dtype=str).fillna("") if os.path.exists(f_xe_bcs) else pd.DataFrame()
            if not df_xe_bcs.empty:
                ds_lop_list = ["Tất cả các lớp", "10A1", "10A2", "10A3", "10A4", "10A5", "10A6", "10A7", "11A1", "11A2", "11A3", "11A4", "11A5", "11A6", "11A7", "12A1", "12A2", "12A3", "12A4", "12A5", "12A6", "12A7"]
                col_bcs_x1, col_bcs_x2 = st.columns([1, 2])
                with col_bcs_x1:
                    lop_loc_xe = st.selectbox("Lọc xe theo lớp:", ds_lop_list, key="sb_loc_xe_bcs")
                with col_bcs_x2:
                    tim_kw_xe = st.text_input("🔍 Tìm kiếm xe (Mã xe / Biển số / Tên HS):", placeholder="VD: 24-AA, Lê Văn...", key="txt_kw_xe_bcs")

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

    # =========================================================================
    # TAB: CHỈNH SỬA THÔNG TIN CÁ NHÂN CỦA EM & ĐỀ XUẤT CẤP QUYỀN
    # =========================================================================
    if "👤 CHỈNH SỬA THÔNG TIN CÁ NHÂN CỦA EM" in tab_map:
        with tab_map["👤 CHỈNH SỬA THÔNG TIN CÁ NHÂN CỦA EM"]:
            st.markdown("### 👤 Cập Nhật Hồ Sơ Cá Nhân & Đề Xuất Cấp Quyền")
            st.caption("🔒 **Quyền riêng tư:** Em chỉ có quyền chỉnh sửa thông tin của chính mình. Dữ liệu sẽ được đồng bộ trực tiếp lên hệ thống toàn trường và KTX.")

            # Lấy thông tin bổ trợ từ danh sách toàn trường nếu có
            f_tt_full = "D:/danh_sach_hoc_sinh_toan_truong.csv"
            row_tt_self = None
            if os.path.exists(f_tt_full):
                try:
                    df_tt_tmp = pd.read_csv(f_tt_full, encoding='utf-8-sig', dtype=str).fillna("")
                    m_tt_find = pd.Series([False] * len(df_tt_tmp))
                    if ma_lk_curr:
                        m_tt_find = m_tt_find | (df_tt_tmp["Mã học sinh"] == ma_lk_curr)
                    if not m_tt_find.any() and hs_ten:
                        m_tt_find = (df_tt_tmp["Họ và tên"].str.strip().str.lower() == hs_ten.strip().lower()) & (df_tt_tmp["Lớp"].str.strip().str.upper() == lop_em.strip().upper())
                    if m_tt_find.any():
                        row_tt_self = df_tt_tmp[m_tt_find].iloc[0]
                except Exception:
                    pass

            # Giá trị khởi tạo
            ho_ten_init = str(row_hs_self.get("Họ và tên", hs_ten)) if row_hs_self is not None else (str(row_tt_self.get("Họ và tên", hs_ten)) if row_tt_self is not None else hs_ten)
            lop_init = str(row_hs_self.get("Lớp", lop_em)) if row_hs_self is not None else (str(row_tt_self.get("Lớp", lop_em)) if row_tt_self is not None else lop_em)
            sdt_hs_init = clean_phone_str(row_hs_self.get("SĐT Học sinh", "")) if row_hs_self is not None else (clean_phone_str(row_tt_self.get("SĐT Học sinh", "")) if row_tt_self is not None else clean_phone_str(u_curr.get("phone", "")))

            # Phụ huynh
            ten_bo_init = str(row_hs_self.get("Họ tên Bố", "")).replace("nan", "") if row_hs_self is not None else (str(row_tt_self.get("Tên cha", "")).replace("nan", "") if row_tt_self is not None else "")
            ten_me_init = str(row_hs_self.get("Họ tên Mẹ", "")).replace("nan", "") if row_hs_self is not None else (str(row_tt_self.get("Tên mẹ", "")).replace("nan", "") if row_tt_self is not None else "")
            sdt_ph_init = clean_phone_str(row_hs_self.get("SĐT Phụ huynh", "")) if row_hs_self is not None else (clean_phone_str(row_tt_self.get("SĐT Bố", row_tt_self.get("SĐT Mẹ", ""))) if row_tt_self is not None else "")

            # Địa chỉ
            thon_init = str(row_hs_self.get("Thôn", "")).replace("nan", "") if row_hs_self is not None else (str(row_tt_self.get("Thôn", "")).replace("nan", "") if row_tt_self is not None else "")
            xa_init = str(row_hs_self.get("Xã", "")).replace("nan", "") if row_hs_self is not None else (str(row_tt_self.get("Xã", "")).replace("nan", "") if row_tt_self is not None else "")

            # KTX
            day_init = str(row_hs_self.get("Dãy nhà", "Dãy Nam")).strip() if row_hs_self is not None else "Ngoại trú / Không ở KTX"
            phong_init = str(row_hs_self.get("Phòng", "Phòng 301")).strip() if row_hs_self is not None else "Không ở KTX"
            giuong_init = str(row_hs_self.get("Giường", "G-01")).strip() if row_hs_self is not None else "Không có"

            # Tìm phương tiện xe trong quan_ly_phuong_tien.csv
            f_xe_csv = os.path.join(BASE_DIR, "quan_ly_phuong_tien.csv") if os.path.exists(os.path.join(BASE_DIR, "quan_ly_phuong_tien.csv")) else "D:/quan_ly_phuong_tien.csv"
            df_xe_all_load = pd.read_csv(f_xe_csv, encoding='utf-8-sig', dtype=str).fillna("") if os.path.exists(f_xe_csv) else pd.DataFrame()
            
            row_xe_mine = None
            if not df_xe_all_load.empty:
                # Match họ tên và lớp
                m_xe1 = (df_xe_all_load["Họ và tên"].str.strip().str.lower() == ho_ten_init.strip().lower()) & (df_xe_all_load["Lớp"].str.strip().str.upper() == lop_init.strip().upper())
                if m_xe1.any():
                    row_xe_mine = df_xe_all_load[m_xe1].iloc[0]
                elif sdt_hs_init:
                    sdt_clean_xe = df_xe_all_load["SĐT Học sinh"].apply(clean_phone_str)
                    m_xe2 = (sdt_clean_xe == sdt_hs_init)
                    if m_xe2.any():
                        row_xe_mine = df_xe_all_load[m_xe2].iloc[0]

            bien_so_init = str(row_xe_mine.get("Biển số xe", "")).strip() if row_xe_mine is not None else ""
            loai_xe_init = str(row_xe_mine.get("Loại xe", "xe máy điện")).strip() if row_xe_mine is not None else "xe máy điện"
            hang_xe_init = str(row_xe_mine.get("Hãng xe", "")).strip() if row_xe_mine is not None else ""
            mau_xe_init = str(row_xe_mine.get("Màu xe", "")).strip() if row_xe_mine is not None else ""
            noi_de_init = str(row_xe_mine.get("Nơi gửi xe", "trong trường")).strip() if row_xe_mine is not None else "Trong trường"

            # Tạo 2 tab nhỏ bên trong: Tab Cập nhật hồ sơ & Tab Đề xuất cấp quyền
            tab_sub_hs1, tab_sub_hs2 = st.tabs([
                "📝 CẬP NHẬT HỒ SƠ & PHƯƠNG TIỆN CỦA EM",
                "📨 ĐỀ XUẤT CẤP QUYỀN (TRƯỞNG PHÒNG, CÁN BỘ LỚP, CỜ ĐỎ)"
            ])

            with tab_sub_hs1:
                with st.form("form_edit_hoc_sinh_profile_comprehensive"):
                    # 1. THÔNG TIN HỌC SINH
                    st.markdown("##### 1. 🎓 Thông Tin Học Sinh & Tài Khoản")
                    col_hs_1, col_hs_2 = st.columns(2)
                    with col_hs_1:
                        ho_ten_moi = st.text_input("Họ và tên của em:", value=ho_ten_init)
                        ds_lop_chuan = [
                            "10A1", "10A2", "10A3", "10A4", "10A5", "10A6", "10A7",
                            "11A1", "11A2", "11A3", "11A4", "11A5", "11A6", "11A7",
                            "12A1", "12A2", "12A3", "12A4", "12A5", "12A6", "12A7"
                        ]
                        idx_lop = ds_lop_chuan.index(lop_init) if lop_init in ds_lop_chuan else 0
                        lop_moi = st.selectbox("Lớp học:", ds_lop_chuan, index=idx_lop)
                    with col_hs_2:
                        sdt_hs_moi = st.text_input("Số điện thoại của em (10 số):", value=sdt_hs_init, placeholder="VD: 0988123456")
                        pw_hs_moi = st.text_input("Đổi mật khẩu mới (bỏ trống nếu giữ nguyên):", type="password")

                    st.markdown("---")
                    # 2. THÔNG TIN PHỤ HUYNH & ĐỊA CHỈ
                    st.markdown("##### 2. 👨‍👩‍👧 Thông Tin Phụ Huynh & Địa Chỉ Gia Đình")
                    col_ph_1, col_ph_2 = st.columns(2)
                    with col_ph_1:
                        ten_bo_moi = st.text_input("Họ tên Bố:", value=ten_bo_init, placeholder="Nhập họ tên Bố...")
                        ten_me_moi = st.text_input("Họ tên Mẹ:", value=ten_me_init, placeholder="Nhập họ tên Mẹ...")
                        sdt_ph_moi = st.text_input("Số điện thoại Phụ huynh liên hệ:", value=sdt_ph_init, placeholder="VD: 0912345678")
                    with col_ph_2:
                        thon_moi = st.text_input("Thôn / Bản thường trú:", value=thon_init, placeholder="VD: Thôn Tân Sơn...")
                        xa_moi = st.text_input("Xã / Thị trấn:", value=xa_init, placeholder="VD: Xã Bảo Hà...")

                    st.markdown("---")
                    # 3. THÔNG TIN KÝ TÚC XÁ / BÁN TRÚ
                    st.markdown("##### 3. 🏢 Cập Nhật Phòng Ở Bán Trú KTX")
                    col_ktx_1, col_ktx_2, col_ktx_3 = st.columns(3)
                    with col_ktx_1:
                        ds_day = ["Dãy Nam", "Dãy Nữ", "Ngoại trú / Không ở KTX"]
                        idx_day = ds_day.index(day_init) if day_init in ds_day else 0
                        day_nha_moi = st.selectbox("Dãy nhà KTX:", ds_day, index=idx_day)
                    with col_ktx_2:
                        ds_phong = [
                            "Phòng 205", "Phòng 207", "Phòng 208", 
                            "Phòng 301", "Phòng 302", "Phòng 303", "Phòng 304", "Phòng 305", "Phòng 306", "Phòng 307", "Phòng 308", 
                            "Phòng 401", "Phòng 402", "Phòng 403", "Phòng 404", "Phòng 405", "Phòng 406", "Phòng 407", "Phòng 408", 
                            "Không ở KTX"
                        ]
                        idx_p = ds_phong.index(phong_init) if phong_init in ds_phong else 0
                        phong_moi = st.selectbox("Phòng ở hiện tại:", ds_phong, index=idx_p)
                    with col_ktx_3:
                        ds_giuong = [f"G-{i:02d}" for i in range(1, 13)] + ["Không có"]
                        idx_g = ds_giuong.index(giuong_init) if giuong_init in ds_giuong else 0
                        giuong_moi = st.selectbox("Vị trí giường ngủ:", ds_giuong, index=idx_g)

                    st.markdown("---")
                    # 4. THÔNG TIN PHƯƠNG TIỆN CÁ NHÂN
                    st.markdown("##### 4. 🛵 Cập Nhật Thông Tin Phương Tiện Đi Lại & Nơi Để Xe")
                    if row_xe_mine is not None:
                        st.info(f"🚲 **Phương tiện hiện tại trên hệ thống:** Mã xe: **{row_xe_mine.get('Mã xe', '')}** | Biển số: **{bien_so_init}** | Nơi để xe: **{noi_de_init}**")
                    else:
                        st.warning("⚠️ Hiện tại em chưa có phương tiện đăng ký trên hệ thống. Em có thể điền thông tin bên dưới để đăng ký thẻ xe mã QR mới:")

                    col_xe_1, col_xe_2 = st.columns(2)
                    with col_xe_1:
                        bien_so_moi = st.text_input("Biển số xe của em:", value=bien_so_init, placeholder="VD: 24-AA 123.45 hoặc Chưa có biển")
                        ds_loai_xe = ["xe máy điện", "xe đạp điện", "xe máy", "xe đạp", "Khác"]
                        loai_xe_val_lower = loai_xe_init.lower()
                        idx_loai = 0
                        for idx_lx, lx in enumerate(ds_loai_xe):
                            if lx in loai_xe_val_lower:
                                idx_loai = idx_lx
                                break
                        loai_xe_moi = st.selectbox("Loại xe:", ds_loai_xe, index=idx_loai)
                        hang_xe_moi = st.text_input("Hãng xe / Thương hiệu:", value=hang_xe_init, placeholder="VD: VinFast, Espero, Honda, Favo...")
                    with col_xe_2:
                        mau_xe_moi = st.text_input("Màu sắc xe:", value=mau_xe_init, placeholder="VD: Đen, Đỏ, Trắng, Xanh...")
                        ds_noi_de = [
                            "Trong trường", 
                            "Gửi ngoài trường (Dũng Toan)", 
                            "Gửi ngoài trường (Cổng phụ)", 
                            "Gửi ngoài trường (Khác)", 
                            "Đi bộ / Không đi xe"
                        ]
                        idx_nd = 0
                        for idx_n, nd in enumerate(ds_noi_de):
                            if nd.lower() in noi_de_init.lower():
                                idx_nd = idx_n
                                break
                        noi_de_moi = st.selectbox("Nơi để xe hàng ngày:", ds_noi_de, index=idx_nd)

                    btn_luu_ho_so = st.form_submit_button("💾 LƯU & ĐỒNG BỘ TOÀN BỘ HỒ SƠ CỦA EM", type="primary", use_container_width=True)

                    if btn_luu_ho_so:
                        if not ho_ten_moi.strip():
                            st.error("❌ Họ và tên không được để trống!")
                        else:
                            # 1. CẬP NHẬT DANH SÁCH BÁN TRÚ NẾU CÓ
                            if row_hs_self is not None:
                                idx_hs_u = df_current[df_current["Mã HS"] == row_hs_self["Mã HS"]].index[0]
                                df_current.loc[idx_hs_u, "Họ và tên"] = ho_ten_moi.strip()
                                df_current.loc[idx_hs_u, "Lớp"] = lop_moi.strip()
                                if sdt_hs_moi.strip():
                                    df_current.loc[idx_hs_u, "SĐT Học sinh"] = clean_phone_str(sdt_hs_moi)
                                if ten_bo_moi.strip():
                                    df_current.loc[idx_hs_u, "Họ tên Bố"] = ten_bo_moi.strip()
                                if ten_me_moi.strip():
                                    df_current.loc[idx_hs_u, "Họ tên Mẹ"] = ten_me_moi.strip()
                                if sdt_ph_moi.strip():
                                    df_current.loc[idx_hs_u, "SĐT Phụ huynh"] = clean_phone_str(sdt_ph_moi)
                                if thon_moi.strip():
                                    df_current.loc[idx_hs_u, "Thôn"] = thon_moi.strip()
                                if xa_moi.strip():
                                    df_current.loc[idx_hs_u, "Xã"] = xa_moi.strip()
                                if day_nha_moi != "Ngoại trú / Không ở KTX":
                                    df_current.loc[idx_hs_u, "Dãy nhà"] = day_nha_moi
                                if phong_moi != "Không ở KTX":
                                    df_current.loc[idx_hs_u, "Phòng"] = phong_moi
                                if giuong_moi != "Không có":
                                    df_current.loc[idx_hs_u, "Giường"] = giuong_moi
                                
                                dong_bo_file_da_noi(df_current, [
                                    FILE_DU_LIEU_THUC_TE, 
                                    "D:/danh_sach_hoc_sinh_thuc_te.csv", 
                                    "D:/phan_mem_ban_tru_cloud/danh_sach_hoc_sinh_thuc_te.csv"
                                ])

                            # 2. CẬP NHẬT TOÀN TRƯỜNG
                            if os.path.exists(f_tt_full):
                                try:
                                    df_tt_up = pd.read_csv(f_tt_full, encoding='utf-8-sig', dtype=str).fillna("")
                                    m_tt_up = pd.Series([False] * len(df_tt_up))
                                    if ma_lk_curr:
                                        m_tt_up = m_tt_up | (df_tt_up["Mã học sinh"] == ma_lk_curr)
                                    if not m_tt_up.any():
                                        m_tt_up = (df_tt_up["Họ và tên"].str.strip().str.lower() == ho_ten_init.strip().lower()) & (df_tt_up["Lớp"].str.strip().str.upper() == lop_init.strip().upper())
                                    if m_tt_up.any():
                                        idx_tt_u = df_tt_up[m_tt_up].index[0]
                                        df_tt_up.loc[idx_tt_u, "Họ và tên"] = ho_ten_moi.strip()
                                        df_tt_up.loc[idx_tt_u, "Lớp"] = lop_moi.strip()
                                        if sdt_hs_moi.strip():
                                            df_tt_up.loc[idx_tt_u, "SĐT Học sinh"] = clean_phone_str(sdt_hs_moi)
                                        if ten_bo_moi.strip():
                                            df_tt_up.loc[idx_tt_u, "Tên cha"] = ten_bo_moi.strip()
                                        if ten_me_moi.strip():
                                            df_tt_up.loc[idx_tt_u, "Tên mẹ"] = ten_me_moi.strip()
                                        if sdt_ph_moi.strip():
                                            df_tt_up.loc[idx_tt_u, "SĐT Bố"] = clean_phone_str(sdt_ph_moi)
                                        if thon_moi.strip():
                                            df_tt_up.loc[idx_tt_u, "Thôn"] = thon_moi.strip()
                                        if xa_moi.strip():
                                            df_tt_up.loc[idx_tt_u, "Xã"] = xa_moi.strip()
                                        dong_bo_file_da_noi(df_tt_up, [
                                            f_tt_full, 
                                            "D:/phan_mem_ban_tru_cloud/danh_sach_hoc_sinh_toan_truong.csv"
                                        ])
                                except Exception:
                                    pass

                            # 3. CẬP NHẬT TÀI KHOẢN NGƯỜI DÙNG
                            if os.path.exists(FILE_TAI_KHOAN):
                                df_tk = pd.read_csv(FILE_TAI_KHOAN, encoding='utf-8-sig', dtype=str).fillna("")
                                m_tk = (df_tk["Tên đăng nhập"] == u_username)
                                if ma_lk_curr:
                                    m_tk = m_tk | (df_tk["Mã liên kết"] == ma_lk_curr)
                                if m_tk.any():
                                    df_tk.loc[m_tk, "Họ và tên"] = ho_ten_moi.strip()
                                    df_tk.loc[m_tk, "Đơn vị / Lớp"] = lop_moi.strip()
                                    if sdt_hs_moi.strip():
                                        df_tk.loc[m_tk, "Số điện thoại"] = clean_phone_str(sdt_hs_moi)
                                    if pw_hs_moi.strip() and len(pw_hs_moi.strip()) >= 4:
                                        df_tk.loc[m_tk, "Mật khẩu"] = pw_hs_moi.strip()

                                # Cập nhật tài khoản phụ huynh nếu có
                                ten_ph_update = ten_bo_moi.strip() if ten_bo_moi.strip() else ten_me_moi.strip()
                                m_ph_tk = (df_tk["Tên đăng nhập"] == f"ph_{u_username}")
                                if ma_lk_curr:
                                    m_ph_tk = m_ph_tk | ((df_tk["Vai trò"] == "Phụ huynh") & (df_tk["Mã liên kết"] == ma_lk_curr))
                                if m_ph_tk.any():
                                    if ten_ph_update:
                                        df_tk.loc[m_ph_tk, "Họ và tên"] = f"PH em {ho_ten_moi.strip()} ({ten_ph_update})"
                                    if sdt_ph_moi.strip():
                                        df_tk.loc[m_ph_tk, "Số điện thoại"] = clean_phone_str(sdt_ph_moi)

                                dong_bo_file_da_noi(df_tk, [
                                    FILE_TAI_KHOAN, 
                                    "D:/tai_khoan_nguoi_dung.csv", 
                                    "D:/phan_mem_ban_tru_cloud/tai_khoan_nguoi_dung.csv"
                                ])

                            # 4. CẬP NHẬT PHƯƠNG TIỆN XE & NƠI ĐỂ XE (quan_ly_phuong_tien.csv)
                            if os.path.exists(f_xe_csv):
                                df_xe_save = pd.read_csv(f_xe_csv, encoding='utf-8-sig', dtype=str).fillna("")
                                ten_ph_xe = ten_bo_moi.strip() if ten_bo_moi.strip() else (ten_me_moi.strip() if ten_me_moi.strip() else "Phụ huynh")
                                sdt_ph_xe = clean_phone_str(sdt_ph_moi)
                                sdt_hs_xe = clean_phone_str(sdt_hs_moi)

                                m_xe_ex = pd.Series([False] * len(df_xe_save))
                                if row_xe_mine is not None and "Mã xe" in row_xe_mine:
                                    m_xe_ex = (df_xe_save["Mã xe"] == row_xe_mine["Mã xe"])
                                if not m_xe_ex.any():
                                    m_xe_ex = (df_xe_save["Họ và tên"].str.strip().str.lower() == ho_ten_init.strip().lower()) & (df_xe_save["Lớp"].str.strip().str.upper() == lop_init.strip().upper())

                                if m_xe_ex.any():
                                    idx_xe_target = df_xe_save[m_xe_ex].index[0]
                                    df_xe_save.loc[idx_xe_target, "Họ và tên"] = ho_ten_moi.strip()
                                    df_xe_save.loc[idx_xe_target, "Lớp"] = lop_moi.strip()
                                    df_xe_save.loc[idx_xe_target, "Biển số xe"] = bien_so_moi.strip() if bien_so_moi.strip() else "Chưa có biển"
                                    df_xe_save.loc[idx_xe_target, "Loại xe"] = loai_xe_moi.strip()
                                    df_xe_save.loc[idx_xe_target, "Hãng xe"] = hang_xe_moi.strip()
                                    df_xe_save.loc[idx_xe_target, "Màu xe"] = mau_xe_moi.strip()
                                    df_xe_save.loc[idx_xe_target, "Nơi gửi xe"] = noi_de_moi.strip()
                                    if sdt_hs_xe:
                                        df_xe_save.loc[idx_xe_target, "SĐT Học sinh"] = sdt_hs_xe
                                    if ten_ph_xe:
                                        df_xe_save.loc[idx_xe_target, "Họ tên Phụ huynh"] = ten_ph_xe
                                    if sdt_ph_xe:
                                        df_xe_save.loc[idx_xe_target, "SĐT Phụ huynh"] = sdt_ph_xe
                                elif bien_so_moi.strip() or noi_de_moi != "Đi bộ / Không đi xe":
                                    # Tạo mã xe mới
                                    max_num = 0
                                    for mx in df_xe_save["Mã xe"]:
                                        m_num = re.search(r'\d+', str(mx))
                                        if m_num:
                                            max_num = max(max_num, int(m_num.group(0)))
                                    ma_xe_new = f"XE-{max_num + 1:03d}"
                                    dong_xe_moi = {
                                        "Mã xe": ma_xe_new,
                                        "Họ và tên": ho_ten_moi.strip(),
                                        "Lớp": lop_moi.strip(),
                                        "Loại xe": loai_xe_moi.strip(),
                                        "Hãng xe": hang_xe_moi.strip(),
                                        "Màu xe": mau_xe_moi.strip(),
                                        "Biển số xe": bien_so_moi.strip() if bien_so_moi.strip() else "Chưa có biển",
                                        "SĐT Học sinh": sdt_hs_xe,
                                        "GVCN": "",
                                        "SĐT GVCN": "",
                                        "Họ tên Phụ huynh": ten_ph_xe,
                                        "SĐT Phụ huynh": sdt_ph_xe,
                                        "Nơi gửi xe": noi_de_moi.strip(),
                                        "Địa chỉ": f"{thon_moi.strip()}, {xa_moi.strip()}",
                                        "Tình trạng": "Đủ điều kiện lưu hành",
                                        "Số lần vi phạm": "0",
                                        "Ghi chú": "Học sinh tự cập nhật trên Cổng thông tin"
                                    }
                                    df_xe_save = pd.concat([df_xe_save, pd.DataFrame([dong_xe_moi])], ignore_index=True)

                                dong_bo_file_da_noi(df_xe_save, [
                                    f_xe_csv, 
                                    "D:/quan_ly_phuong_tien.csv", 
                                    "D:/phan_mem_ban_tru_cloud/quan_ly_phuong_tien.csv"
                                ])

                            st.success("🎉 ĐÃ CẬP NHẬT THÀNH CÔNG TOÀN BỘ HỒ SƠ & PHƯƠNG TIỆN CỦA EM! Dữ liệu đã được đồng bộ liên thông.")
                            st.balloons()
                            st.rerun()

            # TAB SUB 2: ĐỀ XUẤT CẤP QUYỀN
            with tab_sub_hs2:
                st.markdown("#### 📨 Đề Xuất Cấp Quyền / Bổ Nhiệm Chức Vụ")
                st.info("💡 **Gửi nguyện vọng nhận nhiệm vụ:** Em có thể gửi đề xuất nhận nhiệm vụ (Trưởng phòng KTX, Lớp trưởng, Bí thư chi đoàn, Đội Cờ đỏ xung kích...) để Ban Giám Hiệu xem xét và phê duyệt.")

                f_req_cap = os.path.join(BASE_DIR, "de_xuat_cap_quyen.csv") if os.path.exists(os.path.join(BASE_DIR, "de_xuat_cap_quyen.csv")) else "D:/de_xuat_cap_quyen.csv"
                df_req_all = pd.read_csv(f_req_cap, encoding='utf-8-sig', dtype=str).fillna("") if os.path.exists(f_req_cap) else pd.DataFrame(columns=["Mã yêu cầu", "Tên đăng nhập", "Họ và tên", "Quyền xin cấp", "Lý do", "Ngày gửi", "Trạng thái"])

                # Lịch sử đề xuất của em
                my_reqs = df_req_all[
                    (df_req_all["Tên đăng nhập"] == u_username) | 
                    (df_req_all["Họ và tên"].str.strip().str.lower() == ho_ten_init.strip().lower())
                ]
                if not my_reqs.empty:
                    st.markdown("##### 📋 Lịch Sử Đề Xuất Của Em:")
                    for _, r_rq in my_reqs.iterrows():
                        tt = r_rq.get('Trạng thái', 'Chờ duyệt')
                        if "đã duyệt" in tt.lower() or "chấp thuận" in tt.lower():
                            c_icon = "🟢"
                        elif "từ chối" in tt.lower():
                            c_icon = "🔴"
                        else:
                            c_icon = "⏳"
                        st.markdown(f"""
                        <div style="background:#F8FAFC; border-left:4px solid #0284C7; padding:10px 14px; border-radius:6px; margin-bottom:8px;">
                            <b>{c_icon} {r_rq.get('Mã yêu cầu', '')}:</b> Xin cấp quyền <b>{r_rq.get('Quyền xin cấp', '')}</b> | <b>Trạng thái:</b> <code>{tt}</code> | Ngày gửi: {r_rq.get('Ngày gửi', '')}<br>
                            <span style="font-size:12.5px; color:#4B5563;">💬 <i>Lý do:</i> {r_rq.get('Lý do', '')}</span>
                        </div>
                        """, unsafe_allow_html=True)
                    st.markdown("---")

                with st.form("form_hoc_sinh_de_xuat_quyen"):
                    st.markdown("##### ✍️ Gửi Đề Xuất Nhận Nhiệm Vụ Mới:")
                    opt_quyen_hs = [
                        "Trưởng phòng KTX (Quản lý phòng 5S & Báo vắng 4 khung giờ)",
                        "Lớp trưởng (Đánh giá vi phạm phương tiện xe & Nề nếp)",
                        "Bí thư chi đoàn (Đánh giá phương tiện xe & Hoạt động Đoàn)",
                        "Đội viên Cờ đỏ xung kích toàn trường",
                        "Ban Quản lý Bán trú học sinh",
                        "Khác (Ghi rõ trong nội dung lý do)"
                    ]
                    quyen_de_xuat_chon = st.selectbox("Chức danh / Quyền hạn em muốn đề xuất:", opt_quyen_hs)
                    ly_do_de_xuat = st.text_area("Lý do & Nguyện vọng nhận nhiệm vụ:", placeholder="Trình bày lý do, kinh nghiệm hoặc mong muốn cống hiến để Ban Giám Hiệu xem xét...")
                    btn_gui_dx = st.form_submit_button("📨 GỬI ĐỀ XUẤT LÊN BAN GIÁM HIỆU", type="primary", use_container_width=True)

                    if btn_gui_dx:
                        if not ly_do_de_xuat.strip():
                            st.warning("⚠️ Em vui lòng viết rõ lý do / nguyện vọng để Ban Giám Hiệu có căn cứ phê duyệt nhé.")
                        else:
                            ma_yc_moi = f"YC-{len(df_req_all) + 1:03d}"
                            ngay_gui_str = datetime.now().strftime("%d/%m/%Y %H:%M")
                            dong_yc_moi = {
                                "Mã yêu cầu": ma_yc_moi,
                                "Tên đăng nhập": u_username,
                                "Họ và tên": ho_ten_init,
                                "Quyền xin cấp": quyen_de_xuat_chon,
                                "Ly do": ly_do_de_xuat.strip(),
                                "Ngày gửi": ngay_gui_str,
                                "Trạng thái": "Chờ duyệt ⏳"
                            }
                            df_req_all = pd.concat([df_req_all, pd.DataFrame([dong_yc_moi])], ignore_index=True)
                            dong_bo_file_da_noi(df_req_all, [
                                f_req_cap, 
                                "D:/de_xuat_cap_quyen.csv", 
                                "D:/phan_mem_ban_tru_cloud/de_xuat_cap_quyen.csv"
                            ])
                            st.success(f"🎉 ĐÃ GỬI ĐỀ XUẤT ({ma_yc_moi}) TỚI BAN GIÁM HIỆU THÀNH CÔNG! Thầy Hiệu trưởng và Ban Giám Hiệu sẽ sớm xem xét và phê duyệt.")
                            st.balloons()
                            st.rerun()

        # TAB: THỰC ĐƠN HÔM NAY
    # =========================================================================
    if "🥗 THỰC ĐƠN HÔM NAY" in tab_map:
        with tab_map["🥗 THỰC ĐƠN HÔM NAY"]:
            st.markdown("#### 🍲 Thực Đơn Bữa Ăn Hôm Nay Tại Ký Túc Xá:")
            if os.path.exists(FILE_THUC_DON):
                df_td_v = pd.read_csv(FILE_THUC_DON, encoding='utf-8-sig')
                st.dataframe(df_td_v, use_container_width=True, hide_index=True)

# -*- coding: utf-8 -*-
"""
PHÂN HỆ 1: QUẢN LÝ CHUNG & ĐIỀU HÀNH NHÀ TRƯỜNG
Trường THPT số 2 Bảo Yên - Xã Bảo Hà, Huyện Bảo Yên, Tỉnh Lào Cai
"""

import os
import streamlit as st
import pandas as pd
from datetime import datetime, date

def render_phan_he_quan_ly_chung(df_tai_khoan, role_curr, nam_hoc, BASE_DIR, THU_MUC_NAM_HOC):
    st.markdown("""
        <div style='background: linear-gradient(135deg, #1E3A8A, #3B82F6); padding: 18px 24px; border-radius: 12px; color: white; margin-bottom: 20px;'>
            <h2 style='margin:0; font-size: 24px; color: white;'>🏛️ HỆ THỐNG QUẢN TRỊ & ĐIỀU HÀNH NHÀ TRƯỜNG</h2>
            <p style='margin: 4px 0 0 0; opacity: 0.9; font-size: 14px;'>
                Trường THPT số 2 Bảo Yên (Bảo Hà, Lào Cai) • Năm học: <b>{}</b>
            </p>
        </div>
    """.format(nam_hoc), unsafe_allow_html=True)

    folder_nam = nam_hoc.replace(" ", "")
    dir_nam = os.path.join(THU_MUC_NAM_HOC, folder_nam)
    f_lct = os.path.join(dir_nam, "lich_cong_tac_tuan.csv")
    f_tb = os.path.join(dir_nam, "thong_bao_nha_truong.csv")

    tab_tong_quan, tab_lich_tuan, tab_danh_ba, tab_bieu_mau = st.tabs([
        "🏫 TỔNG QUAN TRƯỜNG LỚP",
        "📅 LỊCH CÔNG TÁC TUẦN",
        "👥 DANH BẠ HỘI ĐỒNG SƯ PHẠM",
        "📂 VĂN BẢN & BIỂU MẪU"
    ])

    # ----------------------------------------------------
    # TAB 1: TỔNG QUAN TRƯỜNG LỚP
    # ----------------------------------------------------
    with tab_tong_quan:
        st.subheader("🏫 Quy Mô & Cơ Cấu Tổ Chức Nhà Trường")
        
        # Thống kê nhanh
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.metric("🏫 Tổng số lớp", "20 Lớp", "Khối 10, 11, 12")
        with c2:
            st.metric("👨‍🎓 Tổng số học sinh", "840 Học sinh", "Toàn trường")
        with c3:
            st.metric("🛏️ Học sinh bán trú", "207 Em", "KTX 19 phòng")
        with c4:
            st.metric("👨‍🏫 Cán bộ, GV, NV", "58 Thầy/Cô", "4 Tổ chuyên môn")

        st.markdown("---")
        
        col_info1, col_info2 = st.columns([1.2, 1])
        with col_info1:
            st.markdown("#### 🏢 Thông Tin Đơn Vị:")
            st.markdown("""
            * **Tên đơn vị:** Trường THPT số 2 Bảo Yên
            * **Địa chỉ:** Xã Bảo Hà, huyện Bảo Yên, tỉnh Lào Cai
            * **Đặc thù trường:** Trường THPT vùng cao có đông học sinh con em đồng bào các dân tộc thiểu số và học sinh bán trú ăn ở tập trung tại Ký túc xá.
            * **Cơ cấu khối lớp (20 Lớp):**
              - **Khối 10 (6 Lớp):** 10A1, 10A2, 10A3, 10A4, 10A6, 10A7 (~255 học sinh)
              - **Khối 11 (7 Lớp):** 11A1, 11A2, 11A3, 11A4, 11A5, 11A6, 11A7 (~295 học sinh)
              - **Khối 12 (7 Lớp):** 12A1, 12A2, 12A3, 12A4, 12A5, 12A6, 12A7 (~290 học sinh)
            """)

        with col_info2:
            st.markdown("#### 👑 Ban Lãnh Đạo & Điều Hành:")
            st.info("""
            * **Hiệu trưởng:** Thầy Bùi Văn Tiến (Phụ trách chung)
            * **Phó Hiệu trưởng 1:** Thầy/Cô PHT PT Bán trú & Cơ sở vật chất
            * **Phó Hiệu trưởng 2:** Thầy/Cô PHT PT Chuyên môn & Khảo thí
            * **Chủ tịch Công đoàn:** Thầy/Cô CTCĐ
            * **Bí thư Đoàn trường:** Thầy/Cô Bí thư Đoàn TNCS Hồ Chí Minh
            * **Tổ trưởng Bán trú:** Thầy Quản nhiệm KTX
            """)

        # Bảng tổng hợp quy mô 20 lớp
        st.markdown("#### 📋 Bảng Thống Kê Sĩ Số 20 Lớp Học Năm Học " + nam_hoc)
        classes_data = [
            {"Khối": "Khối 10", "Lớp": "10A1", "Sĩ số": 43, "Nữ": 24, "Dân tộc": 39, "Ở bán trú": 18, "GVCN": "Thầy/Cô GVCN 10A1"},
            {"Khối": "Khối 10", "Lớp": "10A2", "Sĩ số": 42, "Nữ": 21, "Dân tộc": 38, "Ở bán trú": 15, "GVCN": "Thầy/Cô GVCN 10A2"},
            {"Khối": "Khối 10", "Lớp": "10A3", "Sĩ số": 43, "Nữ": 23, "Dân tộc": 40, "Ở bán trú": 16, "GVCN": "Thầy/Cô GVCN 10A3"},
            {"Khối": "Khối 10", "Lớp": "10A4", "Sĩ số": 42, "Nữ": 22, "Dân tộc": 37, "Ở bán trú": 14, "GVCN": "Thầy/Cô GVCN 10A4"},
            {"Khối": "Khối 10", "Lớp": "10A6", "Sĩ số": 43, "Nữ": 25, "Dân tộc": 41, "Ở bán trú": 17, "GVCN": "Thầy/Cô GVCN 10A6"},
            {"Khối": "Khối 10", "Lớp": "10A7", "Sĩ số": 42, "Nữ": 20, "Dân tộc": 39, "Ở bán trú": 15, "GVCN": "Thầy/Cô GVCN 10A7"},
            {"Khối": "Khối 11", "Lớp": "11A1", "Sĩ số": 42, "Nữ": 23, "Dân tộc": 36, "Ở bán trú": 12, "GVCN": "Thầy/Cô GVCN 11A1"},
            {"Khối": "Khối 11", "Lớp": "11A2", "Sĩ số": 41, "Nữ": 21, "Dân tộc": 38, "Ở bán trú": 11, "GVCN": "Thầy/Cô GVCN 11A2"},
            {"Khối": "Khối 11", "Lớp": "11A3", "Sĩ số": 43, "Nữ": 24, "Dân tộc": 39, "Ở bán trú": 10, "GVCN": "Thầy/Cô GVCN 11A3"},
            {"Khối": "Khối 11", "Lớp": "11A4", "Sĩ số": 42, "Nữ": 22, "Dân tộc": 37, "Ở bán trú": 9, "GVCN": "Thầy/Cô GVCN 11A4"},
            {"Khối": "Khối 11", "Lớp": "11A5", "Sĩ số": 42, "Nữ": 20, "Dân tộc": 40, "Ở bán trú": 10, "GVCN": "Thầy/Cô GVCN 11A5"},
            {"Khối": "Khối 11", "Lớp": "11A6", "Sĩ số": 43, "Nữ": 25, "Dân tộc": 38, "Ở bán trú": 11, "GVCN": "Thầy/Cô GVCN 11A6"},
            {"Khối": "Khối 11", "Lớp": "11A7", "Sĩ số": 42, "Nữ": 21, "Dân tộc": 39, "Ở bán trú": 8, "GVCN": "Thầy/Cô GVCN 11A7"},
            {"Khối": "Khối 12", "Lớp": "12A1", "Sĩ số": 41, "Nữ": 22, "Dân tộc": 35, "Ở bán trú": 7, "GVCN": "Thầy/Cô GVCN 12A1"},
            {"Khối": "Khối 12", "Lớp": "12A2", "Sĩ số": 42, "Nữ": 23, "Dân tộc": 36, "Ở bán trú": 8, "GVCN": "Thầy/Cô GVCN 12A2"},
            {"Khối": "Khối 12", "Lớp": "12A3", "Sĩ số": 41, "Nữ": 21, "Dân tộc": 37, "Ở bán trú": 7, "GVCN": "Thầy/Cô GVCN 12A3"},
            {"Khối": "Khối 12", "Lớp": "12A4", "Sĩ số": 42, "Nữ": 24, "Dân tộc": 38, "Ở bán trú": 6, "GVCN": "Thầy/Cô GVCN 12A4"},
            {"Khối": "Khối 12", "Lớp": "12A5", "Sĩ số": 41, "Nữ": 20, "Dân tộc": 36, "Ở bán trú": 7, "GVCN": "Thầy/Cô GVCN 12A5"},
            {"Khối": "Khối 12", "Lớp": "12A6", "Sĩ số": 42, "Nữ": 22, "Dân tộc": 39, "Ở bán trú": 6, "GVCN": "Thầy/Cô GVCN 12A6"},
            {"Khối": "Khối 12", "Lớp": "12A7", "Sĩ số": 41, "Nữ": 21, "Dân tộc": 38, "Ở bán trú": 6, "GVCN": "Thầy/Cô GVCN 12A7"},
        ]
        df_classes = pd.DataFrame(classes_data)
        st.dataframe(df_classes, use_container_width=True, hide_index=True)

    # ----------------------------------------------------
    # TAB 2: LỊCH CÔNG TÁC TUẦN
    # ----------------------------------------------------
    with tab_lich_tuan:
        st.subheader("📅 Lịch Công Tác Tuần & Lịch Trực Nhà Trường")
        st.caption("Cập nhật lịch công tác chỉ đạo của Ban Giám Hiệu và các hoạt động chuyên môn toàn trường.")
        
        if os.path.exists(f_lct):
            df_lct_curr = pd.read_csv(f_lct, encoding='utf-8-sig').fillna("")
            st.dataframe(df_lct_curr, use_container_width=True, hide_index=True)
        else:
            st.info("Chưa có dữ liệu lịch công tác tuần cho năm học này.")

        # Quyền BGH: Thêm / cập nhật lịch
        if role_curr == "Ban Giám hiệu":
            with st.expander("➕ **Cập nhật thêm nội dung lịch công tác tuần:**", expanded=False):
                with st.form("form_them_lich_tuan"):
                    c_thu, c_time = st.columns([1, 1])
                    with c_thu:
                        f_thu = st.selectbox("Thứ trong tuần:", ["Thứ Hai", "Thứ Ba", "Thứ Tư", "Thứ Năm", "Thứ Sáu", "Thứ Bảy", "Chủ Nhật"])
                    with c_time:
                        f_time = st.text_input("Thời gian:", value="08:00")
                    f_nd = st.text_area("Nội dung công việc:", placeholder="Nhập tóm tắt công việc...")
                    c_ct, c_dd = st.columns([1, 1])
                    with c_ct:
                        f_ct = st.text_input("Chủ trì:", value="Ban Giám Hiệu")
                    with c_dd:
                        f_dd = st.text_input("Địa điểm:", value="Phòng họp HĐSP")
                    f_tp = st.text_input("Thành phần tham gia:", value="Toàn thể CB, GV, NV")
                    
                    btn_them_lct = st.form_submit_button("💾 LƯU LỊCH CÔNG TÁC MỚI", type="primary", use_container_width=True)
                    if btn_them_lct:
                        if not f_nd.strip():
                            st.warning("Vui lòng nhập nội dung công việc!")
                        else:
                            new_row = pd.DataFrame([{
                                'Thứ': f_thu,
                                'Thời gian': f_time.strip(),
                                'Nội dung công việc': f_nd.strip(),
                                'Chủ trì': f_ct.strip(),
                                'Địa điểm': f_dd.strip(),
                                'Thành phần': f_tp.strip()
                            }])
                            df_lct_new = pd.concat([df_lct_curr, new_row], ignore_index=True) if os.path.exists(f_lct) else new_row
                            df_lct_new.to_csv(f_lct, index=False, encoding='utf-8-sig')
                            st.success("🎉 Đã lưu lịch công tác tuần thành công!")
                            st.rerun()

    # ----------------------------------------------------
    # TAB 3: DANH BẠ HỘI ĐỒNG SƯ PHẠM
    # ----------------------------------------------------
    with tab_danh_ba:
        st.subheader("👥 Danh Bạ Cán Bộ - Giáo Viên - Nhân Viên")
        st.caption("Tra cứu thông tin liên hệ, chức danh và tổ chuyên môn trong nhà trường.")
        
        df_staff_tk = df_tai_khoan[df_tai_khoan["Vai trò"].isin(["Ban Giám hiệu", "Giáo viên quản lý", "Kế toán bán trú", "Nhà bếp / Cấp dưỡng", "Ban Chấp hành Đoàn"])]
        
        search_gv = st.text_input("🔍 Tìm nhanh cán bộ / giáo viên (Tên, Chức danh, SĐT):", "")
        df_show_gv = df_staff_tk.copy()
        if search_gv:
            df_show_gv = df_show_gv[
                df_show_gv["Họ và tên"].str.contains(search_gv, case=False, na=False) |
                df_show_gv["Chức danh"].str.contains(search_gv, case=False, na=False) |
                df_show_gv["Số điện thoại"].astype(str).str.contains(search_gv, na=False)
            ]
            
        st.dataframe(
            df_show_gv[["Họ và tên", "Chức danh", "Vai trò", "Mã liên kết", "Số điện thoại", "Ghi chú"]],
            use_container_width=True,
            hide_index=True
        )

    # ----------------------------------------------------
    # TAB 4: VĂN BẢN & BIỂU MẪU
    # ----------------------------------------------------
    with tab_bieu_mau:
        st.subheader("📂 Kho Biểu Mẫu & Văn Bản Điều Hành")
        st.markdown("""
        * 📄 **Quy chế Quản lý Bán trú & KTX:** Số 01/QC-THPT2BY ban hành kèm theo Quyết định của Hiệu trưởng.
        * 📄 **Nội quy Học sinh & Tiêu chí Thi đua Đoàn trường:** Quy định đồng phục, tác phong và chấm điểm nề nếp 20 chi đoàn.
        * 📄 **Mẫu Đơn xin về cuối tuần (Dành cho học sinh & phụ huynh):** Tải về hoặc tạo đơn trực tiếp trên phần mềm.
        * 📄 **Sổ Nhật ký Kiểm thực 3 bước:** Theo quy định an toàn vệ sinh thực phẩm Bộ Y tế.
        """)
        st.success("💡 Toàn bộ các quy trình trên đã được số hóa trực tiếp vào các tab chức năng của phần mềm!")

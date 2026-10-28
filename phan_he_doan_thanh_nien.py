# -*- coding: utf-8 -*-
"""
PHÂN HỆ 3: ĐOÀN THANH NIÊN (ĐTN) & NỀ NẾP HỌC SINH
Trường THPT số 2 Bảo Yên - Xã Bảo Hà, Huyện Bảo Yên, Tỉnh Lào Cai
"""

import os
import streamlit as st
import pandas as pd
from datetime import datetime, date

def render_phan_he_doan_thanh_nien(df_tai_khoan, role_curr, nam_hoc, BASE_DIR, THU_MUC_NAM_HOC):
    st.markdown("""
        <div style='background: linear-gradient(135deg, #059669, #10B981); padding: 18px 24px; border-radius: 12px; color: white; margin-bottom: 20px;'>
            <h2 style='margin:0; font-size: 24px; color: white;'>🚩 ĐOÀN THANH NIÊN (ĐTN) & NỀ NẾP HỌC SINH</h2>
            <p style='margin: 4px 0 0 0; opacity: 0.95; font-size: 14px;'>
                Đoàn TNCS Hồ Chí Minh - Trường THPT số 2 Bảo Yên • Năm học: <b>{}</b>
            </p>
        </div>
    """.format(nam_hoc), unsafe_allow_html=True)

    folder_nam = nam_hoc.replace(" ", "")
    dir_nam = os.path.join(THU_MUC_NAM_HOC, folder_nam)
    f_dtn_td = os.path.join(dir_nam, "thi_dua_dtn_20_lop.csv")
    f_dtn_dv = os.path.join(dir_nam, "danh_sach_doan_vien.csv")

    tab_bang_vang, tab_cham_diem, tab_doan_vien, tab_phong_trao = st.tabs([
        "🏆 BẢNG VÀNG THI ĐUA 20 CHI ĐOÀN",
        "✍️ CHẤM ĐIỂM NỀ NẾP TUẦN",
        "🎗️ QUẢN LÝ ĐOÀN VIÊN & SỔ ĐOÀN",
        "🎪 KẾ HOẠCH & PHONG TRÀO"
    ])

    # ----------------------------------------------------
    # TAB 1: BẢNG VÀNG THI ĐUA 20 CHI ĐOÀN
    # ----------------------------------------------------
    with tab_bang_vang:
        st.subheader("🏆 Bảng Xếp Hạng Thi Đua Nề Nếp Các Chi Đoàn")
        st.caption("Tổng hợp tự động từ kết quả chấm nề nếp hàng ngày của Đội Cờ Đỏ và Ban Chấp Hành Đoàn Trường.")

        if os.path.exists(f_dtn_td):
            df_td = pd.read_csv(f_dtn_td, encoding='utf-8-sig').fillna("")
            
            # Đảm bảo các cột số tính toán đúng
            for col in ['Điểm gốc', 'Chuyên cần', 'Đồng phục', 'Vệ sinh', 'Truy bài', 'Xếp hàng', 'Điểm cộng', 'Điểm trừ', 'Tổng điểm']:
                if col in df_td.columns:
                    df_td[col] = pd.to_numeric(df_td[col], errors='coerce').fillna(0)

            # Sắp xếp và tính hạng
            df_td['Xếp hạng'] = df_td['Tổng điểm'].rank(ascending=False, method='min').astype(int)
            df_td = df_td.sort_values(by=['Tổng điểm', 'Điểm cộng'], ascending=[False, False])

            # Top 3 vinh danh cờ luân lưu
            if len(df_td) >= 3:
                top1 = df_td.iloc[0]
                top2 = df_td.iloc[1]
                top3 = df_td.iloc[2]
                
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

            # Bộ lọc khối
            chon_khoi = st.selectbox("🔍 Lọc theo khối:", ["Tất cả 20 Chi đoàn", "Khối 10", "Khối 11", "Khối 12"])
            df_view = df_td.copy()
            if chon_khoi != "Tất cả 20 Chi đoàn":
                df_view = df_view[df_view['Khối'] == chon_khoi.replace("Khối ", "")]

            st.dataframe(
                df_view[['Xếp hạng', 'Chi đoàn', 'Khối', 'Điểm gốc', 'Điểm cộng', 'Điểm trừ', 'Tổng điểm', 'Xếp loại', 'Ghi chú']],
                use_container_width=True,
                hide_index=True
            )

            # Tải bảng điểm Excel
            csv_td_bytes = df_td.to_csv(index=False, encoding='utf-8-sig').encode('utf-8-sig')
            st.download_button(
                label="📥 TẢI BẢNG XẾP HẠNG THI ĐUA ĐTN (EXCEL / CSV)",
                data=csv_td_bytes,
                file_name=f"bang_thi_dua_dtn_thpt2_baoyen_{nam_hoc.replace(' ', '')}.csv",
                mime="text/csv",
                use_container_width=True
            )
        else:
            st.info("Chưa có dữ liệu thi đua ĐTN cho năm học này.")

    # ----------------------------------------------------
    # TAB 2: CHẤM ĐIỂM NỀ NẾP TUẦN
    # ----------------------------------------------------
    with tab_cham_diem:
        st.subheader("✍️ Cập Nhật Điểm Nề Nếp Cho Từng Chi Đoàn")
        st.caption("Dành cho Ban Chấp Hành Đoàn Trường, Đội Cờ Đỏ và Giáo viên chủ nhiệm.")

        if os.path.exists(f_dtn_td):
            df_td_edit = pd.read_csv(f_dtn_td, encoding='utf-8-sig').fillna("")
            ds_lop = sorted(list(df_td_edit['Chi đoàn'].unique()))

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

                        # Lưu file
                        df_td_edit.to_csv(f_dtn_td, index=False, encoding='utf-8-sig')

                        # Đồng bộ sang các vị trí khác
                        for dest_dir in ['D:/phan_mem_ban_tru_cloud/du_lieu_nam_hoc', 'd:/OneDrive/Hô sơ cá nhan/Học AI/du_lieu_nam_hoc']:
                            p_sync = os.path.join(dest_dir, folder_nam, 'thi_dua_dtn_20_lop.csv')
                            if os.path.exists(os.path.dirname(p_sync)):
                                try:
                                    df_td_edit.to_csv(p_sync, index=False, encoding='utf-8-sig')
                                except Exception:
                                    pass

                        st.success(f"🎉 Đã cập nhật thành công điểm thi đua cho Chi đoàn {lop_duoc_chon}! Tổng điểm: {tong_diem_moi} điểm.")
                        st.rerun()

    # ----------------------------------------------------
    # TAB 3: QUẢN LÝ ĐOÀN VIÊN & SỔ ĐOÀN
    # ----------------------------------------------------
    with tab_doan_vien:
        st.subheader("🎗️ Quản Lý Đoàn Viên & Sổ Đoàn 20 Chi Đoàn")
        st.caption("Theo dõi số lượng Đoàn viên, hồ sơ Sổ Đoàn và danh sách bồi dưỡng kết nạp Đoàn viên mới.")

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
        else:
            st.info("Chưa có dữ liệu danh sách Đoàn viên.")

    # ----------------------------------------------------
    # TAB 4: KẾ HOẠCH & PHONG TRÀO
    # ----------------------------------------------------
    with tab_phong_trao:
        st.subheader("🎪 Kế Hoạch Hoạt Động & Sự Kiện Thanh Niên")
        st.caption("Các chương trình công tác Đoàn và phong trào thanh niên trường học năm học " + nam_hoc)

        phong_trao_list = [
            {"Thời gian": "Tháng 10 - 11", "Tên hoạt động": "Hội thi làm Báo tường & Phong trào 'Hoa điểm tốt dâng Thầy Cô'", "Mục đích": "Chào mừng Ngày Nhà giáo Việt Nam 20/11", "Đơn vị thực hiện": "20 Chi đoàn toàn trường", "Trạng thái": "Đang diễn ra 🔥"},
            {"Thời gian": "Tháng 12", "Tên hoạt động": "Chiến dịch Tình nguyện Mùa Đông & Chăm sóc Nghĩa trang Liệt sĩ", "Mục đích": "Kỷ niệm ngày thành lập QĐND Việt Nam 22/12", "Đơn vị thực hiện": "BCH Đoàn trường & Đội TNV", "Trạng thái": "Sắp diễn ra"},
            {"Thời gian": "Tháng 01", "Tên hoạt động": "Chương trình 'Tết ấm tình thương' tặng quà học sinh khó khăn", "Mục đích": "Hỗ trợ học sinh nghèo vượt khó đón Tết", "Đơn vị thực hiện": "Đoàn trường & Quỹ Bán trú", "Trạng thái": "Kế hoạch"},
            {"Thời gian": "Tháng 03", "Tên hoạt động": "Tháng Thanh niên & Hội trại truyền thống 26/3", "Mục đích": "Kỷ niệm 96 năm Ngày thành lập Đoàn TNCS HCM", "Đơn vị thực hiện": "Toàn thể CB, ĐVTN toàn trường", "Trạng thái": "Trọng điểm ⭐"}
        ]
        df_pt = pd.DataFrame(phong_trao_list)
        st.dataframe(df_pt, use_container_width=True, hide_index=True)

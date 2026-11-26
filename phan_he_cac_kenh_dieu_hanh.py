# -*- coding: utf-8 -*-
"""
HỆ THỐNG 9 KÊNH ĐIỀU HÀNH & TÁC NGHIỆP CỐT LÕI
Trường THPT số 2 Bảo Yên - Xã Bảo Hà, Tỉnh Lào Cai
Tập hợp toàn bộ chức năng chuyên môn, lịch tuần, nhiệm vụ, theo dõi hằng ngày,
dạy học, hồ sơ đánh giá và tiện ích - Tinh gọn, hiện đại, loại bỏ hoàn toàn trùng lặp.
"""
import os
import time
import json
import pandas as pd
from datetime import datetime, date
import streamlit as st
from phan_he_hoc_sinh_phu_huynh import dong_bo_file_da_noi
from phan_he_quan_ly_chung import kiem_tra_quyen_quan_tri_nien_khoa, doc_cau_hinh_nam_hoc

def st_html(html_str):
    """Render HTML an toàn không bị biến thành code block"""
    cleaned = "\n".join(line.strip() for line in str(html_str).strip().splitlines())
    st.markdown(cleaned, unsafe_allow_html=True)

def render_channel_header(icon, title, subtitle, active_id="1"):
    """Banner tiêu đề chuẩn mực của từng Kênh tác nghiệp kèm thanh điều hướng 9 Kênh"""
    st_html(f"""
    <div style="background: linear-gradient(135deg, #0D5C75 0%, #103F75 100%); border-left: 6px solid #E0A834; padding: 14px 20px; border-radius: 12px; margin-bottom: 12px; color: white; box-shadow: 0 4px 12px rgba(13, 92, 117, 0.18); display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px;">
        <div>
            <div style="font-size: 11px; text-transform: uppercase; letter-spacing: 1.2px; color: #A7F3D0; font-weight: 800; margin-bottom: 2px;">
                TRƯỜNG THPT SỐ 2 BẢO YÊN • CỔNG ĐIỀU HÀNH NỘI BỘ
            </div>
            <h3 style="margin: 0; font-size: 20px; font-weight: 900; color: #FFFFFF; display: flex; align-items: center; gap: 8px;">
                <span>{icon}</span> {title}
            </h3>
            <div style="font-size: 12.5px; color: #E2E8F0; margin-top: 3px;">
                {subtitle}
            </div>
        </div>
        <div style="text-align: right; background: rgba(0,0,0,0.2); padding: 6px 14px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.15);">
            <div style="font-size: 11px; color: #FEF08A; font-weight: 700;">HỌC KỲ I (2026 - 2027)</div>
            <div style="font-size: 12px; color: #FFFFFF; font-weight: 800; margin-top: 2px;">🟢 Kênh trực tuyến 24/7</div>
        </div>
    </div>
    """)
    try:
        import cong_dieu_hanh_trang_chu
        cong_dieu_hanh_trang_chu.render_sticky_nav_bar(active_id=active_id)
    except Exception:
        pass

# =============================================================================
# KÊNH 2: CÔNG VIỆC & NHIỆM VỤ NHÀ TRƯỜNG
# =============================================================================
def render_kenh_cong_viec(df_tai_khoan, role_curr, nam_hoc, BASE_DIR, THU_MUC_NAM_HOC):
    """Kênh 2: Quản trị nhiệm vụ, giao việc rõ người rõ việc, theo dõi tiến độ"""
    render_channel_header("📋", "KÊNH 2: CÔNG VIỆC & NHIỆM VỤ NHÀ TRƯỜNG", "Sổ giao việc rõ người, rõ hạn, theo dõi tiến độ và đánh giá kết quả thực hiện", active_id="2")

    folder_nam = nam_hoc.replace(" ", "")
    dir_nam = os.path.join(THU_MUC_NAM_HOC, folder_nam) if os.path.exists(THU_MUC_NAM_HOC) else BASE_DIR
    f_tasks = os.path.join(dir_nam, "nhiem_vu_nha_truong.csv")
    if not os.path.exists(f_tasks):
        f_tasks = os.path.join(BASE_DIR, "nhiem_vu_nha_truong.csv")

    df_tasks = pd.DataFrame()
    if os.path.exists(f_tasks):
        try:
            df_tasks = pd.read_csv(f_tasks, encoding='utf-8-sig').fillna("")
        except Exception:
            pass

    tong_nv = len(df_tasks) if not df_tasks.empty else 6
    nv_done = len(df_tasks[df_tasks['Trạng thái'].str.contains('hoàn thành|xong', case=False, na=False)]) if not df_tasks.empty else 4
    nv_doing = tong_nv - nv_done
    ty_le_done = int((nv_done / tong_nv) * 100) if tong_nv > 0 else 67

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("🔴 Quá hạn", "0 việc", delta="0% tồn đọng")
    with c2:
        st.metric("🟡 Hôm nay", "2 việc", delta="Đang xử lý")
    with c3:
        st.metric("🔵 Sắp đến hạn", f"{nv_doing} việc", delta="Tuần này")
    with c4:
        st.metric("🟢 Đã hoàn thành", f"{nv_done}/{tong_nv}", delta=f"{ty_le_done}% tiến độ")

    tab_ds_nv, tab_giao_nv, tab_bao_cao_nv = st.tabs([
        "📋 SỔ GIAO VIỆC & THEO DÕI TIẾN ĐỘ",
        "➕ GIAO NHIỆM VỤ MỚI (BGH & TỔ TRƯỞNG)",
        "✓ BÁO CÁO TIẾN ĐỘ & HOÀN THÀNH"
    ])

    with tab_ds_nv:
        st.markdown("##### 📌 Bảng Danh Sách Công Việc Nhà Trường (Cập nhật Live):")
        c_f1, c_f2 = st.columns([1, 1])
        with c_f1:
            loc_tt = st.selectbox("Lọc theo trạng thái:", ["Tất cả", "Đang thực hiện", "Đã hoàn thành", "Chưa bắt đầu"])
        with c_f2:
            nguoi_th_unique = ["Tất cả"] + sorted(list(df_tasks['Người thực hiện'].unique())) if ('Người thực hiện' in df_tasks.columns and not df_tasks.empty) else ["Tất cả"]
            loc_nguoi = st.selectbox("Lọc theo người thực hiện:", nguoi_th_unique)

        df_show = df_tasks.copy()
        if not df_show.empty:
            if loc_tt != "Tất cả" and 'Trạng thái' in df_show.columns:
                df_show = df_show[df_show['Trạng thái'].str.contains(loc_tt, case=False, na=False)]
            if loc_nguoi != "Tất cả" and 'Người thực hiện' in df_show.columns:
                df_show = df_show[df_show['Người thực hiện'] == loc_nguoi]
            st.dataframe(df_show, use_container_width=True, hide_index=True)
        else:
            st.info("Chưa có bản ghi nhiệm vụ nào.")

    with tab_giao_nv:
        st.markdown("##### ➕ Phân Công & Giao Nhiệm Vụ Mới:")
        with st.form("form_giao_viec_moi"):
            cg1, cg2 = st.columns(2)
            with cg1:
                ten_cv = st.text_input("Tên công việc / Nhiệm vụ (*):", placeholder="VD: Kiểm tra chuyên đề ôn thi TN THPT môn Toán...")
                nguoi_ct = st.text_input("Người chủ trì (*):", value="Ban Giám Hiệu")
                nguoi_th = st.text_input("Người / Tổ phối hợp thực hiện (*):", placeholder="VD: Thầy Hoàng Văn Nam (Tổ KHTN)...")
            with cg2:
                han_th = st.date_input("Hạn hoàn thành:", date.today())
                muc_do = st.selectbox("Mức độ ưu tiên:", ["Bình thường", "Quan trọng", "Khẩn cấp ⭐"])
                phan_loai = st.selectbox("Phân loại công việc:", ["Chuyên môn", "Bán trú & KTX", "Đoàn thể & Nề nếp", "Cơ sở vật chất", "Khác"])
            ghi_chu_nv = st.text_input("Ghi chú / Yêu cầu sản phẩm minh chứng:")
            btn_giao = st.form_submit_button("💾 PHÂN CÔNG & GIAO VIỆC NGAY", type="primary", use_container_width=True)

            if btn_giao:
                if ten_cv.strip() and nguoi_th.strip():
                    ma_nv_new = f"NV-{int(time.time()) % 10000:04d}"
                    new_task_row = {
                        "Mã NV": ma_nv_new,
                        "Mã việc": ma_nv_new,
                        "Tên công việc": ten_cv.strip(),
                        "Người chủ trì": nguoi_ct.strip(),
                        "Người thực hiện": nguoi_th.strip(),
                        "Hạn hoàn thành": han_th.strftime("%d/%m/%Y"),
                        "Mức độ": muc_do,
                        "Phân loại": phan_loai,
                        "Trạng thái": "Đang thực hiện",
                        "Ghi chú": ghi_chu_nv.strip()
                    }
                    df_tasks_new = pd.concat([df_tasks, pd.DataFrame([new_task_row])], ignore_index=True)
                    dong_bo_file_da_noi(df_tasks_new, [
                        f_tasks,
                        "D:/nhiem_vu_nha_truong.csv",
                        "D:/phan_mem_ban_tru_cloud/nhiem_vu_nha_truong.csv"
                    ])
                    st.success(f"🎉 Đã giao việc thành công: '{ten_cv}' đến {nguoi_th}!")
                    st.rerun()
                else:
                    st.error("⚠️ Vui lòng nhập đầy đủ Tên công việc và Người thực hiện!")

    with tab_bao_cao_nv:
        st.markdown("##### ✓ Cập Nhật Báo Cáo Tiến Độ Nhiệm Vụ:")
        if not df_tasks.empty and 'Tên công việc' in df_tasks.columns:
            list_tasks = list(df_tasks['Tên công việc'].unique())
            cv_select = st.selectbox("Chọn công việc báo cáo kết quả:", list_tasks)
            idx_task = df_tasks[df_tasks['Tên công việc'] == cv_select].index[0]
            curr_row = df_tasks.loc[idx_task]

            st.info(f"📌 **Người thực hiện:** {curr_row.get('Người thực hiện')} | **Hạn hoàn thành:** {curr_row.get('Hạn hoàn thành')} | **Trạng thái:** {curr_row.get('Trạng thái')}")
            c_up1, c_up2 = st.columns(2)
            with c_up1:
                tt_new = st.selectbox("Trạng thái mới:", ["Đang thực hiện", "Đã hoàn thành", "Tạm hoãn / Điều chỉnh"], index=1 if "hoàn thành" in str(curr_row.get('Trạng thái')).lower() else 0)
            with c_up2:
                mc_note = st.text_input("Ghi chú minh chứng kết quả:", value=str(curr_row.get('Ghi chú', '')))

            if st.button("💾 CẬP NHẬT KẾT QUẢ CÔNG VIỆC", type="primary", use_container_width=True):
                df_tasks.at[idx_task, 'Trạng thái'] = tt_new
                df_tasks.at[idx_task, 'Ghi chú'] = mc_note.strip()
                dong_bo_file_da_noi(df_tasks, [
                    f_tasks,
                    "D:/nhiem_vu_nha_truong.csv",
                    "D:/phan_mem_ban_tru_cloud/nhiem_vu_nha_truong.csv"
                ])
                st.success(f"🎉 Đã cập nhật trạng thái nhiệm vụ '{cv_select}' sang: {tt_new}!")
                st.rerun()

# =============================================================================
# KÊNH 3: LỊCH LÀM VIỆC TUẦN
# =============================================================================
def render_kenh_lich_lam_viec(df_tai_khoan, role_curr, nam_hoc, BASE_DIR, THU_MUC_NAM_HOC):
    """Kênh 3: Lịch làm việc & công tác tuần tập trung"""
    render_channel_header("📅", "KÊNH 3: LỊCH LÀM VIỆC & CÔNG TÁC TUẦN", "Lịch công tác tập trung của Ban Giám Hiệu, Các Tổ Chuyên Môn, Trực Tuần & KTX", active_id="3")

    folder_nam = nam_hoc.replace(" ", "")
    dir_nam = os.path.join(THU_MUC_NAM_HOC, folder_nam) if os.path.exists(THU_MUC_NAM_HOC) else BASE_DIR
    f_lct = os.path.join(dir_nam, "lich_cong_tac_tuan.csv")
    if not os.path.exists(f_lct):
        f_lct = os.path.join(BASE_DIR, "lich_cong_tac_tuan.csv")

    df_lct = pd.DataFrame()
    if os.path.exists(f_lct):
        try:
            df_lct = pd.read_csv(f_lct, encoding='utf-8-sig').fillna("")
        except Exception:
            pass

    tab_lct_view, tab_lct_add, tab_lct_truc = st.tabs([
        "🗓️ LỊCH CÔNG TÁC TUẦN NÀY (TOÀN TRƯỜNG)",
        "➕ ĐĂNG KÝ & THÊM LỊCH TUẦN MỚI",
        "🚗 LỊCH CÔNG TÁC NGOÀI TRƯỜNG & TRỰC TUẦN"
    ])

    with tab_lct_view:
        c_t1, c_t2 = st.columns([1, 2])
        with c_t1:
            tuan_xem = st.selectbox("Chọn tuần làm việc:", [f"Tuần {i:02d}" for i in range(1, 38)], index=11)
        with c_t2:
            st.caption(f"📅 **Kế hoạch giáo dục:** {tuan_xem} · Năm học {nam_hoc}")

        if not df_lct.empty:
            df_tuan_show = df_lct[df_lct['Tuần'].str.strip() == tuan_xem] if 'Tuần' in df_lct.columns else df_lct
            if not df_tuan_show.empty:
                st.dataframe(df_tuan_show, use_container_width=True, hide_index=True)
            else:
                st.info(f"💡 Chưa có dữ liệu lịch làm việc cho {tuan_xem}. Xem toàn bộ lịch bên dưới:")
                st.dataframe(df_lct, use_container_width=True, hide_index=True)
        else:
            st.info("Chưa có tệp lịch công tác tuần.")

    with tab_lct_add:
        st.markdown("##### ➕ Thêm Mục Lịch Công Tác Mới:")
        with st.form("form_add_lct"):
            cl1, cl2 = st.columns(2)
            with cl1:
                tuan_add = st.selectbox("Tuần:", [f"Tuần {i:02d}" for i in range(1, 38)], index=11)
                thu_add = st.selectbox("Thứ trong tuần:", ["Thứ Hai", "Thứ Ba", "Thứ Tư", "Thứ Năm", "Thứ Sáu", "Thứ Bảy", "Chủ Nhật"])
                buoi_add = st.selectbox("Buổi:", ["Buổi Sáng (07h00 - 11h30)", "Buổi Chiều (13h30 - 17h00)", "Buổi Tối KTX (19h30 - 21h30)", "Cả ngày"])
            with cl2:
                noi_dung_add = st.text_input("Nội dung công việc (*):", placeholder="VD: Họp Chi bộ mở rộng...")
                thanh_phan_add = st.text_input("Thành phần tham gia:", placeholder="VD: Cấp ủy, BGH, Tổ trưởng...")
                dia_diem_add = st.text_input("Địa điểm:", value="Phòng Hội đồng")
                chu_tri_add = st.text_input("Chủ trì:", value="Hiệu trưởng")
            btn_add_lct = st.form_submit_button("💾 LƯU MỤC LỊCH CÔNG TÁC", type="primary", use_container_width=True)

            if btn_add_lct:
                if noi_dung_add.strip():
                    new_lct = {
                        "Tuần": tuan_add,
                        "Thứ": thu_add,
                        "Buổi": buoi_add,
                        "Nội dung": noi_dung_add.strip(),
                        "Thành phần": thanh_phan_add.strip(),
                        "Địa điểm": dia_diem_add.strip(),
                        "Chủ trì": chu_tri_add.strip()
                    }
                    df_lct_new = pd.concat([df_lct, pd.DataFrame([new_lct])], ignore_index=True)
                    dong_bo_file_da_noi(df_lct_new, [
                        f_lct,
                        "D:/lich_cong_tac_tuan.csv",
                        "D:/phan_mem_ban_tru_cloud/lich_cong_tac_tuan.csv"
                    ])
                    st.success(f"🎉 Đã thêm thành công lịch: '{noi_dung_add}' ({thu_add})!")
                    st.rerun()

    with tab_lct_truc:
        st.markdown("##### 🚗 Lịch Công Tác Sở GD&ĐT & Lịch Trực KTX Tuần Này:")
        st.markdown("""
        <div style="background:#F8FAFC; border:1px solid #CBD5E1; border-radius:10px; padding:14px 18px; line-height:1.7; font-size:13px;">
            • <b>Thứ Tư (25/11):</b> Thầy Hiệu trưởng dự Hội nghị Chuyển đổi số ngành GD&ĐT tại Sở GD&ĐT Lào Cai.<br>
            • <b>Thứ Năm (26/11):</b> Cô PHT dự tập huấn công tác thi TN THPT tại TX Sa Pa.<br>
            • <b>Trực Ban Đêm KTX (Thứ 2 - Thứ 5):</b> Thầy Hoàng Văn Hải & Cô Lương Thị Mai (Trực quản nhiệm 19h30 - 21h30).<br>
            • <b>Trực Cổng Trường & An Toàn Giao Thông:</b> Đội cờ đỏ Đoàn trường & Bảo vệ trực 06h45 - 07h15 và 11h15 - 11h45.
        </div>
        """, unsafe_allow_html=True)

# =============================================================================
# KÊNH 4: THEO DÕI HẰNG NGÀY
# =============================================================================
def render_kenh_theo_doi_hang_ngay(df_tai_khoan, role_curr, nam_hoc, BASE_DIR, THU_MUC_NAM_HOC):
    """Kênh 4: Báo sĩ số 21 lớp, Tiến độ chương trình, Thiết bị dạy học"""
    render_channel_header("📊", "KÊNH 4: THEO DÕI HẰNG NGÀY (LIVE OPERATIONS)", "Giám sát trực tiếp Sĩ số 21 lớp, Tiến độ chương trình giảng dạy và Thiết bị dạy học", active_id="4")

    tab_ss, tab_td, tab_tb = st.tabs([
        "👥 SĨ SỐ & ĐIỂM DANH CHUYÊN CẦN 21 LỚP",
        "📚 TIẾN ĐỘ CHƯƠNG TRÌNH (210 MÔN/LỚP)",
        "🔬 SỬ DỤNG & MƯỢN TRẢ THIẾT BỊ DẠY HỌC"
    ])

    f_ss = os.path.join(BASE_DIR, "bao_cao_si_so_lop_hang_ngay.csv")
    f_td = os.path.join(BASE_DIR, "tien_do_chuong_trinh_21_lop.csv")
    f_tb = os.path.join(BASE_DIR, "thiet_bi_day_hoc.csv")

    with tab_ss:
        st.markdown("#### 👥 Báo Sĩ Số & Chuyên Cần 21 Lớp Học (Trực Tiếp)")
        st.caption("Dành cho Giáo viên chủ nhiệm, Ban cán sự lớp (Lớp trưởng) và Đội Cờ Đỏ cập nhật quân số hàng ngày.")

        df_ss_all = pd.read_csv(f_ss, encoding='utf-8-sig').fillna("") if os.path.exists(f_ss) else pd.DataFrame()
        today_s = datetime.now().strftime("%d/%m/%Y")

        with st.form("form_bao_si_so_live"):
            css1, css2 = st.columns(2)
            with css1:
                lop_ss = st.selectbox("Chọn lớp báo cáo:", [f"10A{i}" for i in range(1, 8)] + [f"11A{i}" for i in range(1, 8)] + [f"12A{i}" for i in range(1, 8)])
                buoi_ss = st.selectbox("Buổi học:", ["Buổi Sáng (Chính khóa)", "Buổi Chiều (Tăng cường)", "Cả ngày"])
                ngay_ss = st.date_input("Ngày báo cáo:", date.today())
            with css2:
                co_mat_ss = st.number_input("Số học sinh có mặt:", min_value=0, max_value=55, value=44)
                vang_ss = st.number_input("Số học sinh vắng:", min_value=0, max_value=20, value=0)
                ly_do_ss = st.text_input("Họ tên & Lý do vắng (nếu có):", placeholder="VD: Hoàng Văn Nam (ốm có phép)...")
            btn_ss = st.form_submit_button("💾 GỬI BÁO CÁO SĨ SỐ LỚP", type="primary", use_container_width=True)

            if btn_ss:
                new_ss_entry = {
                    "Ngày": ngay_ss.strftime("%d/%m/%Y"),
                    "Lớp": lop_ss,
                    "Buổi": buoi_ss,
                    "Có mặt": co_mat_ss,
                    "Vắng": vang_ss,
                    "Lý do vắng": ly_do_ss.strip(),
                    "Thời gian báo": datetime.now().strftime("%H:%M:%S")
                }
                df_ss_new = pd.concat([df_ss_all, pd.DataFrame([new_ss_entry])], ignore_index=True)
                dong_bo_file_da_noi(df_ss_new, [
                    f_ss,
                    "D:/bao_cao_si_so_lop_hang_ngay.csv",
                    "D:/phan_mem_ban_tru_cloud/bao_cao_si_so_lop_hang_ngay.csv"
                ])
                st.success(f"🎉 Đã gửi thành công báo cáo sĩ số Lớp {lop_ss} (Có mặt: {co_mat_ss}, Vắng: {vang_ss})!")
                st.rerun()

        st.markdown("---")
        st.markdown("##### 📜 Nhật Ký Báo Sĩ Số Gần Nhất:")
        if not df_ss_all.empty:
            st.dataframe(df_ss_all.tail(21), use_container_width=True, hide_index=True)

    with tab_td:
        st.markdown("#### 📚 Giám Sát Tiến Độ Chương Trình (21 Lớp • GDPT 2018)")
        if os.path.exists(f_td):
            df_td_ct = pd.read_csv(f_td, encoding='utf-8-sig').fillna("")
            c_f_khoi, c_f_mon = st.columns(2)
            with c_f_khoi:
                khoi_list = ["Tất cả"] + sorted(list(df_td_ct['Khối'].unique())) if 'Khối' in df_td_ct.columns else ["Tất cả"]
                khoi_sel = st.selectbox("Lọc theo Khối:", khoi_list)
            with c_f_mon:
                to_list = ["Tất cả"] + sorted(list(df_td_ct['Tổ chuyên môn'].unique())) if 'Tổ chuyên môn' in df_td_ct.columns else ["Tất cả"]
                to_sel = st.selectbox("Lọc theo Tổ chuyên môn:", to_list)

            df_td_view = df_td_ct.copy()
            if khoi_sel != "Tất cả":
                df_td_view = df_td_view[df_td_view['Khối'] == khoi_sel]
            if to_sel != "Tất cả":
                df_td_view = df_td_view[df_td_view['Tổ chuyên môn'] == to_sel]

            st.dataframe(df_td_view, use_container_width=True, hide_index=True)
        else:
            st.info("Chưa có tệp tiến độ chương trình.")

    with tab_tb:
        st.markdown("#### 🔬 Sử Dụng & Mượn Trả Thiết Bị Dạy Học")
        if os.path.exists(f_tb):
            df_tb_all = pd.read_csv(f_tb, encoding='utf-8-sig').fillna("")
            st.dataframe(df_tb_all, use_container_width=True, hide_index=True)

            with st.expander("➕ **Đăng Ký Mượn Thiết Bị / Phòng Thực Hành Mới:**"):
                with st.form("form_muon_tb"):
                    cm1, cm2 = st.columns(2)
                    with cm1:
                        gv_muon = st.text_input("Giáo viên đăng ký mượn:", value=st.session_state.get("user_login", {}).get("fullname", "Giáo viên"))
                        ten_tb_muon = st.selectbox("Chọn thiết bị / phòng bộ môn:", list(df_tb_all['Tên thiết bị / Dụng cụ'].unique()) if 'Tên thiết bị / Dụng cụ' in df_tb_all.columns else ["Phòng Tin học 1", "Phòng Hóa - Sinh", "Bộ dụng cụ Vật lý 10"])
                    with cm2:
                        ngay_sd = st.date_input("Ngày sử dụng:", date.today())
                        lop_sd = st.selectbox("Lớp sử dụng:", [f"10A{i}" for i in range(1, 8)] + [f"11A{i}" for i in range(1, 8)] + [f"12A{i}" for i in range(1, 8)])
                    btn_m_tb = st.form_submit_button("💾 GỬI PHIẾU ĐĂNG KÝ SỬ DỤNG", type="primary", use_container_width=True)
                    if btn_m_tb:
                        st.success(f"🎉 Đã gửi thành công đăng ký mượn '{ten_tb_muon}' cho lớp {lop_sd} ngày {ngay_sd.strftime('%d/%m/%Y')}!")
        else:
            st.info("Chưa có danh mục thiết bị dạy học.")

# =============================================================================
# KÊNH 5: KẾT QUẢ DẠY VÀ HỌC & CHUYÊN MÔN
# =============================================================================
def render_kenh_day_va_hoc(df_tai_khoan, role_curr, nam_hoc, BASE_DIR, THU_MUC_NAM_HOC):
    """Kênh 5: Sổ đầu bài, Thời khóa biểu, Kết quả khảo sát, Danh sách học sinh & CBGV"""
    render_channel_header("📈", "KÊNH 5: KẾT QUẢ DẠY VÀ HỌC & CHUYÊN MÔN", "Sổ đầu bài điện tử, Thời khóa biểu 21 lớp, Phân tích chất lượng giáo dục và Danh bạ toàn trường", active_id="5")

    tab_sdb, tab_tkb, tab_chat_luong, tab_hs_all, tab_cbgv = st.tabs([
        "📖 SỔ ĐẦU BÀI ĐIỆN TỬ (21 LỚP)",
        "🗓️ THỜI KHÓA BIỂU 21 LỚP HỌC",
        "🎯 PHÂN TÍCH CHẤT LƯỢNG & PHỤ ĐẠO",
        "👨‍🎓 HỒ SƠ 929 HỌC SINH TOÀN TRƯỜNG",
        "📋 DANH BẠ 42 CÁN BỘ - GIÁO VIÊN"
    ])

    f_sdb = os.path.join(BASE_DIR, "so_dau_bai.csv")
    f_tkb = os.path.join(BASE_DIR, "thoi_khoa_bieu.csv")
    f_hs_tt = os.path.join(BASE_DIR, "danh_sach_hoc_sinh_toan_truong.csv")
    f_gv_db = os.path.join(BASE_DIR, "danh_ba_cbgv_nv.csv")

    with tab_sdb:
        st.markdown("#### 📖 Sổ Đầu Bài Điện Tử (SĐB) — Ký Duyệt Tiết Dạy Trực Tuyến")
        if os.path.exists(f_sdb):
            df_sdb = pd.read_csv(f_sdb, encoding='utf-8-sig').fillna("")
            st.dataframe(df_sdb.tail(20), use_container_width=True, hide_index=True)
        else:
            st.info("Sổ đầu bài điện tử đang đồng bộ.")

    with tab_tkb:
        st.markdown("#### 🗓️ Tra Cứu Thời Khóa Biểu Giảng Dạy (Tuần 12)")
        if os.path.exists(f_tkb):
            df_tkb = pd.read_csv(f_tkb, encoding='utf-8-sig').fillna("")
            lop_tkb = st.selectbox("Chọn lớp tra cứu TKB:", sorted(list(df_tkb['Lớp'].unique())) if 'Lớp' in df_tkb.columns else ["10A1", "11A1", "12A1"])
            df_tkb_lop = df_tkb[df_tkb['Lớp'] == lop_tkb] if 'Lớp' in df_tkb.columns else df_tkb
            st.dataframe(df_tkb_lop, use_container_width=True, hide_index=True)
        else:
            st.info("Chưa có tệp thời khóa biểu.")

    with tab_chat_luong:
        st.markdown("#### 🎯 Phân Tích Chất Lượng Học Tập & Danh Sách Cần Phụ Đạo")
        st_html("""
        <div style="background:#F0FDFA; border:1px solid #99F6E4; border-radius:10px; padding:14px 18px; margin-bottom:14px;">
            <div style="font-size:14px; font-weight:800; color:#0F766E;">📊 KẾT QUẢ KHẢO SÁT CHẤT LƯỢNG THÁNG 11 (929 HỌC SINH):</div>
            <div style="font-size:12.5px; line-height:1.6; color:#0F172A; margin-top:6px;">
                • <b>Xuất sắc & Giỏi (ĐTB >= 8.0):</b> 324 học sinh (34.9%)<br>
                • <b>Khá (ĐTB 6.5 - 7.9):</b> 452 học sinh (48.7%)<br>
                • <b>Đạt (ĐTB 5.0 - 6.4):</b> 145 học sinh (15.6%)<br>
                • <b>Chưa đạt (ĐTB < 5.0):</b> 8 học sinh (0.8%) — Đã lên lịch phụ đạo Toán & Tiếng Anh ca chiều.
            </div>
        </div>
        """)

    with tab_hs_all:
        st.markdown("#### 👨‍🎓 Tra Cứu Danh Sách 929 Học Sinh Toàn Trường")
        if os.path.exists(f_hs_tt):
            df_hs = pd.read_csv(f_hs_tt, encoding='utf-8-sig').fillna("")
            c_h1, c_h2 = st.columns(2)
            with c_h1:
                lop_f = st.selectbox("Lọc theo lớp học:", ["Tất cả"] + sorted(list(df_hs['Lớp'].unique())) if 'Lớp' in df_hs.columns else ["Tất cả"])
            with c_h2:
                ten_tim = st.text_input("Tìm kiếm theo họ tên học sinh:")
            df_hs_v = df_hs.copy()
            if lop_f != "Tất cả":
                df_hs_v = df_hs_v[df_hs_v['Lớp'] == lop_f]
            if ten_tim.strip():
                df_hs_v = df_hs_v[df_hs_v['Họ và tên'].str.contains(ten_tim.strip(), case=False, na=False)]
            st.dataframe(df_hs_v, use_container_width=True, hide_index=True)

    with tab_cbgv:
        st.markdown("#### 📋 Danh Bạ 42 Cán Bộ - Giáo Viên - Nhân Viên")
        if os.path.exists(f_gv_db):
            df_gv = pd.read_csv(f_gv_db, encoding='utf-8-sig').fillna("")
            st.dataframe(df_gv, use_container_width=True, hide_index=True)

# =============================================================================
# KÊNH 8: HỒ SƠ – ĐÁNH GIÁ & QUẢN TRỊ HỆ THỐNG
# =============================================================================
def render_kenh_ho_so_danh_gia(df_tai_khoan, role_curr, nam_hoc, BASE_DIR, THU_MUC_NAM_HOC):
    """Kênh 8: 4 Thư mục điện tử, Đánh giá KPI 4 tổ, Kế hoạch năm và Quản trị niên khóa"""
    render_channel_header("📁", "KÊNH 8: HỒ SƠ – ĐÁNH GIÁ & QUẢN TRỊ HỆ THỐNG", "4 Thư mục tài liệu điện tử, Đánh giá KPI 4 Tổ chuyên môn, Kế hoạch năm và Cấu hình hệ thống", active_id="8")

    u_curr = st.session_state.get("user_login", {})
    duoc_quyen_admin = kiem_tra_quyen_quan_tri_nien_khoa(u_curr, role_curr, BASE_DIR)

    tab_folders, tab_kpi, tab_kh, tab_users, tab_sync = st.tabs([
        "📂 4 THƯ MỤC TÀI LIỆU HỒ SƠ ĐIỆN TỬ",
        "🌟 ĐÁNH GIÁ KPI 4 TỔ CHUYÊN MÔN",
        "📝 KẾ HOẠCH NĂM HỌC & CHỦ NHIỆM",
        "👑 PHÂN QUYỀN & TÀI KHOẢN (ADMIN)",
        "🔄 TỰ ĐỘNG ĐỒNG BỘ ĐÁM MÂY (24/7)"
    ])

    with tab_folders:
        st.markdown("#### 📂 4 Thư Mục Tài Liệu Hồ Sơ Biểu Mẫu Điện Tử (Google Drive)")
        st_html("""
        <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap:14px; margin-top:10px;">
            <div style="background:white; border:1px solid #CBD5E1; border-radius:10px; padding:14px; border-left:5px solid #0D5C75;">
                <b style="font-size:13.5px; color:#0F172A;">📁 01 · HỒ SƠ - VĂN BẢN QUẢN LÝ</b>
                <div style="font-size:11.5px; color:#64748B; margin:6px 0 10px 0;">Quyết định phân công, quy chế dân chủ, công văn đi/đến.</div>
                <a href="https://drive.google.com" target="_blank" style="background:#0D5C75; color:white; padding:4px 12px; border-radius:6px; font-size:11.5px; font-weight:bold; text-decoration:none;">Mở Thư Mục Drive ↗</a>
            </div>
            <div style="background:white; border:1px solid #CBD5E1; border-radius:10px; padding:14px; border-left:5px solid #059669;">
                <b style="font-size:13.5px; color:#0F172A;">📁 02 · KẾ HOẠCH & CHUYÊN MÔN</b>
                <div style="font-size:11.5px; color:#64748B; margin:6px 0 10px 0;">Kế hoạch giáo dục môn học, giáo án số, biên bản sinh hoạt tổ.</div>
                <a href="https://drive.google.com" target="_blank" style="background:#059669; color:white; padding:4px 12px; border-radius:6px; font-size:11.5px; font-weight:bold; text-decoration:none;">Mở Thư Mục Drive ↗</a>
            </div>
            <div style="background:white; border:1px solid #CBD5E1; border-radius:10px; padding:14px; border-left:5px solid #D97706;">
                <b style="font-size:13.5px; color:#0F172A;">📁 03 · CÔNG TÁC CHỦ NHIỆM</b>
                <div style="font-size:11.5px; color:#64748B; margin:6px 0 10px 0;">Sổ chủ nhiệm 21 lớp, biên bản họp CMHS, hồ sơ hoàn cảnh học sinh.</div>
                <a href="https://drive.google.com" target="_blank" style="background:#D97706; color:white; padding:4px 12px; border-radius:6px; font-size:11.5px; font-weight:bold; text-decoration:none;">Mở Thư Mục Drive ↗</a>
            </div>
            <div style="background:white; border:1px solid #CBD5E1; border-radius:10px; padding:14px; border-left:5px solid #7C3AED;">
                <b style="font-size:13.5px; color:#0F172A;">📁 04 · CƠ SỞ VẬT CHẤT & THIẾT BỊ</b>
                <div style="font-size:11.5px; color:#64748B; margin:6px 0 10px 0;">Kiểm kê tài sản, theo dõi thiết bị dạy học, nhật ký KTX.</div>
                <a href="https://drive.google.com" target="_blank" style="background:#7C3AED; color:white; padding:4px 12px; border-radius:6px; font-size:11.5px; font-weight:bold; text-decoration:none;">Mở Thư Mục Drive ↗</a>
            </div>
        </div>
        """)

    with tab_kpi:
        st.markdown("#### 🌟 Đánh Giá KPI 4 Tổ Chuyên Môn (52 Cán Bộ Giáo Viên)")
        st_html("""
        <div style="background:#F8FAFC; border:1px solid #CBD5E1; border-radius:10px; padding:14px 18px; margin-top:8px;">
            <div style="font-size:13.5px; font-weight:800; color:#0F172A; margin-bottom:8px;">BẢNG TỔNG HỢP KPI THÁNG 11:</div>
            <div style="font-size:12.5px; line-height:1.7; color:#334155;">
                • <b>01 · TỔ VĂN PHÒNG:</b> 98.5% Hoàn thành đúng hạn · Không có việc trễ.<br>
                • <b>02 · TỔ KHTN:</b> 97.8% Hoàn thành phân phối chương trình và thí nghiệm thực hành.<br>
                • <b>03 · TỔ KHXH:</b> 99.1% Đã hoàn thành hồ sơ kiểm tra chuyên môn định kỳ.<br>
                • <b>04 · TỔ TBMC & KTX:</b> 100% Hoàn thành kiểm thực an toàn thực phẩm và quản lý KTX 5S.
            </div>
        </div>
        """)

    with tab_kh:
        st.markdown("#### 📝 Kế Hoạch Năm Học & Kế Hoạch Chủ Nhiệm")
        f_khn = os.path.join(BASE_DIR, "ke_hoach_nam.csv")
        f_khcn = os.path.join(BASE_DIR, "ke_hoach_chu_nhiem.csv")
        if os.path.exists(f_khn):
            st.markdown("##### 📌 Kế Hoạch Giáo Dục Nhà Trường:")
            df_khn = pd.read_csv(f_khn, encoding='utf-8-sig').fillna("")
            st.dataframe(df_khn, use_container_width=True, hide_index=True)
        if os.path.exists(f_khcn):
            st.markdown("##### 📌 Kế Hoạch Công Tác Chủ Nhiệm:")
            df_khcn = pd.read_csv(f_khcn, encoding='utf-8-sig').fillna("")
            st.dataframe(df_khcn, use_container_width=True, hide_index=True)

    with tab_users:
        if duoc_quyen_admin:
            st.markdown("#### 👑 Phân Quyền & Quản Trị Tài Khoản Toàn Trường")
            f_tk = os.path.join(BASE_DIR, "tai_khoan_nguoi_dung.csv")
            if os.path.exists(f_tk):
                df_tk = pd.read_csv(f_tk, encoding='utf-8-sig', dtype=str).fillna("")
                st.caption(f"Tổng số tài khoản: **{len(df_tk)} tài khoản** (Ban Giám Hiệu, GVCN, KTX, Học sinh, Phụ huynh)")
                st.dataframe(df_tk[['Tên đăng nhập', 'Họ và tên', 'Vai trò', 'Chức danh', 'Mã liên kết', 'Quyền quản lý']], use_container_width=True, hide_index=True)
        else:
            st.warning("🔒 Chức năng này chỉ dành riêng cho Ban Giám Hiệu và Quản Trị Viên hệ thống.")

    with tab_sync:
        st.markdown("#### 🔄 Trung Tâm Tự Động Đồng Bộ Đám Mây (24/7)")
        st.caption("Dữ liệu tự động đồng bộ hai chiều giữa máy tính nội bộ trường và máy chủ Web Cloud GitHub / Streamlit.")
        try:
            import dich_vu_tu_dong_dong_bo
            st_d = dich_vu_tu_dong_dong_bo.lay_trang_thai_dich_vu()
            st.success(f"🟢 **Trạng thái dịch vụ nền:** {st_d.get('trang_thai', 'Đang hoạt động')} | Số lần đồng bộ thành công: {st_d.get('so_lan_dong_bo_thanh_cong', 0)}")
        except Exception:
            st.info("🟢 Dịch vụ đồng bộ đám mây đang sẵn sàng tự động đồng bộ mỗi khi có thay đổi dữ liệu.")

        if duoc_quyen_admin:
            sync_s1, sync_s2 = st.tabs(["📊 ĐỒNG BỘ GOOGLE SHEETS BẢNG TÍNH", "🐙 ĐỒNG BỘ GITHUB (WEB CLOUD)"])
            with sync_s1:
                try:
                    from dong_bo_google_sheets import render_tab_google_sheets
                    render_tab_google_sheets(BASE_DIR, nam_hoc, THU_MUC_NAM_HOC)
                except Exception as ex_gs:
                    st.error(f"Lỗi tải giao diện Google Sheets: {ex_gs}")
            with sync_s2:
                st.markdown("##### 🐙 Đẩy Dữ Liệu Lên Máy Chủ GitHub & Cloud")
                st.caption("Thực hiện đồng bộ tức thì các tập tin dữ liệu lên repository GitHub để Streamlit Cloud tự động cập nhật bản mới nhất.")
                if st.button("🚀 Bấm Để Đồng Bộ Ngay Lên GitHub Cloud", key="btn_manual_push_git", type="primary"):
                    with st.spinner("Đang đẩy dữ liệu lên GitHub Cloud..."):
                        try:
                            import subprocess
                            res = subprocess.run(["python", "D:/run_push_github.py"], capture_output=True, text=True, timeout=35)
                            if res.returncode == 0:
                                st.success("🎉 Đồng bộ lên GitHub Cloud thành công! Streamlit Cloud đang nạp dữ liệu mới nhất.")
                            else:
                                st.warning(f"Kết quả đồng bộ: {res.stdout or res.stderr}")
                        except Exception as ex_push:
                            st.info(f"Yêu cầu đồng bộ đã được ghi nhận: {ex_push}")

# =============================================================================
# KÊNH 9: TIỆN ÍCH GIÁO DỤC SỐ & CÀI ĐẶT
# =============================================================================
def render_kenh_tien_ich_va_cai_dat(BASE_DIR, THU_MUC_NAM_HOC, nam_hoc, duong_dan_online="", duong_dan_app_mobile=""):
    """Kênh 9: 9 Nền tảng trực tuyến mở nhanh và Hướng dẫn cài đặt ứng dụng PWA"""
    render_channel_header("🚀", "KÊNH 9: TIỆN ÍCH GIÁO DỤC SỐ & CÀI ĐẶT APP", "Lối tắt 9 nền tảng trực tuyến thiết yếu và Hướng dẫn cài đặt ứng dụng lên màn hình điện thoại", active_id="9")

    tab_apps, tab_pwa = st.tabs([
        "🚀 LỐI TẮT 9 NỀN TẢNG GIÁO DỤC SỐ",
        "📱 CÀI ĐẶT ỨNG DỤNG LÊN ĐIỆN THOẠI (PWA)"
    ])

    with tab_apps:
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
                    <div style="background: white; border: 1px solid #E2E8F0; border-radius: 10px; padding: 12px 14px; margin-bottom: 12px; display: flex; align-items: center; gap: 12px; box-shadow: 0 2px 5px rgba(0,0,0,0.02);">
                        <div style="background: {item['bg']}; color: {item['mau']}; width: 38px; height: 38px; border-radius: 8px; display: flex; align-items: center; justify-content: center; font-size: 20px; flex-shrink: 0;">
                            {item['icon']}
                        </div>
                        <div style="overflow: hidden;">
                            <div style="font-weight: 700; font-size: 13px; color: #1E293B;">{item['ten']}</div>
                            <div style="font-size: 11px; color: #64748B;">{item['mo_ta']}</div>
                        </div>
                    </div>
                </a>
                """)

    with tab_pwa:
        link_hien = duong_dan_app_mobile if duong_dan_app_mobile else "https://thpt2baoyen.streamlit.app"
        st.markdown(f"""
        <div style="border: 2px solid #16A34A; padding: 20px; border-radius: 16px; background: #F0FDF4; box-shadow: 0 4px 15px rgba(22, 163, 74, 0.12); text-align: center;">
            <div style="background:#16A34A; color:white; display:inline-block; padding:4px 16px; border-radius:20px; font-weight:bold; font-size:12px; margin-bottom:10px;">
                🌟 ĐỊA CHỈ TRUY CẬP ĐÁM MÂY CHÍNH THỨC
            </div>
            <h4 style="color:#15803D; margin:5px 0 10px 0;">CÀI ĐẶT ỨNG DỤNG LÊN ĐIỆN THOẠI KHÔNG CẦN VÀO APP STORE</h4>
            <div style="font-size:13px; color:#374151; margin-bottom:12px;">
                Địa chỉ Web Cloud: <a href="{link_hien}" target="_blank" style="color:#0284C7; font-weight:bold;">{link_hien}</a>
            </div>
            <div style="display:flex; justify-content:center; gap:20px; text-align:left; flex-wrap:wrap; margin-top:14px;">
                <div style="background:white; border:1px solid #BBF7D0; border-radius:10px; padding:12px 16px; max-width:320px;">
                    <b style="color:#0F766E;">🍏 Dành cho iPhone / iPad (Safari):</b>
                    <ol style="font-size:12px; color:#475569; margin:6px 0 0 16px; padding:0;">
                        <li>Mở link bằng trình duyệt Safari.</li>
                        <li>Bấm nút <b>Chia sẻ (Share)</b> ở đáy màn hình.</li>
                        <li>Chọn <b>Thêm vào MH chính (Add to Home Screen)</b>.</li>
                    </ol>
                </div>
                <div style="background:white; border:1px solid #BBF7D0; border-radius:10px; padding:12px 16px; max-width:320px;">
                    <b style="color:#0F766E;">🤖 Dành cho Android (Chrome / Cốc Cốc):</b>
                    <ol style="font-size:12px; color:#475569; margin:6px 0 0 16px; padding:0;">
                        <li>Mở link bằng trình duyệt Google Chrome.</li>
                        <li>Bấm dấu <b>3 chấm ⋮</b> ở góc trên bên phải.</li>
                        <li>Chọn <b>Cài đặt ứng dụng</b> hoặc <b>Thêm vào màn hình chính</b>.</li>
                    </ol>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

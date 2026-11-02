# -*- coding: utf-8 -*-
"""
MODULE QUẢN LÝ NHẬN XÉT & ĐÁNH GIÁ BỮA ĂN BÁN TRÚ THỜI GIAN THỰC
Trường THPT số 2 Bảo Yên - Lào Cai
Phục vụ:
1. Học sinh bán trú & Phụ huynh bán trú gửi nhận xét, đánh giá bữa ăn (Trưa, Tối) từng ngày theo 3 mức: Tốt, Khá, Không tốt kèm ghi chú món ăn.
2. Tổng hợp báo cáo thời gian thực (Real-time Dashboard) hiển thị tại Kênh QUẢN LÝ BÁN TRÚ cho Ban Giám Hiệu, Thầy Quản nhiệm KTX và Nhà bếp theo dõi, điều chỉnh thực đơn.
"""

import os
import uuid
from datetime import datetime, date
import pandas as pd
import streamlit as st

FILE_DANH_GIA_CSV = "D:/danh_gia_bua_an_ban_tru.csv"
FILE_CLOUD_DANH_GIA = "D:/phan_mem_ban_tru_cloud/danh_gia_bua_an_ban_tru.csv"

COT_DANH_GIA = [
    "Mã đánh giá",
    "Thời gian",
    "Ngày ăn",
    "Bữa ăn",
    "Mức đánh giá",
    "Nhận xét món ăn",
    "Người đánh giá",
    "Vai trò",
    "Mã HS",
    "Lớp",
    "Phòng KTX",
    "Tên đăng nhập"
]

def lay_du_lieu_danh_gia(base_dir="D:/"):
    """Đọc dữ liệu nhận xét, đánh giá bữa ăn từ CSV"""
    f_path = os.path.join(base_dir, "danh_gia_bua_an_ban_tru.csv") if os.path.exists(os.path.join(base_dir, "danh_gia_bua_an_ban_tru.csv")) else FILE_DANH_GIA_CSV
    if os.path.exists(f_path):
        try:
            return pd.read_csv(f_path, encoding='utf-8-sig', dtype=str).fillna("")
        except Exception:
            pass
            
    # Tạo dữ liệu mẫu ban đầu nếu chưa có
    df_init = pd.DataFrame([
        {
            "Mã đánh giá": "DG-20261102-001",
            "Thời gian": "02/11/2026 12:15",
            "Ngày ăn": "02/11/2026",
            "Bữa ăn": "Bữa trưa",
            "Mức đánh giá": "Tốt",
            "Nhận xét món ăn": "Cơm dẻo ngon, thịt kho tàu mềm đậm đà, canh rau ngót nấu thịt băm ngọt thanh.",
            "Người đánh giá": "Em Bàn Hải Phong",
            "Vai trò": "Học sinh bán trú",
            "Mã HS": "HS0001",
            "Lớp": "10A1",
            "Phòng KTX": "Phòng 301",
            "Tên đăng nhập": "hocsinh"
        },
        {
            "Mã đánh giá": "DG-20261102-002",
            "Thời gian": "02/11/2026 12:20",
            "Ngày ăn": "02/11/2026",
            "Bữa ăn": "Bữa trưa",
            "Mức đánh giá": "Tốt",
            "Nhận xét món ăn": "Đậu hũ sốt cà chua và su su xào giòn ngọt, nhà bếp phục vụ cơm thêm rất nhiệt tình.",
            "Người đánh giá": "Phụ huynh em Nguyễn Thị Mai",
            "Vai trò": "Phụ huynh bán trú",
            "Mã HS": "HS0003",
            "Lớp": "10A3",
            "Phòng KTX": "Phòng 204",
            "Tên đăng nhập": "phuhuynh"
        },
        {
            "Mã đánh giá": "DG-20261102-003",
            "Thời gian": "02/11/2026 12:25",
            "Ngày ăn": "02/11/2026",
            "Bữa ăn": "Bữa trưa",
            "Mức đánh giá": "Khá",
            "Nhận xét món ăn": "Món ăn đầy đặn, đủ no; mong nhà bếp hôm nào có thêm hoa quả tráng miệng thì tuyệt vời.",
            "Người đánh giá": "Em Hoàng Văn Lâm",
            "Vai trò": "Học sinh bán trú",
            "Mã HS": "HS0015",
            "Lớp": "11A2",
            "Phòng KTX": "Phòng 303",
            "Tên đăng nhập": "hsn028"
        },
        {
            "Mã đánh giá": "DG-20261101-004",
            "Thời gian": "01/11/2026 18:30",
            "Ngày ăn": "01/11/2026",
            "Bữa ăn": "Bữa tối",
            "Mức đánh giá": "Tốt",
            "Nhận xét món ăn": "Gà rang gừng ấm bụng, cơm canh nóng hổi giữa thời tiết se lạnh của Bảo Hà.",
            "Người đánh giá": "Em Lương Thị Linh",
            "Vai trò": "Học sinh bán trú",
            "Mã HS": "HS0021",
            "Lớp": "12A1",
            "Phòng KTX": "Phòng 102",
            "Tên đăng nhập": "hsu019"
        },
        {
            "Mã đánh giá": "DG-20261101-005",
            "Thời gian": "01/11/2026 18:40",
            "Ngày ăn": "01/11/2026",
            "Bữa ăn": "Bữa tối",
            "Mức đánh giá": "Khá",
            "Nhận xét món ăn": "Thức ăn ngon nhưng hôm qua hơi nhiều món xào dầu mỡ, mong nhà bếp luân phiên thêm món luộc.",
            "Người đánh giá": "Phụ huynh em Đặng Tuấn Kiệt",
            "Vai trò": "Phụ huynh bán trú",
            "Mã HS": "HS0045",
            "Lớp": "10A5",
            "Phòng KTX": "Phòng 305",
            "Tên đăng nhập": "ph_hsu045"
        }
    ])
    try:
        df_init.to_csv(f_path, index=False, encoding='utf-8-sig')
    except Exception:
        pass
    return df_init

def luu_danh_gia_bua_an(dong_moi, base_dir="D:/"):
    """Lưu đánh giá mới và đồng bộ đa nơi (cục bộ, cloud, backup)"""
    targets = [
        FILE_DANH_GIA_CSV,
        FILE_CLOUD_DANH_GIA,
        os.path.join(base_dir, "danh_gia_bua_an_ban_tru.csv"),
        os.path.join("d:/OneDrive/Hô sơ cá nhan/Học AI", "danh_gia_bua_an_ban_tru.csv")
    ]
    df_cur = lay_du_lieu_danh_gia(base_dir)
    df_new = pd.concat([pd.DataFrame([dong_moi]), df_cur], ignore_index=True)
    
    for t in targets:
        try:
            os.makedirs(os.path.dirname(t), exist_ok=True)
            df_new.to_csv(t, index=False, encoding='utf-8-sig')
        except Exception:
            pass
    return True

# =============================================================================
# 1. GIAO DIỆN FORM ĐÁNH GIÁ CHO HỌC SINH & PHỤ HUYNH
# =============================================================================
def render_form_danh_gia(u_curr, row_hs, vai_tro_nguoi_gui="Học sinh bán trú", base_dir="D:/"):
    """
    Form đánh giá bữa ăn (Trưa / Tối) hàng ngày dành cho Học sinh hoặc Phụ huynh
    """
    ten_hs = str(row_hs.get("Họ và tên", u_curr.get("fullname", "Học sinh"))).strip()
    lop_hs = str(row_hs.get("Lớp", u_curr.get("ma_lien_ket", ""))).strip()
    phong_hs = str(row_hs.get("Phòng", "")).strip()
    ma_hs = str(row_hs.get("Mã HS", "")).strip()

    st.markdown("""
        <div style='background: linear-gradient(135deg, #059669, #047857); padding: 12px 18px; border-radius: 10px; color: white; margin-bottom: 12px;'>
            <div style='display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:8px;'>
                <div>
                    <h3 style='margin:0; font-size: 19px; color: white; font-weight:800;'>⭐ NHẬN XÉT & ĐÁNH GIÁ CHẤT LƯỢNG BỮA ĂN BÁN TRÚ</h3>
                    <p style='margin: 3px 0 0 0; opacity: 0.95; font-size: 13px;'>
                        Ý kiến của em và gia đình được gửi trực tiếp thời gian thực đến Thầy Quản nhiệm, Nhà bếp & Ban Giám Hiệu
                    </p>
                </div>
                <div style='background:rgba(255,255,255,0.25); padding:4px 12px; border-radius:14px; font-weight:bold; font-size:12px;'>
                    🔔 GÓP Ý TRỰC TIẾP
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    col_f1, col_f2 = st.columns([1.3, 1], gap="medium")

    with col_f1:
        st.markdown("#### 📝 Gửi Phiếu Nhận Xét Hôm Nay:")
        with st.form("form_nhan_xet_bua_an"):
            c_d1, c_d2 = st.columns(2)
            with c_d1:
                ngay_an_val = st.date_input("📅 Ngày ăn:", value=date.today(), key="dt_ngay_an_dg")
                ngay_an_str = ngay_an_val.strftime("%d/%m/%Y")
            with c_d2:
                bua_an_sel = st.selectbox("🍲 Bữa ăn nhận xét:", ["Bữa trưa", "Bữa tối"], key="sb_bua_an_dg")

            st.markdown("##### 🎯 Mức độ hài lòng về bữa ăn:")
            muc_danh_gia = st.radio(
                "Mức đánh giá:",
                [
                    "🟢 Tốt (Món ăn ngon, nóng sốt, đầy đặn, hợp vệ sinh)",
                    "🟡 Khá (Ăn được, cần bổ sung hoặc cải thiện thêm)",
                    "🔴 Không tốt (Chưa vừa miệng / Suất ăn ít / Cần phản ánh)"
                ],
                index=0,
                key="rb_muc_dg"
            )
            # Trích xuất mức chuẩn: Tốt, Khá, Không tốt
            muc_chuan = "Tốt" if "Tốt" in muc_danh_gia and "Không tốt" not in muc_danh_gia else ("Khá" if "Khá" in muc_danh_gia else "Không tốt")

            ghi_chu_mon = st.text_area(
                "✍️ Nhận xét chi tiết về món ăn (hương vị, số lượng, vệ sinh...):",
                placeholder="VD: Cơm hôm nay dẻo và thơm; canh thịt ngọt vừa vặn; mong nhà bếp giảm bớt dầu mỡ trong món xào...",
                key="txt_nx_mon_an",
                height=95
            )

            nguoi_gui_label = f"Em {ten_hs}" if vai_tro_nguoi_gui == "Học sinh bán trú" else f"Phụ huynh em {ten_hs} ({u_curr.get('fullname', '')})"
            st.caption(f"👤 Người gửi: **{nguoi_gui_label}** - Lớp: **{lop_hs}** - Phòng: **{phong_hs}**")

            btn_submit_dg = st.form_submit_button("🚀 GỬI ĐÁNH GIÁ ĐẾN NHÀ BẾP & BAN GIÁM HIỆU", type="primary", use_container_width=True)

            if btn_submit_dg:
                ma_dg = f"DG-{datetime.now().strftime('%Y%m%d%H%M%S')}"
                dong_dg = {
                    "Mã đánh giá": ma_dg,
                    "Thời gian": datetime.now().strftime("%d/%m/%Y %H:%M"),
                    "Ngày ăn": ngay_an_str,
                    "Bữa ăn": bua_an_sel,
                    "Mức đánh giá": muc_chuan,
                    "Nhận xét món ăn": ghi_chu_mon.strip() if ghi_chu_mon.strip() else f"Đánh giá bữa ăn mức {muc_chuan}.",
                    "Người đánh giá": nguoi_gui_label,
                    "Vai trò": vai_tro_nguoi_gui,
                    "Mã HS": ma_hs,
                    "Lớp": lop_hs,
                    "Phòng KTX": phong_hs,
                    "Tên đăng nhập": u_curr.get("username", "")
                }
                luu_danh_gia_bua_an(dong_dg, base_dir)
                st.success(f"🎉 Cảm ơn {('em' if vai_tro_nguoi_gui == 'Học sinh bán trú' else 'quý phụ huynh')}! Nhận xét đánh giá mức **{muc_chuan}** cho **{bua_an_sel}** ngày {ngay_an_str} đã được ghi nhận thời gian thực gửi đến Ban Quản lý Bán trú & Nhà bếp.")
                st.balloons()
                st.rerun()

    with col_f2:
        st.markdown("#### 📜 Lịch Sử Nhận Xét Của Gia Đình:")
        df_all_dg = lay_du_lieu_danh_gia(base_dir)
        df_mine = pd.DataFrame()
        if not df_all_dg.empty:
            if ma_hs:
                df_mine = df_all_dg[df_all_dg["Mã HS"] == ma_hs].copy()
            else:
                df_mine = df_all_dg[df_all_dg["Tên đăng nhập"] == u_curr.get("username", "")].copy()

        if not df_mine.empty:
            for idx, r in df_mine.head(5).iterrows():
                badge_bg = "#DEF7EC" if r["Mức đánh giá"] == "Tốt" else ("#FEF08A" if r["Mức đánh giá"] == "Khá" else "#FEE2E2")
                badge_color = "#03543F" if r["Mức đánh giá"] == "Tốt" else ("#854D0E" if r["Mức đánh giá"] == "Khá" else "#991B1B")
                icon_muc = "🟢" if r["Mức đánh giá"] == "Tốt" else ("🟡" if r["Mức đánh giá"] == "Khá" else "🔴")

                st.markdown(f"""
                <div style="background:#FFFFFF; border:1px solid #E5E7EB; border-left:4px solid {badge_color}; padding:10px 12px; border-radius:8px; margin-bottom:8px; box-shadow:0 1px 2px rgba(0,0,0,0.04);">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:4px;">
                        <span style="font-size:12px; font-weight:bold; color:#1F2937;">{r['Bữa ăn']} ({r['Ngày ăn']})</span>
                        <span style="background:{badge_bg}; color:{badge_color}; padding:2px 8px; border-radius:10px; font-weight:bold; font-size:11.5px;">{icon_muc} {r['Mức đánh giá']}</span>
                    </div>
                    <div style="font-size:12.5px; color:#374151; font-style:italic; line-height:1.4;">
                        "{r['Nhận xét món ăn']}"
                    </div>
                    <div style="font-size:11px; color:#9CA3AF; margin-top:4px;">
                        🕒 Gửi lúc {r['Thời gian']} • {r['Người đánh giá']}
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("💡 Bạn chưa gửi nhận xét đánh giá nào. Hãy đánh giá sau mỗi bữa trưa và tối để nhà trường ngày càng nâng cao chất lượng nhé!")


# =============================================================================
# 2. BẢNG TỔNG HỢP THỜI GIAN THỰC HIỂN THỊ KÊNH QUẢN LÝ BÁN TRÚ
# =============================================================================
def render_dashboard_danh_gia_live(base_dir="D:/", role_curr="Ban Giám hiệu"):
    """
    Dashboard tổng hợp báo cáo đánh giá bữa ăn theo thời gian thực (Real-time).
    Hiển thị tại kênh QUẢN LÝ BÁN TRÚ cho BGH, Quản nhiệm, Kế toán và Nhà bếp.
    """
    st.markdown("""
        <div style='background: linear-gradient(135deg, #1E40AF, #1D4ED8); padding: 12px 18px; border-radius: 10px; color: white; margin-bottom: 14px;'>
            <div style='display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:8px;'>
                <div>
                    <h3 style='margin:0; font-size: 19px; color: white; font-weight:800;'>📊 TỔNG HỢP Ý KIẾN & ĐÁNH GIÁ BỮA ĂN THỜI GIAN THỰC (REAL-TIME)</h3>
                    <p style='margin: 3px 0 0 0; opacity: 0.95; font-size: 13px;'>
                        Tổng hợp phản hồi trực tiếp từ 100% Học sinh & Phụ huynh bán trú về chất lượng các bữa ăn hàng ngày
                    </p>
                </div>
                <div style='background:rgba(255,255,255,0.22); padding:4px 12px; border-radius:14px; font-weight:bold; font-size:12px;'>
                    ⚡ DỮ LIỆU ĐỒNG BỘ LIVE
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    df_dg = lay_du_lieu_danh_gia(base_dir)

    if df_dg.empty:
        st.info("💡 Hiện tại chưa có dữ liệu đánh giá bữa ăn nào được gửi lên.")
        return

    # Bộ lọc nhanh
    c_f1, c_f2, c_f3, c_f4 = st.columns([1.2, 1, 1, 1])
    with c_f1:
        ds_ngay = ["Tất cả các ngày"] + sorted(list(df_dg["Ngày ăn"].unique()), reverse=True)
        loc_ngay = st.selectbox("📅 Lọc theo ngày:", ds_ngay, index=0, key="sb_loc_ngay_dg")
    with c_f2:
        loc_bua = st.selectbox("🍲 Lọc theo bữa ăn:", ["Tất cả các bữa", "Bữa trưa", "Bữa tối"], index=0, key="sb_loc_bua_dg")
    with c_f3:
        loc_muc = st.selectbox("⭐ Lọc mức đánh giá:", ["Tất cả mức", "Tốt", "Khá", "Không tốt"], index=0, key="sb_loc_muc_dg")
    with c_f4:
        loc_dt = st.selectbox("👥 Đối tượng gửi:", ["Tất cả", "Học sinh bán trú", "Phụ huynh bán trú"], index=0, key="sb_loc_dt_dg")

    df_view = df_dg.copy()
    if loc_ngay != "Tất cả các ngày":
        df_view = df_view[df_view["Ngày ăn"] == loc_ngay]
    if loc_bua != "Tất cả các bữa":
        df_view = df_view[df_view["Bữa ăn"] == loc_bua]
    if loc_muc != "Tất cả mức":
        df_view = df_view[df_view["Mức đánh giá"] == loc_muc]
    if loc_dt != "Tất cả":
        df_view = df_view[df_view["Vai trò"] == loc_dt]

    # --- KPI METRICS ---
    tong_dg = len(df_view)
    so_tot = len(df_view[df_view["Mức đánh giá"] == "Tốt"])
    so_kha = len(df_view[df_view["Mức đánh giá"] == "Khá"])
    so_kt = len(df_view[df_view["Mức đánh giá"] == "Không tốt"])

    ty_le_tot = (so_tot / tong_dg * 100) if tong_dg > 0 else 0
    ty_le_kha = (so_kha / tong_dg * 100) if tong_dg > 0 else 0
    ty_le_kt = (so_kt / tong_dg * 100) if tong_dg > 0 else 0
    ty_le_hai_long = ((so_tot + so_kha) / tong_dg * 100) if tong_dg > 0 else 0

    c_m1, c_m2, c_m3, c_m4 = st.columns(4)
    with c_m1:
        st.markdown(f"""
        <div style="background:#EFF6FF; border:1px solid #BFDBFE; border-left:4px solid #2563EB; padding:12px; border-radius:8px; text-align:center;">
            <div style="font-size:12px; color:#1E40AF; font-weight:bold;">TỔNG LƯỢT ĐÁNH GIÁ</div>
            <div style="font-size:24px; font-weight:800; color:#1D4ED8; margin:4px 0;">{tong_dg}</div>
            <div style="font-size:11.5px; color:#3B82F6;">Hài lòng: <b>{ty_le_hai_long:.1f}%</b></div>
        </div>
        """, unsafe_allow_html=True)
    with c_m2:
        st.markdown(f"""
        <div style="background:#ECFDF5; border:1px solid #A7F3D0; border-left:4px solid #059669; padding:12px; border-radius:8px; text-align:center;">
            <div style="font-size:12px; color:#065F46; font-weight:bold;">🟢 MỨC TỐT (NGON / ĐỦ)</div>
            <div style="font-size:24px; font-weight:800; color:#059669; margin:4px 0;">{so_tot}</div>
            <div style="font-size:11.5px; color:#047857;">Tỷ lệ: <b>{ty_le_tot:.1f}%</b></div>
        </div>
        """, unsafe_allow_html=True)
    with c_m3:
        st.markdown(f"""
        <div style="background:#FEFCE8; border:1px solid #FEF08A; border-left:4px solid #CA8A04; padding:12px; border-radius:8px; text-align:center;">
            <div style="font-size:12px; color:#854D0E; font-weight:bold;">🟡 MỨC KHÁ (CẦN NÂNG CAO)</div>
            <div style="font-size:24px; font-weight:800; color:#CA8A04; margin:4px 0;">{so_kha}</div>
            <div style="font-size:11.5px; color:#A16207;">Tỷ lệ: <b>{ty_le_kha:.1f}%</b></div>
        </div>
        """, unsafe_allow_html=True)
    with c_m4:
        st.markdown(f"""
        <div style="background:#FEF2F2; border:1px solid #FECACA; border-left:4px solid #DC2626; padding:12px; border-radius:8px; text-align:center;">
            <div style="font-size:12px; color:#991B1B; font-weight:bold;">🔴 KHÔNG TỐT (CẦN KHẮC PHỤC)</div>
            <div style="font-size:24px; font-weight:800; color:#DC2626; margin:4px 0;">{so_kt}</div>
            <div style="font-size:11.5px; color:#B91C1C;">Tỷ lệ: <b>{ty_le_kt:.1f}%</b></div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='margin-top:14px;'></div>", unsafe_allow_html=True)

    # --- BẢNG CHI TIẾT CÁC PHẢN HỒI ---
    st.subheader(f"📋 Danh Sách Nhận Xét Chi Tiết ({len(df_view)} phản hồi)")
    st.caption("Dữ liệu tự động cập nhật ngay khi học sinh hoặc phụ huynh gửi nhận xét.")

    cot_hien_thi = [
        "Thời gian", "Ngày ăn", "Bữa ăn", "Mức đánh giá", "Nhận xét món ăn", 
        "Người đánh giá", "Vai trò", "Lớp", "Phòng KTX"
    ]
    st.dataframe(
        df_view[[c for c in cot_hien_thi if c in df_view.columns]],
        use_container_width=True,
        hide_index=True
    )

    # Nút tải báo cáo Excel/CSV
    c_btn1, c_btn2 = st.columns([1, 2])
    with c_btn1:
        csv_dg_bytes = df_view.to_csv(index=False, encoding='utf-8-sig').encode('utf-8-sig')
        st.download_button(
            label="📥 TẢI DỮ LIỆU ĐÁNH GIÁ (EXCEL / CSV)",
            data=csv_dg_bytes,
            file_name=f"bao_cao_danh_gia_bua_an_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv",
            use_container_width=True
        )
    with c_btn2:
        if so_kt > 0:
            st.warning(f"⚠️ **Lưu ý nhà bếp:** Có **{so_kt} lượt đánh giá 'Không tốt'**. Thầy Quản nhiệm và Tổ trưởng bếp vui lòng đọc kỹ ghi chú nhận xét món ăn để điều chỉnh kịp thời cho bữa tiếp theo!")
        else:
            st.success("✅ **Chất lượng bữa ăn đạt chuẩn:** 100% học sinh và phụ huynh đánh giá mức Tốt và Khá. Cảm ơn Tổ nuôi dưỡng nhà bếp!")

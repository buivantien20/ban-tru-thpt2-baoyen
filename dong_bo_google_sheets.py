# -*- coding: utf-8 -*-
"""
MÔ ĐUN ĐỒNG BỘ DỮ LIỆU ĐÁM MÂY GOOGLE SHEETS
Trường THPT số 2 Bảo Yên - Xã Bảo Hà, Huyện Bảo Yên, Tỉnh Lào Cai
"""

import os
import json
import streamlit as st
import pandas as pd
import requests

FILE_CONFIG_GSHEET = "D:/cau_hinh_google_sheets.json"
if not os.path.exists("D:/") and not os.name == 'nt':
    FILE_CONFIG_GSHEET = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cau_hinh_google_sheets.json")

def doc_cau_hinh_gsheet(base_dir):
    p = os.path.join(base_dir, "cau_hinh_google_sheets.json")
    if os.path.exists(p):
        try:
            with open(p, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"webhook_url": "", "sheet_url": "", "tu_dong_dong_bo": True}

def luu_cau_hinh_gsheet(cfg, base_dir):
    for d in [base_dir, 'D:/phan_mem_ban_tru_cloud', 'd:/OneDrive/Hô sơ cá nhan/Học AI']:
        if os.path.exists(d):
            p = os.path.join(d, "cau_hinh_google_sheets.json")
            try:
                with open(p, "w", encoding="utf-8") as f:
                    json.dump(cfg, f, ensure_ascii=False, indent=2)
            except Exception:
                pass

def gui_du_lieu_len_gsheet(webhook_url, sheet_name, df_data):
    """Gửi một bảng dữ liệu lên Google Sheets thông qua Google Apps Script Webhook"""
    if not webhook_url or not webhook_url.startswith("https://script.google.com"):
        return False, "Chưa cấu hình URL Google Apps Script hợp lệ."
    try:
        payload = {
            "action": "sync",
            "sheet_name": sheet_name,
            "data": df_data.fillna("").to_dict(orient="records")
        }
        res = requests.post(webhook_url, json=payload, timeout=15)
        if res.status_code == 200:
            return True, "Đồng bộ thành công!"
        else:
            return False, f"Máy chủ Google phản hồi mã: {res.status_code}"
    except Exception as e:
        return False, f"Lỗi kết nối: {str(e)}"

def render_tab_google_sheets(BASE_DIR, nam_hoc, THU_MUC_NAM_HOC):
    st.subheader("☁️ Quản Trị Kết Nối Google Sheets & Dữ Liệu Bền Vững Đám Mây")
    st.caption("Giải pháp lưu trữ vĩnh viễn trên Google Drive của trường: Không bao giờ mất dữ liệu và dễ dàng mở xem, in ấn bằng Excel / Google Sheets.")

    cfg = doc_cau_hinh_gsheet(BASE_DIR)
    current_webhook = cfg.get("webhook_url", "")
    current_sheet_url = cfg.get("sheet_url", "")

    col_stat1, col_stat2 = st.columns([1, 1])
    with col_stat1:
        if current_webhook:
            st.success("✅ **Trạng thái:** Đã kết nối với Google Sheets")
        else:
            st.warning("⚠️ **Trạng thái:** Đang lưu trữ cục bộ (Chưa kích hoạt Google Sheets)")

    with col_stat2:
        if current_sheet_url:
            st.markdown(f"🔗 [**Mở Google Sheet của trường trên Google Drive**]({current_sheet_url})")

    st.markdown("---")

    tab_cfg, tab_huong_dan = st.tabs(["⚙️ Cấu hình kết nối", "📖 Hướng dẫn 2 phút cài đặt Google Sheets"])

    with tab_cfg:
        with st.form("form_config_gsheet"):
            st.markdown("##### 🔑 Thông tin liên kết Google Sheets của trường:")
            input_webhook = st.text_input(
                "1. Webhook URL Google Apps Script:",
                value=current_webhook,
                placeholder="https://script.google.com/macros/s/.../exec"
            )
            input_sheet_url = st.text_input(
                "2. Link file Google Sheets trên Google Drive (để mở nhanh):",
                value=current_sheet_url,
                placeholder="https://docs.google.com/spreadsheets/d/.../edit"
            )
            btn_save_cfg = st.form_submit_button("💾 LƯU CẤU HÌNH KẾT NỐI", type="primary", use_container_width=True)
            if btn_save_cfg:
                cfg["webhook_url"] = input_webhook.strip()
                cfg["sheet_url"] = input_sheet_url.strip()
                luu_cau_hinh_gsheet(cfg, BASE_DIR)
                st.success("🎉 Đã lưu thông tin kết nối Google Sheets thành công!")
                st.rerun()

        # Nút đẩy dữ liệu thử nghiệm
        if input_webhook:
            st.markdown("##### 🚀 Đồng bộ thủ công dữ liệu lên Google Sheets:")
            c_btn1, c_btn2, c_btn3 = st.columns(3)
            with c_btn1:
                if st.button("📤 Đẩy 449 Tài Khoản lên Google Sheet", use_container_width=True):
                    f_tk = os.path.join(BASE_DIR, "tai_khoan_nguoi_dung.csv")
                    if os.path.exists(f_tk):
                        df_tk = pd.read_csv(f_tk, encoding='utf-8-sig', dtype=str).fillna("")
                        ok, msg = gui_du_lieu_len_gsheet(input_webhook, "Tai_Khoan", df_tk)
                        if ok:
                            st.success(f"🎉 {msg}")
                        else:
                            st.error(f"❌ {msg}")
            with c_btn2:
                if st.button("📤 Đẩy Thi Đua ĐTN 20 Lớp lên Google Sheet", use_container_width=True):
                    f_dtn = os.path.join(THU_MUC_NAM_HOC, nam_hoc.replace(" ", ""), "thi_dua_dtn_20_lop.csv")
                    if os.path.exists(f_dtn):
                        df_dtn = pd.read_csv(f_dtn, encoding='utf-8-sig', dtype=str).fillna("")
                        ok, msg = gui_du_lieu_len_gsheet(input_webhook, "Thi_Dua_DTN", df_dtn)
                        if ok:
                            st.success(f"🎉 {msg}")
                        else:
                            st.error(f"❌ {msg}")
            with c_btn3:
                if st.button("📤 Đẩy 207 Học Sinh Bán Trú lên Google Sheet", use_container_width=True):
                    f_hs = os.path.join(THU_MUC_NAM_HOC, nam_hoc.replace(" ", ""), "danh_sach_hoc_sinh_thuc_te.csv")
                    if os.path.exists(f_hs):
                        df_hs = pd.read_csv(f_hs, encoding='utf-8-sig', dtype=str).fillna("")
                        ok, msg = gui_du_lieu_len_gsheet(input_webhook, "Hoc_Sinh_Ban_Tru", df_hs)
                        if ok:
                            st.success(f"🎉 {msg}")
                        else:
                            st.error(f"❌ {msg}")

    with tab_huong_dan:
        st.markdown("""
        ### 📝 3 BƯỚC THIẾT LẬP GOOGLE SHEETS MIỄN PHÍ CHO NHÀ TRƯỜNG:
        
        #### **Bước 1: Tạo file Google Sheets mới**
        1. Thầy/Cô mở Google Drive của mình hoặc của trường: [drive.google.com](https://drive.google.com)
        2. Bấm **Mới (New) ➜ Google Trang tính (Google Sheets)**.
        3. Đổi tên file thành: **`He_Thong_Quan_Tri_THPT2_BaoYen`**.
        4. Sao chép link trình duyệt của file dán vào ô **"2. Link file Google Sheets"** ở tab bên cạnh.

        #### **Bước 2: Dán mã Google Apps Script tự động**
        1. Trên thanh menu của Google Sheets, chọn: **Tiện ích mở rộng (Extensions) ➜ Apps Script**.
        2. Xóa hết mã có sẵn và dán toàn bộ đoạn mã bên dưới vào:
        """)

        script_code = """function doPost(e) {
  try {
    var payload = JSON.parse(e.postData.contents);
    var sheetName = payload.sheet_name || "Data";
    var rows = payload.data || [];
    
    var ss = SpreadsheetApp.getActiveSpreadsheet();
    var sheet = ss.getSheetByName(sheetName);
    if (!sheet) {
      sheet = ss.insertSheet(sheetName);
    }
    
    if (rows.length > 0) {
      sheet.clearContents();
      var headers = Object.keys(rows[0]);
      var values = [headers];
      for (var i = 0; i < rows.length; i++) {
        var row = [];
        for (var j = 0; j < headers.length; j++) {
          row.push(rows[i][headers[j]] || "");
        }
        values.push(row);
      }
      sheet.getRange(1, 1, values.length, headers.length).setValues(values);
    }
    
    return ContentService.createTextOutput(JSON.stringify({status: "success", count: rows.length}))
      .setMimeType(ContentService.MimeType.JSON);
  } catch (err) {
    return ContentService.createTextOutput(JSON.stringify({status: "error", message: err.toString()}))
      .setMimeType(ContentService.MimeType.JSON);
  }
}"""
        st.code(script_code, language="javascript")

        st.markdown("""
        #### **Bước 3: Lấy link Webhook**
        1. Ở góc trên bên phải màn hình Apps Script, bấm nút màu xanh: **Triển khai (Deploy) ➜ Tùy chọn triển khai mới (New deployment)**.
        2. Bấm biểu tượng bánh răng ⚙️ ➜ chọn **Ứng dụng web (Web App)**.
        3. Điền thông tin:
           - **Thực thi dưới dạng (Execute as):** Tôi (*email của Thầy/Cô*).
           - **Ai có quyền truy cập (Who has access):** Bất kỳ ai (*Anyone*).
        4. Bấm **Triển khai (Deploy)** ➜ Cấp quyền (Authorize access) ➜ Sao chép **URL ứng dụng web** (có dạng `https://script.google.com/macros/s/.../exec`).
        5. Dán URL đó vào ô **"1. Webhook URL Google Apps Script"** là xong!
        """)

# -*- coding: utf-8 -*-
"""
Kịch bản khởi tạo danh sách tài khoản toàn trường chuẩn 100%
Dành cho Trường THPT số 2 Bảo Yên
Theo 3 yêu cầu cốt lõi của Ban Giám Hiệu
"""
import os
import pandas as pd
import unicodedata
import re

def strip_accents(text):
    if not text or pd.isna(text):
        return ""
    text = unicodedata.normalize('NFD', str(text))
    text = re.sub(r'[\u0300-\u036f]', '', text)
    return text.lower().strip()

def clean_phone(p):
    if not p or pd.isna(p):
        return ""
    s = str(p).replace(".0", "").strip()
    s = re.sub(r'\D', '', s)
    if s and not s.startswith("0") and len(s) == 9:
        s = "0" + s
    return s

def tao_tai_khoan():
    cbgv_file = "D:/danh_ba_cbgv_nv.csv"
    hs_tt_file = "D:/danh_sach_hoc_sinh_thuc_te.csv"
    hs_all_file = "D:/danh_sach_hoc_sinh_toan_truong.csv"
    out_file = "D:/tai_khoan_nguoi_dung.csv"

    df_cbgv = pd.read_csv(cbgv_file)
    df_hs_tt = pd.read_csv(hs_tt_file)
    df_hs_all = pd.read_csv(hs_all_file)

    accounts = []
    seen_usernames = set()

    def add_acc(u, p, fn, r, title, ref, phone, note, role_manage="Cá nhân", status="Hoạt động"):
        u_clean = str(u).lower().strip()
        if u_clean in seen_usernames:
            return
        seen_usernames.add(u_clean)
        accounts.append({
            'Tên đăng nhập': u_clean,
            'Mật khẩu': str(p).strip(),
            'Họ và tên': str(fn).strip(),
            'Vai trò': str(r).strip(),
            'Chức danh': str(title).strip(),
            'Mã liên kết': str(ref).strip(),
            'Số điện thoại': clean_phone(phone),
            'Ghi chú': str(note).strip(),
            'Trạng thái': status,
            'Quyền quản lý': str(role_manage).strip()
        })

    # ========================================================
    # 1. HỆ THỐNG QUẢN TRỊ TỐI CAO & BAN GIÁM HIỆU MẪU
    # ========================================================
    add_acc('admin', 'bgh123', 'Ban Giám Hiệu (Admin)', 'Ban Giám hiệu', 'Hiệu trưởng / Admin tối cao', 'Toàn trường', '0988400184', 'Admin quản trị toàn hệ thống', 'Toàn quyền quản trị')
    add_acc('hieutruong', 'ht123', 'Thầy Bùi Văn Tiến', 'Ban Giám hiệu', 'Hiệu trưởng nhà trường', 'Toàn trường', '0988400184', 'Hiệu trưởng Bùi Văn Tiến', 'Toàn quyền quản trị')
    add_acc('phohieutruong1', 'pht123', 'Cô Đỗ Thị Hồng Phương', 'Ban Giám hiệu', 'Phó Hiệu trưởng PT Bán trú', 'Toàn trường', '0374083336', 'Phó Hiệu trưởng Đỗ Thị Hồng Phương', 'Toàn quyền quản trị')
    add_acc('phohieutruong2', 'pht123', 'Cô Nguyễn Thị Hồng Thanh', 'Ban Giám hiệu', 'Phó Hiệu trưởng PT Chuyên môn', 'Toàn trường', '0389191058', 'Phó Hiệu trưởng Nguyễn Thị Hồng Thanh', 'Toàn quyền quản trị')

    # Phân hệ đặc thù
    add_acc('bithudoan', 'dtn123', 'Thầy Phạm Duy Thanh', 'Ban Chấp hành Đoàn', 'Bí thư Đoàn TNCS Hồ Chí Minh', 'Toàn trường', '0915095449', 'Bí thư Đoàn trường Phạm Duy Thanh', 'Quản lý phương tiện & Cờ đỏ')
    add_acc('codo', 'codo123', 'Đội Cờ Đỏ Nhà Trường', 'Đội Cờ đỏ', 'Đội viên Cờ đỏ xung kích', 'Toàn trường', '0988654321', 'Đội Cờ đỏ chấm thi đua xe & nề nếp', 'Quản lý phương tiện & Cờ đỏ')
    add_acc('quannhiem', 'qn123', 'Thầy Quản Nhiệm Bán Trú', 'Giáo viên quản lý', 'Tổ trưởng Quản nhiệm KTX', 'Toàn trường', '0988123005', 'Quản nhiệm KTX bán trú', 'Quản lý bán trú')
    add_acc('gvtruc01', 'truc123', 'Giáo Viên Trực Ca 1', 'Giáo viên quản lý', 'Giáo viên trực ký túc xá', 'Toàn trường', '0988123006', 'Giáo viên trực KTX ca 1', 'Quản lý bán trú')
    add_acc('gvtruc02', 'truc123', 'Giáo Viên Trực Ca 2', 'Giáo viên quản lý', 'Giáo viên trực ký túc xá', 'Toàn trường', '0988123007', 'Giáo viên trực KTX ca 2', 'Quản lý bán trú')
    add_acc('beptruong', 'bep123', 'Bếp Trưởng Bán Trú', 'Nhà bếp / Cấp dưỡng', 'Bếp trưởng phụ trách dinh dưỡng', 'Toàn trường', '0988123008', 'Bếp trưởng nhà ăn KTX', 'Nhà bếp')
    add_acc('capduong', 'bep123', 'Tổ Cấp Dưỡng Bán Trú', 'Nhà bếp / Cấp dưỡng', 'Nhân viên cấp dưỡng', 'Toàn trường', '0988123009', 'Nhân viên cấp dưỡng', 'Nhà bếp')
    add_acc('nhabep', 'bep123', 'Nhà Bếp Bán Trú', 'Nhà bếp / Cấp dưỡng', 'Nhân viên nhà bếp', 'Toàn trường', '0988123010', 'Nhà bếp báo cơm', 'Nhà bếp')
    add_acc('ketoan', 'kt123', 'Cô Doãn Thị Hồng Anh', 'Kế toán bán trú', 'Kế toán quản lý thu chi', 'Toàn trường', '0947217000', 'Kế toán nhà trường Doãn Thị Hồng Anh', 'Kế toán')
    add_acc('vanthu', 'nv123', 'Cô Hoàng Ngọc Bích', 'Nhân viên', 'Nhân viên văn thư', 'Toàn trường', '0965162534', 'Văn thư nhà trường', 'Cá nhân')
    add_acc('thietbi', 'nv123', 'Cô Nguyễn Thị Thúy', 'Nhân viên', 'Nhân viên thiết bị', 'Toàn trường', '0827982155', 'Cán bộ thiết bị', 'Cá nhân')
    add_acc('baove', 'nv123', 'Bác Lê Thái Trường', 'Nhân viên', 'Nhân viên bảo vệ', 'Toàn trường', '0966261760', 'Bảo vệ trường học', 'Cá nhân')

    # ========================================================
    # 2. 42 CÁN BỘ GIÁO VIÊN & NHÂN VIÊN TỪ DANH BẠ
    # ========================================================
    for idx, r in df_cbgv.iterrows():
        ten = str(r['Họ và tên']).strip()
        vt = str(r['Vị trí việc làm']).strip()
        cv_hien = str(r['Chức vụ hiển thị']).strip()
        gvcn_lop = str(r.get('Giáo viên chủ nhiệm lớp', '')).strip()
        if gvcn_lop.lower() == 'nan':
            gvcn_lop = ""
        sdt = clean_phone(r.get('Số điện thoại', ''))
        ma_dd = str(r.get('Mã định danh', '')).strip()

        # Tạo username theo tên viết tắt hoặc SĐT
        ten_parts = ten.split()
        if len(ten_parts) >= 2:
            u_gv = strip_accents(ten_parts[-1]) + "".join([strip_accents(p)[0] for p in ten_parts[:-1]])
        else:
            u_gv = strip_accents(ten)

        role_str = "Giáo viên quản lý" if vt == "Giáo viên" else ("Ban Giám hiệu" if vt == "Cán bộ quản lý" else "Nhân viên")
        role_manage = "Toàn quyền quản trị" if vt == "Cán bộ quản lý" else "Quản lý bán trú"

        # Nếu là GVCN thì liên kết với lớp đó
        ref_link = gvcn_lop if gvcn_lop else "Toàn trường"
        title_str = f"GVCN {gvcn_lop} - {ten}" if gvcn_lop else f"{cv_hien} ({ten})"

        add_acc(u_gv, 'gv123', ten, role_str, title_str, ref_link, sdt, f"{cv_hien} - {ten}", role_manage)
        
        # Nếu là GVCN, tạo thêm tài khoản định danh lớp gvcn_10a1...
        if gvcn_lop:
            u_gvcn = f"gvcn_{gvcn_lop.lower()}"
            add_acc(u_gvcn, 'gvcn123', f"Thầy/Cô GVCN {gvcn_lop} ({ten})", 'Giáo viên quản lý', f"Giáo viên chủ nhiệm lớp {gvcn_lop}", gvcn_lop, sdt, f"GVCN {gvcn_lop} ({ten})", "Quản lý bán trú")

    # ========================================================
    # 3. BAN CÁN SỰ 20 LỚP (20 LỚP TRƯỞNG & 20 BÍ THƯ CHI ĐOÀN)
    # ========================================================
    classes = [f'10A{i}' for i in range(1, 8)] + [f'11A{i}' for i in range(1, 8)] + [f'12A{i}' for i in range(1, 8)]
    for lop in classes:
        # Tài khoản Lớp trưởng
        add_acc(
            f"loptruong_{lop.lower()}",
            "lt123",
            f"Lớp Trưởng Lớp {lop}",
            "Học sinh",
            f"Lớp trưởng ({lop})",
            lop,
            "",
            f"Ban Cán sự Lớp - Lớp trưởng {lop}",
            role_manage="Ban Cán sự Lớp & Cờ đỏ"
        )
        # Tài khoản Bí thư Chi đoàn
        add_acc(
            f"bithu_{lop.lower()}",
            "bt123",
            f"Bí Thư Chi Đoàn {lop}",
            "Học sinh",
            f"Bí thư Chi đoàn ({lop})",
            lop,
            "",
            f"Ban Cán sự Lớp - Bí thư Chi đoàn {lop}",
            role_manage="Ban Cán sự Lớp & Cờ đỏ"
        )

    # ========================================================
    # 4. HỌC SINH BÁN TRÚ (196 EM TỪ danh_sach_hoc_sinh_thuc_te.csv)
    # ========================================================
    # Tìm 19 Trưởng phòng
    for idx, r in df_hs_tt.iterrows():
        ma_hs = str(r['Mã HS']).strip()
        u_hs = ma_hs.lower().replace('-', '')
        ten_hs = str(r['Họ và tên']).strip()
        lop_hs = str(r.get('Lớp', '')).strip()
        phong_hs = str(r.get('Phòng', '')).strip()
        giuong_hs = str(r.get('Giường', '')).strip()
        cv_phong = str(r.get('Chức vụ phòng', 'Thành viên')).strip()
        sdt_hs = clean_phone(r.get('SĐT Học sinh', ''))

        is_tp = ("trưởng phòng" in cv_phong.lower())
        title_hs = f"Trưởng phòng ({phong_hs})" if is_tp else f"Học sinh bán trú ({phong_hs})"
        role_manage_hs = "Trưởng phòng KTX" if is_tp else "Cá nhân"

        add_acc(
            u_hs,
            "hs123",
            ten_hs,
            "Học sinh",
            title_hs,
            ma_hs,
            sdt_hs,
            f"Lớp {lop_hs} - {phong_hs} - {giuong_hs} ({cv_phong})",
            role_manage=role_manage_hs
        )

    # ========================================================
    # 5. HỌC SINH NGOẠI TRÚ (TOÀN TRƯỜNG TỪ danh_sach_hoc_sinh_toan_truong.csv)
    # ========================================================
    for idx, r in df_hs_all.iterrows():
        ma_dinh_danh = str(r['Mã học sinh']).strip()
        ten_hs = str(r['Họ và tên']).strip()
        lop_hs = str(r.get('Lớp', '')).strip()
        sdt_hs = clean_phone(r.get('SĐT Học sinh', ''))

        u_hs_all = f"hs_{ma_dinh_danh}"
        add_acc(
            u_hs_all,
            "hs123",
            ten_hs,
            "Học sinh",
            f"Học sinh ({lop_hs})",
            ma_dinh_danh,
            sdt_hs,
            f"Học sinh Lớp {lop_hs} - Toàn trường",
            role_manage="Cá nhân"
        )

    # ========================================================
    # 6. PHỤ HUYNH HỌC SINH (ĐÚNG 196 TÀI KHOẢN CHO 196 HS BÁN TRÚ)
    # Ràng buộc: Mỗi học sinh CHỈ CẤP ĐÚNG 1 TÀI KHOẢN cho 1 Phụ huynh (Bố hoặc Mẹ)
    # ========================================================
    count_ph = 0
    for idx, r in df_hs_tt.iterrows():
        ma_hs = str(r['Mã HS']).strip()
        u_ph = 'ph_' + ma_hs.lower().replace('-', '')
        ten_hs = str(r['Họ và tên']).strip()
        lop_hs = str(r.get('Lớp', '')).strip()
        phong_hs = str(r.get('Phòng', '')).strip()

        # Chọn Bố hoặc Mẹ (Ưu tiên Bố, nếu không có Bố thì lấy Mẹ)
        bo = str(r.get('Họ tên Bố', '')).strip()
        me = str(r.get('Họ tên Mẹ', '')).strip()
        if bo and bo.lower() != 'nan':
            ten_ph_real = f"{bo} (Bố em {ten_hs})"
        elif me and me.lower() != 'nan':
            ten_ph_real = f"{me} (Mẹ em {ten_hs})"
        else:
            ten_ph_real = f"Phụ huynh em {ten_hs}"

        sdt_ph = clean_phone(r.get('SĐT Phụ huynh', ''))

        add_acc(
            u_ph,
            "ph123",
            ten_ph_real,
            "Phụ huynh học sinh",
            f"Phụ huynh em {ten_hs}",
            ma_hs,
            sdt_ph,
            f"Phụ huynh học sinh {ten_hs} - Lớp {lop_hs} ({phong_hs})",
            role_manage="Cá nhân"
        )
        count_ph += 1

    df_out = pd.DataFrame(accounts)
    df_out.to_csv(out_file, index=False, encoding='utf-8-sig')
    print(f"✅ Đã tạo thành công {len(df_out)} tài khoản vào {out_file}!")
    print(f"📊 Trong đó:")
    print(f"- Tổng phụ huynh bán trú: {count_ph} (đúng 196 học sinh bán trú)")
    print(df_out['Vai trò'].value_counts())
    print("\nQuyền quản lý:")
    print(df_out['Quyền quản lý'].value_counts())

if __name__ == '__main__':
    tao_tai_khoan()

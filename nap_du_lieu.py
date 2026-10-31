import csv

raw_data = """PHÂN PHÒNG HỌC SINH ĐĂNG KÝ Ở BÁN TRÚ NĂM HỌC 2026 - 2027  - BÁN TRÚ NAM,,,,,,,,,,,,,,,
NAM,,,,,,,,,,,,,,,
TT,Phòng,SL,Họ và tên,Lớp,"Giới
 tính","Dân
 tộc",Thôn ,Xã,Phụ huynh ,,SĐT (Bố/mẹ),SĐT học sinh,Cách trường (KM),Ghi chú,
,,,,,,,,,Họ - tên Bố,Họ -  tên Mẹ,,,,,
1,308,1,Bàn Hải Phong ,10a1,Nam,Dao,Khe Bàn,Bảo Hà,Bàn Văn Trịnh,Lý Thị Neo,867106916,971909148,12,,
2,,2,Đặng Đức Khiêm,10a1,Nam,Dao,Bông,Bảo Hà,Đặng Văn Hoàng,Triệu Thị Phấy,977183836,869753415,10,,
3,,3,Hoàng Minh Quân,10a1,Nam,Tày,Cam cọn 1,Bảo Hà,Hoàng Văn Nhiễu,Hoàng Thị Nhàn,971994864,869889243,16,,
4,,4,Hoàng Quốc Phòng ,10a1,Nam,xa phó ,Nhai thổ 2 ,Bảo Hà ,Hoàng Văn Hải ,Tẩn San Mẩy ,387149387,327654940,20,,
5,,5,Hoàng Xuân Huần,10a1,Nam,Tày,3 nhai thổ,Bảo Hà,Hoàng Văn Hoà,Sầm thị biết,365140211,377690811,18,,
6,,6,Nông Đức Duy,10a1,Nam ,Dao,Bông,Bảo hà,Nông Ton Pham,Sầm Thị Nghè,366675523,325242301,10,,
7,,7,Hoàng Thừa Tài ,10a1,nam,Dao,Khe Bàn ,Bảo Hà ,  Hoàng Xuân Lâm ,   Triệu Thị Náy ,335402730,33509143,15km,,
8,,8,Hoàng Văn Ánh,10a1,Nam,Tày,Thôn 3AB,Bảo Hà ,Hoàng Văn Hoàn,Hoàng Thị Hòa,*0336821553,*0334172984,,,
9,,9,Triệu Quang Vũ,10A2,Nam,Kinh,Tân Thành,Bảo Hà,Triệu Công Đoàn,Hoàng Thị Tuyết,382528034,373502163,15,,
10,,10,Sùng Thuận Phong,10A2,Nam,H'Mông,Thùng 2,Bảo Hà,Sùng A Giáo,Thào Thị Đấu,382221652,344448939,7,,
11,,11,Lý Quang Hùng,10A3,Nam,Dao,1 Nhai Tẻn,Bảo Hà,Lý Văn Thành,Bàn Thị Tánh,0985125102,0389175004,,,
12,307,1,Đặng Minh Toan,10A3,Nam,Phù Lá,2 Nhai Thổ,Bảo Hà,Đặng Văn Túc,Hoàng Thị Xuân,0392724342,0383066871,17km,,
13,,2,Hoàng Gia Bảo,10A3,Nam,Tày,3AB,Bảo Hà,Hoàng Văn Tuyến,Hoàng Thị Huế,0337287811,0327065011,17km,,
14,,3,Hà Chí Tường,10A3,Nam,Tày,6AB,Bảo Hà,Hà Văn Hướng,Hoàng Thị Mến,0345554070,0357756445,10km,,
15,,4,Hoàng Đức Lương,10A3,Nam,Tày,7AB,Bảo Hà,Hoàng Văn Thành,Nguyễn Thị Kiều,0362754731,0339259811,16km,,
16,,5,Lý Chí Kiên,10A3,Nam,Dao,1 Nhai Tẻn,Bảo Hà,Lý Văn Sơn,Lý Thị Nguyên,0385305641,0383819941,16km,,
17,,6,Hoàng Phi Long,10A3,Nam,Tày,Cao Sơn,Bảo Hà,Hoàng Văn Hằng,Đặng Thị Tình,0977815398,0367424987,18km,Khuyết tật,
18,,7,Đặng Quang Dũng,10A3,Nam,Dao,Thống Nhất,Bảo Hà,Đặng Văn Tiên,Trần Thị Thắm,0906194200,0702041505,10km,,
19,,8,Bàn Minh Đức,10A3,Nam,Dao,Thống Nhất,Bảo Hà,Bàn Văn May,Bàn Thị Lan,0388039801,,10km,,
20,,9,Hoàng Hữu Duy,10A3,Nam,Tày,Khoai 2,Bảo Hà,Hoàng Văn Đức,Triệu Thị Phương,0964141142,,12km,,
21,,10,Nông Xuân Kiểm,10A3,Nam,Tày,3AB,Bảo Hà,Nông Văn Đại,Dương Thi Oai,0364247326,0862705096,17km,,
22,,11,Bàn Quốc Anh,10A4,Nam,Dao,4 Nhai Thổ,Bảo Hà,Nguyễn Duy Thưởng,Bàn Thị Hoa,0868640391,0327590264,15,,
23,306,1,Bàn Thành Nghiệp,10A4,Nam,Dao,Bông 3,Bảo Hà,Bàn Ton San,Đặng Thị Hương,0359845021,0367313671,11,,
24,,2,Đặng Nguyên Long,10A4,Nam,Dao,Bông 3,Bảo Hà,Đặng Văn Hùng,Đặng Thị Nhình,966231870,357413720,11,,
25,,3,Đặng Nguyên Lương,10A4,Nam,Dao,Bông 3,Bảo Hà,Hoàng Văn Ngợi,Đặng Thị Sàn,0915586635,349976830,11,,
26,,4,Hà Xuân Quang,10A4,Nam,Tày,6AB,Bảo Hà,Hà Văn Long,Hoàng Thị Bến,0359615338,352633953,13,,
27,,5,Hoàng Trung Đức,10A4,Nam,Tày,3 AB,Bảo Hà ,Hoàng Văn Huỳnh,Hoàng Thị Chuyến,394977390,862105274,15,,
28,,6,Hoàng Văn Thượng,10A4,Nam,Tày,7AB,Bảo Hà,Hoàng văn Hoàng ,Đinh Thị Hằng ,0968022730,0335508944,12,,
29,,7,Bùi Đức Hiếu,10A7,Nam,Nùng,1 Tân Văn,Bảo Hà,Bùi Văn Minh,Hoàng Thị Ban,0879005432,0975994825,15,Mồ côi bố,
30,,8,Lý Văn Hiếu,10A7,Nam,Dao,Nhai Tẻn,Bảo Hà,Lý Văn Đức,Đặng Thị Ngọc,0386690111,0355298309,20,,
31,,9,Nguyễn Tiến Thành,10A7,Nam,Cao Lan,Bản Khoai 3,Bảo Hà,Nguyễn Văn Tý,Hoàng Thị Lê,0813658987,,10,,
32,,10,Triệu Đức Lương,10A7,Nam,Tày,Bản Khoai 2,Bảo Hà,Triệu Văn Phong,Triệu Thị Mẳn,0337554986,,15,,
33,305,1,Triệu Văn Tuấn,10A7,Nam,Dao,Khe Bàn,Bảo Hà,Triệu Tòn Khách,Triệu Thị Tam,0359796861,,15,,
34,,2,Hoàng Quốc Tân,11A1,Nam,Tày,3AB,Bảo Hà,Hoàng Văn Tuyệt,Chu Thị Tuất,986295990,357689190,16km,,
35,,3,Cư Seo Tánh ,11A1,Nam,H'mông,Thíp Dạo,Lâm Giang,Cư Seo Giả,Sùng Thị Mê,355802206,356063728,11,Mồ côi bố,
36,,4,Đặng Tuấn Anh ,11A1,Nam,Dao,1 nhai tẻn,Bảo Hà,Đặng Quang lợi,Đặng Thị Hà,986391620,333785199,20,,
37,,5,Hoàng đình Khải ,11A1,Nam,Tày,2AB,Bảo Hà,Hoàng văn nhu,Hoàng Thị Diên,362013615,357508650,15,,
38,,6,Đoàn Bình Tin,11A2,Nam ,Kinh,Cam Cọn 2,Bảo Hà  ,Đoàn Xuân Hưng,Sầm Thị Mơ,0362615095,0326730495,16,,
39,,7,Lý Thành Vương ,11A2,Nam ,Dao ,Cọn 2,Bảo Hà  ,Lý Văn Bắc,Bàn Thị Hoảnh ,0987220421,0868556054,17,,
40,,8,Ma Seo Cương ,11A2,Nam ,Mông,Thùng ,Bảo Hà  ,Ma Seo Vẳng,Vàng Thị Si,0336161311,,7,,
41,,9,Đặng Thanh Lâm,11A2,Nam ,Dao ,Nhai Tẻn 2,Bảo Hà  ,ĐặngVăn Thắng,Đặng Thị Hoa,0961252844,0338639155,22,,
42,,10,Nguyễn Tùng Dương,11A2,Nam ,Kinh,Cam Cọn 1,Bảo Hà  ,Nguyễn Văn Sơn,Đoàn Thị Liên,0375591987,0818233010,15,,
43,,11,Trần Văn Cương ,11A2,Nam ,Tày ,Khoai 2,Bảo Hà  ,Trần Văn Biên,Hoàng Thị Thượng,0382263861,0347059024,12,,
44,304,1,Triệu Tiến Chu,11A2,Nam ,Dao ,Khe Bàn,Bảo Hà  ,Triệu Văn Minh,Lý Thị Xuân,0373021933,0869511475,11,,
45,,2,Hoàng Văn Yên,11A3,Nam,Tày,Cọn 2,Bảo Hà,Hoàng Văn Nhất,Lương Thị Lâm,0326862213,0326862213,15,,
46,,3,Trương Ngọc Quý,11A3,Nam,Tày, Bỗng Buôn,Bảo hà,Trương Văn Hùng,Ngô Thị Biên,0332167706,0869954329,14,,
47,,4,Triệu Kim Ngân,11A3,Nam,Dao, Bỗng Buôn,Bảo hà,Triệu Văn Hai,Triệu Thị Mấy,0339005679,0968940910,15,,
48,,5,Nông Tài Phú,11A3,Nam,Dao,Lỵ 1-2,Bảo hà,Nông Văn Quý ,Trần Thị Lai,0332167706,0788006714,12,,
49,,6,Phùng Kim Ngân,11A3,Nam,Dao,Khe Bàn,Bảo hà,Phùng Tòn Cau,Triệu Thị Còi,0989215410,0375618620,15,,
50,,7,Nguyễn Tuấn Hưng,11A3,Nam,Tày,Bông 1-2,Bảo hà,Nguyễn Văn Oanh,Lý Thị Chản,0336338785,0343797540,10,,
51,,8,Ma A Chính,11A3,Nam,H mông,Thùng 2,Bảo hà,Ma Seo Dình,Giàng Thị Líu,0398513625,0368265904,10,,
52,,9,Ma Seo Minh,11A3,Nam,H mông,Thùng 3,Bảo hà,Ma Seo Kếnh,Thào Thị Súa,0984417060,0867594844,10,,
53,,10,Nguyễn Đoàn Huy ,11A3,Nam,Thái,Thôn 1Tân Văn,Bảo hà,Nguyễn Văn Tuyên,La Thị Sim,0379284224,0969491485,13,,
54,,11,Sầm Quyết Thắng,11A3,Nam,Kinh,Bỗng Buôn,Bảo hà,Sầm Văn Chiến,Nông Thị Kiểm,0367966816,0347819042,14,,
55,303,1,Lê Tiến Dũng,11A4,Nam,Dao,Nhai Tẻn,Bảo Hà,Lê Văn Quý,Đặng Thị Liên,0973108813,,11,,
56,,2,Lương Đình Nhật,11A4,Nam,Tày,Thôn Kim sơn,Bảo Hà,Lương Văn Minh,Hoàng Thị Biền,0982330038,,11,,
57,,3,Ma Gia Huy,11A4,Nam,Mông,Thôn Thùng ,Bảo Hà,Ma Seo Trang,Giàng Thị Phương,0329345427,,7,,
58,,4,Nông Quang Lê,11A4,Nam,Dao,Thôn bông,Bảo Hà,Nông Hữu Long,Hoàng Thị Ghến,0967112007,,8,,
59,,5,Trần Quang Chiến,11A4,Nam,Dao,Thống nhất,Bảo Hà,Trần Văn Sáng,Trần Thị Nọi,0961039921,,12,,
60,,6,Hoàng Quốc Dân,11A4,Nam,Tày,3AB,Bảo Hà,Hoàng Văn Định,Hà Thị Duyên,374381468,337092110,15,vắng,
61,,7,Triệu Tiến Duy,11A4,Nam,Dao,Thống nhất,Bảo Hà,Triệu Văn Dung,Lý Thị Êm,0823620135,,11,vắng,
62,,8,Đặng Văn Học,11a5,Nam,dao,Liên Sơn,Lâm Giang,Đặng Văn Thắng,Đỗ Thị Hoàn,975510175,528043975,11,,
63,,9,Hoàng Xuân Trường,11a5,nam,tày,Kim sơn,Bảo Hà,Hoàng Văn Toàn ,Lý Thị Hưng,964744195,339996815,16,,
64,,10,Nguyễn Sinh Hùng,11a5,nam,tày,Bỗng Buôn,Bảo Hà,Nguyễn Văn Lả,Nông Thị Cảnh,965866703,377027607,12,,
65,,11,Nguyễn Trịnh Quang,11a5,nam,kinh,Bảo Ân,Bảo Hà,Nguyễn Long Phi,Nguyễn Thị Thu,366474580,865729436,15,,
66,302,1,Triệu Hữu Dũng,11a5,nam,dao,Bỗng Buôn,Bảo Hà,Triệu Văn Lạng,Triệu Thị Thim,326860289,966588213,15,,
67,,2,Đặng Hải Nam,11A6,Nam,Dao,4 Nhai Thổ,Bảo Hà,Đặng Văn  Bìn,Đặng Thị Nga,0327297821,,19,,
68,,3,Hảng Thuận Phú,11A6,Nam,Mông,Bùn Dạo,Lam Giang,Hảng Seo Thành,Vàng Thị Chẩu,0979630403,0373342490,15,,
69,,4,Hà Duy Lợi,11A7,Nam,Tày,Kim Sơn,Bảo Hà,Hà Ngọc Chuyển,Hoàng Thị Đậm,0345526774,0356663914,15,,
70,,5,Lý Minh Bảo,11A7,Nam,Dao,Nhai Tẻn,Bảo Hà,Lý Văn Giáp,Đặng Thị Lan,0963970115,0333281827,18,,
71,,6,Sùng A Phong,11A7,Nam,Mông,Thíp Dạo,Lâm Giang,Sùng A Chư,Hạng Thị Chấu,0867058874,0822086471,17,,
72,,7,Đặng Minh Sơn,12A1,Nam,Dao,Nhai Tẻn,Bảo Hà,Đặng Văn Bình,Đặng Thị Hà,359295548,981276177,20,,
73,,8,Hảng Seo Lành,12A1,Nam,Mông,Bùn Dạo,Lâm Giang,Hảng Seo Sảng,Lù Thị Hoa,392366160,867594844,16,,
74,,9,Hoàng Trọng Khôi,12A1,Nam,Tày, 3 AB,Bảo Hà,Hoàng Văn Lực,Triệu Thị In,0974630324,0789076768,16,,
75,,10,Tẩn Hoàng Nghiệp,12A1,Nam,Dao,Nhai Thổ,Kim Sơn,Tẩn A Khế,Hoàng Thị Tâm,0989063570,0988611544,15,,
76,301,1,Triệu Anh Quang,12A1,Nam,Dao,Hồng Cam,Bảo Hà,Triệu Xuân Vượng,Triệu Thị Lai,0398854726,,10,,
77,,2,Vi Duy Hoàng,12A1,Nam,Dao,Nhai Tẻn ,Bảo Hà,Vi Văn Kiên,Đặng Thị Tâm,866721046,866721046,23,,
78,,3,Đặng Văn Hiếu,12A2,Nam,Dao,Bông ,Bảo Hà,Nguyễn Văn Hoán,Đặng Thị Phái,0327512038,0382253891,10,,
79,,4,Hoàng Đình Tập,12A2,Nam,Tày,3 Nhai Thổ ,Bảo Hà,Hoàng Văn Thuận,Bàn Thị Hà,0971110758,0867982915,20,,
80,,5,Hoàng Minh Vũ,12A2,Nam,Tày,Cam cọn,Bảo Hà,Hoàng Văn Vựng,Hoàng Thị Nhiệm,0359367426,0364198642,17,,
81,,6,Lê Bảo Nghĩa,12A4,Nam,Dao,Nhai Tẻn,Bảo Hà,Lê Thái Đình,Đặng Thị Thơm,342136204,383058557,13,,
82,,7,Nông Khánh Duy,12A4,Nam,Dao,Thống nhất,Bảo Hà,Nông Văn Hình,Đặng Thị Giảng,776705861,,10,,
83,,8,Sầm Minh Hữu,12A4,Nam,Tày,Tân Thành,Bảo Hà,Sầm Văn Chiến,Nông Thị Kiểm,367966816,819683614,17,,
84,,9,Trần Tuấn Anh ,12A4,Nam,Kinh,3 Nhai Thổ ,Bảo Hà,Trần Văn Hoàng,Hoàng Thị Toan,989865335,347024175,14,,
85,,10,Triệu Tiến Thắng,12A4,Nam,Dao,Khe Bàn,Bảo Hà,Triệu Văn Lán,Phùng Thị Tam,366851077,328063484,12,,
86,,11,Bàn Duy Khoa,12A5,Nam,Dao,Bông 3,Bảo Hà,Bàn Ton San,Đặng Thị Hương,0973983608,0328323191,10,,
87,205,1,Bàn Thanh Chung,12A5,Nam,Dao,Nhai Tẻn,Bảo Hà,Bàn Tuấn Anh,Tráng Thị Mai,363145091,0329384292,20,,
88,,2,Hà Phúc Lâm,12A5,Nam,Xa phó, 3 Nhai Thổ,Bảo Hà,Hà Xuân Tình,Lý Thị Chắc,0336383054,0376608278,18,Bố mẹ ly hôn,vắng
89,,3,Hoàng Hải Duy,12A5,Nam,Xa phó,2 Nhai Thổ,Bảo Hà,Hoàng Văn Hồng,Nông Thị Thúy,0334181619,0356516499,24,Mồ côi cha,
90,,4,Sầm Minh Đức,12A5,Nam,Tày,Cọn 2,Bảo Hà,Sầm Quốc Đạt(mất),Tòng Thị Pheng,0347953516,,15,,
91,,5,Triệu Qúy Đức,12A5,Nam,Dao,Khe Bàn,Bảo Hà,Hoàng Văn Lai,Triệu Thị Mùi,0354162240,0375967056,16,Bố mẹ ly hôn,
92,,6,Vũ Duy Khánh,12A5,Nam,Kinh,Tân Thành,Bảo Hà,Vũ Văn Toàn,Lê Ngọc Thu,0379414597,0357071304,8,,
93,,7,La Ngọc Tuyến,12A7,Nam,Tày,Cọn 1,Bảo Hà,La Văn Tuyên,Hà Thị Thuỳ,378922358,327883495,15,,
94,,8,Triệu Trung Quý,12A3,Nam,Dao,Bông 3,Bảo Hà,Triệu Trung Kim,,985681214,,,,
95,,9,Hoàng Trần Hiệp,12A3,Nam,Tày,Thôn 3 Nhai Thổ,Bảo hà,Nguyễn Văn Thưởng,Hoàng Thị Thảo,0374684251,0327711651,20,,
PHÂN PHÒNG HỌC SINH ĐĂNG KÝ Ở BÁN TRÚ NĂM HỌC 2026 - 2027 - Khu nữ,,,,,,,,,,,,,,
NỮ,,,,,,,,,,,,,,
TT,Phòng,SL,Họ và tên,Lớp,"Giới
 tính","Dân
 tộc",Thôn ,Xã,Phụ huynh ,,SĐT (Bố/mẹ),SĐT học sinh,Cách trường (KM),Ghi chú
,,,,,,,,,Họ - tên Bố,Họ -  tên Mẹ,,,,
1,401,1,Triệu Thị Hiền,10a1,Nữ,Dao,Tân thành,Bảo Hà,Triệu Văn Hai,Triệu Thị Mấy,983990102,978083718,16,
2,,2,Lý Lan Phương ,10a1,Nữ,Dao,Tân thành ,Bảo Hà,Lý Văn Chúi ,Bàn Thị Náy ,336675404,369080231,15,
3,,3,Lý Thị Thảo ,10a1,Nữ,Dao,Bùn Dạo,Lâm Giang ,Lý Văn Xuân ,Đặng Thị Liên,392107797,339869621,13,
4,,4,Triệu Thị Thuý Hằng ,10a1,Nữ,Dao,Bông 3,Bảo Hà,Triệu Văn Phúc,Triệu Thị Chung,971316587,368814711,10,
5,,5,Phùng Thị Khách ,10a1,Nữ,Dao,Khe bàn ,Bảo Hà,Đặng Văn Xương ,Phùng Thị Liều ,377536147,394515961,10,
6,,6,Triệu Thu Yến,10a1,Nữ,dao,khe bàn,Bảo Hà,Triệu Tòn Chản,Triệu Thị Tám,375109274,395423735,10,
7,,7,Lý Bảo Thanh,10a1,Nữ,Dao,Khe Bàn,Bảo Hà,Lý Văn Tém,Hà Thị Nhàn,963534328,387266574,12,
8,,8,Hà Tố Uyên,10a1,Nữ,Thái,Khe Bàn,Bảo Hà,Hà Văn Nam,Nguyễn Thị Mai,966511169,362800201,10,
9,,9,Hoàng Mỹ Lệ ,10a1,Nữ,Tày,Kim Sơn ,Bảo Hà,Hoàng Văn Phú ,Hà Thị Năm ,326824340,328958260,15,
10,,10,Lương Thị Thu Hoài ,10a1 ,Nữ,Tày,Kim Sơn ,Bảo Hà,Lương Văn Hiếu ,Hoàng Thị Cứ ,394276331,354059236,15,
11,,11,Nguyễn Thị Bích Hợp ,10a1,Nữ ,Tày,Kim Sơn,Bảo Hà,Nguyễn Văn Hoà ,Lý Thị Đới ,962190098,358263884,20Km,
12,402,1,Sùng Thị Yến Chi ,10A2,Nữ ,H'mông ,Khoai ,Bảo Hà ,Sùng Seo Dế ,Sần Thị Gánh ,388587059,,10,
13,,2,Lý Quỳnh Anh,10A2,Nữ ,Dao,Thống Nhất,Bảo Hà ,Lý Văn Sêm,Bàn Thị Vin,343564169,365134102,12,
14,,3,Ma Thị Thiệu Mấn,10A2,Nữ,H'mông,Thùng 2,Bảo Hà,Ma Seo Vinh,Giàng Thị Đỡ,967067434,927106212,7,
15,,4,Lý Thị Tâm Như ,10A2,Nữ ,Tày,6AB,Bảo Hà ,,Nông Thị Châm ,376549216,328939607,14,
16,,5,Lý Thị Mẫn,10A3,Nữ,Tày,Kim Sơn,Bảo Hà,,Lý Thị Môn,0965005785,0386843454,15,
17,,6,Giàng Thị Thu Trang,10A3,Nữ,H' Mông,Tắp 1,Bảo Hà,Giàng Seo Quang,Vù Thị Tâu,0326633006,0387326153,17,
18,,7,Triệu Phương Thảo,10A3,Nữ,Dao,Khe Dai,Bảo Hà,Triệu Nguyên Bình,Đặng Thị Tếch,0868884083,,8,
19,,8,Giàng Thị Thoại,10A3,Nữ,H' Mông,Chùn,Bảo Hà,Giàng Seo Dìn,Chấu Thị Chứ,0967295787,0337400273,10,
20,,9,Đặng Thùy Tâm,10A3,Nữ,Dao,Thùng 2,Bảo Hà,Đặng Văn Nhất,Hoàng Thị Mùi,0968047896,0356996937,9,
21,,10,Phùng Thị Thiên Thu,10A3,Nữ,Dao,Khe Dai,Bảo Hà,Phùng Văn Phúc,Lý Thi Lai,0382940304,0343364542,8,
22,,11,Hoàng Thị Việt Anh,10A3,Nữ,Tày,Khoai 2,Bảo Hà,Hoàng Văn Chiến,Triệu Thị Lắc,0388345114,,12,
23,,12,Trần Thị Khuyên,10A3,Nữ,Dao,Thống Nhất,Bảo Hà,Trần Văn Páo,Bàn Thị Néo,0973800992,0876031730,14,
24,403,1,Triệu Thị Hà Vy,10A3,Nữ,Tày,Khoai 2,Bảo Hà,Triệu Văn Phượng,Nguyễn Thị Mơ,0964049067,0358377993,12,
25,,2,Bàn Thị Thanh Trúc,10A3,Nữ,Dao,Bông 3,Bảo Hà,Bàn Ton Máy,Triệu Thi Sai,0376930020,0345533218,10,
26,,3,Tô Thị Khánh Ngọc,10A3,Nữ,Dao,Tân Thành,Bảo Hà,Tô Văn Oai,Lù Thị Ly,0392872778,0397626423,12,
27,,4,Triệu Thị Ánh,10A4,Nữ,Dao,Cam 2,Bảo Hà,Triệu Văn Ngọ,Đặng Thị Điệp,0968309335,,20,
28,,5,Bàn Thị Hoa,10A4,Nữ,Dao,1 Nhai Tẻn,Bảo Hà,Bàn Tuấn Anh ,Tráng Thị Mai,0971240758,868654376,17,
29,,6,Triệu Thị Huyền,10A4,Nữ,Dao,Tân Thành,Bảo Hà,Triệu Văn Thắng,Triệu Thị Náy,0378346106,387053047,12,
30,,7,Phan Quỳnh Nga,10A4,Nữ,Tày,Kim Sơn ,Bảo Hà,Phan Trung Thành ,Hoàng Thị Hiền ,0378402157,396963631,12,
31,,8,Hoàng Thị Nhi,10A4,Nữ,Tày,3 Nhai Thổ,Bảo Hà,Hoàng Văn Thuận,Bàn Thị Hà,0344245596,0325103423,15,
32,,9,Đặng Thị Nhung,10A4,Nữ,Dao,Tân Thành ,Bảo Hà,Đặng Văn Xan,Đặng Thị Khách ,0961049812,0382814837,12,
33,,10,Hoàng Thu Phương,10A4,Nữ,Dao,Thôn thùng 2,Bảo Hà,Hoàng Thừa Hiển,Phùng Thị Mấy,036 9738258,384060643,6,
34,,11,Triệu Phương Thảo,10A4,Nữ,Dao,Khe Bàn,Bảo Hà,Triệu Hồng Hai,Triệu Thị Thim,0346489164,0365504034,12,
35,,12,Triệu Thị Thu Thuỷ,10A4,Nữ,Tày,Kim Sơn ,Bảo Hà,Đặng Minh Tuấn ,Triệu Thị Tom,0357737660,0327475431,12,
36,404,1,Hoàng Bảo Trân,10A4,Nữ,Tày,3 Nhai Thổ ,Bảo Hà,Hoàng Văn Phòng,Huỳnh Thị Ly,0377059015,0342111506,15,
37,,2,Lò Thị Mai Hương,10A6,Nữ,Dao,Khoai 2,Bảo Hà,Lý Văn Đạt,Lò Thị Mùi,0379953812,,7,
38,,3,Triệu Phương Anh,10A7,Nữ,Dao,Khe Bàn,Bảo Hà,Triệu Phúc Bảo,Triệu Thị Mùi,0375299757,,15,
39,,4,Triệu Phương Nhi,10A7,Nữ,Dao,Khe Bàn,Bảo Hà,Triệu Tòn Cau,Triệu Thị Vân,0373708930,0377173493,15,
40,,5,Triệu Thị Hồng Thắm ,10A7,Nữ,Dao,Thống Nhất,Bảo Hà,Triệu Văn Dũng ,Bàn Thị Yệng,09131186459,,11,
41,,6,Lâm Hoài Thương,10A7,Nữ,Tày,2 Tân Văn,Bảo Hà,Lâm Sỹ Tưởng,Nguyễn Thị Tươi,0357731984,,11,
42,,7,Lê Ngọc Ánh,10A7,Nữ,Dao,Thống Nhất,Bảo Hà,Lê Văn Sơn ,Lý Hồng Kim,0327501693,,10,
43,,8,Triệu Thiên My,10A7,Nữ,Dao,Tân Thành,Bảo Hà,Triệu Văn Nhất,Bàn Thị Mấy,0332457830,,14,
44,,9,Trương Thị Hoa,10A7,Nữ,Dao,Thống Nhất,Bảo Hà,Trương Văn Tó,Đặng Thị Ghi,0932251314,,11,
45,,10,Lý Bảo Linh,10A7,Nữ,Dao,1 Nhai Tẻn,Bảo Hà,Hoàng Ngọc Lâm,Hoàng Thị Chang,0866159110,,20,
46,,11,Đặng Yến Nhi,10A7,Nữ,Dao,1 Nhai Tẻn,Bảo Hà,Đặng Quốc Phong,Trướng Thị Hoa,0865577163,,19,
47,405,1,Nguyễn Khánh Linh,11A1,Nữ,Kinh,Bảo Ân,Bảo Hà,Nguyễn Bá Duy,Nguyễn Thị Ngà,976732702,865241865,15,
48,,2,Ma Thị Hoa ,11A1,Nữ,H'mông,Thùng 2,Bảo Hà,Ma Seo Xá,Giàng Thị Ly,375513312,388897314,7,
49,,3,Hoàng Hải Yến,11A1,Nữ,Tày,Cọn 2,Bảo Hà,Nguyễn Văn Huy. ,Hoàng Thị Hạnh ,354771469,392932010,17,
50,,4,Lục Mai Phương,11A1,Nữ,Tày,1AB,Bảo Hà,Lục Thế Anh,Lý Thị Minh,394617256,352343099,15,
51,,5,Trương Thủy Hoàn,11A1,Nữ,:Dao. ,1 Nhai Tẻn,Bảo Hà,Trương Văn Chấn,Đặng Thị Loan,384566897,372604095,25,
52,,6,Nông Thị Quý ,11A1,Nữ,Dao,Thống Nhất,Bảo Hà,Nông Văn Tôn,Triệu Thị Hoa,347341064,375547964,15,
53,,7,Bàn Thị Hồng Thêm,11A2,Nữ ,Dao,Nhai Tẻn,Bảo Hà,Bàn Văn Tinh ,Đặng Thị Hồng,0865160428,0376705948,21,
54,,8,Hoàng Thị Hồng Nhung,11A2,Nữ ,Tày,Nhai Thổ 3,Bảo Hà,Hoàng Văn Sinh ,Triệu Thị Nhi,0966153442,0337685142,20,
55,,9,Hoàng Thuý Tiên,11A2,Nữ ,Xa Phó ,Nhai Thổ 2,Bảo Hà,Hoàng Văn Tiến,Hoàng Thị Vần,0328428391,0981514010,21,
56,,10,Đặng Khánh Linh,11A2,Nữ ,Dao,Nhai Tẻn ,Bảo Hà,Đặng Văn Hải ,Đặng Thị Thắng,0367920906,0386849760,20,
57,,11,Ma Thị Nga,11A2,Nữ ,Mông,Khoai 1,Bảo Hà,Ma Seo Của ,Sùng Thị Chứ,0336881647,0337271613,13,
58,,12,Ma Thị Hương,11A2,Nữ ,Mông,Chùn,Bảo Hà,Ma Seo Chư,Thào Thị Chứ,0376447773,0362422816,10,
59,406,1,Nguyễn Minh Tâm,11A2,Nữ ,Kinh,Cam Cọn 2,Bảo Hà,Nguyễn Thành Chung,La Thị Chuyền,0399614192,0965430664,16,
60,,2,Sùng Thuý Liên,11A2,Nữ ,Mông,Nhai Tẻn 2,Bảo Hà,Sùng Seo Xủ ,Giàng Thị Cái,0969534104,0867904896,22,
61,,3,Hoàng Ngọc Diệp ,11A2,Nữ ,Tày,Cọn 1,Bảo Hà,Hoàng Văn Nhiễu,Hoàng Thị Nhàn,0865613874,0343961184,16,
62,,4,Hoàng Thị Nhung,11A2,Nữ ,Tày,Khoai 2,Bảo Hà,Hoàng Văn Lệ,Hoàng Thị Sáo,0971560361,0366925813,13,
63,,5,Đặng Thị Hoa,11A3,Nữ,Dao,Bông 1-2,Bảo Hà,Nguyễn Văn Hoán,Đặng Thị Phái,0969052416,0969052416,10,
64,,6,Lê Như Quỳnh,11A3,Nữ,Tày,Cọn 1,Bảo Hà,Lê Xuân Chỉnh,Hoàng Thị Lương,0387879813,0988476042,15,
65,,7,Tráng Thị Đại,11A4,Nữ,Dao,Nhai Tẻn,Bảo Hà,Tráng Văn Trấn,Đặng Thị Dòng,0369808294,,16,
66,,8,Triệu Thị Thu Hiền,11A4,Nữ,Dao,Khe Bàn,Bảo Hà,Triệu Kim Hương,Triệu Thị Mắn,0342024303,,11,
67,,9,Đặng Hồng Hoa,11A4,Nữ,Dao,Tân thành,Bảo Hà,Đặng Văn Nhì,Triệu Thị Chúi,0393130600,,11,
68,,10,Hoàng Thị Hồng Mai,11A4,Nữ,Tày ,Thôn Khoai ,Bảo Hà,Hoàng Văn Lưng,Triệu Thị Thủy,0862175022,,13,vắng
69,,11,Đinh Thị Hồng Thái,11A4,Nữ,Tày ,Thôn 7 AB,Bảo Hà,Đinh Quang Sáng,Lương Thị Thơi,0393679215,,14,
70,,12,Triệu Thanh Thảo,11A4,Nữ,Dao,Khe Bàn,Bảo Hà,Hoàng Văn Lai,Triệu Thị Mùi,0354162240,,16,
71,407,1,Đặng Hồng Thư,11A4,Nữ,Dao,Bỗng,Bảo Hà,Đặng Ton Thanh,Triệu Thị Thủy,0365471167,,9,
72,,2,Đặng Thị Vân,11A4,Nữ,Dao,Hồng Cam ,Bảo Hà,Đặng Văn Thức,Bàn Thị Nhàn,0862908820,,11,
73,,3,Hoàng Tố Vân,11A4,Nữ,Tày,Thôn 3 AB,Bảo Hà,Hoàng Văn Tú,Lương Thị Bình,0396141165,,12,
74,,4,Lý Hồng Mỹ,11A4,Nữ,Dao,Nhai tẻn,Bảo Hà,Lý Văn Đanh,Lý Thị Phương,0375302378,,12,
75,,5,Triệu Thùy Linh,11A5,NỮ,dao,Khe Bàn ,Bảo Hà,Triệu Văn Nhất,Triệu Thị Thiên Lý,329966224,376596804,15,
76,,6,Lê Thị Hoài,11A6,Nữ,Kinh ,Cam Cọn,Bảo Hà,Lê Xuân Huấn,Phạm Thị Hồng,363710228,798746877,11,
77,,7,Lý Thị Yến,11A6,Nữ,Dao,Khe Bàn,Bảo Hà,Lý Tòn Cau,Triệu Thị Chầy,0975991760,0338364398,15,
78,,8,Trần Thị Thu,11A7,Nữ,Kinh,Khoai,Xã Bảo Hà,Trần Văn Luận,Kim Thị Nhàn,0328995435,0364201038,9,
79,,9,Tráng Thị Dung,11A7,Nữ,H'Mông,Nhai Tẻn,Xã Bảo Hà,Tráng A Hồ,Cư Thị Do,0328219084,0373502744,22,
80,,10,Đặng Thị Anh Đào,11A7,Nữ,Dao,Bông ,Xã Bảo Hà,Đặng Văn Hoàng,Triệu Thị Phấy,0372158238,0389864250,11,
81,,11,Hoàng Thị Thúy Kiều,11A7,Nữ,Tày,3AB,Xã Bảo Hà,Hoàng Văn Phức,Hoàng Thị Nhu,0336455820,0354751347,16,
82,,12,Hoàng Bảo Ngọc,11A7,Nữ,Tày,3 Nhai Thổ,Xã Bảo Hà,Lý Tiến Hương,Hoàng Thị Hường,0987898550,0342128230,20,
83,408,1,Hoàng Thị Phương,11A7,Nữ,Tày,Cam 2,Xã Bảo Hà,Hoàng Văn Toản,Đinh Thị Liên,0383945477,0862516497,15,
84,,2,Bàn Thanh Thuý,11A7,Nữ,Dao,Thống Nhất,Xã Bảo Hà,Bàn Văn Mài,Đặng Thị Thu,0344615907,0342986680,11,
85,,3,Đặng Thị Thanh Vân,12A1,Nữ,Dao,Nhai Tẻn ,Bảo Hà,Đặng Văn Ngọc,Vi Thị Lan,374737518,0342363155,20,
86,,4,Nông Thị Ánh Nguyệt,12A1,Nữ,Dao,Bông ,Bảo Hà,Nông Ton Phan,Sầm Thị Nghè,334264373,862165844,10,
87,,5,Phan Thị Yến nhi,12A1,Nữ,Dao,Bông ,Bảo Hà,Đặng Văn Ton,Phan Thị Tam,325422275,,10,
88,,6,Lý Thanh Hoa,12A1,Nữ,Dao,Thống Nhất,Bảo Hà,Lý văn phong,Nguyễn thị chích,971561057,971365265,9,
89,,7,Đặng Thị Lan Anh,12A1,Nữ,Dao,Bản Cam 1,Cam Cọn,Đặng Văn Thôm,Triệu Thị Êm,0342986321,0363227019,10,
90,,8,Hoàng Thị Thu,12A2,Nữ,Tày,Kim Sơn,Bảo Hà,Hoàng Văn Ích,Hà Thị Tuyên,0368432272,0328516810,11,
91,,9,Lý Thị Nga,12A2,Nữ,Dao,Nhai Tẻn ,Bảo Hà,Lý Văn Thành,Bàn Thị Tánh,0389175004,0345955260,15,
92,,10,Bàn Thúy Kim,12A2,Nữ,Dao,Cam 1,Bảo Hà,Bàn Văn Khi,Đặng Thị Giêng,0344610271,0395251073,17,
93,,11,Triệu Thị Thanh Huyên,12A2,Nữ,Tày,Khoai ,Bảo Hà,Triệu Văn Hoàng,Hoàng Thị Hòa,0348846980,0976871507,13,
94,,12,Hoàng Thị Thanh Mai,12A2,Nữ,Tày,3 Nhai Thổ ,Bảo Hà,Hoàng Văn Huân,Chu Thị Hà,0981260564,0867569315,15,
95,207,1,Đặng Thị Kiều Trang,12A2,Nữ,Dao,Thống Nhất,Bảo Hà,Đặng Văn Huế,Triệu Thị Yêu,0914447463,0906138963,15,
96,,2,Bàn Thị Kim Phượng,12A2,Nữ,Dao,Nhai Tẻn ,Bảo Hà,Bàn Sơn Hà,Bàn Thị Hồng,0363914593,0348876307,14,
97,,3,Nguyễn Thùy Trâm,12A2,Nữ,Tày,Kim Sơn,Bảo Hà,Nguyễn Văn Thuấn,Sầm Thị Trang,0376988106,0379378649,12,vắng
98,,4,Lí Thị Lan Anh,12A3,Nữ,Dao,Bỗng 2,Bảo Hà,Lí Văn Chúi,Bàn Thị Náy,",0336675404",0364386771,15,
99,,5,Triệu Thanh Thư,12A3,Nữ,Dao,Bông 1-2,Bảo Hà,Triệu Văn Tư,Bàn Thị Thanh,0865530827,",0971068785",9,
100,,6,Chu Thị Hải Yến ,12A3,Nữ,Tày,3AB,Bảo Hà,Chu Văn Chang,Lương Thị Dần,0366 383 983 ,036 248 1095,15,
101,,7,Đặng Thị Xuyên,12A3,Nữ,Dao,Lỵ 1-2,Bảo Hà,Đặng Văn Nhật,Trần Thị Pu, 0915039526,0376813920,10,
102,,8,Hà Thị Nguyên,12A3,Nữ,Phù Lá,Kim Sơn,Bảo Hà,Hà Văn Hành,Hoàng Thị Nhất,0866621716,0353810009,17,
103,,9,Chu Bích Loan,12A4,Nữ,Tày,Kim Sơn,Bao Hà,Chu Văn Đài,Mạc Thị Tài,346318191,335470790,12,
104,,10,Hoàng Thị Nhài,12A4,Nữ,Tày,Khoai ,Bao Hà,Hoàng Văn Đức,Triệu Thị Phương,964141142,353940311,10,
105,208,1,Hoàng Thị Phương Oanh,12A4,Nữ,Tày,7AB,Bảo Hà,Hoàng Văn Tường,Hoàng Thị Lợi,364668915,383207751,17,
106,,2,Triệu Thị Sinh,12A4,Nữ,Dao,Khe Bàn,Bao Hà,Triệu Văn Thất,Hà Thị Săm,989559091,333446323,12,
107,,3,Hoàng Thị Mừng,12A4,Nữ,Tày,Kim Sơn,Bao Hà,Hoàng Văn Màu,Hoàng Thị Mơ,399240014,,12,
108,,4,Đặng Thị Nhung ,12A6,Nữ,Dao,Thống Nhất,Bảo Hà,Đặng Văn Minh,Lý Thị Tiên,896016371,773033260,15,
109,,5,Sầm Khánh Ly,12A7,Nữ,Tày,Cọn 1,Bảo Hà,Sầm Văn Chương,La Thị Thảo,356269517,702096831,20,
110,,6,La Thị Thanh Huyên,12A7,Nữ,Giáy,Làng Đam,Lâm Giang,La Xuân Trường,Nông Thị Tâm,326578351,396971718,9,
111,,7,Đặng Thị Yến Nhi,12A7,Nữ,Dao,Tân Thành,Bảo Hà,Đặng Văn Xan,Đặng Thị Khách,332631529,373840285,17,
112,,8,Lương Thị Lý,12A7,Nữ,Tày,Bỗng Buôn,Bảo Hà,Lương Xuân Liêm,Vũ Thị Mơn,355060921,329462258,12,"""

lines = raw_data.strip().splitlines()

students = []
current_gender = "Nam"
current_day = "Dãy Nam"
current_room = ""

def clean_phone(phone_str):
    if not phone_str:
        return ""
    p = str(phone_str).strip().replace("*", "").replace(" ", "").replace('"', '').replace(",", "")
    if p and not p.startswith("0") and len(p) in [9, 10]:
        p = "0" + p
    return p

for line in lines:
    line_clean = line.strip()
    if not line_clean:
        continue
    if "BÁN TRÚ NAM" in line_clean or line_clean.startswith("NAM,"):
        current_gender = "Nam"
        current_day = "Dãy Nam"
        continue
    if "Khu nữ" in line_clean or line_clean.startswith("NỮ,"):
        current_gender = "Nữ"
        current_day = "Dãy Nữ"
        continue
    if line_clean.startswith("TT,") or "Họ và tên" in line_clean or "Họ - tên Bố" in line_clean:
        continue
        
    reader = csv.reader([line_clean])
    parts = next(reader)
    if len(parts) < 5:
        continue
    
    tt = parts[0].strip()
    if not tt.isdigit():
        continue
        
    phong = parts[1].strip()
    if phong:
        current_room = f"NAM-{phong}" if current_gender == "Nam" else f"NU-{phong}"
        
    sl = parts[2].strip()
    giuong = f"G-{int(sl):02d}" if sl.isdigit() else f"G-{len(students)+1:02d}"
    
    ho_ten = parts[3].strip()
    lop = parts[4].strip().upper()
    
    # Xác định khối
    khoi = "Khối 10"
    if lop.startswith("11"):
        khoi = "Khối 11"
    elif lop.startswith("12"):
        khoi = "Khối 12"
        
    dan_toc = parts[6].strip() if len(parts) > 6 else ""
    thon = parts[7].strip() if len(parts) > 7 else ""
    xa = parts[8].strip() if len(parts) > 8 else ""
    bo = parts[9].strip() if len(parts) > 9 else ""
    me = parts[10].strip() if len(parts) > 10 else ""
    sdt_ph = clean_phone(parts[11]) if len(parts) > 11 else ""
    sdt_hs = clean_phone(parts[12]) if len(parts) > 12 else ""
    khoang_cach = parts[13].strip() if len(parts) > 13 else ""
    ghi_chu = parts[14].strip() if len(parts) > 14 else ""
    
    is_vang = "vắng" in ghi_chu.lower()
    
    ma_hs = f"HS{current_gender[0]}-{len(students)+1:03d}"
    
    students.append({
        "Mã HS": ma_hs,
        "Họ và tên": ho_ten,
        "Giới tính": current_gender,
        "Khối": khoi,
        "Lớp": lop,
        "Dãy nhà": current_day,
        "Phòng": current_room,
        "Giường": giuong,
        "Dân tộc": dan_toc,
        "Thôn": thon,
        "Xã": xa,
        "Phụ huynh (Bố/Mẹ)": f"{bo} / {me}".strip(" /"),
        "SĐT Phụ huynh": sdt_ph,
        "SĐT Học sinh": sdt_hs,
        "Cách trường (KM)": khoang_cach,
        "Chính sách NĐ116": "Có",
        "GĐ1: Ăn trưa": not is_vang,
        "GĐ2: Phòng nghỉ": not is_vang,
        "Trạng thái": "Xin về nhà" if is_vang else "Tại trường",
        "Ghi chú nề nếp": ghi_chu
    })

# Ghi ra 2 file CSV
keys = list(students[0].keys())

with open("D:\\danh_sach_hoc_sinh_thuc_te.csv", "w", newline="", encoding="utf-8-sig") as f:
    writer = csv.DictWriter(f, fieldnames=keys)
    writer.writeheader()
    writer.writerows(students)

with open("d:\\OneDrive\\Hô sơ cá nhan\\Học AI\\danh_sach_hoc_sinh_thuc_te.csv", "w", newline="", encoding="utf-8-sig") as f:
    writer = csv.DictWriter(f, fieldnames=keys)
    writer.writeheader()
    writer.writerows(students)

print(f"Tong so hoc sinh da nap thanh cong: {len(students)}")

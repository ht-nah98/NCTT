# PHƯƠNG PHÁP — cách hệ thống này nghĩ

> Thư mục này giải thích **cách nghĩ**, không chỉ cách chạy. Đọc xong bạn có
> thể tự nâng cấp, tự xây lại, hoặc bác bỏ cách làm hiện tại.
>
> Phiên bản: v1.0 · Lập 2026-08-28 · Ngách tham chiếu: `christian-blues`

---

## Bắt đầu từ đâu

| Bạn muốn | Đọc |
|---|---|
| Hiểu tổng thể trong 10 phút | `00_DOC_TRUOC_TIEN.md` |
| Biết dữ liệu đi qua những gì | `01_DUONG_DI_CUA_DU_LIEU.md` |
| Xem từng bước phân tích + code thật | `02_CACH_PHAN_TICH_TUNG_BUOC.md` |
| Hiểu cách ra kết luận, chống tự lừa | `03_CACH_RA_KET_LUAN.md` |
| Biết hệ thống yếu chỗ nào | `04_GIOI_HAN_VA_CACH_KHAC_PHUC.md` |
| Tự xây / nâng cấp | `05_TU_XAY_LAI.md` |
| Hiểu AI được phép làm gì | `06_PROMPT_VA_VAI_TRO_AI.md` |

---

## Ba điều bất ngờ nhất

**① Hệ thống không dùng AI để phân tích.** 15.542 dòng code, **0 lời gọi mô
hình ngôn ngữ**. Toàn bộ là regex + pandas + scipy. AI viết ra *công cụ đo*,
chứ không phải AI đi *đo*. Lý do và đánh đổi: `00_DOC_TRUOC_TIEN.md §1–2`.

**② Kết quả "0/26 đặc trưng thumbnail đứng vững" là thành công, không phải thất
bại.** Nó nghĩa là *"không có mẹo thumbnail nào cứu được nội dung yếu"* — biết
một biến vô dụng giúp dồn sức vào chỗ có ích. Chi tiết:
`02_CACH_PHAN_TICH_TUNG_BUOC.md §STEP_04`.

**③ Số lượng không phải sức mạnh.** Chủ đề `healing` xuất hiện 757 lần, gấp 13
lần `finally` (58 lần). Nhưng `healing` có like trung vị 3 (dưới nền 4), còn
`finally` được 26,5 like. Người ta *nói nhiều* về chữa lành nhưng *không ai đồng
tình đặc biệt*. Chi tiết: `§STEP_05`.

---

## Bốn nguyên tắc xuyên suốt

```
① BỐN TẦNG KHÔNG TRỘN     FACT → METRIC → SCORE → INSIGHT
                          tầng sau không được sửa tầng trước

② LUÔN CÓ NHÓM ĐỐI CHỨNG   không có rổ B4 thì mọi công thức là mê tín

③ KIỂM BA LỚP              trong mẫu → toàn thị trường → trong từng kênh
                          bẫy Simpson đảo 8,1× thành 0,48×

④ QUY TẮC PHẢI CÓ THỨ      tài liệu không tự thành sự thật:
   THỰC THI VÀ THỨ KIỂM    phải có code gắn và code kiểm
```

---

## Liên kết

| Cần gì | Đọc |
|---|---|
| Kiến trúc kỹ thuật + sơ đồ | `../00_system/01_ARCHITECTURE.md` |
| Sáu nhóm nguồn Y·P·S·V·K·N | `../00_system/10_SOURCE_CLASSES.md` |
| Bốn tài liệu đầu ra T1.1–T1.4 | `../00_system/11_OUTPUT_CONTRACT.md` |
| **90 bài học đã rút** | `../04_reference/lessons_learned.md` |

---

## Kiểm chứng mọi khẳng định trong thư mục này

Mọi con số đều chạy lại được:

```bash
bash pipeline/run_all.sh                        # 66 giây, dựng lại tất cả
python3 pipeline/scoring/verify_rubric.py       # code có khớp điểm không
python3 pipeline/scoring/verify_system_docs.py  # tài liệu có khớp code không
```

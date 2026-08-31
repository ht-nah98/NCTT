# HỢP ĐỒNG CDKH — Giao kèo dữ liệu giữa R&D và IT

> **Trạng thái: BẢN THẢO — CHƯA ÁP DỤNG.**
> Quy trình hiện hành vẫn là luồng cũ (CDKH là *đầu ra*, suy từ comment ở STEP_05).
> Tài liệu này chuẩn bị cho luồng mới, khi R&D bàn giao CDKH làm *đầu vào*.
> Cần R&D duyệt trước khi viết code.
>
> Phiên bản: v1.0 · Cập nhật 2026-08-19 · giao kèo CDKH với R&D

---

## 1. VÌ SAO CẦN TÀI LIỆU NÀY

Luồng mới đảo chiều một giả định gốc:

| | Luồng cũ (đang chạy) | Luồng mới (sắp tới) |
|---|---|---|
| Danh sách kênh | đầu vào | đầu vào |
| **CDKH** | **đầu ra** — suy từ comment | **đầu vào** — R&D bàn giao |
| Công thức thắng | 1 công thức / ngách | **N công thức / N phân khúc** |

Ẩn dụ đã thống nhất: **R&D lập hồ sơ bệnh án · IT bắt bệnh trên hồ sơ đó.**
Cùng là "Nam đau đầu" nhưng nguyên nhân khác nhau → **mỗi hồ sơ một chẩn đoán riêng**.

Nếu không chốt định dạng trước, ngày nhận file đầu tiên sẽ là ngày ngồi
đoán xem R&D đã đặt tên trường thế nào. Chốt trước thì hôm đó chỉ việc chạy.

---

## 2. NGUYÊN TẮC: CHỈ NHẬN THỨ ĐO ĐƯỢC

Đây là điều khoản quan trọng nhất, và là điều dễ gây hiểu lầm nhất.

Hệ thống **không** nhận CDKH dạng văn xuôi mô tả. Lý do không phải hình thức —
mà vì mỗi trường trong hồ sơ phải **đối chiếu được với một tín hiệu đo được
trên dữ liệu thật**. Trường nào không ánh xạ được thì hệ thống không xác nhận
cũng không bác bỏ được nó; nó chỉ nằm đó như một lời khẳng định.

> **Hệ quả cần R&D biết trước:** hệ thống có quyền **BÁC BỎ** một phân khúc do
> R&D đề xuất, nếu dữ liệu không đỡ. Đó là chức năng, không phải lỗi.
> Một hệ thống chỉ biết gật đầu với hồ sơ R&D thì không có giá trị kiểm chứng.

---

## 3. ĐỊNH DẠNG FILE

**Đường dẫn:** `<N>/00_input/raw/cdkh.yaml`
**Định dạng:** YAML (dễ đọc bằng mắt, dễ sửa tay, giữ được tiếng Việt có dấu)

Đặt trong `00_input/raw/` nên chịu **quy tắc R1: không được sửa sau khi nhận**.
Muốn đổi → R&D phát hành bản mới, tăng `version`.

```yaml
schema: cdkh/v1
niche: christian-blues          # phải khớp tên thư mục ngách
version: 1                      # tăng mỗi lần R&D phát hành lại
issued_by: "Team R&D"
issued_at: 2026-08-19           # ngày bàn giao

segments:
  - id: seg_healing             # bắt buộc, snake_case, duy nhất
    name: "Người đang chịu đựng"
    hypothesis: >
      Phụ nữ 45–65 đang trải qua mất mát hoặc bệnh tật, nghe nhạc để
      tìm sự an ủi trong lúc cầu nguyện buổi sáng.

    # ── PHẦN ĐO ĐƯỢC — hệ thống sẽ kiểm định từng dòng ──
    signals:
      pain:    [healing, struggling]      # từ vựng §4.2
      context: [prayer_devo, morning]     # từ vựng §4.3
      attributes: []                      # từ vựng §4.1
    demographics:
      age_range: [45, 65]                 # để trống nếu không giả định
      gender: null                        # "F" | "M" | null
    expected_share_pct: 30                # ước lượng % của R&D (tùy chọn)

    # ── PHẦN KHÔNG ĐO ĐƯỢC — ghi nhận, không kiểm định ──
    notes: "Nguồn: phỏng vấn 5 người nghe + báo cáo Luminate 2025"
```

---

## 4. TỪ VỰNG ĐƯỢC PHÉP DÙNG

Đây là **toàn bộ** tín hiệu hệ thống hiện đo được, trích trực tiếp từ
`pipeline/analyze/step05_audience.py`. R&D chỉ được dùng các mã trong bảng này.

> Cần một tín hiệu chưa có? → ghi vào `notes`, kèm ví dụ câu comment thật.
> IT sẽ bổ sung mẫu nhận dạng và phát hành `cdkh/v2`. **Không tự đặt mã mới** —
> mã lạ sẽ bị cổng kiểm từ chối chứ không âm thầm bỏ qua.

### 4.1 `attributes` — thuộc tính tự khai

| Mã | Nghĩa |
|---|---|
| `retired` | đã nghỉ hưu |
| `musician` | nhạc công, người chơi nhạc |
| `trucker` | tài xế đường dài |
| `veteran` | cựu quân nhân |
| `disabled` | người khuyết tật |
| `nurse_care` | điều dưỡng, người chăm sóc |
| `widow` | góa bụa |
| `recovery` | đang cai nghiện / phục hồi |
| `new_convert` | mới tin đạo |
| `longtime_faith` | có đức tin lâu năm |

### 4.2 `pain` — nỗi đau / nhu cầu

| Mã | Nghĩa |
|---|---|
| `finally` | "cuối cùng cũng tìm được" — đã tìm kiếm từ lâu |
| `cant_stand` | chán ghét cái đang có |
| `never_heard` | chưa từng nghe thấy thứ như vậy |
| `struggling` | đang trải qua giai đoạn khó khăn |
| `better_than` | so sánh hơn hẳn lựa chọn khác |
| `healing` | chữa lành, an ủi, rơi nước mắt |

### 4.3 `context` — bối cảnh nghe

| Mã | Nghĩa |
|---|---|
| `driving` | khi lái xe |
| `housework` | khi làm việc nhà |
| `work` | khi làm việc |
| `sleep_night` | khi ngủ / ban đêm / mất ngủ |
| `prayer_devo` | khi cầu nguyện, tĩnh nguyện |
| `morning` | buổi sáng, bắt đầu ngày |
| `sick_hosp` | khi ốm đau, nằm viện |
| `grief` | khi tang chế |

### 4.4 `discovery` — cách tìm thấy *(chỉ dùng khi cần)*

`algorithm` · `searched` · `shared` · `subscribed` · `repeat`

---

## 5. RÀNG BUỘC ĐẠO ĐỨC — BẮT BUỘC

Kế thừa **quy tắc R6** của hệ thống, không có ngoại lệ:

| # | Ràng buộc |
|---|---|
| E1 | `demographics` chỉ ghi nhận khi người nghe **tự khai công khai**. Không suy đoán tuổi, sắc tộc, tôn giáo từ tên người. |
| E2 | Không có trường nào cho sắc tộc. Không thêm. |
| E3 | `age_range` là **giả thuyết của R&D để kiểm định**, không phải sự thật. Hệ thống đối chiếu với tuổi tự khai (n nhỏ — xem §6). |
| E4 | Không nhận CDKH mô tả **cá nhân cụ thể**. Chỉ nhận mô tả **nhóm**. |

---

## 6. HỆ THỐNG TRẢ LỜI GÌ

Với mỗi phân khúc, cổng kiểm sinh `<N>/05_audience/00_cdkh_validation.md`:

| Kết luận | Điều kiện | Nghĩa |
|---|---|---|
| ✅ **XÁC NHẬN** | `p < 0.001` và like trung vị ≥ 2× nền | Dữ liệu đỡ giả thuyết R&D |
| ⚠️ **YẾU** | `p < 0.05` | Có dấu hiệu, chưa đủ chắc |
| 🛑 **BÁC BỎ** | không đạt | Dữ liệu **không** đỡ |
| ❔ **KHÔNG ĐỦ MẪU** | `n < 30` | Không kết luận được — *không phải là bác bỏ* |

Cơ chế kiểm định (Mann–Whitney U) **đã chạy sẵn** trong hệ thống hiện tại,
xem `<N>/05_audience/04_signal_tests.csv`. Luồng mới chỉ đổi nguồn giả thuyết:
thay vì hệ thống tự đặt, nó lấy từ hồ sơ R&D.

> **Cảnh báo cần nói trước với R&D:** chia ngách thành N phân khúc thì mỗi
> phân khúc chỉ còn ~1/N dữ liệu. Với ~6.400 comment, chia 4 nhóm là chấp nhận
> được; chia 10 nhóm thì phần lớn sẽ rơi vào **KHÔNG ĐỦ MẪU**.
> **Khuyến nghị: 3–5 phân khúc.**

Riêng `age_range` hiện chỉ đối chiếu được với **n=82** người tự khai tuổi
trên 6.413 comment (1,3%). Đây là mẫu nhỏ — hệ thống sẽ báo độ tin cậy thấp
cho mọi kết luận về tuổi, dù giả thuyết đúng hay sai.

### 6.1 Số liệu thật hôm nay — R&D cần xem trước khi đặt giả thuyết

Bốn nhóm hệ thống tự nhận ra trên ngách christian-blues (6.413 comment):

| Nhóm | n | % | Đủ mẫu? |
|---|---|---|---|
| `p_healing` — đang chịu đựng | 967 | 15,1% | ✅ dư sức |
| `p_elder` — cao tuổi | 70 | 1,1% | ⚠️ sát ngưỡng |
| `p_convert` — mới tin đạo | 33 | 0,5% | ⚠️ sát ngưỡng |
| `p_music` — nhạc công | 4 | 0,1% | 🛑 **không thể kết luận** |

**Ý nghĩa cho R&D:** phân bố này **rất lệch**. Một nhóm chiếm 15%, ba nhóm còn
lại cộng lại chưa tới 2%. Nếu hồ sơ CDKH đề xuất 4 phân khúc cân bằng nhau,
thực tế đo được sẽ **không đỡ nổi ba trong bốn**.

Đây không phải lỗi dữ liệu — nó phản ánh việc **người ta chỉ bình luận khi có
lý do cảm xúc mạnh**. Người nghe nhạc lúc lái xe hiếm khi dừng lại để viết gì.

Khuyến nghị thực tế: đặt **1–2 phân khúc chính** có đủ mẫu để kết luận chắc,
cộng thêm vài phân khúc phụ chấp nhận trước là chỉ mang tính **thăm dò**.

---

## 7. VIỆC PHẢI LÀM KHI ÁP DỤNG

Chưa làm — liệt kê để không quên khi có lệnh:

| # | Việc | Chạm vào |
|---|---|---|
| 1 | Cổng kiểm CDKH: đọc `cdkh.yaml`, chặn mã lạ, chặn sai schema | script mới |
| 2 | Kiểm định từng phân khúc → `00_cdkh_validation.md` | mở rộng `step05_audience.py` |
| 3 | Gắn video/kênh vào phân khúc chiếm ưu thế | mở rộng `step05_audience.py` |
| 4 | **Playbook theo phân khúc** — `segments[]` thay vì 1 công thức | `step10_playbook.py` |
| 5 | Cập nhật hợp đồng file (`05_FILE_CONTRACTS.md`) | tài liệu |
| 6 | Cập nhật kiến trúc (`01_ARCHITECTURE.md` §2 workflow) | tài liệu |

Việc 4 là việc nặng nhất và đáng giá nhất: nó biến "một toa thuốc cho cả
phòng khám" thành đúng thứ ẩn dụ hồ sơ bệnh án đòi hỏi.

---

## 8. CẦN R&D XÁC NHẬN

1. **Định dạng YAML** ổn không? (thay thế: CSV phẳng, hoặc Excel theo mẫu cố định)
2. **Từ vựng §4** có đủ diễn tả các phân khúc R&D định đề xuất không?
3. **Số phân khúc** dự kiến bao nhiêu? (khuyến nghị 3–5)
4. R&D có chấp nhận việc hệ thống **BÁC BỎ** một phân khúc do mình đề xuất không?
5. Danh sách kênh bàn giao kèm theo có **gắn sẵn phân khúc cho từng kênh** không,
   hay chỉ là danh sách phẳng và IT tự gắn?

Câu 5 quan trọng: ô `AA4` trong file flow ghi *"RnD gửi IT danh sách kênh **đã
được xếp theo phân khúc khách hàng**"* — nếu đúng vậy thì việc 3 ở §7 không cần
làm, IT chỉ việc dùng nhãn có sẵn. Cần chốt để khỏi làm thừa.

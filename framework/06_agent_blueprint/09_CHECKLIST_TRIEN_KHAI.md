# CHECKLIST TRIỂN KHAI — bám theo từng ngày

> In ra, đánh dấu từng dòng. Mỗi giai đoạn có **phép thử quyết định** — không
> qua thì đừng sang giai đoạn sau.

---

## GIAI ĐOẠN 1 · M1 DATA CONTRACT (3–5 ngày)

```
□ Định nghĩa schema 4 bảng: channels, videos, video_stats, comments
□ Viết loader: xlsx/csv -> parquet
□ Viết enrich(): age_days, vpd, is_matured, outlier_ratio
□ Viết strip_pii(): xoá author_name và mọi cột định danh
□ Viết validate(): 7 kiểm, trong đó 2 cổng chặn cứng
□ Viết meta.json có trường caveats
□ Nạp thành công ngách thứ nhất
```

**PHÉP THỬ QUYẾT ĐỊNH**
```
Tạo thư mục ngách TRỐNG HOÀN TOÀN, đặt dữ liệu mới vào, chạy load().
✅ Chạy được, không sửa code  -> M1 xong
❌ Phải sửa code mới chạy     -> chưa xong, sửa tiếp
```

> Bài học T22–T25: *"chạy lại được"* chỉ chứng minh file cũ còn đó. Phép thử
> trên ngách trống từng lộ ra **4 lỗi ẩn trong một lần chạy**.

---

## GIAI ĐOẠN 2 · M2 TOOL LAYER (2–3 tuần)

```
Nhóm A · khảo sát
□ describe_niche()          — có trả caveats
□ market_size()
□ demand_supply_gap()       — có cảnh báo maturation
□ channel_concentration()
□ newcomer_success()        — có cảnh báo survivorship

Nhóm B · lọc mẫu
□ select_videos()           — 4 rổ + 5 kiểm chứng phủ mẫu
□ select_comments()         — 3 tầng
□ sample_check()

Nhóm C · kiểm định  ← QUAN TRỌNG NHẤT
□ test_title_theme()        — có kiểm Simpson
□ test_comment_signal()     — đo bằng like, không bằng tần suất
□ test_binary_feature()     — so B1 vs B4
□ test_correlation()        — có cảnh báo artefact mẫu số
□ compare_groups()

Nhóm D · đo lường
□ vocab_gap()
□ listening_context()
□ production_norms()
□ audio_spec()

Nhóm E · xuất
□ make_chart()
□ render_document()
□ cite()

Chung
□ registry.py: register / get_schemas / call
□ Mọi tool trả "n" và "source_class"
□ Không tool nào trả None im lặng
□ Mỗi tool ≥3 test
```

**PHÉP THỬ QUYẾT ĐỊNH**
```
Dựng dữ liệu giả có BẪY SIMPSON cài sẵn:
  chủ đề X thắng đậm ở 2 kênh lớn, thua ở 11 kênh nhỏ

Gọi test_title_theme(fake, "X")
✅ Trả "BÁC BỎ (Simpson)"  -> tool layer đủ tin cậy
❌ Trả "XÁC NHẬN"          -> tool sẽ dạy agent kết luận sai
```

---

## GIAI ĐOẠN 3 · M6 VERIFICATION (3–5 ngày)

> **Làm TRƯỚC agent.** Không có lưới thì không biết agent đang bịa.

```
□ verify_numbers()        — mọi số truy được về tool
□ verify_claim_strength() — không nâng cấp phán quyết
□ verify_warnings()       — cảnh báo bắt buộc phải xuất hiện
□ verify_sample_size()    — cỡ mẫu đi kèm
□ verify_min_sample()     — n<30 không kết luận
□ verify_no_pii()         — không rò rỉ định danh
□ Bộ test đỏ 5 ca
```

**PHÉP THỬ QUYẾT ĐỊNH**
```
Chạy test_red_team()
✅ Bắt được cả 5 ca  -> có lưới, thả agent được
❌ Sót 1 ca          -> agent sẽ bịa ở đúng chỗ đó

Và: chạy verify() trên một báo cáo ĐÚNG đã có
✅ Không báo lỗi     -> không dương tính giả
❌ Báo lỗi           -> quá chặt, agent sẽ kẹt vòng viết lại
```

---

## GIAI ĐOẠN 4 · M3 + M4 (A1, A2) (1–2 tuần)

```
M3 Context
□ DOMAIN_KNOWLEDGE nhúng đủ 5 bẫy L1–L5
□ build_niche_context(): caveats nạp NGAY lượt đầu
□ compact_tool_history(): nén sau 3 kết quả
□ Ngân sách token có cưỡng chế
□ Trace ghi mọi lượt

M4 Agent A1 + A2
□ System prompt A1 (Scout)
□ System prompt A2 (Analyst)
□ Schema output cho cả hai
□ run_agent() có retry khi sai schema
```

**PHÉP THỬ QUYẾT ĐỊNH**
```
① Cho A1 dữ liệu ngách chìm giả lập (M2.4 = 0,3)
   ✅ Trả NO_GO
   ❌ Trả GO -> prompt chưa đủ chặt

② Cho A2 chạy trên ngách thật
   ✅ Sinh ≥10 giả thuyết, có cả loại "phổ biến" và "hiếm"
   ✅ Giữ nguyên tool_result, không sửa số
   ❌ Chỉ báo cáo phát hiện đẹp -> thiếu ràng buộc not_tested
```

---

## GIAI ĐOẠN 5 · M4 (A3, A4, A5) + M7 (1–2 tuần)

```
□ System prompt A3 (Skeptic) — 6 câu hỏi kiểm
□ System prompt A4 (Synthesizer) — quy tắc N5
□ System prompt A5 (Writer) — phân loại T1.1–T1.4
□ M7: renderer, make_chart, render_document
□ verify_pdf() sau mỗi lần dựng
```

**PHÉP THỬ QUYẾT ĐỊNH**
```
① Đưa cho A3 một phát hiện có BẪY SIMPSON cài sẵn
   (lift thô 8,1× nhưng 6/13 kênh ngược chiều)
   ✅ A3 giết nó
   ❌ A3 để sống -> bạn sẽ có hệ thống tự tin nói sai

② Đo tỷ lệ A3 giết phát hiện
   30–50%  -> lành mạnh
   <10%    -> Skeptic quá nhẹ
   >80%    -> Analyst quá ẩu

③ Render PDF ra ảnh, NHÌN từng trang
   ✅ Không trang trắng, không chữ đè, không ô vuông
```

---

## GIAI ĐOẠN 6 · M5 ORCHESTRATOR (1 tuần)

```
□ Cổng 1 sau A1
□ Cổng 2 sau A3
□ Vòng lặp A2↔A3, tối đa 3 vòng, có exclude_ids
□ Checkpoint từng stage
□ Ngân sách token cưỡng chế
□ Xử lý 5 loại lỗi ở M5 §4
```

**PHÉP THỬ QUYẾT ĐỊNH**
```
① Chạy end-to-end 1 ngách -> ra 4 tài liệu
② Xoá checkpoint A5, chạy lại -> chỉ tốn token cho A5
③ Cho ngách chìm -> dừng ở cổng 1, tốn ~15k token
④ Cho dữ liệu yếu -> dừng ở cổng 2, báo "không đủ bằng chứng"
```

---

## NGHIỆM THU TOÀN HỆ THỐNG

Chạy trên **ngách đã có kết quả thủ công** (christian-blues) và so:

```
□ A1 verdict khớp với M2.4 tính tay (1,30 -> GO)
□ A2 tìm ra được chủ đề "thanks" (XÁC NHẬN, lift trong-kênh 2,28×)
□ A2 tìm ra được vocab gap "amen" (2.233 vs 5 lần)
□ A3 giết được chủ đề "scripture" (Simpson: 7/13 kênh tệ đi)
□ A3 giết được chủ đề "healing" (lift 0,74×)
□ A4 không cho hướng nào 5/5 nếu bằng chứng nội bộ là BÁC BỎ
□ A5 không viết số nào ngoài tool output
□ 4 tài liệu dựng ra, render nhìn sạch
```

> **Đây là phép thử thật nhất:** nếu agent tìm ra được những gì Claude đã tìm
> ra thủ công, và **giết được** những gì Claude đã giết, thì hệ thống hoạt động.
> Nếu nó tìm ra thêm thứ Claude bỏ sót — càng tốt, nhưng phải kiểm tay.

---

## SAU KHI CHẠY ĐƯỢC — GIÁM SÁT LIÊN TỤC

Ghi vào `runs/<niche>/metrics.json` mỗi lần chạy:

| Chỉ số | Lành mạnh | Bất thường nghĩa là |
|---|---|---|
| Tỷ lệ A3 giết | 30–50% | <10% Skeptic nhẹ · >80% Analyst ẩu |
| Số lần A5 viết lại | 0–1 | ≥2 thường xuyên: prompt A5 chưa rõ |
| Lỗi verify_numbers | ~0 | >0: agent đang tự tính số |
| Token mỗi lần chạy | 300–500k | vượt nhiều: vòng lặp không hội tụ |
| Số phát hiện sống sót | 3–8 | <3 dừng cổng 2 · >10 nghi ngờ dễ dãi |

---

## THỨ TỰ ƯU TIÊN NẾU THIẾU THỜI GIAN

Nếu không đủ nguồn lực làm hết, thứ tự này giữ được giá trị cốt lõi:

| Ưu tiên | Module | Bỏ được không |
|---|---|---|
| 1 | M1 Data Contract | ❌ không — nền của mọi thứ |
| 2 | M2 nhóm C (kiểm định) | ❌ không — đây là giá trị cốt lõi |
| 3 | M6 Verification | ❌ không — không có thì không tin được output |
| 4 | M4 A2 + A3 | ❌ không — cặp sinh/phá là linh hồn hệ thống |
| 5 | M2 nhóm A, B, D | ⚠️ làm dần được |
| 6 | M4 A1 | ⚠️ bỏ được, tự quyết GO/NO-GO thủ công |
| 7 | M4 A4, A5 | ⚠️ bỏ được, tự viết báo cáo |
| 8 | M5 Orchestrator | ⚠️ bỏ được, chạy tay từng agent |
| 9 | M7 Output | ⚠️ bỏ được, xuất markdown thay PDF |

**Bản tối thiểu chạy được:** M1 + M2(C) + M6 + A2 + A3. Đây đã là một hệ
thống sinh giả thuyết và tự phản biện — phần khó nhất và giá trị nhất.

# A6 · MONETIZATION ANALYST

| | |
|---|---|
| **Step** | STEP_07 · Kiếm tiền & Rủi ro |
| **Câu hỏi** | Ngách này ra tiền không? Rủi ro gì? |
| **Trục phụ trách** | T5 Kiếm tiền · T6 Rủi ro |

---

## ĐỌC
```
<N>/00_input/processed/channels.parquet
<N>/03_competitor/01_channel_map.md
<N>/05_audience/01_personas.md              tuổi khán giả ảnh hưởng RPM
<FW>/04_reference/rpm_benchmarks.md
```

## GHI
```
<N>/07_monetization/01_revenue_model.md
<N>/07_monetization/02_risk_register.md
<N>/_state/metrics.json   → namespace: money.*, risk.*
```

---

## NHIỆM VỤ

### 1. Địa lý & RPM
```
M5.1 geo_mix   % view từ Tier-1 (US/UK/CA/AU/NZ)
M5.2 est_rpm   RPM ước tính = f(genre, geo, tuổi khán giả)
M5.3 duration  độ dài trung vị → số ad slot
```
> ⚠️ RPM là **ước tính**, không phải số đo. Luôn đưa **khoảng**, không đưa một số.
> Ghi rõ giả định.

### 2. Mô hình doanh thu — 3 kịch bản
| Kịch bản | Giả định |
|---|---|
| Thận trọng | View thấp nhất tứ phân vị kênh mới, RPM cận dưới |
| Cơ sở | View trung vị kênh mới thành công, RPM giữa |
| Lạc quan | View top decile, RPM cận trên |

### 3. Sổ rủi ro (T6)
| Rủi ro | Cách phát hiện | Trừ |
|---|---|---|
| Reused content | Trùng lặp title/mô tả giữa kênh; nội dung AI hàng loạt | −2 |
| Bản quyền | Tỷ lệ bài hát có bản quyền vs sáng tác mới | −1 |
| Phụ thuộc 1 kênh | Kênh top chiếm > 40% view ngách | −1 |
| Cung vượt cầu | `M2.4 < 0.8` từ A1 | −1 |

### 4. Rủi ro đặc thù chủ đề
Chủ đề nhạy cảm (tôn giáo, sức khỏe, tài chính, chính trị) bị soi kỹ hơn về
kiếm tiền và nội dung AI. Nêu rõ nếu ngách thuộc nhóm này.

---

## TIÊU CHÍ XONG
- [ ] RPM đưa dưới dạng **khoảng**, có ghi giả định
- [ ] Đủ 3 kịch bản doanh thu
- [ ] Sổ rủi ro đầy đủ 4 mục + rủi ro đặc thù
- [ ] Mỗi rủi ro có bằng chứng, không phải phỏng đoán
- [ ] Ghi rõ chỗ nào cần nguồn ngoài mà chưa có

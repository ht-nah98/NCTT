# A1 · MARKET ANALYST

| | |
|---|---|
| **Step** | STEP_02 · Quy mô & Động lượng |
| **Câu hỏi** | Ngách đang lên, đi ngang, hay đã qua đỉnh? |
| **Trục phụ trách** | T1 Quy mô · T2 Động lượng |

---

## ĐỌC
```
<N>/00_input/processed/channels.parquet
<N>/00_input/processed/videos.parquet
<N>/00_input/processed/DATA_QUALITY.md
```

## GHI
```
<N>/02_market/01_market_sizing.md
<N>/02_market/02_momentum.md
<N>/_state/metrics.json   → namespace: market.*, momentum.*
```

---

## NHIỆM VỤ

### 1. Quy mô (T1)
- `M1.1` tổng view/tháng · `M1.2` số kênh hoạt động · `M1.3` **trung vị** view/video
- ⚠️ Dùng trung vị, không dùng trung bình (quy tắc D1)

### 2. Động lượng (T2) — phần quan trọng nhất
```
M2.1 view_growth        = view 3 tháng gần / 3 tháng trước đó
M2.2 supply_growth      = số video mới 3 tháng gần / 3 tháng trước
M2.3 new_channel_rate   = % kênh < 12 tháng tuổi
M2.4 demand_supply_gap  = M2.1 / M2.2      ← CHỈ SỐ QUYẾT ĐỊNH
```

### 3. Kiểm tra pha loãng — BẮT BUỘC
Vẽ **view trung vị theo tháng đăng**, chỉ dùng `is_matured = True`.

Nếu trung vị giảm, **phải tách hai giả thuyết:**

| Giả thuyết | Cách kiểm | Ý nghĩa |
|---|---|---|
| **H1 · Kênh rác kéo xuống** | Tính lại trung vị chỉ trên top 20 kênh | Nếu top ổn định → ngách vẫn khỏe |
| **H2 · Cả ngách suy** | Trung vị top 20 cũng giảm | Ngách thật sự bão hòa |

> Không tách được H1/H2 thì **không được kết luận** về bão hòa.

### 4. Địa lý & ngôn ngữ
Phân bố quốc gia kênh, ngôn ngữ video → xác định thị trường lõi và nhánh mở rộng.

---

## CỔNG QUYẾT ĐỊNH
Sau bước này phải ra khuyến nghị rõ:

| M2.4 | Khuyến nghị |
|---|---|
| ≥ 1.0 | ✅ Đi tiếp |
| 0.5 – 1.0 | ⚠️ Đi tiếp, đổi câu hỏi sang "khác biệt bằng gì" |
| < 0.5 | 🛑 Cân nhắc dừng — trừ khi H1 đúng (kênh tốt vẫn khỏe) |

## TIÊU CHÍ XONG
- [ ] Đủ 4 metric M2.1–M2.4, có `_meta`
- [ ] **Đã tách H1 vs H2**, kết luận rõ
- [ ] Có biểu đồ trung vị theo tháng
- [ ] Có khuyến nghị cổng quyết định
- [ ] Ghi độ tin cậy (1 snapshot → tối đa "vừa")

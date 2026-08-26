# THAM CHIẾU RPM

> Dùng cho metric `M5.2` trong trục T5.
> ⚠️ **Đây là ước tính khoảng, không phải số đo.** Luôn đưa khoảng, ghi rõ giả định,
> và verify bằng dữ liệu thật khi có.

## YẾU TỐ ẢNH HƯỞNG RPM

```
RPM ≈ f( địa lý , độ tuổi khán giả , chủ đề , định dạng , mùa )
```

| Yếu tố | Ảnh hưởng |
|---|---|
| **Địa lý** | Lớn nhất. Tier-1 (US/UK/CA/AU/NZ) cao hơn nhiều lần thị trường mới nổi |
| **Độ tuổi** | Khán giả 45+ thường RPM cao hơn (sức mua, ít dùng adblock) |
| **Chủ đề** | Tài chính/bảo hiểm/B2B cao nhất; giải trí/trẻ em thấp nhất |
| **Định dạng** | Video dài > 8 phút có nhiều ad slot hơn |
| **Mùa** | Q4 cao nhất, Q1 thấp nhất — chênh có thể 2× |

## KHOẢNG THAM CHIẾU (nhạc, thị trường Mỹ)

| Nhóm | RPM ước tính |
|---|---|
| Nhạc nền / lo-fi / instrumental, khán giả trẻ | $0.5 – $2 |
| Nhạc có lời, khán giả rộng | $1.5 – $4 |
| Nhạc chủ đề đặc thù, khán giả lớn tuổi Tier-1 | $3 – $8 |
| Nội dung có yếu tố giáo dục/tôn giáo, khán giả 50+ Mỹ | $4 – $10 |

> Nhạc nói chung RPM **thấp hơn** nội dung nói (talking-head), vì thời lượng xem
> dài nhưng mức độ chú ý thấp.

## CÁCH DÙNG
1. Xác định geo mix từ `channels.parquet`
2. Xác định độ tuổi khán giả từ `05_audience/01_personas.md`
3. Chọn khoảng phù hợp
4. **Ghi rõ giả định** và mức độ không chắc chắn
5. Đưa 3 kịch bản, không đưa một con số

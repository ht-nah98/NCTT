#!/usr/bin/env bash
# ══════════════════════════════════════════════════════════════════════
# CHẠY LẠI TOÀN BỘ PIPELINE TỪ DỮ LIỆU THÔ
#
#   bash pipeline/run_all.sh [niche_path] [--with-thumbs] [--no-pdf]
#
#   --with-thumbs   chạy cả nhánh phân tích ảnh (cần raw/thumbs/*.jpg)
#                   CHẬM: ~2 phút trích đặc trưng + ~12 phút rút brief
#   --no-pdf        bỏ qua bước sinh PDF (chỉ chạy phân tích + chấm điểm)
#
# Nhánh LÕI luôn chạy (không cần ảnh). Nhánh ẢNH là tùy chọn.
# ══════════════════════════════════════════════════════════════════════
set -euo pipefail

N="niches/christian-blues"; THUMBS=0; PDF=1
for a in "$@"; do
  case "$a" in
    --with-thumbs) THUMBS=1 ;;
    --no-pdf)      PDF=0 ;;
    --*)           echo "Tham số lạ: $a"; exit 1 ;;
    *)             N="$a" ;;
  esac
done
[ -d "$N" ] || { echo "Không thấy ngách: $N"; exit 1; }

# Dựng khung thư mục trước — ngách mới chưa có 02_market/, 03_competitor/...
# (Bỏ bước này thì script phân tích chết ở lần ghi CSV đầu tiên. Bài học T22.)
python3 pipeline/_common.py "$N" >/dev/null

t0=$(date +%s)
step() { printf '\n\033[1m▸ %s\033[0m\n' "$1"; }
ok()   { printf '  ✅ %s\n' "$1"; }

echo "═══════════════════════════════════════════════════"
echo " CHẠY LẠI PIPELINE · $N"
echo " nhánh ảnh: $([ $THUMBS = 1 ] && echo BẬT || echo tắt) · PDF: $([ $PDF = 1 ] && echo BẬT || echo tắt)"
echo "═══════════════════════════════════════════════════"

# ─────────── NHÁNH LÕI: dữ liệu → phân tích → điểm ───────────
step "STEP_01 · Nền móng"
python3 pipeline/extract/normalize.py      "$N" >/dev/null; ok "chuẩn hóa xlsx → parquet"
python3 pipeline/transform/enrich.py       "$N" >/dev/null; ok "kiểm toán + làm giàu"
python3 pipeline/transform/apply_filters.py "$N" >/dev/null; ok "lọc chọn lọc 4 rổ"

step "STEP_02→07 · Phân tích"
python3 pipeline/analyze/step02_market.py       "$N" >/dev/null; ok "quy mô & động lượng"
python3 pipeline/analyze/step03_competitor.py "$N" >/dev/null; ok "bản đồ đối thủ"
python3 pipeline/analyze/step04_outlier.py "$N" >/dev/null; ok "sàng lọc đối chứng"
# Chuẩn sản xuất (nhịp đăng · tracklist · độ dài) — lấp §5.5 của hồ sơ ngách.
python3 pipeline/analyze/step03b_production_norms.py "$N" >/dev/null; ok "chuẩn sản xuất"

# ── Nhánh NHẠC (04h) · tùy chọn — cần 00_input/raw/audio/*.yaml (DSP librosa).
#    Chạy Ở ĐÂY vì STEP_08 và STEP_10 đều ĐỌC AUDIO_BRIEF.json.
#    Đặt sau chúng thì lần chạy đầu trên ngách mới sẽ thiếu khối music (T40).
if ls "$N"/00_input/raw/audio/*.yaml >/dev/null 2>&1; then
  python3 pipeline/extract/normalize_audio.py "$N" >/dev/null; ok "âm thanh: YAML → parquet"
  python3 pipeline/analyze/step04h_audio.py   "$N" >/dev/null; ok "âm thanh: AUDIO_BRIEF.json"
fi
# ── Nhánh KIỂM ĐỊNH nhạc (04h2) · tùy chọn — cần raw/audio_dna.xlsx (nhiều track
#    có view thật). Khác 04h: 04h MÔ TẢ nhóm top, 04h2 KIỂM ĐỊNH thắng/thua.
#    KHÔNG nuốt stdout: cảnh báo bẫy Simpson phải hiện ra (T46).
if [ -f "$N/00_input/raw/audio_dna.xlsx" ]; then
  python3 pipeline/extract/normalize_audio_dna.py "$N" >/dev/null
  # bản ĐẦY ĐỦ 594 trường (nếu có) — 04h3 tự ưu tiên dùng bản này
  python3 pipeline/extract/normalize_audio_full.py "$N" >/dev/null
  python3 pipeline/analyze/step04h2_audio_test.py "$N" | grep -vE '^✅|^   [a-z]' || true
  ok "âm thanh: AUDIO_TEST.json (kiểm định)"
  # 04h3 = TÁI TẠO (mục tiêu sản xuất). Khác 04h2 (so sánh thắng/thua).
  python3 pipeline/analyze/step04h3_audio_recipe.py "$N" >/dev/null
  ok "âm thanh: AUDIO_RECIPE.json (công thức tái tạo)"
fi
# ── Phân tích LỜI HÁT (04i) · tùy chọn — cần lyrics_features + audio_dna_full.
#    Ghép hai bên theo track_id để hỏi được «lời thế nào thì nhạc thế nào».
if [ -f "$N/00_input/processed/lyrics_features.parquet" ] \
   && [ -f "$N/00_input/processed/audio_dna_full.parquet" ]; then
  python3 pipeline/analyze/step04i_lyrics.py "$N" >/dev/null
  ok "lời hát: LYRICS_ANALYSIS.json"
fi
# ── Thông số nhạc DIỆN RỘNG (04j) · tùy chọn — đo trên toàn bộ track thay vì
#    5 bản. Gỡ bẫy nhân đôi tempo trước khi tính (T38-39).
if [ -f "$N/00_input/processed/audio_dna_full.parquet" ]; then
  python3 pipeline/analyze/step04j_music_wide.py "$N" >/dev/null
  ok "nhạc diện rộng: MUSIC_WIDE.json"
fi
# ── Nhánh LỜI HÁT (L5) · tùy chọn — chạy khi đã có transcript, từ BẤT KỲ nhánh
#    nào: L3 (phiên âm cả video) hoặc A2+A3 (audio cắt sẵn theo bài). A3 ghi
#    vào đúng thư mục transcripts/ nên chỗ này không cần biết nguồn là gì.
#    L1–L4 và A1–A3 KHÔNG chạy ở đây: chúng gọi mạng/tốn hàng giờ CPU, không
#    thuộc luồng dựng lại báo cáo. Chạy tay theo pipeline/lyrics/README.md
#    (nhánh L) hoặc README_A.md (nhánh A).
if ls "$N"/00_input/lyrics/transcripts/*.json >/dev/null 2>&1; then
  python3 pipeline/lyrics/L5_features.py "$N" >/dev/null
  ok "lời hát: lyrics_features.parquet"
fi
# Phân loại public-domain vs sáng tác mới — cần lyrics_raw.parquet (L3), độc
# lập với L5. So khớp n-gram với corpus hymn/spiritual PD (T-PD, 2026-08-25).
if [ -f "$N/00_input/processed/lyrics_raw.parquet" ]; then
  python3 pipeline/analyze/step_pd_classify.py "$N" >/dev/null
  ok "phân loại bản quyền lời: pd_classification.parquet"
  # Trích bằng chứng nghe được (link tua + cụm trùng nguyên văn) cho mọi track
  # có điểm khớp > 0 — kể cả dưới ngưỡng, để người đọc tự đối chứng.
  python3 pipeline/analyze/step_pd_evidence.py "$N" >/dev/null
  ok "bằng chứng đối chứng: pd_evidence.parquet"
fi
python3 pipeline/analyze/step05_audience.py "$N" >/dev/null; ok "chân dung khách hàng"
python3 pipeline/analyze/step06_keyword.py "$N" >/dev/null; ok "từ khóa & đóng gói"
# step07 ĐỌC M2.4 từ metrics.json → phải gom trước
python3 pipeline/transform/collect_metrics.py "$N" >/dev/null 2>&1 || true
python3 pipeline/analyze/step07_monetization.py "$N" >/dev/null; ok "kiếm tiền & rủi ro"

step "GOM CHỈ SỐ"
python3 pipeline/transform/collect_metrics.py "$N"

step "ÁP NGƯỠNG RUBRIC"
python3 pipeline/scoring/apply_thresholds.py "$N"

step "CHẤM ĐIỂM"
python3 pipeline/scoring/scoring_engine.py "$N"

step "STEP_08 · Tổng hợp"
# step08 ĐỌC scores.json → phải chạy SAU chấm điểm
python3 pipeline/analyze/step08_synthesis.py "$N" >/dev/null; ok "tổng hợp"
python3 pipeline/analyze/step09_data_audit.py "$N" >/dev/null; ok "kiểm kê dữ liệu"

step "STEP_10 · Playbook khởi tạo kênh"
python3 pipeline/analyze/step10_playbook.py "$N" >/dev/null
ok "CHANNEL_PLAYBOOK.json (đầu vào cho workflow sản xuất)"
python3 pipeline/analyze/step10b_channel_profiles.py "$N" >/dev/null
ok "CHANNEL_PROFILES.json (hồ sơ 5 kênh hình mẫu)"

step "TỰ KIỂM RUBRIC"
python3 pipeline/scoring/verify_rubric.py "$N"

# Tự kiểm TÀI LIỆU HỆ THỐNG — tài liệu có còn khớp code không (T90).
# Không dừng pipeline nếu lệch, chỉ báo: sửa tài liệu là việc của người,
# không nên chặn việc dựng lại báo cáo.
step "TỰ KIỂM TÀI LIỆU HỆ THỐNG"
python3 pipeline/scoring/verify_system_docs.py "$N" || true

# ─────────── NHÁNH ẢNH (tùy chọn) ───────────
if [ $THUMBS = 1 ]; then
  if ! ls "$N"/00_input/raw/thumbs/*.jpg >/dev/null 2>&1; then
    echo "⚠ Bỏ qua nhánh ảnh: không thấy $N/00_input/raw/thumbs/*.jpg"
  else
    step "STEP_04b · Kiểm định thumbnail"
    python3 pipeline/analyze/step04c_thumbnail_full.py "$N" --workers=8 >/dev/null
    ok "trích đặc trưng hình học toàn ngách"
    python3 pipeline/analyze/step04b_thumbnail.py      "$N" >/dev/null; ok "so B1 vs B4"
    python3 pipeline/analyze/step04d_thumbnail_top.py  "$N" >/dev/null; ok "nhóm dẫn đầu + kiểm Simpson"

    step "STEP_04g · Brief tái tạo ảnh"
    CUDA_VISIBLE_DEVICES="" python3 pipeline/analyze/step04g_brief_extract.py "$N" >/dev/null
    ok "đo NGƯỜI (YOLO-seg) + CHỮ (OCR) trên nhóm top 5%"
  fi
fi

# ─────────── BÁO CÁO PDF ───────────
if [ $PDF = 1 ]; then
  step "SINH BÁO CÁO PDF"
  # BIỂU ĐỒ: vẫn sinh — build_final_summary/build_niche_profile nhúng các PNG này.
  # BUILDER 7 BÁO CÁO STEP: NGỪNG DỰNG (2026-08-26). Chúng cho 79 trang mà mỗi
  # bản tự lặp "Tóm tắt điều hành" + "Độ tin cậy" riêng, cùng một bộ số nền lặp
  # ở 6-7 file. Nội dung đã gộp vào build_detail.py (8 trang). Script build_report*
  # chuyển vào pipeline/_archive/report_by_step/ (2026-08-28) — xem README ở đó.
  for i in "" 03 04 05 06 07 08; do
    python3 "pipeline/report/charts$i.py" >/dev/null 2>&1 || true
  done
  ok "biểu đồ (7 bộ)"
  # Khung chấm điểm — tài liệu chung, nhưng đọc scores.json làm ví dụ nên
  # phải dựng SAU khi chấm để số trong PDF luôn khớp (T27).
  # Nhánh tái tạo nội dung: ảnh (04b→04g) rồi nhạc (04h) — cùng tầng MÔ TẢ
  if [ $THUMBS = 1 ] && [ -f "$N/04_outlier/_brief_data.json" ]; then
    python3 pipeline/report/charts04b.py      >/dev/null 2>&1 || true
    python3 pipeline/report/build_report04b.py >/dev/null && ok "STEP_04b (thumbnail)"
    python3 pipeline/report/build_brief_pdf.py >/dev/null && ok "STEP_04g (brief ảnh)"
  fi
  # ── BÁO CÁO NHẠC HỢP NHẤT — thay 3 bản 04h/04h2/04h3 ─────────────────
  #    Người dùng phản hồi 3 bản «chia nhiều phần quá, khó đọc». Bản hợp nhất
  #    gộp âm thanh + âm nhạc + LỜI HÁT vào một file, theo trình tự sản xuất.
  #    Cần cả AUDIO_RECIPE (nhạc, n=5) và LYRICS_ANALYSIS (lời, n=307).
  if [ -f "$N/04_outlier/audio/AUDIO_RECIPE.json" ] \
     && [ -f "$N/04_outlier/lyrics/LYRICS_ANALYSIS.json" ]; then
    python3 pipeline/report/build_music_unified.py "$N" >/dev/null \
      && ok "NHẠC hợp nhất (nhạc + lời)"
  else
    # thiếu phần lời → lùi về 3 bản cũ để không mất báo cáo nhạc
    if [ -f "$N/04_outlier/audio/AUDIO_BRIEF.json" ]; then
      python3 pipeline/report/build_report04h.py "$N" >/dev/null && ok "STEP_04h (brief nhạc)"
    fi
    if [ -f "$N/04_outlier/audio/AUDIO_TEST.json" ]; then
      python3 pipeline/report/build_report04h2.py "$N" >/dev/null && ok "STEP_04h2 (kiểm định nhạc)"
    fi
    if [ -f "$N/04_outlier/audio/AUDIO_RECIPE.json" ]; then
      python3 pipeline/report/build_report04h3.py "$N" >/dev/null && ok "STEP_04h3 (công thức tái tạo)"
    fi
  fi

  python3 pipeline/report/build_rubric_pdf.py "$N" >/dev/null && ok "RUBRIC (khung chấm điểm)"
  # Kiến trúc — tài liệu khung chung. Đọc scores.json/metrics.json làm ví dụ
  # nên cũng phải dựng SAU khi chấm (T27). In cảnh báo lệch sơ đồ nếu có.
  python3 pipeline/report/build_arch_pdf.py "$N" | grep -v '^✅' || true
  ok "ARCH (kiến trúc hệ thống)"
  # HỒ SƠ NGÁCH — bản cho cấp duyệt, bám khung template v1.0 của phòng R&D.
  # Đọc metrics/scores + AUDIO_RECIPE nên phải dựng SAU cùng (T27).
  # Biểu đồ hồ sơ phải sinh TRƯỚC builder — builder nhúng ảnh dạng base64.
  python3 pipeline/report/charts_profile.py "$N" >/dev/null 2>&1 || true
  python3 pipeline/report/build_niche_profile.py "$N" >/dev/null && ok "HỒ SƠ NGÁCH (bản trình sếp)"

  # ĐÚC KẾT CUỐI — bản cô đọng gộp 8 bước, chỉ kết quả + số liệu quyết định
  # (yêu cầu 2026-08-25). Đọc _synthesis.json/scores.json nên dựng SAU cùng.
  python3 pipeline/report/build_final_summary.py "$N" >/dev/null 2>&1 && ok "BÁO CÁO (bản trình — 8 trang)"
  # BẢN CHI TIẾT — gộp nội dung 7 báo cáo STEP đã ngừng dựng ở trên.
  python3 pipeline/report/build_detail.py "$N" >/dev/null 2>&1 && ok "CHI TIẾT (bản tra cứu — gộp 7 bước)"
  # BẢN QUYỀN LỜI — chỉ dựng khi đã phân loại PD ở bước trên.
  if [ -f "$N/02_analysis/pd_classification.parquet" ]; then
    python3 pipeline/report/build_pd_report.py "$N" >/dev/null 2>&1 && ok "BẢN QUYỀN (public domain vs sáng tác mới)"
  fi
  # PHỤ LỤC bộ đối chiếu — chỉ đọc corpus JSON, không phụ thuộc kết quả phân loại.
  python3 pipeline/report/build_pd_corpus_list.py "$N" >/dev/null 2>&1 && ok "PHỤ LỤC (danh sách corpus PD + nguồn)"
  # PHỤ LỤC đối chứng — link YouTube tua tới chỗ trùng, để người đọc tự nghe kiểm.
  if [ -f "$N/02_analysis/pd_evidence.parquet" ]; then
    python3 pipeline/report/build_pd_evidence.py "$N" >/dev/null 2>&1 && ok "PHỤ LỤC (đối chứng track khớp hymn)"
  fi

  # ── BỐN TÀI LIỆU T1.1–T1.4 ────────────────────────────────────────────
  #    Chuẩn đầu ra sau 49 vòng cải tiến, thay cách tổ chức báo cáo theo STEP.
  #    Tổ chức theo NGƯỜI ĐỌC và LOẠI PHÁT BIỂU, không theo bước chạy:
  #      T1.1 fact base · T1.2 cơ chế · T1.3 đặc tả sản xuất · T1.4 thẻ đối thủ
  #    Dựng SAU chấm điểm vì T1.1 đọc scores.json.
  #    Xem framework/00_system/11_OUTPUT_CONTRACT.md
  # 7 tài liệu ĐỊNH VỊ riêng — mỗi định vị một PDF, có video đối chứng tra được.
  python3 pipeline/report/build_positioning_cards.py "$N" >/dev/null \
    && ok "ĐỊNH VỊ · 7 tài liệu riêng (99_report/_dinh-vi/)"
  python3 pipeline/report/build_T11_niche_facts.py      "$N" >/dev/null && ok "T1.1 · Hồ sơ ngách (fact base)"
  python3 pipeline/report/build_T12_audience_model.py   "$N" >/dev/null && ok "T1.2 · Mô hình khán giả & cơ chế"
  python3 pipeline/report/build_T13_music_spec.py       "$N" >/dev/null && ok "T1.3 · Đặc tả dòng nhạc"
  python3 pipeline/report/build_T14_competitor_cards.py "$N" >/dev/null && ok "T1.4 · Thẻ đối thủ"

  # Dò số liệu cũ còn sót trong PDF (bài học T27–T28).
  # Không dừng pipeline nếu lệch — chỉ báo để người dùng biết.
  step "KIỂM BÁO CÁO"
  python3 pipeline/report/verify_reports.py "$N" || true
fi

printf '\n═══════════════════════════════════════════════════\n'
printf ' ✅ XONG trong %d giây\n' "$(( $(date +%s) - t0 ))"
SCORE=$(python3 -c "import json,sys;print(json.load(open(sys.argv[1]))['total_score'])" \
        "$N/_state/scores.json" 2>/dev/null || echo '?')
printf ' Điểm: %s / 20\n' "$SCORE"
printf ' Báo cáo: %s/99_report/\n' "$N"
printf '═══════════════════════════════════════════════════\n'

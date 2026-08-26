"""STEP_01.1 — Chuẩn hóa: xlsx -> parquet. Ép kiểu, chuẩn UTC. KHÔNG sửa giá trị."""
import pandas as pd, sys, json
from pathlib import Path

NICHE = Path(sys.argv[1] if len(sys.argv)>1 else "niches/christian-blues")
RAW   = NICHE/"00_input/raw/christian-blues-raw.xlsx"
OUT   = NICHE/"00_input/processed"; OUT.mkdir(parents=True, exist_ok=True)

SHEETS = ["channels","videos","video_stats","comments","thumbnails","media_probe","video_master"]
DATE_COLS = ["published_at","fetched_at","snapshot_at","updated_at","probed_at"]

report = {}
xl = pd.ExcelFile(RAW)
for sh in SHEETS:
    if sh not in xl.sheet_names:
        report[sh] = {"status":"MISSING"}; continue
    df = pd.read_excel(xl, sh)
    for c in df.columns:
        if c in DATE_COLS:
            df[c] = pd.to_datetime(df[c], errors="coerce", utc=True)
    # numeric coercion
    for c in ["view_count","like_count","comment_count","subscriber_count",
              "video_count","duration_sec","category_id","width","height","bytes"]:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")
    # ID-like cols must stay string (phash is a 59-bit binary hash, not a number)
    for c in ["phash","video_id","channel_id","comment_id","parent_id","author_hash"]:
        if c in df.columns:
            df[c] = df[c].astype(str)
    # any remaining object col with oversized ints -> string
    for c in df.select_dtypes(include=["object"]).columns:
        if df[c].map(lambda v: isinstance(v,int) and abs(v) > 2**62).any():
            df[c] = df[c].astype(str)
    df.to_parquet(OUT/f"{sh}.parquet", index=False)
    report[sh] = {"status":"OK","rows":len(df),"cols":len(df.columns)}
    print(f"{sh:15} {len(df):>7} rows -> {sh}.parquet")

(OUT/"_normalize_report.json").write_text(json.dumps(report, indent=2, default=str))
print("\nDONE normalize")

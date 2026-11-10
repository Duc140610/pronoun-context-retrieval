import argparse
import os
import re
import pandas as pd
import config


def parse_movie_id(doc_path):
    # Đường dẫn dạng: en/1990/100288/4719672.xml.gz -> movie_id là 100288
    parts = doc_path.strip().split("/")
    if len(parts) >= 3:
        return parts[2]
    match = re.search(r"/(\d+)/", doc_path)
    return match.group(1) if match else doc_path


def process_ids(ids_path, min_ratio_11=config.C3_MIN_RATIO_11):
    print(f"Đang xử lý {ids_path}...")
    doc_stats = {}

    current_pair = None
    cur_en_path, cur_vi_path = None, None
    n_links = 0
    n_11 = 0
    max_en_id = 0
    c1_violations = 0
    c1_vi_violations = 0

    prev_en_id = -1
    prev_vi_id = -1

    with open(ids_path, "r", encoding="utf-8") as f:
        for line in f:
            parts = line.rstrip("\n").split("\t")
            if len(parts) < 4:
                continue

            en_path, vi_path = parts[0], parts[1]
            en_ids = [int(x) for x in parts[2].split()] if parts[2] else []
            vi_ids = [int(x) for x in parts[3].split()] if parts[3] else []

            pair = (en_path, vi_path)
            if pair != current_pair:
                if current_pair is not None:
                    movie_id = parse_movie_id(cur_en_path)
                    doc_stats[current_pair] = {
                        "en_path": cur_en_path,
                        "vi_path": cur_vi_path,
                        "movie": movie_id,
                        "n_links": n_links,
                        "n_11": n_11,
                        "ratio_11": n_11 / n_links if n_links > 0 else 0,
                        "max_en_id": max_en_id,
                        "c1_violations": c1_violations,
                        "c1_vi_violations": c1_vi_violations,
                    }
                current_pair = pair
                cur_en_path, cur_vi_path = en_path, vi_path
                n_links = 0
                n_11 = 0
                max_en_id = 0
                c1_violations = 0
                c1_vi_violations = 0

                prev_en_id = -1
                prev_vi_id = -1

            n_links += 1
            if len(en_ids) == 1 and len(vi_ids) == 1:
                n_11 += 1

            for eid in en_ids:
                if eid <= prev_en_id:
                    c1_violations += 1
                prev_en_id = eid
                if eid > max_en_id:
                    max_en_id = eid
                    
            for vid in vi_ids:
                if vid <= prev_vi_id:
                    c1_vi_violations += 1
                prev_vi_id = vid

        if current_pair is not None:
            movie_id = parse_movie_id(cur_en_path)
            doc_stats[current_pair] = {
                "en_path": cur_en_path,
                "vi_path": cur_vi_path,
                "movie": movie_id,
                "n_links": n_links,
                "n_11": n_11,
                "ratio_11": n_11 / n_links if n_links > 0 else 0,
                "max_en_id": max_en_id,
                "c1_violations": c1_violations,
                "c1_vi_violations": c1_vi_violations,
            }

    df = pd.DataFrame(list(doc_stats.values()))

    # Lưu toàn bộ thống kê trước khi lọc
    df.to_csv("data/boundaries_table.csv", index=False)

    print(f"Tổng số tài liệu quét được: {len(df):,}")

    print(
        "C1 tiếng Anh đạt:",
        (df.c1_violations == 0).sum()
    )

    print(
        "C1 cả Anh và Việt đạt:",
        (
            (df.c1_violations == 0) &
            (df.c1_vi_violations == 0)
        ).sum()
    )

    print(
        "C2 theo max_en_id >= 200:",
        (df.max_en_id >= 200).sum()
    )

    print(
        "C2 theo n_links >= 200:",
        (df.n_links >= 200).sum()
    )


    # Phương án A: C1 chỉ tiếng Anh + C2 theo n_links
    a = (
        (df.c1_violations == 0) &
        (df.n_links >= 200)
    )

    # Phương án B: C1 cả Anh và Việt + C2 theo n_links
    b = (
        (df.c1_violations == 0) &
        (df.c1_vi_violations == 0) &
        (df.n_links >= 200)
    )

    # Phương án C: C1 cả Anh và Việt + C2 theo max_en_id
    c = (
        (df.c1_violations == 0) &
        (df.c1_vi_violations == 0) &
        (df.max_en_id >= 200)
    )

    print("A - C1 EN + C2 n_links:", a.sum())
    print("B - C1 EN+VI + C2 n_links:", b.sum())
    print("C - C1 EN+VI + C2 max_en_id:", c.sum())
        
    # C1 & C2
    c1_c2 = df[
    (df.c1_violations <= config.C1_MAX_VIOLATIONS_EN) &
    (df.c1_vi_violations <= config.C1_MAX_VIOLATIONS_VI) &
    (df.max_en_id >= config.C2_MIN_SENTENCES)
]
    unique_movies_c2 = len(c1_c2["movie"].unique())
    print(f"Số tài liệu đạt C1 + C2: {len(c1_c2):,} (tương ứng {unique_movies_c2:,} phim duy nhất)")

    # C3: Lọc theo ratio_11
    c3 = c1_c2[c1_c2.ratio_11 >= min_ratio_11]

    # C4: Mỗi mã phim chọn bản có n_links lớn nhất
    c4 = c3.sort_values("n_links", ascending=False).drop_duplicates(subset=["movie"]).reset_index(drop=True)
    print(f"Số phim đạt chuẩn C1-C4 (ratio_11 >= {min_ratio_11}): {len(c4):,}")

    os.makedirs("data", exist_ok=True)
    out_csv = "data/selected_docs.csv"
    c4.to_csv(out_csv, index=False)
    print(f"Đã lưu kết quả vào {out_csv}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--ids", default="OpenSubtitles.en-vi.ids", help="Đường dẫn file .ids")
    parser.add_argument("--min-ratio-11", type=float, default=config.C3_MIN_RATIO_11)
    args = parser.parse_args()
    process_ids(args.ids, args.min_ratio_11)
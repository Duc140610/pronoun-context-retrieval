import hashlib
import pandas as pd
import config


def hash_score(movie, seed=config.SPLIT_SEED):
    """Số thực trong [0, 1), tất định theo (seed, mã phim)."""
    digest = hashlib.md5(f"{seed}:{movie}".encode("utf-8")).hexdigest()
    return int(digest, 16) / (16**32)


def assign_split(movie, seed=config.SPLIT_SEED, dev_ratio=config.DEV_RATIO):
    """Trả về 'dev' hoặc 'test'. Chỉ phụ thuộc vào mã phim và seed."""
    return "dev" if hash_score(movie, seed) < dev_ratio else "test"


def pick_movies(movies, n_dev=config.N_DEV, n_test=config.N_TEST, seed=config.SPLIT_SEED):
    """Chia trên toàn bộ `movies` trước, rồi lấy n phim đầu theo giá trị băm."""
    df = pd.DataFrame({"movie": sorted(set(map(str, movies)))})
    df["score"] = df.movie.map(lambda m: hash_score(m, seed))
    df["split"] = df.movie.map(lambda m: assign_split(m, seed))
    df = df.sort_values(["score", "movie"])
    dev = df[df.split == "dev"].head(n_dev)
    test = df[df.split == "test"].head(n_test)
    return pd.concat([dev, test]).reset_index(drop=True)


if __name__ == "__main__":
    sel = pd.read_csv("data/selected_docs.csv", dtype={"movie": str})
    picked = pick_movies(sel.movie)
    merged = picked.merge(sel, on="movie", how="left")
    merged.to_csv("data/split_movies.csv", index=False)
    print(f"Đã tạo data/split_movies.csv: {len(merged)} phim ({len(picked[picked.split == 'dev'])} dev, {len(picked[picked.split == 'test'])} test)")
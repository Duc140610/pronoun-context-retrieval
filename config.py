"""
Cấu hình dự án PR1: Context Retrieval cho dịch đại từ Anh-Việt.
Nguồn chân lý duy nhất cho toàn bộ các hằng số và tham số thực nghiệm.
"""

# Hạt giống băm cố định (BẤT BIẾN - không thay đổi sau khi chia tập)
SPLIT_SEED = 20261110
DEV_RATIO = 0.70
N_DEV = 280
N_TEST = 120

# Tiêu chí lọc ranh giới (C1 - C4)
# C1: Giới hạn số lần vi phạm thứ tự ID
C1_MAX_VIOLATIONS_EN = 0
C1_MAX_VIOLATIONS_VI = 0

# C2: Số ID câu tiếng Anh tối thiểu
C2_MIN_SENTENCES = 200

# C3: Tỷ lệ alignment 1-1 tối thiểu
C3_MIN_RATIO_11 = 0.85

# Cấu hình lọc câu mẫu
MAX_WE_PER_MOVIE = 3  # Giới hạn số câu 'we' lấy từ mỗi phim để đa dạng ngữ cảnh

# Đường dẫn tải dữ liệu từ xa
OPUS_ZIP_URL = "https://object.pouta.csc.fi/OPUS-OpenSubtitles/v2018/xml/en.zip"
TOTAL_ZIP_SIZE = 25071142020  # Content-Length chính xác từ server

# Thư mục lưu trữ
DIR_RAW_XML = "data/raw"
CACHE_CD_FILE = "data/central_directory_index.pkl"
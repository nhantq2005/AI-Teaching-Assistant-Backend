import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Load các biến môi trường từ file .env
load_dotenv()

# Lấy chuỗi kết nối từ file .env
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")

# 1. Khởi tạo Engine (Bộ máy giao tiếp với database)
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    echo=True  # Bật True để in các câu lệnh SQL ra terminal (tiện cho debug), set False khi deploy
)

# 2. Khởi tạo SessionLocal (Phiên làm việc với database)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Hàm Dependency để FastAPI sử dụng mỗi khi có request cần gọi Database
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
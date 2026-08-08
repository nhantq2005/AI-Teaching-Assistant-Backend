import json
import pickle
from pathlib import Path
from langchain_core.documents import Document
from langchain_community.retrievers import BM25Retriever


def build_bm25_index():
    # 1. Tự động xác định đường dẫn
    CURRENT_FILE = Path(__file__).resolve()
    ROOT_DIR = CURRENT_FILE.parents[3] if len(CURRENT_FILE.parents) > 3 else CURRENT_FILE.parent

    # 2. Cấu hình đường dẫn Input và Output
    input_chunk_file = ROOT_DIR / "processed_data" / "CSLT_Ch2_2122" / "final_chunks.jsonl"
    bm25_save_path = ROOT_DIR / "bm25_index.pkl"

    if not input_chunk_file.exists():
        print(f"[LỖI] Không tìm thấy file chunk tại: {input_chunk_file}")
        return

    # 3. Đọc dữ liệu Document
    print(f"[*] Đang tải dữ liệu từ {input_chunk_file.name}...")
    docs = []
    with open(input_chunk_file, 'r', encoding='utf-8') as f:
        for line in f:
            data = json.loads(line)
            docs.append(
                Document(
                    page_content=data['page_content'],
                    metadata=data['metadata']
                )
            )

    # 4. Khởi tạo và lưu mô hình BM25 (Sparse Retriever)
    print("[*] Đang xây dựng Sparse Retriever (BM25)...")
    bm25_retriever = BM25Retriever.from_documents(docs)

    with open(bm25_save_path, 'wb') as f:
        pickle.dump(bm25_retriever, f)

    print(f"[OK] Đã lưu thành công BM25 index tại: {bm25_save_path}")


if __name__ == "__main__":
    build_bm25_index()
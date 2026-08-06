import pickle
from pathlib import Path
from typing import List
from langchain_core.documents import Document


def update_bm25_index(new_documents: List[Document]):
    CURRENT_FILE = Path(__file__).resolve()
    ROOT_DIR = CURRENT_FILE.parents[3] if len(CURRENT_FILE.parents) > 3 else CURRENT_FILE.parent
    bm25_save_path = ROOT_DIR / "bm25_index.pkl"

    # 1. Lấy toàn bộ document cũ đang có trong BM25 (nếu có)
    existing_docs = []
    if bm25_save_path.exists():
        with open(bm25_save_path, 'rb') as f:
            old_retriever = pickle.load(f)
            existing_docs = old_retriever.docs

    # 2. Gộp document cũ và document mới
    all_docs = existing_docs + new_documents

    # 3. Tạo lại BM25Retriever tổng hợp và lưu đè file pkl
    from langchain_community.retrievers import BM25Retriever
    updated_retriever = BM25Retriever.from_documents(all_docs)

    with open(bm25_save_path, 'wb') as f:
        pickle.dump(updated_retriever, f)

    print(f"[OK] Đã cập nhật thành công BM25 Index ({len(all_docs)} chunks)!")
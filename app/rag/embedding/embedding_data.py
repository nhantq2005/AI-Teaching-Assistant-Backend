# import json
# from pathlib import Path
# from langchain_core.documents import Document
# from langchain_community.vectorstores import Chroma
# from langchain_huggingface import HuggingFaceEmbeddings
#
#
# def load_chunks_from_jsonl(file_path: Path) -> list[Document]:
#     """Đọc dữ liệu từ file JSONL và chuyển thành danh sách LangChain Document."""
#     docs = []
#     with open(file_path, 'r', encoding='utf-8') as f:
#         for line in f:
#             data = json.loads(line)
#             # Khôi phục lại đối tượng Document với content và metadata
#             doc = Document(
#                 page_content=data['page_content'],
#                 metadata=data['metadata']
#             )
#             docs.append(doc)
#     return docs
#
#
# def main():
#     # 1. Tự động xác định đường dẫn project
#     CURRENT_FILE = Path(__file__).resolve()
#     ROOT_DIR = CURRENT_FILE.parents[3] if len(CURRENT_FILE.parents) > 3 else CURRENT_FILE.parent
#
#     # 2. Cấu hình đường dẫn Input (dữ liệu chunk) và Output (thư mục lưu ChromaDB)
#     input_chunk_file = ROOT_DIR / "processed_data" / "CSLT_Ch2_2122" / "final_chunks.jsonl"
#     chroma_db_dir = ROOT_DIR / "chroma_db"
#
#     if not input_chunk_file.exists():
#         print(f"[LỖI] Không tìm thấy file chunk tại: {input_chunk_file}")
#         print("Vui lòng chạy file chunking.py trước khi embedding.")
#         return
#
#     # 3. Load danh sách các chunks
#     print(f"[*] Đang tải dữ liệu từ {input_chunk_file.name}...")
#     documents = load_chunks_from_jsonl(input_chunk_file)
#     print(f"[OK] Đã tải thành công {len(documents)} chunks.\n")
#
#     # 4. Khởi tạo mô hình Embedding
#     # Sử dụng BGE-M3 (rất mạnh cho đa ngôn ngữ và tiếng Việt)
#     # Nếu máy cấu hình yếu, bạn có thể đổi sang "keepitreal/vietnamese-sbert"
#     model_name = "BAAI/bge-m3"
#     print(
#         f"[*] Đang khởi tạo mô hình Embedding ({model_name}). Quá trình này có thể mất chút thời gian ở lần tải đầu tiên...")
#
#     embeddings = HuggingFaceEmbeddings(
#         model_name=model_name,
#         # Nếu máy bạn có GPU, hãy đổi "cpu" thành "cuda" để chạy nhanh hơn
#         model_kwargs={'device': 'cpu'},
#         encode_kwargs={'normalize_embeddings': True}  # Chuẩn hóa vector (Cosine Similarity)
#     )
#     print("[OK] Đã nạp xong mô hình Embedding.\n")
#
#     # 5. Khởi tạo và đẩy dữ liệu vào ChromaDB
#     print("[*] Đang tiến hành nhúng (Embedding) và lưu vào ChromaDB...")
#
#     # Chroma.from_documents sẽ tự động chia lô (batch) và nhúng từng Document
#     vectorstore = Chroma.from_documents(
#         documents=documents,
#         embedding=embeddings,
#         persist_directory=str(chroma_db_dir),
#         collection_name="cslt_collection"  # Tên bộ sưu tập dữ liệu
#     )
#
#     print(f"[OK] Hoàn tất! Database đã được lưu tại: {chroma_db_dir}")
#
#     # ==========================================
#     # TEST THỬ CHỨC NĂNG RETRIEVAL (TÌM KIẾM)
#     # ==========================================
#     print("\n" + "=" * 50)
#     print("TEST TÌM KIẾM VECTOR (SIMILARITY SEARCH)")
#     print("=" * 50)
#
#     query = "Biến là gì?"
#     print(f"Câu hỏi: '{query}'\n")
#
#     # Tìm 2 chunk có ngữ nghĩa liên quan nhất
#     results = vectorstore.similarity_search(query, k=2)
#
#     for i, res in enumerate(results):
#         print(f"--- Kết quả {i + 1} ---")
#         print(f"Metadata: {res.metadata}")
#         print(f"Nội dung: {res.page_content[:200]}...\n")
#
#
# if __name__ == "__main__":
#     main()

from pathlib import Path
from typing import List

import torch
from langchain_core.documents import Document
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings


def embed_and_save_to_chroma(documents: List[Document], collection_name: str = "cslt_collection"):
    CURRENT_FILE = Path(__file__).resolve()
    ROOT_DIR = CURRENT_FILE.parents[3] if len(CURRENT_FILE.parents) > 3 else CURRENT_FILE.parent
    chroma_db_dir = ROOT_DIR / "chroma_db"

    if not documents:
        print("[CẢNH BÁO] Không có dữ liệu document để embedding.")
        return

    model_name = "BAAI/bge-m3"
    print(f"[*] Đang khởi tạo mô hình Embedding ({model_name})...")

    device = "cuda" if torch.cuda.is_available() else "cpu"

    embeddings = HuggingFaceEmbeddings(
        model_name=model_name,
        model_kwargs={'device': device},
        encode_kwargs={'normalize_embeddings': True}
    )

    print(f"[*] Đang thêm {len(documents)} chunks mới vào ChromaDB...")

    # Khởi tạo hoặc nạp ChromaDB hiện có
    vectorstore = Chroma(
        persist_directory=str(chroma_db_dir),
        embedding_function=embeddings,
        collection_name=collection_name
    )

    # Nạp bổ sung các chunk mới vào vectorstore
    vectorstore.add_documents(documents)

    print(f"[OK] Hoàn tất! Đã lưu thành công vào ChromaDB tại: {chroma_db_dir}")
    return vectorstore
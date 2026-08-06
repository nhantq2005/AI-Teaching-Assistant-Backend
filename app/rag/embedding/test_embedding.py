from pathlib import Path
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings


def main():
    # 1. Xác định đường dẫn project
    CURRENT_FILE = Path(__file__).resolve()
    ROOT_DIR = CURRENT_FILE.parents[3] if len(CURRENT_FILE.parents) > 3 else CURRENT_FILE.parent
    chroma_db_dir = ROOT_DIR / "chroma_db"

    if not chroma_db_dir.exists():
        print(f"[LỖI] Không tìm thấy thư mục Database tại: {chroma_db_dir}")
        print("Vui lòng chạy file embedding_data.py trước để tạo DB.")
        return

    # 2. Nạp lại mô hình Embedding (Bắt buộc phải giống model lúc tạo DB)
    model_name = "BAAI/bge-m3"
    print(f"[*] Đang tải mô hình Embedding ({model_name}) lên bộ nhớ...")
    embeddings = HuggingFaceEmbeddings(
        model_name=model_name,
        model_kwargs={'device': 'cpu'},
        encode_kwargs={'normalize_embeddings': True}
    )
    print("[OK] Đã nạp xong mô hình Embedding.\n")

    # 3. Kết nối với Vector Database có sẵn
    print(f"[*] Đang kết nối với ChromaDB tại {chroma_db_dir}...")
    vectorstore = Chroma(
        persist_directory=str(chroma_db_dir),
        embedding_function=embeddings,
        collection_name="cslt_collection"
    )
    print("[OK] Đã kết nối thành công!\n")

    # 4. Vòng lặp Test Tìm kiếm
    print("=" * 60)
    print("TEST TÌM KIẾM VECTOR (Gõ 'exit' hoặc 'quit' để thoát)")
    print("=" * 60)

    while True:
        query = input("\nNhập câu hỏi tìm kiếm: ")
        if query.lower() in ['exit', 'quit']:
            print("Đã thoát công cụ test.")
            break

        if not query.strip():
            continue

        print("[*] Đang truy xuất dữ liệu...")
        # Tìm 3 chunk có ngữ nghĩa liên quan nhất
        results = vectorstore.similarity_search(query, k=5)

        for i, res in enumerate(results):
            print(f"\n--- Kết quả {i + 1} ---")
            print(f"Metadata: {res.metadata}")
            # In ra 300 ký tự đầu tiên của kết quả để dễ nhìn
            print(f"Nội dung:\n{res.page_content}\n")


if __name__ == "__main__":
    main()
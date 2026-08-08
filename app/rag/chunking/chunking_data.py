# import json
# from pathlib import Path
# import re
# from langchain_core.documents import Document
# from langchain_text_splitters import RecursiveCharacterTextSplitter
#
#
# def load_and_group_blocks(jsonl_path):
#     """Đọc file JSONL và gộp các block theo cây thư mục (heading_path)."""
#     grouped_sections = {}
#
#     with open(jsonl_path, 'r', encoding='utf-8') as f:
#         for line in f:
#             block = json.loads(line)
#
#             # Bỏ qua các block chỉ chứa mỗi tiêu đề (vì tiêu đề đã nằm trong metadata)
#             if block['block_type'] == 'heading':
#                 continue
#
#             # Nối mảng heading_path thành một chuỗi chủ đề thống nhất
#             path_key = " > ".join(block['heading_path']) if block.get('heading_path') else "General"
#
#             if path_key not in grouped_sections:
#                 grouped_sections[path_key] = {
#                     "text": "",
#                     "metadata": {
#                         "source": block['source_file'],
#                         "topic_path": path_key,
#                         "start_page": block['page_number']
#                     }
#                 }
#
#             block_text = block['text']
#
#             # 1. Sửa lỗi mũi tên bị dịch nhầm thành chữ "đ" (đ error -> -> error)
#             block_text = re.sub(r'(^|\n)đ (error|warning)', r'\1-> \2', block_text)
#
#             # 2. Phục hồi thẻ Markdown nếu thuật toán nhận diện đây là Code
#             if block.get('block_type') == 'code':
#                 block_text = f"```cpp\n{block_text}\n```"
#
#             # Nối nội dung text đã được "trang điểm" vào chủ đề tương ứng
#             grouped_sections[path_key]["text"] += block_text + "\n\n"
#             # ==========================================
#
#     return grouped_sections
#
#
# def create_langchain_documents(grouped_sections):
#     """Chuyển đổi dữ liệu đã gộp thành LangChain Documents và cắt nhỏ nếu cần."""
#     # Cấu hình bộ cắt đệ quy: Giới hạn 800 ký tự, phần giao nhau 100 ký tự
#     text_splitter = RecursiveCharacterTextSplitter(
#         chunk_size=800,
#         chunk_overlap=100,
#         separators=["\n\n", "\n", ".", " ", ""]
#     )
#
#     documents = []
#     for path_key, data in grouped_sections.items():
#         # Bỏ qua các mục trống
#         if not data["text"].strip():
#             continue
#
#         doc = Document(page_content=data["text"].strip(), metadata=data["metadata"])
#
#         # Split_documents sẽ tự động chia nhỏ doc nếu vượt quá chunk_size
#         # và TỰ ĐỘNG copy nguyên metadata cho các chunk con.
#         splits = text_splitter.split_documents([doc])
#         documents.extend(splits)
#
#     return documents
#
#
# # def save_chunks_to_jsonl(chunks, output_path):
# #     """Lưu danh sách LangChain Documents vào file JSONL."""
# #     # Đảm bảo thư mục cha tồn tại
# #     output_path.parent.mkdir(parents=True, exist_ok=True)
# #
# #     with open(output_path, 'w', encoding='utf-8') as f:
# #         for chunk in chunks:
# #             # Chuyển object Document thành dictionary để dễ lưu trữ
# #             chunk_dict = {
# #                 "page_content": chunk.page_content,
# #                 "metadata": chunk.metadata
# #             }
# #             # Ghi từng chunk thành một dòng JSON độc lập
# #             f.write(json.dumps(chunk_dict, ensure_ascii=False) + "\n")
#
# #
# # if __name__ == "__main__":
# #     # 1. Tự động xác định thư mục gốc của project (lùi lại 3 cấp từ app/rag/chunking)
# #     CURRENT_FILE = Path(__file__).resolve()
# #     ROOT_DIR = CURRENT_FILE.parents[3] if len(CURRENT_FILE.parents) > 3 else CURRENT_FILE.parent
# #
# #     # 2. Xây dựng đường dẫn tuyệt đối tới file JSONL đầu vào và file lưu chunk đầu ra
# #     jsonl_file = ROOT_DIR / "processed_data" / "CSLT_Ch2_2122" / "blocks.jsonl"
# #     output_chunk_file = ROOT_DIR / "processed_data" / "CSLT_Ch2_2122" / "final_chunks.jsonl"
# #
# #     # 3. Bắt lỗi thân thiện nếu chưa có file
# #     if not jsonl_file.exists():
# #         print(f"[LỖI] Không tìm thấy file tại: {jsonl_file}")
# #         print("Vui lòng đảm bảo bạn đã chạy script read_pdf.py thành công cho file CSLT.pdf.")
# #     else:
# #         # Thực thi
# #         grouped_data = load_and_group_blocks(jsonl_file)
# #         final_chunks = create_langchain_documents(grouped_data)
# #
# #         # [MỚI] Lưu dữ liệu vào file
# #         save_chunks_to_jsonl(final_chunks, output_chunk_file)
# #
# #         print(f"[OK] Tổng số chunk được tạo ra: {len(final_chunks)}")
# #         print(f"[OK] Đã lưu các chunk thành công vào: {output_chunk_file}\n")
# #
# #         for i in range(min(2, len(final_chunks))):
# #             print(f"--- Chunk {i + 1} ---")
# #             print(f"Metadata: {final_chunks[i].metadata}")
# #             print(f"Nội dung:\n{final_chunks[i].page_content[:200]}...\n")


import json
import re
from pathlib import Path
from typing import List, Dict, Any
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter


def group_blocks_from_memory(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    grouped_sections = {}

    for block in records:
        if block['block_type'] == 'heading':
            continue

        # Nối mảng heading_path thành một chuỗi chủ đề thống nhất
        path_key = " > ".join(block['heading_path']) if block.get('heading_path') else "General"

        if path_key not in grouped_sections:
            grouped_sections[path_key] = {
                "text": "",
                "metadata": {
                    "source": block['source_file'],
                    "topic_path": path_key,
                    "start_page": block['page_number']
                }
            }

        block_text = block['text']

        block_text = re.sub(r'(^|\n)đ (error|warning)', r'\1-> \2', block_text)

        # 2. Phục hồi thẻ Markdown nếu thuật toán nhận diện đây là Code
        if block.get('block_type') == 'code':
            block_text = f"```cpp\n{block_text}\n```"

        # Nối nội dung text đã được "trang điểm" vào chủ đề tương ứng
        grouped_sections[path_key]["text"] += block_text + "\n\n"
        # ==========================================

    return grouped_sections


def create_langchain_documents(grouped_sections: Dict[str, Any]) -> List[Document]:
    """Chuyển đổi dữ liệu đã gộp thành LangChain Documents và cắt nhỏ nếu cần."""
    # Cấu hình bộ cắt đệ quy: Giới hạn 800 ký tự, phần giao nhau 100 ký tự
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=100,
        separators=["\n\n", "\n", ".", " ", ""]
    )

    documents = []
    for path_key, data in grouped_sections.items():
        # Bỏ qua các mục trống
        if not data["text"].strip():
            continue

        doc = Document(page_content=data["text"].strip(), metadata=data["metadata"])

        # Split_documents sẽ tự động chia nhỏ doc nếu vượt quá chunk_size
        # và TỰ ĐỘNG copy nguyên metadata cho các chunk con.
        splits = text_splitter.split_documents([doc])
        documents.extend(splits)

    return documents


def save_chunks_to_jsonl(chunks: List[Document], output_path: Path):
    """(Tùy chọn) Lưu danh sách LangChain Documents vào file JSONL để debug hoặc sao lưu."""
    # Đảm bảo thư mục cha tồn tại
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        for chunk in chunks:
            # Chuyển object Document thành dictionary để dễ lưu trữ
            chunk_dict = {
                "page_content": chunk.page_content,
                "metadata": chunk.metadata
            }
            # Ghi từng chunk thành một dòng JSON độc lập
            f.write(json.dumps(chunk_dict, ensure_ascii=False) + "\n")
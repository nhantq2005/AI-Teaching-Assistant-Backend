# import os
# import warnings
#
# os.environ["HF_HOME"] = "D:/AI_teaching_assistant/huggingface_cache"
# os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"
# os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "max_split_size_mb:128"
#
# warnings.filterwarnings("ignore", category=DeprecationWarning)
#
# import torch
# from langchain_text_splitters import RecursiveCharacterTextSplitter
#
# DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
#
# print(f"Using device: {DEVICE}")
#
# if DEVICE == "cuda":
#     print(f"GPU name: {torch.cuda.get_device_name(0)}")
#
# text_splitter = RecursiveCharacterTextSplitter(
#     chunk_size=700,
#     chunk_overlap=100,
#     separators=[
#         "\n\n",
#         "\n",
#         ". ",
#         "! ",
#         "? ",
#         "; ",
#         ", ",
#         " ",
#         ""
#     ],
# )
#
#
# def chunking(text: str):
#     chunks = text_splitter.split_text(text)
#
#     # Xóa chunk rỗng
#     chunks = [chunk.strip() for chunk in chunks if chunk.strip()]
#
#     return chunks
#
#
# if __name__ == "__main__":
#     text = """
# Cây nhị phân tìm kiếm, hay Binary Search Tree, là một cấu trúc dữ liệu dạng cây trong đó mỗi nút có tối đa hai nút con.
# Với mỗi nút, các giá trị nhỏ hơn nút hiện tại sẽ nằm ở cây con bên trái, còn các giá trị lớn hơn sẽ nằm ở cây con bên phải.
# Nhờ tính chất này, thao tác tìm kiếm, thêm và xóa phần tử có thể đạt độ phức tạp trung bình O(log n) nếu cây được cân bằng.
# Tuy nhiên, nếu dữ liệu được thêm vào theo thứ tự tăng dần hoặc giảm dần, cây có thể bị lệch và hiệu năng tìm kiếm giảm xuống O(n).
#
# Trong lập trình hướng đối tượng, bốn tính chất quan trọng gồm đóng gói, kế thừa, đa hình và trừu tượng.
# Đóng gói giúp che giấu dữ liệu bên trong đối tượng và chỉ cho phép truy cập thông qua các phương thức được định nghĩa.
# Kế thừa cho phép một lớp con tái sử dụng thuộc tính và hành vi của lớp cha, giúp giảm lặp lại mã nguồn.
# Đa hình cho phép cùng một phương thức có thể có cách thực thi khác nhau tùy vào đối tượng cụ thể.
# Trừu tượng giúp lập trình viên tập trung vào chức năng chính mà không cần quan tâm quá nhiều đến chi tiết cài đặt bên trong.
#
# Hệ điều hành là phần mềm trung gian giữa phần cứng máy tính và các chương trình ứng dụng.
# Một trong những nhiệm vụ quan trọng của hệ điều hành là quản lý tiến trình.
# Mỗi tiến trình đại diện cho một chương trình đang chạy và có không gian bộ nhớ, trạng thái CPU cùng các tài nguyên riêng.
# Bộ lập lịch tiến trình quyết định tiến trình nào được cấp CPU tại một thời điểm nhằm tối ưu hiệu suất và đảm bảo tính công bằng.
#
# Quản lý bộ nhớ là một chức năng quan trọng khác của hệ điều hành.
# Cơ chế bộ nhớ ảo cho phép chương trình sử dụng không gian địa chỉ lớn hơn dung lượng RAM vật lý.
# Kỹ thuật phân trang chia bộ nhớ thành các trang có kích thước cố định để dễ quản lý.
# Khi một trang dữ liệu chưa có trong RAM, hệ điều hành sẽ phát sinh lỗi trang và nạp dữ liệu từ bộ nhớ phụ vào RAM.
#
# Trong cơ sở dữ liệu quan hệ, chuẩn hóa là quá trình tổ chức dữ liệu nhằm giảm dư thừa và tránh bất thường khi thêm, sửa hoặc xóa dữ liệu.
# Dạng chuẩn thứ nhất yêu cầu mỗi ô dữ liệu chỉ chứa một giá trị nguyên tử.
# Dạng chuẩn thứ hai yêu cầu bảng phải đạt chuẩn một và các thuộc tính không khóa phải phụ thuộc đầy đủ vào khóa chính.
# Dạng chuẩn thứ ba yêu cầu không tồn tại phụ thuộc bắc cầu giữa các thuộc tính không khóa.
# Chuẩn hóa giúp dữ liệu nhất quán hơn, nhưng trong một số hệ thống cần tốc độ truy vấn cao, người ta có thể phi chuẩn hóa để giảm số lượng phép nối bảng.
#
# Mô hình TCP/IP là nền tảng của mạng Internet và gồm bốn tầng chính: tầng truy cập mạng, tầng Internet, tầng giao vận và tầng ứng dụng.
# Giao thức IP chịu trách nhiệm định tuyến gói tin giữa các mạng khác nhau.
# TCP cung cấp cơ chế truyền dữ liệu tin cậy thông qua đánh số thứ tự, xác nhận ACK và truyền lại khi xảy ra lỗi.
# Ngược lại, UDP không đảm bảo độ tin cậy nhưng có độ trễ thấp, phù hợp với các ứng dụng thời gian thực như gọi video, chơi game trực tuyến hoặc truyền phát trực tiếp.
#
# Độ phức tạp thuật toán được dùng để đánh giá lượng tài nguyên mà thuật toán cần sử dụng khi kích thước đầu vào tăng lên.
# Ký hiệu Big O mô tả tốc độ tăng của thời gian chạy hoặc bộ nhớ theo kích thước dữ liệu.
# Ví dụ, tìm kiếm tuyến tính có độ phức tạp O(n) vì trong trường hợp xấu nhất phải duyệt qua toàn bộ danh sách.
# Trong khi đó, tìm kiếm nhị phân trên mảng đã sắp xếp có độ phức tạp O(log n) vì mỗi bước loại bỏ được một nửa không gian tìm kiếm.
# Việc lựa chọn thuật toán và cấu trúc dữ liệu phù hợp có ảnh hưởng lớn đến hiệu năng của hệ thống, đặc biệt khi xử lý dữ liệu lớn.
# """
#
#     chunks = chunking(text)
#
#     for i, chunk in enumerate(chunks, 1):
#         print(f"Chunk {i}")
#         print(chunk)
#         print("=" * 50)


import os
import re
import warnings
from dataclasses import dataclass, asdict
from typing import Any, Dict, List, Optional

os.environ["HF_HOME"] = "D:/AI_teaching_assistant/huggingface_cache"
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"
os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "max_split_size_mb:128"

warnings.filterwarnings("ignore", category=DeprecationWarning)

from langchain_text_splitters import RecursiveCharacterTextSplitter


DEFAULT_CHUNK_SIZE = 800
DEFAULT_CHUNK_OVERLAP = 100

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=DEFAULT_CHUNK_SIZE,
    chunk_overlap=DEFAULT_CHUNK_OVERLAP,
    separators=[
        "\n\n",
        "\n",
        ". ",
        "! ",
        "? ",
        "; ",
        ", ",
        " ",
        "",
    ],
)


@dataclass
class Chunk:
    content: str
    chunk_index: int
    source_type: str
    metadata: Dict[str, Any]


def clean_text(text: str) -> str:
    if not text:
        return ""

    text = text.replace("\x00", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def split_long_text(text: str) -> List[str]:
    text = clean_text(text)

    if not text:
        return []

    chunks = text_splitter.split_text(text)
    return [chunk.strip() for chunk in chunks if chunk.strip()]


def make_chunk(
    content: str,
    chunk_index: int,
    source_type: str,
    base_metadata: Optional[Dict[str, Any]] = None,
    extra_metadata: Optional[Dict[str, Any]] = None,
) -> Chunk:
    metadata = dict(base_metadata or {})
    metadata.update(extra_metadata or {})

    return Chunk(
        content=content.strip(),
        chunk_index=chunk_index,
        source_type=source_type,
        metadata=metadata,
    )


def chunk_plain_text(
    text: str,
    base_metadata: Optional[Dict[str, Any]] = None,
) -> List[Dict[str, Any]]:
    chunks: List[Chunk] = []

    for part in split_long_text(text):
        chunks.append(
            make_chunk(
                content=part,
                chunk_index=len(chunks),
                source_type="text",
                base_metadata=base_metadata,
            )
        )

    return [asdict(chunk) for chunk in chunks]


def chunk_pdf_pages(
    pages: List[Dict[str, Any]],
    base_metadata: Optional[Dict[str, Any]] = None,
) -> List[Dict[str, Any]]:
    chunks: List[Chunk] = []

    for page in pages:
        page_number = page.get("page_number")
        page_text = clean_text(page.get("text", ""))

        if not page_text:
            continue

        page_parts = split_long_text(page_text)

        for local_index, part in enumerate(page_parts):
            chunks.append(
                make_chunk(
                    content=part,
                    chunk_index=len(chunks),
                    source_type="pdf",
                    base_metadata=base_metadata,
                    extra_metadata={
                        "page_number": page_number,
                        "page_chunk_index": local_index,
                    },
                )
            )

    return [asdict(chunk) for chunk in chunks]


def chunk_docx_sections(
    sections: List[Dict[str, Any]],
    base_metadata: Optional[Dict[str, Any]] = None,
) -> List[Dict[str, Any]]:
    chunks: List[Chunk] = []

    for section in sections:
        section_title = clean_text(section.get("section_title", ""))
        section_text = clean_text(section.get("text", ""))

        if not section_text:
            continue

        full_text = f"{section_title}\n{section_text}" if section_title else section_text
        section_parts = split_long_text(full_text)

        for local_index, part in enumerate(section_parts):
            chunks.append(
                make_chunk(
                    content=part,
                    chunk_index=len(chunks),
                    source_type="docx",
                    base_metadata=base_metadata,
                    extra_metadata={
                        "section_title": section_title,
                        "section_chunk_index": local_index,
                    },
                )
            )

    return [asdict(chunk) for chunk in chunks]


def chunk_pptx_slides(
    slides: List[Dict[str, Any]],
    base_metadata: Optional[Dict[str, Any]] = None,
) -> List[Dict[str, Any]]:
    chunks: List[Chunk] = []

    for slide in slides:
        slide_number = slide.get("slide_number")
        slide_title = clean_text(slide.get("slide_title", ""))
        slide_text = clean_text(slide.get("text", ""))

        if not slide_text and not slide_title:
            continue

        full_text = f"{slide_title}\n{slide_text}" if slide_title else slide_text
        slide_parts = split_long_text(full_text)

        for local_index, part in enumerate(slide_parts):
            chunks.append(
                make_chunk(
                    content=part,
                    chunk_index=len(chunks),
                    source_type="pptx",
                    base_metadata=base_metadata,
                    extra_metadata={
                        "slide_number": slide_number,
                        "slide_title": slide_title,
                        "slide_chunk_index": local_index,
                    },
                )
            )

    return [asdict(chunk) for chunk in chunks]


def chunk_document(
    document_type: str,
    data: Any,
    base_metadata: Optional[Dict[str, Any]] = None,
) -> List[Dict[str, Any]]:
    document_type = document_type.lower().strip()

    if document_type == "pdf":
        return chunk_pdf_pages(data, base_metadata)

    if document_type == "docx":
        return chunk_docx_sections(data, base_metadata)

    if document_type == "pptx":
        return chunk_pptx_slides(data, base_metadata)

    if document_type == "text":
        return chunk_plain_text(data, base_metadata)

    raise ValueError(f"Unsupported document_type: {document_type}")
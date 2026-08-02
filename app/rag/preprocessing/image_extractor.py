import os
from pathlib import Path

import google.generativeai as genai
from PIL import Image


PROMPT = """
        Bạn là chuyên gia phân tích hình ảnh phục vụ hệ thống RAG.
        
        Hãy xử lý hình ảnh và trả về đúng cấu trúc sau:
        
        Loại ảnh:
        [Xác định loại: Flowchart, Diagram, Table, Code, Formula, Slide Figure hoặc Other]
        
        Văn bản trích xuất:
        [Trích xuất chính xác nội dung nhìn thấy trong ảnh]
        
        Mô tả phục vụ RAG:
        [Mô tả chủ đề, thành phần, mối quan hệ hoặc luồng hoạt động trong ảnh]
        
        Từ khóa:
        - [Từ khóa 1]
        - [Từ khóa 2]
        - [Từ khóa khác]
        
        Yêu cầu:
        - Không bịa đặt nội dung.
        - Giữ nguyên thuật ngữ chuyên ngành.
        - Với lưu đồ, mô tả thứ tự và điều kiện rẽ nhánh.
        - Với bảng, trình bày bằng Markdown table.
        - Với code, giữ nguyên cấu trúc và thụt lề.
        """.strip()


def extract_image_gemini(image_path: str | Path) -> str:
    path = Path(image_path)

    if not path.is_file():
        raise FileNotFoundError(f"Không tìm thấy ảnh: {path}")

    api_key = os.getenv("")
    if not api_key:
        raise RuntimeError(
            "Chưa cấu hình GEMINI_API_KEY trong biến môi trường."
        )

    genai.configure(api_key=api_key)

    model_name = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
    model = genai.GenerativeModel(model_name)

    try:
        with Image.open(path) as image:
            response = model.generate_content([PROMPT, image])
    except Exception as exc:
        raise RuntimeError(
            f"Lỗi khi Gemini xử lý ảnh {path.name}: {exc}"
        ) from exc

    result = getattr(response, "text", None)

    if not result or not result.strip():
        raise RuntimeError(
            f"Gemini không trả về nội dung cho ảnh {path.name}."
        )

    return result.strip()


# Giữ tương thích với main_pipeline.py cũ
def extract_flowchart_gemini(image_path: str | Path) -> str:
    return extract_image_gemini(image_path)
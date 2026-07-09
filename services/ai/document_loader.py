import fitz  # Import thư viện PyMuPDF


def doc_pdf_tieng_viet(file_path):
    # Mở tài liệu PDF
    doc = fitz.open(file_path)

    toan_bo_van_ban = ""

    # Duyệt qua từng trang và trích xuất chữ
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        # Lấy text, mặc định PyMuPDF xử lý UTF-8 rất tốt
        text = page.get_text()
        toan_bo_van_ban += f"--- Trang {page_num + 1} ---\n{text}\n"

    return toan_bo_van_ban


# Sử dụng
if __name__=="__main__":
    file_pdf = "D:\AI_teaching_assistant\data\CSLT_Ch1_2122.pdf"
    van_ban = doc_pdf_tieng_viet(file_pdf)
    print(van_ban)
import os
import warnings

# =====================================================================
# BẮT BUỘC: Cấu hình môi trường phải đặt ở ĐẦU FILE (Trước khi import thư viện AI)
# =====================================================================
os.environ["HF_HOME"] = "D:/AI_teaching_assistant/huggingface_cache"
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"
warnings.filterwarnings("ignore", category=DeprecationWarning)

from langchain_experimental.text_splitter import SemanticChunker
from langchain_huggingface import HuggingFaceEmbeddings


def semantic_chunking(text):
    # Thêm tham số cache_folder để chắc chắn model được tải về ổ D
    embedding = HuggingFaceEmbeddings(
        model_name="AITeamVN/Vietnamese_Embedding",
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True},
        cache_folder="D:/AI_teaching_assistant/huggingface_cache"
    )

    text_splitter = SemanticChunker(
        embeddings=embedding,
        breakpoint_threshold_type="percentile",
        breakpoint_threshold_amount=95
    )

    chunks = text_splitter.create_documents([text])

    return [chunk.page_content for chunk in chunks]


if __name__ == "__main__":
    text = """Cây nhị phân tìm kiếm (Binary Search Tree - BST) là một cấu trúc dữ liệu dạng cây, trong đó mỗi nút có tối đa hai nút con: nút con trái và nút con phải. Đặc điểm quan trọng của BST là mọi giá trị trong cây con trái của một nút đều nhỏ hơn giá trị của nút đó, trong khi mọi giá trị trong cây con phải đều lớn hơn. Nhờ tính chất này, các thao tác tìm kiếm, chèn và xóa có thể được thực hiện với độ phức tạp trung bình là O(log n) nếu cây được cân bằng.
                Khi thực hiện thao tác tìm kiếm trên BST, thuật toán bắt đầu từ nút gốc. Nếu giá trị cần tìm nhỏ hơn giá trị của nút hiện tại, thuật toán tiếp tục tìm trong cây con trái. Ngược lại, nếu giá trị lớn hơn, thuật toán sẽ chuyển sang cây con phải. Quá trình này lặp lại cho đến khi tìm thấy giá trị hoặc gặp nút rỗng. Tuy nhiên, nếu cây bị mất cân bằng và trở thành một danh sách liên kết, độ phức tạp của thao tác tìm kiếm có thể tăng lên O(n).
                Trong lập trình hướng đối tượng (Object-Oriented Programming - OOP), bốn tính chất cơ bản bao gồm đóng gói (Encapsulation), kế thừa (Inheritance), đa hình (Polymorphism) và trừu tượng (Abstraction). Đóng gói giúp bảo vệ dữ liệu bằng cách giới hạn quyền truy cập thông qua các phương thức. Kế thừa cho phép một lớp mới tái sử dụng các thuộc tính và phương thức của lớp cha. Đa hình giúp cùng một lời gọi phương thức có thể tạo ra các hành vi khác nhau tùy thuộc vào đối tượng thực thi. Trừu tượng giúp người lập trình tập trung vào các chức năng cần thiết mà không phải quan tâm đến chi tiết cài đặt bên trong.
                Hệ điều hành (Operating System - OS) đóng vai trò là phần mềm trung gian giữa phần cứng và các chương trình ứng dụng. Một trong những chức năng quan trọng của hệ điều hành là quản lý tiến trình. Mỗi tiến trình đại diện cho một chương trình đang thực thi và có không gian bộ nhớ, thanh ghi CPU cùng các tài nguyên riêng. Bộ lập lịch (Scheduler) quyết định tiến trình nào được cấp CPU tại từng thời điểm nhằm tối ưu hiệu suất và đảm bảo tính công bằng giữa các tiến trình.
                Quản lý bộ nhớ là một nhiệm vụ quan trọng khác của hệ điều hành. Cơ chế bộ nhớ ảo (Virtual Memory) cho phép mỗi tiến trình sử dụng không gian địa chỉ lớn hơn dung lượng RAM vật lý thông qua kỹ thuật phân trang (Paging). Khi một trang dữ liệu chưa có trong RAM, hệ điều hành sẽ phát sinh lỗi trang (Page Fault), sau đó nạp dữ liệu từ bộ nhớ phụ vào RAM trước khi tiếp tục thực thi chương trình.
                Trong môn Cơ sở dữ liệu (Database), chuẩn hóa dữ liệu (Normalization) là quá trình tổ chức các bảng nhằm giảm sự dư thừa và tránh các bất thường khi cập nhật dữ liệu. Các dạng chuẩn phổ biến bao gồm 1NF, 2NF và 3NF. Việc chuẩn hóa giúp dữ liệu nhất quán hơn, tuy nhiên trong một số hệ thống yêu cầu tốc độ truy vấn cao, người ta có thể áp dụng phi chuẩn hóa (Denormalization) để giảm số lượng phép JOIN giữa các bảng.
                Đối với môn Mạng máy tính (Computer Networks), mô hình TCP/IP gồm bốn tầng chính: tầng truy cập mạng, tầng Internet, tầng giao vận và tầng ứng dụng. Giao thức IP chịu trách nhiệm định tuyến gói tin giữa các mạng khác nhau, trong khi TCP đảm bảo dữ liệu được truyền tin cậy thông qua cơ chế đánh số thứ tự, xác nhận (ACK) và truyền lại khi xảy ra lỗi. Ngược lại, UDP không đảm bảo độ tin cậy nhưng có độ trễ thấp, phù hợp với các ứng dụng thời gian thực như gọi video hoặc truyền phát trực tuyến.
                Độ phức tạp thuật toán là một kiến thức nền tảng trong môn Giải thuật và Cấu trúc dữ liệu. Ký hiệu Big O được sử dụng để mô tả tốc độ tăng của thời gian thực thi hoặc lượng bộ nhớ sử dụng khi kích thước dữ liệu đầu vào tăng lên. Ví dụ, thuật toán tìm kiếm tuyến tính có độ phức tạp O(n), trong khi tìm kiếm nhị phân trên mảng đã được sắp xếp có độ phức tạp O(log n). Việc lựa chọn thuật toán và cấu trúc dữ liệu phù hợp có ảnh hưởng rất lớn đến hiệu năng của hệ thống, đặc biệt khi xử lý tập dữ liệu lớn."""

    chunks = semantic_chunking(text)

    for i, chunk in enumerate(chunks, 1):
        print(f"Chunk {i}")
        print(chunk)
        print("=" * 50)
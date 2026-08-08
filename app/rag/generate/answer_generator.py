import os
from pathlib import Path
from dotenv import load_dotenv
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
import os
from dotenv import load_dotenv

from app.rag.generate.hybrid_retriever import get_hybrid_reranked_retriever

load_dotenv()


def format_docs(docs):
    """Hàm gộp nội dung các chunk lại thành một chuỗi văn bản để đưa vào Prompt."""
    formatted_str = ""
    for i, doc in enumerate(docs):
        # Trích xuất metadata để LLM biết nguồn gốc tài liệu
        source = doc.metadata.get("source", "Không rõ")
        page = doc.metadata.get("start_page", "Không rõ")
        topic = doc.metadata.get("topic_path", "Không rõ")

        formatted_str += f"[Tài liệu {i + 1} | Nguồn: {source} | Trang: {page} | Chủ đề: {topic}]\n{doc.page_content}\n\n"
    return formatted_str


def get_rag_chain():
    """Khởi tạo luồng RAG (Retrieval-Augmented Generation)."""
    # 1. Tự động xác định đường dẫn thư mục database
    retriever = get_hybrid_reranked_retriever(top_k=3)

    llm = ChatGoogleGenerativeAI(
        model="gemini-3.5-flash",
        temperature=0.2
    )

    # 5. Xây dựng Kịch bản trợ giảng (Prompt Template)
    # template = """Bạn là một Trợ giảng AI chuyên ngành Công nghệ thông tin.
    #             Nhiệm vụ của bạn là giải đáp thắc mắc của sinh viên một cách chi tiết, dễ hiểu và sư phạm.
    #
    #             HÃY TUÂN THỦ NGHIÊM NGẶT CÁC QUY TẮC SAU:
    #             1. Dựa TRỰC TIẾP vào các đoạn tài liệu (Context) được cung cấp bên dưới để trả lời.
    #             2. Nếu Context không chứa thông tin để trả lời câu hỏi, hãy nói: "Xin lỗi, hiện tại tài liệu môn học chưa đề cập đến vấn đề này, bạn có thể làm rõ hơn câu hỏi được không?". TUYỆT ĐỐI KHÔNG tự bịa ra câu trả lời.
    #             3. Luôn định dạng code bằng Markdown rõ ràng.
    #             4. Trích dẫn tên tài liệu và số trang (nếu có) để sinh viên tiện tra cứu.
    #
    #             NGỮ CẢNH (CONTEXT):
    #             {context}
    #
    #             CÂU HỎI CỦA SINH VIÊN:
    #             {question}
    #
    #             CÂU TRẢ LỜI CỦA TRỢ GIẢNG:
    #             """

    template = """Bạn là một Trợ giảng AI chuyên ngành Công nghệ thông tin. 
                Nhiệm vụ của bạn là giải đáp thắc mắc của sinh viên một cách chi tiết, dễ hiểu, mang tính sư phạm và khơi gợi tư duy.
            
                HÃY TUÂN THỦ NGHIÊM NGẶT CÁC QUY TẮC SAU:
                1. Dựa TRỰC TIẾP vào các đoạn tài liệu (Context) được cung cấp bên dưới để trả lời.
                2. Nếu Context KHÔNG chứa thông tin để trả lời, hãy nói: "Xin lỗi, hiện tại tài liệu môn học chưa đề cập đến vấn đề này, bạn có thể làm rõ hơn câu hỏi được không?". TUYỆT ĐỐI KHÔNG tự bịa ra thông tin không có trong Context.
                3. Nếu Context chỉ chứa một phần câu trả lời, hãy giải đáp phần đó và nói rõ tài liệu chưa cung cấp đủ thông tin cho phần còn lại.
                4. Luôn định dạng code (nếu có) bằng Markdown rõ ràng.
                5. Cuối mỗi ý hoặc câu trả lời, PHẢI trích dẫn nguồn theo định dạng: [Tên tài liệu - Trang X] để sinh viên tiện tra cứu.
            
                NGỮ CẢNH (CONTEXT):
                {context}
            
                CÂU HỎI CỦA SINH VIÊN:
                {question}
            
                CÂU TRẢ LỜI CỦA TRỢ GIẢNG:
                """

    prompt = PromptTemplate.from_template(template)

    # 6. Xâu chuỗi quy trình (LangChain LCEL)
    rag_chain = (
            {"context": retriever | format_docs, "question": RunnablePassthrough()}
            | prompt
            | llm
            | StrOutputParser()
    )

    return rag_chain

def stream_answer(query: str):
    """Hàm hỗ trợ gọi stream để trả về từng chunk cho API"""
    rag_chain = get_rag_chain()
    for chunk in rag_chain.stream(query):
        yield chunk

if __name__ == "__main__":
    # Đảm bảo bạn đã có biến môi trường GOOGLE_API_KEY
    if not os.environ.get("GOOGLE_API_KEY"):
        print("[LỖI] Thiếu GOOGLE_API_KEY.")
        print("Vui lòng gõ lệnh: export GOOGLE_API_KEY='api_key_cua_ban' trước khi chạy script.")
        exit()

    print("[*] Đang khởi tạo Trợ giảng AI...")
    rag_chain = get_rag_chain()
    print("[OK] Trợ giảng đã sẵn sàng!\n")

    # Vòng lặp chat tương tác trên terminal
    print("=" * 50)
    print("NHẬP CÂU HỎI ĐỂ CHAT VỚI AI (Gõ 'exit' hoặc 'quit' để thoát)")
    print("=" * 50)

    while True:
        user_query = input("\nSinh viên: ")
        if user_query.lower() in ['exit', 'quit']:
            break

        print("Trợ giảng AI: ", end="", flush=True)

        # Stream câu trả lời để tạo hiệu ứng gõ phím theo thời gian thực
        for chunk in rag_chain.stream(user_query):
            print(chunk, end="", flush=True)
        print()

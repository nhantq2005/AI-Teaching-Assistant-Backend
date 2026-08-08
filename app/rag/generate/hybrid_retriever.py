import pickle
from pathlib import Path

from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_classic.retrievers import EnsembleRetriever
from langchain_classic.retrievers import ContextualCompressionRetriever
from langchain_classic.retrievers.document_compressors import CrossEncoderReranker
from langchain_community.cross_encoders import HuggingFaceCrossEncoder


def get_hybrid_reranked_retriever(top_k: int = 3):
    """
    Khởi tạo bộ máy tìm kiếm Hybrid (BM25 + BGE-M3) tích hợp Re-ranker.
    """
    # 1. Định vị đường dẫn
    CURRENT_FILE = Path(__file__).resolve()
    ROOT_DIR = CURRENT_FILE.parents[3] if len(CURRENT_FILE.parents) > 3 else CURRENT_FILE.parent
    chroma_db_dir = ROOT_DIR / "chroma_db"
    bm25_save_path = ROOT_DIR / "bm25_index.pkl"

    # 2. Khởi tạo Dense Retriever (Chroma + BGE-M3)
    embeddings = HuggingFaceEmbeddings(
        model_name="BAAI/bge-m3",
        model_kwargs={'device': 'cpu'},
        encode_kwargs={'normalize_embeddings': True}
    )
    vectorstore = Chroma(
        persist_directory=str(chroma_db_dir),
        embedding_function=embeddings,
        collection_name="cslt_collection"
    )
    # Lấy nhiều kết quả hơn (gấp đôi) để tạo phễu lọc cho Re-ranker
    chroma_retriever = vectorstore.as_retriever(search_kwargs={"k": top_k * 2})

    # 3. Khởi tạo Sparse Retriever (BM25)
    if not bm25_save_path.exists():
        raise FileNotFoundError(f"Chưa tìm thấy BM25 index tại: {bm25_save_path}. Hãy chạy script build trước.")

    with open(bm25_save_path, 'rb') as f:
        bm25_retriever = pickle.load(f)
    bm25_retriever.k = top_k * 2

    # 4. Gộp thành Ensemble Retriever (Cân bằng trọng số 50/50)
    ensemble_retriever = EnsembleRetriever(
        retrievers=[bm25_retriever, chroma_retriever],
        weights=[0.5, 0.5]
    )

    # 5. Khởi tạo Re-ranker (Cross-Encoder)
    cross_encoder = HuggingFaceCrossEncoder(model_name="BAAI/bge-reranker-v2-m3")

    # Cấu hình bộ nén: Chấm điểm và chỉ giữ lại số lượng tài liệu đúng bằng top_k
    compressor = CrossEncoderReranker(model=cross_encoder, top_n=top_k)

    # 6. Bọc bộ tìm kiếm tổng hợp qua lớp Nén (Compression)
    compression_retriever = ContextualCompressionRetriever(
        base_compressor=compressor,
        base_retriever=ensemble_retriever
    )

    return compression_retriever
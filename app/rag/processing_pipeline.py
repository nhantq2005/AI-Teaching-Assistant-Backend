from app.rag.chunking.chunking_data import group_blocks_from_memory, create_langchain_documents
from app.rag.embedding.embedding_data import embed_and_save_to_chroma
from app.rag.preprocessing.read_pdf import extract_pdf
from app.rag.embedding.bm25_index import update_bm25_index # (Tùy theo nơi bạn đặt file)
from app.models.document import ProcessingStatus
from app.services.document_service import DocumentService

async def process_document_pipeline(document_id: int, file_bytes: bytes, file_name: str, session):
    try:
        # 1. Đọc dữ liệu từ RAM -> List[Dict]
        records = extract_pdf(file_bytes, file_name)

        # 2. Gom nhóm và Chunking -> List[Document]
        grouped_data = group_blocks_from_memory(records)
        final_chunks = create_langchain_documents(grouped_data)

        # 3. Đẩy vào Vector DB (ChromaDB)
        embed_and_save_to_chroma(final_chunks, collection_name="cslt_collection")

        # 4. Cập nhật BM25 Index
        update_bm25_index(final_chunks)

        # 5. Cập nhật trạng thái trong Database
        document_service = DocumentService(session)
        db_document = await document_service.get_document_by_id(document_id)
        if db_document:
            db_document.process_status = ProcessingStatus.COMPLETED
            await session.commit()

    except Exception as e:
        print(f"[LỖI PIPELINE] Document {document_id}: {str(e)}")
        document_service = DocumentService(session)
        db_document = await document_service.get_document_by_id(document_id)
        if db_document:
            db_document.process_status = ProcessingStatus.FAILED
            await session.commit()
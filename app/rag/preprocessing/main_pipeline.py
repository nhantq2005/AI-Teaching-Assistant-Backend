import argparse
import json
import logging
from pathlib import Path
from uuid import uuid4

from app.rag.preprocessing.extracted_image import describe_image
from app.rag.preprocessing.read_data import PDFReader
from app.schemas.document_block import BlockType

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def process_document_pipeline(
    pdf_path: Path,
    output_json: Path,
    image_dir: Path,
    annotated_dir: Path,
    ollama_url: str,
    model: str,
) -> None:
    logger.info("Bắt đầu xử lý file PDF: %s", pdf_path.name)

    image_dir.mkdir(parents=True, exist_ok=True)
    annotated_dir.mkdir(parents=True, exist_ok=True)

    reader = PDFReader()
    try:
        blocks = reader.extract_pdf(
            file_path=pdf_path,
            document_id=uuid4(),
            image_dir=image_dir,
            annotated_dir=annotated_dir,
        )
    except Exception as exc:
        logger.exception("Lỗi khi trích xuất PDF: %s", exc)
        return

    logger.info("Đã trích xuất %d block từ PDF.", len(blocks))

    for block in blocks:
        if block.block_type != BlockType.IMAGE:
            continue

        image_path_value = block.metadata.get("image_path")
        if image_path_value:
            image_path = Path(image_path_value)
        else:
            image_path = image_dir / str(block.metadata.get("file_name", ""))

        if not image_path.is_file():
            message = f"Không tìm thấy file ảnh vật lý: {image_path}"
            logger.warning(message)
            block.metadata["vlm_error"] = message
            continue

        try:
            logger.info("Đang phân tích ảnh: %s", image_path.name)
            vlm_text, quality_issues = describe_image(
                ollama_url=ollama_url,
                model=model,
                image_path=image_path,
                max_retries=3,
                timeout=180.0,
                strict_format=False,
            )
            block.content = vlm_text
            block.metadata["vlm_processed"] = True
            block.metadata["quality_issues"] = quality_issues
        except Exception as exc:
            logger.exception("Lỗi VLM với ảnh %s: %s", image_path.name, exc)
            block.metadata["vlm_processed"] = False
            block.metadata["vlm_error"] = str(exc)

    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(
        json.dumps([block.to_dict() for block in blocks], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    non_empty = sum(bool(str(block.content).strip()) for block in blocks)
    logger.info(
        "Hoàn tất: %d/%d block có content. Kết quả: %s",
        non_empty,
        len(blocks),
        output_json,
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Trích xuất PDF và phân tích ảnh cho RAG.")
    parser.add_argument("pdf_path", type=Path)
    parser.add_argument("--output", type=Path, default=Path("outputs/rag_data.json"))
    parser.add_argument("--image-dir", type=Path, default=Path("outputs/extracted_images"))
    parser.add_argument("--annotated-dir", type=Path, default=Path("outputs/annotated_slides"))
    parser.add_argument("--ollama-url", default="http://localhost:11434")
    parser.add_argument("--model", default="qwen2.5vl:3b")
    args = parser.parse_args()

    if not args.pdf_path.is_file():
        parser.error(f"Không tìm thấy file: {args.pdf_path}")

    process_document_pipeline(
        pdf_path=args.pdf_path,
        output_json=args.output,
        image_dir=args.image_dir,
        annotated_dir=args.annotated_dir,
        ollama_url=args.ollama_url,
        model=args.model,
    )
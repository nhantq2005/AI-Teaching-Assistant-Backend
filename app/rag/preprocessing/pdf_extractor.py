import logging
import argparse
import json
import unicodedata
from pathlib import Path
from uuid import UUID, uuid4
import pymupdf
from app.schemas.document_block import BlockType, BoundingBox, DocumentBlock

# Cấu hình logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PDFExtractor:
    def extract(self, file_path: Path, document_id: UUID, image_dir: Path | None = None,
                annotated_dir: Path | None = None) -> list[DocumentBlock]:
        blocks: list[DocumentBlock] = []

        if not file_path.is_file():
            raise FileNotFoundError(f"Không tìm thấy file PDF: {file_path}")

        try:
            with pymupdf.open(file_path) as pdf:
                for page_index, page in enumerate(pdf):
                    page_number = page_index + 1

                    page_blocks = self._extract_page_blocks(
                        page=page,
                        document_id=document_id,
                        page_number=page_number,
                        image_dir=image_dir,
                        annotated_dir=annotated_dir,
                        source_file=file_path.name,
                    )
                    blocks.extend(page_blocks)

        except Exception as exc:
            logger.exception("Lỗi khi xử lý file PDF %s", file_path)
            raise RuntimeError(f"Không thể trích xuất PDF: {file_path}") from exc

        return blocks

    def _extract_page_blocks(
            self,
            page: pymupdf.Page,
            document_id: UUID,
            page_number: int,
            image_dir: Path | None = None,
            annotated_dir: Path | None = None,
            source_file: str | None = None,
    ) -> list[DocumentBlock]:
        page_dict = page.get_text("rawdict", sort=True)
        result: list[DocumentBlock] = []

        page_width = float(page.rect.width)
        page_height = float(page.rect.height)

        for block_index, raw_block in enumerate(page_dict.get("blocks", [])):
            raw_block_type = raw_block.get("type")

            # ---------------------------------------------------------
            # 1. TRÍCH XUẤT ĐỘC LẬP TỪNG ĐOẠN VĂN BẢN (PARAGRAPH)
            # ---------------------------------------------------------
            if raw_block_type == 0:
                text, _ = self._extract_text_and_style(raw_block)
                text = text.strip()

                if not text:
                    continue

                bbox = self._create_bbox(raw_block.get("bbox"))
                if bbox is None:
                    continue

                if self._is_header_footer_or_noise(text, bbox, page_height):
                    continue

                # Tạo block độc lập cho từng đoạn văn thay vì gộp chung
                result.append(
                    DocumentBlock(
                        id=uuid4(),
                        document_id=document_id,
                        page_number=page_number,
                        block_index=block_index,
                        block_type=BlockType.PARAGRAPH,
                        content=text,
                        bbox=bbox,
                        metadata={
                            "source": "pymupdf",
                            "source_file": source_file,
                            "page_width": page_width,
                            "page_height": page_height,
                        },
                    )
                )

            # ---------------------------------------------------------
            # 2. XỬ LÝ KHỐI HÌNH ẢNH & VẼ ĐÁNH DẤU
            # ---------------------------------------------------------
            elif raw_block_type == 1:
                bbox = self._create_bbox(raw_block.get("bbox"))
                if bbox is None:
                    continue

                block_id = uuid4()
                extension = raw_block.get("ext", "png")
                image_filename = f"{block_id}.{extension}"

                image_bytes = raw_block.get("image")
                if image_bytes and image_dir:
                    image_path = image_dir / image_filename
                    with open(image_path, "wb") as f:
                        f.write(image_bytes)

                rect = pymupdf.Rect(bbox.x0, bbox.y0, bbox.x1, bbox.y1)
                page.draw_rect(rect, color=(1, 0, 0), width=3)

                result.append(
                    DocumentBlock(
                        id=block_id,
                        document_id=document_id,
                        page_number=page_number,
                        block_index=block_index,
                        block_type=BlockType.IMAGE,
                        content="",
                        bbox=bbox,
                        metadata={
                            "source": "pymupdf",
                            "raw_block_type": raw_block_type,
                            "requires_caption": True,
                            "width": raw_block.get("width"),
                            "height": raw_block.get("height"),
                            "extension": extension,
                            "page_width": page_width,
                            "page_height": page_height,
                            "file_name": image_filename,
                            "source_file": source_file,
                        },
                    )
                )

        # Xuất ảnh slide đã đánh dấu
        if annotated_dir:
            annotated_slide_path = annotated_dir / f"slide_page_{page_number}.png"
            pix = page.get_pixmap(dpi=150)
            pix.save(str(annotated_slide_path))

        return result

    def _extract_text_and_style(self, raw_block: dict) -> tuple[str, dict]:
        lines: list[str] = []
        font_sizes: list[float] = []
        font_names: list[str] = []
        bold_count = 0
        span_count = 0

        for line in raw_block.get("lines", []):
            spans = line.get("spans", [])
            if not spans:
                continue

            line_text = self._join_spans(spans)
            if line_text.strip():
                lines.append(line_text.rstrip())

            for span in spans:
                span_count += 1
                font_sizes.append(float(span.get("size", 0.0)))
                font_names.append(str(span.get("font", "")))

                if self._is_bold_span(span):
                    bold_count += 1

        metadata = {
            "font_sizes": font_sizes,
            "font_names": list(dict.fromkeys(font_names)),
            "max_font_size": max(font_sizes) if font_sizes else 0.0,
            "average_font_size": sum(font_sizes) / len(font_sizes) if font_sizes else 0.0,
            "is_bold": (bold_count / span_count >= 0.5) if span_count else False,
        }

        return "\n".join(lines), metadata

    @staticmethod
    def _join_spans(spans: list[dict]) -> str:
        if not spans:
            return ""

        result = ""
        for span in spans:
            chars = span.get("chars", [])
            if not chars:
                continue

            font_size = float(span.get("size", 10.0))
            span_text = ""

            for i, char_data in enumerate(chars):
                char = char_data.get("c", "")

                if i > 0:
                    prev_bbox = chars[i - 1].get("bbox", [0, 0, 0, 0])
                    curr_bbox = char_data.get("bbox", [0, 0, 0, 0])

                    prev_x1 = prev_bbox[2]
                    curr_x0 = curr_bbox[0]
                    gap = curr_x0 - prev_x1

                    if gap > (font_size * 0.15) and not char.isspace() and not span_text[-1].isspace():
                        span_text += " "

                span_text += char

            span_text = unicodedata.normalize("NFC", span_text)

            if result:
                previous_char = result[-1]
                current_char = span_text[0]

                is_prev_word_char = previous_char.isalnum() or previous_char in ".,:;!?)%\"'"
                is_curr_word_char = current_char.isalnum() or current_char in "(\"'"

                should_add_space = (
                        not previous_char.isspace()
                        and not current_char.isspace()
                        and is_prev_word_char
                        and is_curr_word_char
                )

                if should_add_space:
                    result += " "

            result += span_text

        return result

    @staticmethod
    def _is_bold_span(span: dict) -> bool:
        font_name = str(span.get("font", "")).lower()
        return any(marker in font_name for marker in ("bold", "black", "semibold", "demibold"))

    @staticmethod
    def _create_bbox(bbox: tuple | list | None) -> BoundingBox | None:
        if not bbox or len(bbox) != 4:
            return None
        return BoundingBox(
            x0=float(bbox[0]), y0=float(bbox[1]), x1=float(bbox[2]), y1=float(bbox[3])
        )

    @staticmethod
    def _is_header_footer_or_noise(text: str, bbox: BoundingBox, page_height: float) -> bool:
        is_bottom_10_percent = bbox.y1 > (page_height * 0.9)
        if "CƠ SỞ LẬP TRÌNH" in text.upper():
            return True
        if is_bottom_10_percent and text.strip().isdigit():
            return True
        return False


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Trích xuất block văn bản và ảnh từ PDF"
    )

    parser.add_argument(
        "pdf_path",
        type=Path,
        nargs="?",
        default=None,
        help="Đường dẫn tới file PDF đầu vào",
    )

    parser.add_argument(
        "--output",
        type=Path,
        default=Path("ketqua.json"),
        help="File JSON đầu ra",
    )
    parser.add_argument(
        "--image-dir",
        type=Path,
        default=Path("extracted_images"),
        help="Directory for extracted images.",
    )
    parser.add_argument(
        "--annotated-dir",
        type=Path,
        default=Path("annotated_slides"),
        help="Directory for annotated page images.",
    )

    return parser.parse_args()


def resolve_pdf_path(pdf_path: Path | None) -> Path:
    if pdf_path is not None:
        return pdf_path

    preferred = Path("CSLT_Ch2_2122.pdf")
    if preferred.exists():
        return preferred

    pdf_files = sorted(Path.cwd().glob("*.pdf"))
    if pdf_files:
        return pdf_files[0]

    raise FileNotFoundError(
        "Không tìm thấy file PDF nào trong thư mục hiện tại"
    )


def save_blocks(blocks: list[DocumentBlock], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(
            [block.to_dict() for block in blocks],
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )


def main() -> None:
    args = parse_args()
    pdf_path = resolve_pdf_path(args.pdf_path)

    # 1. Thư mục chứa các mảnh ảnh nhỏ được cắt ra
    image_dir = args.image_dir
    image_dir.mkdir(parents=True, exist_ok=True)

    # 2. Thư mục chứa toàn bộ ảnh Slide đã được vẽ viền đỏ đánh dấu
    annotated_dir = args.annotated_dir
    annotated_dir.mkdir(parents=True, exist_ok=True)

    extractor = PDFExtractor()
    document_id = uuid4()

    blocks = extractor.extract(
        file_path=pdf_path,
        document_id=document_id,
        image_dir=image_dir,
        annotated_dir=annotated_dir,  # Kích hoạt tính năng xuất slide
    )

    save_blocks(blocks, args.output)

    logger.info(
        "Hoàn tất! Đã lưu %s block vào %s.\n- Ảnh cắt rời lưu tại: '%s'\n- Ảnh Slide đánh dấu lưu tại: '%s'",
        len(blocks),
        args.output,
        image_dir,
        annotated_dir
    )


if __name__ == "__main__":
    main()

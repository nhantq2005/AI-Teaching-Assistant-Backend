import json
import unicodedata
from pathlib import Path
from uuid import uuid4

import pymupdf

from app.schemas.document_block import BoundingBox, BlockType, DocumentBlock


class PDFReader:
    def extract_pdf(
        self,
        file_path: Path,
        document_id,
        image_dir: Path | None = None,
        annotated_dir: Path | None = None,
    ) -> list[DocumentBlock]:
        if not file_path.is_file():
            raise FileNotFoundError(f"File not found: {file_path}")

        if image_dir is not None:
            image_dir.mkdir(parents=True, exist_ok=True)
        if annotated_dir is not None:
            annotated_dir.mkdir(parents=True, exist_ok=True)

        blocks: list[DocumentBlock] = []
        try:
            with pymupdf.open(file_path) as pdf:
                for page_index, page in enumerate(pdf):
                    blocks.extend(
                        self.extract_page_blocks(
                            page=page,
                            document_id=document_id,
                            page_number=page_index + 1,
                            source_file=str(file_path),
                            image_dir=image_dir,
                            annotated_dir=annotated_dir,
                        )
                    )
        except Exception as exc:
            raise RuntimeError(f"Lỗi đọc PDF: {exc}") from exc

        return blocks

    def extract_page_blocks(
        self,
        page: pymupdf.Page,
        document_id,
        page_number: int,
        source_file: str,
        image_dir: Path | None,
        annotated_dir: Path | None,
    ) -> list[DocumentBlock]:
        page_dict = page.get_text("rawdict", sort=True)
        results: list[DocumentBlock] = []

        page_width = float(page.rect.width)
        page_height = float(page.rect.height)

        combined_texts: list[str] = []
        image_blocks: list[DocumentBlock] = []

        min_x0, min_y0 = page_width, page_height
        max_x1, max_y1 = 0.0, 0.0

        for block_index, raw_block in enumerate(page_dict.get("blocks", [])):
            raw_block_type = raw_block.get("type")

            if raw_block_type == 0:
                text, _ = self.extract_text(raw_block)
                text = text.strip()
                if not text:
                    continue

                bbox = self.create_bbox(raw_block.get("bbox"))
                if bbox is None or self._is_header_footer_or_noise(text, bbox, page_height):
                    continue

                combined_texts.append(text)
                min_x0 = min(min_x0, bbox.x0)
                min_y0 = min(min_y0, bbox.y0)
                max_x1 = max(max_x1, bbox.x1)
                max_y1 = max(max_y1, bbox.y1)

            elif raw_block_type == 1:
                bbox = self.create_bbox(raw_block.get("bbox"))
                if bbox is None:
                    continue

                block_id = uuid4()
                extension = str(raw_block.get("ext") or "png").lower()
                image_filename = f"{block_id}.{extension}"
                image_path: Path | None = None

                if image_dir is not None:
                    image_path = image_dir / image_filename
                    image_bytes = raw_block.get("image")

                    if image_bytes:
                        image_path.write_bytes(image_bytes)
                    else:
                        # Dự phòng: render vùng bbox khi rawdict không trả image bytes.
                        image_filename = f"{block_id}.png"
                        image_path = image_dir / image_filename
                        clip = pymupdf.Rect(bbox.x0, bbox.y0, bbox.x1, bbox.y1)
                        pix = page.get_pixmap(clip=clip, dpi=200, alpha=False)
                        pix.save(str(image_path))
                        extension = "png"

                image_blocks.append(
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
                            "image_path": str(image_path.resolve()) if image_path else None,
                            "source_file": source_file,
                        },
                    )
                )

        if annotated_dir is not None:
            file_stem = Path(source_file).stem if source_file else "doc"
            annotated_path = annotated_dir / f"{file_stem}_page_{page_number}.png"
            page.get_pixmap(dpi=150, alpha=False).save(str(annotated_path))

        if combined_texts:
            if min_x0 > max_x1:
                page_bbox = BoundingBox(x0=0.0, y0=0.0, x1=page_width, y1=page_height)
            else:
                page_bbox = BoundingBox(x0=min_x0, y0=min_y0, x1=max_x1, y1=max_y1)

            results.append(
                DocumentBlock(
                    id=uuid4(),
                    document_id=document_id,
                    page_number=page_number,
                    block_index=0,
                    block_type=BlockType.PARAGRAPH,
                    content="\n".join(combined_texts),
                    bbox=page_bbox,
                    metadata={
                        "source": "pymupdf",
                        "source_file": source_file,
                        "page_width": page_width,
                        "page_height": page_height,
                        "note": "Merged page content",
                    },
                )
            )

        results.extend(image_blocks)
        return results

    def extract_text(self, raw_block: dict) -> tuple[str, dict]:
        lines: list[str] = []
        for line in raw_block.get("lines", []):
            spans = line.get("spans", [])
            if not spans:
                continue

            line_text = self.join_spans(spans)
            if line_text.strip():
                lines.append(line_text.rstrip())

        return "\n".join(lines), raw_block

    @staticmethod
    def create_bbox(bbox: tuple | list | None) -> BoundingBox | None:
        if not bbox or len(bbox) != 4:
            return None
        return BoundingBox(
            x0=float(bbox[0]),
            y0=float(bbox[1]),
            x1=float(bbox[2]),
            y1=float(bbox[3]),
        )

    @staticmethod
    def join_spans(spans: list[dict]) -> str:
        """Ghép text từ output `rawdict` của PyMuPDF.

        `rawdict` dùng khóa `chars`, không dùng `text`.
        """
        result = ""
        previous_span: dict | None = None

        for span in spans:
            chars = span.get("chars", [])
            span_text = "".join(str(char.get("c", "")) for char in chars)
            span_text = unicodedata.normalize("NFC", span_text)
            if not span_text:
                continue

            if result and previous_span is not None:
                previous_bbox = previous_span.get("bbox") or [0, 0, 0, 0]
                current_bbox = span.get("bbox") or [0, 0, 0, 0]
                gap = float(current_bbox[0]) - float(previous_bbox[2])
                font_size = min(
                    float(previous_span.get("size") or 10),
                    float(span.get("size") or 10),
                )
                threshold = max(1.0, font_size * 0.15)

                if (
                    gap > threshold
                    and not result[-1].isspace()
                    and not span_text[0].isspace()
                    and span_text[0] not in ".,;:!?)]}%"
                    and result[-1] not in "([{$"
                ):
                    result += " "

            result += span_text
            previous_span = span

        return result

    @staticmethod
    def _is_header_footer_or_noise(text: str, bbox: BoundingBox, page_height: float) -> bool:
        return bbox.y1 > page_height * 0.9 and text.strip().isdigit()

    @staticmethod
    def save_blocks(blocks: list[DocumentBlock], output_path: Path) -> None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(
            json.dumps([block.to_dict() for block in blocks], ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
from __future__ import annotations

import json
import re
import unicodedata
from pathlib import Path
from uuid import uuid4
import pymupdf
from app.schemas.document_block import BoundingBox, BlockType, DocumentBlock


class PDFReader:
    def extract_pdf(self, file_path: Path, document_id,
                    image_dir: Path | None = None, annotated_dir: Path | None = None,) -> list[DocumentBlock]:
        if not file_path.is_file():
            raise FileNotFoundError(f"Không tìm thấy file: {file_path}")

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
        # rawdict có chars + bbox của từng ký tự, cần thiết để sửa lỗi dính từ.
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

        # Một số trang (ví dụ trang ký hiệu lưu đồ) bị tách thành nhiều ảnh nhỏ.
        # Gộp vùng ảnh thành một ảnh lớn để VLM đọc đúng ngữ cảnh.
        image_blocks = self._merge_small_image_blocks(
            page=page,
            image_blocks=image_blocks,
            document_id=document_id,
            page_number=page_number,
            source_file=source_file,
            image_dir=image_dir,
            page_width=page_width,
            page_height=page_height,
        )

        if annotated_dir is not None:
            file_stem = Path(source_file).stem if source_file else "doc"
            annotated_path = annotated_dir / f"{file_stem}_page_{page_number}.png"
            page.get_pixmap(dpi=150, alpha=False).save(str(annotated_path))

        # Với tài liệu dạng slide, giữ một text block/page là hợp lý;
        # bước tạo RAG sẽ ghép text + mô tả hình của cùng trang.
        if combined_texts:
            page_bbox = BoundingBox(
                x0=min_x0 if min_x0 <= max_x1 else 0.0,
                y0=min_y0 if min_y0 <= max_y1 else 0.0,
                x1=max_x1 if min_x0 <= max_x1 else page_width,
                y1=max_y1 if min_y0 <= max_y1 else page_height,
            )
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
                        "note": "Merged page text",
                    },
                )
            )

        results.extend(image_blocks)
        results.sort(
            key=lambda block: (
                block.page_number,
                block.bbox.y0 if block.bbox else 0.0,
                block.bbox.x0 if block.bbox else 0.0,
                block.block_index,
            )
        )
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
        return BoundingBox(x0=float(bbox[0]), y0=float(bbox[1]), x1=float(bbox[2]), y1=float(bbox[3]),)

    @staticmethod
    def join_spans(spans: list[dict]) -> str:
        """Ghép văn bản bằng khoảng cách giữa từng ký tự trong rawdict."""
        no_space_before = set(".,;:!?)]}%»”’")
        no_space_after = set("([{$«“‘")

        result: list[str] = []
        previous_char = ""
        previous_bbox: tuple | list | None = None
        previous_font_size = 10.0

        for span in spans:
            font_size = float(span.get("size") or 10.0)
            chars = span.get("chars") or []

            # Fallback nếu đầu vào không phải rawdict.
            if not chars and span.get("text"):
                chars = [{"c": char, "bbox": None} for char in str(span["text"])]

            for char_info in chars:
                current_char = unicodedata.normalize("NFC", str(char_info.get("c", "")))
                current_bbox = char_info.get("bbox")
                if not current_char:
                    continue

                if current_char.isspace():
                    if result and result[-1] != " ":
                        result.append(" ")
                    previous_char = " "
                    previous_bbox = current_bbox
                    previous_font_size = font_size
                    continue

                if (
                    result
                    and previous_char
                    and not previous_char.isspace()
                    and previous_bbox is not None
                    and current_bbox is not None
                ):
                    gap = float(current_bbox[0]) - float(previous_bbox[2])
                    reference_size = min(previous_font_size, font_size)
                    threshold = max(0.7, reference_size * 0.12)

                    if (
                        gap > threshold
                        and current_char not in no_space_before
                        and previous_char not in no_space_after
                    ):
                        result.append(" ")

                if result and result[-1] == " " and current_char in no_space_before:
                    result.pop()

                result.append(current_char)
                previous_char = current_char
                previous_bbox = current_bbox
                previous_font_size = font_size

        text = "".join(result)
        text = re.sub(r"[ \t]+", " ", text)
        text = re.sub(r"\s+([,.;:!?%)\]])", r"\1", text)
        text = re.sub(r"([(\[])\s+", r"\1", text)
        return text.strip()

    @staticmethod
    def _is_header_footer_or_noise(
        text: str,
        bbox: BoundingBox,
        page_height: float,
    ) -> bool:
        clean_text = re.sub(r"\s+", " ", text).strip()

        # Footer của slide thường nằm sát 6% cuối trang.
        if bbox.y0 >= page_height * 0.94:
            return True

        # Số trang đứng riêng gần cuối trang.
        if bbox.y1 > page_height * 0.88 and clean_text.isdigit():
            return True

        if len(clean_text) == 1 and not clean_text.isalnum():
            return True

        return False

    @staticmethod
    def _merge_small_image_blocks(
        page: pymupdf.Page,
        image_blocks: list[DocumentBlock],
        document_id,
        page_number: int,
        source_file: str,
        image_dir: Path | None,
        page_width: float,
        page_height: float,
    ) -> list[DocumentBlock]:
        if image_dir is None or len(image_blocks) < 4:
            return image_blocks

        small_images = []
        for block in image_blocks:
            width = int(block.metadata.get("width") or 0)
            height = int(block.metadata.get("height") or 0)
            if width > 0 and height > 0 and width * height < 100_000:
                small_images.append(block)

        if len(small_images) < max(4, int(len(image_blocks) * 0.6)):
            return image_blocks

        x0 = min(block.bbox.x0 for block in image_blocks if block.bbox)
        y0 = min(block.bbox.y0 for block in image_blocks if block.bbox)
        x1 = max(block.bbox.x1 for block in image_blocks if block.bbox)
        y1 = max(block.bbox.y1 for block in image_blocks if block.bbox)

        padding = 16.0
        clip = pymupdf.Rect(
            max(0.0, x0 - padding),
            max(0.0, y0 - padding),
            min(page_width, x1 + padding),
            min(page_height * 0.94, y1 + padding),
        )

        merged_id = uuid4()
        merged_path = image_dir / f"{merged_id}_visual_group.png"
        pix = page.get_pixmap(clip=clip, dpi=200, alpha=False)
        pix.save(str(merged_path))

        return [
            DocumentBlock(
                id=merged_id,
                document_id=document_id,
                page_number=page_number,
                block_index=min(block.block_index for block in image_blocks),
                block_type=BlockType.IMAGE,
                content="",
                bbox=BoundingBox(x0=clip.x0, y0=clip.y0, x1=clip.x1, y1=clip.y1),
                metadata={
                    "source": "pymupdf_rendered_group",
                    "requires_caption": True,
                    "width": pix.width,
                    "height": pix.height,
                    "extension": "png",
                    "page_width": page_width,
                    "page_height": page_height,
                    "file_name": merged_path.name,
                    "image_path": str(merged_path.resolve()),
                    "source_file": source_file,
                    "merged_image_count": len(image_blocks),
                    "merged_from_ids": [str(block.id) for block in image_blocks],
                },
            )
        ]

    @staticmethod
    def save_blocks(blocks: list[DocumentBlock], output_path: Path) -> None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(
            json.dumps([block.to_dict() for block in blocks], ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
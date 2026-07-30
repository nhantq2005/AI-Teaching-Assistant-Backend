from __future__ import annotations

import base64
import json
import re
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Iterable

PROMPT = r"""
Phân tích ảnh tài liệu và trả về nội dung cốt lõi để lưu vào RAG.

Yêu cầu:
- Chỉ trả kết quả, không chào hỏi, không mở đầu kiểu "Dưới đây là".
- Ngắn gọn, chính xác, không thêm kiến thức hoặc ví dụ không xuất hiện trong ảnh.
- Giữ nguyên thuật ngữ chuyên ngành, tên riêng, ký hiệu và mã nguồn.
- Nếu tiêu đề slide và tiêu đề sơ đồ trùng ý, chỉ giữ một tiêu đề phù hợp nhất.

Cách trình bày:
- Sơ đồ phân cấp: dòng đầu là chủ đề; mỗi nhánh viết một dòng theo mẫu
  - Tên nhóm: mục 1, mục 2, mục 3
- Lưu đồ: mỗi bước hoặc nhánh viết một bullet, dùng "->" để thể hiện hướng đi.
- Bảng: dùng Markdown table.
- Mã nguồn: dùng fenced code block và giữ nguyên thụt lề.
- Công thức: dùng LaTeX.
- Ảnh thông thường: tóm tắt trong 1-3 câu.
- Phần không đọc được ghi [Không rõ].

Không tạo các mục "Loại ảnh", "Mô tả phục vụ RAG" hoặc "Từ khóa".
""".strip()

REFUSAL_PATTERNS = (
    "chưa cung cấp ảnh",
    "không có ảnh",
    "không thể xem ảnh",
    "xin lỗi",
)


def _encode_image(image_path: Path) -> str:
    return base64.b64encode(image_path.read_bytes()).decode("utf-8")


def _call_ollama(
    image_path: Path,
    ollama_url: str,
    model: str,
    timeout: float,
    strict_format: bool = False,
) -> str:
    prompt = PROMPT
    if strict_format:
        prompt += "\n\nBắt buộc tuân thủ đúng định dạng ngắn gọn nêu trên."

    payload = {
        "model": model,
        "prompt": prompt,
        "images": [_encode_image(image_path)],
        "stream": False,
        "options": {
            "temperature": 0.0,
            "num_ctx": 1024,
            "num_predict": 200,
            "num_gpu": 18,
        },
    }

    request = urllib.request.Request(
        f"{ollama_url.rstrip('/')}/api/generate",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            data = json.loads(response.read().decode("utf-8"))
    except urllib.error.URLError as exc:
        raise RuntimeError(
            "Không kết nối được Ollama. Hãy chạy: ollama serve"
        ) from exc

    if data.get("error"):
        raise RuntimeError(str(data["error"]))

    text = str(data.get("response", "")).strip()
    if not text:
        raise RuntimeError("Ollama trả về nội dung rỗng.")

    # Bỏ code fence bao ngoài nếu model tự thêm cho toàn bộ câu trả lời.
    if text.startswith("```") and text.endswith("```"):
        lines = text.splitlines()
        if len(lines) >= 3:
            text = "\n".join(lines[1:-1]).strip()

    return text


def _quality_issues(text: str) -> list[str]:
    lowered = text.casefold()
    issues: list[str] = []

    if len(text.strip()) < 10:
        issues.append("too_short")
    if any(pattern in lowered for pattern in REFUSAL_PATTERNS):
        issues.append("model_refused")
    if any(section in text for section in ("Loại ảnh:", "Mô tả phục vụ RAG:", "Từ khóa:")):
        issues.append("old_verbose_format")

    return issues


def describe_image(
    ollama_url: str,
    model: str,
    image_path: Path,
    max_retries: int = 2,
    timeout: float = 180.0,
    strict_format: bool = False,
) -> tuple[str, list[str]]:
    """Phân tích một ảnh và trả về (nội dung, danh sách lỗi chất lượng)."""
    last_error: Exception | None = None
    best_text = ""
    best_issues: list[str] = []

    for attempt in range(max_retries):
        try:
            text = _call_ollama(
                image_path=Path(image_path),
                ollama_url=ollama_url,
                model=model,
                timeout=timeout,
                strict_format=strict_format or attempt > 0,
            )
            issues = _quality_issues(text)
            if not issues:
                return text, []

            best_text, best_issues = text, issues
        except Exception as exc:  # noqa: BLE001
            last_error = exc

        if attempt + 1 < max_retries:
            time.sleep(2)

    if best_text:
        return best_text, best_issues
    raise RuntimeError(f"Không xử lý được {Path(image_path).name}: {last_error}")


def _get(block: Any, field: str, default: Any = None) -> Any:
    return block.get(field, default) if isinstance(block, dict) else getattr(block, field, default)


def _set(block: Any, field: str, value: Any) -> None:
    if isinstance(block, dict):
        block[field] = value
    else:
        setattr(block, field, value)


def _metadata(block: Any) -> dict[str, Any]:
    if isinstance(block, dict):
        return block.setdefault("metadata", {})

    metadata = getattr(block, "metadata", None)
    if metadata is None:
        metadata = {}
        setattr(block, "metadata", metadata)
    return metadata


def _is_image(block: Any) -> bool:
    block_type = _get(block, "block_type", "")
    return str(getattr(block_type, "value", block_type)).lower() == "image"


def _resolve_image(block: Any, image_dir: Path) -> Path | None:
    metadata = _metadata(block)

    raw_path = metadata.get("image_path")
    if raw_path:
        path = Path(str(raw_path))
        for candidate in (path, image_dir / path.name):
            if candidate.is_file():
                return candidate

    file_name = metadata.get("file_name") or metadata.get("image_file")
    if file_name:
        path = image_dir / Path(str(file_name)).name
        if path.is_file():
            return path

    return None


def _skip_reason(block: Any, min_image_area: int = 25_000) -> str | None:
    metadata = _metadata(block)
    try:
        width = int(metadata.get("width") or 0)
        height = int(metadata.get("height") or 0)
    except (TypeError, ValueError):
        return None

    if width > 0 and height > 0 and width * height < min_image_area:
        return f"Ảnh quá nhỏ ({width}x{height})."
    return None


def enrich_image_blocks(
    blocks: Iterable[Any],
    image_dir: Path,
    ollama_url: str = "http://localhost:11434",
    model: str = "qwen2.5vl:3b",
    max_retries: int = 2,
    timeout: float = 180.0,
    strict_format: bool = False,
    force: bool = False,
    skip_noise_images: bool = True,
    **_: Any,
) -> dict[str, int]:
    """Gọi VLM cho các block ảnh và cập nhật content ngay trên block."""
    stats = {
        "image_blocks": 0,
        "processed": 0,
        "already_processed": 0,
        "skipped_noise": 0,
        "missing_file": 0,
        "failed": 0,
    }

    image_dir = Path(image_dir)
    for block in blocks:
        if not _is_image(block):
            continue

        stats["image_blocks"] += 1
        metadata = _metadata(block)

        if str(_get(block, "content", "") or "").strip() and not force:
            stats["already_processed"] += 1
            continue

        image_path = _resolve_image(block, image_dir)
        if image_path is None:
            metadata.update(vlm_processed=False, vlm_error="Không tìm thấy file ảnh.")
            stats["missing_file"] += 1
            continue

        if skip_noise_images:
            reason = _skip_reason(block)
            if reason:
                metadata.update(vlm_processed=False, vlm_skipped=True, vlm_skip_reason=reason)
                stats["skipped_noise"] += 1
                continue

        try:
            text, issues = describe_image(
                ollama_url=ollama_url,
                model=model,
                image_path=image_path,
                max_retries=max_retries,
                timeout=timeout,
                strict_format=strict_format,
            )
            _set(block, "content", text)
            metadata.update(
                image_path=str(image_path.resolve()),
                vlm_processed=True,
                vlm_skipped=False,
                vlm_model=model,
                quality_issues=issues,
            )
            metadata.pop("vlm_error", None)
            metadata.pop("vlm_skip_reason", None)
            stats["processed"] += 1
        except Exception as exc:  # noqa: BLE001
            metadata.update(vlm_processed=False, vlm_error=str(exc))
            stats["failed"] += 1

    return stats


def _split_text(text: str, chunk_size: int, overlap: int) -> list[str]:
    text = re.sub(r"\n{3,}", "\n\n", text).strip()
    if not text or len(text) <= chunk_size:
        return [text] if text else []

    chunks: list[str] = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        if end < len(text):
            cut = max(text.rfind("\n", start, end), text.rfind(" ", start, end))
            end = cut if cut > start else end
        chunks.append(text[start:end].strip())
        start = max(end - overlap, start + 1)
    return [chunk for chunk in chunks if chunk]


def build_rag_records(
    blocks: Iterable[dict[str, Any]],
    source_file: str | None,
    chunk_size: int,
    chunk_overlap: int,
) -> tuple[list[dict[str, Any]], list[str], list[str]]:
    """Chuyển block thành chunk RAG và loại bản ghi trùng nội dung."""
    records: list[dict[str, Any]] = []
    skipped: list[str] = []

    for block in blocks:
        block_id = str(block.get("id", ""))
        content = str(block.get("content", "")).strip()
        if not content:
            skipped.append(block_id or "<missing-id>")
            continue

        block_type = str(block.get("block_type", "unknown"))
        chunks = _split_text(content, chunk_size, chunk_overlap)
        base_metadata = dict(block.get("metadata") or {})
        base_metadata.update(
            document_id=block.get("document_id"),
            page_number=block.get("page_number"),
            block_index=block.get("block_index"),
            block_type=block_type,
            source_type="image" if block_type == "image" else "text",
            source_file=base_metadata.get("source_file") or source_file,
            bbox=block.get("bbox"),
            parent_block_id=block_id,
            chunk_count=len(chunks),
        )

        for index, chunk in enumerate(chunks):
            metadata = dict(base_metadata, chunk_index=index)
            records.append(
                {
                    "id": f"{block_id}:chunk:{index}",
                    "text": chunk,
                    "metadata": metadata,
                }
            )

    unique: list[dict[str, Any]] = []
    seen: dict[str, dict[str, Any]] = {}
    duplicates: list[str] = []

    for record in records:
        key = record["text"].casefold()
        if key in seen:
            duplicates.append(record["id"])
            continue
        seen[key] = record
        unique.append(record)

    return unique, skipped, duplicates


def write_json(path: Path, data: Any) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def write_jsonl(path: Path, records: Iterable[dict[str, Any]]) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as file:
        for record in records:
            file.write(json.dumps(record, ensure_ascii=False) + "\n")
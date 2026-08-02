from __future__ import annotations

import base64
import json
import re
import time
import urllib.error
import urllib.request
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable

PROMPT = r"""
Trích xuất nội dung có ý nghĩa trong ảnh tài liệu để lưu vào hệ thống RAG.

Quy tắc bắt buộc:
- Chỉ ghi nội dung thực sự nhìn thấy trong ảnh; không suy diễn hoặc bổ sung kiến thức.
- Giữ nguyên thuật ngữ, số liệu, ký hiệu, mã nguồn và quan hệ mũi tên.
- Nếu là lưu đồ/sơ đồ, mô tả đúng thứ tự và hướng liên kết bằng "X -> Y".
- Chỉ ghi những nút thực sự được mũi tên nối với nhau.
- Không xem biểu tượng trang trí hoặc chữ trong biểu tượng trang trí là một bước của quy trình.
- Không tạo bảng, mã nguồn hoặc công thức nếu ảnh không có.
- Không dùng tên giả như "Mục 1", "Mục 2", "Tên nhóm".
- Nếu ảnh chỉ là biểu tượng nhỏ hoặc không đọc được nội dung có nghĩa, trả đúng: [Không rõ]
- Không chào hỏi, không giải thích cách phân tích.

Chỉ trả về nội dung cuối cùng, ngắn gọn và đầy đủ.
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
        prompt += """

Kết quả trước chưa đạt yêu cầu. Hãy đọc lại ảnh:
- Không tạo placeholder chung chung.
- Không thêm loại nội dung không xuất hiện.
- Không bỏ dở câu trả lời.
- Giữ đúng hướng mũi tên và quan hệ giữa các thành phần.
"""

    payload = {
        "model": model,
        "prompt": prompt,
        "images": [_encode_image(image_path)],
        "stream": False,
        "keep_alive": -1,
        "options": {
            "temperature": 0.0,
            "num_ctx": 2048,
            "num_predict": 320,
            "num_gpu": -1,
            "num_batch": 64,
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
        raise RuntimeError("Không kết nối được Ollama. Hãy chạy Ollama service.") from exc

    if data.get("error"):
        raise RuntimeError(str(data["error"]))

    text = str(data.get("response", "")).strip()
    if not text:
        raise RuntimeError("Ollama trả về nội dung rỗng.")

    if text.startswith("```") and text.endswith("```"):
        lines = text.splitlines()
        if len(lines) >= 3:
            text = "\n".join(lines[1:-1]).strip()

    return text


def _quality_issues(text: str) -> list[str]:
    lowered = text.casefold()
    stripped = text.strip()
    issues: list[str] = []

    if len(stripped) < 10 and stripped != "[Không rõ]":
        issues.append("too_short")
    if stripped == "[Không rõ]":
        issues.append("unclear")
    if any(pattern in lowered for pattern in REFUSAL_PATTERNS):
        issues.append("model_refused")
    if re.search(r"\bMục\s*1\b.*\bMục\s*2\b", text, flags=re.I | re.S):
        issues.append("generic_placeholder")
    if "Tên nhóm:" in text:
        issues.append("generic_placeholder")
    if text.count("```") % 2 != 0:
        issues.append("unclosed_code_fence")
    if stripped.endswith(("->", "|", ",", ":")):
        issues.append("possibly_truncated")

    return list(dict.fromkeys(issues))


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


def _block_type(block: Any) -> str:
    value = _get(block, "block_type", "unknown")
    return str(getattr(value, "value", value)).lower()


def _is_image(block: Any) -> bool:
    return _block_type(block) == "image"


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
        max_retries: int = 3,
        timeout: float = 180.0,
        strict_format: bool = False,
        force: bool = False,
        skip_noise_images: bool = True,
        **_: Any,
) -> dict[str, int]:
    stats = {
        "image_blocks": 0,
        "processed": 0,
        "already_processed": 0,
        "skipped_noise": 0,
        "missing_file": 0,
        "excluded": 0,
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
            metadata.update(
                vlm_processed=False,
                exclude_from_embedding=True,
                vlm_error="Không tìm thấy file ảnh.",
            )
            stats["missing_file"] += 1
            continue

        if skip_noise_images:
            reason = _skip_reason(block)
            if reason:
                metadata.update(
                    vlm_processed=False,
                    vlm_skipped=True,
                    exclude_from_embedding=True,
                    vlm_skip_reason=reason,
                )
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
            exclude = bool(issues) or text.strip() == "[Không rõ]"
            metadata.update(
                image_path=str(image_path.resolve()),
                vlm_processed=True,
                vlm_skipped=False,
                vlm_model=model,
                quality_issues=issues,
                exclude_from_embedding=exclude,
            )
            metadata.pop("vlm_error", None)
            metadata.pop("vlm_skip_reason", None)
            stats["processed"] += 1
            if exclude:
                stats["excluded"] += 1
        except Exception as exc:  # noqa: BLE001
            metadata.update(
                vlm_processed=False,
                exclude_from_embedding=True,
                vlm_error=str(exc),
            )
            stats["failed"] += 1

    return stats


def _split_text(text: str, chunk_size: int, overlap: int) -> list[str]:
    if chunk_size <= 0:
        raise ValueError("chunk_size phải lớn hơn 0")
    if overlap < 0 or overlap >= chunk_size:
        raise ValueError("chunk_overlap phải thỏa 0 <= overlap < chunk_size")

    text = re.sub(r"\n{3,}", "\n\n", text).strip()
    if not text or len(text) <= chunk_size:
        return [text] if text else []

    chunks: list[str] = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        if end < len(text):
            candidates = [
                text.rfind("\n\n", start, end),
                text.rfind(". ", start, end),
                text.rfind("! ", start, end),
                text.rfind("? ", start, end),
                text.rfind("\n", start, end),
                text.rfind(" ", start, end),
            ]
            cut = max(candidates)
            if cut > start:
                end = cut + (1 if text[cut: cut + 2] in {". ", "! ", "? "} else 0)

        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        start = max(end - overlap, start + 1)

    return chunks


def build_page_rag_records(
        blocks: Iterable[dict[str, Any]],
        source_file: str | None,
        chunk_size: int = 900,
        chunk_overlap: int = 120,
) -> tuple[list[dict[str, Any]], list[str], list[str]]:
    """Ghép text và mô tả hình theo trang, rồi mới chia chunk."""
    grouped: dict[tuple[str, int], list[dict[str, Any]]] = defaultdict(list)
    skipped: list[str] = []

    for block in blocks:
        block_id = str(block.get("id", "")) or "<missing-id>"
        metadata = dict(block.get("metadata") or {})
        content = str(block.get("content", "") or "").strip()

        if metadata.get("exclude_from_embedding") or not content or content == "[Không rõ]":
            skipped.append(block_id)
            continue

        document_id = str(block.get("document_id", ""))
        page_number = int(block.get("page_number") or 0)
        grouped[(document_id, page_number)].append(block)

    records: list[dict[str, Any]] = []
    for (document_id, page_number), page_blocks in sorted(grouped.items(), key=lambda item: item[0][1]):
        page_blocks.sort(key=lambda block: int(block.get("block_index") or 0))

        parts: list[str] = []
        block_ids: list[str] = []
        block_types: list[str] = []
        page_source_file = source_file

        for block in page_blocks:
            block_id = str(block.get("id", ""))
            block_type = str(block.get("block_type", "unknown")).lower()
            content = str(block.get("content", "")).strip()
            metadata = dict(block.get("metadata") or {})

            block_ids.append(block_id)
            block_types.append(block_type)
            page_source_file = metadata.get("source_file") or page_source_file

            if block_type == "image":
                parts.append(f"Mô tả hình/sơ đồ:\n{content}")
            else:
                parts.append(content)

        page_text = "\n\n".join(parts).strip()
        chunks = _split_text(page_text, chunk_size, chunk_overlap)
        title = page_text.splitlines()[0].strip() if page_text else ""

        for chunk_index, chunk in enumerate(chunks):
            records.append(
                {
                    "id": f"{document_id}:page:{page_number}:chunk:{chunk_index}",
                    "text": chunk,
                    "metadata": {
                        "document_id": document_id,
                        "page_number": page_number,
                        "source_file": page_source_file,
                        "source_type": "page",
                        "title": title,
                        "block_ids": block_ids,
                        "block_types": sorted(set(block_types)),
                        "chunk_index": chunk_index,
                        "chunk_count": len(chunks),
                    },
                }
            )

    unique: list[dict[str, Any]] = []
    duplicates: list[str] = []
    seen: set[str] = set()
    for record in records:
        key = re.sub(r"\s+", " ", record["text"]).strip().casefold()
        if key in seen:
            duplicates.append(record["id"])
            continue
        seen.add(key)
        unique.append(record)

    return unique, skipped, duplicates


# Giữ tên cũ để code khác trong dự án không bị lỗi import.
def build_rag_records(blocks: Iterable[dict[str, Any]], source_file: str | None, chunk_size: int,
                      chunk_overlap: int, ) -> tuple[list[dict[str, Any]], list[str], list[str]]:
    return build_page_rag_records(
        blocks=blocks,
        source_file=source_file,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )


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

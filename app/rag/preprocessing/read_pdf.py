from __future__ import annotations

import json
import math
import re
import statistics
import unicodedata
from collections import defaultdict
from pathlib import Path
import pymupdf
from app.rag.preprocessing.convert_to_unicode import convert_tcvn3_to_unicode

CURRENT_FILE = Path(__file__).resolve()
ROOT = (
    CURRENT_FILE.parents[3]
    if len(CURRENT_FILE.parents) > 3
    else CURRENT_FILE.parent
)
INPUT_DIR = ROOT / "data"
OUTPUT_DIR = ROOT / "processed_data"

SKIP_TOC = True
REMOVE_HEADER_FOOTER = True
WRITE_PREVIEW = True


PAGE_RE = re.compile(r"^\s*(?:\d{1,4}|[ivxlcdm]{1,8})\s*$", re.I)
LIST_RE = re.compile(
    r"^\s*(?:[•▪◦●○■□◆◇‣⁃–—-]|§|\(?[A-Za-z]\)|\d+(?:\.\d+)*[.)])\s+"
)
HEADING_RE = re.compile(
    r"^\s*(?:chương\s+\d+|chapter\s+\d+|\d+(?:\.\d+)+\.?\s+)",
    re.I,
)
TOC_RE = re.compile(r"\.{4,}\s*\d+\s*$")

def clean(text: str) -> str:
    text = convert_tcvn3_to_unicode(text)
    text = unicodedata.normalize("NFC", text)
    text = text.replace("\u00a0", " ").replace("\u200b", "")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\s+([,.;:!?%)\]])", r"\1", text)

    return text.strip()


def join_chars(spans: list[dict]) -> str:
    """Ghép ký tự theo bbox để phục hồi dấu cách bị thiếu."""
    result: list[str] = []
    prev_char = ""
    prev_bbox = None
    prev_size = 10.0

    no_space_before = set(",.;:!?)]}%")
    no_space_after = set("([{")

    for span in spans:
        size = float(span.get("size") or 10)

        for item in span.get("chars") or []:
            char = str(item.get("c", ""))
            bbox = item.get("bbox")

            if not char:
                continue

            if char.isspace():
                if result and result[-1] != " ":
                    result.append(" ")

                prev_char, prev_bbox, prev_size = " ", bbox, size
                continue

            if (
                result
                and prev_char
                and not prev_char.isspace()
                and prev_bbox
                and bbox
            ):
                gap = float(bbox[0]) - float(prev_bbox[2])
                threshold = max(0.8, min(prev_size, size) * 0.18)

                if (
                    gap > threshold
                    and char not in no_space_before
                    and prev_char not in no_space_after
                    and result[-1] != " "
                ):
                    result.append(" ")

            if result and result[-1] == " " and char in no_space_before:
                result.pop()

            result.append(char)
            prev_char, prev_bbox, prev_size = char, bbox, size

    return clean("".join(result))


def read_pages(pdf_bytes: bytes):
    pages = []

    with pymupdf.open(stream=pdf_bytes, filetype="pdf") as doc:
        if doc.needs_pass:
            raise ValueError("PDF được bảo vệ bằng mật khẩu.")

        for page_index, page in enumerate(doc):
            blocks = []

            for raw_block in page.get_text("rawdict", sort=True).get("blocks", []):
                if raw_block.get("type") != 0:
                    continue

                lines = []

                for raw_line in raw_block.get("lines", []):
                    spans = raw_line.get("spans") or []
                    text = join_chars(spans)

                    if not text:
                        continue

                    sizes = [
                        float(span.get("size") or 0)
                        for span in spans
                        if span.get("chars")
                    ]
                    fonts = [
                        str(span.get("font", "")).casefold()
                        for span in spans
                    ]

                    lines.append(
                        {
                            "text": text,
                            "bbox": tuple(raw_line.get("bbox", (0, 0, 0, 0))),
                            "size": statistics.median(sizes) if sizes else 0,
                            "mono": any(
                                key in " ".join(fonts)
                                for key in ("courier", "consolas", "mono")
                            ),
                        }
                    )

                if lines:
                    blocks.append(
                        {
                            "bbox": tuple(raw_block.get("bbox", (0, 0, 0, 0))),
                            "lines": lines,
                        }
                    )

            pages.append(
                {
                    "number": page_index + 1,
                    "width": float(page.rect.width),
                    "height": float(page.rect.height),
                    "blocks": blocks,
                }
            )

    return pages


def signature(text: str) -> str:
    return re.sub(r"\d+", "<n>", clean(text).casefold())


def repeated_edges(pages: list[dict]) -> set[str]:
    found: dict[str, set[int]] = defaultdict(set)

    for page in pages:
        for block in page["blocks"]:
            for line in block["lines"]:
                y0, y1 = line["bbox"][1], line["bbox"][3]

                if y1 > page["height"] * 0.10 and y0 < page["height"] * 0.86:
                    continue

                value = signature(line["text"])

                if value and value != "<n>":
                    found[value].add(page["number"])

    minimum = max(3, math.ceil(len(pages) * 0.12))
    return {value for value, nums in found.items() if len(nums) >= minimum}


def is_toc(page: dict) -> bool:
    lines = [
        line["text"]
        for block in page["blocks"]
        for line in block["lines"]
    ]
    text = "\n".join(lines)

    return (
        "mục lục" in text.casefold()
        or sum(bool(TOC_RE.search(line)) for line in lines) >= 4
    )


def is_code(lines: list[dict]) -> bool:
    texts = [line["text"].strip() for line in lines]
    strong = sum(
        text.startswith(
            (
                "//",
                "/*",
                "#include",
                "#define",
                "import ",
                "from ",
                "def ",
                "class ",
                "public ",
                "private ",
                "using namespace ",
                "SELECT ",
                "INSERT ",
                "UPDATE ",
                "DELETE ",
            )
        )
        or text in {"{", "}", "};"}
        or bool(re.search(r"^\w[\w.\[\]]*\s*=\s*.+;?$", text))
        or any(op in text for op in ("<<", ">>", "==", "!=", "=>", "->"))
        for text in texts
    )
    mono = sum(line["mono"] for line in lines)

    return strong >= 2 or (
        strong >= 1
        and mono / max(1, len(lines)) >= 0.60
    )


def heading_level(text: str) -> int:
    if re.match(r"^\s*(?:chương|chapter)\s+\d+", text, re.I):
        return 1

    match = re.match(r"^\s*(\d+(?:\.\d+)+)", text)

    return min(4, match.group(1).count(".") + 1) if match else 2


def to_blocks(page: dict, edges: set[str], body_size: float) -> list[dict]:
    result = []

    for raw_block in page["blocks"]:
        lines = []

        for line in raw_block["lines"]:
            text = line["text"]
            y0, y1 = line["bbox"][1], line["bbox"][3]
            edge = y1 <= page["height"] * 0.10 or y0 >= page["height"] * 0.86

            if edge and PAGE_RE.fullmatch(text):
                continue

            if REMOVE_HEADER_FOOTER and edge and signature(text) in edges:
                continue

            lines.append(line)

        if not lines:
            continue

        text_lines = [line["text"] for line in lines]
        text = clean(" ".join(text_lines))
        bbox = [
            round(float(value), 2)
            for value in raw_block["bbox"]
        ]

        if is_code(lines):
            result.append(
                {
                    "block_type": "code",
                    "text": "\n".join(text_lines),
                    "bbox": bbox,
                }
            )
            continue

        if any(LIST_RE.match(value) for value in text_lines):
            current = []

            for value in text_lines:
                if LIST_RE.match(value):
                    if current:
                        result.append(
                            {
                                "block_type": "list_item",
                                "text": clean(" ".join(current)),
                                "bbox": bbox,
                            }
                        )
                    current = [value]
                elif current:
                    current.append(value)
                else:
                    result.append(
                        {
                            "block_type": "paragraph",
                            "text": clean(value),
                            "bbox": bbox,
                        }
                    )

            if current:
                result.append(
                    {
                        "block_type": "list_item",
                        "text": clean(" ".join(current)),
                        "bbox": bbox,
                    }
                )
            continue

        max_size = max(line["size"] for line in lines)
        letters = [char for char in text if char.isalpha()]
        upper_ratio = (
            sum(char.isupper() for char in letters) / len(letters)
            if letters
            else 0
        )

        if (
            HEADING_RE.match(text)
            or max_size >= body_size * 1.22
            or (
                upper_ratio >= 0.78
                and len(text) <= 120
                and not text.endswith((".", ",", ";", ":"))
            )
        ):
            result.append(
                {
                    "block_type": "heading",
                    "heading_level": heading_level(text),
                    "text": text,
                    "bbox": bbox,
                }
            )
        else:
            result.append(
                {
                    "block_type": "paragraph",
                    "text": text,
                    "bbox": bbox,
                }
            )

    return result


def extract_pdf(pdf_bytes: bytes, file_name: str):
    pages = read_pages(pdf_bytes)
    edges = repeated_edges(pages)

    sizes = [
        line["size"]
        for page in pages
        for block in page["blocks"]
        for line in block["lines"]
        if line["size"] > 0 and len(line["text"]) > 3
    ]
    body_size = statistics.median(sizes) if sizes else 11.0
    file_stem = file_name.rsplit('.', 1)[0]

    records = []
    headings: list[str] = []

    for page in pages:
        if SKIP_TOC and is_toc(page):
            continue

        for index, block in enumerate(to_blocks(page, edges, body_size)):
            if block["block_type"] == "heading":
                level = block.get("heading_level", 2)
                headings = headings[: level - 1] + [block["text"]]

            records.append(
                {
                    "id": f"{file_stem}:p{page['number']}:b{index}",
                    "source_file": file_name,
                    "page_number": page["number"],
                    "block_index": index,
                    "block_type": block["block_type"],
                    "heading_level": block.get("heading_level"),
                    "heading_path": headings.copy(),
                    "text": block["text"],
                    "bbox": block["bbox"],
                }
            )

    # jsonl_path = output_dir / "blocks.jsonl"
    #
    # with jsonl_path.open("w", encoding="utf-8") as file:
    #     for record in records:
    #         file.write(json.dumps(record, ensure_ascii=False) + "\n")
    #
    # if WRITE_PREVIEW:
    #     preview = []
    #
    #     for record in records:
    #         preview.append(
    #             f"[TRANG {record['page_number']}] "
    #             f"[{record['block_type'].upper()}]\n"
    #             f"{record['text']}"
    #         )
    #
    #     (output_dir / "preview.txt").write_text(
    #         "\n\n".join(preview),
    #         encoding="utf-8",
    #     )
    #
    # print(f"[OK] {pdf_path.name}: {len(records)} blocks")

    return records


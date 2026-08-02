from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import Enum
from typing import Any
from uuid import UUID


class BlockType(str, Enum):
    PARAGRAPH = "paragraph"
    IMAGE = "image"


@dataclass
class BoundingBox:
    x0: float
    y0: float
    x1: float
    y1: float

    def to_dict(self) -> dict[str, float]:
        return asdict(self)


@dataclass
class DocumentBlock:
    id: int
    document_id: int
    page_number: int
    block_index: int
    block_type: BlockType
    content: str
    bbox: BoundingBox | None = None
    metadata: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["id"] = str(self.id)
        data["document_id"] = str(self.document_id)
        data["block_type"] = self.block_type.value
        if self.bbox is not None:
            data["bbox"] = self.bbox.to_dict()
        data["metadata"] = self.metadata or {}
        return data

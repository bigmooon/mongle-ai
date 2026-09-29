"""Deterministic diagnostic image; does not interpret prompts or source photos."""

from __future__ import annotations

import struct
import zlib

from agents.character_creation.schemas import ImageGenerationResult, LLMPersonaResult


def _diagnostic_png() -> bytes:
    """Encode a 64px purple checkerboard using only the standard library."""
    def chunk(kind: bytes, payload: bytes) -> bytes:
        return (
            struct.pack(">I", len(payload))
            + kind
            + payload
            + struct.pack(">I", zlib.crc32(kind + payload))
        )

    colors = (b"\xa7\x8b\xfa", b"\xed\xe9\xfe")
    rows = b"".join(
        b"\x00" + b"".join(colors[(x // 8 + y // 8) % 2] for x in range(64))
        for y in range(64)
    )
    return (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", struct.pack(">IIBBBBB", 64, 64, 8, 2, 0, 0, 0))
        + chunk(b"IDAT", zlib.compress(rows))
        + chunk(b"IEND", b"")
    )


class MockImageGenerator:
    """Character ImageGeneratorPort for local integration checks, not AI output."""

    async def generate(
        self,
        *,
        user_id: str,
        llm_result: LLMPersonaResult,
        fallback_persona: str,
        source_image_bytes: bytes | None = None,
    ) -> ImageGenerationResult:
        return ImageGenerationResult(
            image_bytes=_diagnostic_png(),
            appearance_payload=None,
        )

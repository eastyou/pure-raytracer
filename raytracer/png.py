"""手写 PNG 编码器。

标准库只有 zlib 和 struct，足够拼出 PNG：IHDR + IDAT + IEND 三个块，
每行数据前置一个过滤类型字节 0（None）。
"""

from __future__ import annotations

import struct
import zlib
from pathlib import Path
from typing import Union

PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
COLOR_TYPE_RGB = 2
BIT_DEPTH = 8


def _chunk(tag: bytes, data: bytes) -> bytes:
    checksum = zlib.crc32(tag + data) & 0xFFFFFFFF
    return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", checksum)


def encode_png(width: int, height: int, rgb: bytes) -> bytes:
    """把 RGB 像素编码为 PNG 字节。

    ``rgb`` 长度为 ``width * height * 3``，按行优先排列。
    """
    if width <= 0 or height <= 0:
        raise ValueError("图片宽高必须大于 0")
    expected = width * height * 3
    if len(rgb) != expected:
        raise ValueError(
            "像素数据长度不正确: 期望 %d 字节，实际 %d 字节" % (expected, len(rgb))
        )

    scanlines = bytearray()
    stride = width * 3
    for row in range(height):
        scanlines.append(0)
        start = row * stride
        scanlines.extend(rgb[start : start + stride])

    header = struct.pack(
        ">IIBBBBB", width, height, BIT_DEPTH, COLOR_TYPE_RGB, 0, 0, 0
    )
    return b"".join(
        [
            PNG_SIGNATURE,
            _chunk(b"IHDR", header),
            _chunk(b"IDAT", zlib.compress(bytes(scanlines), 9)),
            _chunk(b"IEND", b""),
        ]
    )


def write_png(
    path: Union[str, Path], width: int, height: int, rgb: bytes
) -> None:
    """编码并写入文件。"""
    payload = encode_png(width, height, rgb)
    target = Path(path)
    if target.parent and not target.parent.exists():
        target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(payload)

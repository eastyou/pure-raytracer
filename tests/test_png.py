from __future__ import annotations

import os
import struct
import tempfile
import unittest
import zlib
from typing import List, Tuple

from raytracer.png import PNG_SIGNATURE, encode_png, write_png


def parse_chunks(data: bytes) -> List[Tuple[bytes, bytes]]:
    if not data.startswith(PNG_SIGNATURE):
        raise AssertionError("PNG 签名不正确")
    chunks: List[Tuple[bytes, bytes]] = []
    position = len(PNG_SIGNATURE)
    while position < len(data):
        length = struct.unpack(">I", data[position : position + 4])[0]
        tag = data[position + 4 : position + 8]
        payload = data[position + 8 : position + 8 + length]
        crc = struct.unpack(">I", data[position + 8 + length : position + 12 + length])[0]
        if crc != (zlib.crc32(tag + payload) & 0xFFFFFFFF):
            raise AssertionError("CRC 校验失败: %r" % tag)
        chunks.append((tag, payload))
        position += 12 + length
    return chunks


class PngTest(unittest.TestCase):
    def test_encode_header(self) -> None:
        chunks = parse_chunks(encode_png(2, 1, bytes([255, 0, 0, 0, 255, 0])))
        tags = [tag for tag, _ in chunks]
        self.assertEqual(tags, [b"IHDR", b"IDAT", b"IEND"])

        width, height, depth, color_type, compression, filtering, interlace = (
            struct.unpack(">IIBBBBB", chunks[0][1])
        )
        self.assertEqual((width, height), (2, 1))
        self.assertEqual(depth, 8)
        self.assertEqual(color_type, 2)
        self.assertEqual((compression, filtering, interlace), (0, 0, 0))

    def test_idat_roundtrip(self) -> None:
        rgb = bytes([255, 0, 0, 0, 255, 0, 0, 0, 255, 10, 20, 30])
        chunks = dict(parse_chunks(encode_png(2, 2, rgb)))
        raw = zlib.decompress(chunks[b"IDAT"])
        expected = b"\x00" + rgb[0:6] + b"\x00" + rgb[6:12]
        self.assertEqual(raw, expected)

    def test_invalid_data_length(self) -> None:
        with self.assertRaises(ValueError):
            encode_png(2, 2, b"\x00\x00\x00")

    def test_invalid_size(self) -> None:
        with self.assertRaises(ValueError):
            encode_png(0, 1, b"")

    def test_write_png(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "sub", "demo.png")
            write_png(path, 1, 1, bytes([1, 2, 3]))
            self.assertTrue(os.path.exists(path))
            with open(path, "rb") as handle:
                self.assertEqual(handle.read(8), PNG_SIGNATURE)


if __name__ == "__main__":
    unittest.main()

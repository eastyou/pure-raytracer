"""渲染主循环与光线求值。"""

from __future__ import annotations

import math
import random
from typing import Callable, Optional

from .camera import Camera
from .geometry import World
from .vec3 import Vec3

ProgressCallback = Callable[[int, int], None]


def _sky(direction: Vec3) -> Vec3:
    unit = direction.normalized()
    t = 0.5 * (unit.y + 1.0)
    return Vec3(1.0, 1.0, 1.0) * (1.0 - t) + Vec3(0.45, 0.62, 0.95) * t


def trace(
    world: World,
    origin: Vec3,
    direction: Vec3,
    max_depth: int,
    rng: random.Random,
) -> Vec3:
    """迭代式路径追踪：沿光线累乘衰减，避免递归栈开销。"""
    color = Vec3(1.0, 1.0, 1.0)
    current_origin = origin
    current_direction = direction

    for _ in range(max_depth):
        hit = world.hit(current_origin, current_direction)
        if hit is None:
            return color * _sky(current_direction)
        scattered = hit.material.scatter(current_direction, hit, rng)
        if scattered is None:
            return Vec3(0.0, 0.0, 0.0)
        attenuation, new_direction = scattered
        if attenuation.near_zero():
            return Vec3(0.0, 0.0, 0.0)
        color = color * attenuation
        current_origin = hit.point
        current_direction = new_direction.normalized()

    return Vec3(0.0, 0.0, 0.0)


def _to_byte(value: float) -> int:
    """伽马校正（gamma 2.0）后量化到 0-255。"""
    if value <= 0.0:
        return 0
    if value >= 1.0:
        return 255
    return int(255.999 * math.sqrt(value))


def render(
    world: World,
    camera: Camera,
    width: int,
    height: int,
    samples: int = 8,
    max_depth: int = 5,
    seed: int = 0,
    progress: Optional[ProgressCallback] = None,
) -> bytes:
    """渲染并返回 RGB 字节，可能耗时较长，建议先用小图预览。"""
    if width <= 0 or height <= 0:
        raise ValueError("图片宽高必须大于 0")
    if samples <= 0:
        raise ValueError("采样数必须大于 0")
    if max_depth <= 0:
        raise ValueError("光线深度必须大于 0")

    rng = random.Random(seed)
    pixels = bytearray(width * height * 3)
    index = 0
    inv_samples = 1.0 / samples

    for y in range(height):
        for x in range(width):
            red = 0.0
            green = 0.0
            blue = 0.0
            for _ in range(samples):
                s = (x + rng.random()) / width
                t = (height - 1 - y + rng.random()) / height
                origin, direction = camera.ray(s, t, rng)
                color = trace(world, origin, direction, max_depth, rng)
                red += color.x
                green += color.y
                blue += color.z
            pixels[index] = _to_byte(red * inv_samples)
            pixels[index + 1] = _to_byte(green * inv_samples)
            pixels[index + 2] = _to_byte(blue * inv_samples)
            index += 3
        if progress is not None:
            progress(y + 1, height)

    return bytes(pixels)

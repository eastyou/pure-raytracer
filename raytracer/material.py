"""材质：漫反射、金属、电介质（玻璃）。

``scatter`` 返回 ``(attenuation, scattered_direction)``，返回 ``None`` 表示光线被吸收。
"""

from __future__ import annotations

import math
import random
from typing import Any, Optional, Tuple

from .vec3 import Vec3

Scatter = Tuple[Vec3, Vec3]


def random_unit_vector(rng: random.Random) -> Vec3:
    """在单位球面上均匀取点。"""
    while True:
        candidate = Vec3(
            rng.uniform(-1.0, 1.0),
            rng.uniform(-1.0, 1.0),
            rng.uniform(-1.0, 1.0),
        )
        length_squared = candidate.length_squared()
        if 1e-12 < length_squared <= 1.0:
            return candidate / math.sqrt(length_squared)


class Lambertian:
    """理想漫反射，可选棋盘格纹理。"""

    __slots__ = ("albedo", "checker_scale", "checker_albedo")

    def __init__(
        self,
        albedo: Vec3,
        checker_scale: float = 0.0,
        checker_albedo: Optional[Vec3] = None,
    ) -> None:
        self.albedo = albedo
        self.checker_scale = float(checker_scale)
        self.checker_albedo = checker_albedo or Vec3(0.2, 0.2, 0.2)

    def color_at(self, point: Vec3) -> Vec3:
        if self.checker_scale <= 0:
            return self.albedo
        cell = (
            math.floor(point.x * self.checker_scale)
            + math.floor(point.z * self.checker_scale)
        )
        return self.albedo if int(cell) % 2 == 0 else self.checker_albedo

    def scatter(
        self, direction: Vec3, hit: Any, rng: random.Random
    ) -> Optional[Scatter]:
        scattered = hit.normal + random_unit_vector(rng)
        if scattered.near_zero():
            scattered = hit.normal
        return self.color_at(hit.point), scattered


class Metal:
    """带粗糙度的金属。"""

    __slots__ = ("albedo", "fuzz")

    def __init__(self, albedo: Vec3, fuzz: float = 0.0) -> None:
        if fuzz < 0:
            raise ValueError("金属粗糙度不能为负")
        self.albedo = albedo
        self.fuzz = min(float(fuzz), 1.0)

    def scatter(
        self, direction: Vec3, hit: Any, rng: random.Random
    ) -> Optional[Scatter]:
        reflected = direction.reflect(hit.normal)
        scattered = reflected + random_unit_vector(rng) * self.fuzz
        if scattered.dot(hit.normal) <= 0:
            return None
        return self.albedo, scattered


class Dielectric:
    """玻璃等透明介质，包含全反射与 Schlick 近似。"""

    __slots__ = ("refractive_index",)

    def __init__(self, refractive_index: float = 1.5) -> None:
        if refractive_index <= 1.0:
            raise ValueError("折射率必须大于 1")
        self.refractive_index = float(refractive_index)

    def scatter(
        self, direction: Vec3, hit: Any, rng: random.Random
    ) -> Optional[Scatter]:
        front_face = direction.dot(hit.normal) < 0
        ratio = 1.0 / self.refractive_index if front_face else self.refractive_index

        # hit.normal 始终朝向射线来向，可以直接用于斯涅尔定律与反射。
        cos_theta = min((-direction).dot(hit.normal), 1.0)
        sin_theta = math.sqrt(max(0.0, 1.0 - cos_theta * cos_theta))
        cannot_refract = ratio * sin_theta > 1.0
        if cannot_refract:
            scattered = direction.reflect(hit.normal)
        else:
            scattered = direction.refract(hit.normal, ratio)
        return Vec3(1.0, 1.0, 1.0), scattered

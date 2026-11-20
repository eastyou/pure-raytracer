"""针孔 / 薄透镜相机。"""

from __future__ import annotations

import math
import random
from typing import Tuple

from .vec3 import Vec3


def _random_in_unit_disk(rng: random.Random) -> Vec3:
    while True:
        point = Vec3(rng.uniform(-1, 1), rng.uniform(-1, 1), 0.0)
        if point.length_squared() < 1.0:
            return point


class Camera:
    """视角由位置、朝向、垂直视场角决定，可选景深。"""

    def __init__(
        self,
        lookfrom: Vec3,
        lookat: Vec3,
        vup: Vec3,
        vertical_fov: float,
        aspect: float,
        aperture: float = 0.0,
        focus_distance: float = 1.0,
    ) -> None:
        if aspect <= 0:
            raise ValueError("宽高比必须大于 0")
        if not 0.0 < vertical_fov < 180.0:
            raise ValueError("视场角必须在 (0, 180) 度之间")

        theta = math.radians(vertical_fov)
        half_height = math.tan(theta / 2.0)
        half_width = aspect * half_height

        self.origin = lookfrom
        self.w = (lookfrom - lookat).normalized()
        self.u = vup.cross(self.w).normalized()
        self.v = self.w.cross(self.u)
        self.aperture = aperture
        self.focus_distance = focus_distance

        self.horizontal = self.u * (2.0 * half_width * focus_distance)
        self.vertical = self.v * (2.0 * half_height * focus_distance)
        self.lower_left = (
            self.origin
            - self.horizontal * 0.5
            - self.vertical * 0.5
            - self.w * focus_distance
        )

    def ray(
        self, s: float, t: float, rng: random.Random
    ) -> Tuple[Vec3, Vec3]:
        """``(s, t)`` 为归一化屏幕坐标，返回 ``(起点, 单位方向)``。"""
        origin = self.origin
        if self.aperture > 0:
            offset = _random_in_unit_disk(rng) * self.aperture
            origin = origin + self.u * offset.x + self.v * offset.y
        target = self.lower_left + self.horizontal * s + self.vertical * t
        return origin, (target - origin).normalized()

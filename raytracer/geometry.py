"""几何体与场景求交。"""

from __future__ import annotations

import math
from typing import Any, List, Optional

from .vec3 import Vec3


class Hit:
    """一次射线与物体的交点。"""

    __slots__ = ("t", "point", "normal", "material")

    def __init__(
        self, t: float, point: Vec3, normal: Vec3, material: Any
    ) -> None:
        self.t = t
        self.point = point
        self.normal = normal
        self.material = material


class Sphere:
    """球体。"""

    __slots__ = ("center", "radius", "material")

    def __init__(self, center: Vec3, radius: float, material: Any) -> None:
        if radius <= 0:
            raise ValueError("球半径必须大于 0")
        self.center = center
        self.radius = float(radius)
        self.material = material

    def hit(
        self, origin: Vec3, direction: Vec3, t_min: float, t_max: float
    ) -> Optional[Hit]:
        oc = origin - self.center
        a = direction.length_squared()
        half_b = oc.dot(direction)
        c = oc.length_squared() - self.radius * self.radius
        discriminant = half_b * half_b - a * c
        if discriminant <= 0:
            return None
        root = math.sqrt(discriminant)
        t = (-half_b - root) / a
        if t <= t_min or t >= t_max:
            t = (-half_b + root) / a
            if t <= t_min or t >= t_max:
                return None
        point = origin + direction * t
        outward = (point - self.center) / self.radius
        normal = outward if direction.dot(outward) < 0 else -outward
        return Hit(t, point, normal, self.material)


class Plane:
    """无限平面，常用于地面。"""

    __slots__ = ("point", "normal", "material")

    def __init__(self, point: Vec3, normal: Vec3, material: Any) -> None:
        if normal.near_zero():
            raise ValueError("平面法线不能是零向量")
        self.point = point
        self.normal = normal.normalized()
        self.material = material

    def hit(
        self, origin: Vec3, direction: Vec3, t_min: float, t_max: float
    ) -> Optional[Hit]:
        denominator = self.normal.dot(direction)
        if abs(denominator) < 1e-9:
            return None
        t = (self.point - origin).dot(self.normal) / denominator
        if t <= t_min or t >= t_max:
            return None
        point = origin + direction * t
        normal = self.normal if denominator < 0 else -self.normal
        return Hit(t, point, normal, self.material)


class World:
    """场景：一组物体，返回最近的交点。"""

    def __init__(self) -> None:
        self.objects: List[Any] = []

    def add(self, obj: Any) -> None:
        self.objects.append(obj)

    def hit(
        self, origin: Vec3, direction: Vec3, t_min: float = 1e-4,
        t_max: float = math.inf,
    ) -> Optional[Hit]:
        closest: Optional[Hit] = None
        limit = t_max
        for obj in self.objects:
            found = obj.hit(origin, direction, t_min, limit)
            if found is not None:
                closest = found
                limit = found.t
        return closest

"""三维向量：光线追踪里所有几何运算的基础。

实现精简，只保留渲染需要的操作，``__slots__`` 降低单个对象的内存开销。
"""

from __future__ import annotations

import math
from typing import Iterator, Union

Number = Union[int, float]


class Vec3:
    """一个可变的三维向量。"""

    __slots__ = ("x", "y", "z")

    def __init__(self, x: Number = 0.0, y: Number = 0.0, z: Number = 0.0) -> None:
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)

    def __repr__(self) -> str:
        return "Vec3(%g, %g, %g)" % (self.x, self.y, self.z)

    def __iter__(self) -> Iterator[float]:
        yield self.x
        yield self.y
        yield self.z

    def __add__(self, other: "Vec3") -> "Vec3":
        return Vec3(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other: "Vec3") -> "Vec3":
        return Vec3(self.x - other.x, self.y - other.y, self.z - other.z)

    def __neg__(self) -> "Vec3":
        return Vec3(-self.x, -self.y, -self.z)

    def __mul__(self, other: Union["Vec3", Number]) -> "Vec3":
        if isinstance(other, Vec3):
            return Vec3(self.x * other.x, self.y * other.y, self.z * other.z)
        return Vec3(self.x * other, self.y * other, self.z * other)

    def __rmul__(self, scalar: Number) -> "Vec3":
        return self * scalar

    def __truediv__(self, scalar: Number) -> "Vec3":
        if scalar == 0:
            raise ZeroDivisionError("向量不能除以 0")
        return Vec3(self.x / scalar, self.y / scalar, self.z / scalar)

    def dot(self, other: "Vec3") -> float:
        return self.x * other.x + self.y * other.y + self.z * other.z

    def cross(self, other: "Vec3") -> "Vec3":
        return Vec3(
            self.y * other.z - self.z * other.y,
            self.z * other.x - self.x * other.z,
            self.x * other.y - self.y * other.x,
        )

    def length_squared(self) -> float:
        return self.dot(self)

    def length(self) -> float:
        return math.sqrt(self.length_squared())

    def normalized(self) -> "Vec3":
        length = self.length()
        if length == 0:
            raise ZeroDivisionError("零向量无法归一化")
        return self / length

    def reflect(self, normal: "Vec3") -> "Vec3":
        """关于单位法线反射。"""
        return self - normal * (2.0 * self.dot(normal))

    def refract(self, normal: "Vec3", eta_ratio: float) -> "Vec3":
        """斯涅尔定律折射，``normal`` 需为单位向量且与入射方向相反。"""
        cos_theta = min((-self).dot(normal), 1.0)
        sin2_theta = 1.0 - cos_theta * cos_theta
        sin2_refracted = eta_ratio * eta_ratio * sin2_theta
        if sin2_refracted > 1.0:
            raise ValueError("发生全反射，调用方应先判断")
        return (self + normal * cos_theta) * eta_ratio - normal * math.sqrt(
            1.0 - sin2_refracted
        )

    def near_zero(self, epsilon: float = 1e-8) -> bool:
        return (
            abs(self.x) < epsilon
            and abs(self.y) < epsilon
            and abs(self.z) < epsilon
        )

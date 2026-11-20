from __future__ import annotations

import math
import unittest

from raytracer.vec3 import Vec3


class Vec3Test(unittest.TestCase):
    def test_add_sub_neg(self) -> None:
        a = Vec3(1, 2, 3)
        b = Vec3(4, 5, 6)
        self.assertEqual(tuple(a + b), (5.0, 7.0, 9.0))
        self.assertEqual(tuple(b - a), (3.0, 3.0, 3.0))
        self.assertEqual(tuple(-a), (-1.0, -2.0, -3.0))

    def test_scalar_mul_div(self) -> None:
        a = Vec3(1, -2, 3)
        self.assertEqual(tuple(a * 2), (2.0, -4.0, 6.0))
        self.assertEqual(tuple(2 * a), (2.0, -4.0, 6.0))
        self.assertEqual(tuple(a / 2), (0.5, -1.0, 1.5))
        with self.assertRaises(ZeroDivisionError):
            _ = a / 0

    def test_component_wise_mul(self) -> None:
        self.assertEqual(
            tuple(Vec3(1, 2, 3) * Vec3(4, 5, 6)), (4.0, 10.0, 18.0)
        )

    def test_dot_cross(self) -> None:
        self.assertEqual(Vec3(1, 2, 3).dot(Vec3(4, -5, 6)), 12.0)
        self.assertEqual(tuple(Vec3(1, 0, 0).cross(Vec3(0, 1, 0))), (0.0, 0.0, 1.0))

    def test_length_and_normalize(self) -> None:
        a = Vec3(3, 4, 0)
        self.assertEqual(a.length_squared(), 25.0)
        self.assertEqual(a.length(), 5.0)
        unit = a.normalized()
        self.assertAlmostEqual(unit.length(), 1.0)
        with self.assertRaises(ZeroDivisionError):
            Vec3().normalized()

    def test_reflect(self) -> None:
        reflected = Vec3(1, -1, 0).reflect(Vec3(0, 1, 0))
        self.assertEqual(tuple(reflected), (1.0, 1.0, 0.0))

    def test_refract_straight_through(self) -> None:
        refracted = Vec3(0, -1, 0).refract(Vec3(0, 1, 0), 0.5)
        self.assertAlmostEqual(refracted.x, 0.0)
        self.assertAlmostEqual(refracted.y, -1.0)
        self.assertAlmostEqual(refracted.z, 0.0)

    def test_refract_total_internal_reflection(self) -> None:
        with self.assertRaises(ValueError):
            Vec3(1, 0, 0).refract(Vec3(0, 1, 0), 2.0)

    def test_near_zero(self) -> None:
        self.assertTrue(Vec3(0, 0, 0).near_zero())
        self.assertFalse(Vec3(0.1, 0, 0).near_zero())

    def test_repr(self) -> None:
        self.assertEqual(repr(Vec3(1, 2, 3)), "Vec3(1, 2, 3)")


if __name__ == "__main__":
    unittest.main()

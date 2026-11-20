from __future__ import annotations

import unittest

from raytracer.material import Dielectric, Lambertian, Metal, random_unit_vector
from raytracer.geometry import Hit
from raytracer.vec3 import Vec3

import random


class RandomVectorTest(unittest.TestCase):
    def test_unit_length(self) -> None:
        rng = random.Random(7)
        for _ in range(50):
            vector = random_unit_vector(rng)
            self.assertAlmostEqual(vector.length(), 1.0, places=9)


class LambertianTest(unittest.TestCase):
    def test_solid_color(self) -> None:
        material = Lambertian(Vec3(0.9, 0.1, 0.1))
        self.assertEqual(tuple(material.color_at(Vec3(1, 2, 3))), (0.9, 0.1, 0.1))

    def test_checker_pattern(self) -> None:
        material = Lambertian(
            Vec3(1, 1, 1), checker_scale=1.0, checker_albedo=Vec3(0, 0, 0)
        )
        first = material.color_at(Vec3(0.5, 0, 0.5))
        second = material.color_at(Vec3(1.5, 0, 0.5))
        self.assertNotEqual(tuple(first), tuple(second))

    def test_scatter(self) -> None:
        material = Lambertian(Vec3(0.5, 0.5, 0.5))
        hit = Hit(1.0, Vec3(0, 0, 0), Vec3(0, 1, 0), material)
        result = material.scatter(Vec3(0, -1, 0), hit, random.Random(1))
        self.assertIsNotNone(result)
        assert result is not None
        attenuation, direction = result
        self.assertEqual(tuple(attenuation), (0.5, 0.5, 0.5))
        self.assertGreater(direction.dot(hit.normal), 0)


class MetalTest(unittest.TestCase):
    def test_reflection_direction(self) -> None:
        material = Metal(Vec3(1, 1, 1), fuzz=0.0)
        hit = Hit(1.0, Vec3(0, 0, 0), Vec3(0, 1, 0), material)
        result = material.scatter(Vec3(1, -1, 0), hit, random.Random(2))
        self.assertIsNotNone(result)
        assert result is not None
        _, direction = result
        self.assertGreater(direction.y, 0)
        self.assertAlmostEqual(direction.x, 1.0)

    def test_fuzz_clamped(self) -> None:
        self.assertEqual(Metal(Vec3(1, 1, 1), fuzz=5.0).fuzz, 1.0)

    def test_negative_fuzz(self) -> None:
        with self.assertRaises(ValueError):
            Metal(Vec3(1, 1, 1), fuzz=-0.1)


class DielectricTest(unittest.TestCase):
    def test_refracts_normal_incidence(self) -> None:
        material = Dielectric(1.5)
        hit = Hit(1.0, Vec3(0, 0, 0), Vec3(0, 1, 0), material)
        result = material.scatter(Vec3(0, -1, 0), hit, random.Random(3))
        self.assertIsNotNone(result)
        assert result is not None
        attenuation, direction = result
        self.assertEqual(tuple(attenuation), (1.0, 1.0, 1.0))
        self.assertAlmostEqual(direction.y, -1.0)

    def test_invalid_index(self) -> None:
        with self.assertRaises(ValueError):
            Dielectric(1.0)


if __name__ == "__main__":
    unittest.main()

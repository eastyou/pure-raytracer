from __future__ import annotations

import math
import unittest

from raytracer.geometry import Hit, Plane, Sphere, World
from raytracer.material import Lambertian
from raytracer.vec3 import Vec3


class SphereTest(unittest.TestCase):
    def setUp(self) -> None:
        self.material = Lambertian(Vec3(0.5, 0.5, 0.5))
        self.sphere = Sphere(Vec3(0, 0, -5), 1.0, self.material)

    def test_hit_front(self) -> None:
        hit = self.sphere.hit(Vec3(0, 0, 0), Vec3(0, 0, -1), 0.001, math.inf)
        self.assertIsNotNone(hit)
        assert hit is not None
        self.assertAlmostEqual(hit.t, 4.0)
        self.assertAlmostEqual(hit.point.z, -4.0)
        self.assertEqual(tuple(hit.normal), (0.0, 0.0, 1.0))

    def test_hit_inside(self) -> None:
        hit = self.sphere.hit(Vec3(0, 0, -5), Vec3(0, 0, -1), 0.001, math.inf)
        self.assertIsNotNone(hit)
        assert hit is not None
        self.assertAlmostEqual(hit.t, 1.0)
        self.assertEqual(tuple(hit.normal), (0.0, 0.0, 1.0))

    def test_hit_second_root(self) -> None:
        hit = self.sphere.hit(Vec3(0, 0, 0), Vec3(0, 0, -1), 4.5, math.inf)
        self.assertIsNotNone(hit)
        assert hit is not None
        self.assertAlmostEqual(hit.t, 6.0)

    def test_miss(self) -> None:
        self.assertIsNone(
            self.sphere.hit(Vec3(0, 2, 0), Vec3(0, 0, -1), 0.001, math.inf)
        )
        self.assertIsNone(
            self.sphere.hit(Vec3(0, 0, 0), Vec3(0, 0, 1), 0.001, math.inf)
        )

    def test_invalid_radius(self) -> None:
        with self.assertRaises(ValueError):
            Sphere(Vec3(0, 0, 0), 0.0, self.material)

    def test_hit_returns_material(self) -> None:
        hit = self.sphere.hit(Vec3(0, 0, 0), Vec3(0, 0, -1), 0.001, math.inf)
        assert hit is not None
        self.assertIs(hit.material, self.material)


class PlaneTest(unittest.TestCase):
    def setUp(self) -> None:
        self.material = Lambertian(Vec3(0.5, 0.5, 0.5))
        self.plane = Plane(Vec3(0, 0, 0), Vec3(0, 1, 0), self.material)

    def test_hit_from_above(self) -> None:
        hit = self.plane.hit(Vec3(0, 2, 0), Vec3(0, -1, 0), 0.001, math.inf)
        self.assertIsNotNone(hit)
        assert hit is not None
        self.assertAlmostEqual(hit.t, 2.0)
        self.assertEqual(tuple(hit.normal), (0.0, 1.0, 0.0))

    def test_parallel_ray(self) -> None:
        self.assertIsNone(
            self.plane.hit(Vec3(0, 2, 0), Vec3(1, 0, 0), 0.001, math.inf)
        )

    def test_behind_ray(self) -> None:
        self.assertIsNone(
            self.plane.hit(Vec3(0, 2, 0), Vec3(0, 1, 0), 0.001, math.inf)
        )

    def test_invalid_normal(self) -> None:
        with self.assertRaises(ValueError):
            Plane(Vec3(0, 0, 0), Vec3(0, 0, 0), self.material)


class WorldTest(unittest.TestCase):
    def test_returns_closest_hit(self) -> None:
        material = Lambertian(Vec3(0.5, 0.5, 0.5))
        world = World()
        world.add(Sphere(Vec3(0, 0, -5), 1.0, material))
        world.add(Sphere(Vec3(0, 0, -3), 1.0, material))
        hit = world.hit(Vec3(0, 0, 0), Vec3(0, 0, -1))
        self.assertIsNotNone(hit)
        assert hit is not None
        self.assertAlmostEqual(hit.t, 2.0)

    def test_empty_world(self) -> None:
        self.assertIsNone(World().hit(Vec3(0, 0, 0), Vec3(0, 0, -1)))


class HitTest(unittest.TestCase):
    def test_fields(self) -> None:
        hit = Hit(1.0, Vec3(0, 0, 0), Vec3(0, 1, 0), None)
        self.assertEqual(hit.t, 1.0)
        self.assertEqual(tuple(hit.point), (0.0, 0.0, 0.0))


if __name__ == "__main__":
    unittest.main()

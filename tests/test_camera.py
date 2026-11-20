from __future__ import annotations

import random
import unittest

from raytracer.camera import Camera
from raytracer.vec3 import Vec3


class CameraTest(unittest.TestCase):
    def setUp(self) -> None:
        self.camera = Camera(
            lookfrom=Vec3(0, 0, 3),
            lookat=Vec3(0, 0, 0),
            vup=Vec3(0, 1, 0),
            vertical_fov=60.0,
            aspect=16.0 / 9.0,
        )

    def test_center_ray_points_at_target(self) -> None:
        origin, direction = self.camera.ray(0.5, 0.5, random.Random(1))
        self.assertEqual(tuple(origin), (0.0, 0.0, 3.0))
        self.assertAlmostEqual(direction.x, 0.0)
        self.assertAlmostEqual(direction.y, 0.0)
        self.assertAlmostEqual(direction.z, -1.0)

    def test_direction_is_unit_length(self) -> None:
        rng = random.Random(2)
        for s in (0.0, 0.3, 0.5, 1.0):
            _, direction = self.camera.ray(s, 1.0 - s, rng)
            self.assertAlmostEqual(direction.length(), 1.0, places=9)

    def test_aperture_moves_origin(self) -> None:
        camera = Camera(
            lookfrom=Vec3(0, 0, 3),
            lookat=Vec3(0, 0, 0),
            vup=Vec3(0, 1, 0),
            vertical_fov=60.0,
            aspect=1.0,
            aperture=0.2,
            focus_distance=3.0,
        )
        rng = random.Random(3)
        origins = {tuple(camera.ray(0.5, 0.5, rng)[0]) for _ in range(20)}
        self.assertGreater(len(origins), 1)

    def test_invalid_parameters(self) -> None:
        with self.assertRaises(ValueError):
            Camera(Vec3(0, 0, 1), Vec3(0, 0, 0), Vec3(0, 1, 0), 60.0, 0.0)
        with self.assertRaises(ValueError):
            Camera(Vec3(0, 0, 1), Vec3(0, 0, 0), Vec3(0, 1, 0), 180.0, 1.0)


if __name__ == "__main__":
    unittest.main()

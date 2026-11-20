from __future__ import annotations

import random
import unittest

from raytracer.camera import Camera
from raytracer.demo import build_demo_scene
from raytracer.geometry import Sphere, World
from raytracer.material import Lambertian
from raytracer.render import _to_byte, render, trace
from raytracer.vec3 import Vec3


class GammaTest(unittest.TestCase):
    def test_bounds(self) -> None:
        self.assertEqual(_to_byte(-1.0), 0)
        self.assertEqual(_to_byte(0.0), 0)
        self.assertEqual(_to_byte(1.0), 255)
        self.assertEqual(_to_byte(2.0), 255)

    def test_midpoint(self) -> None:
        self.assertEqual(_to_byte(0.25), 127)


class TraceTest(unittest.TestCase):
    def test_blank_world_returns_sky(self) -> None:
        color = trace(World(), Vec3(0, 0, 0), Vec3(0, 1, 0), 3, random.Random(1))
        self.assertGreater(color.x, 0.0)
        self.assertGreater(color.z, 0.0)

    def test_hit_sphere_darkens(self) -> None:
        world = World()
        world.add(
            Sphere(Vec3(0, 0, -2), 1.0, Lambertian(Vec3(0.5, 0.5, 0.5)))
        )
        camera = Camera(
            Vec3(0, 0, 0), Vec3(0, 0, -1), Vec3(0, 1, 0), 60.0, 1.0
        )
        origin, direction = camera.ray(0.5, 0.5, random.Random(1))
        color = trace(world, origin, direction, 5, random.Random(1))
        self.assertLess(color.length(), 2.0)


class RenderTest(unittest.TestCase):
    def test_output_size_and_range(self) -> None:
        world, camera = build_demo_scene(aspect=1.5)
        pixels = render(world, camera, 12, 8, samples=1, max_depth=2, seed=5)
        self.assertEqual(len(pixels), 12 * 8 * 3)
        self.assertTrue(all(0 <= value <= 255 for value in pixels))

    def test_deterministic_with_seed(self) -> None:
        world, camera = build_demo_scene(aspect=1.5)
        first = render(world, camera, 8, 6, samples=2, max_depth=2, seed=11)
        second = render(world, camera, 8, 6, samples=2, max_depth=2, seed=11)
        self.assertEqual(first, second)

    def test_different_seed_changes_noise(self) -> None:
        world, camera = build_demo_scene(aspect=1.5)
        first = render(world, camera, 8, 6, samples=2, max_depth=2, seed=1)
        second = render(world, camera, 8, 6, samples=2, max_depth=2, seed=2)
        self.assertNotEqual(first, second)

    def test_progress_callback(self) -> None:
        world, camera = build_demo_scene(aspect=1.5)
        calls = []
        render(
            world,
            camera,
            4,
            3,
            samples=1,
            max_depth=1,
            seed=1,
            progress=lambda done, total: calls.append((done, total)),
        )
        self.assertEqual(len(calls), 3)
        self.assertEqual(calls[-1], (3, 3))

    def test_invalid_parameters(self) -> None:
        world, camera = build_demo_scene(aspect=1.5)
        with self.assertRaises(ValueError):
            render(world, camera, 0, 10)
        with self.assertRaises(ValueError):
            render(world, camera, 10, 10, samples=0)
        with self.assertRaises(ValueError):
            render(world, camera, 10, 10, max_depth=0)


if __name__ == "__main__":
    unittest.main()

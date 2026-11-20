"""示例场景：经典三球 + 棋盘地面。"""

from __future__ import annotations

from typing import Tuple

from .camera import Camera
from .geometry import Sphere, World
from .material import Dielectric, Lambertian, Metal
from .vec3 import Vec3


def build_demo_scene(aspect: float = 16.0 / 9.0) -> Tuple[World, Camera]:
    world = World()

    ground = Lambertian(
        albedo=Vec3(0.72, 0.7, 0.68),
        checker_scale=4.0,
        checker_albedo=Vec3(0.18, 0.2, 0.22),
    )
    world.add(Sphere(Vec3(0.0, -1000.0, 0.0), 1000.0, ground))

    world.add(Sphere(Vec3(0.0, 0.5, 0.0), 0.5, Dielectric(1.5)))
    world.add(Sphere(Vec3(-1.05, 0.5, 0.0), 0.5, Lambertian(Vec3(0.85, 0.28, 0.26))))
    world.add(Sphere(Vec3(1.05, 0.5, 0.0), 0.5, Metal(Vec3(0.92, 0.88, 0.72), 0.04)))
    world.add(Sphere(Vec3(0.55, 0.18, 1.15), 0.18, Metal(Vec3(0.3, 0.62, 0.9), 0.18)))

    camera = Camera(
        lookfrom=Vec3(0.0, 1.15, 4.4),
        lookat=Vec3(0.0, 0.55, 0.0),
        vup=Vec3(0.0, 1.0, 0.0),
        vertical_fov=32.0,
        aspect=aspect,
        aperture=0.06,
        focus_distance=(Vec3(0.0, 1.15, 4.4) - Vec3(0.0, 0.5, 0.0)).length(),
    )
    return world, camera

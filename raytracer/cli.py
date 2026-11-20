"""命令行入口：渲染示例场景并写出 PNG。"""

from __future__ import annotations

import argparse
import sys
import time
from typing import Optional, Sequence

from .demo import build_demo_scene
from .png import write_png
from .render import ProgressCallback, render


def _progress_printer() -> ProgressCallback:
    """返回一个进度打印器，每 10% 输出一次。"""
    state = {"step": 0}

    def callback(done: int, height: int) -> None:
        percent = done * 100 // height
        if percent >= state["step"] + 10 or done == height:
            state["step"] = percent // 10 * 10
            print("  渲染进度 %3d%%" % percent, flush=True)

    return callback


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="raytrace",
        description="纯 Python 光线追踪渲染器：输出 PNG，零第三方依赖",
    )
    parser.add_argument("-o", "--output", default="render.png", help="输出文件路径")
    parser.add_argument("-W", "--width", type=int, default=480, help="图片宽度")
    parser.add_argument("-H", "--height", type=int, default=270, help="图片高度")
    parser.add_argument("-s", "--samples", type=int, default=8, help="每像素采样数")
    parser.add_argument("-d", "--depth", type=int, default=5, help="最大光线弹射次数")
    parser.add_argument("--seed", type=int, default=2026, help="随机种子，保证结果可复现")
    parser.add_argument("--quiet", action="store_true", help="不输出进度")
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    if args.width <= 0 or args.height <= 0:
        print("错误: 宽高必须大于 0", file=sys.stderr)
        return 2
    if args.samples <= 0 or args.depth <= 0:
        print("错误: 采样数与深度必须大于 0", file=sys.stderr)
        return 2

    world, camera = build_demo_scene(aspect=args.width / args.height)
    progress = None if args.quiet else _progress_printer()
    started = time.time()
    try:
        pixels = render(
            world,
            camera,
            width=args.width,
            height=args.height,
            samples=args.samples,
            max_depth=args.depth,
            seed=args.seed,
            progress=progress,
        )
        write_png(args.output, args.width, args.height, pixels)
    except OSError as exc:
        print("写入失败: %s" % exc, file=sys.stderr)
        return 1
    elapsed = time.time() - started
    print(
        "完成: %s (%dx%d, %d spp) 用时 %.2f 秒"
        % (args.output, args.width, args.height, args.samples, elapsed)
    )
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())

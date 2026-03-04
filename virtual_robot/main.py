from __future__ import annotations

import argparse
import random

from .env import Environment
from .robot import Robot, Direction
from .ui_cli import run_cli
from .ui_tk import run_tk


def build_demo_env(width: int, height: int, *, seed: int = 7) -> Environment:
    random.seed(seed)
    env = Environment(width=width, height=height)
    env.set_goal(width - 2, height - 2)

    obs = set()

    # vertical wall with a gap
    vx = width // 2
    for y in range(1, height - 1):
        if y == height // 3:
            continue
        obs.add((vx, y))

    # horizontal wall with a gap
    hy = height // 2
    for x in range(1, width - 1):
        if x == width // 3:
            continue
        obs.add((x, hy))

    # small block
    bx, by = width // 4, height // 4
    for dx in range(2):
        for dy in range(2):
            obs.add((bx + dx, by + dy))

    obs.discard((0, 0))
    obs.discard(env.goal)

    env.add_obstacles(obs)
    return env


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Virtual Robot Simulation"
    )
    p.add_argument("--gui", action="store_true", help="Run with a simple Tkinter GUI")
    p.add_argument("--width", type=int, default=12)
    p.add_argument("--height", type=int, default=12)
    p.add_argument("--delay", type=float, default=0.15, help="CLI delay between steps (seconds)")
    p.add_argument("--max-steps", type=int, default=300)
    p.add_argument("--dynamic", type=int, default=1, help="Number of dynamic obstacles (0 disables)")
    p.add_argument("--seed", type=int, default=7, help="Random seed")
    p.add_argument("--cell-size", type=int, default=32, help="GUI cell size (pixels)")
    p.add_argument("--delay-ms", type=int, default=120, help="GUI delay per step (milliseconds)")
    return p.parse_args()


def main() -> None:
    args = parse_args()

    env = build_demo_env(args.width, args.height, seed=args.seed)
    robot = Robot(x=0, y=0, direction=Direction.EAST)

    # Dynamic obstacles (optional but helps demonstrate obstacle avoidance)
    if args.dynamic > 0:
        random.seed(args.seed)
        env.seed_dynamic_obstacles(args.dynamic, avoid={robot.pos})

    if args.gui:
        run_tk(env, robot, max_steps=args.max_steps, cell_size=args.cell_size, delay_ms=args.delay_ms)
    else:
        run_cli(env, robot, delay=args.delay, max_steps=args.max_steps)


if __name__ == "__main__":
    main()

"""
main.py
What it does:
This file connects everything together.

It:
 - Creates the Environment
 - Adds obstacles
 - Sets the goal
 - Creates the Robot
 - Creates the Simulation
 - Starts the simulation
 - It is like the “project builder”.
"""

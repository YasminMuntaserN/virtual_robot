from __future__ import annotations

import time

from .env import Environment
from .robot import Robot, Direction, RobotState
from .sim import Simulation


def _dir_char(d: Direction) -> str:
    return {
        Direction.NORTH: "^",
        Direction.EAST:  ">",
        Direction.SOUTH: "v",
        Direction.WEST:  "<",
    }[d]


def render_cli(env: Environment, robot: Robot, step: int) -> None:
    for y in range(env.height):
        row = []
        for x in range(env.width):
            c = (x, y)
            if c == robot.pos:
                row.append(_dir_char(robot.direction))
            elif c == env.goal:
                row.append("G")
            elif c in env.dynamic_obstacles:
                row.append("X")
            elif c in env.obstacles:
                row.append("#")
            else:
                row.append(".")
        print(" ".join(row))
    print(f"step: {step} | state: {robot.state.name} | pos: ({robot.x},{robot.y}) | dir: {robot.direction.name}")
    print()


def run_cli(env: Environment, robot: Robot, *, delay: float = 0.15, max_steps: int = 300) -> None:
    sim = Simulation(env=env, robot=robot, max_steps=max_steps)

    while True:
        render_cli(env, robot, sim.current_step)

        cont = sim.step()
        if not cont:
            break
        time.sleep(delay)

    print("Simulation finished.")
    if robot.state == RobotState.FINISHED:
        print("✅ Robot reached the goal!")
    else:
        print("⏹️ Stopped (max steps reached or no path).")

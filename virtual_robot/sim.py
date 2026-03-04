from __future__ import annotations

from dataclasses import dataclass
from typing import Set

from .env import Environment
from .robot import Robot, RobotState


@dataclass
class Simulation:
    env: Environment
    robot: Robot
    max_steps: int = 300
    current_step: int = 0

    def step(self) -> bool:
        """Run a single simulation step. Returns True if simulation should continue."""
        # Move dynamic obstacles first (forces reactive avoidance sometimes)
        self.env.update_dynamic_obstacles(avoid={self.robot.pos})

        sensors = self.robot.sense(self.env)
        self.robot.decide(self.env, sensors)

        self.current_step += 1

        if self.robot.state == RobotState.FINISHED:
            return False
        if self.current_step >= self.max_steps:
            return False
        return True

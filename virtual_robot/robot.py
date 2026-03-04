from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Tuple

from .env import Environment, Coord
from .planner import bfs_path


class Direction(Enum):
    NORTH = 0
    EAST = 1
    SOUTH = 2
    WEST = 3


class RobotState(Enum):
    IDLE = 0
    PLANNING = 1
    MOVING = 2
    AVOIDING = 3
    FINISHED = 4


SensorData = Dict[str, str]  # {"front": "CLEAR", "left": "...", "right": "..."}


def _dir_to_delta(d: Direction) -> Tuple[int, int]:
    if d == Direction.NORTH:
        return (0, -1)
    if d == Direction.SOUTH:
        return (0, 1)
    if d == Direction.EAST:
        return (1, 0)
    return (-1, 0)  # WEST


@dataclass
class Robot:
    x: int
    y: int
    direction: Direction = Direction.NORTH
    state: RobotState = RobotState.IDLE

    # BFS path-following
    path: List[Coord] = field(default_factory=list)
    path_index: int = 0

    # avoidance bookkeeping
    avoidance_turns: int = 0

    @property
    def pos(self) -> Coord:
        return (self.x, self.y)

    def turn_left(self) -> None:
        self.direction = Direction((self.direction.value - 1) % 4)

    def turn_right(self) -> None:
        self.direction = Direction((self.direction.value + 1) % 4)

    def next_position(self) -> Coord:
        dx, dy = _dir_to_delta(self.direction)
        return (self.x + dx, self.y + dy)

    def _status_at(self, env: Environment, coord: Coord) -> str:
        x, y = coord
        if not env.is_within_bounds(x, y):
            return "WALL"
        if env.is_goal(x, y):
            return "GOAL"
        if env.is_obstacle(x, y):
            return "OBSTACLE"
        return "CLEAR"

    def sense(self, env: Environment) -> SensorData:
        """Virtual sensors: status of the cell in front/left/right."""
        front = self.next_position()

        left_dir = Direction((self.direction.value - 1) % 4)
        right_dir = Direction((self.direction.value + 1) % 4)

        ldx, ldy = _dir_to_delta(left_dir)
        rdx, rdy = _dir_to_delta(right_dir)

        left = (self.x + ldx, self.y + ldy)
        right = (self.x + rdx, self.y + rdy)

        return {
            "front": self._status_at(env, front),
            "left": self._status_at(env, left),
            "right": self._status_at(env, right),
        }

    def move_forward(self, env: Environment) -> bool:
        nx, ny = self.next_position()
        if not env.is_within_bounds(nx, ny):
            return False
        if env.is_obstacle(nx, ny):
            return False
        self.x, self.y = nx, ny
        return True

    def plan_path(self, env: Environment) -> bool:
        """Compute BFS path from current position to goal."""
        self.state = RobotState.PLANNING
        p = bfs_path(env, self.pos, env.goal)
        self.path = p or []
        self.path_index = 1 if (p and len(p) > 1) else 0
        return bool(p)

    def _face_towards(self, target: Coord) -> None:
        tx, ty = target
        dx, dy = tx - self.x, ty - self.y

        if dx == 1 and dy == 0:
            self.direction = Direction.EAST
        elif dx == -1 and dy == 0:
            self.direction = Direction.WEST
        elif dx == 0 and dy == 1:
            self.direction = Direction.SOUTH
        elif dx == 0 and dy == -1:
            self.direction = Direction.NORTH

    def _follow_planned_step(self, env: Environment) -> bool:
        if not self.path or self.path_index >= len(self.path):
            return False

        target = self.path[self.path_index]
        self._face_towards(target)

        if env.is_obstacle(*target):
            return False

        ok = self.move_forward(env)
        if ok:
            self.path_index += 1
        return ok

    def _avoid_obstacle_reactive(self, env: Environment, sensors: SensorData) -> bool:
        """
        Minimal reactive obstacle avoidance:
        - If front is blocked: turn right (try up to 4 turns).
        - If front is clear: move forward one step.
        """
        if sensors["front"] in ("OBSTACLE", "WALL"):
            self.turn_right()
            self.avoidance_turns += 1
            return False
        return self.move_forward(env)

    def decide(self, env: Environment, sensors: SensorData) -> None:
        """
        FSM + BFS + Obstacle Avoidance.

        IDLE/PLANNING -> compute BFS
        MOVING -> follow BFS path
        AVOIDING -> reactive turning/move, then re-plan BFS
        FINISHED -> stop
        """
        # goal check first
        if env.is_goal(self.x, self.y):
            self.state = RobotState.FINISHED
            return

        if self.state in (RobotState.IDLE, RobotState.PLANNING):
            has_path = self.plan_path(env)
            self.state = RobotState.MOVING if has_path else RobotState.AVOIDING
            self.avoidance_turns = 0
            return

        if self.state == RobotState.MOVING:
            ok = self._follow_planned_step(env)
            if ok:
                return
            self.state = RobotState.AVOIDING
            self.avoidance_turns = 0
            return

        if self.state == RobotState.AVOIDING:
            _ = self._avoid_obstacle_reactive(env, sensors)

            # if we turned a full circle and still blocked, just try re-plan anyway
            if self.avoidance_turns >= 4:
                self.avoidance_turns = 0

            # try to re-plan frequently so we return to BFS navigation
            _ = self.plan_path(env)
            self.state = RobotState.MOVING if self.path else RobotState.AVOIDING
            return

        # FINISHED
        if self.state == RobotState.FINISHED:
            return

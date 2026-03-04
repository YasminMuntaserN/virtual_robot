from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, Set, Tuple, List
import random

Coord = Tuple[int, int]


@dataclass
class Environment:
    """
    Coordinate-based 2D environment.

    - Bounds: 0 <= x < width, 0 <= y < height
    - Obstacles are stored as coordinate sets (NOT a grid matrix).
    - Optional dynamic obstacles can move each simulation step.
    """
    width: int
    height: int
    obstacles: Set[Coord] = field(default_factory=set)
    goal: Coord = (0, 0)
    dynamic_obstacles: Set[Coord] = field(default_factory=set)

    def is_within_bounds(self, x: int, y: int) -> bool:
        return 0 <= x < self.width and 0 <= y < self.height

    def is_obstacle(self, x: int, y: int) -> bool:
        return (x, y) in self.obstacles or (x, y) in self.dynamic_obstacles

    def is_goal(self, x: int, y: int) -> bool:
        return (x, y) == self.goal

    def add_obstacles(self, coords: Iterable[Coord]) -> None:
        for c in coords:
            if self.is_within_bounds(*c) and c != self.goal:
                self.obstacles.add(c)

    def set_goal(self, x: int, y: int) -> None:
        if not self.is_within_bounds(x, y):
            raise ValueError("Goal is out of bounds")
        self.goal = (x, y)
        # Keep goal cell free
        self.obstacles.discard(self.goal)
        self.dynamic_obstacles.discard(self.goal)

    def seed_dynamic_obstacles(self, count: int, *, avoid: Set[Coord]) -> None:
        """Place N dynamic obstacles randomly (not on avoid/goal/static obstacles)."""
        free: List[Coord] = []
        for y in range(self.height):
            for x in range(self.width):
                c = (x, y)
                if c == self.goal or c in self.obstacles or c in avoid:
                    continue
                free.append(c)
        random.shuffle(free)
        self.dynamic_obstacles = set(free[: max(0, count)])

    def update_dynamic_obstacles(self, *, avoid: Set[Coord]) -> None:
        """
        Move each dynamic obstacle one step randomly (4-neighborhood),
        staying in bounds and not colliding with static obstacles, goal, or 'avoid' coords.
        """
        if not self.dynamic_obstacles:
            return

        def neighbors(c: Coord):
            x, y = c
            yield (x + 1, y)
            yield (x - 1, y)
            yield (x, y + 1)
            yield (x, y - 1)

        new_positions: Set[Coord] = set()
        current = list(self.dynamic_obstacles)
        random.shuffle(current)

        occupied = set(self.obstacles) | {self.goal} | set(avoid)

        for c in current:
            options = []
            for n in neighbors(c):
                if not self.is_within_bounds(*n):
                    continue
                if n in occupied:
                    continue
                options.append(n)

            nxt = random.choice(options) if options else c
            if nxt in new_positions:
                nxt = c
            new_positions.add(nxt)

        self.dynamic_obstacles = new_positions

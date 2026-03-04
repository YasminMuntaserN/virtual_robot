from __future__ import annotations

from collections import deque
from typing import Dict, List, Optional

from .env import Environment, Coord


def bfs_path(env: Environment, start: Coord, goal: Coord) -> Optional[List[Coord]]:
    """
    Breadth-First Search on a 4-connected grid.
    Returns a list of coordinates including start and goal, or None if no path exists.

    - Treats obstacles (static + dynamic) as blocked.
    - Unweighted (each move costs 1).
    """
    if start == goal:
        return [start]

    sx, sy = start
    gx, gy = goal

    if not env.is_within_bounds(sx, sy) or not env.is_within_bounds(gx, gy):
        return None
    if env.is_obstacle(sx, sy) or env.is_obstacle(gx, gy):
        return None

    q = deque([start])
    parent: Dict[Coord, Optional[Coord]] = {start: None}

    def neighbors(c: Coord):
        x, y = c
        yield (x + 1, y)
        yield (x - 1, y)
        yield (x, y + 1)
        yield (x, y - 1)

    while q:
        cur = q.popleft()
        if cur == goal:
            break
        for nxt in neighbors(cur):
            if nxt in parent:
                continue
            if not env.is_within_bounds(*nxt):
                continue
            if env.is_obstacle(*nxt):
                continue
            parent[nxt] = cur
            q.append(nxt)

    if goal not in parent:
        return None

    # reconstruct path
    path: List[Coord] = []
    cur: Optional[Coord] = goal
    while cur is not None:
        path.append(cur)
        cur = parent[cur]
    path.reverse()
    return path

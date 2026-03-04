from __future__ import annotations

import tkinter as tk
from dataclasses import dataclass
import math

from .env import Environment
from .robot import Robot, Direction, RobotState
from .sim import Simulation


@dataclass
class TkConfig:
    cell_size: int = 32
    delay_ms: int = 120


class TkViewer:
    def __init__(self, env: Environment, robot: Robot, *, max_steps: int = 300, cfg: TkConfig | None = None):
        self.env = env
        self.robot = robot
        self.cfg = cfg or TkConfig()
        self.sim = Simulation(env=env, robot=robot, max_steps=max_steps)

        self.root = tk.Tk()
        self.root.title("Virtual Robot (BFS + FSM + Obstacle Avoidance)")

        w = env.width * self.cfg.cell_size
        h = env.height * self.cfg.cell_size

        self.canvas = tk.Canvas(self.root, width=w, height=h)
        self.canvas.pack()

        controls = tk.Frame(self.root)
        controls.pack(fill="x")

        self.btn = tk.Button(controls, text="Start", command=self.toggle)
        self.btn.pack(side="left", padx=8, pady=8)

        self.status = tk.Label(controls, text="")
        self.status.pack(side="left", padx=8)

        self.running = False
        self.draw()

    def toggle(self):
        self.running = not self.running
        self.btn.config(text="Pause" if self.running else "Start")
        if self.running:
            self.tick()

    def draw_cell(self, x: int, y: int, fill: str):
        s = self.cfg.cell_size
        x0, y0 = x * s, y * s
        x1, y1 = x0 + s, y0 + s
        self.canvas.create_rectangle(x0, y0, x1, y1, fill=fill, outline="gray")

    def _dir_angle(self, d: Direction) -> float:
        return {
            Direction.EAST: 0,
            Direction.NORTH: -90,
            Direction.WEST: 180,
            Direction.SOUTH: 90,
        }[d]

    def draw_robot(self):
        s = self.cfg.cell_size
        cx = self.robot.x * s + s / 2
        cy = self.robot.y * s + s / 2
        r = s * 0.35

        # base triangle (pointing up)
        pts = [(cx, cy - r), (cx - r, cy + r), (cx + r, cy + r)]

        ang = math.radians(self._dir_angle(self.robot.direction))
        cos_a, sin_a = math.cos(ang), math.sin(ang)

        def rot(px, py):
            dx, dy = px - cx, py - cy
            rx = dx * cos_a - dy * sin_a
            ry = dx * sin_a + dy * cos_a
            return (cx + rx, cy + ry)

        rpts = [rot(px, py) for px, py in pts]
        flat = [v for p in rpts for v in p]
        self.canvas.create_polygon(*flat, fill="red", outline="black")

    def draw(self):
        self.canvas.delete("all")

        for y in range(self.env.height):
            for x in range(self.env.width):
                c = (x, y)
                if c in self.env.obstacles:
                    self.draw_cell(x, y, "black")
                elif c in self.env.dynamic_obstacles:
                    self.draw_cell(x, y, "orange")
                elif c == self.env.goal:
                    self.draw_cell(x, y, "green")
                else:
                    self.draw_cell(x, y, "white")

        self.draw_robot()

        self.status.config(
            text=f"step {self.sim.current_step}/{self.sim.max_steps} | state={self.robot.state.name} | pos=({self.robot.x},{self.robot.y})"
        )

    def tick(self):
        if not self.running:
            return

        cont = self.sim.step()
        self.draw()

        if not cont:
            self.running = False
            self.btn.config(text="Start")
            if self.robot.state == RobotState.FINISHED:
                self.status.config(text=self.status.cget("text") + "  ✅ reached goal")
            else:
                self.status.config(text=self.status.cget("text") + "  ⏹ stopped")
            return

        self.root.after(self.cfg.delay_ms, self.tick)

    def run(self):
        self.root.mainloop()


def run_tk(env: Environment, robot: Robot, *, max_steps: int = 300, cell_size: int = 32, delay_ms: int = 120):
    viewer = TkViewer(env, robot, max_steps=max_steps, cfg=TkConfig(cell_size=cell_size, delay_ms=delay_ms))
    viewer.run()

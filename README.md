# Virtual Robot Simulation

A minimal, structured **virtual autonomous robot** project in **Python**.
The robot runs in a **2D coordinate-based environment** (x, y), senses its surroundings using **virtual sensors**, makes decisions using a **Finite State Machine (FSM)**, and reaches a **goal** using **Breadth-First Search (BFS)** path planning.  
A simple **reactive obstacle avoidance** behavior is also included (useful when obstacles block the planned path).

This project is designed to satisfy the **core mandatory requirements** of a “virtual robot” course project, plus extension tracks:
- **Path Planning (BFS)**
- **Finite State Machine (FSM)**
- **Obstacle Avoidance**
- **User Interface**: CLI visualization + optional Tkinter GUI

---

## Features

### Mandatory requirements ✅
- **2D environment**: coordinate-based map with bounds and obstacles
- **Robot model**: position `(x, y)`, orientation `(N/E/S/W)`, internal state
- **Movement system**: move forward, turn left/right, collision prevention
- **Decision-making**: rule/algorithm-based logic using virtual sensor data
- **Simulation loop**: step-by-step updates of robot + environment

### Extension tracks ✅
- **Path Planning (BFS)**: robot plans a shortest path on a 4-neighborhood grid
- **FSM**: organized behavior using explicit states and transitions
- **Obstacle Avoidance**: reactive turning/moving when blocked
- **UI**:
  - CLI renderer (prints the map every step)
  - Optional Tkinter GUI (simple colored grid + robot arrow)

### Optional (small) extra
- **Dynamic obstacles** (orange cells in GUI / `X` in CLI) that move every step.
  This makes avoidance behavior more visible and realistic.

---

## Requirements

- Python **3.10+** recommended (project uses modern type hints)
- No external libraries required
- **Tkinter** for GUI (often included with Python on Windows/macOS; on some Linux distros it may require installation)

---

## Project structure

```
virtual_robot/
  README.md
  run.py                      # entry point (CLI by default, GUI with --gui)
  virtual_robot/
    __init__.py
    env.py                    # coordinate-based environment + obstacles sets
    planner.py                # BFS path planning
    robot.py                  # robot model + FSM + sensing + avoidance
    sim.py                    # simulation loop (steps)
    ui_cli.py                 # CLI visualization
    ui_tk.py                  # Tkinter GUI visualization
    main.py                   # CLI args + demo environment setup
```

---

## Quick start

### 1) Run CLI mode (default)

From the project folder:

```bash
python run.py
```

You will see a printed map that updates every step.

### 2) Run GUI mode (Tkinter)

```bash
python run.py --gui
```

Press **Start** to begin (and Pause/Start to toggle).

---

## Map legend

### CLI legend
- `^  >  v  <` : robot (shows facing direction)
- `#` : static obstacle
- `X` : dynamic obstacle (moves each step)
- `G` : goal
- `.` : empty cell

### GUI legend (colors)
- White: empty
- Black: static obstacle
- Orange: dynamic obstacle
- Green: goal
- Red triangle: robot (direction)

---

## Command-line options

Run `python run.py -h` to see all options. Common ones:

```bash
python run.py --width 12 --height 12
python run.py --dynamic 0               # disable dynamic obstacles
python run.py --max-steps 500
python run.py --delay 0.05              # CLI step delay (seconds)
python run.py --seed 7                  # affects dynamic obstacle movement
```

GUI-specific:
```bash
python run.py --gui --cell-size 28 --delay-ms 120
```

---

## How the simulation works

Each simulation step:

1. **Environment update** (optional): dynamic obstacles move one cell randomly.
2. **Sense**: robot reads virtual sensors:
   - `"front"`, `"left"`, `"right"` each returns one of:
     - `CLEAR`, `OBSTACLE`, `WALL`, `GOAL`
3. **Decide**: robot uses FSM + BFS + avoidance to choose an action.
4. **Act**: robot may turn and/or move forward.
5. Stop when robot reaches goal or max steps is reached.

---

## Algorithms and design

### Coordinate-based environment
This project does **not** store a grid matrix. Instead:
- Static obstacles are stored in a **set**: `obstacles = {(x1,y1), (x2,y2), ...}`
- Dynamic obstacles are stored in a **set**: `dynamic_obstacles = {...}`
- Goal is a single coordinate: `goal = (x, y)`

Checking collisions becomes simple:
- Out of bounds → blocked
- If `(x,y)` in either obstacle set → blocked

---

### BFS path planning (shortest path)
The planner uses BFS on the 4-connected neighborhood:
- From `(x, y)` the robot can move to:
  - `(x+1, y)`, `(x-1, y)`, `(x, y+1)`, `(x, y-1)`
- BFS guarantees the **shortest number of steps** in an unweighted grid.
- Time complexity: **O(V + E)**, for a grid it’s effectively **O(width × height)**.

Output of BFS:
- A list of coordinates: `[start, ..., goal]`
- Robot follows it one step at a time.

---

### FSM (Finite State Machine)
The robot uses explicit states:

- `IDLE` / `PLANNING`  
  Compute BFS path to the goal.

- `MOVING`  
  Follow the next BFS path coordinate:
  - Turn to face the next cell
  - Move forward (if still clear)

- `AVOIDING`  
  If the planned next cell is blocked (often due to dynamic obstacles):
  - **Reactive behavior**:
    - If front is blocked: turn right (up to 4 turns)
    - If front is clear: move forward
  - Re-run BFS frequently to return to optimal navigation

- `FINISHED`  
  Stop when the robot reaches the goal.

Why FSM helps:
- Makes behavior predictable and easy to explain in a presentation
- Keeps logic organized instead of large nested `if` statements

---

## Customizing the environment

The demo environment is built in:
- `virtual_robot/main.py` → `build_demo_env(...)`

You can modify:
- Goal position (`env.set_goal(x, y)`)
- Static obstacle coordinates (`env.add_obstacles({...})`)
- Dynamic obstacle count (`--dynamic N`)

Tip: Ensure the start `(0,0)` and goal cells are not obstacles.

---

## Troubleshooting

### GUI doesn’t open / Tkinter not found
- Use CLI mode instead: `python run.py`
- On some Linux systems, install Tkinter (example package name: `python3-tk`)

### Robot doesn’t reach the goal
- Increase max steps: `--max-steps 800`
- Disable dynamic obstacles: `--dynamic 0`
- Ensure the goal is reachable (no fully-blocking walls)

---

## Academic integrity notes (for later submission)
- All logic here is implemented directly in Python (no robotics/AI libraries that solve the problem automatically).
- If you add external references (e.g., BFS explanation sources), cite them in the final submission.

---

## Where to look first in the code
- `virtual_robot/robot.py`:
  - `sense(...)`
  - `decide(...)` (FSM + avoidance + BFS follow)
- `virtual_robot/planner.py`:
  - `bfs_path(...)`
- `virtual_robot/env.py`:
  - obstacle sets + dynamic obstacle movement
- `virtual_robot/sim.py`:
  - step-by-step simulation loop

---

## Demo suggestions (5–7 minutes)
If you need a clean demo:
1. Run with **dynamic obstacles disabled** (`--dynamic 0`) to show BFS path planning.
2. Run again with **dynamic obstacles enabled** to show obstacle avoidance + replanning.
3. Briefly explain FSM states and transitions.

---

## License
For coursework / educational use.

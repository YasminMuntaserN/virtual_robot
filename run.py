"""
Convenience entry point.

Usage:
  python run.py            # CLI
  python run.py --gui      # Tkinter GUI
"""

from virtual_robot.main import main

if __name__ == "__main__":
    main()


"""
run.py
What it does:
This is the entry point of the project.

When we run:
python run.py

It:
 - Reads command line arguments
 - Chooses CLI or GUI mode
 - Calls main.py

"""
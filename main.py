"""
Graph Navigator — entry point.
Run:  python main.py
"""

import sys
import os

# Ensure project root is on the path when running from any directory
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from view.console_view import ConsoleView


def main():
    view = ConsoleView()
    view.run()


if __name__ == "__main__":
    main()

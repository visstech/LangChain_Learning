"""
todo.py
-------
The simplest possible to-do list: one task per line in a text file.
This keeps the project beginner-friendly — no database needed yet.
Later, you could swap this for a real to-do app's API (Todoist, Notion, etc).
"""

TODO_FILE = "todo.txt"


def get_todos() -> list:
    """
    Read today's to-do tasks from todo.txt, one task per line.
    Returns an empty list if the file doesn't exist yet.
    """
    try:
        with open(TODO_FILE, "r") as f:
            # Strip whitespace and skip any blank lines
            tasks = [line.strip() for line in f if line.strip()]
        return tasks
    except FileNotFoundError:
        return []


if __name__ == "__main__":
    print(get_todos())

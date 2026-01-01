## Python-Specific Guidelines

| Purpose | Command |
|---------|---------|
| Run tests | `pytest -q` |
| Format code | `black .` |
| Type check | `mypy .` |
| Install deps | `pip install -r requirements.txt` |
| Virtual env | `python -m venv venv && source venv/bin/activate` |

## Entry Points

{python_entry_points}

## Common Patterns

- Use `pathlib.Path` instead of `os.path`
- Type hints required for all functions
- Docstrings follow Google style

## Python Project

### Dependencies

| File | Purpose |
|------|---------|
| `requirements.txt` | Pip dependencies |
| `pyproject.toml` | Project configuration (PEP 518) |

### Common Commands

| Task | Command |
|------|---------|
| Install deps | `pip install -e .` |
| Run tests | `pytest -q --tb=short` |
| Coverage | `pytest --cov=src --cov-report=term-missing` |
| Lint | `ruff check .` |
| Format | `ruff format .` |

### Config Injection (into project.json)

```json
{
  "project_type": "python",
  "dev_server_port": 8000,
  "test_command": "pytest -q --tb=short",
  "health_check": ""
}
```

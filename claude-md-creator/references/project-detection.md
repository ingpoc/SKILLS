# Project Detection Reference

## Detection Markers

### Language Detection

| Marker | Language | Package Manager |
|--------|----------|----------------|
| `package.json` | TypeScript/JavaScript | npm |
| `requirements.txt` | Python | pip |
| `pyproject.toml` | Python | uv/pip |
| `Cargo.toml` | Rust | cargo |
| `go.mod` | Go | go |
| `Gemfile` | Ruby | bundle |
| `pom.xml` | Java | Maven |
| `build.gradle` | Java/Kotlin | Gradle |
| `composer.json` | PHP | composer |

### Framework Detection (Node.js)

| Dependency | Framework |
|------------|-----------|
| `next` | Next.js |
| `vite` + `react` | Vite React |
| `react` | React |
| `vue` | Vue |
| `svelte` | Svelte |
| `nuxt` | Nuxt |

### Framework Detection (Python)

| Dependency | Framework |
|------------|-----------|
| `fastapi` | FastAPI |
| `starlette` | FastAPI |
| `django` | Django |
| `flask` | Flask |
| `tornado` | Tornado |
| `aiohttp` | aiohttp |

## Command Extraction

### From package.json

```json
{
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "test": "vitest",
    "lint": "eslint ."
  }
}
```

Extracted as:
- `dev_command`: `npm run dev`
- `build_command`: `npm run build`
- `test_command`: `npm test`

### From pyproject.toml

```toml
[tool.pytest.ini_options]
test_command = "pytest -q"
```

## Adding New Frameworks

To add framework detection:

1. Edit `detect-project.py`
2. Add to framework detection:
```python
if "your-framework" in deps:
    result["framework"] = "YourFramework"
```

3. Create template in `assets/framework-templates/your-framework.md`
4. Map in `generate-claude-md.py`:
```python
framework_map = {
    "yourframework": "your-framework.md",
    # ...
}
```

## Port Detection

Common dev server ports:
- Next.js: 3000
- Vite: 5173
- Create React App: 3000
- FastAPI: 8000
- Django: 8000
- Flask: 5000

Detected from:
- `package.json` → proxy settings
- `vite.config.ts` → server.port
- `.env` files → PORT variable

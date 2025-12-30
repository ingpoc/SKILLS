# Project Detection Patterns

## Detection Flow

```bash
#!/bin/bash
# scripts/detect-project.sh

detect_project_type() {
    if [ -f "package.json" ]; then
        if grep -q "next" package.json; then echo "nextjs"
        elif grep -q "react" package.json; then echo "react"
        elif grep -q "express" package.json; then echo "express"
        else echo "node"
        fi
    elif [ -f "requirements.txt" ] || [ -f "pyproject.toml" ]; then
        if [ -f "manage.py" ]; then echo "django"
        elif grep -q "fastapi" requirements.txt 2>/dev/null; then echo "fastapi"
        elif grep -q "flask" requirements.txt 2>/dev/null; then echo "flask"
        else echo "python"
        fi
    elif [ -f "Cargo.toml" ]; then echo "rust"
    elif [ -f "go.mod" ]; then echo "go"
    elif [ -f "pom.xml" ]; then echo "java-maven"
    elif [ -f "build.gradle" ]; then echo "java-gradle"
    else echo "unknown"
    fi
}
```

## Project Signatures

| Project Type | Key Files | Additional Checks |
|--------------|-----------|-------------------|
| **Next.js** | package.json, next.config.js | `"next"` in dependencies |
| **React** | package.json, src/App.tsx | `"react"` in dependencies |
| **FastAPI** | requirements.txt, main.py | `fastapi` in requirements |
| **Django** | manage.py, settings.py | Django imports |
| **Flask** | app.py, requirements.txt | `flask` in requirements |
| **Express** | package.json, server.js | `"express"` in dependencies |
| **Rust** | Cargo.toml, src/main.rs | - |
| **Go** | go.mod, main.go | - |

## Structure Detection

### Python Project Structure

```python
def detect_python_structure(root: str) -> dict:
    structure = {
        "type": "python",
        "package_manager": None,
        "test_framework": None,
        "has_docker": False,
        "has_ci": False
    }

    # Package manager
    if exists("pyproject.toml"):
        if "poetry" in read("pyproject.toml"):
            structure["package_manager"] = "poetry"
        else:
            structure["package_manager"] = "pip"
    elif exists("requirements.txt"):
        structure["package_manager"] = "pip"

    # Test framework
    if exists("pytest.ini") or exists("conftest.py"):
        structure["test_framework"] = "pytest"
    elif exists("tests/") and glob("tests/test_*.py"):
        structure["test_framework"] = "pytest"

    # Docker
    structure["has_docker"] = exists("Dockerfile")

    # CI
    structure["has_ci"] = (
        exists(".github/workflows/") or
        exists(".gitlab-ci.yml") or
        exists("Jenkinsfile")
    )

    return structure
```

### Node Project Structure

```python
def detect_node_structure(root: str) -> dict:
    pkg = read_json("package.json")

    structure = {
        "type": "node",
        "framework": detect_node_framework(pkg),
        "package_manager": detect_node_pm(),
        "test_framework": detect_node_tests(pkg),
        "typescript": exists("tsconfig.json"),
        "has_docker": exists("Dockerfile"),
        "has_ci": exists(".github/workflows/")
    }

    return structure

def detect_node_framework(pkg: dict) -> str:
    deps = {**pkg.get("dependencies", {}), **pkg.get("devDependencies", {})}

    if "next" in deps: return "nextjs"
    if "nuxt" in deps: return "nuxt"
    if "express" in deps: return "express"
    if "fastify" in deps: return "fastify"
    if "react" in deps: return "react"
    if "vue" in deps: return "vue"
    return "node"

def detect_node_pm() -> str:
    if exists("pnpm-lock.yaml"): return "pnpm"
    if exists("yarn.lock"): return "yarn"
    if exists("bun.lockb"): return "bun"
    return "npm"
```

## Project Config Output

```json
{
  "project": {
    "name": "my-project",
    "type": "fastapi",
    "language": "python",
    "version": "3.11"
  },
  "structure": {
    "source_dir": "src/",
    "test_dir": "tests/",
    "config_dir": "config/"
  },
  "tooling": {
    "package_manager": "poetry",
    "test_framework": "pytest",
    "linter": "ruff",
    "formatter": "black"
  },
  "commands": {
    "install": "poetry install",
    "test": "pytest",
    "lint": "ruff check .",
    "format": "black .",
    "run": "uvicorn main:app --reload"
  },
  "features": {
    "docker": true,
    "ci": true,
    "database": "postgresql"
  }
}
```

## Auto-Detection Script

```bash
#!/bin/bash
# scripts/full-detect.sh

echo "{"
echo '  "project_type": "'$(detect_project_type)'",'

# Detect structure
echo '  "has_tests": '$([ -d "tests" ] || [ -d "test" ] && echo "true" || echo "false")','
echo '  "has_docker": '$([ -f "Dockerfile" ] && echo "true" || echo "false")','
echo '  "has_ci": '$([ -d ".github/workflows" ] && echo "true" || echo "false")','

# Detect database
if grep -r "postgresql\|postgres" . --include="*.py" --include="*.json" --include="*.yaml" -q 2>/dev/null; then
    echo '  "database": "postgresql",'
elif grep -r "mysql" . --include="*.py" --include="*.json" --include="*.yaml" -q 2>/dev/null; then
    echo '  "database": "mysql",'
elif grep -r "sqlite" . --include="*.py" --include="*.json" --include="*.yaml" -q 2>/dev/null; then
    echo '  "database": "sqlite",'
else
    echo '  "database": null,'
fi

# Entry points
echo '  "entry_points": ['
find . -name "main.py" -o -name "app.py" -o -name "index.ts" -o -name "server.js" 2>/dev/null | head -3 | while read f; do
    echo "    \"$f\","
done
echo '  ]'
echo "}"
```

## Project-Specific Initialization

| Project Type | Init Steps |
|--------------|------------|
| **FastAPI** | Check uvicorn, verify routes, test /health |
| **Django** | Check migrations, verify settings, test admin |
| **Next.js** | Check next.config, verify pages, test build |
| **React** | Check vite/webpack config, verify components |
| **Express** | Check routes, verify middleware, test endpoints |

## Health Check by Project Type

```python
HEALTH_CHECKS = {
    "fastapi": [
        "curl -s localhost:8000/health",
        "curl -s localhost:8000/docs"
    ],
    "django": [
        "python manage.py check",
        "python manage.py migrate --check"
    ],
    "nextjs": [
        "npm run build",
        "curl -s localhost:3000"
    ],
    "express": [
        "curl -s localhost:3000/health"
    ]
}
```

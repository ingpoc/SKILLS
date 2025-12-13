# File Structure

## Overview

The Two-Agent Framework relies on a specific file and directory structure to function properly. This structure enables automatic discovery of components, consistent behavior across projects, and seamless integration between agents. Understanding this structure is essential for both implementing new projects and integrating the framework into existing codebases.

## Complete Directory Structure

```
project-root/
├── .claude/                           # Framework configuration and state
│   ├── agents/                       # Agent definitions (local override)
│   │   ├── initializer-agent.md      # Project planning agent
│   │   └── coding-agent.md           # Feature implementation agent
│   │
│   ├── skills/                       # Custom skills
│   │   └── progress-harness/         # Progress tracking skill
│   │       ├── SKILL.md              # Skill definition
│   │       ├── references/           # Documentation references
│   │       ├── assets/               # Templates and scripts
│   │       │   ├── init.sh.template
│   │       │   └── feature-list.template.json
│   │       ├── examples/             # Example implementations
│   │       └── scripts/              # Utility scripts
│   │           ├── validate-progress.py
│   │           └── migrate-features.py
│   │
│   ├── progress/                     # Progress tracking files
│   │   ├── feature-list.json         # Master feature database
│   │   ├── session-state.json        # Session recovery data
│   │   └── claude-progress.txt       # Human-readable progress log
│   │
│   ├── hooks/                        # Enforcement scripts
│   │   ├── pre-tool-guard.sh         # Block unauthorized edits
│   │   ├── post-tool-guard.sh        # Remind about progress
│   │   ├── session-progress-check.sh # Detect abnormal exits
│   │   ├── verify-coding-agent.sh    # Verify progress updated
│   │   └── session-end.sh            # Mark session complete
│   │
│   └── settings.json                 # Claude Code configuration
│
├── .mcp.json                         # MCP server configuration
│
├── docs/                             # Project documentation
│   ├── README.md                     # Project overview
│   ├── API.md                        # API documentation
│   ├── DEPLOYMENT.md                 # Deployment guide
│   └── CLAUDE.md                     # Claude-specific guidelines
│
├── src/                              # Source code
│   ├── components/                   # Reusable components
│   ├── services/                     # Business logic
│   ├── utils/                        # Utility functions
│   └── types/                        # Type definitions
│
├── tests/                            # Test files
│   ├── unit/                         # Unit tests
│   ├── integration/                  # Integration tests
│   └── e2e/                          # End-to-end tests
│
├── scripts/                          # Build and deployment scripts
│   ├── build.sh                      # Build script
│   ├── deploy.sh                     # Deployment script
│   └── test.sh                       # Test runner
│
├── config/                           # Configuration files
│   ├── database.json                 # Database config
│   ├── api.json                      # API config
│   └── environment.json              # Environment settings
│
├── init.sh                           # Environment initialization
├── README.md                         # Project README
├── package.json                      # Node.js dependencies
├── .gitignore                        # Git ignore rules
└── .github/                          # GitHub workflows
    └── workflows/                    # CI/CD pipelines
```

## Critical Files and Their Formats

### 1. .claude/settings.json

Controls Claude Code behavior and hook activation:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "/bin/bash .claude/hooks/pre-tool-guard.sh",
            "statusMessage": "Checking tool authorization..."
          }
        ]
      }
    ],
    "PostToolUse": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "/bin/bash .claude/hooks/post-tool-guard.sh",
            "statusMessage": "Remember to update progress..."
          }
        ]
      }
    ],
    "SessionStart": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "/bin/bash .claude/hooks/session-progress-check.sh",
            "statusMessage": "Checking for incomplete sessions..."
          }
        ]
      }
    ],
    "SubagentStop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "/bin/bash .claude/hooks/verify-coding-agent.sh",
            "statusMessage": "Verifying progress updates..."
          }
        ]
      }
    ],
    "SessionEnd": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "/bin/bash .claude/hooks/session-end.sh",
            "statusMessage": "Marking session complete..."
          }
        ]
      }
    ]
  }
}
```

### 2. .claude/progress/feature-list.json

The master feature database with exact article format:

```json
{
  "project_name": "my-application",
  "total_features": 247,
  "completed": 0,
  "pending": 247,
  "categories": {
    "authentication": {
      "priority": "high",
      "description": "User authentication and authorization",
      "features": [
        {
          "id": "AUTH-001",
          "name": "User Registration",
          "description": "New user registration with email verification",
          "category": "functional",
          "steps": [
            "Navigate to registration page",
            "Enter valid email address",
            "Enter password",
            "Click register button",
            "Verify email in inbox",
            "Confirm email verification code"
          ],
          "passes": false,
          "dependencies": [],
          "estimated_hours": 4,
          "created_at": "2025-01-08T10:00:00Z",
          "updated_at": "2025-01-08T10:00:00Z",
          "notes": ""
        }
      ]
    }
  },
  "metadata": {
    "created_at": "2025-01-08T10:00:00Z",
    "last_updated": "2025-01-08T10:00:00Z",
    "version": "1.0.0",
    "total_categories": 12
  }
}
```

### 3. .claude/progress/session-state.json

Session recovery and tracking:

```json
{
  "session_number": 1,
  "started_at": "2025-01-08T10:00:00Z",
  "agent_type": "coding",
  "status": "active",
  "last_feature_id": "AUTH-001",
  "current_feature": {
    "id": "AUTH-002",
    "name": "User Login",
    "started_at": "2025-01-08T11:30:00Z",
    "progress": "in_progress"
  },
  "heartbeat": {
    "last_heartbeat": "2025-01-08T12:45:00Z",
    "interval_seconds": 300,
    "missed_heartbeats": 0
  },
  "session_summary": {
    "features_completed": 1,
    "features_blocked": 0,
    "total_time_minutes": 95,
    "notes": "Good progress on auth flow"
  },
  "git_state": {
    "branch": "main",
    "last_commit": "feat(AUTH-001): Implement user registration",
    "uncommitted_changes": false
  }
}
```

### 4. .claude/progress/claude-progress.txt

Human-readable progress log:

```
# My Application Development Progress
# Started: 2025-01-08 | Last Updated: 2025-01-08

## Phase 1: Authentication (In Progress)
- [x] AUTH-001: User Registration (4h)
  - Email verification integrated
  - Password strength validation added
  - Rate limiting implemented
- [-] AUTH-002: User Login (currently working)
  - JWT session management done
  - Need to add remember me functionality

## Session 1 - 2025-01-08 (2h)
### Completed:
- [x] Set up project structure
- [x] Implement user registration
- [x] Add email verification

### Next:
- [ ] Complete login feature
- [ ] Add password reset
```

### 5. init.sh

Environment initialization script:

```bash
#!/bin/bash
# Environment setup for My Application

set -e

echo "Setting up My Application..."

# Check prerequisites
command -v node >/dev/null 2>&1 || { echo "Node.js is required"; exit 1; }
command -v git >/dev/null 2>&1 || { echo "Git is required"; exit 1; }

# Install dependencies
echo "Installing dependencies..."
npm install

# Set up database
echo "Setting up database..."
npm run db:migrate

# Create environment file
if [ ! -f .env ]; then
  cp .env.example .env
  echo "Created .env file - please update with your values"
fi

# Install git hooks
echo "Installing git hooks..."
cp .claude/hooks/* .git/hooks/
chmod +x .git/hooks/*

# Build project
echo "Building project..."
npm run build

echo "Setup complete! Run 'npm run dev' to start development"
```

### 6. .gitignore

Git ignore pattern for Two-Agent projects:

```
# Dependencies
node_modules/
__pycache__/
*.pyc
venv/
env/

# Build outputs
dist/
build/
*.egg-info/

# Environment files
.env
.env.local
.env.*.local

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Framework specific
.claude/progress/backups/
.claude/sessions/
.claude/temp/

# Logs
logs/
*.log

# Test coverage
coverage/
.nyc_output/
.coverage
```

## File Naming Conventions

### Feature IDs
Format: `CATEGORY-NUMBER`
- Categories: 3-letter uppercase codes (AUTH, UI, API, DB, etc.)
- Numbers: 3-digit sequential starting from 001
- Examples: AUTH-001, UI-015, API-042

### File Names
- **Components**: PascalCase (UserProfile.tsx)
- **Services**: camelCase (userService.js)
- **Utilities**: camelCase with prefix (helpers.js, validators.js)
- **Tests**: *.test.js, *.spec.js
- **Hooks**: kebab-case with .sh extension (session-progress-check.sh)

### Commit Messages
Format: `type(scope): description`
- Types: feat, fix, docs, style, refactor, test, chore
- Scope: feature ID when applicable
- Example: `feat(AUTH-001): Implement user registration`

## Auto-Discovery Mechanisms

### Agents
- Global: `~/.claude/agents/`
- Project: `.claude/agents/` (overrides global)
- Discovered by: Claude Code at startup

### Skills
- Global: `~/.claude/skills/`
- Project: `.claude/skills/` (overrides global)
- Discovered by: Both Claude Code and Agent SDK

### Hooks
- Location: `.claude/hooks/`
- Configuration: `.claude/settings.json`
- Discovered by: Native Claude Code hook system

### MCP Servers
- Configuration: `.mcp.json` at project root
- Discovered by: Both Claude Code and Agent SDK (different servers)

## Project Type Specific Structures

### Web Application (React/Next.js)

```
web-app/
├── src/
│   ├── app/                     # Next.js app router
│   ├── components/              # React components
│   │   ├── ui/                  # Reusable UI components
│   │   └── features/            # Feature-specific components
│   ├── hooks/                   # Custom React hooks
│   ├── lib/                     # Utility libraries
│   └── types/                   # TypeScript types
├── public/                      # Static assets
├── styles/                      # CSS/styled-components
└── next.config.js               # Next.js config
```

### API Service (Node.js/Express)

```
api-service/
├── src/
│   ├── controllers/             # Route controllers
│   ├── services/                # Business logic
│   ├── models/                  # Data models
│   ├── middleware/              # Express middleware
│   ├── routes/                  # Route definitions
│   ├── utils/                   # Utilities
│   └── config/                  # Configuration
├── tests/                       # Test files
└── swagger/                     # API documentation
```

### CLI Tool

```
cli-tool/
├── src/
│   ├── commands/                # Command implementations
│   ├── lib/                     # Core library
│   ├── utils/                   # Utilities
│   └── types/                   # TypeScript types
├── bin/                         # Executable scripts
├── man/                         # Manual pages
└── completion/                  # Shell completion scripts
```

### Mobile App (React Native)

```
mobile-app/
├── src/
│   ├── components/              # React Native components
│   ├── screens/                 # App screens
│   ├── navigation/              # Navigation config
│   ├── services/                # API services
│   ├── store/                   # State management
│   └── utils/                   # Utilities
├── android/                     # Android-specific code
├── ios/                         # iOS-specific code
└── __tests__/                   # Jest tests
```

## Template Files

### feature-list.template.json

```json
{
  "project_name": "{{PROJECT_NAME}}",
  "total_features": {{FEATURE_COUNT}},
  "completed": 0,
  "pending": {{FEATURE_COUNT}},
  "categories": {
    "{{CATEGORY_1}}": {
      "priority": "high",
      "description": "{{CATEGORY_1_DESCRIPTION}}",
      "features": [
        {
          "id": "{{CATEGORY_1}}-001",
          "name": "{{FEATURE_1_NAME}}",
          "description": "{{FEATURE_1_DESCRIPTION}}",
          "category": "functional",
          "steps": [
            "{{STEP_1}}",
            "{{STEP_2}}",
            "{{STEP_3}}"
          ],
          "passes": false,
          "dependencies": [],
          "estimated_hours": 4,
          "created_at": "{{TIMESTAMP}}",
          "updated_at": "{{TIMESTAMP}}",
          "notes": ""
        }
      ]
    }
  },
  "metadata": {
    "created_at": "{{TIMESTAMP}}",
    "last_updated": "{{TIMESTAMP}}",
    "version": "1.0.0",
    "total_categories": {{CATEGORY_COUNT}}
  }
}
```

### init.sh.template

```bash
#!/bin/bash
# Environment setup for {{PROJECT_NAME}}

set -e

PROJECT_NAME="{{PROJECT_NAME}}"
FRAMEWORK="{{FRAMEWORK}}"
DATABASE="{{DATABASE}}"

echo "Setting up $PROJECT_NAME..."

# Framework-specific setup
case $FRAMEWORK in
  "react")
    echo "Setting up React project..."
    npm create react-app . --template typescript
    ;;
  "next")
    echo "Setting up Next.js project..."
    npx create-next-app@latest . --typescript --tailwind --eslint
    ;;
  "express")
    echo "Setting up Express project..."
    npm init -y
    npm install express
    ;;
esac

# Install dependencies
echo "Installing dependencies..."
npm install

# Database setup
if [ "$DATABASE" != "none" ]; then
  echo "Setting up $DATABASE..."
  # Database-specific commands
fi

# Initialize Two-Agent Framework
echo "Initializing Two-Agent Framework..."
mkdir -p .claude/progress
mkdir -p .claude/hooks

echo "Setup complete!"
```

## Integration with Existing Projects

### Migration Steps

1. **Create .claude directory structure**
   ```bash
   mkdir -p .claude/{agents,skills,progress,hooks}
   ```

2. **Add settings.json**
   ```bash
   cp ~/.claude/skills/progress-harness/assets/settings.json .claude/
   ```

3. **Initialize feature list**
   ```bash
   # Use initializer-agent to break down existing features
   ```

4. **Set up hooks**
   ```bash
   cp ~/.claude/skills/progress-harness/assets/hooks/*.sh .claude/hooks/
   chmod +x .claude/hooks/*.sh
   ```

5. **Create initial progress**
   ```bash
   echo "# Project Progress\n\nStarted on $(date)" > .claude/progress/claude-progress.txt
   ```

### Minimal Structure for Quick Start

For projects wanting to start with minimal setup:

```
project/
├── .claude/
│   ├── progress/
│   │   └── feature-list.json
│   └── settings.json (optional)
└── src/
```

## Validation Scripts

### validate-structure.py

```python
#!/usr/bin/env python3
"""Validate project structure compliance"""

import os
import json
import sys
from pathlib import Path

REQUIRED_DIRS = [
    ".claude",
    ".claude/progress"
]

REQUIRED_FILES = [
    ".claude/progress/feature-list.json"
]

OPTIONAL_FILES = [
    ".claude/settings.json",
    ".claude/progress/session-state.json",
    ".claude/progress/claude-progress.txt",
    "init.sh"
]

def validate_structure():
    """Validate project structure"""
    errors = []
    warnings = []

    # Check required directories
    for dir_path in REQUIRED_DIRS:
        if not os.path.isdir(dir_path):
            errors.append(f"Missing required directory: {dir_path}")

    # Check required files
    for file_path in REQUIRED_FILES:
        if not os.path.isfile(file_path):
            errors.append(f"Missing required file: {file_path}")

    # Check optional files
    for file_path in OPTIONAL_FILES:
        if not os.path.isfile(file_path):
            warnings.append(f"Missing optional file: {file_path}")

    # Validate feature-list.json
    if os.path.isfile(".claude/progress/feature-list.json"):
        try:
            with open(".claude/progress/feature-list.json") as f:
                data = json.load(f)

            # Check required fields
            if "categories" not in data:
                errors.append("feature-list.json missing 'categories' field")

            # Check features have steps
            for category in data.get("categories", {}).values():
                for feature in category.get("features", []):
                    if "steps" not in feature:
                        errors.append(f"Feature {feature.get('id', 'unknown')} missing 'steps' array")

        except json.JSONDecodeError as e:
            errors.append(f"Invalid JSON in feature-list.json: {e}")

    return errors, warnings

def main():
    errors, warnings = validate_structure()

    if errors:
        print("❌ Errors found:")
        for error in errors:
            print(f"  - {error}")

    if warnings:
        print("⚠️  Warnings:")
        for warning in warnings:
            print(f"  - {warning}")

    if not errors and not warnings:
        print("✅ Project structure is valid")

    return 1 if errors else 0

if __name__ == "__main__":
    sys.exit(main())
```

## Best Practices

### 1. Directory Organization
- Keep .claude directory clean and organized
- Use subdirectories for different component types
- Maintain separation between code and configuration

### 2. File Management
- Commit all .claude files except sensitive data
- Use .gitignore to exclude temporary files
- Keep feature-list.json under version control

### 3. Naming Consistency
- Follow established naming conventions
- Use descriptive names for clarity
- Maintain consistency across the project

### 4. Documentation
- Document project-specific conventions
- Include CLAUDE.md files in each major directory
- Keep README files up to date

### 5. Security
- Never commit API keys or passwords
- Use environment variables for configuration
- Review .gitignore regularly

## Troubleshooting

### Common Issues

1. **Hooks Not Working**
   - Verify .claude/settings.json exists and is valid
   - Check hook scripts are executable
   - Ensure hook paths are correct

2. **Feature List Not Found**
   - Verify .claude/progress/ directory exists
   - Check file permissions
   - Run initializer-agent to create initial list

3. **Agents Not Available**
   - Check agent files are in ~/.claude/agents/
   - Verify agent YAML format is correct
   - Restart Claude Code if needed

4. **Progress Not Tracking**
   - Verify session-state.json is being updated
   - Check heartbeat mechanism is working
   - Review hook outputs for errors

### Recovery Procedures

```bash
# Reset project structure
git checkout HEAD -- .claude/

# Recreate from template
cp -r ~/.claude/skills/progress-harness/assets/template/.claude .

# Validate structure
python3 .claude/scripts/validate-structure.py
```

This comprehensive file structure ensures the Two-Agent Framework functions correctly while maintaining organization and consistency across projects.
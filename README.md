# Claude Code Skills Collection

A curated collection of specialized skills for Claude Code, designed to enhance productivity, enforce best practices, and enable advanced workflows.

## Overview

This repository contains custom Claude Code skills that extend Claude's capabilities with specialized knowledge, workflows, and tool integrations. Each skill provides deep expertise in a specific domain.

## Available Skills

### 🔍 Full Stack Debugger

Systematic debugging workflow for issues spanning UI, backend, and database layers. Combines browser testing, log analysis, code examination, and automated server restarts to iteratively resolve full-stack issues.

**Use cases:**
- Debugging errors that span multiple application layers
- Resolving failing schedulers, import errors, database issues
- Systematic root cause analysis and verification
- API payload problems and configuration errors
- Issues originating in backend but manifesting in UI

**Workflow:**
- **Detection** - Multi-layer error detection (browser UI, backend logs, database state)
- **Analysis** - Root cause identification through code and log analysis
- **Fix** - One issue at a time with proven fix patterns
- **Restart** - Automated server restart with cache clearing
- **Verification** - Browser, API, database, and log verification
- **Iteration** - Continue until all issues resolved

**MCP Integration:**
Integrates with robo-trader-dev MCP tools for 95%+ token-efficient debugging:
- `analyze_logs` - Pattern detection with time windows (98% savings)
- `check_system_health` - Database, queues, API status (97% savings)
- `diagnose_database_locks` - Correlate logs with code patterns (95% savings)
- `suggest_fix` - Known pattern matching with examples (90% savings)

**Triggers:** Debugging full-stack issues, error states in UI, backend failures, database errors, cascading failures

📁 [View skill details](./full-stack-debugger/SKILL.md)

---

### 🎨 Tufte Slide Design

Apply Edward Tufte's data visualization principles from "The Visual Display of Quantitative Information" to create high-impact presentations.

**Use cases:**
- Designing presentations with clarity and precision
- Creating charts and graphs that maximize data-ink ratio
- Reviewing slides for visual excellence
- Transforming complex data into clear visual displays

**Key principles:**
- Maximize data-ink ratio (remove chartjunk)
- Show the data with graphical integrity
- Use small multiples and sparklines for dense information
- Direct labeling instead of legends
- Eliminate decoration that doesn't inform

**Triggers:** "make a slide", "create presentation", "design chart", "visualize data", "review my slides"

📁 [View skill details](./tufte-slide-design/SKILL.md)

---

### 🤖 Two-Agent Harness

A complete two-agent development system based on the research paper "Effective Harnesses for Long-Running Agents". Separates project planning from implementation for complex, multi-session development work.

**Architecture:**
- **Opus** (orchestrator) - Delegates work, never implements directly
- **Initializer Agent** (sonnet) - Breaks down projects into 200+ trackable features
- **Coding Agent** (sonnet) - Implements features one at a time with quality assurance

**Features:**
- Comprehensive project breakdown with feature tracking
- Enforcement hooks to prevent premature implementation
- Session state recovery after crashes
- Progress tracking across sessions
- Git integration for systematic commits

**Use cases:**
- Setting up new complex projects
- Managing multi-session development work
- Enforcing separation between planning and implementation
- Tracking progress on large feature sets

**Triggers:** "set up two-agent system", "install agent harness", "configure Opus delegation"

📁 [View skill details](./two-agent-harness/SKILL.md)

## Installation

### Individual Skill Installation

Each skill can be installed separately by copying its directory to your Claude Code skills location:

```bash
# For user-specific skills
cp -r <skill-name> ~/.claude/skills/

# Or for project-specific skills
cp -r <skill-name> /path/to/project/.claude/skills/
```

### Two-Agent Harness Setup

The two-agent harness includes an automated setup script:

```bash
bash ./two-agent-harness/scripts/setup-two-agent-system.sh
```

This will install agents, hooks, and reference documentation automatically.

## Usage

Skills are automatically available in Claude Code once installed. Claude will invoke them when:
1. You explicitly request the skill by name
2. Your query matches the skill's trigger phrases
3. The task context aligns with the skill's domain

Example:
```
User: "Create a presentation about Q4 sales data"
Claude: [Automatically invokes tufte-slide-design skill]
```

## Skill Structure

Each skill follows this structure:

```
skill-name/
├── SKILL.md              # Skill definition and documentation
├── references/           # Supporting documentation and resources
├── assets/              # Templates, examples, or other assets
└── scripts/             # Automation scripts (if applicable)
```

## Development

### Creating New Skills

To create a new skill:

1. Create a directory with a descriptive name (kebab-case)
2. Add a `SKILL.md` file with frontmatter:
   ```markdown
   ---
   name: skill-name
   description: Brief description of what the skill does and when to use it
   ---

   # Skill Name
   [Detailed documentation]
   ```
3. Add reference materials in `references/` directory
4. Include templates or examples in `assets/` if needed

### Best Practices

- **Clear triggers**: Define specific phrases that should invoke the skill
- **Focused scope**: Each skill should have a single, well-defined purpose
- **Rich references**: Include comprehensive documentation and examples
- **Automated setup**: Provide setup scripts for complex installations

## Contributing

Contributions are welcome! To contribute:

1. Fork the repository
2. Create a new skill or enhance an existing one
3. Test the skill thoroughly with Claude Code
4. Submit a pull request with clear documentation

## Skills Roadmap

Future skills under consideration:
- API design patterns
- Database schema design
- Security review workflows
- Code review checklist
- Testing strategy generator

## License

These skills are provided as-is for use with Claude Code. Each skill may reference external resources that have their own licenses.

## Resources

- [Claude Code Documentation](https://code.claude.com/)
- [Creating Custom Skills Guide](https://docs.anthropic.com/claude-code/skills)
- [Effective Harnesses Research Paper](https://www.anthropic.com/research)
- [Edward Tufte's Visual Display of Quantitative Information](https://www.edwardtufte.com/tufte/books_vdqi)

## Support

For issues or questions:
- Open an issue in this repository
- Check individual skill documentation
- Refer to Claude Code's official documentation

---

**Note:** These skills require Claude Code to be installed and configured. They extend Claude's capabilities but do not modify the core Claude Code system.

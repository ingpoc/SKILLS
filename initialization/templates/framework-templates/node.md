## Node.js Project

### Dependencies

| File | Purpose |
|------|---------|
| `package.json` | NPM dependencies and scripts |

### Common Commands

| Task | Command |
|------|---------|
| Install deps | `npm install` |
| Run tests | `npm test` |
| Lint | `npm run lint` |
| Build | `npm run build` |
| Dev server | `npm run dev` |

### Config Injection (into project.json)

```json
{
  "project_type": "node",
  "dev_server_port": 3000,
  "test_command": "npm test",
  "health_check": "curl -sf http://localhost:3000/health"
}
```

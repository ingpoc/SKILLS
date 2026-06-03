## Go Project

### Dependencies

| File | Purpose |
|------|---------|
| `go.mod` | Go module definition |

### Common Commands

| Task | Command |
|------|---------|
| Run | `go run .` |
| Build | `go build` |
| Test | `go test ./...` |
| Tidy | `go mod tidy` |
| Vet | `go vet ./...` |

### Config Injection (into project.json)

```json
{
  "project_type": "go",
  "dev_server_port": 8080,
  "test_command": "go test ./...",
  "health_check": "curl -sf http://localhost:8080/health"
}
```

## Go-Specific Guidelines

| Purpose | Command |
|---------|---------|
| Build | `go build` |
| Run | `go run .` |
| Test | `go test ./...` |
| Format | `go fmt ./...` |
| Tidy | `go mod tidy` |

## Entry Points

{go_entry_points}

## Common Patterns

- Error handling: always check error returns
- Use `gofmt` before commits
- Package names match directory names

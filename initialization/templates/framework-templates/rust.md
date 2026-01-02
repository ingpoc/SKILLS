## Rust Project

### Dependencies

| File | Purpose |
|------|---------|
| `Cargo.toml` | Rust project config |

### Common Commands

| Task | Command |
|------|---------|
| Build | `cargo build` |
| Run | `cargo run` |
| Test | `cargo test` |
| Check | `cargo check` |
| Lint | `cargo clippy` |

### Config Injection (into project.json)

```json
{
  "project_type": "rust",
  "dev_server_port": 8080,
  "test_command": "cargo test",
  "health_check": "curl -sf http://localhost:8080/health"
}
```

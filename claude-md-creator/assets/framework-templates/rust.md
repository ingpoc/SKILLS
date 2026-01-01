## Rust-Specific Guidelines

| Purpose | Command |
|---------|---------|
| Build | `cargo build` |
| Run | `cargo run` |
| Test | `cargo test` |
| Check | `cargo check` |
| Format | `cargo fmt` |
| Lint | `cargo clippy` |

## Entry Points

{rust_entry_points}

## Common Patterns

- Use `Result<T, E>` for error handling
- Prefer `&str` over `String` for function arguments
- Use `cargo fmt` before commits

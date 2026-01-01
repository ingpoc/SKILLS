# Local Overrides

## My Preferences

- I prefer port 3001 (not 3000)
- Skip slow tests during development
- Use local PostgreSQL instance

## Local Commands

| Purpose | Command |
|---------|---------|
| Start dev (port 3001) | `PORT=3001 npm run dev` |
| Quick tests | `npm test -- --testNamePattern="fast"` |
| Local DB | `docker-compose up postgres` |

## Environment

- Port: 3001
- Database: postgres://localhost:5432/localdb
- Debug: true

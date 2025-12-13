# Testing Strategy

## Overview

Testing in the Two-Agent Framework is not an afterthought—it's an integral part of the development workflow. The framework requires that every feature includes human-readable test procedures in its "steps" array and must be verified before marking as complete. This comprehensive testing strategy ensures reliability, maintains quality, and enables autonomous development across multiple sessions.

## Testing Philosophy

### 1. Test-First Development
- Every feature includes test steps from creation
- Tests drive feature implementation
- Features are not complete until tests pass

### 2. Human-Readable Procedures
- Test steps written for non-technical users
- Clear, actionable instructions
- Verifiable outcomes for each step

### 3. Multi-Level Testing
- Unit tests for individual components
- Integration tests for system interactions
- End-to-end tests for complete user flows

### 4. Browser Automation
- Puppeteer MCP for UI testing
- Real browser interactions
- Cross-browser compatibility

## Testing Pyramid

```
    ▲     E2E Tests (10%)
   / \
  / ▲ \   Integration Tests (20%)
 / ▲ ▲ \
/ ▲ ▲ ▲ \ Unit Tests (70%)
```

### Unit Tests (70%)
- Fast, isolated tests
- Test individual functions and components
- Mock external dependencies
- Run on every commit

### Integration Tests (20%)
- Test component interactions
- API endpoint testing
- Database operations
- Service integrations

### End-to-End Tests (10%)
- Complete user workflows
- Browser automation
- Real data scenarios
- Critical path testing

## Feature Test Format

### The "steps" Array Requirement

Every feature in `feature-list.json` must include a detailed steps array:

```json
{
  "id": "AUTH-001",
  "name": "User Registration",
  "steps": [
    "Navigate to homepage at http://localhost:3000",
    "Click 'Sign Up' button in top navigation",
    "Verify registration page loads with form fields",
    "Enter valid email address in email field",
    "Enter password meeting strength requirements",
    "Confirm password in repeat field",
    "Click 'Create Account' button",
    "Check for email verification message",
    "Verify confirmation email arrives in inbox",
    "Click verification link in email",
    "Confirm successful registration with welcome message"
  ],
  "passes": false
}
```

### Step Writing Guidelines

1. **Start with Navigation**
   - Always begin with getting to the right page
   - Include full URLs when applicable
   - Specify how to access the feature

2. **Be Specific**
   - Name buttons, links, and fields
   - Include exact text to look for
   - Specify expected locations

3. **Include Verification**
   - What should happen after each action
   - What messages should appear
   - What state should change

4. **Test Edge Cases**
   - Invalid inputs
   - Error conditions
   - Boundary values

5. **Write for Humans**
   - Avoid technical jargon
   - Use simple, clear language
   - Assume no prior knowledge

## Testing Workflow

### 1. Before Implementation
```bash
# Verify test environment
npm run test:env
# or
pytest --collect-only

# Start required services
npm run dev &
# or
docker-compose up -d

# Verify services are running
curl http://localhost:3000/health
```

### 2. During Implementation
```bash
# Run unit tests continuously
npm run test:watch
# or
ptw --runner "python -m pytest"

# Run linting
npm run lint
# or
flake8 src/
```

### 3. After Implementation
```bash
# Run full test suite
npm test
# or
pytest

# Run integration tests
npm run test:integration
# or
pytest tests/integration/

# Run E2E tests
npm run test:e2e
# or
pytest tests/e2e/
```

### 4. Feature Verification
```bash
# Get feature steps
FEATURE_ID="AUTH-001"
jq -r --arg id "$FEATURE_ID" \
  '.categories[].features[] | select(.id == $id) | .steps[]' \
  .claude/progress/feature-list.json

# Execute steps manually
echo "Starting manual verification of $FEATURE_ID..."
# [Follow each step manually]

# Mark as passing only after verification
jq --arg id "$FEATURE_ID" \
  '(.categories[].features[] | select(.id == $id)) |= .passes = true' \
  .claude/progress/feature-list.json > .tmp && \
  mv .tmp .claude/progress/feature-list.json
```

## Browser Automation with Puppeteer MCP

### Setup

Install and configure Puppeteer MCP server:

```bash
# Install Puppeteer MCP
npm install -g @anthropic-ai/puppeteer-mcp-server

# Add to .mcp.json
{
  "mcpServers": {
    "puppeteer": {
      "command": "npx",
      "args": ["@anthropic-ai/puppeteer-mcp-server"],
      "env": {
        "PUPPETEER_HEADLESS": "false"
      }
    }
  }
}
```

### Testing Examples

#### Form Submission Test

```javascript
// Test user registration form
await mcp__playwright__browser_navigate("http://localhost:3000/register");

// Fill registration form
await mcp__playwright__browser_fill_form({
  fields: [
    {
      name: "Email",
      type: "textbox",
      ref: "input[name='email']",
      value: "test@example.com"
    },
    {
      name: "Password",
      type: "textbox",
      ref: "input[name='password']",
      value: "SecurePass123!"
    },
    {
      name: "Confirm Password",
      type: "textbox",
      ref: "input[name='confirmPassword']",
      value: "SecurePass123!"
    }
  ]
});

// Submit form
await mcp__playwright__browser_click({
  element: "Create Account button",
  ref: "button[type='submit']"
});

// Verify success
await mcp__playwright__browser_wait_for({
  text: "Account created successfully",
  textGone: "Create Account"
});
```

#### Navigation Test

```javascript
// Test navigation flow
await mcp__playwright__browser_navigate("http://localhost:3000");

// Click login link
await mcp__playwright__browser_click({
  element: "Login link",
  ref: "a[href='/login']"
});

// Verify page title
const title = await mcp__playwright__browser_evaluate({
  function: "() => document.title"
});

console.assert(title.includes("Login"), "Page title should include 'Login'");
```

#### API Response Test

```javascript
// Test API endpoint from browser
const response = await mcp__playwright__browser_evaluate({
  function: "() => fetch('/api/users').then(r => r.json())"
});

console.assert(response.length > 0, "API should return users");
```

## Test Organization

### Directory Structure

```
tests/
├── unit/                           # Unit tests
│   ├── components/                 # Component tests
│   │   ├── Button.test.js
│   │   └── Form.test.js
│   ├── services/                   # Service tests
│   │   ├── authService.test.js
│   │   └── apiService.test.js
│   └── utils/                      # Utility tests
│       ├── validators.test.js
│       └── helpers.test.js
│
├── integration/                    # Integration tests
│   ├── api/                        # API tests
│   │   ├── auth.test.js
│   │   └── users.test.js
│   ├── database/                   # Database tests
│   │   ├── migrations.test.js
│   │   └── models.test.js
│   └── workflows/                  # Workflow tests
│       ├── registration.test.js
│       └── checkout.test.js
│
├── e2e/                           # End-to-end tests
│   ├── auth-flow.test.js
│   ├── shopping-cart.test.js
│   └── admin-panel.test.js
│
├── fixtures/                      # Test data
│   ├── users.json
│   ├── products.json
│   └── orders.json
│
├── helpers/                       # Test utilities
│   ├── setup.js
│   ├── teardown.js
│   └── utils.js
│
└── config/                        # Test configuration
    ├── jest.config.js
    ├── cucumber.js
    └── playwright.config.js
```

### Test Naming Conventions

- **Unit tests**: `[ComponentName].test.js`
- **Integration tests**: `[feature].integration.test.js`
- **E2E tests**: `[user-flow].e2e.test.js`
- **Fixtures**: `[entity].json`
- **Helpers**: `[purpose].helper.js`

### Test File Template

```javascript
// tests/unit/components/Button.test.js
import { render, fireEvent, screen } from '@testing-library/react';
import { Button } from '../../../src/components/Button';

describe('Button Component', () => {
  // Test setup
  beforeEach(() => {
    // Reset mocks, clear DOM, etc.
  });

  // Basic functionality tests
  describe('Rendering', () => {
    it('renders with correct text', () => {
      render(<Button>Click me</Button>);
      expect(screen.getByText('Click me')).toBeInTheDocument();
    });

    it('applies correct className', () => {
      render(<Button className="custom-class">Button</Button>);
      const button = screen.getByRole('button');
      expect(button).toHaveClass('custom-class');
    });
  });

  // Interaction tests
  describe('Interactions', () => {
    it('calls onClick when clicked', () => {
      const handleClick = jest.fn();
      render(<Button onClick={handleClick}>Button</Button>);

      fireEvent.click(screen.getByRole('button'));
      expect(handleClick).toHaveBeenCalledTimes(1);
    });

    it('does not call onClick when disabled', () => {
      const handleClick = jest.fn();
      render(<Button onClick={handleClick} disabled>Button</Button>);

      fireEvent.click(screen.getByRole('button'));
      expect(handleClick).not.toHaveBeenCalled();
    });
  });

  // Edge case tests
  describe('Edge Cases', () => {
    it('handles missing onClick gracefully', () => {
      expect(() => {
        render(<Button>Button</Button>);
        fireEvent.click(screen.getByRole('button'));
      }).not.toThrow();
    });

    it('handles empty children', () => {
      render(<Button></Button>);
      expect(screen.getByRole('button')).toBeInTheDocument();
    });
  });
});
```

## Test Data Management

### Fixtures

```json
// tests/fixtures/users.json
{
  "validUser": {
    "id": 1,
    "email": "test@example.com",
    "password": "SecurePass123!",
    "name": "Test User"
  },
  "invalidUser": {
    "email": "invalid-email",
    "password": "123"
  }
}
```

### Factory Pattern

```javascript
// tests/helpers/factories.js
import { faker } from '@faker-js/faker';

export const createUser = (overrides = {}) => ({
  id: faker.datatype.number(),
  email: faker.internet.email(),
  name: faker.name.fullName(),
  password: faker.internet.password(),
  createdAt: faker.date.past(),
  ...overrides
});

export const createProduct = (overrides = {}) => ({
  id: faker.datatype.number(),
  name: faker.commerce.productName(),
  price: parseFloat(faker.commerce.price()),
  description: faker.lorem.paragraph(),
  ...overrides
});
```

### Database Seeding

```javascript
// tests/helpers/database.js
import { PrismaClient } from '@prisma';
import { createUser, createProduct } from './factories';

const prisma = new PrismaClient();

export async function seedDatabase() {
  // Clean up
  await prisma.user.deleteMany();
  await prisma.product.deleteMany();

  // Seed data
  const users = Array.from({ length: 10 }, () => createUser());
  const products = Array.from({ length: 50 }, () => createProduct());

  await prisma.user.createMany({ data: users });
  await prisma.product.createMany({ data: products });

  return { users, products };
}

export async function cleanupDatabase() {
  await prisma.$disconnect();
}
```

## Continuous Integration Testing

### GitHub Actions

```yaml
# .github/workflows/test.yml
name: Tests

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest

    strategy:
      matrix:
        node-version: [16.x, 18.x, 20.x]

    services:
      postgres:
        image: postgres:14
        env:
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
    - uses: actions/checkout@v3

    - name: Setup Node.js
      uses: actions/setup-node@v3
      with:
        node-version: ${{ matrix.node-version }}
        cache: 'npm'

    - name: Install dependencies
      run: npm ci

    - name: Run linting
      run: npm run lint

    - name: Run unit tests
      run: npm run test:unit

    - name: Run integration tests
      run: npm run test:integration
      env:
        DATABASE_URL: postgresql://postgres:postgres@localhost:5432/test

    - name: Run E2E tests
      run: npm run test:e2e
      env:
        CYPRESS_baseUrl: http://localhost:3000

    - name: Upload coverage
      uses: codecov/codecov-action@v3
```

### Test Coverage

```javascript
// jest.config.js
module.exports = {
  collectCoverage: true,
  coverageDirectory: 'coverage',
  coverageReporters: ['text', 'lcov', 'html'],
  coverageThreshold: {
    global: {
      branches: 80,
      functions: 80,
      lines: 80,
      statements: 80
    }
  },
  collectCoverageFrom: [
    'src/**/*.{js,jsx,ts,tsx}',
    '!src/**/*.d.ts',
    '!src/index.js'
  ]
};
```

## Performance Testing

### Load Testing

```javascript
// tests/performance/load-test.js
import http from 'k6/http';
import { check, sleep } from 'k6';

export let options = {
  stages: [
    { duration: '2m', target: 100 },
    { duration: '5m', target: 100 },
    { duration: '2m', target: 200 },
    { duration: '5m', target: 200 },
    { duration: '2m', target: 0 },
  ],
};

export default function () {
  let response = http.get('http://localhost:3000/api/products');
  check(response, {
    'status is 200': (r) => r.status === 200,
    'response time < 500ms': (r) => r.timings.duration < 500,
  });
  sleep(1);
}
```

### Visual Regression Testing

```javascript
// tests/visual/visual.test.js
import { test, expect } from '@playwright/test';

test('homepage visual regression', async ({ page }) => {
  await page.goto('http://localhost:3000');

  await expect(page).toHaveScreenshot('homepage.png');
});

test('product page visual regression', async ({ page }) => {
  await page.goto('http://localhost:3000/products/1');

  await expect(page).toHaveScreenshot('product-page.png');
});
```

## Testing Best Practices

### 1. Test Structure
- Use AAA pattern: Arrange, Act, Assert
- Keep tests focused and simple
- One assertion per test when possible
- Use descriptive test names

### 2. Test Independence
- Tests should not depend on each other
- Clean up after each test
- Use fresh data for each test
- Avoid shared state

### 3. Mocking and Stubbing
- Mock external dependencies
- Use factory patterns for test data
- Keep mocks close to implementation
- Don't over-mock

### 4. Flaky Tests
- Identify and fix flaky tests
- Use proper waits and retries
- Avoid time-based assertions
- Isolate async operations

### 5. Test Documentation
- Document complex test scenarios
- Explain business logic being tested
- Include setup instructions
- Note any limitations

## Testing Checklist

### Before Marking Feature Complete

- [ ] All unit tests pass
- [ ] Integration tests pass
- [ ] Manual steps verified
- [ ] E2E tests pass
- [ ] Code coverage > 80%
- [ ] Performance tests pass
- [ ] Accessibility tests pass
- [ ] Visual regression tests pass
- [ ] Documentation updated

### Continuous Testing

- [ ] Tests run on every commit
- [ ] Tests run on every PR
- [ ] Coverage reports generated
- [ ] Flaky test alerts configured
- [ ] Performance baselines tracked

## Test Automation Scripts

### Pre-commit Hook

```bash
#!/bin/sh
# .git/hooks/pre-commit

# Run unit tests
npm run test:unit
if [ $? -ne 0 ]; then
  echo "Unit tests failed. Please fix before committing."
  exit 1
fi

# Run linting
npm run lint
if [ $? -ne 0 ]; then
  echo "Linting errors found. Please fix before committing."
  exit 1
fi

# Type checking
npm run type-check
if [ $? -ne 0 ]; then
  echo "Type errors found. Please fix before committing."
  exit 1
fi

echo "All pre-commit checks passed!"
exit 0
```

### Test Runner Script

```bash
#!/bin/bash
# scripts/test-all.sh

echo "Running full test suite..."

# Kill any existing processes
pkill -f "node.*server" || true
pkill -f "npm.*dev" || true

# Start services
echo "Starting services..."
npm run dev &
SERVER_PID=$!

# Wait for server
echo "Waiting for server..."
until curl -s http://localhost:3000 > /dev/null; do
  sleep 2
done

# Run tests
echo "Running tests..."
npm run test:unit
npm run test:integration
npm run test:e2e

# Cleanup
kill $SERVER_PID

echo "Test suite complete!"
```

This comprehensive testing strategy ensures that every feature is thoroughly verified before being marked as complete, maintaining high code quality and reliability throughout the development process.
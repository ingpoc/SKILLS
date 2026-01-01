# API Design Rules

## Purpose

Guidelines for designing REST API endpoints in this project.

## Guidelines

| Rule | When to Apply |
|------|---------------|
| Use kebab-case for endpoints | All new routes |
| Return 404 for missing resources | GET requests |
| Return 201 with Location header | POST creates |
| Use PATCH for partial updates | Update operations |

## Request/Response Format

All endpoints must:
1. Validate input with Pydantic models
2. Return consistent error format
3. Include request ID in response headers

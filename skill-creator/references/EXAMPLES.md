# Example Skills

> Complete, working examples of Agent Skills to learn from and adapt.

These examples demonstrate different skill patterns, from simple instruction-only skills to complex skills with scripts and resources.

---

## Example 1: Simple Instruction Skill

A minimal skill that provides expertise through instructions only.

### Structure
```
git-commit-helper/
└── SKILL.md
```

### SKILL.md
```yaml
---
name: git-commit-helper
description: Write clear, conventional git commit messages following best practices. Use when committing code, writing commit messages, or when the user mentions commits, git history, or changelog.
---

# Git Commit Helper

## When to use this skill

Activate when the user:
- Asks for help writing a commit message
- Wants to commit staged changes
- Mentions conventional commits or commit standards
- Asks about git history or changelogs

## Commit Message Format

\`\`\`
<type>(<scope>): <subject>

<body>

<footer>
\`\`\`

### Type (required)
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation only
- `style`: Formatting, missing semicolons, etc.
- `refactor`: Code change that neither fixes a bug nor adds a feature
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

### Scope (optional)
The component or area affected: `auth`, `api`, `ui`, `db`, etc.

### Subject (required)
- Max 50 characters
- Imperative mood ("add" not "added")
- No period at the end
- Lowercase first letter

### Body (optional)
- Wrap at 72 characters
- Explain "why" not "what"
- Separate from subject with blank line

### Footer (optional)
- Reference issues: `Fixes #123`
- Breaking changes: `BREAKING CHANGE: description`

## Workflow

1. Review staged changes: `git diff --cached`
2. Identify the type of change
3. Determine affected scope
4. Write concise subject line
5. Add body if the "why" isn't obvious
6. Include footer references if applicable

## Examples

### Simple feature
\`\`\`
feat(auth): add OAuth2 login support
\`\`\`

### Bug fix with context
\`\`\`
fix(api): handle null response from payment gateway

The payment gateway occasionally returns null instead of an error
object when the service is degraded. This caused unhandled exceptions
in the checkout flow.

Fixes #456
\`\`\`

### Documentation update
\`\`\`
docs: update README with Docker instructions
\`\`\`

### Breaking change
\`\`\`
feat(api)!: change authentication header format

BREAKING CHANGE: The Authorization header now requires "Bearer " prefix.
Update all API clients to include the prefix.
\`\`\`
```

---

## Example 2: Skill with Scripts

A skill that includes executable code for automation.

### Structure
```
api-tester/
├── SKILL.md
└── scripts/
    ├── test-endpoint.sh
    └── validate-response.py
```

### SKILL.md
```yaml
---
name: api-tester
description: Test REST API endpoints with automated request generation and response validation. Use when testing APIs, debugging endpoints, validating responses, or when the user mentions API testing, HTTP requests, or endpoint validation.
license: MIT
compatibility: Requires curl, jq, and python3
---

# API Tester

## When to use this skill

Activate when the user wants to:
- Test an API endpoint
- Debug API responses
- Validate request/response formats
- Check API availability or performance

## Quick Start

Test an endpoint:
\`\`\`bash
./scripts/test-endpoint.sh GET https://api.example.com/users
\`\`\`

Validate a response:
\`\`\`bash
echo '{"id": 1, "name": "Test"}' | python3 scripts/validate-response.py
\`\`\`

## Workflow

1. **Identify endpoint**: Get URL, method, headers, and body
2. **Run test script**: Use `scripts/test-endpoint.sh`
3. **Validate response**: Check status, headers, and body
4. **Report results**: Summarize findings

## Script: test-endpoint.sh

Usage:
\`\`\`bash
./scripts/test-endpoint.sh <METHOD> <URL> [BODY]

# Examples
./scripts/test-endpoint.sh GET https://api.example.com/users
./scripts/test-endpoint.sh POST https://api.example.com/users '{"name":"Test"}'
\`\`\`

## Script: validate-response.py

Validates JSON responses against common patterns:
\`\`\`bash
curl -s https://api.example.com/users/1 | python3 scripts/validate-response.py
\`\`\`

## Common Issues

### Connection refused
- Check if the server is running
- Verify the URL and port

### 401 Unauthorized
- Check authentication headers
- Verify API key or token

### 500 Internal Server Error
- Check request body format
- Review server logs if accessible
```

### scripts/test-endpoint.sh
```bash
#!/bin/bash
# Test an API endpoint and display formatted response

METHOD="${1:-GET}"
URL="${2}"
BODY="${3}"

if [ -z "$URL" ]; then
    echo "Usage: $0 <METHOD> <URL> [BODY]"
    exit 1
fi

echo "Testing: $METHOD $URL"
echo "---"

if [ -n "$BODY" ]; then
    curl -s -X "$METHOD" \
        -H "Content-Type: application/json" \
        -d "$BODY" \
        -w "\n\nStatus: %{http_code}\nTime: %{time_total}s\n" \
        "$URL" | jq . 2>/dev/null || cat
else
    curl -s -X "$METHOD" \
        -w "\n\nStatus: %{http_code}\nTime: %{time_total}s\n" \
        "$URL" | jq . 2>/dev/null || cat
fi
```

### scripts/validate-response.py
```python
#!/usr/bin/env python3
"""Validate JSON API responses."""

import json
import sys

def validate_response(data):
    """Validate common API response patterns."""
    issues = []
    
    if not isinstance(data, (dict, list)):
        issues.append("Response should be an object or array")
        return issues
    
    if isinstance(data, dict):
        # Check for error patterns
        if 'error' in data and 'message' not in data:
            issues.append("Error response should include 'message' field")
        
        # Check for pagination
        if 'items' in data and 'total' not in data:
            issues.append("Paginated response should include 'total' field")
    
    return issues

if __name__ == "__main__":
    try:
        data = json.load(sys.stdin)
        issues = validate_response(data)
        
        if issues:
            print("Validation issues found:")
            for issue in issues:
                print(f"  - {issue}")
            sys.exit(1)
        else:
            print("✓ Response validation passed")
            sys.exit(0)
    except json.JSONDecodeError as e:
        print(f"Invalid JSON: {e}")
        sys.exit(1)
```

---

## Example 3: Skill with References

A skill that uses progressive disclosure with reference files.

### Structure
```
docker-helper/
├── SKILL.md
└── references/
    ├── DOCKERFILE-PATTERNS.md
    ├── COMPOSE-REFERENCE.md
    └── TROUBLESHOOTING.md
```

### SKILL.md
```yaml
---
name: docker-helper
description: Create, optimize, and troubleshoot Docker containers and compose files. Use when working with Docker, containers, images, Dockerfiles, or docker-compose. Helps with building, running, and debugging containerized applications.
compatibility: Requires docker and docker-compose installed
metadata:
  author: devops-team
  version: "2.0"
---

# Docker Helper

## When to use this skill

Activate when the user wants to:
- Create or optimize a Dockerfile
- Set up docker-compose configuration
- Debug container issues
- Optimize image size or build time

## Quick Actions

### Create a Dockerfile

1. Identify the application type (Node.js, Python, Go, etc.)
2. Choose appropriate base image
3. Apply multi-stage build if beneficial
4. Follow security best practices

See [references/DOCKERFILE-PATTERNS.md](references/DOCKERFILE-PATTERNS.md) for language-specific patterns.

### Create docker-compose.yml

1. Define services needed
2. Configure networking
3. Set up volumes for persistence
4. Add health checks

See [references/COMPOSE-REFERENCE.md](references/COMPOSE-REFERENCE.md) for compose patterns.

### Debug Container Issues

1. Check container logs: `docker logs <container>`
2. Inspect container: `docker inspect <container>`
3. Execute shell: `docker exec -it <container> /bin/sh`

See [references/TROUBLESHOOTING.md](references/TROUBLESHOOTING.md) for common issues.

## Best Practices Summary

- Use specific image tags, not `latest`
- Order Dockerfile commands by change frequency
- Use `.dockerignore` to reduce context size
- Run as non-root user when possible
- Use multi-stage builds for smaller images
```

### references/DOCKERFILE-PATTERNS.md
```markdown
# Dockerfile Patterns

## Node.js Application

\`\`\`dockerfile
# Build stage
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

# Production stage
FROM node:20-alpine
WORKDIR /app
RUN addgroup -g 1001 -S nodejs && adduser -S nodejs -u 1001
COPY --from=builder /app/node_modules ./node_modules
COPY --chown=nodejs:nodejs . .
USER nodejs
EXPOSE 3000
CMD ["node", "server.js"]
\`\`\`

## Python Application

\`\`\`dockerfile
FROM python:3.11-slim
WORKDIR /app
RUN useradd -m -r appuser && chown appuser /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY --chown=appuser:appuser . .
USER appuser
EXPOSE 8000
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0"]
\`\`\`

## Go Application

\`\`\`dockerfile
# Build stage
FROM golang:1.21-alpine AS builder
WORKDIR /app
COPY go.* ./
RUN go mod download
COPY . .
RUN CGO_ENABLED=0 go build -o /app/server

# Production stage
FROM scratch
COPY --from=builder /app/server /server
EXPOSE 8080
ENTRYPOINT ["/server"]
\`\`\`
```

---

## Example 4: Complete Complex Skill

A comprehensive skill with scripts, references, and assets.

### Structure
```
pr-reviewer/
├── SKILL.md
├── scripts/
│   └── analyze-diff.py
├── references/
│   ├── REVIEW-CRITERIA.md
│   └── SECURITY-CHECKLIST.md
└── assets/
    └── review-template.md
```

### SKILL.md
```yaml
---
name: pr-reviewer
description: Perform comprehensive code reviews on pull requests, checking for code quality, security issues, and best practices. Use when reviewing PRs, checking code changes, or when the user asks for code review, feedback, or wants changes analyzed.
license: MIT
compatibility: Requires git. Optional python3 for advanced analysis.
metadata:
  author: engineering-team
  version: "1.5"
allowed-tools: Bash(git:*) Read Write
---

# PR Reviewer

## When to use this skill

Activate when the user wants to:
- Review a pull request
- Get feedback on code changes
- Check changes for security issues
- Analyze code quality

## Quick Start

For a standard review:
1. Fetch the changes: `git fetch origin pull/<PR_NUMBER>/head:pr-review`
2. Review the diff: `git diff main...pr-review`
3. Apply the review criteria from [references/REVIEW-CRITERIA.md](references/REVIEW-CRITERIA.md)

## Review Workflow

### 1. Understand the Context
- Read the PR description
- Understand the problem being solved
- Check linked issues

### 2. Analyze the Diff
Run the analysis script:
\`\`\`bash
python3 scripts/analyze-diff.py
\`\`\`

Or manually:
\`\`\`bash
git diff main...HEAD --stat
git diff main...HEAD
\`\`\`

### 3. Apply Review Criteria

Check each file against:
- [ ] Code correctness
- [ ] Test coverage
- [ ] Documentation
- [ ] Security (see [references/SECURITY-CHECKLIST.md](references/SECURITY-CHECKLIST.md))
- [ ] Performance

### 4. Provide Feedback

Use the template at [assets/review-template.md](assets/review-template.md) for consistent feedback format.

## Output Format

Structure feedback as:

\`\`\`markdown
## Review Summary

**Overall**: Approve / Request Changes / Comment

### Strengths
- ...

### Issues Found
- [Critical] ...
- [Suggestion] ...

### Questions
- ...
\`\`\`

## Reference Files

- [REVIEW-CRITERIA.md](references/REVIEW-CRITERIA.md): Detailed review standards
- [SECURITY-CHECKLIST.md](references/SECURITY-CHECKLIST.md): Security review checklist
- [review-template.md](assets/review-template.md): Feedback template
```

---

## Example 5: Minimal Valid Skill

The absolute minimum required for a valid skill.

### Structure
```
hello-world/
└── SKILL.md
```

### SKILL.md
```yaml
---
name: hello-world
description: A minimal example skill that greets users. Use when the user asks for a greeting or hello world example.
---

# Hello World

When activated, respond with a friendly greeting and explain that this is a minimal skill example.

Example: "Hello! This is the hello-world skill demonstrating the minimal Agent Skills format."
```

---

## Key Patterns

| Pattern | Use Case | Example |
|---------|----------|---------|
| Instruction-only | Simple expertise | git-commit-helper |
| With scripts | Automation needed | api-tester |
| With references | Complex documentation | docker-helper |
| Full structure | Enterprise workflows | pr-reviewer |
| Minimal | Getting started | hello-world |

---

*For more examples, see https://github.com/anthropics/skills*

# Example Skills

This document provides comprehensive examples of Agent Skills for various use cases.

## Simple Skills

### Minimal Skill

The simplest possible skill:

```
greeting/
└── SKILL.md
```

**SKILL.md:**
```markdown
---
name: greeting
description: Generate friendly greetings. Use when the user asks for a greeting, welcome message, or salutation.
---

# Greeting Generator

When asked to create a greeting:
1. Consider the context (formal, casual, festive)
2. Personalize if a name is provided
3. Keep it warm and appropriate

Examples:
- Formal: "Dear Mr. Smith, I hope this message finds you well."
- Casual: "Hey there! Great to hear from you!"
- Festive: "Season's greetings and best wishes for the new year!"
```

### Documentation Skill

Help write consistent documentation:

```markdown
---
name: doc-writer
description: Write clear technical documentation following best practices. Use when creating README files, API docs, guides, or any technical writing.
---

# Documentation Writer

## Principles
- Write for your audience (beginners vs. experts)
- Lead with the most important information
- Use concrete examples
- Keep sentences short and direct

## README Structure
1. **Title**: Clear, descriptive name
2. **Description**: One-paragraph summary
3. **Installation**: Step-by-step setup
4. **Usage**: Basic examples
5. **API Reference**: Detailed documentation
6. **Contributing**: How to help
7. **License**: Legal terms

## Style Guide
- Use active voice
- Avoid jargon unless necessary
- Include code examples
- Add screenshots for UI features
```

---

## Intermediate Skills

### Code Review Skill

```
code-review/
├── SKILL.md
└── references/
    └── CHECKLIST.md
```

**SKILL.md:**
```markdown
---
name: code-review
description: Perform thorough code reviews with consistent feedback. Use when asked to review code, check a PR, or provide feedback on changes.
metadata:
  author: dev-team
  version: "1.0"
---

# Code Review

## Quick Review Process

1. **Understand the Change**: Read the PR description or ask for context
2. **Review Structure**: Check file organization and naming
3. **Analyze Logic**: Verify correctness and efficiency
4. **Check Style**: Ensure consistency with project conventions
5. **Verify Tests**: Confirm adequate test coverage
6. **Security Scan**: Look for vulnerabilities

## Feedback Format

Structure your review as:

### Summary
One sentence describing the overall quality.

### Strengths
- What's done well (2-3 points)

### Suggestions
- Non-blocking improvements

### Required Changes
- Issues that must be fixed before merge

For detailed checklist, see [references/CHECKLIST.md](references/CHECKLIST.md).
```

**references/CHECKLIST.md:**
```markdown
# Code Review Checklist

## Logic & Correctness
- [ ] Code does what it's supposed to do
- [ ] Edge cases are handled
- [ ] Error handling is appropriate
- [ ] No obvious bugs

## Performance
- [ ] No unnecessary loops or iterations
- [ ] Efficient data structures used
- [ ] No N+1 queries (for database code)
- [ ] Appropriate caching if needed

## Security
- [ ] Input validation present
- [ ] No SQL injection vulnerabilities
- [ ] No XSS vulnerabilities
- [ ] Secrets not hardcoded
- [ ] Authentication/authorization correct

## Style & Maintainability
- [ ] Code is readable
- [ ] Names are descriptive
- [ ] Comments explain "why" not "what"
- [ ] No dead code
- [ ] DRY principles followed

## Testing
- [ ] Unit tests for new logic
- [ ] Edge cases tested
- [ ] Tests are readable
- [ ] No flaky tests

## Documentation
- [ ] Public APIs documented
- [ ] README updated if needed
- [ ] Breaking changes noted
```

---

### Git Workflow Skill

```
git-workflow/
├── SKILL.md
└── references/
    ├── BRANCHING.md
    └── COMMIT-MESSAGES.md
```

**SKILL.md:**
```markdown
---
name: git-workflow
description: Follow consistent Git workflows and best practices. Use when working with Git, creating branches, writing commits, or managing version control.
---

# Git Workflow

## Quick Reference

### Branch Naming
```
feature/description    # New features
bugfix/description     # Bug fixes
hotfix/description     # Urgent production fixes
docs/description       # Documentation
refactor/description   # Code refactoring
```

### Commit Message Format
```
type(scope): subject

body (optional)

footer (optional)
```

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

### Common Workflows

**Start a feature:**
\`\`\`bash
git checkout -b feature/my-feature
# make changes
git add .
git commit -m "feat: add my feature"
git push -u origin feature/my-feature
\`\`\`

**Sync with main:**
\`\`\`bash
git fetch origin
git rebase origin/main
\`\`\`

For detailed guidelines:
- [Branching Strategy](references/BRANCHING.md)
- [Commit Message Guide](references/COMMIT-MESSAGES.md)
```

---

## Advanced Skills

### API Integration Skill

```
api-integration/
├── SKILL.md
├── scripts/
│   ├── fetch.py
│   └── validate.py
├── references/
│   ├── AUTHENTICATION.md
│   └── ERROR-HANDLING.md
└── assets/
    └── schemas/
        └── response.json
```

**SKILL.md:**
```markdown
---
name: api-integration
description: Build robust API integrations with proper error handling, authentication, and validation. Use when working with REST APIs, webhooks, or external services.
metadata:
  author: platform-team
  version: "2.0"
compatibility: Requires Python 3.9+, requests library
---

# API Integration

## Quick Start

### Make an API Request
\`\`\`python
import requests

response = requests.get(
    "https://api.example.com/data",
    headers={"Authorization": f"Bearer {token}"}
)
response.raise_for_status()
data = response.json()
\`\`\`

### Validate Response
Use the validation script:
\`\`\`bash
python scripts/validate.py response.json
\`\`\`

## Best Practices

1. **Always use timeouts**
   \`\`\`python
   requests.get(url, timeout=30)
   \`\`\`

2. **Handle errors gracefully**
   See [references/ERROR-HANDLING.md](references/ERROR-HANDLING.md)

3. **Secure authentication**
   See [references/AUTHENTICATION.md](references/AUTHENTICATION.md)

4. **Validate schemas**
   Reference schema at `assets/schemas/response.json`

## Common Patterns

### Retry Logic
\`\`\`python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(stop=stop_after_attempt(3), wait=wait_exponential())
def fetch_with_retry(url):
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    return response.json()
\`\`\`

### Pagination
\`\`\`python
def fetch_all_pages(base_url):
    results = []
    url = base_url
    while url:
        response = requests.get(url).json()
        results.extend(response["data"])
        url = response.get("next")
    return results
\`\`\`
```

---

### Data Processing Skill

```
data-processor/
├── SKILL.md
├── scripts/
│   ├── transform.py
│   ├── validate.py
│   └── analyze.py
├── references/
│   ├── FORMATS.md
│   └── TRANSFORMATIONS.md
└── assets/
    ├── schemas/
    │   └── data-schema.json
    └── examples/
        ├── input.csv
        └── output.json
```

**SKILL.md:**
```markdown
---
name: data-processor
description: Process, transform, and analyze data files. Use when working with CSV, JSON, Excel, or data transformation tasks.
metadata:
  author: data-team
  version: "1.5"
compatibility: Requires Python 3.9+, pandas, openpyxl
---

# Data Processor

## Capabilities

- CSV, JSON, Excel file processing
- Data validation and cleaning
- Format conversion
- Statistical analysis

## Quick Start

### Validate Data
\`\`\`bash
python scripts/validate.py input.csv --schema assets/schemas/data-schema.json
\`\`\`

### Transform Data
\`\`\`bash
python scripts/transform.py input.csv --output output.json
\`\`\`

### Analyze Data
\`\`\`bash
python scripts/analyze.py data.csv --stats
\`\`\`

## Common Operations

### Read CSV
\`\`\`python
import pandas as pd
df = pd.read_csv("data.csv")
\`\`\`

### Convert Formats
\`\`\`python
# CSV to JSON
df.to_json("output.json", orient="records")

# CSV to Excel
df.to_excel("output.xlsx", index=False)
\`\`\`

### Data Cleaning
\`\`\`python
# Remove duplicates
df = df.drop_duplicates()

# Handle missing values
df = df.fillna(0)  # or df.dropna()

# Type conversion
df["date"] = pd.to_datetime(df["date"])
\`\`\`

See [references/FORMATS.md](references/FORMATS.md) for supported formats.
See [references/TRANSFORMATIONS.md](references/TRANSFORMATIONS.md) for advanced transformations.
```

---

## Workflow Skills

### PR Template Skill

```markdown
---
name: pr-template
description: Create well-structured pull request descriptions. Use when opening a PR, writing PR descriptions, or documenting code changes.
---

# Pull Request Template

## Standard PR Format

### Title
`type(scope): brief description`

Types: feat, fix, docs, refactor, test, chore

### Description Template

\`\`\`markdown
## Summary
Brief description of changes (1-2 sentences).

## Changes
- Change 1
- Change 2
- Change 3

## Testing
- [ ] Unit tests added/updated
- [ ] Manual testing completed
- [ ] Edge cases verified

## Screenshots
(If UI changes)

## Related Issues
Closes #123
\`\`\`

## Examples

### Feature PR
\`\`\`
feat(auth): add OAuth2 login support

## Summary
Adds Google and GitHub OAuth2 authentication options to the login page.

## Changes
- Add OAuth2 provider configuration
- Create login buttons for Google/GitHub
- Handle OAuth callback and token exchange
- Store OAuth tokens securely

## Testing
- [x] Unit tests for OAuth flow
- [x] Integration tests with mock providers
- [x] Manual testing with real OAuth apps
\`\`\`
```

---

### Testing Skill

```markdown
---
name: test-writer
description: Write comprehensive tests following best practices. Use when creating unit tests, integration tests, or test strategies.
---

# Test Writer

## Testing Principles

1. **Test behavior, not implementation**
2. **One assertion per test (when practical)**
3. **Use descriptive test names**
4. **Follow AAA pattern**: Arrange, Act, Assert

## Test Structure

\`\`\`python
def test_descriptive_name():
    # Arrange
    input_data = create_test_data()
    
    # Act
    result = function_under_test(input_data)
    
    # Assert
    assert result == expected_value
\`\`\`

## Naming Convention

`test_<function>_<scenario>_<expected_result>`

Examples:
- `test_add_positive_numbers_returns_sum`
- `test_login_invalid_password_raises_error`
- `test_process_empty_list_returns_empty`

## Test Categories

### Unit Tests
- Test single functions/methods
- Mock external dependencies
- Fast execution

### Integration Tests
- Test component interactions
- Use real dependencies when practical
- May be slower

### Edge Cases to Cover
- Empty inputs
- Null/None values
- Boundary conditions
- Error conditions
- Concurrent access (if applicable)
```

---

## Domain-Specific Skills

### Security Audit Skill

```markdown
---
name: security-audit
description: Perform security audits and identify vulnerabilities. Use when reviewing code for security issues, checking for vulnerabilities, or hardening applications.
---

# Security Audit

## Quick Scan Checklist

### Authentication
- [ ] Passwords hashed with bcrypt/argon2
- [ ] Session tokens are secure random
- [ ] MFA available for sensitive operations
- [ ] Password policies enforced

### Authorization
- [ ] Principle of least privilege
- [ ] Role-based access control
- [ ] Authorization checked on every request

### Input Validation
- [ ] All user input validated
- [ ] Parameterized queries used
- [ ] File uploads validated and sanitized

### Data Protection
- [ ] Sensitive data encrypted at rest
- [ ] TLS for data in transit
- [ ] No secrets in code or logs
- [ ] PII handling compliant

### Common Vulnerabilities

| Vulnerability | Check For |
|--------------|-----------|
| SQL Injection | String concatenation in queries |
| XSS | Unescaped user content in HTML |
| CSRF | Missing tokens on forms |
| IDOR | Direct object references without auth check |

## Reporting Format

\`\`\`markdown
## Finding: [Title]
**Severity**: Critical/High/Medium/Low
**Location**: [file:line]

### Description
[What the issue is]

### Impact
[What could happen if exploited]

### Recommendation
[How to fix it]
\`\`\`
```

---

## Creating Your Own

Use these examples as templates. Key principles:

1. **Start simple** - Add complexity only as needed
2. **Clear triggers** - Description should make activation obvious
3. **Actionable instructions** - Tell the agent exactly what to do
4. **Progressive disclosure** - Keep SKILL.md focused, details in references
5. **Concrete examples** - Show, don't just tell

# Code Review Task

You are a code reviewer examining changes made by an autonomous development agent.
Your goal is to ensure the implementation meets quality standards and follows project guidelines.

## Story Context

**ID**: {{STORY_ID}}
**Title**: {{STORY_TITLE}}
**Description**: {{STORY_DESCRIPTION}}

### Acceptance Criteria
{{ACCEPTANCE_CRITERIA}}

---

## Project Guidelines (AGENTS.md)

{{AGENTS_MD}}

---

## Changes to Review

### Diff Statistics
{{DIFF_STATS}}

### Full Diff
```diff
{{DIFF}}
```

---

## Review Instructions

Please review the changes above and evaluate them against:

1. **Acceptance Criteria**: Do the changes satisfy all acceptance criteria for the story?
2. **Code Quality**: Is the code clean, readable, and well-structured?
3. **Project Guidelines**: Does the code follow the guidelines in AGENTS.md?
4. **Best Practices**: Are there any obvious issues, bugs, or improvements needed?

### Your Response

Provide a brief review (2-5 paragraphs) covering:
- What was done well
- Any issues or concerns
- Specific suggestions for improvement (if any)

### Final Verdict

End your review with exactly ONE of these markers:

- `<verdict>APPROVE</verdict>` - Changes are acceptable and ready to merge
- `<verdict>REJECT</verdict>` - Changes need revision before merging

If you REJECT, clearly explain what needs to be fixed.

---

## Begin Review

Review the changes now and provide your assessment.

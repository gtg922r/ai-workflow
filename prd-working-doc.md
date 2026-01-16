- get rid of the heavy-weight TUI. just have the pretty console/CLI interface
- convert prd to a different form. maybe toml or markdown
- add support for gemini-cli agent (https://geminicli.com/docs/cli/headless/)
- fix the current console display. every single line has time stamp which means box shapes doesn't work 
- add custom command for working with a prd doc. process the doc and add to prd.json, ask questions as you go.
- add a skill for runner ralph (how it works, the architecture, infra, etc)
- Add support for streaming from model
  - https://code.claude.com/docs/en/headless
  - https://cursor.com/docs/cli/headless
  - Should show the last 3-4 lines in a scrolling window (don't fill up the window)
- use more conductor like tracks with phases, have a planner run first, have it report out along each of the phases. 
- got a error without much input. see if can get better support:
```
[10:05:40] ✗ Failure: unknown error
[10:05:40] ┌── 🤖 Agent Output ─────────────────────────────────────────────────┐
[10:05:40] │ ConnectError:  Error
```

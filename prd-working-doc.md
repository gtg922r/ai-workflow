- get rid of the heavy-weight TUI. just have the pretty console/CLI interface
- in the workflow doctor not having api keys set should not be a critical issue. each of the agents offers their auth flow. just amke it informational
- convert prd to a different form. maybe toml or markdown
- add a command option to runner-ralph for the user to specify the location of the prd file.
- add support for gemini-cli agent (https://geminicli.com/docs/cli/headless/)
- fix the current console display. every single line has time stamp which means box shapes doesn't work 
- add an option to runner-ralph which triggers a selection screen where the user can select which stories from the prd they want to run and in what order (rater than the default behavior of processing the prd in order). 
- when installing via the install script, get this warning `npm warn gitignore-fallback No .npmignore file found, using .gitignore for file exclusion. Consider creating a .npmignore file to explicitly control published files.`. Fix it so there is no warning using the most reasonable approach.
- add custom command for working with a prd doc. process the doc and add to prd.json, ask questions as you go.
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

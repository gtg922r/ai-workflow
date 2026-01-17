- get rid of the heavy-weight TUI in runner-ralph entirely - get rid of the --tui option and its associated code
- Add support for streaming from agent utilizing streaming-json options
  - https://code.claude.com/docs/en/headless
  - https://cursor.com/docs/cli/headless
  - Should show the last 3-4 lines in a scrolling section - basically as a status indicator that the agent is working. don't fill up the whole console - only show the last few lines. 
- add support for gemini-cli agent in runner-ralph (https://geminicli.com/docs/cli/headless/)
- use more conductor like tracks with phases, have a planner run first, have it report out along each of the phases. 
- got a error without much input. see if can get better support:
```
[10:05:40] ✗ Failure: unknown error
[10:05:40] ┌── 🤖 Agent Output ─────────────────────────────────────────────────┐
[10:05:40] │ ConnectError:  Error
```
## Archive
- get rid of the heavy-weight TUI in runner-ralph. just have the pretty console/CLI interface you get with --no-tui. make that the default
- in the workflow doctor not having api keys set should not be a critical issue. each of the agents offers their auth flow. just amke it informational
- add custom command for working with a prd doc. process the doc and add to prd.json, ask questions as you go.
- improve the current console display in runner-ralph. every single line has time stamp which means box shapes doesn't work 
- add a command option to runner-ralph for the user to specify the location of the prd file.
- when installing via the install script, get this warning `npm warn gitignore-fallback No .npmignore file found, using .gitignore for file exclusion. Consider creating a .npmignore file to explicitly control published files.`. Fix it so there is no warning using the most reasonable approach.
- add an option to runner-ralph which triggers a selection screen where the user can select which stories from the prd they want to run and in what order (rater than the default behavior of processing the prd in order). 
s
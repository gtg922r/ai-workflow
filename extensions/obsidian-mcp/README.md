# Obsidian MCP Extension for Gemini CLI

A Gemini CLI extension that connects your AI assistant to your Obsidian vault using the Model Context Protocol (MCP). Provides safe read/write access to notes while protecting YAML frontmatter from corruption.

## Features

- **Full Vault Access**: Read, write, search, and organize notes
- **Safe Operations**: YAML frontmatter protection prevents metadata corruption
- **11 MCP Tools**: Complete toolkit for all vault operations
- **Custom Commands**: Pre-built shortcuts for common workflows
- **Local & Private**: Your vault data stays on your machine

## Prerequisites

- [Gemini CLI](https://github.com/google-gemini/gemini-cli) installed
- Node.js v18.0.0+
- An Obsidian vault (local directory)

## Installation

### 1. Link the Extension

From this extension directory:

```bash
cd extensions/obsidian-mcp
gemini extensions link .
```

Or link from the repository root:

```bash
gemini extensions link ./extensions/obsidian-mcp
```

### 2. Configure Your Vault Path

Add your vault path to Gemini CLI settings. Create or edit `~/.gemini/settings.json`:

```json
{
  "config": {
    "obsidian": {
      "vaultPath": "/path/to/your/obsidian/vault"
    }
  }
}
```

Replace `/path/to/your/obsidian/vault` with the actual path to your Obsidian vault directory.

### 3. Verify Installation

```bash
gemini extensions list
```

You should see `obsidian-mcp` in the list. Start Gemini CLI and the `obsidian` MCP server will be available.

## Available Commands

After installation, these commands are available in Gemini CLI:

| Command | Description |
|---------|-------------|
| `/obsidian:search <query>` | Search notes by content or tags |
| `/obsidian:daily [content]` | Create or open today's daily note |
| `/obsidian:summary [filter]` | Summarize recent vault activity |
| `/obsidian:new <description>` | Create a new note with smart defaults |
| `/obsidian:tag <action>` | Manage tags - add, remove, or list |
| `/obsidian:link [note]` | Find and suggest note connections |

### Example Usage

```
> /obsidian:search machine learning
> /obsidian:daily Had a productive meeting about the Q1 roadmap
> /obsidian:new project note for website redesign
> /obsidian:tag add #reviewed to all notes in projects/
> /obsidian:link my-idea.md
```

## MCP Tools Reference

The extension provides these MCP tools for direct use:

### File Operations
- `read_note` - Read content of a specific note
- `write_note` - Create or modify notes (overwrite/append/prepend)
- `delete_note` - Remove a note (requires confirmation)
- `move_note` - Relocate a note to a different path

### Discovery & Search
- `list_directory` - Browse vault folder structure
- `search_notes` - Find notes by content or metadata
- `read_multiple_notes` - Batch read multiple notes

### Metadata Management
- `get_frontmatter` - Extract YAML frontmatter from a note
- `update_frontmatter` - Modify note metadata
- `get_notes_info` - Get file statistics and dates
- `manage_tags` - Add, remove, or list tags

## Tips & Best Practices

### Organizing Notes
- Use consistent folder structures (`projects/`, `references/`, `daily/`)
- Include meaningful frontmatter (tags, status, dates)
- Create `[[wiki-links]]` to build your knowledge graph

### Effective Searching
- Search by content: "notes about Python"
- Search by tags: "notes tagged #project"
- Combine with date filters: "notes modified this week"

### Batch Operations
1. Search to find target notes
2. Review with batch read
3. Apply changes with update tools

## Troubleshooting

### MCP Server Not Starting
- Verify Node.js v18+ is installed: `node --version`
- Check vault path is correct in settings
- Try running manually: `npx @mauricio.wolff/mcp-obsidian@latest /path/to/vault`

### Permission Issues
- Ensure the vault directory is readable/writable
- Check that `.obsidian` folder permissions aren't blocking access

### Commands Not Found
- Verify extension is linked: `gemini extensions list`
- Reload Gemini CLI after linking

## Security

- **Local Only**: All operations happen on your machine
- **No Cloud Sync**: Your data is never transmitted externally
- **Safe Frontmatter**: YAML metadata is protected from corruption
- **Confirmation Required**: Destructive operations need explicit approval

## Resources

- [mcp-obsidian on npm](https://www.npmjs.com/package/@mauricio.wolff/mcp-obsidian)
- [mcp-obsidian on GitHub](https://github.com/bitbonsai/mcp-obsidian)
- [Gemini CLI Extensions Documentation](https://geminicli.com/docs/extensions/)
- [Model Context Protocol](https://modelcontextprotocol.io/)

## License

This extension wrapper is provided as part of the ai-workflow repository. The underlying `@mauricio.wolff/mcp-obsidian` package has its own license terms.

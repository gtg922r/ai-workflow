# Obsidian Vault Integration

You have access to the user's Obsidian vault through MCP tools. Use these tools to help manage notes, search content, and organize knowledge.

## Quick Reference

**Essential Commands:**
- `/obsidian:search <query>` - Search notes by content or tags
- `/obsidian:daily` - Create or open today's daily note
- `/obsidian:summary` - Summarize recent vault activity

## Available Tools

### File Operations
| Tool | Purpose | Example |
|------|---------|---------|
| `read_note` | Read note content | Read "projects/my-idea.md" |
| `write_note` | Create/update notes | Create a new meeting note |
| `delete_note` | Remove a note | Delete outdated draft |
| `move_note` | Relocate a note | Move to archive folder |

### Discovery & Search
| Tool | Purpose | Example |
|------|---------|---------|
| `list_directory` | Browse vault structure | List all folders in vault |
| `search_notes` | Find notes by content/metadata | Search for "machine learning" |
| `read_multiple_notes` | Batch read notes | Read all notes in a folder |

### Metadata Management
| Tool | Purpose | Example |
|------|---------|---------|
| `get_frontmatter` | Extract YAML metadata | Get tags from a note |
| `update_frontmatter` | Modify note metadata | Add status field |
| `get_notes_info` | Get file statistics | Check modification dates |
| `manage_tags` | Add/remove/list tags | Tag notes with "reviewed" |

## Usage Patterns

### Creating Notes
When creating notes, consider:
- Use appropriate folder structure (e.g., `projects/`, `daily/`, `references/`)
- Include relevant YAML frontmatter (tags, status, date)
- Link to related notes using `[[wiki-links]]`

### Searching Notes
The `search_notes` tool searches both content and frontmatter. Use it to:
- Find notes by topic: "search for notes about Python"
- Filter by tags: "find all notes tagged #project"
- Locate by date: "notes modified this week"

### Batch Operations
For bulk updates, combine tools:
1. Use `search_notes` to find target notes
2. Use `read_multiple_notes` to review content
3. Use `update_frontmatter` or `write_note` to apply changes

## Write Modes

When using `write_note`, specify the mode:
- **overwrite**: Replace entire note content (default)
- **append**: Add content to the end
- **prepend**: Add content to the beginning

## Best Practices

1. **Preserve frontmatter**: The MCP server protects YAML frontmatter from corruption
2. **Use meaningful paths**: Organize notes in logical folder structures
3. **Link generously**: Create `[[wiki-links]]` to build your knowledge graph
4. **Tag consistently**: Use tags for cross-cutting concerns (status, project, topic)

## Safety Notes

- The `.obsidian` directory and system files are automatically excluded
- Delete operations require explicit confirmation
- Your vault data stays local - never transmitted to external servers

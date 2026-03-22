# Gemini CLI Tool Mapping

## Installation

Install the extension directly from GitHub:

```bash
gemini extensions install https://github.com/mikeparcewski/wicked-prezzie
```

Verify it's loaded:

```bash
gemini extensions list
```

Gemini CLI discovers the extension via `gemini-extension.json` and loads this file (`GEMINI.md`) as context automatically.

### Prerequisites

```bash
pip install python-pptx beautifulsoup4 lxml Pillow
```

- **Google Chrome** — headless layout extraction
- **LibreOffice** — PPTX rendering (`brew install --cask libreoffice` / `apt install libreoffice`)
- **poppler** — PDF to PNG (`brew install poppler` / `apt install poppler-utils`)

## Tool Mapping

Skills use Claude Code tool names. When you encounter these in a skill, use your platform equivalent:

| Skill references | Gemini CLI equivalent |
|-----------------|----------------------|
| `Read` (file reading) | `read_file` |
| `Write` (file creation) | `write_file` |
| `Edit` (file editing) | `replace` |
| `Bash` (run commands) | `run_shell_command` |
| `Grep` (search file content) | `grep_search` |
| `Glob` (search files by name) | `glob` |
| `TodoWrite` (task tracking) | `write_todos` |
| `Skill` tool (invoke a skill) | `activate_skill` |
| `WebSearch` | `google_web_search` |
| `WebFetch` | `web_fetch` |
| `Task` tool (dispatch subagent) | Experimental — Gemini CLI has [subagent support](https://geminicli.com/docs/core/subagents/) but it is experimental. May need to be enabled in settings. Falls back to sequential execution if unavailable. |

## Usage

The same natural-language prompts work in both Claude and Gemini:

```
"Make me a presentation about our Q1 results"
"Convert the HTML slides in my-deck/ to PowerPoint"
"Index the source documents in ./rfp-materials/"
"Run a brainstorm for the client deck"
"Audit my deck"
"Analyze the team's feedback comments from the Word doc"
```

Gemini reads the same SKILL.md files and follows the same workflows. The only difference is tool names (see mapping above).

## Limitations

- **Subagent support is experimental** — Gemini CLI has [subagent support](https://geminicli.com/docs/core/subagents/) but it is experimental and may need to be enabled in settings. Multi-agent workflows (parallel brainstorm teams, parallel extraction) will fall back to sequential execution if subagents are unavailable.
- **No vision in CLI** — Gemini CLI may not support reading binary files (PDF, PPTX, images) with vision. For slide-learn indexing, text-based extraction works; vision descriptions of charts/diagrams may need manual input.
- **Skill triggering** — Gemini uses `activate_skill` instead of `Skill`. Triggering accuracy depends on Gemini's skill matching implementation.

## Subagent support (experimental)

Gemini CLI has [experimental subagent support](https://geminicli.com/docs/core/subagents/). When enabled, skills that dispatch parallel agents (brainstorm teams, validation lenses, parallel extraction) will work as designed. When unavailable, these workflows fall back to sequential execution — same results, just slower.

## Additional Gemini CLI tools

These tools are available in Gemini CLI but have no Claude Code equivalent:

| Tool | Purpose |
|------|---------|
| `list_directory` | List files and subdirectories |
| `ask_user` | Request structured input from the user |
| `tracker_create_task` | Rich task management (create, update, list, visualize) |
| `enter_plan_mode` / `exit_plan_mode` | Switch to read-only research mode before making changes |

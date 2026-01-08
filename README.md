# prompt-forge

A minimal CLI tool for crafting and testing AI prompts locally without API costs.

## Features

- **Simple template syntax**: `{{variable}}` placeholders with optional defaults
- **Flexible variable input**: CLI flags, JSON files, or interactive prompts
- **Smart priority**: CLI > JSON > defaults > interactive
- **Simulation mode**: Test prompts with built-in or custom regex-based responses
- **Multiple output formats**: Text, Markdown, JSON
- **Token estimation**: Built-in `--show-tokens` for prompt optimization
- **Validation tools**: `--check` lists variables, `--dry-run` previews output
- **History tracking**: `--save` logs prompts and responses
- **Multiple input sources**: Files, stdin, or inline templates
- **Response templating**: Simulated responses can use prompt variables

## Installation

### Quick Start
```bash
python3 prompt_forge.py template.txt --var role=assistant
```

### Make Executable
```bash
chmod +x prompt_forge.py
./prompt_forge.py template.txt --var role=assistant
```

## Usage

### Basic Commands

```bash
# Render template with variables
prompt_forge.py template.txt --var role=expert --var task="code review"

# Use JSON variables file
prompt_forge.py template.txt --vars vars.json

# Simulate AI response
prompt_forge.py template.txt --vars vars.json --simulate

# Custom simulation rules
prompt_forge.py template.txt --vars vars.json --simulate --rules custom.json

# Interactive mode (prompts for missing variables)
prompt_forge.py template.txt --interactive

# Inline template
prompt_forge.py --template "You are a {{role}}" --var role=assistant

# From stdin
echo "Role: {{role}}, Task: {{task}}" | prompt_forge.py --var role=tester --var task=debug

# Check template variables
prompt_forge.py template.txt --check

# JSON output with token count
prompt_forge.py template.txt --vars vars.json --format json --show-tokens

# Markdown format with simulation
prompt_forge.py template.txt --vars vars.json --simulate --format markdown

# Save to history
prompt_forge.py template.txt --vars vars.json --simulate --save
```

### Options

**Variables:**
- `--var KEY=VALUE` - Set variable (repeatable, highest priority)
- `--vars FILE` - Load variables from JSON file
- `--interactive` - Prompt for missing variables interactively

**Template Input:**
- `template` (positional) - Template file path
- `--template TEXT` - Inline template text
- stdin - Read template from pipe

**Simulation:**
- `--simulate` - Generate simulated AI response
- `--rules FILE` - Custom simulation rules (JSON)

**Output:**
- `--format FORMAT` - Output format: `text` (default), `markdown`, `json`
- `--show-tokens` - Display estimated token count
- `--save [FILE]` - Append to history log (default: `~/.prompt-forge.log`)

**Validation:**
- `--check` - List all template variables and exit
- `--dry-run` - Preview rendered output without saving

**Info:**
- `--version` - Show version information

## Template Format

### Basic Placeholder
```
You are a {{role}}.

Your task is to help with: {{task}}
```

### With Default Values
```
You are a {{role|default="assistant"}}.

Context: {{context|default="General assistance"}}

Guidelines: {{guidelines|default="Be clear and concise"}}
```

**Variable Extraction:**
- Variables use `{{name}}` syntax
- Defaults use `{{name|default="fallback value"}}`
- Only alphanumeric variable names supported

## Variable Priority

Variables are resolved in this order (highest to lowest):

1. **CLI flags** (`--var key=value`) - Always wins
2. **JSON file** (`--vars file.json`) - Overrides defaults
3. **Template defaults** (`{{var|default="value"}}`) - Fallback if not provided
4. **Interactive prompts** (`--interactive`) - Last resort
5. **Error** - If still missing after all sources

### Example:
```bash
# Template: "Role: {{role}}"
# vars.json: {"role": "assistant"}
# Command:
prompt_forge.py template.txt --vars vars.json --var role=expert

# Result: role = "expert" (CLI flag overrides JSON)
```

## Examples

### Example 1: Basic Rendering
```bash
$ cat template.txt
You are a {{role}}.
Help me with: {{task}}

$ prompt_forge.py template.txt --var role="coding expert" --var task="Python optimization"
You are a coding expert.
Help me with: Python optimization
```

### Example 2: Using Defaults
```bash
$ cat template.txt
Role: {{role|default="assistant"}}
Task: {{task}}

$ prompt_forge.py template.txt --var task="debug code"
Role: assistant
Task: debug code
```

### Example 3: Check Variables
```bash
$ prompt_forge.py template.txt --check
Template variables:
  - role (default: "assistant")
  - task (required)
  - context (default: "General assistance")
```

### Example 4: Simulate Response
```bash
$ prompt_forge.py template.txt --var role=coder --var task="write Python function" --simulate
You are a coder.
Help me with: write Python function

---
Here's a code implementation:

```
# Implementation
```

This demonstrates the functionality.
```

### Example 5: JSON Output
```bash
$ prompt_forge.py template.txt --vars vars.json --simulate --format json --show-tokens
{
  "prompt": "You are a coding assistant.\nHelp me with: write Python functions",
  "timestamp": "2024-01-08T12:00:00",
  "tokens": 15,
  "response": "Here's a code implementation:\n\n```\n# Implementation\n```"
}
```

### Example 6: Markdown Format
```bash
$ prompt_forge.py template.txt --vars vars.json --simulate --format markdown --show-tokens
# Prompt

You are a coding assistant.
Help me with: write Python functions

## Metadata
- Tokens: 15
- Timestamp: 2024-01-08 12:00:00

# Simulated Response

Here's a code implementation:

```
# Implementation
```
```

### Example 7: Variable Priority Test
```bash
# vars.json has: {"role": "assistant", "task": "help users"}
$ prompt_forge.py template.txt --vars vars.json --var role=override --var task="specific task"
You are a override.
Help me with: specific task
```

### Example 8: Save to History
```bash
$ prompt_forge.py template.txt --vars vars.json --simulate --save
You are a coding assistant.
Help me with: write Python functions

---
Here's a code implementation...

Saved to /Users/username/.prompt-forge.log

$ cat ~/.prompt-forge.log
=== 2024-01-08 12:00:00 ===
Prompt:
You are a coding assistant.
Help me with: write Python functions

Response:
Here's a code implementation...

---
```

## File Formats

### Variables File (`vars.json`)
```json
{
  "role": "coding assistant",
  "task": "write Python functions",
  "context": "Building a web scraper",
  "guidelines": "Use requests library, handle errors"
}
```

### Rules File (`rules.json`)
```json
{
  "rules": [
    {
      "regex": "code|programming|function|implement",
      "response": "Here's a code implementation:\n\n```python\n# Code here\n```"
    },
    {
      "regex": "explain|what is|describe",
      "response": "Explanation:\n\nKey points:\n1. First\n2. Second"
    },
    {
      "regex": ".*",
      "response": "I understand. Here's my response about {{task}}."
    }
  ]
}
```

**Rules format:**
- `regex`: Pattern to match in the prompt (case-insensitive)
- `response`: Template for the response (can use `{{variables}}`)

## Built-in Simulation Rules

The tool includes 6 default simulation patterns:

1. **Code/Programming** - Matches: `code|programming|python|javascript|function|class|implement`
2. **Explanations** - Matches: `explain|what is|describe|definition`
3. **Lists/Steps** - Matches: `list|enumerate|steps|how to`
4. **Debugging** - Matches: `debug|error|fix|problem`
5. **Reviews** - Matches: `review|analyze|evaluate`
6. **Catch-all** - Matches: `.*` (everything else)

Each rule returns a formatted response appropriate to the request type.

## Token Estimation

The `--show-tokens` flag provides a simple estimation:

**Formula:** `word_count × 1.3`

This is a conservative estimate for English text. Actual token counts may vary by:
- Language model (GPT-3.5, GPT-4, Claude, etc.)
- Language (English, code, other languages)
- Special characters and formatting

**Example:**
```bash
$ prompt_forge.py template.txt --vars vars.json --show-tokens
You are a coding assistant.
Help me with: write Python functions

[Tokens: 15]
```

## Use Cases

### 1. Prompt Engineering
Iterate on prompt designs without API costs:
```bash
# Test variations
prompt_forge.py prompt-v1.txt --vars test-vars.json --simulate
prompt_forge.py prompt-v2.txt --vars test-vars.json --simulate
prompt_forge.py prompt-v3.txt --vars test-vars.json --simulate
```

### 2. AI Agent Development
Develop system prompts with reusable templates:
```bash
# System prompt template
cat > agent-system.txt << EOF
You are a {{agent_type}} specialized in {{domain}}.
Your capabilities: {{capabilities}}
Your constraints: {{constraints}}
EOF

# Test with different configurations
prompt_forge.py agent-system.txt --vars config-dev.json
prompt_forge.py agent-system.txt --vars config-prod.json
```

### 3. Documentation Generation
Create consistent prompts for documentation:
```bash
prompt_forge.py doc-generator.txt --var component=API --var detail=high
```

### 4. Local Testing
Simulate AI responses before committing to API:
```bash
# Test locally first
prompt_forge.py query.txt --vars params.json --simulate --save

# When satisfied, pipe to actual API
prompt_forge.py query.txt --vars params.json --format json | curl ...
```

### 5. Batch Processing
Generate multiple prompts from different variable sets:
```bash
for config in configs/*.json; do
    prompt_forge.py template.txt --vars "$config" --format json >> prompts.jsonl
done
```

## History Log Format

When using `--save`, prompts are appended to a log file:

```
=== 2024-01-08 12:00:00 ===
Prompt:
You are a coding assistant.
Help me with: write Python functions

Response:
Here's a code implementation:
```
# Implementation
```

---

=== 2024-01-08 12:05:00 ===
Prompt:
...
```

**Default location:** `~/.prompt-forge.log`  
**Custom location:** `--save /path/to/custom.log`

## Requirements

- **Python:** 3.6+
- **Dependencies:** None (stdlib only)
- **Modules used:**
  - `argparse` - CLI argument parsing
  - `re` - Template variable extraction and pattern matching
  - `json` - JSON file handling
  - `datetime` - Timestamps
  - `pathlib` - File path handling

## Implementation Details

- **141 lines** of clean, readable Python
- **Stdlib only** - no external dependencies
- **Regex-based** - efficient template parsing
- **Streaming** - handles large templates efficiently
- **Safe** - validates inputs before processing

## Limitations

- **No conditionals** - No `{if}` or `{for}` logic in templates (v1.0)
- **Single-turn** - One prompt/response at a time (no conversations)
- **Simple tokens** - Estimation only (not actual tokenizer)
- **No multi-line entries** - Stack traces not supported in simulation
- **Alphanumeric vars** - Variable names: `[a-zA-Z0-9_]` only

## Future Enhancements (v1.1+)

- Conditional template logic (`{{if condition}}...{{endif}}`)
- Loop constructs (`{{for item in list}}...{{endfor}}`)
- Template includes (`{{include other.txt}}`)
- Multi-turn conversation support
- More accurate tokenization (model-specific)
- Template validation with syntax highlighting
- Interactive template editor mode

## Workflow

**Typical prompt development workflow:**

1. **Create template** with variables
2. **Check variables** with `--check`
3. **Test locally** with `--simulate`
4. **Iterate** on template based on simulated results
5. **Validate** with `--dry-run`
6. **Save** successful prompts with `--save`
7. **Use** final prompt with actual AI API

## Tips

### Organizing Templates
```bash
prompts/
├── system/
│   ├── coder.txt
│   ├── analyst.txt
│   └── reviewer.txt
├── tasks/
│   ├── debug.txt
│   ├── explain.txt
│   └── refactor.txt
└── vars/
    ├── defaults.json
    ├── dev.json
    └── prod.json
```

### Testing Variations
```bash
# Test different roles with same task
for role in coder analyst reviewer; do
    prompt_forge.py system/$role.txt --vars task.json --simulate
done
```

### Piping to Real APIs
```bash
# Generate prompt, pipe to OpenAI
prompt_forge.py template.txt --vars vars.json --format json | \
    jq -r '.prompt' | \
    curl https://api.openai.com/v1/completions -d @-
```

## Troubleshooting

### Missing Variable Error
```
Error: Missing required variables: task
```
**Solution:** Provide via `--var task=value` or `--vars file.json`

### Invalid Var Format
```
Error: Invalid --var format: roleassistant (use KEY=VALUE)
```
**Solution:** Use `--var role=assistant` (with `=`)

### Template Not Found
```
Error: No template provided (use file, --template, or stdin)
```
**Solution:** Provide template via file, `--template`, or stdin

### Unused Variables Warning
```
Warning: Unused variables: extra_var
```
**Note:** Variable was provided but not found in template (not an error)

## License

MIT

## Repository

https://github.com/novyxlabs/prompt-forge

---

Built with the **AI-agent-first workflow** - craft prompts locally, test without API costs, iterate rapidly.


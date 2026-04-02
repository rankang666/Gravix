# Creating Skills for Gravix

遵循Claude官方最佳实践的技能创建指南。

## 📁 Directory Structure

Gravix skills follow Claude's official best practices with a **document-driven architecture**:

```
skills/
├── README.md                    # This file
├── echoing-messages/            # Echo skill
│   ├── SKILL.md                # Main documentation (YAML + Markdown)
│   └── scripts/
│       └── echo.py             # Implementation code
├── evaluating-expressions/      # Calculator skill
│   ├── SKILL.md
│   └── scripts/
│       └── calculate.py
├── monitoring-system-resources/ # System info skill
│   ├── SKILL.md
│   └── scripts/
│       └── system_info.py
├── submitting-funboost-tasks/   # Funboost task skill
│   ├── SKILL.md
│   └── scripts/
│       └── funboost_task.py
└── creating-custom-skills/      # Custom skill template
    ├── SKILL.md
    └── scripts/
        └── custom_example.py
```

## 🎯 SKILL.md Format Requirements

### Required YAML Frontmatter

Every SKILL.md must begin with YAML frontmatter:

```yaml
---
name: processing-files
description: Process and analyze data files. Use when working with CSV, JSON, or text data files.
---
```

### Naming Rules

The `name` field must follow these rules:

- **Max 64 characters**
- **Lowercase letters, numbers, and hyphens only**
- **No XML tags**
- **No reserved words**: "anthropic", "claude"
- **Use gerund form** (verb + -ing): `processing-pdfs`, `analyzing-data`, `executing-tasks`

✅ **Good examples:**
- `processing-pdfs`
- `analyzing-spreadsheets`
- `monitoring-system-resources`
- `submitting-funboost-tasks`

❌ **Avoid:**
- `PDF-Processor` (uppercase, not gerund)
- `helper` (too vague)
- `claude-tools` (reserved word)
- `process_pdf` (underscore, not hyphen)

### Description Rules

The `description` field must:

- **Be non-empty, max 1024 characters**
- **No XML tags**
- **Describe both: what it does AND when to use it**
- **Write in third person** (not "I can help" or "you can use")
- **Include specific trigger/context information**

✅ **Good examples:**
```yaml
description: Extract text and tables from PDF files, fill forms, merge documents. Use when processing PDF files or when PDFs, forms, or document extraction are mentioned.

description: Evaluate mathematical expressions safely with basic arithmetic operations. Use when performing calculations or testing mathematical logic.

description: Retrieve CPU, memory, and disk usage information for system monitoring and health checks. Use when checking server resources or diagnosing performance issues.
```

❌ **Avoid:**
```yaml
description: I can help you process PDF files
description: Use this skill to calculate things
description: A helpful tool for data processing
```

### Complete Example

```markdown
---
name: processing-pdfs
description: Extract text and tables from PDF files, fill forms, merge documents. Use when processing PDF files or when PDFs, forms, or document extraction are mentioned.
---

# Processing PDFs

Extract text, tables, and form data from PDF documents.

## Quick Start

```python
result = await executor.execute('pdf_process', {'file': 'document.pdf'})
```

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| file | string | ✅ | Path to PDF file |
| extract_tables | boolean | ❌ | Extract tables (default: false) |

## Returns

Extracted content in structured JSON format.

## Advanced Features

**Form filling**: See [FORMS.md](FORMS.md) for complete guide
**API reference**: See [REFERENCE.md](REFERENCE.md) for all methods
**Examples**: See [EXAMPLES.md](EXAMPLES.md) for common patterns
```

## 🚀 Creating a New Skill

### Quick Method: Copy Template

```bash
# 1. Copy template
cp -r skills/creating-custom-skills skills/my-new-skill

# 2. Edit files
cd skills/my-new-skill
# - Edit SKILL.md (update YAML frontmatter and documentation)
# - Edit scripts/custom_example.py (update class name and implementation)
```

### From Scratch

1. **Create directory structure**
```bash
mkdir -p skills/my-new-skill/scripts
```

2. **Write SKILL.md**
```markdown
---
name: processing-data
description: Process data files and extract insights. Use when analyzing CSV, JSON, or text data files.
---

# Processing Data

## Quick Start

```python
result = await executor.execute('my_skill', {'file': 'data.csv'})
```

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| file | string | ✅ | Path to data file |
| format | string | ❌ | Output format (json/csv) |
```

3. **Implement skill class**
```python
# scripts/my_skill.py
from app.skills.base import BaseSkill, SkillResult

class MyNewSkill(BaseSkill):
    skill_id = "my_skill"
    name = "My New Skill"
    version = "1.0.0"
    description = "Process data files"
    category = "custom"
    timeout = 30

    parameters_schema = {
        "type": "object",
        "properties": {
            "file": {"type": "string", "description": "Path to data file"},
            "format": {"type": "string", "enum": ["json", "csv"], "description": "Output format"}
        },
        "required": ["file"]
    }

    async def execute(self, file: str, format: str = "json", **kwargs) -> SkillResult:
        try:
            # Implementation here
            return SkillResult(
                success=True,
                data={"result": "processed", "format": format}
            )
        except Exception as e:
            return SkillResult(
                success=False,
                data=None,
                error=str(e)
            )
```

4. **Done**

Restart the service. SkillRegistry will automatically discover and load your new skill.

## 📋 Skill Class Specification

```python
from app.skills.base import BaseSkill, SkillResult

class MySkill(BaseSkill):
    # Required metadata (should match SKILL.md)
    skill_id = "my_skill"              # Unique identifier
    name = "My Skill"                  # Display name
    version = "1.0.0"                  # Version
    description = "Description"        # From SKILL.md
    category = "custom"                # Category
    timeout = 30                       # Timeout in seconds

    # Parameter JSON Schema
    parameters_schema = {
        "type": "object",
        "properties": {
            "param1": {
                "type": "string",
                "description": "Description of parameter"
            }
        },
        "required": ["param1"]
    }

    async def execute(self, param1: str, **kwargs) -> SkillResult:
        """Execute the skill logic."""
        try:
            # Your implementation
            result = do_something(param1)
            return SkillResult(success=True, data=result)
        except Exception as e:
            return SkillResult(success=False, data=None, error=str(e))
```

## 📊 Built-in Skills

| skill_id | name (YAML) | Function | Documentation |
|----------|-------------|----------|---------------|
| `echo` | echoing-messages | Message echo with timestamp | [SKILL.md](skills/echoing-messages/SKILL.md) |
| `calculate` | evaluating-expressions | Mathematical calculations | [SKILL.md](skills/evaluating-expressions/SKILL.md) |
| `system_info` | monitoring-system-resources | CPU/memory/disk information | [SKILL.md](skills/monitoring-system-resources/SKILL.md) |
| `funboost_task` | submitting-funboost-tasks | Funboost queue integration | [SKILL.md](skills/submitting-funboost-tasks/SKILL.md) |
| `custom_example` | creating-custom-skills | Custom skill template | [SKILL.md](skills/creating-custom-skills/SKILL.md) |

## 📚 Best Practices

### 1. YAML Frontmatter

✅ **Good:**
```yaml
---
name: evaluating-expressions
description: Evaluate mathematical expressions safely with basic arithmetic operations. Use when performing calculations or testing mathematical logic.
---
```

❌ **Avoid:**
```yaml
---
name: MyCalculator
description: I can help you calculate math expressions
---
```

### 2. Conciseness (Progressive Disclosure)

- Keep SKILL.md under 500 lines
- Put detailed content in separate files
- Link to additional resources: [FORMS.md](FORMS.md), [REFERENCE.md](REFERENCE.md)
- Use clear section headers

### 3. Documentation vs Code

- **SKILL.md** - Documentation (loaded into context)
- **scripts/*.py** - Implementation (executed, not loaded)
- Specify "run this script" vs "read this file"

### 4. Parameter Validation

- Use JSON Schema for parameter definitions
- Validate parameters in execute() method
- Return meaningful error messages

### 5. Error Handling

- Catch exceptions and return detailed errors
- Handle edge cases gracefully
- Don't make Claude guess what went wrong

## 🔍 Loading Mechanism

1. Scan `skills/` directory
2. Find subdirectories containing `SKILL.md`
3. Find `.py` files in `scripts/` subdirectories
4. Dynamically import Python files
5. Register classes inheriting from `BaseSkill`

## 📚 Common Patterns

### Pattern 1: Template with Strict Requirements

Use when output format must be exact:

```markdown
## Report Structure

Always use this exact template:

```markdown
# [Analysis Title]

## Executive Summary
[One paragraph overview]

## Key Findings
- Finding 1 with supporting data
- Finding 2 with supporting data

## Recommendations
1. Actionable recommendation 1
2. Actionable recommendation 2
```
```

### Pattern 2: Workflow with Checklist

Use for complex multi-step processes:

```markdown
## Data Processing Workflow

Copy this checklist and track progress:

```
Progress:
- [ ] Step 1: Validate input format
- [ ] Step 2: Extract data
- [ ] Step 3: Transform data
- [ ] Step 4: Generate output
- [ ] Step 5: Verify results
```

**Step 1: Validate Input**

Run validation script: `python scripts/validate.py input.csv`

**Step 2: Extract Data**

...
```

### Pattern 3: Conditional Workflow

Use when approach depends on input type:

```markdown
## Document Modification Workflow

1. Determine modification type:

   **Creating new content?** → Follow "Creation Workflow" below
   **Editing existing content?** → Follow "Editing Workflow" below

2. Creation Workflow:
   - Use library X
   - Build from scratch
   - Export as format Y

3. Editing Workflow:
   - Parse existing document
   - Modify directly
   - Validate changes
```

## 📚 References

- [Claude Skills Best Practices](https://platform.claude.com/docs/zh-CN/agents-and-tools/agent-skills/best-practices) (Official)
- [Skills Overview](skills/README.md)
- [GRAVIX_GUIDE.md](GRAVIX_GUIDE.md)

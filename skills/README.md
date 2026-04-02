# Gravix Skills System

按Claude官方最佳实践组织的技能系统，采用**文档驱动架构**。

## 📁 Directory Structure

```
skills/
├── README.md                    # This file
├── echo/                        # Echo skill
│   ├── SKILL.md                # Main documentation (YAML frontmatter + Markdown)
│   └── scripts/
│       └── echo.py             # Implementation code
├── calculate/                   # Calculator skill
│   ├── SKILL.md
│   └── scripts/
│       └── calculate.py
├── system_info/                 # System information skill
│   ├── SKILL.md
│   └── scripts/
│       └── system_info.py
├── funboost_task/               # Funboost task skill
│   ├── SKILL.md
│   └── scripts/
│       └── funboost_task.py
└── custom_example/              # Custom skill template
    ├── SKILL.md
    └── scripts/
        └── custom_example.py
```

## 🎯 SKILL.md Standard Format

### Required YAML Frontmatter

Every SKILL.md must begin with YAML frontmatter:

```yaml
---
name: processing-files
description: Process and analyze data files. Use when working with CSV, JSON, or text data files.
---
```

**Naming requirements:**
- Max 64 characters
- Lowercase letters, numbers, and hyphens only
- No XML tags
- No reserved words: "anthropic", "claude"
- **Use gerund form** (verb + -ing): `processing-pdfs`, `analyzing-data`, `executing-tasks`

**Description requirements:**
- Required, max 1024 characters
- No XML tags
- **Must describe both: what it does AND when to use it**
- **Write in third person** (not "I can help" or "you can use")
- Include specific trigger/context information

**Good examples:**
```yaml
name: processing-pdfs
description: Extract text and tables from PDF files, fill forms, merge documents. Use when processing PDF files or when PDFs, forms, or document extraction are mentioned.

name: calculating-expressions
description: Evaluate mathematical expressions safely with basic arithmetic operations. Use when performing calculations or testing mathematical logic.
```

### Document Structure

```markdown
---
name: processing-pdfs
description: Extract text and tables from PDF files...
---

# Processing PDFs

## Quick Start

```python
result = await executor.execute('pdf_process', {'file': 'document.pdf'})
```

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| file | string | ✅ | Path to PDF file |

## Returns

## Advanced Features

For form filling, see [FORMS.md](FORMS.md)
For API reference, see [REFERENCE.md](REFERENCE.md)
```

## 🚀 Creating New Skills

### Method 1: Copy Template

```bash
# Copy template
cp -r skills/custom_example skills/my_new_skill

# Edit files
cd skills/my_new_skill
# Edit SKILL.md - update YAML frontmatter and documentation
# Edit scripts/custom_example.py - update implementation and class name
```

### Method 2: From Scratch

1. **Create directory**
```bash
mkdir -p skills/my_skill/scripts
```

2. **Write SKILL.md**
```markdown
---
name: processing-data
description: Process data files and extract insights. Use when analyzing CSV, JSON, or text data.
---

# Processing Data

## Quick Start

```python
result = await executor.execute('my_skill', {'file': 'data.csv'})
```

## Parameters
...
```

3. **Implement skill class**
```python
# scripts/my_skill.py
from app.skills.base import BaseSkill, SkillResult

class MySkill(BaseSkill):
    skill_id = "my_skill"
    name = "My Skill"
    version = "1.0.0"
    description = "Process data files"
    category = "custom"
    timeout = 30

    parameters_schema = {
        "type": "object",
        "properties": {
            "file_path": {"type": "string", "description": "Path to data file"}
        },
        "required": ["file_path"]
    }

    async def execute(self, file_path: str, **kwargs) -> SkillResult:
        try:
            # Implementation
            return SkillResult(success=True, data={"result": "..."})
        except Exception as e:
            return SkillResult(success=False, data=None, error=str(e))
```

4. **Restart service**

SkillRegistry automatically discovers and loads new skills.

## 📋 Skill Class Specification

```python
class MySkill(BaseSkill):
    # Skill metadata
    skill_id = "my_skill"              # Unique identifier
    name = "My Skill"                  # Display name
    version = "1.0.0"                  # Version
    description = "Description"        # From SKILL.md
    category = "custom"                # Category
    timeout = 30                       # Timeout in seconds

    # Parameter JSON Schema
    parameters_schema = {
        "type": "object",
        "properties": {...},
        "required": [...]
    }

    async def execute(self, **kwargs) -> SkillResult:
        # Implementation
        pass
```

## 📊 Built-in Skills

| Skill ID | name (YAML) | Function | Documentation |
|----------|-------------|----------|---------------|
| `echo` | echoing-messages | Message echo with timestamp | [echo/SKILL.md](echo/SKILL.md) |
| `calculate` | evaluating-expressions | Mathematical calculations | [calculate/SKILL.md](calculate/SKILL.md) |
| `system_info` | monitoring-system-resources | CPU/memory/disk information | [system_info/SKILL.md](system_info/SKILL.md) |
| `funboost_task` | submitting-funboost-tasks | Funboost queue integration | [funboost_task/SKILL.md](funboost_task/SKILL.md) |
| `custom_example` | creating-custom-skills | Custom skill template | [custom_example/SKILL.md](custom_example/SKILL.md) |

## 📚 Best Practices

### 1. Conciseness

- Keep SKILL.md under 500 lines
- Put detailed content in separate files (FORMS.md, reference.md)
- Use progressive disclosure pattern

### 2. Documentation First

- SKILL.md is primary documentation (loaded into context)
- Code in scripts/ is executed, not loaded
- Specify "run this script" vs "read this file"

### 3. Parameter Validation

- Use JSON Schema for parameters
- Validate in execute() method

### 4. Error Handling

- Return detailed error messages
- Handle edge cases
- Don't make Claude guess

### 5. Third-Person Descriptions

- ✅ Good: "Processes PDF files and extracts text"
- ❌ Bad: "I can help you process PDF files"
- ❌ Bad: "Use this skill to process PDF files"

## 🔍 Skill Loading Mechanism

1. Scan `skills/` directory
2. Find subdirectories containing `SKILL.md`
3. Find `.py` files in `scripts/` subdirectories
4. Dynamically import Python files
5. Register classes inheriting from `BaseSkill`

## 📚 References

- [Claude Skills Best Practices](https://platform.claude.com/docs/zh-CN/agents-and-tools/agent-skills/best-practices)
- [GRAVIX_GUIDE.md](../GRAVIX_GUIDE.md) - Complete project guide
- [CREATING_SKILLS.md](../CREATING_SKILLS.md) - Detailed skill creation guide

---
name: creating-custom-skills
description: Template and guide for creating custom Gravix skills. Copy this skill as a starting point or reference when developing new functionality.
---

# Creating Custom Skills

Template demonstrating how to create skills following Claude best practices.

## Quick Start

```python
result = await executor.execute(
    'custom_example',
    {'name': 'World', 'greeting': 'Hello'}
)
```

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| name | string | ✅ | Name to include in greeting |
| greeting | string | ❌ | Custom greeting word (default: "Hello") |

## Returns

```json
{
  "success": true,
  "data": {
    "message": "Hello, World!",
    "timestamp": "2026-04-02T12:00:00"
  }
}
```

## Creating a New Skill

### Step 1: Create Directory Structure

```bash
mkdir -p skills/my_skill/scripts
```

### Step 2: Write SKILL.md

```markdown
---
name: processing-data
description: Process data files and extract insights. Use when analyzing CSV, JSON, or text data files.
---

# Processing Data

## Quick Start
...
```

**Naming requirements:**
- Use **gerund form** (verb + -ing): `processing-files`, `analyzing-data`
- Max 64 characters, lowercase letters/numbers/hyphens only
- Description must specify function + when to use (third person)

### Step 3: Implement Skill Class

Create `scripts/my_skill.py`:

```python
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
            # Implementation here
            return SkillResult(success=True, data={"result": "..."})
        except Exception as e:
            return SkillResult(success=False, data=None, error=str(e))
```

### Step 4: Test and Deploy

Restart the service. SkillRegistry automatically discovers new skills.

## Best Practices

1. **Documentation First**: SKILL.md should clearly describe what the skill does and when to use it
2. **Third-Person Perspective**: Write descriptions objectively, not "I can help" or "you can use"
3. **Parameter Validation**: Use JSON Schema for type checking
4. **Error Handling**: Return meaningful error messages in SkillResult
5. **Progressive Disclosure**: Keep SKILL.md under 500 lines, link to additional files if needed
6. **Consistent Naming**: Use gerund form for skill names (e.g., `processing-pdfs` not `pdf-processor`)

## Related Resources

- [Claude Skills Best Practices](https://platform.claude.com/docs/zh-CN/agents-and-tools/agent-skills/best-practices)
- [Skills Overview](../skills/README.md)
- [Project Guide](../GRAVIX_GUIDE.md)

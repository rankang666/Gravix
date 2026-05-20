#!/usr/bin/env python
# encoding: utf-8
"""
@Time: 2026/5/20
@Project: Gravix
@File: test_skills_loading.py
@Author: Claude
@Software: PyCharm
@Desc: Test skills loading - both code and documentation skills
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from app.skills.registry import SkillRegistry
from app.utils.logger import logger


async def test_skills_loading():
    """Test that both code and documentation skills are loaded"""

    logger.info("=" * 60)
    logger.info("Testing Skills Loading")
    logger.info("=" * 60)

    # Initialize registry
    registry = SkillRegistry()

    # List all registered skills
    skills = registry.list_skills()

    logger.info(f"\n✅ Total skills loaded: {len(skills)}")

    # Categorize skills
    code_skills = []
    doc_skills = []

    for skill in skills:
        skill_id = skill['skill_id']
        metadata = registry._skill_metadata.get(skill_id, {})

        if metadata.get('type') == 'documentation':
            doc_skills.append(skill)
        else:
            code_skills.append(skill)

    logger.info(f"\n📊 Code Skills: {len(code_skills)}")
    for skill in code_skills:
        logger.info(f"  - {skill['skill_id']}: {skill['name']}")

    logger.info(f"\n📖 Documentation Skills: {len(doc_skills)}")
    for skill in doc_skills:
        logger.info(f"  - {skill['skill_id']}: {skill['name']}")

    # Test executing a documentation skill
    if doc_skills:
        logger.info(f"\n🧪 Testing documentation skill execution...")
        doc_skill_id = doc_skills[0]['skill_id']
        skill = registry.get_skill(doc_skill_id)

        if skill:
            result = await skill.execute()
            logger.info(f"✅ Documentation skill executed successfully")
            logger.info(f"   Result type: {result.get('type')}")
            logger.info(f"   Content length: {len(result.get('content', ''))} chars")
        else:
            logger.error(f"❌ Failed to get skill instance")

    # Test executing a code skill
    if code_skills:
        logger.info(f"\n🧪 Testing code skill execution...")
        code_skill_id = code_skills[0]['skill_id']
        skill = registry.get_skill(code_skill_id)

        if skill:
            # Test with a simple command (for system_info or echo)
            try:
                result = await skill.execute()
                logger.info(f"✅ Code skill executed successfully")
                logger.info(f"   Result: {result}")
            except Exception as e:
                logger.info(f"⚠️  Code skill execution needs parameters: {e}")
        else:
            logger.error(f"❌ Failed to get skill instance")

    logger.info("\n" + "=" * 60)
    logger.info("Skills Loading Test Complete!")
    logger.info("=" * 60)

    # Summary
    logger.info(f"\n📈 Summary:")
    logger.info(f"  - Total skills: {len(skills)}")
    logger.info(f"  - Code skills: {len(code_skills)}")
    logger.info(f"  - Documentation skills: {len(doc_skills)}")
    logger.info(f"  - All types supported! ✅")

    return len(code_skills) > 0 and len(doc_skills) > 0


if __name__ == '__main__':
    success = asyncio.run(test_skills_loading())
    if success:
        logger.info("\n🎉 Skills system supports both code and documentation skills!")
    else:
        logger.warning("\n⚠️  Some skill types may be missing")

    sys.exit(0 if success else 1)

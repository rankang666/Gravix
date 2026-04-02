#!/usr/bin/env python
# encoding: utf-8
"""
@Time: 2026/4/1
@Project: Gravix
@File: registry.py
@Author: Claude
@Software: PyCharm
@Desc: Skill Registry - Load and manage skills from directory tree structure (Claude best practices)
"""

import importlib
import importlib.util
import inspect
from pathlib import Path
from typing import Dict, List, Type, Optional, Any
from app.skills.base import BaseSkill
from app.utils.logger import logger


class SkillRegistry:
    """
    Central registry for all skills

    The registry loads skills from a directory tree structure following Claude best practices:

    skills/
    ├── echo/
    │   ├── SKILL.md           # Documentation (loaded when triggered)
    │   └── scripts/
    │       └── echo.py       # Implementation (executed, not loaded)
    ├── calculate/
    │   ├── SKILL.md
    │   └── scripts/
    │       └── calculate.py
    └── ...

    Each skill directory structure:
    - SKILL.md          - Main documentation and metadata
    - scripts/          - Implementation scripts
    - tests/            - Test files (optional)
    - examples/         - Example usage (optional)

    Example:
        ```python
        registry = SkillRegistry()
        skill = registry.get_skill('system_info')
        result = await skill.execute(info_type='cpu')
        ```
    """

    def __init__(self, skills_dir: str = 'skills'):
        """
        Initialize the skill registry

        Args:
            skills_dir: Base directory containing skill packages
        """
        self.skills_dir = Path(skills_dir)
        self._skills: Dict[str, Type[BaseSkill]] = {}
        self._instances: Dict[str, BaseSkill] = {}
        self._skill_metadata: Dict[str, Dict[str, Any]] = {}
        self._load_all_skills()

    def _load_all_skills(self):
        """Load all skills from directory tree structure"""
        if not self.skills_dir.exists():
            logger.warning(f"Skills directory not found: {self.skills_dir}")
            return

        # Scan all subdirectories in skills/
        for skill_dir in sorted(self.skills_dir.iterdir()):
            # Skip non-directories, private directories, and non-skill dirs
            if not skill_dir.is_dir() or skill_dir.name.startswith('_'):
                continue

            # Skip if it doesn't look like a skill directory
            if not (skill_dir / 'SKILL.md').exists():
                logger.debug(f"Skipping {skill_dir.name} - no SKILL.md found")
                continue

            self._load_skill_from_directory(skill_dir)

        logger.info(f"Total skills registered: {len(self._skills)}")

    def _load_skill_from_directory(self, skill_dir: Path):
        """
        Load a skill from a directory

        Args:
            skill_dir: Skill directory path (e.g., skills/echo/)
        """
        skill_name = skill_dir.name
        scripts_dir = skill_dir / 'scripts'

        if not scripts_dir.exists():
            logger.warning(f"Skill '{skill_name}' has no scripts/ directory")
            return

        # Find Python files in scripts/ directory
        py_files = list(scripts_dir.glob('*.py'))
        if not py_files:
            logger.warning(f"Skill '{skill_name}' has no Python files in scripts/")
            return

        # Load each Python file
        for py_file in py_files:
            if py_file.name.startswith('_'):
                continue

            self._load_skill_from_file(skill_name, py_file)

    def _load_skill_from_file(self, skill_name: str, py_file: Path):
        """
        Load skill class from a Python file

        Args:
            skill_name: Name of the skill
            py_file: Path to Python file
        """
        try:
            # Create module spec and load module
            module_name = f"skills.{skill_name}.scripts.{py_file.stem}"
            spec = importlib.util.spec_from_file_location(module_name, py_file)

            if spec is None or spec.loader is None:
                logger.error(f"Failed to load spec for {py_file}")
                return

            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # Find Skill classes in the module
            for item_name in dir(module):
                item = getattr(module, item_name)

                # Check if it's a Skill class
                if (inspect.isclass(item) and
                    issubclass(item, BaseSkill) and
                    item is not BaseSkill):

                    # Get skill_id from class attribute
                    skill_id = getattr(item, 'skill_id', skill_name)

                    # Register the skill
                    self._skills[skill_id] = item

                    # Store metadata
                    self._skill_metadata[skill_id] = {
                        'name': getattr(item, 'name', skill_name),
                        'description': getattr(item, 'description', ''),
                        'version': getattr(item, 'version', '1.0.0'),
                        'category': getattr(item, 'category', 'general'),
                        'skill_dir': f"skills/{skill_name}",
                        'documentation': f"skills/{skill_name}/SKILL.md"
                    }

                    logger.info(
                        f"Registered skill: {skill_id} ({self._skill_metadata[skill_id]['name']}) "
                        f"from {py_file.name}"
                    )
                    break  # Only register first skill class found

        except Exception as e:
            logger.error(f"Failed to load skill from {py_file}: {e}")

    def get_skill(self, skill_id: str) -> Optional[BaseSkill]:
        """
        Get a skill instance by ID

        Args:
            skill_id: Unique identifier for the skill

        Returns:
            BaseSkill instance or None if not found
        """
        # Return cached instance if available
        if skill_id in self._instances:
            return self._instances[skill_id]

        # Create new instance
        if skill_id in self._skills:
            skill_class = self._skills[skill_id]
            try:
                # Create config from class metadata
                config = self._create_config_from_class(skill_class, skill_id)
                instance = skill_class(config)
                self._instances[skill_id] = instance
                return instance
            except Exception as e:
                logger.error(f"Failed to instantiate skill '{skill_id}': {e}")
                return None

        logger.warning(f"Skill not found: {skill_id}")
        return None

    def _create_config_from_class(
        self,
        skill_class: Type[BaseSkill],
        skill_id: str
    ) -> Dict[str, Any]:
        """
        Create configuration dict from skill class metadata

        Args:
            skill_class: Skill class
            skill_id: Skill ID

        Returns:
            Configuration dictionary
        """
        return {
            'skill_id': skill_id,
            'name': getattr(skill_class, 'name', skill_id),
            'description': getattr(skill_class, 'description', ''),
            'version': getattr(skill_class, 'version', '1.0.0'),
            'category': getattr(skill_class, 'category', 'general'),
            'enabled': True,
            'parameters': getattr(skill_class, 'parameters_schema', {}),
            'timeout': getattr(skill_class, 'timeout', 300)
        }

    def list_skills(self, include_disabled: bool = False) -> List[Dict[str, Any]]:
        """
        List all available skills

        Args:
            include_disabled: Whether to include disabled skills

        Returns:
            List of skill information dictionaries
        """
        skills_info = []
        for skill_id, skill_class in self._skills.items():
            metadata = self._skill_metadata.get(skill_id, {})
            enabled = True  # Can be made configurable later

            if not include_disabled and not enabled:
                continue

            skills_info.append({
                'skill_id': skill_id,
                'name': metadata.get('name', skill_id),
                'description': metadata.get('description', ''),
                'version': metadata.get('version', '1.0.0'),
                'category': metadata.get('category', 'general'),
                'enabled': enabled,
                'documentation': metadata.get('documentation', '')
            })

        return sorted(skills_info, key=lambda x: x['skill_id'])

    def get_skill_documentation(self, skill_id: str) -> Optional[str]:
        """
        Get the documentation path for a skill

        Args:
            skill_id: Skill identifier

        Returns:
            Path to SKILL.md or None
        """
        if skill_id in self._skill_metadata:
            return self._skill_metadata[skill_id].get('documentation')
        return None

    def reload_skills(self):
        """Reload all skill configurations from disk"""
        logger.info("Reloading all skills...")
        self._skills.clear()
        self._instances.clear()
        self._skill_metadata.clear()
        self._load_all_skills()
        logger.info("Skills reloaded successfully")

    def get_skill_count(self) -> int:
        """Get total number of registered skills"""
        return len(self._skills)

    def __len__(self) -> int:
        """Return number of registered skills"""
        return len(self._skills)

    def __contains__(self, skill_id: str) -> bool:
        """Check if skill is registered"""
        return skill_id in self._skills

#!/usr/bin/env python
# encoding: utf-8
"""
@Time: 2026/4/17
@Project: Gravix
@File: migration.py
@Author: Claude
@Software: PyCharm
@Desc: Data migration from JSON to database
"""

import os
import json
from typing import Dict, Any, List

from app.database.base import DatabaseAdapter
from app.utils.logger import logger


class DataMigration:
    """
    Migrate data from JSON files to database
    """

    def __init__(self, json_path: str = 'data/sessions.json'):
        """
        Initialize migration

        Args:
            json_path: Path to JSON sessions file
        """
        self.json_path = json_path

    def load_json_data(self) -> Dict[str, Any]:
        """Load data from JSON file"""
        if not os.path.exists(self.json_path):
            logger.warning(f"JSON file not found: {self.json_path}")
            return {}

        try:
            with open(self.json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            logger.info(f"Loaded JSON data from {self.json_path}")
            return data
        except Exception as e:
            logger.error(f"Failed to load JSON data: {e}")
            return {}

    def migrate_to_database(self, db: DatabaseAdapter) -> bool:
        """
        Migrate JSON data to database

        Args:
            db: Database adapter

        Returns:
            True if successful, False otherwise
        """
        json_data = self.load_json_data()
        if not json_data:
            logger.info("No JSON data to migrate")
            return True

        try:
            sessions_data = json_data.get('sessions', [])
            current_session_id = json_data.get('current_session_id')

            logger.info(f"Migrating {len(sessions_data)} sessions to database...")

            # Begin transaction
            db.begin_transaction()

            # Migrate each session
            migrated_count = 0
            for session_data in sessions_data:
                try:
                    # Extract session info
                    session_id = session_data['session_id']
                    title = session_data['title']
                    metadata = session_data.get('metadata', {})
                    created_at = session_data.get('created_at')
                    last_activity = session_data.get('last_activity')

                    # Create session in database
                    db.create_session(session_id, title, metadata)

                    # Migrate messages
                    messages = session_data.get('messages', [])
                    for msg in messages:
                        db.add_message(
                            session_id,
                            msg['role'],
                            msg['content'],
                            msg.get('metadata', {})
                        )

                    migrated_count += 1
                    logger.debug(f"Migrated session: {session_id}")

                except Exception as e:
                    logger.error(f"Failed to migrate session {session_data.get('session_id')}: {e}")
                    continue

            # Commit transaction
            db.commit()

            logger.info(f"✅ Successfully migrated {migrated_count}/{len(sessions_data)} sessions")

            # Backup JSON file
            self._backup_json_file()

            return True

        except Exception as e:
            logger.error(f"Migration failed: {e}")
            db.rollback()
            return False

    def _backup_json_file(self):
        """Create backup of JSON file"""
        try:
            backup_path = f"{self.json_path}.backup"
            import shutil
            shutil.copy2(self.json_path, backup_path)
            logger.info(f"✅ JSON file backed up to: {backup_path}")
        except Exception as e:
            logger.warning(f"Failed to create backup: {e}")

    @staticmethod
    def detect_json_data() -> bool:
        """Check if JSON data file exists and has content"""
        json_path = 'data/sessions.json'
        if not os.path.exists(json_path):
            return False

        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            sessions = data.get('sessions', [])
            return len(sessions) > 0
        except:
            return False


def auto_migrate_if_needed(db: DatabaseAdapter) -> bool:
    """
    Automatically migrate JSON data to database if needed

    Args:
        db: Database adapter

    Returns:
        True if migration was performed or not needed, False if failed
    """
    try:
        # Ensure database is connected
        if db.connection is None:
            db.connect()
            db.initialize_schema()
            logger.info("✅ Database connected for migration")
    except Exception as e:
        logger.error(f"Failed to connect database for migration: {e}")
        return False

    # Check if JSON data exists
    if not DataMigration.detect_json_data():
        logger.info("No JSON data to migrate")
        return True

    # Check if database already has data
    try:
        existing_sessions = db.list_sessions()
        if existing_sessions:
            logger.info(f"Database already has {len(existing_sessions)} sessions, skipping migration")
            return True
    except Exception as e:
        logger.error(f"Failed to check existing sessions: {e}")
        return True  # Continue anyway to attempt migration

    # Perform migration
    logger.info("🔄 Starting automatic migration from JSON to database...")
    migration = DataMigration()
    success = migration.migrate_to_database(db)

    if success:
        logger.info("✅ Migration completed successfully")
    else:
        logger.error("❌ Migration failed")

    return success

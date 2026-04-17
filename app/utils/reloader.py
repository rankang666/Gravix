#!/usr/bin/env python
# encoding: utf-8
"""
@Time: 2026/4/16
@Project: Gravix
@File: reloader.py
@Desc: Hot reload functionality for development
"""

import asyncio
import os
import sys
import signal
from pathlib import Path
from typing import Set, Callable, Optional
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileModifiedEvent

from app.utils.logger import logger


class CodeChangeHandler(FileSystemEventHandler):
    """Handle Python file change events"""

    def __init__(
        self,
        reload_callback: Callable,
        ignored_dirs: Set[str] = None,
        ignored_files: Set[str] = None
    ):
        """
        Initialize code change handler

        Args:
            reload_callback: Function to call when code changes
            ignored_dirs: Directories to ignore (e.g., __pycache__, .git)
            ignored_files: Files to ignore (e.g., .pyc, .log)
        """
        super().__init__()
        self.reload_callback = reload_callback
        self.ignored_dirs = ignored_dirs or {
            '__pycache__',
            '.git',
            '.pytest_cache',
            'node_modules',
            '.venv',
            'venv',
            'env',
            'Html'
        }
        self.ignored_files = ignored_files or {
            '.pyc',
            '.pyo',
            '.pyd',
            '.so',
            '.log',
            '.db',
            '.sqlite'
        }
        self.last_reload = 0
        self.reload_cooldown = 1.0  # Seconds between reloads

    def on_modified(self, event):
        """Handle file modification event"""
        if event.is_directory:
            return

        # Check if should ignore this file/directory
        path = Path(event.src_path)

        # Ignore by directory
        if any(part in self.ignored_dirs for part in path.parts):
            return

        # Ignore by file extension/name
        if path.suffix in self.ignored_files or path.name in self.ignored_files:
            return

        # Only process Python files
        if path.suffix == '.py':
            import time
            current_time = time.time()

            # Prevent rapid reloads (cooldown)
            if current_time - self.last_reload < self.reload_cooldown:
                return

            self.last_reload = current_time

            logger.info(f"📝 Code change detected: {path}")
            logger.info("♻️  Reloading server...")

            # Trigger reload callback
            if asyncio.iscoroutinefunction(self.reload_callback):
                # If callback is async, create a task
                asyncio.create_task(self.reload_callback(path))
            else:
                # If callback is sync, call it directly
                self.reload_callback(path)


class HotReloadManager:
    """
    Hot reload manager for development

    Monitors Python files for changes and triggers server reload
    """

    def __init__(
        self,
        watch_paths: list = None,
        on_reload: Callable = None,
        enabled: bool = True
    ):
        """
        Initialize hot reload manager

        Args:
            watch_paths: List of paths to monitor (defaults to project root)
            on_reload: Callback function when code changes
            enabled: Whether hot reload is enabled
        """
        self.enabled = enabled
        self.observer = None
        self.watch_paths = watch_paths or []
        self.on_reload = on_reload
        self.is_running = False

        if not self.watch_paths:
            # Default to current directory
            self.watch_paths = [Path.cwd()]

        if self.enabled:
            logger.info("♻️  Hot reload enabled - Monitoring for code changes")
            for path in self.watch_paths:
                logger.info(f"   Watching: {path}")

    async def start(self):
        """Start monitoring for file changes"""
        if not self.enabled:
            return

        if self.is_running:
            logger.warning("Hot reload already running")
            return

        try:
            self.observer = Observer()
            handler = CodeChangeHandler(
                reload_callback=self._trigger_reload,
                ignored_dirs={
                    '__pycache__', '.git', '.pytest_cache',
                    'node_modules', '.venv', 'venv', 'Html'
                }
            )

            # Add all watch paths
            for watch_path in self.watch_paths:
                if os.path.exists(watch_path):
                    self.observer.schedule(handler, str(watch_path), recursive=True)
                    logger.info(f"📁 Monitoring: {watch_path}")

            self.observer.start()
            self.is_running = True
            logger.info("✅ Hot reload manager started")

        except Exception as e:
            logger.error(f"Failed to start hot reload: {e}")
            logger.info("Continuing without hot reload...")

    def stop(self):
        """Stop monitoring file changes"""
        if self.observer:
            self.observer.stop()
            self.observer.join()
            self.is_running = False
            logger.info("♻️  Hot reload manager stopped")

    async def _trigger_reload(self, changed_file: Path):
        """Trigger server reload"""
        logger.info(f"♻️  Reloading due to change in: {changed_file}")

        if self.on_reload:
            try:
                if asyncio.iscoroutinefunction(self.on_reload):
                    await self.on_reload(changed_file)
                else:
                    self.on_reload(changed_file)
            except Exception as e:
                logger.error(f"Error during reload: {e}")

    async def reload_with_notification(self, changed_file: Path = None):
        """
        Reload with notification to all connected clients

        Args:
            changed_file: File that triggered the reload
        """
        from app.chat.http_server import ChatHTTPServer

        # This will be called by the handler, notify clients if needed
        if changed_file:
            logger.info(f"🔄 Server reloaded (change: {changed_file.name})")
        else:
            logger.info("🔄 Server reloaded")

        # Send reload notification to clients if you have access to them
        # You can pass a callback to do this


def setup_signal_handlers(reload_callback: Callable):
    """Setup signal handlers for manual reload"""
    try:
        # SIGUSR1 for manual reload (Unix/Linux/Mac)
        signal.signal(signal.SIGUSR1, lambda sig, frame: reload_callback())
        logger.info("💡 Send SIGUSR1 to manually trigger reload: kill -USR1 <pid>")
    except AttributeError:
        # Windows doesn't have SIGUSR1
        pass

    # SIGINT for graceful shutdown
    signal.signal(signal.SIGINT, signal.SIG_DFL)


async def watch_and_reload(
    reload_func: Callable,
    paths: list = None
):
    """
    Simple watch and reload loop

    Args:
        reload_func: Async function to call for reload
        paths: Paths to watch
    """
    import time

    paths = paths or [Path.cwd()]
    logger.info(f"🔍 Starting simple file watcher for: {paths}")

    last_modification_times = {}

    # Initial scan
    for watch_path in paths:
        for py_file in Path(watch_path).rglob('*.py'):
            if '__pycache__' not in str(py_file):
                last_modification_times[str(py_file)] = os.path.getmtime(py_file)

    logger.info(f"📝 Watching {len(last_modification_times)} Python files")

    try:
        while True:
            await asyncio.sleep(1)  # Check every second

            for py_file, last_mtime in list(last_modification_times.items()):
                if not os.path.exists(py_file):
                    # File was deleted
                    del last_modification_times[py_file]
                    continue

                current_mtime = os.path.getmtime(py_file)

                if current_mtime > last_mtime:
                    logger.info(f"📝 Changed: {py_file}")
                    last_modification_times[py_file] = current_mtime

                    # Trigger reload
                    try:
                        if asyncio.iscoroutinefunction(reload_func):
                            await reload_func(py_file)
                        else:
                            reload_func(py_file)
                    except Exception as e:
                        logger.error(f"Error during reload: {e}")

    except asyncio.CancelledError:
        logger.info("File watcher stopped")

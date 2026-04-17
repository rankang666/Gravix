#!/usr/bin/env python3
# encoding: utf-8
"""
Test script to verify hot reload functionality
"""

import os
import sys
import time
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))


def test_hot_reload_detection():
    """Test that hot reload detects file changes"""
    print("=" * 60)
    print("Hot Reload Detection Test")
    print("=" * 60)
    print()

    # Check if watchdog is installed
    try:
        import watchdog
        print("✅ watchdog library is installed")
    except ImportError:
        print("❌ watchdog library not found")
        print()
        print("Install it with:")
        print("  pip install watchdog==3.0.0")
        return False

    print()

    # Check if reloader module can be imported
    try:
        from app.utils.reloader import HotReloadManager, CodeChangeHandler
        print("✅ Hot reload module can be imported")
    except ImportError as e:
        print(f"❌ Cannot import hot reload module: {e}")
        return False

    print()

    # Test handler creation
    try:
        def dummy_reload(path):
            print(f"🔄 Reload triggered by: {path}")

        handler = CodeChangeHandler(
            reload_callback=dummy_reload,
            ignored_dirs={'__pycache__', '.git', 'Html'},
            ignored_files={'.pyc', '.log'}
        )
        print("✅ Code change handler created")
        print(f"   Ignored dirs: {handler.ignored_dirs}")
        print(f"   Ignored files: {handler.ignored_files}")
    except Exception as e:
        print(f"❌ Failed to create handler: {e}")
        return False

    print()

    # Test manager creation
    try:
        manager = HotReloadManager(
            watch_paths=[Path.cwd()],
            on_reload=dummy_reload,
            enabled=True
        )
        print("✅ Hot reload manager created")
        print(f"   Watching: {manager.watch_paths}")
        print(f"   Enabled: {manager.enabled}")
    except Exception as e:
        print(f"❌ Failed to create manager: {e}")
        return False

    print()
    print("=" * 60)
    print("✅ All hot reload components verified!")
    print("=" * 60)
    print()
    print("Next steps:")
    print("1. Install watchdog: pip install watchdog==3.0.0")
    print("2. Enable hot reload: ENABLE_HOT_RELOAD=true python3 run_all.py")
    print("3. Modify a Python file and watch for reload message")
    print()

    return True


def simulate_file_change():
    """Simulate a file change to test the handler"""
    print("=" * 60)
    print("File Change Simulation")
    print("=" * 60)
    print()

    from app.utils.reloader import CodeChangeHandler

    reload_triggered = False

    def test_reload(path):
        nonlocal reload_triggered
        reload_triggered = True
        print(f"✅ Reload triggered: {path}")

    handler = CodeChangeHandler(reload_callback=test_reload)

    # Simulate different file changes
    test_cases = [
        ("app/chat/server.py", True, "Python file - should trigger"),
        ("system_prompt.txt", False, "Non-Python file - should not trigger"),
        ("__pycache__/test.pyc", False, "Cache file - should be ignored"),
        (".git/config", False, "Git file - should be ignored"),
        ("app/test.py", True, "Python file in app - should trigger"),
    ]

    print("Testing file change detection:")
    print()

    for file_path, should_trigger, description in test_cases:
        reload_triggered = False

        # Create mock event
        class MockEvent:
            def __init__(self, path):
                self.src_path = path

        event = MockEvent(file_path)
        handler.on_modified(event)

        if should_trigger:
            if reload_triggered:
                print(f"✅ {description}")
                print(f"   {file_path}")
            else:
                print(f"❌ {description} - FAILED")
                print(f"   {file_path}")
                return False
        else:
            if not reload_triggered:
                print(f"✅ {description}")
                print(f"   {file_path}")
            else:
                print(f"❌ {description} - FAILED")
                print(f"   {file_path}")
                return False

    print()
    return True


def main():
    """Run all tests"""
    print()
    result1 = test_hot_reload_detection()
    print()

    if result1:
        result2 = simulate_file_change()
        print()

        if result2:
            print("=" * 60)
            print("🎉 All hot reload tests passed!")
            print("=" * 60)
            print()
            print("Hot reload is ready to use!")
            print()
            print("Start your server with:")
            print("  ENABLE_HOT_RELOAD=true python3 run_all.py")
            return 0

    print("=" * 60)
    print("❌ Some tests failed")
    print("=" * 60)
    return 1


if __name__ == "__main__":
    sys.exit(main())

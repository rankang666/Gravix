#!/usr/bin/env python3
# encoding: utf-8
"""
WebSocket connection test for Gravix Chat Server
"""

import asyncio
import json
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

import aiohttp
import os
from datetime import datetime

# Load environment variables
env_path = Path(__file__).parent / '.env'
if env_path.exists():
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key.strip()] = value.strip()


async def test_websocket_connection():
    """Test WebSocket connection and basic message flow"""

    print("=" * 60)
    print("Gravix WebSocket Connection Test")
    print("=" * 60)
    print()

    ws_url = "ws://localhost:8765/ws"

    try:
        async with aiohttp.ClientSession() as session:
            async with session.ws_connect(ws_url) as ws:
                print(f"✅ Connected to {ws_url}")
                print()

                # Receive welcome message
                msg = await ws.receive()
                if msg.type == aiohttp.WSMsgType.TEXT:
                    data = json.loads(msg.data)
                    print(f"📩 Server message: {data.get('content', 'No content')}")
                print()

                # Send test message
                test_message = {
                    "type": "chat",
                    "content": "/help"
                }

                print(f"📤 Sending test message: {test_message['content']}")
                await ws.send_json(test_message)
                print()

                # Receive responses
                print("📩 Waiting for responses...")
                response_count = 0
                max_responses = 5  # Limit responses to avoid infinite wait

                while response_count < max_responses:
                    msg = await ws.receive()

                    if msg.type == aiohttp.WSMsgType.TEXT:
                        data = json.loads(msg.data)
                        msg_type = data.get('type')

                        if msg_type == 'thinking':
                            print(f"💭 {data.get('content', 'Thinking...')}")
                        elif msg_type == 'chat_response':
                            print(f"🤖 AI Response:\n{data.get('content', '')}")
                            response_count += 1
                            # After chat_response, we're done
                            break
                        elif msg_type == 'system':
                            print(f"📢 System: {data.get('content', '')}")

                    elif msg.type == aiohttp.WSMsgType.CLOSED:
                        print("❌ Connection closed by server")
                        break

                    elif msg.type == aiohttp.WSMsgType.ERROR:
                        print(f"❌ WebSocket error: {ws.exception()}")
                        break

                print()
                print("=" * 60)
                print("✅ WebSocket connection test completed!")
                print("=" * 60)
                return True

    except aiohttp.ClientConnectorError as e:
        print(f"❌ Connection failed: {e}")
        print()
        print("Possible reasons:")
        print("1. Server is not running - Start with: python3 run_all.py")
        print("2. Wrong port - Check if server is running on port 8765")
        print("3. Firewall blocking - Check your firewall settings")
        print()
        print("Try: lsof -i :8765  (check if port is in use)")
        return False

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_http_access():
    """Test HTTP access to static files"""

    print("=" * 60)
    print("HTTP Access Test")
    print("=" * 60)
    print()

    base_url = "http://localhost:8765"

    try:
        async with aiohttp.ClientSession() as session:
            # Test main page
            print(f"📥 Testing: {base_url}/")
            async with session.get(base_url) as resp:
                if resp.status == 200:
                    print(f"✅ Status: {resp.status}")
                    content_type = resp.headers.get('Content-Type', '')
                    print(f"✅ Content-Type: {content_type}")
                else:
                    print(f"❌ Status: {resp.status}")

            print()

            # Test favicon (should return 204)
            print(f"📥 Testing: {base_url}/favicon.ico")
            async with session.get(f"{base_url}/favicon.ico") as resp:
                print(f"✅ Status: {resp.status} (204 = No Content, expected)")
                if resp.status != 204:
                    print(f"⚠️  Unexpected favicon response")

        print()
        return True

    except aiohttp.ClientConnectorError as e:
        print(f"❌ HTTP connection failed: {e}")
        return False

    except Exception as e:
        print(f"❌ HTTP test failed: {e}")
        return False


async def main():
    """Run all tests"""

    # Test HTTP first
    http_ok = await test_http_access()

    print()

    # Test WebSocket
    ws_ok = await test_websocket_connection()

    print()
    if http_ok and ws_ok:
        print("🎉 All tests passed! Your Gravix server is working correctly.")
        print()
        print("Next steps:")
        print("1. Open browser: http://localhost:8765")
        print("2. Start chatting!")
        return 0
    else:
        print("❌ Some tests failed. Please check the errors above.")
        return 1


if __name__ == '__main__':
    sys.exit(asyncio.run(main()))

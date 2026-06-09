import asyncio
import json
from typing import Optional, List, Dict, Any
from pathlib import Path
from utils.logger import logger


class MCPServer:

    def __init__(self, name: str, command: str, args: List[str] = None, env: Dict[str, str] = None):
        self.name = name
        self.command = command
        self.args = args or []
        self.env = env or {}
        self.process = None
        self.request_id = 0

    async def start(self) -> bool:
        try:
            env = {**self.env}
            self.process = await asyncio.create_subprocess_exec(
                self.command, *self.args,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env=env
            )
            await asyncio.sleep(2)

            init_request = {
                "jsonrpc": "2.0",
                "id": self.request_id,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2025-06-18",
                    "capabilities": {},
                    "clientInfo": {"name": "ThreadsAutoPoster", "version": "1.0.0"}
                }
            }
            await self._send(init_request)
            response = await self._receive()

            if response and "result" in response:
                logger.success(f"MCP server '{self.name}' started")
                return True
            else:
                logger.error(f"MCP server '{self.name}' did not respond to initialize")
                return False

        except Exception as e:
            logger.error(f"Failed to start MCP server '{self.name}': {e}")
            return False

    async def stop(self):
        if self.process:
            self.process.terminate()
            await self.process.wait()
            logger.info(f"MCP server '{self.name}' stopped")

    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Optional[str]:
        try:
            self.request_id += 1
            request = {
                "jsonrpc": "2.0",
                "id": self.request_id,
                "method": "tools/call",
                "params": {
                    "name": tool_name,
                    "arguments": arguments
                }
            }

            await self._send(request)
            response = await self._receive()

            if response and "result" in response:
                content = response["result"].get("content", [])
                if content and len(content) > 0:
                    text = content[0].get("text", "")
                    return text
            return None

        except Exception as e:
            logger.error(f"Error calling tool '{tool_name}' on '{self.name}': {e}")
            return None

    async def _send(self, message: Dict):
        if not self.process or self.process.stdin.closed:
            raise Exception("Process not running")

        msg_str = json.dumps(message) + "\n"
        self.process.stdin.write(msg_str.encode())
        await self.process.stdin.drain()

    async def _receive(self) -> Optional[Dict]:
        if not self.process or self.process.stdout.at_eof():
            return None

        try:
            line = await asyncio.wait_for(self.process.stdout.readline(), timeout=30.0)
            if line:
                return json.loads(line.decode())
        except asyncio.TimeoutError:
            logger.warning("MCP server timeout")
        except Exception as e:
            logger.error(f"MCP receive error: {e}")

        return None


class MCPManager:

    def __init__(self):
        self.servers: Dict[str, MCPServer] = {}
        self.config_path = Path('config/mcp_servers.json')

    async def load_servers(self):
        if not self.config_path.exists():
            logger.info("MCP config not found, creating example")
            self._create_example_config()
            return

        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)

            for server_config in config.get('servers', []):
                name = server_config['name']
                command = server_config['command']
                args = server_config.get('args', [])
                env = server_config.get('env', {})

                server = MCPServer(name, command, args, env)
                if await server.start():
                    self.servers[name] = server

        except Exception as e:
            logger.error(f"Error loading MCP config: {e}")

    async def stop_all(self):
        for server in self.servers.values():
            await server.stop()

    def add_server(self, name: str, command: str, args: List[str] = None, env: Dict[str, str] = None):
        config = {"servers": []}
        if self.config_path.exists():
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)

        config['servers'].append({
            "name": name,
            "command": command,
            "args": args or [],
            "env": env or {}
        })

        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)

        logger.info(f"Added MCP server: {name}")

    def remove_server(self, name: str) -> bool:
        if not self.config_path.exists():
            return False

        with open(self.config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)

        original_len = len(config.get('servers', []))
        config['servers'] = [s for s in config.get('servers', []) if s['name'] != name]

        if len(config['servers']) == original_len:
            return False

        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)

        logger.info(f"Removed MCP server: {name}")
        return True

    def list_servers(self) -> List[Dict]:
        if not self.config_path.exists():
            return []

        with open(self.config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)

        return config.get('servers', [])

    def _create_example_config(self):
        example = {
            "servers": [
                {
                    "name": "web-search",
                    "command": "python",
                    "args": ["server.py"],
                    "env": {}
                }
            ]
        }

        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(example, f, indent=2, ensure_ascii=False)

        logger.info(f"Created example config: {self.config_path}")

    async def search(self, query: str, max_results: int = 3) -> Optional[str]:
        for server_name, server in self.servers.items():
            try:
                result = await server.call_tool("web_search", {
                    "query": query,
                    "max_results": max_results
                })
                if result:
                    logger.info(f"MCP search via '{server_name}' for: {query}")
                    return result
            except Exception as e:
                logger.warning(f"MCP server '{server_name}' search failed: {e}")

        return None


mcpManager = MCPManager()
mcpClient = mcpManager

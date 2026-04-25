"""
Model Context Protocol (MCP) Server
Exposes Customer Success FTE tools via MCP protocol
"""

import asyncio
import json
from typing import Any, Dict, List, Optional
from datetime import datetime
import sys

# Import tool implementations
from agent.tools import (
    search_knowledge_base,
    create_ticket,
    get_customer_history,
    escalate_to_human,
    send_response
)


class MCPServer:
    """MCP Server for Customer Success FTE"""

    def __init__(self):
        self.name = "customer-success-fte"
        self.version = "1.0.0"
        self.tools = self._register_tools()

    def _register_tools(self) -> List[Dict[str, Any]]:
        """Register all available tools with MCP metadata"""
        return [
            {
                "name": "search_knowledge_base",
                "description": "Search product documentation for relevant information. Use when customer asks about product features, how-to questions, or needs technical information.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Search query text"
                        },
                        "max_results": {
                            "type": "integer",
                            "description": "Maximum number of results to return",
                            "default": 5
                        }
                    },
                    "required": ["query"]
                }
            },
            {
                "name": "create_ticket",
                "description": "Create a support ticket for tracking. ALWAYS create a ticket at the start of every conversation. Include the source channel.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "customer_id": {
                            "type": "string",
                            "description": "Customer UUID"
                        },
                        "issue": {
                            "type": "string",
                            "description": "Brief description of the issue"
                        },
                        "channel": {
                            "type": "string",
                            "enum": ["email", "whatsapp", "web_form"],
                            "description": "Source channel"
                        },
                        "priority": {
                            "type": "string",
                            "enum": ["low", "medium", "high", "urgent"],
                            "description": "Priority level",
                            "default": "medium"
                        },
                        "category": {
                            "type": "string",
                            "description": "Issue category (optional)"
                        }
                    },
                    "required": ["customer_id", "issue", "channel"]
                }
            },
            {
                "name": "get_customer_history",
                "description": "Get customer's complete interaction history across ALL channels. Use to understand context from previous conversations.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "customer_id": {
                            "type": "string",
                            "description": "Customer UUID"
                        }
                    },
                    "required": ["customer_id"]
                }
            },
            {
                "name": "escalate_to_human",
                "description": "Escalate conversation to human support. Use when: customer asks about pricing/refunds, sentiment is negative, cannot find information, or customer requests human help.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "ticket_id": {
                            "type": "string",
                            "description": "Ticket UUID"
                        },
                        "reason": {
                            "type": "string",
                            "description": "Detailed reason for escalation"
                        },
                        "urgency": {
                            "type": "string",
                            "enum": ["normal", "high", "urgent"],
                            "description": "Urgency level",
                            "default": "normal"
                        }
                    },
                    "required": ["ticket_id", "reason"]
                }
            },
            {
                "name": "send_response",
                "description": "Send response to customer via their channel. Response will be automatically formatted (email: formal, WhatsApp: concise, web: semi-formal).",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "ticket_id": {
                            "type": "string",
                            "description": "Ticket UUID"
                        },
                        "message": {
                            "type": "string",
                            "description": "Response message content"
                        },
                        "channel": {
                            "type": "string",
                            "enum": ["email", "whatsapp", "web_form"],
                            "description": "Target channel"
                        }
                    },
                    "required": ["ticket_id", "message", "channel"]
                }
            }
        ]

    async def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle incoming MCP request

        Args:
            request: MCP request object

        Returns:
            MCP response object
        """
        method = request.get("method")
        params = request.get("params", {})

        try:
            if method == "tools/list":
                return await self._list_tools()
            elif method == "tools/call":
                return await self._call_tool(params)
            elif method == "server/info":
                return await self._server_info()
            else:
                return {
                    "error": {
                        "code": -32601,
                        "message": f"Method not found: {method}"
                    }
                }

        except Exception as e:
            return {
                "error": {
                    "code": -32603,
                    "message": f"Internal error: {str(e)}"
                }
            }

    async def _server_info(self) -> Dict[str, Any]:
        """Return server information"""
        return {
            "result": {
                "name": self.name,
                "version": self.version,
                "description": "Customer Success FTE - Multi-channel AI support agent",
                "capabilities": {
                    "tools": True,
                    "resources": False,
                    "prompts": False
                }
            }
        }

    async def _list_tools(self) -> Dict[str, Any]:
        """List all available tools"""
        return {
            "result": {
                "tools": self.tools
            }
        }

    async def _call_tool(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a tool call

        Args:
            params: Tool call parameters

        Returns:
            Tool execution result
        """
        tool_name = params.get("name")
        arguments = params.get("arguments", {})

        # Map tool names to functions
        tool_map = {
            "search_knowledge_base": search_knowledge_base,
            "create_ticket": create_ticket,
            "get_customer_history": get_customer_history,
            "escalate_to_human": escalate_to_human,
            "send_response": send_response
        }

        if tool_name not in tool_map:
            return {
                "error": {
                    "code": -32602,
                    "message": f"Unknown tool: {tool_name}"
                }
            }

        try:
            # Execute the tool
            tool_func = tool_map[tool_name]
            result = await tool_func(**arguments)

            return {
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": result
                        }
                    ]
                }
            }

        except TypeError as e:
            return {
                "error": {
                    "code": -32602,
                    "message": f"Invalid parameters: {str(e)}"
                }
            }
        except Exception as e:
            return {
                "error": {
                    "code": -32603,
                    "message": f"Tool execution failed: {str(e)}"
                }
            }

    async def run_stdio(self):
        """Run MCP server using stdio transport"""
        print("MCP Server started (stdio mode)", file=sys.stderr)
        print(f"Server: {self.name} v{self.version}", file=sys.stderr)
        print("Waiting for requests...", file=sys.stderr)

        while True:
            try:
                # Read request from stdin
                line = sys.stdin.readline()
                if not line:
                    break

                request = json.loads(line)

                # Handle request
                response = await self.handle_request(request)

                # Write response to stdout
                print(json.dumps(response), flush=True)

            except json.JSONDecodeError as e:
                error_response = {
                    "error": {
                        "code": -32700,
                        "message": f"Parse error: {str(e)}"
                    }
                }
                print(json.dumps(error_response), flush=True)
            except Exception as e:
                print(f"Error: {e}", file=sys.stderr)
                break

    async def run_http(self, host: str = "0.0.0.0", port: int = 3000):
        """Run MCP server using HTTP transport (for testing)"""
        from aiohttp import web

        async def handle_mcp_request(request):
            """Handle HTTP POST request"""
            try:
                data = await request.json()
                response = await self.handle_request(data)
                return web.json_response(response)
            except Exception as e:
                return web.json_response({
                    "error": {
                        "code": -32603,
                        "message": str(e)
                    }
                }, status=500)

        app = web.Application()
        app.router.add_post('/mcp', handle_mcp_request)

        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, host, port)
        await site.start()

        print(f"MCP Server running on http://{host}:{port}/mcp", file=sys.stderr)
        print("Press Ctrl+C to stop", file=sys.stderr)

        # Keep running
        try:
            await asyncio.Event().wait()
        except KeyboardInterrupt:
            print("\nShutting down...", file=sys.stderr)
            await runner.cleanup()


async def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Customer Success FTE MCP Server")
    parser.add_argument(
        "--transport",
        choices=["stdio", "http"],
        default="stdio",
        help="Transport protocol (default: stdio)"
    )
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="HTTP host (default: 0.0.0.0)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=3000,
        help="HTTP port (default: 3000)"
    )

    args = parser.parse_args()

    server = MCPServer()

    if args.transport == "stdio":
        await server.run_stdio()
    else:
        await server.run_http(args.host, args.port)


if __name__ == "__main__":
    asyncio.run(main())

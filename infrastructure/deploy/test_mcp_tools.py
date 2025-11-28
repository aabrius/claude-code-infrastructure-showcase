#!/usr/bin/env python3
"""
Example script showing how to interact with the deployed GAM MCP Server.

This demonstrates the MCP protocol flow:
1. Initialize session
2. List available tools
3. Call a tool
"""

import requests
import json
import time

SERVICE_URL = "https://gam-mcp-server-183972668403.us-central1.run.app"


class MCPClient:
    def __init__(self, service_url):
        self.service_url = service_url
        self.session_id = None
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json,text/event-stream"
        }
    
    def parse_sse_response(self, response_text):
        """Parse Server-Sent Events response."""
        for line in response_text.strip().split('\n'):
            if line.startswith('data: '):
                return json.loads(line[6:])
        return None
    
    def initialize(self):
        """Initialize MCP session."""
        response = requests.post(
            f"{self.service_url}/mcp/v1/initialize",
            headers=self.headers,
            json={
                "jsonrpc": "2.0",
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {"tools": {}},
                    "clientInfo": {
                        "name": "gam-test-client",
                        "version": "1.0.0"
                    }
                },
                "id": 1
            }
        )
        
        if response.status_code == 200:
            self.session_id = response.headers.get('mcp-session-id')
            data = self.parse_sse_response(response.text)
            return data
        else:
            raise Exception(f"Failed to initialize: {response.status_code} - {response.text}")
    
    def list_tools(self):
        """List available tools."""
        headers = self.headers.copy()
        headers['mcp-session-id'] = self.session_id
        
        response = requests.post(
            f"{self.service_url}/mcp/tools/list",
            headers=headers,
            json={
                "jsonrpc": "2.0",
                "method": "tools/list",
                "params": {},
                "id": 2
            }
        )
        
        if response.status_code == 200:
            return self.parse_sse_response(response.text)
        else:
            raise Exception(f"Failed to list tools: {response.status_code} - {response.text}")
    
    def call_tool(self, tool_name, arguments):
        """Call a specific tool."""
        headers = self.headers.copy()
        headers['mcp-session-id'] = self.session_id
        
        response = requests.post(
            f"{self.service_url}/mcp/tools/call",
            headers=headers,
            json={
                "jsonrpc": "2.0",
                "method": "tools/call",
                "params": {
                    "name": tool_name,
                    "arguments": arguments
                },
                "id": 3
            }
        )
        
        if response.status_code == 200:
            return self.parse_sse_response(response.text)
        else:
            raise Exception(f"Failed to call tool: {response.status_code} - {response.text}")


def main():
    print("GAM MCP Server Test Client")
    print("=" * 60)
    
    # Create client
    client = MCPClient(SERVICE_URL)
    
    # Initialize session
    print("\n1. Initializing session...")
    init_result = client.initialize()
    print(f"Session ID: {client.session_id}")
    print(f"Server: {init_result['result']['serverInfo']['name']} v{init_result['result']['serverInfo']['version']}")
    
    # List tools
    print("\n2. Listing available tools...")
    try:
        tools_result = client.list_tools()
        print(f"Tools response: {json.dumps(tools_result, indent=2)}")
        
        if 'result' in tools_result and 'tools' in tools_result['result']:
            tools = tools_result['result']['tools']
            print(f"Found {len(tools)} tools:")
            for tool in tools:
                print(f"  - {tool['name']}: {tool['description'][:60]}...")
        else:
            print("Unexpected response format")
    except Exception as e:
        print(f"Error listing tools: {e}")
    
    # Call a tool
    print("\n3. Calling gam_quick_report tool...")
    tool_result = client.call_tool(
        "gam_quick_report",
        {
            "report_type": "delivery",
            "days_back": 7,
            "format": "summary"
        }
    )
    
    print("\nTool Result:")
    if 'result' in tool_result:
        result_data = tool_result['result']
        if isinstance(result_data, list) and len(result_data) > 0:
            content = result_data[0].get('content', [])
            if content and isinstance(content[0], dict):
                print(content[0].get('text', 'No text in response'))
        else:
            print(json.dumps(result_data, indent=2))
    else:
        print(json.dumps(tool_result, indent=2))


if __name__ == "__main__":
    main()
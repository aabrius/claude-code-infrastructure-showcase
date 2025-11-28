#!/usr/bin/env python3
"""
Example usage of Google Ad Manager API via MCP (Model Context Protocol).

This example demonstrates how to interact with the GAM API using MCP tools,
which is the recommended way for AI assistants to access the API.
"""

import asyncio
import json
import subprocess
import sys
from typing import Dict, Any


class MCPClient:
    """Simple MCP client for testing GAM tools."""
    
    def __init__(self, server_command: str):
        """
        Initialize MCP client.
        
        Args:
            server_command: Command to start the MCP server
        """
        self.server_command = server_command
        self.process = None
    
    async def start_server(self):
        """Start the MCP server process."""
        self.process = await asyncio.create_subprocess_exec(
            *self.server_command.split(),
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        print("MCP server started")
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Call a tool via MCP protocol.
        
        Args:
            tool_name: Name of the tool to call
            arguments: Tool arguments
            
        Returns:
            Tool response
        """
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments
            }
        }
        
        request_line = json.dumps(request) + "\n"
        self.process.stdin.write(request_line.encode())
        await self.process.stdin.drain()
        
        response_line = await self.process.stdout.readline()
        response = json.loads(response_line.decode())
        
        if "error" in response:
            raise Exception(f"Tool call failed: {response['error']}")
        
        return response["result"]
    
    async def stop_server(self):
        """Stop the MCP server process."""
        if self.process:
            self.process.terminate()
            await self.process.wait()
            print("MCP server stopped")


async def example_quick_reports():
    """Example: Generate quick reports using MCP."""
    print("\n=== Quick Reports Example ===")
    
    # Start MCP client
    client = MCPClient("python src/mcp/server.py")
    await client.start_server()
    
    try:
        # Get available quick report types
        print("1. Getting available quick report types...")
        response = await client.call_tool("gam_get_quick_report_types", {})
        print(f"Available types: {json.dumps(response, indent=2)}")
        
        # Generate a delivery report
        print("\n2. Generating delivery report...")
        response = await client.call_tool("gam_quick_report", {
            "report_type": "delivery",
            "days_back": 7,
            "format": "json"
        })
        print(f"Delivery report: {json.dumps(response, indent=2)}")
        
        # Generate an inventory report
        print("\n3. Generating inventory report...")
        response = await client.call_tool("gam_quick_report", {
            "report_type": "inventory",
            "days_back": 30,
            "format": "summary"
        })
        print(f"Inventory report: {response}")
        
    finally:
        await client.stop_server()


async def example_custom_reports():
    """Example: Create custom reports using MCP."""
    print("\n=== Custom Reports Example ===")
    
    client = MCPClient("python src/mcp/server.py")
    await client.start_server()
    
    try:
        # Get available dimensions and metrics
        print("1. Getting available dimensions and metrics...")
        response = await client.call_tool("gam_get_dimensions_metrics", {
            "report_type": "HISTORICAL",
            "category": "both"
        })
        print(f"Available options: {json.dumps(response, indent=2)}")
        
        # Create a custom report
        print("\n2. Creating custom performance report...")
        response = await client.call_tool("gam_create_report", {
            "name": "Custom Performance Analysis",
            "dimensions": ["DATE", "AD_UNIT_NAME", "DEVICE_CATEGORY_NAME"],
            "metrics": [
                "TOTAL_LINE_ITEM_LEVEL_IMPRESSIONS",
                "TOTAL_LINE_ITEM_LEVEL_CLICKS",
                "TOTAL_LINE_ITEM_LEVEL_CTR"
            ],
            "report_type": "HISTORICAL",
            "days_back": 14,
            "run_immediately": True,
            "format": "json"
        })
        print(f"Custom report: {json.dumps(response, indent=2)}")
        
    finally:
        await client.stop_server()


async def example_metadata_exploration():
    """Example: Explore available metadata using MCP."""
    print("\n=== Metadata Exploration Example ===")
    
    client = MCPClient("python src/mcp/server.py")
    await client.start_server()
    
    try:
        # Get common dimension-metric combinations
        print("1. Getting common combinations...")
        response = await client.call_tool("gam_get_common_combinations", {})
        combinations = json.loads(response["content"][0]["text"])
        
        print("Available analysis types:")
        for analysis_type, config in combinations["common_combinations"].items():
            print(f"  - {analysis_type}: {config['description']}")
            print(f"    Dimensions: {config['dimensions']}")
            print(f"    Metrics: {config['metrics'][:2]}...")  # Show first 2 metrics
        
        # Get dimensions by category
        print("\n2. Getting categorized dimensions...")
        response = await client.call_tool("gam_get_dimensions_metrics", {
            "category": "dimensions"
        })
        dims_response = json.loads(response["content"][0]["text"])
        
        if "by_category" in dims_response["dimensions"]:
            print("Dimension categories:")
            for category, dims in dims_response["dimensions"]["by_category"].items():
                print(f"  - {category}: {len(dims)} dimensions")
                if dims:
                    print(f"    Examples: {dims[:3]}")  # Show first 3
        
    finally:
        await client.stop_server()


async def example_report_management():
    """Example: List and manage reports using MCP."""
    print("\n=== Report Management Example ===")
    
    client = MCPClient("python src/mcp/server.py")
    await client.start_server()
    
    try:
        # List existing reports
        print("1. Listing existing reports...")
        response = await client.call_tool("gam_list_reports", {
            "limit": 10
        })
        reports_response = json.loads(response["content"][0]["text"])
        
        print(f"Found {reports_response['total_reports']} reports:")
        for report in reports_response["reports"][:5]:  # Show first 5
            print(f"  - {report['name']} (ID: {report['id']})")
            print(f"    Created: {report['created']}")
        
    finally:
        await client.stop_server()


def example_claude_desktop_config():
    """Example: Claude Desktop configuration for GAM MCP."""
    print("\n=== Claude Desktop Configuration ===")
    
    config = {
        "mcpServers": {
            "google-ad-manager": {
                "command": "python",
                "args": [
                    "/path/to/gam-api/src/mcp/server.py"
                ],
                "env": {
                    "GAM_CONFIG_PATH": "/path/to/gam-api/config/agent_config.yaml"
                }
            }
        }
    }
    
    print("Add this to your Claude Desktop config.json:")
    print(json.dumps(config, indent=2))
    
    config_path = "~/.config/claude-desktop/config.json"
    print(f"\nUsually located at: {config_path}")
    
    print("\nAfter adding the config:")
    print("1. Restart Claude Desktop")
    print("2. You can then use these tools in conversations:")
    print("   - gam_quick_report")
    print("   - gam_create_report")
    print("   - gam_list_reports")
    print("   - gam_get_dimensions_metrics")
    print("   - gam_get_common_combinations")
    print("   - gam_get_quick_report_types")


async def main():
    """Run all examples."""
    print("Google Ad Manager API - MCP Usage Examples")
    print("=" * 50)
    
    # Note: These examples require a running GAM API setup
    print("⚠️  These examples require:")
    print("1. Valid Google Ad Manager API credentials")
    print("2. Configured agent_config.yaml")
    print("3. MCP dependencies installed")
    print("\nTo run with real data, ensure your setup is complete first.")
    
    # Show Claude Desktop config (always works)
    example_claude_desktop_config()
    
    # Uncomment these to run with actual MCP server
    # await example_quick_reports()
    # await example_custom_reports()
    # await example_metadata_exploration()
    # await example_report_management()
    
    print("\n=== Example Usage Patterns ===")
    print("1. Quick Analysis:")
    print("   'Generate a delivery report for the last 7 days'")
    print("   -> Uses gam_quick_report tool")
    
    print("\n2. Custom Analysis:")
    print("   'Create a report showing impressions by device and geography'")
    print("   -> Uses gam_create_report with custom dimensions/metrics")
    
    print("\n3. Data Exploration:")
    print("   'What dimensions are available for geographic analysis?'")
    print("   -> Uses gam_get_dimensions_metrics tool")
    
    print("\n4. Report Discovery:")
    print("   'What reports already exist in the system?'")
    print("   -> Uses gam_list_reports tool")


if __name__ == "__main__":
    asyncio.run(main())
"""
Helper script to start the MCP server for the demo app.
"""

import subprocess
import sys
import os
import time
import requests


def check_port_available(port: int) -> bool:
    """Check if a port is available."""
    try:
        response = requests.get(f"http://localhost:{port}/health", timeout=1)
        return False  # Port is in use
    except:
        return True  # Port is available


def start_mcp_server(port: int = 9900):
    """Start the MCP server."""
    
    print("🚀 Starting MCP Server...")
    print(f"📍 Port: {port}")
    print(f"🔗 Endpoint: http://localhost:{port}/sse")
    print()
    
    # Check if port is already in use
    if not check_port_available(port):
        print(f"⚠️  Port {port} is already in use. MCP server may already be running.")
        response = input("Do you want to continue anyway? (y/n): ")
        if response.lower() != 'y':
            print("Exiting...")
            sys.exit(0)
    
    # Get environment variables from .env if it exists
    env = os.environ.copy()
    
    try:
        from dotenv import load_dotenv
        load_dotenv()
        env.update(os.environ)
    except ImportError:
        print("⚠️  python-dotenv not installed, using system environment")
    
    # Check for config file
    config_file = os.path.join(os.path.dirname(__file__), "mcp_server_config.yaml")
    use_config = os.path.exists(config_file)
    
    if use_config:
        print(f"📄 Using config file: {config_file}")
    
    # Start MCP server
    try:
        cmd = [
            sys.executable,
            "-m",
            "mcp_server_opensearch",
            "--transport",
            "stream",
            "--port",
            str(port)
        ]
        
        # Add config file if it exists
        if use_config:
            cmd.extend(["--config", config_file])
        
        process = subprocess.Popen(
            cmd,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        print(f"✅ MCP Server started (PID: {process.pid})")
        print()
        print("Waiting for server to be ready...")
        
        # Wait for server to be ready
        max_attempts = 30
        for i in range(max_attempts):
            try:
                response = requests.get(f"http://localhost:{port}/health", timeout=1)
                if response.status_code == 200:
                    print("✅ MCP Server is ready!")
                    print()
                    print("You can now start the Gradio app with:")
                    print("  python app.py")
                    print()
                    print("Press Ctrl+C to stop the MCP server")
                    print()
                    break
            except:
                time.sleep(1)
                print(f"  Attempt {i+1}/{max_attempts}...", end='\r')
        else:
            print("⚠️  Server started but health check failed")
            print("Check the server logs for errors")
        
        # Keep the process running
        try:
            process.wait()
        except KeyboardInterrupt:
            print("\n\n🛑 Stopping MCP Server...")
            process.terminate()
            process.wait()
            print("✅ MCP Server stopped")
            
    except FileNotFoundError:
        print("❌ MCP server package not found!")
        print()
        print("Please install it with:")
        print("  pip install opensearch-mcp-server-py")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error starting MCP server: {e}")
        sys.exit(1)


if __name__ == "__main__":
    port = int(os.environ.get("MCP_SERVER_PORT", 9900))
    start_mcp_server(port)

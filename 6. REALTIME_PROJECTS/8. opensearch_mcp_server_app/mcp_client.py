"""MCP Client wrapper for OpenSearch operations."""

import asyncio
from typing import Optional, Dict, Any, List
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.runnables import RunnablePassthrough
from config import get_settings


class MCPClient:
    """
    Wrapper for MCP client operations.
    Implements singleton pattern for efficient resource management.
    """
    
    _instance: Optional['MCPClient'] = None
    _initialized: bool = False
    
    def __new__(cls):
        """Ensure singleton instance."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize MCP client components."""
        if not self._initialized:
            self.settings = get_settings()
            self.client: Optional[MultiServerMCPClient] = None
            self.llm: Optional[ChatOpenAI] = None
            self.tools: Optional[List] = None
            self.agent = None
            self._initialized = True
    
    async def initialize(self) -> bool:
        """
        Initialize MCP client and connect to server.
        
        Returns:
            bool: True if initialization successful
        """
        try:
            # Initialize OpenAI LLM
            self.llm = ChatOpenAI(
                model=self.settings.openai_model,
                temperature=0,  # Deterministic responses
                api_key=self.settings.openai_api_key
            )
            
            # Initialize MCP client
            self.client = MultiServerMCPClient({
                "opensearch-mcp-server": {
                    "transport": "sse",
                    "url": self.settings.mcp_server_url,
                }
            })
            
            # Load tools from MCP server
            self.tools = await self.client.get_tools()
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to initialize MCP client: {e}")
            return False
    
    async def query(
        self, 
        question: str, 
        verbose: bool = False
    ) -> Dict[str, Any]:
        """
        Execute natural language query against OpenSearch.
        
        Args:
            question: Natural language query
            verbose: Show agent reasoning process
            
        Returns:
            Dict containing:
                - success: bool
                - result: str (answer)
                - error: Optional[str]
                - metadata: Dict with execution details
        """
        if not self.client or not self.llm or not self.tools:
            return {
                "success": False,
                "result": "",
                "error": "MCP client not initialized. Please initialize first.",
                "metadata": {}
            }
        
        try:
            # Bind tools to the LLM
            llm_with_tools = self.llm.bind_tools(self.tools)
            
            # Create system message
            system_message = (
                "You are a helpful AI assistant with access to OpenSearch tools. "
                "Use the available tools to answer questions about OpenSearch indices, "
                "documents, search queries, and cluster management. "
                "When you need to use a tool, make the function call and I will provide the results."
            )
            
            # Prepare messages
            messages = [
                {"role": "system", "content": system_message},
                {"role": "user", "content": question}
            ]
            
            tool_calls_made = []
            max_iterations = 10
            iteration = 0
            
            # Agent loop: invoke LLM, execute tools, repeat until answer
            while iteration < max_iterations:
                iteration += 1
                
                # Get LLM response
                response = await llm_with_tools.ainvoke(messages)
                
                # Check if LLM wants to use tools
                if hasattr(response, 'tool_calls') and response.tool_calls:
                    # Execute tool calls
                    for tool_call in response.tool_calls:
                        tool_name = tool_call.get('name')
                        tool_args = tool_call.get('args', {})
                        
                        if verbose:
                            print(f"\n🔧 Calling tool: {tool_name}")
                            print(f"   Args: {tool_args}")
                        
                        # Find and execute the tool
                        tool_result = None
                        for tool in self.tools:
                            if tool.name == tool_name:
                                try:
                                    tool_result = await tool.ainvoke(tool_args)
                                    tool_calls_made.append({
                                        "tool": tool_name,
                                        "args": tool_args,
                                        "result": str(tool_result)[:200]  # Truncate for metadata
                                    })
                                except Exception as e:
                                    tool_result = f"Error executing tool: {str(e)}"
                                break
                        
                        if tool_result is None:
                            tool_result = f"Tool {tool_name} not found"
                        
                        # Add tool result to messages
                        messages.append({
                            "role": "assistant",
                            "content": f"Using tool {tool_name}",
                            "tool_calls": [tool_call]
                        })
                        messages.append({
                            "role": "tool",
                            "content": str(tool_result),
                            "tool_call_id": tool_call.get('id', 'unknown')
                        })
                    
                    # Continue loop to let LLM process tool results
                    continue
                
                # No more tool calls - we have the final answer
                final_answer = response.content if hasattr(response, 'content') else str(response)
                
                return {
                    "success": True,
                    "result": final_answer,
                    "error": None,
                    "metadata": {
                        "tool_calls": tool_calls_made,
                        "iterations": iteration
                    }
                }
            
            # Max iterations reached
            return {
                "success": False,
                "result": "",
                "error": f"Max iterations ({max_iterations}) reached without completing the task",
                "metadata": {
                    "tool_calls": tool_calls_made,
                    "iterations": iteration
                }
            }
            
        except Exception as e:
            import traceback
            return {
                "success": False,
                "result": "",
                "error": f"{str(e)}\n{traceback.format_exc()}",
                "metadata": {}
            }
    
    def get_tools_info(self) -> List[Dict[str, Any]]:
        """
        Get information about available MCP tools.
        
        Returns:
            List of tool metadata dictionaries
        """
        if not self.tools:
            return []
        
        tools_info = []
        for tool in self.tools:
            tools_info.append({
                "name": tool.name,
                "description": tool.description,
                "category": self._categorize_tool(tool.name)
            })
        
        return tools_info
    
    def _categorize_tool(self, tool_name: str) -> str:
        """Categorize tool by name."""
        if "index" in tool_name.lower() and "document" not in tool_name.lower():
            return "Index Management"
        elif "document" in tool_name.lower() or "query" in tool_name.lower():
            return "Document Operations"
        elif "search" in tool_name.lower():
            return "Search & Query"
        elif "cluster" in tool_name.lower() or "health" in tool_name.lower():
            return "Cluster Management"
        elif "alias" in tool_name.lower():
            return "Alias Management"
        elif "stream" in tool_name.lower():
            return "Data Streams"
        else:
            return "Advanced"
    
    def get_tools_by_category(self) -> Dict[str, List[Dict[str, Any]]]:
        """Get tools organized by category."""
        tools_info = self.get_tools_info()
        categorized = {}
        
        for tool in tools_info:
            category = tool["category"]
            if category not in categorized:
                categorized[category] = []
            categorized[category].append(tool)
        
        return categorized
    
    async def close(self):
        """Clean up resources."""
        # MCP client cleanup if needed
        self.client = None
        self.llm = None
        self.tools = None


# Global client instance
_mcp_client: Optional[MCPClient] = None


async def get_mcp_client() -> MCPClient:
    """
    Get or create MCP client instance.
    
    Returns:
        Initialized MCPClient instance
    """
    global _mcp_client
    
    if _mcp_client is None:
        _mcp_client = MCPClient()
        success = await _mcp_client.initialize()
        if not success:
            raise RuntimeError("Failed to initialize MCP client")
    
    return _mcp_client


async def execute_query(question: str, verbose: bool = False) -> Dict[str, Any]:
    """
    Execute a natural language query.
    
    Args:
        question: Natural language query
        verbose: Show agent reasoning
        
    Returns:
        Query result dictionary
    """
    client = await get_mcp_client()
    return await client.query(question, verbose)

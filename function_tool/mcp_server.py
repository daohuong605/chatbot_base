from fastmcp import FastMCP

# Khởi tạo MCP server
mcp = FastMCP(name="My MCP Server")

# Đăng ký 1 tool
@mcp.tool()
def greet_user(name: str) -> str:
    return f"Hello {name}, chào mừng đến với MCP server!"

if __name__ == "__main__":
    import uvicorn
    # Chạy bằng uvicorn → expose HTTP JSON-RPC tại http://127.0.0.1:8000/mcp
    uvicorn.run(mcp.sse_app, host="127.0.0.1", port=8000)

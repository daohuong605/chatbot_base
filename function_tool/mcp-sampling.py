from mcp.server.fastmcp import Context,FastMCP
from mcp.types import SamplingMessage, TextContent

mcp = FastMCP(name="Sampling Example")

@mcp.tool()
async def generate_poem(topic: str, ctx: Context) -> str:
    """Generate a short poem about the topic using LLM sampling."""
    prompt = f"Write a short poem about {topic}."
    result = await ctx.session.create_message(
        messages=[
            SamplingMessage(
                role="user",
                content=TextContent(type="text",text=prompt),
            )
        ],
        max_tokens=100,
    )
    return result.content.text if result.content.type == "text" else str(result.content)

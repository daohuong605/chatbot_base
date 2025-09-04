from pydantic import BaseModel, Field
from mcp.server.fastmcp import Context, FastMCP

class AgeAskingSchema(BaseModel):
    age: int = Field(description="Enter your age", ge=0, le=120)

mcp = FastMCP(name="Server with Elicitation Example")

@mcp.tool(name="greet_user", description="Greet the user")
async def greet_user(name: str, ctx: Context) -> str:
    greeting_name = f"Hello, {name}!"

    asking_age_result = await ctx.elicit(
        message="How old are you?",
        schema=AgeAskingSchema,
    )
    if asking_age_result.action == "accept" and asking_age_result.data:
        if asking_age_result.data.age < 18:
            greeting_name += " You are a minor."
        else:
            greeting_name += " You are an adult."
    elif asking_age_result.action == "reject":
        greeting_name += "You choose not to provide your age."
    return greeting_name

if __name__ == "__main__":
    mcp.run(transport="streamable-http")

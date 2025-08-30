from langchain_google_genai import ChatGoogleGenerativeAI #wrapperLLM của Google GenAI
from langchain.tools import StructuredTool #bọc hàm  Python thành tool
from langchain.agents import create_openai_functions_agent, AgentExecutor #Khởi tạo agent theo kiểu function calling
from langchain.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from dotenv import load_dotenv
import os
import math

load_dotenv()
google_api_key = os.getenv("GOOGLE_API_KEY")

def evaluate_math_expression(expression: str, precision: int = None) -> float:
    allowed_names = {k: v for k, v in math.__dict__.items() if not k.startswith("__")}
    allowed_names.update({'abs': abs, 'round': round, 'pow': pow, 'min': min, 'max': max})
    try:
        result = eval(expression, {"__builtins__": {}}, allowed_names)
        if precision is not None:
            result = round(result, precision)
        return result
    except Exception as e:
        raise ValueError(f"Error evaluating expression: {e}")

class EvaluateMathExpressionInput(BaseModel):
    expression: str = Field(..., description="Biểu thức toán học. Ví dụ: '9.896 - 4.012 + (-13.23456908) - (-2**(-1.05))'")
    precision: int | None = Field(None, description="Số chữ số thập phân muốn làm tròn")

evaluate_math_expression_tool = StructuredTool.from_function(
    func=evaluate_math_expression,
    name="evaluate_math_expression",
    description="Evaluate a mathematical expression and return the result.",
    args_schema=EvaluateMathExpressionInput,
)

llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    temperature=0.0,
    top_k=1,
    max_output_tokens=1024,
    google_api_key=google_api_key
)

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "Bạn là trợ lý AI có thể dùng tool để giải toán chính xác."),
        ("human", "{input}"),
        ("ai", "{agent_scratchpad}"),
    ]
)

agent = create_openai_functions_agent(llm, [evaluate_math_expression_tool], prompt)
agent_executor = AgentExecutor(agent=agent, tools=[evaluate_math_expression_tool], verbose=True)

response = agent_executor.invoke({
    "input": "Hãy tính: 9.896 - 4.012 + (-13.23456908) - (-2**(-1.05)) và làm tròn 10 chữ số thập phân"
})

print("Kết quả:", response)

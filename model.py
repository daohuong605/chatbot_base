# models.py
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
import os
from dotenv import load_dotenv

load_dotenv()

# Lấy API key
google_api_key = os.getenv("GOOGLE_API_KEY")
deepseek_api_key = os.getenv("DEEPSEEK_API_KEY")
grok_api_key = os.getenv("GROK_API_KEY")

# Google Gemini
gemini_flash = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    temperature=0.7,
    google_api_key=google_api_key,
)

gemini_pro = ChatGoogleGenerativeAI(
    model="gemini-1.5-pro",
    temperature=0.7,
    google_api_key=google_api_key,
)

gemini_flash_lite = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash-lite",
    temperature=0.7,
    google_api_key=google_api_key,
)

# DeepSeek
deepseek_chat = ChatOpenAI(
    model="deepseek-v3.1",          
    temperature=0.7,
    api_key=deepseek_api_key,
    base_url="https://api.deepseek.com/v1",
)

deepseek_reasoner = ChatOpenAI(
    model="deepseek-v3.1",         
    temperature=0.7,
    api_key=deepseek_api_key,
    base_url="https://api.deepseek.com/v1",
)

# Grok (xAI)
grok_chat = ChatOpenAI(
    model="grok-2-latest",
    temperature=0.7,
    api_key=grok_api_key,
    base_url="https://api.x.ai/v1",
)

# Dictionary để chọn model theo tên
models = {
    "gemini-flash": gemini_flash,
    "gemini-flash-lite": gemini_flash_lite,
    # "gemini-pro": gemini_pro,
    "deepseek-chat": deepseek_chat,
    "deepseek-reasoner": deepseek_reasoner,
    "grok-2": grok_chat,
}

# # ✅ Test code
# if __name__ == "__main__":
#     print("Danh sách models khả dụng:", list(models.keys()))

#     try:
#         print("\n--- Test Gemini 2.5 Flash Lite ---")
#         res = models["gemini-flash-lite"].invoke("Xin chào, bạn có hoạt động không?")
#         print("Kết quả:", res.content if hasattr(res, "content") else res)
#     except Exception as e:
#         print("❌ Lỗi khi gọi gemini-2.5-flash-lite:", e)

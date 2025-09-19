# from model import models
# import json

# def elicitation_trigger(last_user_msg: str, provider="gemini-flash") -> list:
#     """
#     Sinh câu hỏi gợi ý dựa trên tin nhắn cuối cùng của user trong lịch sử.
#     """
#     llm = models.get(provider)
#     if not llm:
#         return []

#     prompt = f"""
# Bạn là chatbot tạo gợi ý trò chuyện. 
# Người dùng vừa nói: "{last_user_msg}"

# Hãy sinh ra 3 câu hỏi ngắn gọn, tự nhiên để tiếp tục cuộc trò chuyện. 

# Yêu cầu:
# - Viết bằng tiếng Việt, thân thiện.
# - Mỗi câu hỏi độc lập.
# - Xuất ra dưới dạng JSON list, ví dụ:
# ["Câu hỏi 1", "Câu hỏi 2", "Câu hỏi 3"]
# """

#     try:
#         result = llm.invoke(prompt)
#         content = result.content.strip()

#         if content.startswith("[") and content.endswith("]"):
#             questions = json.loads(content)
#         else:
#             # fallback: tách dòng nếu không phải JSON
#             lines = [l.strip("-• ") for l in content.split("\n") if l.strip()]
#             questions = [l for l in lines if len(l) > 5]

#         return questions[:3] if questions else [
#             f"Bạn có thể chia sẻ thêm về {last_user_msg} không?",
#             f"Tại sao bạn quan tâm đến {last_user_msg} vậy?"
#         ]
#     except Exception as e:
#         print("Elicitation error:", e)
#         return [
#             f"Bạn có thể chia sẻ thêm về {last_user_msg} không?",
#             f"Tại sao bạn quan tâm đến {last_user_msg} vậy?"
#         ]

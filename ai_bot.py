from flask import Flask, request, jsonify
from dotenv import load_dotenv
import os
#import json
#import re
from langchain_google_genai import ChatGoogleGenerativeAI


from data.import_data import insert_message
#from rag.game_rags import get_games_data
from data.get_history import get_latest_messages


# Load biến môi trường
load_dotenv()

app = Flask(__name__, static_folder="static", static_url_path="")

# Lấy API key từ .env
google_api_key = os.getenv("GOOGLE_API_KEY")
if not google_api_key:
    raise ValueError("GOOGLE_API_KEY chưa được cấu hình trong .env")

# Tạo model Google GenAI
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",  # hoặc gemini-pro
    temperature=0.7,
    google_api_key=google_api_key,
)

@app.route("/")
def index():
    return app.send_static_file("chatbot_ui.html")


@app.route("/chat", methods=["POST"])
def chat():
    data = request.json or {}
    user_msg = data.get("message", "").strip()

    if not user_msg:
        return jsonify({"error": "Message không được để trống"}), 400
    
    # Lấy 8 lịch sử  chat gần nhất
    history = get_latest_messages(8)

    # Format lịch sử thành đoạn hội thoại
    history_text = ""
    for item in reversed(history): # Đảo ngược để đúng thứ tự thời gian
        history_text += f"User: {item['message']}\nBot: {item['reply']}\n"

    # Tạo prompt mới có lịch sử chat
    prompt = (
        f"Lịch sử hội thoại: \n{history_text}\n"
        f"User: {user_msg}\n"
    )

    # Gọi model với prompt lấy lịch sử chat
    response = llm.invoke(prompt)
    bot_reply = response.content

    # Lưu vào Supabase
    insert_message(user_msg, bot_reply)

    return jsonify({"reply": bot_reply})


if __name__ == "__main__":
    app.run(debug=True)

from flask import Flask, request, jsonify
from dotenv import load_dotenv
import os
from langchain_google_genai import ChatGoogleGenerativeAI

from data.import_data import insert_message
from rag.game_rags import get_games_data


# Load biến môi trường
load_dotenv()

app = Flask(__name__, static_folder='static', static_url_path='')

# Lấy API key từ .env
google_api_key = os.getenv("GOOGLE_API_KEY")

# Tạo model Google GenAI
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",  # hoặc gemini-pro
    temperature=0.7,
    google_api_key=google_api_key
)

@app.route("/")
def index():
    return app.send_static_file('chatbot_ui.html')

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json or {}
    user_msg = data.get("message", "")

    # Tạo prompt RAG
    games_info = "\n".join([f"- {g.get('name', '')}: {g.get('description', '')}" for g in games_data])
    rag_prompt = (
        f"Dữ liệu game:\n{games_info}\n\n"
        f"Câu hỏi của người dùng: {user_msg}\n"
        f"Hãy trả lời dạng JSON với các trường: title, meta_description (NGẮN GỌN)), content."
    )

    # Gọi model Google GenAI với prompt RAG
    response = llm.invoke(rag_prompt)
    bot_reply = response.content

    # Chèn dữ liệu vào Supabase
    insert_message(user_msg, bot_reply)

    # Trả về JSON đúng định dạng
    try:
        reply_json = response.content if isinstance(response.content, dict) else None
        if not reply_json:
            import json
            reply_json = json.loads(bot_reply)
        return jsonify(reply_json)
    except Exception as e:
        print("Lỗi parse JSON:", e)
        return jsonify({"reply": bot_reply})

games_data = get_games_data()

if __name__ == "__main__":
    app.run(debug=True)
# Run the Flask app

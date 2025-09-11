from flask import Flask, request, Response, stream_with_context
from dotenv import load_dotenv
from model import models
from data.import_data import insert_message
from data.get_history import get_latest_messages

load_dotenv()
app = Flask(__name__, static_folder="static", static_url_path="")

@app.route("/")
def index():
    return app.send_static_file("chatbot_ui.html")

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json or {}
    user_msg = data.get("message", "").strip()
    provider = data.get("provider", "gemini-flash")

    if not user_msg:
        return Response("Message không được để trống", status=400)

    llm = models.get(provider)
    if not llm:
        return Response(f"Provider {provider} không hợp lệ", status=400)

    # ✅ Lấy 8 lịch sử chat gần nhất
    history = get_latest_messages(8)

    history_text = ""
    for item in reversed(history):
        history_text += f"User: {item['message']}\n{item['reply']}\n"

    # Prompt (không thêm "Bot:" ở trước)
    prompt = (
        f"Lịch sử hội thoại:\n{history_text}\n"
        f"User: {user_msg}\n"
    )

    # ✅ Streaming trả về dần dần
    @stream_with_context
    def generate():
        buffer = ""
        try:
            for chunk in llm.stream(prompt):
                if hasattr(chunk, "content") and chunk.content:
                    buffer += chunk.content
                    yield chunk.content
            # lưu sau khi xong
            insert_message(user_msg, buffer)
        except Exception as e:
            yield f"\n[ERROR]: {str(e)}"

    return Response(generate(), mimetype="text/plain")

if __name__ == "__main__":
    app.run(debug=True)

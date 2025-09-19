from flask import Flask, request, Response, stream_with_context, redirect, session, jsonify
from dotenv import load_dotenv
from model import models
from data.import_data import insert_message
from data.get_history import get_latest_messages, get_all_messages, get_long_term_context
# from utils.elicitation import elicitation_trigger
import os, json
from login.register import register_bp
from login.login import login_bp  

load_dotenv()
app = Flask(__name__, static_folder="static", static_url_path="")
app.secret_key = "super-secret-key"  # cần cho session

# đăng ký blueprint
app.register_blueprint(register_bp)
app.register_blueprint(login_bp)

@app.route("/")
def index():
    # nếu chưa login thì bắt về trang login
    if not session.get("user"):
        return redirect("/login-ui")
    return redirect("/chatbot")

@app.route("/chatbot")
def chatbot():
    if not session.get("user"):
        return redirect("/login-ui")
    return app.send_static_file("chatbot_ui.html")

@app.route("/register-ui")
def register_ui():
    return app.send_static_file("register.html")

@app.route("/login-ui")
def login_ui():
    return app.send_static_file("login.html")

@app.route("/history", methods=["POST"])
def history():
    if not session.get("user"):
        return jsonify([]), 401
    user_id = session["user"]["id"]
    history = get_all_messages(user_id)
    return jsonify(history)

# @app.route("/suggestions", methods=["POST"])
# def suggestions():
#     if not session.get("user"):
#         return jsonify([]), 401

#     user_id = session["user"]["id"]

#     # lấy lịch sử mới nhất (1 tin nhắn gần nhất)
#     history = get_latest_messages(user_id, 1)
#     if not history:
#         return jsonify([])

#     last_user_msg = history[-1]["message"]  # lấy message cuối cùng của user

#     from utils.elicitation import elicitation_trigger
#     suggested_questions = elicitation_trigger(last_user_msg)

#     return jsonify(suggested_questions)


# ===== Prompt Builder =====
def build_prompt(user_msg, short_term_context, long_term_context):
    system_prompt = """Bạn là chatbot hỗ trợ cá nhân hóa.
- Dùng short-term context để giữ mạch hội thoại gần nhất.
- Dùng long-term context để nhớ thông tin lâu dài của user.
- Nếu có mâu thuẫn thì ưu tiên short-term context.
"""

    context_prompt = f"""
[Long-term context]
{long_term_context if long_term_context else "Không có dữ liệu"}

[Short-term context]
{short_term_context if short_term_context else "Không có lịch sử gần đây"}
"""

    return f"{system_prompt}\n{context_prompt}\nUser: {user_msg}\nChatbot:"


# ===== Chat Endpoint =====
@app.route("/chat", methods=["POST"])
def chat():
    if not session.get("user"):
        return Response("Bạn chưa đăng nhập", status=401)

    data = request.json or {}
    user_msg = data.get("message", "").strip()
    provider = data.get("provider", "gemini-flash")

    if not user_msg:
        return Response("Message không được để trống", status=400)

    llm = models.get(provider)
    if not llm:
        return Response(f"Provider {provider} không hợp lệ", status=400)

    user = session.get("user")
    if not user:
        return Response("Bạn chưa đăng nhập", status=401)

    user_id = user["id"]

    # Short-term context: lấy từ lịch sử
    short_history = get_latest_messages(user_id, 8)
    short_term_context = "\n".join(
        [f"User: {h['message']}\nBot: {h['reply']}" for h in reversed(short_history)]
    )

    # Long-term context: lấy từ DB / vector DB
    long_term_context = get_long_term_context(user_id, user_msg)

    # Build prompt gọn gàng
    prompt = build_prompt(user_msg, short_term_context, long_term_context)

    # Streaming
    @stream_with_context
    def generate():
        buffer = ""
        try:
            for chunk in llm.stream(prompt):
                if hasattr(chunk, "content") and chunk.content:
                    buffer += chunk.content
                    yield chunk.content  # stream phần trả lời chính

            # Lưu message sau khi bot trả lời xong
            insert_message(user_id, user_msg, buffer)

            # Sau khi trả lời xong => sinh suggested_questions
            # suggested_questions = elicitation_trigger(short_term_context)

            # Gửi block suggestion đặc biệt để frontend parse
            # yield f"\n[SUGGESTIONS]: {json.dumps(suggested_questions, ensure_ascii=False)}"
        except Exception as e:
            yield f"\n[ERROR]: {str(e)}"

    return Response(generate(), mimetype="text/plain")


if __name__ == "__main__":
    app.run(debug=True)

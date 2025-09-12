from flask import Flask, request, Response, stream_with_context, redirect, session
from dotenv import load_dotenv
from model import models
from data.import_data import insert_message
from data.get_history import get_latest_messages
from login.register import register_bp
from login.login import login_bp  # cần viết file login.py tương tự register

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
        return redirect("/chatbot")
    return redirect("/login-ui")

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

    # history
    # history = get_latest_messages(8)
    user = session.get("user")
    if not user:
        return Response("Bạn chưa đăng nhập", status=401)

    user_id = user["id"]

    # history
    history = get_latest_messages(user_id, 8)

    history_text = ""
    for item in reversed(history):
        history_text += f"User: {item['message']}\n{item['reply']}\n"

    # Prompt 
    prompt = (
        f"Lịch sử hội thoại:\n{history_text}\n"
        f"User: {user_msg}\n"
    )

    # Streaming
    @stream_with_context
    def generate():
        buffer = ""
        try:
            for chunk in llm.stream(prompt):
                if hasattr(chunk, "content") and chunk.content:
                    buffer += chunk.content
                    yield chunk.content
            insert_message(user_id, user_msg, buffer)
        except Exception as e:
            yield f"\n[ERROR]: {str(e)}"

    return Response(generate(), mimetype="text/plain")

if __name__ == "__main__":
    app.run(debug=True)

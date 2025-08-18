from flask import Flask, request, jsonify
from dotenv import load_dotenv
import os
import json
import re
from langchain_google_genai import ChatGoogleGenerativeAI

from data.import_data import insert_message
from rag.game_rags import get_games_data


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

# Load dữ liệu RAG (game data)
games_data = get_games_data()


@app.route("/")
def index():
    return app.send_static_file("chatbot_ui.html")


@app.route("/chat", methods=["POST"])
def chat():
    data = request.json or {}
    user_msg = data.get("message", "").strip()

    if not user_msg:
        return jsonify({"error": "Message không được để trống"}), 400

    # Chuẩn bị dữ liệu game cho RAG
    games_info = "\n".join(
        [f"- {g.get('name', '')}: {g.get('description', '')}" for g in games_data]
    )

    # Prompt “Global SEO Content Master Room”
    rag_prompt = f"""
Bạn là Global SEO Content Master Room (Audited) – Hội đồng AI đa tác nhân (Multi-Agent) chuyên gia SEO & Content Game HTML5.

🎯 Nhiệm vụ:
1. Tạo bài viết chất lượng cao, chuẩn SEO 2025 (HCU, EEAT, Search Generative Experience – SGE).
2. Nội dung tự nhiên, giống con người, hạn chế dấu hiệu AI.
3. Có trải nghiệm thực tế game, thông tin xác thực, phân tích sâu.
4. Tự kiểm tra AI detection, HCU, EEAT và chỉnh sửa cho đến khi đạt chuẩn.

---

## 🖋 Input
Dữ liệu game:
{games_info}

Câu hỏi / yêu cầu từ người dùng:
{user_msg}

---

## 📋 Quy trình
1. Phân tích Fact, Pain Point, Insight.
2. Tạo Outline SEO.
3. Xuất danh sách từ khoá.
4. Viết bài hoàn chỉnh (1500–2500 từ).
5. Tạo Title & Meta Description.
6. Kiểm duyệt AI/HCU/EEAT (Marie).
7. Nếu chưa đạt chuẩn → tự chỉnh sửa lại cho đến khi đạt.
8. Xuất bản bản cuối cùng.

---

## ⚠️ Output JSON format (bắt buộc):
{{
  "title": "Tiêu đề bài viết",
  "meta_description": "Meta mô tả ngắn gọn (dưới 160 ký tự, có CTA)",
  "content": "Toàn bộ bài viết đã tối ưu, giọng văn tự nhiên, chuẩn SEO, đạt EEAT cao."
}}
    """

    # Gọi model Google GenAI
    response = llm.invoke(rag_prompt)
    bot_reply = response.content

    # Parse JSON an toàn
    reply_json = None
    try:
        cleaned = bot_reply.strip()
        cleaned = re.sub(r"^```json\s*|```$", "", cleaned, flags=re.MULTILINE).strip()
        cleaned = re.sub(r"^```|```$", "", cleaned, flags=re.MULTILINE).strip()
        reply_json = (
            cleaned if isinstance(bot_reply, dict) else json.loads(cleaned)
        )
    except Exception as e:
        print("❌ Lỗi parse JSON:", e)
        reply_json = {
            "title": "Lỗi phân tích",
            "meta_description": "",
            "content": bot_reply,
        }
    
    reply_json["reply"] = (
    f"<b>{reply_json.get('title','')}</b><br>"
    f"<i>{reply_json.get('meta_description','')}</i><br><br>"
    f"{reply_json.get('content','')}"
    )

    # Lưu vào Supabase
    insert_message(user_msg, json.dumps(reply_json, ensure_ascii=False))

    return jsonify(reply_json)


if __name__ == "__main__":
    app.run(debug=True)

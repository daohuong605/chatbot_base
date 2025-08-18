# 🤖 Chatbot Base

Dự án này là nền tảng chatbot cơ bản, hỗ trợ quản lý dữ liệu hội thoại, tích hợp RAG (Retrieval-Augmented Generation), và giao diện web tĩnh.  

---

## 📂 Cấu trúc thư mục

chatbot_base/
│── data/ # Lưu trữ dữ liệu hội thoại (history của chatbot)
│── rag/ # Các module liên quan đến RAG (tìm kiếm + sinh câu trả lời)
│── static/ # Static files (CSS, JS, images) phục vụ frontend
│── README.md # Tài liệu dự án
│── .gitignore # Bỏ qua file không cần push (vd: .env, venv, ...)

---

## ⚙️ Cài đặt
Tạo môi trường ảo (Python 3.10+):
python -m venv venv
source venv/bin/activate   # Mac/Linux
venv\Scripts\activate      # Windows

Cài đặt dependencies:
pip install -r requirements.txt

🔐 Environment Variables
env
OPENAI_API_KEY=your_api_key_here
DATABASE_URL=sqlite:///data/chatbot.db

🚀 Chạy chatbot


📝 Ghi chú
File .env đã được ignore, chỉ dùng local.

Nếu muốn chia sẻ cấu trúc .env, hãy cập nhật trong .env.example.

Thư mục data/ nên để trong .gitignore nếu chứa dữ liệu nhạy cảm.
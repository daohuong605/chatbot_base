from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Kiểm tra kết nối
if SUPABASE_URL and SUPABASE_KEY:
    try:
        response = supabase.table("ai_messages").select("*").limit(1).execute()
        print("Kết nối Supabase thành công!")
    except Exception as e:
        print("Kết nối Supabase thất bại:", e)
else:
    print("Thiếu SUPABASE_URL hoặc SUPABASE_KEY trong biến môi trường.")   

def insert_message(user_message, bot_reply):
    try:
        response = supabase.table("messages_test").insert({
            "message": user_message,
            "reply": bot_reply
        }).execute()
        print("Tin nhắn đã được chèn thành công:", response)
    except Exception as e:
        print("Lỗi khi chèn tin nhắn:", e)

if __name__ == "__main__":
    # Ví dụ chèn một tin nhắn
    insert_message("Xin chào!", "Chào bạn! Tôi là AI.")
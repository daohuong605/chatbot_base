from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def get_latest_messages(limit=10):
    """
    Lấy `limit` records lịch sử chat gần nhất từ bảng messages_test.
    Trả về list các dict, mỗi dict là một bản ghi.
    """
    try:
        response = (
            supabase.table("messages_test")
            .select("*")
            .order("created_at", desc=True)
            .limit(limit)
            .execute()
        )
        return response.data if hasattr(response, "data") else []
    except Exception as e:
        print("Lỗi khi lấy lịch sử chat:", e)
        return []  
    
if __name__ == "__main__":
   history = get_latest_messages(8)
   for record in history:
       print(record)
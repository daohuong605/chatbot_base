from supabase import create_client
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get Supabase URL and Key from environment variables
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def create_messages_test_table():
    sql = """
    CREATE TABLE IF NOT EXISTS messages_test (
        id SERIAL PRIMARY KEY,
        message TEXT NOT NULL,
        reply TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT NOW()
    );
    """
    
    try:
        response = supabase.rpc("execute_sql", {"sql": sql}).execute()
        print("Kết quả response:", response)  # Print the response for debugging
        print("Đã tạo bảng messages_test thành công (nếu có hàm execute_sql)!")
    except Exception as e:
        print("Không thể tạo bảng qua API. Hãy tạo bảng bằng SQL Editor trên Supabase web.\nLỗi:", e)

if __name__ == "__main__":
    create_messages_test_table() 
from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv() # Load environment variables

# Get Supabase URL and Key from environment variables
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Create a Supabase client
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Kiểm tra kết nối
if SUPABASE_URL and SUPABASE_KEY:
    try:
        # Thử truy vấn đơn giản
        response = supabase.table("ai_messages").select("*").limit(1).execute()
        print("Kết nối Supabase thành công!")
    except Exception as e:
        print("Kết nối Supabase thất bại:", e)
else:
    print("Thiếu SUPABASE_URL hoặc SUPABASE_KEY trong biến môi trường.")
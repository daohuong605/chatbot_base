from supabase import create_client
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def get_games_data():
    """
    Lấy toàn bộ dữ liệu từ bảng games trên Supabase.
    Trả về danh sách dict, mỗi dict là một bản ghi.
    """
    try:
        response = supabase.table("games").select("*").execute()
        if hasattr(response, "data"):
            return response.data
        else:
            return []
    except Exception as e:
        print("Lỗi khi lấy dữ liệu games:", e)
        return []

if __name__ == "__main__":
    games = get_games_data()
    print("Số lượng game:", len(games))
    for game in games:
        print(game)
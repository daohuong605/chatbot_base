import os
import pickle
from supabase import create_client
from dotenv import load_dotenv
from sklearn.feature_extraction.text import TfidfVectorizer

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

VECTORIZER_PATH = "data/vectorizer.pkl"

def train_vectorizer():
    # 1. Lấy toàn bộ messages từ DB
    res = supabase.table("messages_test").select("message").execute()
    records = res.data

    texts = [r["message"] for r in records if r.get("message")]
    if not texts:
        print("⚠️ Không có dữ liệu message nào trong DB để train.")
        return

    # 2. Train TF-IDF
    vectorizer = TfidfVectorizer(max_features=2000)
    vectorizer.fit(texts)

    # 3. Lưu vectorizer ra file pkl
    os.makedirs("data", exist_ok=True)
    with open(VECTORIZER_PATH, "wb") as f:
        pickle.dump(vectorizer, f)

    print(f"✅ Vectorizer đã được train trên {len(texts)} messages và lưu vào {VECTORIZER_PATH}")

if __name__ == "__main__":
    train_vectorizer()

from supabase import create_client
from dotenv import load_dotenv
from tqdm import tqdm
import os
import pickle

# ---------------- CONFIG ----------------
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
TABLE_NAME = "embeddings"
EMB_DIR = "data/embeddings"
# ---------------------------------------


def load_vector_files():
    """Lấy danh sách file .pkl"""
    return [f for f in os.listdir(EMB_DIR) if f.endswith(".pkl")]


def upload_embeddings(supabase):
    files = load_vector_files()
    if not files:
        print("Không có file embedding nào trong thư mục data/embeddings.")
        return

    for file in files:
        path = os.path.join(EMB_DIR, file)
        with open(path, "rb") as f:
            data = pickle.load(f)

        sheet_name = data.get("sheet_name", "unknown")
        embeddings_by_col = data.get("embeddings_by_col", {})
        rows = []

        # Duyệt từng cột embedding
        for col_name, col_data in embeddings_by_col.items():
            texts = col_data.get("texts", [])
            embs = col_data.get("embeddings", [])

            if len(texts) != len(embs):
                print(f"Số lượng text và embedding không khớp trong cột {col_name}")
                continue

            for text, emb in zip(texts, embs):
                # Nếu emb là numpy array, chuyển sang list
                if hasattr(emb, "tolist"):
                    emb = emb.tolist()
                rows.append({
                    "sheet_name": sheet_name,
                    "text": text,
                    "embedding": emb,
                    "metadata": {
                        "column": col_name,
                        "data_hash": data.get("data_hash"),
                        "updated_at": data.get("updated_at"),
                    }
                })

        print(f"\n📤 Upload {len(rows)} embeddings từ {file} ({len(embeddings_by_col)} cột)...")

        if not rows:
            print("File không có dữ liệu hợp lệ, bỏ qua.")
            continue

        # Upload theo batch 500 bản ghi/lần
        batch_size = 500
        for i in tqdm(range(0, len(rows), batch_size), desc=f"{sheet_name}"):
            chunk = rows[i:i + batch_size]
            supabase.table(TABLE_NAME).insert(chunk).execute()

        print(f"Hoàn tất upload {file} ({len(rows)} bản ghi)\n")


def main():
    print("Kết nối Supabase...")
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    print("Kết nối thành công!\n")
    upload_embeddings(supabase)


if __name__ == "__main__":
    main()
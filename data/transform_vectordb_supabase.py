from supabase import create_client
from dotenv import load_dotenv
from tqdm import tqdm
import os
import pickle
from datetime import datetime

load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
TABLE_NAME = "embeddings"
EMB_DIR = "data/embeddings"

def load_vector_files():
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
        df = data.get("df")
        data_hash = data.get("data_hash", "")
        updated_at = data.get("updated_at", datetime.now().isoformat())

        rows = []

        # Duyệt từng cột embedding
        for col_name, col_data in embeddings_by_col.items():
            if isinstance(col_data, dict):
                texts = col_data.get("texts", [])
                embs = col_data.get("embeddings", [])
            else:
                embs = col_data
                texts = df[col_name].astype(str).tolist() if df is not None and col_name in df.columns else []

            if len(texts) != len(embs):
                print(f"Số lượng text và embedding không khớp trong cột {col_name}")
                continue

            for idx, (text, emb) in enumerate(zip(texts, embs)):
                if hasattr(emb, "tolist"):
                    emb = emb.tolist()

                metadata = {}
                level = None
                if df is not None and idx < len(df):
                    metadata = df.iloc[idx].to_dict()
                    level = metadata.get("Mức")

                row = {
                    "sheet_name": sheet_name,
                    "column_name": col_name,
                    "row_index": idx,
                    "text": text,
                    "embedding": emb,
                    "data_hash": data_hash,
                    "updated_at": updated_at,
                    "level": level, 
                }

                rows.append(row)

        print(f"\nUpload {len(rows)} embeddings từ {file} ({len(embeddings_by_col)} cột)...")

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
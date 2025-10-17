import os
import json
import hashlib
import pickle
from datetime import datetime
import time

import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from sentence_transformers import SentenceTransformer

from dotenv import load_dotenv

load_dotenv()

SPREADSHEET_ID = os.getenv("GOOGLE_SHEET_ID")
META_DIR = "data/metadata"
EMD_DIR = "data/embeddings"
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

def get_gspread_client():
    service_account_inf = {
        "type": os.getenv("GOOGLE_TYPE"),
        "project_id": os.getenv("GOOGLE_PROJECT_ID"),
        "private_key": os.getenv("GOOGLE_PRIVATE_KEY").replace("\\n", "\n"),
        "client_email": os.getenv("GOOGLE_CLIENT_EMAIL"),
        "client_id": os.getenv("GOOGLE_CLIENT_ID"),
        "auth_uri": os.getenv("GOOGLE_AUTH_URI"),
        "token_uri": os.getenv("GOOGLE_TOKEN_URI"),
        "auth_provider_x509_cert_url": os.getenv("GOOGLE_AUTH_PROVIDER_x509_CERT_URL"),
        "client_x509_cert_url": os.getenv("GOOGLE_CLIENT_x509_CERT_URL"),
        "universe_domain": os.getenv("GOOGLE_UNIVERSE_DOMAIN")
    }
    scopes = ["https://www.googleapis.com/auth/spreadsheets.readonly"]
    creds = Credentials.from_service_account_info(service_account_inf, scopes=scopes)
    return gspread.authorize(creds)


def hash_dataframe(df: pd.DataFrame) -> str:
    return hashlib.md5(pd.util.hash_pandas_object(df, index=True).values).hexdigest()


def load_metadata_files(meta_dir: str):
    return [
        os.path.join(meta_dir, f)
        for f in os.listdir(meta_dir)
        if f.endswith(".json")
    ]

def load_google_sheet(client, sheet_id: str, sheet_name: str) -> pd.DataFrame:
    worksheet = client.open_by_key(sheet_id).worksheet(sheet_name)
    return pd.DataFrame(worksheet.get_all_records())

def save_embeddings(sheet_name, df, embeddings_by_col, data_hash):
    """
    Lưu file .pkl theo cấu trúc:
        - sheet_name
        - df (bao gồm cột gốc + cột embedding riêng)
        - updated_at
        - data_hash
        - embeddings_by_col (dict chứa vectors)
    """
    save_path = f"{EMD_DIR}/{sheet_name}.pkl"

    for col, emb in embeddings_by_col.items():
        df[f"{col}_embedding"] = emb.tolist()

    data = {
        "sheet_name": sheet_name,
        "df": df,
        "embeddings_by_col": embeddings_by_col,
        "updated_at": datetime.now().isoformat(),
        "data_hash": data_hash,
    }

    os.makedirs(EMD_DIR, exist_ok=True)
    with open(save_path, "wb") as f:
        pickle.dump(data, f)

    print(f"Đã lưu embedding tách cột: {save_path}")


def update_metadata(meta_path: str, data_hash: str):
    """Cập nhật hash và thời gian vào metadata."""
    meta = json.load(open(meta_path, "r"))

    if isinstance(meta, list):
        for m in meta:
            m["data_hash"] = data_hash
            m["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    elif isinstance(meta, dict):
        meta["data_hash"] = data_hash
        meta["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    json.dump(meta, open(meta_path, "w"), indent=2, ensure_ascii=False)

def process_sheet(meta_path: str, client, model):
    metas = json.load(open(meta_path, "r"))
    if isinstance(metas, dict):
        metas = [metas]

    for meta in metas:
        sheet_name = meta["sheet_name"].strip()
        columns = meta.get("column", [])
        print(f"\nĐang xử lý sheet: {sheet_name}")

        try:
            df = load_google_sheet(client, SPREADSHEET_ID, sheet_name)
            time.sleep(2)
        except gspread.exceptions.WorksheetNotFound:
            print(f"Không tìm thấy sheet '{sheet_name}', bỏ qua.")
            continue

        embed_cols = [c for c in columns if c in df.columns and c != "Mức"]
        if not embed_cols:
            print(f"Sheet '{sheet_name}' không có cột hợp lệ để embed.")
            continue

        new_hash = hash_dataframe(df)
        if new_hash == meta.get("data_hash"):
            print(f"{sheet_name}: Dữ liệu không đổi, bỏ qua embedding.")
            continue

        embeddings_by_col = {}
        for col in embed_cols:
            texts = df[col].astype(str).tolist()
            texts = [t if t.strip() != "" else "" for t in texts]
            print(f"Tạo embeddings cho cột '{col}' ({len(texts)} dòng)...")
            embeddings = model.encode(texts, show_progress_bar=True, convert_to_numpy=True)
            embeddings_by_col[col] = embeddings

        save_embeddings(sheet_name, df, embeddings_by_col, new_hash)
        update_metadata(meta_path, new_hash)
        print(f"Hoàn tất: {sheet_name}")


def main():
    print("Bắt đầu embedding pipeline...")
    client = get_gspread_client()
    model = SentenceTransformer(MODEL_NAME)

    meta_files = load_metadata_files(META_DIR)
    if not meta_files:
        print("Không tìm thấy file metadata nào.")
        return

    for meta_path in meta_files:
        process_sheet(meta_path, client, model)

    print("\nHoàn thành toàn bộ embedding pipeline!")


if __name__ == "__main__":
    main()

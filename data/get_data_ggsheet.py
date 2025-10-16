import os, json
import pandas as pd
import requests
from google.oauth2.service_account import Credentials
from dotenv import load_dotenv
import gspread
import time
import hashlib

load_dotenv()

service_account_inf = {
    "type": os.getenv("GOOGLE_TYPE"),
    "project_id": os.getenv("GOOGLE_PROJECT_ID"),
    "private_key": os.getenv("GOOGLE_PRIVATE_KEY"),
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
client = gspread.authorize(creds)


SHEET_ID = os.getenv("GOOGLE_SHEET_ID")
OUTPUT_JSON = "data/metadata/metadata.json"

spreadsheet = client.open_by_key(SHEET_ID)
sheet_list = spreadsheet.worksheets()

print(f"{spreadsheet.title}")
print(f"{len(sheet_list)}")


#Tạo metadata cho dữ liệu
def calc_hash(df: pd.DataFrame) -> str:
    if df.empty:
        return "Dữ liệu rỗng"
    return hashlib.md5(pd.util.hash_pandas_object(df, index=True).values).hexdigest()

def metadata_changed(old, new):
    old_map = {m["sheet_name"]: m for m in old}
    for n in new:
        s = n["sheet_name"]
        if s not in old_map or n["data_hash"] != old_map[s].get("data_hash"):
            return True
    return False

try:
    with open (OUTPUT_JSON, "r", encoding="utf-8") as f:
        old_metadata = json.load(f)
except FileNotFoundError:
    old_metadata= []

timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
new_metadata = []

for ws in sheet_list:
    name = ws.title
    values = ws.get_all_values()
    if not values:
        continue
    df = pd.DataFrame(values[1:], columns=values[0])
    meta = {
        "sheet_name": name,
        "num_rows": len(df),
        "num_columns": len(df.columns),
        "column": list(df.columns),
        "data_hash": calc_hash(df),
        "updated_at": timestamp
    }
    new_metadata.append(meta)
    print(f"Đã đọc sheet {name}, {len(df)} dòng")

if metadata_changed(old_metadata, new_metadata):
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(new_metadata, f, ensure_ascii=False, indent=2)
    print(f"Metadata đã được cập nhật: {OUTPUT_JSON}")
else:
    print("Không có thay đổi – giữ nguyên metadata.json")

print("Kết thúc.")
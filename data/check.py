import pickle

with open("data/embeddings/TC hành vi - Câu nói hay dùng.pkl", "rb") as f:
    data = pickle.load(f)

print("🔑 Các khóa trong file:", list(data.keys()))

for key, value in data.items():
    if isinstance(value, list):
        print(f"{key}: list[{len(value)}]")
    elif isinstance(value, dict):
        print(f"{key}: dict[{len(value)}]")
    else:
        print(f"{key}: {type(value)}")

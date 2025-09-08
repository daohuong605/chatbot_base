def hello():
    return "Xin chào!"
print (hello())

"""
Dùng def khi:
    - Hàm chạy tuần tự không chờ đợi gì
    - Không cần gọi API, không đọc file lớn bất đồng bộ, không kết nối mạng
    - Ví dụ: Tính toán toán học, ử lý dữ liệu trong RAM, đọc biến từ dictionary 
"""

def caculation(a, b):
    return a + b
print (caculation(5, 6))
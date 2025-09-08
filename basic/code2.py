import asyncio

async def hello():
    return "Xin chào async"

async def fetch_data():
    print("Bắt đầu lấy dữ liệu ...")
    await asyncio.sleep(2)
    return "Dữ liệu xong!"

async def main():
    msg = await hello() #await to run
    print(msg)

    result = await fetch_data()
    print(result)

asyncio.run(main())

"""
Dùng async def khi:
    - Hàm có thể chờ một lúc do tác vụ I/O (network, file, database, sleep...)
    - Muốn chương trình không bị chặn (non-blocking) trong lúc chờ
    - Ví dụ: Gọi API, đọc file ghi bất đồng bộ, kết nối databse, xử lý nhiều socket
"""



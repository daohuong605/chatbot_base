import asyncio
import json
from mcp.client.session import ClientSession
from mcp.client.stdio import stdio_client
from mcp import StdioServerParameters

async def chatbot():
    # Tạo server parameters đúng cách
    server_params = StdioServerParameters(
        command="python",
        args=["/Users/huong/Desktop/Chatbot_base/mcp_server/library_management.py"]
    )
    
    async with stdio_client(server_params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()

            print("🤖 Chatbot MCP Client started. Type 'exit' to quit.")

            while True:
                user_input = input("You: ")
                if user_input.lower() in ["exit", "quit"]:
                    break

                try:
                    # Ví dụ: gọi tool add_book nếu người dùng nhập dạng đặc biệt
                    if user_input.startswith("add:"):
                        # format: add:Title|Author|ISBN|tag1,tag2
                        title, author, isbn, tags = user_input[4:].split("|")
                        tags = [t.strip() for t in tags.split(",")]
                        result = await session.call_tool(
                            name="add_book",
                            arguments={
                                "title": title,
                                "author": author,
                                "isbn": isbn,
                                "tags": tags,
                            },
                        )

                    elif user_input.startswith("list"):
                        result = await session.call_tool(name="get_all_books", arguments={})

                    elif user_input.startswith("count"):
                        result = await session.call_tool(name="get_num_books", arguments={})

                    elif user_input.startswith("isbn:"):
                        isbn = user_input[5:].strip()
                        result = await session.call_tool(
                            name="get_book_by_isbn",
                            arguments={"isbn": isbn},
                        )

                    elif user_input.startswith("remove:"):
                        isbn = user_input[7:].strip()
                        result = await session.call_tool(
                            name="remove_book",
                            arguments={"isbn": isbn},
                        )

                    else:
                        # fallback: chỉ gọi tool gợi ý sách ngẫu nhiên
                        result = await session.call_tool(
                            name="get_suggesting_random_book_prompt",
                            arguments={},
                        )

                    # In kết quả
                    if not result:
                        print("Bot: (no response)")
                    else:
                        # Xử lý kết quả trả về từ MCP
                        if hasattr(result, 'content'):
                            for content in result.content:
                                if hasattr(content, 'text'):
                                    print("Bot:", content.text)
                                else:
                                    print("Bot:", str(content))
                        else:
                            # Fallback cho format cũ
                            for item in result:
                                if hasattr(item, "text"):
                                    print("Bot:", item.text)
                                else:
                                    print("Bot:", json.dumps(item, indent=2, ensure_ascii=False))
                                
                except Exception as e:
                    print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(chatbot())
from dotenv import load_dotenv
import os
from openai import OpenAI
from agent import NewsAgent
from database import NewsDB
import uvicorn
from scheduler import start_scheduler  


load_dotenv()


NEWSAPI_KEY = os.getenv("NEWSAPI_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not NEWSAPI_KEY:
    raise ValueError("Không tìm thấy NEWSAPI_KEY trong file .env")
if not OPENAI_API_KEY:
    raise ValueError("Không tìm thấy OPENAI_API_KEY trong file .env")

print("=== Đã đọc thành công API keys ===")
print(f"NEWSAPI_KEY (ẩn): {NEWSAPI_KEY[:6]}...{NEWSAPI_KEY[-4:]}")
print(f"OPENAI_API_KEY (ẩn): {OPENAI_API_KEY[:6]}...{OPENAI_API_KEY[-4:]}")


llm_client = OpenAI(api_key=OPENAI_API_KEY)


db = NewsDB()
agent = NewsAgent(
    news_api_key=NEWSAPI_KEY,
    llm_client=llm_client,
    db=db
)


if __name__ == "__main__":
    print("\n=== News Agent - Hùng đang khởi động ===\n")

    # Option 1: Test ngay lập tức agent (chạy 1 lần tổng hợp tin tức để kiểm tra)
    print("=== Test thủ công agent ngay bây giờ ===")
    try:
        summary = agent.run(topic="AI machine learning")
        print("\nKẾT QUẢ TÓM TẮT MẪU (công nghệ AI/ML):\n")
        print(summary)
        print("\n" + "="*60 + "\n")
    except Exception as e:
        print(f"Lỗi khi test agent: {e}")

    # Option 2: Khởi động scheduler (chạy tự động 8:00 sáng hàng ngày)
    print("=== Khởi động Scheduler (8:00 AM hàng ngày) ===")
    try:
        scheduler = start_scheduler(
            news_api_key=NEWSAPI_KEY,
            openai_api_key=OPENAI_API_KEY,
            topic="AI machine learning"
        )
        print("Scheduler đã chạy ngầm - sẽ tự động tổng hợp tin lúc 8:00 sáng")
    except Exception as e:
        print(f"Lỗi khởi động scheduler: {e}")

    # Option 3: Chạy backend FastAPI (để xem qua trình duyệt)
    print("\n=== Khởi động Backend FastAPI ===")
    print("→ Mở trình duyệt: http://localhost:8000/static/index.html")
    print("→ API endpoint ví dụ: http://localhost:8000/get_news/AI%20machine%20learning")
    
    uvicorn.run("backend:app", host="0.0.0.0", port=8000, reload=True)
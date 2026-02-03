from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import sqlite3

app = FastAPI()

app.mount("/static", StaticFiles(directory="frontend"), name="static")

@app.get("/")
def read_root():
    return {"message": "Welcome to News Agent"}

@app.get("/get_news/{topic}")
def get_news(topic: str):
    conn = sqlite3.connect("news.db")
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            "SELECT summary FROM summaries WHERE topic=? ORDER BY date DESC LIMIT 1",
            (topic,)
        )
        result = cursor.fetchone()
        summary = result[0] if result else "Chưa có bản tin nào cho topic này. Hãy chạy test thủ công hoặc chờ scheduler 8h sáng."
    except Exception as e:
        summary = f"Lỗi khi lấy dữ liệu từ DB: {str(e)}"
    finally:
        conn.close()

    return {"topic": topic, "summary": summary}
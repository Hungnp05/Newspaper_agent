from apscheduler.schedulers.background import BackgroundScheduler
from agent import NewsAgent
from database import NewsDB

def daily_task(agent, topic):
    print("Running daily news aggregation...")
    try:
        summary = agent.run(topic)
        print(f"Hoàn thành tổng hợp tin tức cho topic '{topic}':\n{summary[:200]}...") 
    except Exception as e:
        print(f"Lỗi khi chạy daily_task: {e}")

def start_scheduler(news_api_key, openai_api_key, topic="AI machine learning"):
    db = NewsDB()
    
    from openai import OpenAI
    llm_client = OpenAI(api_key=openai_api_key)
    
    agent = NewsAgent(
        news_api_key=news_api_key,
        llm_client=llm_client,
        db=db
    )
    
    scheduler = BackgroundScheduler()
    scheduler.add_job(
        daily_task,
        'cron',
        hour=9,
        minute=0,
        args=(agent, topic)
    )
    
    scheduler.start()
    print(f"Scheduler đã khởi động - sẽ chạy lúc 9:00 AM hàng ngày cho topic: {topic}")
    
    return scheduler
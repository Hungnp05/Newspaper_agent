import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from openai import OpenAI 

class NewsAgent:
    def __init__(self, news_api_key, llm_client, db=None):
        self.news_api_key = news_api_key
        self.llm_client = llm_client
        self.db = db

    def fetch_news(self, topic="AI machine learning", num_articles=10):
        advanced_query = (
            '("artificial intelligence" OR "machine learning" OR "deep learning" OR AI OR "neural network" OR LLM)'
            ' AND (technology OR tech OR computing OR software OR "data science")'
            ' -crypto -bitcoin -nft -blockchain'
        )

        from_date = (datetime.utcnow() - timedelta(days=7)).strftime("%Y-%m-%d")

        tech_domains = (
            "techcrunch.com,theverge.com,engadget.com,wired.com,arstechnica.com,"
            "mit.edu,zdnet.com,venturebeat.com,thenextweb.com,informationweek.com"
        )

        url = (
            "https://newsapi.org/v2/everything?"
            f"q={requests.utils.quote(advanced_query)}&" 
            f"domains={tech_domains}&"
            f"from={from_date}&"
            f"language=en&"              
            f"sortBy=publishedAt&"       
            f"pageSize={num_articles}&"
            f"apiKey={self.news_api_key}"
        )

        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()

            data = response.json()
            if data.get('status') != 'ok':
                raise Exception(f"NewsAPI error: {data.get('message')}")

            articles = data.get('articles', [])
            news_list = []
            for article in articles:
                title = article.get('title', '').strip()
                desc = article.get('description', '').strip()
                if title or desc:
                    text = f"{title}\n{desc}".strip()
                    news_list.append(text)

            if news_list:
                print(f"Tìm thấy {len(news_list)} bài viết công nghệ/AI.")
                return news_list
            else:
                print("Không có bài viết nào khớp query → thử fallback.")
                return self.scrape_google_news(topic)

        except Exception as e:
            print(f"NewsAPI lỗi: {e}. Chuyển sang scrape Google News...")
            return self.scrape_google_news(topic)

    def scrape_google_news(self, topic):
        query = f"{topic} AI OR \"machine learning\" OR \"deep learning\" OR technology after:{(datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d')}"
        url = f"https://news.google.com/search?q={requests.utils.quote(query)}&hl=en-US&gl=US&ceid=US:en"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                          '(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }

        try:
            response = requests.get(url, headers=headers, timeout=15)
            soup = BeautifulSoup(response.text, 'html.parser')

            items = soup.find_all(['h3', 'div'], attrs={'role': 'heading'})  
            headlines = [item.get_text(strip=True) for item in items if item.get_text(strip=True)]
            return headlines[:8] 
        except Exception as e:
            print(f"Scrape Google News lỗi: {e}")
            return []

    def summarize_news(self, articles):
        if not articles:
            return "Hiện tại chưa có tin tức công nghệ/AI/ML mới đáng chú ý."

        prompt = (
            "Bạn là chuyên gia tổng hợp tin tức công nghệ. Dưới đây là các bài báo mới nhất về AI, "
            "machine learning, deep learning và công nghệ liên quan. Hãy tóm tắt thành bản tin ngắn gọn "
            "bằng tiếng Việt, chuyên nghiệp, dễ đọc, tập trung vào điểm chính, tiến bộ mới, ứng dụng thực tế. "
            "Sắp xếp theo mức độ quan trọng. Độ dài khoảng 250-400 từ. Không thêm thông tin ngoài dữ liệu cung cấp.\n\n"
            + "\n\n".join(articles)
        )

        try:
            response = self.llm_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.6,
                max_tokens=700,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"Lỗi khi tổng hợp: {str(e)}"

    def run(self, topic="Công nghệ AI Machine Learning"):
        articles = self.fetch_news(topic, num_articles=12)
        summary = self.summarize_news(articles)
        
        if self.db:
            self.db.save_summary(topic, summary)
        
        print(f"Bản tin công nghệ hôm nay:\n{summary}")
        return summary
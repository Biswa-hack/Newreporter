import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# --- CONFIGURATION ---
NEWS_API_KEY = "4dbece8fc9244f2981f44f59c44e87a1"
AI_API_KEY = "AIzaSyDL9zu9E6GDyR3_bvlEaktqLSpqNVWQOmk"
SENDER_EMAIL = "magpetacc@gmail.com"
SENDER_PASSWORD = "xalsuqzdracupuii"
" # Use App Passwords, not your real password

def get_news(category):
    url = f"https://newsapi.org/v2/top-headlines?category={category}&apiKey={NEWS_API_KEY}"
    response = requests.get(url).json()
    return response['articles'][:3]  # Get top 3 articles per category

def analyze_impact(article_text):
    # This is a placeholder for your LLM call (OpenAI/Gemini)
    # The prompt would be: "Analyze this news. Provide: 1. Impact 2. Pros 3. Cons"
    return f"IMPACT: High market volatility. \nPROS: Growth in tech. \nCONS: Trade tensions."

def send_email(recipient, content):
    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = recipient
    msg['Subject'] = "Daily Intelligence Briefing"
    
    msg.attach(MIMEText(content, 'plain'))
    
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.send_message(msg)

if __name__ == "__main__":
    # 1. Read your "prescribed" email list
    with open("recipients.txt", "r") as f:
        email_list = [line.strip() for line in f.readlines()]
    
    # 2. Compile report
    full_report = "TODAY'S INTELLIGENCE BRIEFING\n\n"
    categories = ['business', 'politics', 'technology']
    
    for cat in categories:
        articles = get_news(cat)
        for art in articles:
            analysis = analyze_impact(art['description'])
            full_report += f"TITLE: {art['title']}\n{analysis}\n{'-'*20}\n"
    
    # 3. Send to everyone on your list
    for email in email_list:
        send_email(email, full_report)

import os
import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# --- CONFIGURATION (Reading from GitHub Secrets) ---
NEWS_API_KEY = os.getenv("NEWS_API_KEY")
AI_API_KEY = os.getenv("GEMINI_API_KEY")
SENDER_EMAIL = os.getenv("EMAIL_USER")
SENDER_PASSWORD = os.getenv("EMAIL_PASS")

def get_news(category):
    url = f"https://newsapi.org/v2/top-headlines?category={category}&apiKey={NEWS_API_KEY}"
    response = requests.get(url).json()
    # Adding a check to prevent errors if the API fails
    return response.get('articles', [])[:3]

def analyze_impact(article_text):
    # This is currently a placeholder. 
    # To use the real AI, you would add the Gemini logic here.
    return f"IMPACT: High market volatility. \nPROS: Growth in tech. \nCONS: Trade tensions."

def send_email(recipient, content):
    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = recipient
    msg['Subject'] = "Daily Intelligence Briefing"
    
    msg.attach(MIMEText(content, 'plain'))
    
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(msg)
    except Exception as e:
        print(f"Failed to send to {recipient}: {e}")

if __name__ == "__main__":
    # 1. Read your "prescribed" email list
    if not os.path.exists("recipients.txt"):
        print("Error: recipients.txt file not found!")
    else:
        with open("recipients.txt", "r") as f:
            email_list = [line.strip() for line in f.readlines() if line.strip()]
        
        # 2. Compile report
        full_report = "TODAY'S INTELLIGENCE BRIEFING\n\n"
        categories = ['business', 'politics', 'technology']
        
        for cat in categories:
            articles = get_news(cat)
            for art in articles:
                desc = art.get('description', 'No description available')
                analysis = analyze_impact(desc)
                full_report += f"TITLE: {art.get('title')}\n{analysis}\n{'-'*20}\n"
        
        # 3. Send to everyone on your list
        for email in email_list:
            send_email(email, full_report)
            print(f"Email sent to {email}")

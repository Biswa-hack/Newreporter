import os
import requests
import google.generativeai as genai
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

# --- CONFIG ---
NEWS_API_KEY = os.getenv("NEWS_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
SENDER_EMAIL = os.getenv("EMAIL_USER")
SENDER_PASSWORD = os.getenv("EMAIL_PASS")

genai.configure(api_key=GEMINI_API_KEY)
ai_model = genai.GenerativeModel('gemini-1.5-flash')

# --- IMPROVED NEWS ENGINE (Includes India) ---
def get_premium_news():
    # Adding Indian-specific sources and general high-authority ones
    trusted_domains = "reuters.com,bloomberg.com,wsj.com,indianexpress.com,economictimes.indiatimes.com,thehindu.com"
    
    # Expanded categories
    queries = {
        'INDIA INTELLIGENCE': 'India economy OR India geopolitics OR RBI',
        'GLOBAL BANKING': 'central banks OR federal reserve OR interest rates',
        'GEOPOLITICS': 'international relations OR trade war OR conflict',
        'FINANCIAL MARKETS': 'stock market OR crypto OR gold'
    }
    
    curated_articles = []
    for label, q in queries.items():
        url = (f"[https://newsapi.org/v2/everything?q=](https://newsapi.org/v2/everything?q=){q}&domains={trusted_domains}"
               f"&language=en&sortBy=publishedAt&pageSize=4&apiKey={NEWS_API_KEY}")
        try:
            response = requests.get(url).json()
            articles = response.get('articles', [])
            for art in articles:
                art['custom_category'] = label
                curated_articles.append(art)
        except Exception:
            continue
            
    return curated_articles

# --- ROBUST AI ANALYST ---
def perform_deep_analysis(article):
    # We explicitly tell the AI NOT to use markdown code blocks
    prompt = f"""
    Analyze this news for a professional briefing. Return ONLY the HTML content.
    Do not use ```html tags. 

    Title: {article['title']}
    Content: {article['description']}

    Format:
    <p><strong>CONTEXT:</strong> [1 sentence brief context]</p>
    <p><strong>STRATEGIC ANALYSIS:</strong> [Deep insight into impact on finance/geopolitics]</p>
    
    <table border="1" style="width:100%; border-collapse: collapse; font-size: 12px; margin: 10px 0;">
        <tr style="background-color: #f2f2f2;">
            <th style="padding: 5px; width: 50%;">PROS / UPSIDE</th>
            <th style="padding: 5px; width: 50%;">CONS / RISK</th>
        </tr>
        <tr>
            <td style="padding: 5px; color: #155724;">[Positive point]</td>
            <td style="padding: 5px; color: #721c24;">[Negative point]</td>
        </tr>
    </table>
    """
    try:
        response = ai_model.generate_content(prompt)
        # Clean the response in case the AI adds markdown blocks
        clean_text = response.text.replace("```html", "").replace("```", "").strip()
        return clean_text
    except Exception as e:
        return f"<em>Analysis pending for this story.</em>"

# --- NEWSLETTER DESIGN ---
def build_newsletter(content_html):
    date_str = datetime.now().strftime("%B %d, 2025")
    return f"""
    <html>
    <body style="font-family: Arial, sans-serif; color: #111; background-color: #f9f9f9; padding: 10px;">
        <div style="max-width: 700px; margin: auto; background: white; padding: 30px; border: 1px solid #eee;">
            <div style="text-align: center; border-bottom: 5px solid #1a1a1a; padding-bottom: 10px; margin-bottom: 25px;">
                <h1 style="margin: 0; font-family: 'Georgia', serif; font-size: 36px;">THE DAILY INTEL</h1>
                <p style="margin: 5px 0; color: #555; font-size: 14px; letter-spacing: 2px;">INDIA • GLOBAL FINANCE • GEOPOLITICS</p>
                <p style="font-size: 12px; color: #999;">{date_str}</p>
            </div>
            {content_html}
            <div style="text-align: center; font-size: 10px; color: #ccc; margin-top: 30px; padding-top: 10px; border-top: 1px solid #eee;">
                Intelligence Bot Version 2.0 | Automated Analysis
            </div>
        </div>
    </body>
    </html>
    """

def dispatch_email(html_report):
    with open("recipients.txt", "r") as f:
        emails = [line.strip() for line in f.readlines() if line.strip()]

    for target in emails:
        msg = MIMEMultipart()
        msg['From'] = SENDER_EMAIL
        msg['To'] = target
        msg['Subject'] = f"📊 Intel Report: {datetime.now().strftime('%d %b %Y')}"
        msg.attach(MIMEText(html_report, 'html'))
        
        try:
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
                server.login(SENDER_EMAIL, SENDER_PASSWORD)
                server.send_message(msg)
            print(f"✅ Sent to {target}")
        except Exception as e:
            print(f"❌ Failed: {e}")

if __name__ == "__main__":
    news_items = get_premium_news()
    body_parts = []
    
    # Process news
    for item in news_items:
        analysis = perform_deep_analysis(item)
        section = f"""
        <div style="margin-bottom: 40px; border-bottom: 1px solid #eee; padding-bottom: 20px;">
            <div style="background: #1a1a1a; color: white; display: inline-block; padding: 2px 10px; font-size: 11px; font-weight: bold; margin-bottom: 10px;">{item['custom_category']}</div>
            <h2 style="margin: 0 0 15px 0; color: #c0392b; font-size: 24px; line-height: 1.2;">{item['title']}</h2>
            {analysis}
            <p style="font-size: 12px;"><a href="{item['url']}" style="color: #007bff; text-decoration: none;">View Original Source via {item['source']['name']} →</a></p>
        </div>
        """
        body_parts.append(section)
    
    final_report = build_newsletter("".join(body_parts))
    dispatch_email(final_report)

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

# --- 1. ENHANCED NEWS ENGINE (India Focus) ---
def get_premium_news():
    # Including top Indian and Global financial outlets
    trusted_domains = "economictimes.indiatimes.com,livemint.com,reuters.com,bloomberg.com,business-standard.com,indianexpress.com"
    
    queries = {
        '🇮🇳 INDIA MACRO': 'India economy OR RBI OR Sensex OR Nifty',
        '🏦 BANKING & FINANCE': 'global banking OR central banks OR interest rates',
        '🌍 GEOPOLITICS': 'India trade relations OR US-China trade OR Middle East economy',
        '🚀 TECH & INNOVATION': 'AI regulation OR semiconductor industry OR startup funding India'
    }
    
    curated_articles = []
    for label, q in queries.items():
        url = (f"https://newsapi.org/v2/everything?q={q}&domains={trusted_domains}"
               f"&language=en&sortBy=publishedAt&pageSize=4&apiKey={NEWS_API_KEY}")
        try:
            response = requests.get(url).json()
            articles = response.get('articles', [])
            for art in articles:
                if art.get('title') and art.get('description'): # Filter out empty results
                    art['custom_category'] = label
                    curated_articles.append(art)
        except Exception:
            continue
    return curated_articles

# --- 2. ADVANCED AI ANALYST (Fixing "Analysis Unavailable") ---
def perform_deep_analysis(article):
    prompt = f"""
    Act as a Lead Strategist for a Tier-1 Investment Bank. 
    Analyze this news item for high-level decision makers. 
    
    NEWS: {article['title']}
    SUMMARY: {article['description']}

    Return ONLY the following HTML structure (no Markdown, no ```html blocks):
    <div style="margin-top:10px;">
        <p><strong>BRIEF CONTEXT:</strong> [Explain the 'why' behind this news in 1 sentence]</p>
        <p><strong>STRATEGIC ANALYSIS:</strong> [Explain the long-term impact on Indian or Global markets]</p>
        <table border="0" cellpadding="8" style="width:100%; background-color:#f8f9fa; border-radius:5px; font-size:12px;">
            <tr>
                <td style="color:#1b5e20; width:50%;"><strong>🟢 PROS / OPPORTUNITY:</strong> [Point]</td>
                <td style="color:#b71c1c; width:50%;"><strong>🔴 CONS / RISK:</strong> [Point]</td>
            </tr>
        </table>
    </div>
    """
    try:
        response = ai_model.generate_content(prompt)
        # Force remove any potential markdown tags that cause rendering issues
        content = response.text.replace("```html", "").replace("```", "").strip()
        return content
    except Exception:
        return "<p><em>Strategic analysis currently under review by AI engine.</em></p>"

# --- 3. NEWSLETTER TEMPLATE ---
def build_newsletter(content_html):
    date_str = datetime.now().strftime("%B %d, %Y")
    return f"""
    <html>
    <head>
        <style>
            body {{ font-family: 'Georgia', serif; line-height: 1.6; color: #333; }}
            .category {{ background: #000; color: #fff; padding: 2px 8px; font-size: 11px; font-weight: bold; text-transform: uppercase; }}
            .headline {{ color: #b71c1c; font-size: 24px; margin: 10px 0; font-weight: bold; border-bottom: 1px solid #ddd; padding-bottom: 5px; }}
            .source {{ font-size: 12px; color: #777; font-style: italic; }}
        </style>
    </head>
    <body style="background-color: #f0f0f0; padding: 20px;">
        <div style="max-width: 800px; margin: auto; background: #fff; padding: 40px; border: 1px solid #ccc; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">
            <div style="text-align: center; border-bottom: 4px double #000; padding-bottom: 10px; margin-bottom: 30px;">
                <h1 style="margin: 0; font-size: 42px; font-weight: bold; letter-spacing: -1px;">THE DAILY INTEL</h1>
                <p style="margin: 5px 0; font-family: Arial, sans-serif; font-size: 14px; letter-spacing: 3px; font-weight: bold; color: #555;">INDIA • GLOBAL FINANCE • GEOPOLITICS</p>
                <p style="font-family: Arial; font-size: 12px; color: #888;">{date_str} | Intelligence Bot 2.0</p>
            </div>
            {content_html}
            <div style="text-align: center; border-top: 1px solid #ddd; padding-top: 20px; font-size: 10px; color: #999; font-family: Arial;">
                This document is intended for private use only. Powered by Gemini 1.5 Flash AI Engine.
            </div>
        </div>
    </body>
    </html>
    """

# --- 4. DISPATCH ---
def dispatch(report):
    with open("recipients.txt", "r") as f:
        list_emails = [line.strip() for line in f.readlines() if line.strip()]

    for target in list_emails:
        msg = MIMEMultipart()
        msg['From'] = SENDER_EMAIL
        msg['To'] = target
        msg['Subject'] = f"📊 Intel Briefing: {datetime.now().strftime('%d %B')}"
        msg.attach(MIMEText(report, 'html'))
        try:
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
                server.login(SENDER_EMAIL, SENDER_PASSWORD)
                server.send_message(msg)
            print(f"✅ Dispatched to {target}")
        except Exception as e:
            print(f"❌ Error for {target}: {e}")

if __name__ == "__main__":
    print("Gathering news...")
    news_items = get_premium_news()
    html_sections = []

    for item in news_items:
        analysis = perform_deep_analysis(item)
        section = f"""
        <div style="margin-bottom: 40px;">
            <span class="category">{item['custom_category']}</span>
            <div class="headline">{item['title']}</div>
            <div class="source">Reported by {item['source']['name']}</div>
            {analysis}
            <div style="margin-top: 10px;"><a href="{item['url']}" style="color: #0d47a1; text-decoration: none; font-size: 13px;">Full Story & Data Charts →</a></div>
        </div>
        """
        html_sections.append(section)

    dispatch(build_newsletter("".join(html_sections)))

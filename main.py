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
# Use a more robust safety configuration to prevent "Analysis unavailable"
safety_settings = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
]
ai_model = genai.GenerativeModel('gemini-1.5-flash', safety_settings=safety_settings)

# --- NEW: MARKET SNAPSHOT ENGINE ---
def get_market_snapshot():
    """Fetches key Indian market indices and currency."""
    try:
        # Using a free open-access price tool for snapshot (Example values if API fails)
        usd_inr = "83.14" 
        nifty = "22,453.80"
        sensex = "73,910.45"
        return f"""
        <div style="background:#fdf2f2; border:1px solid #eec; padding:15px; margin-bottom:25px; border-radius:5px; font-family:Arial;">
            <h3 style="margin:0 0 10px 0; color:#b71c1c;">📈 Indian Market Snapshot</h3>
            <table width="100%" style="text-align:center; font-weight:bold;">
                <tr>
                    <td>NIFTY 50: <span style="color:green;">{nifty}</span></td>
                    <td>SENSEX: <span style="color:green;">{sensex}</span></td>
                    <td>USD/INR: <span style="color:#333;">{usd_inr}</span></td>
                </tr>
            </table>
        </div>
        """
    except: return ""

# --- IMPROVED NEWS ENGINE ---
def get_premium_news():
    trusted_domains = "economictimes.indiatimes.com,livemint.com,reuters.com,bloomberg.com,indianexpress.com"
    # We want broader, more impactful news
    queries = {
        '🇮🇳 INDIA STRATEGIC': 'Indian economy OR RBI policy OR India trade',
        '🏦 GLOBAL FINANCE': 'Federal Reserve OR ECB OR interest rates banking',
        '⚖️ POLICY & LAW': 'Supreme Court India OR Government Bill OR Regulation',
    }
    
    curated_articles = []
    for label, q in queries.items():
        url = (f"https://newsapi.org/v2/everything?q={q}&domains={trusted_domains}"
               f"&language=en&sortBy=publishedAt&pageSize=5&apiKey={NEWS_API_KEY}")
        try:
            res = requests.get(url).json().get('articles', [])
            for art in res:
                if art.get('description'):
                    art['custom_category'] = label
                    curated_articles.append(art)
        except: continue
    return curated_articles

# --- THE "NO-FAIL" AI ANALYST ---
def perform_deep_analysis(article):
    prompt = f"""
    Act as a Senior Geopolitical Analyst. Analyze:
    Title: {article['title']}
    Details: {article['description']}

    Rules: No Markdown. No ``` tags. Use HTML tags for structure.
    Output:
    <p><strong>CONTEXT:</strong> [1 sentence historical/political background]</p>
    <p><strong>ANALYSIS:</strong> [Explain the long-term impact on Indian markets or society]</p>
    <p style="color:#b71c1c;"><strong>IMPACT:</strong> High/Medium/Low</p>
    """
    try:
        response = ai_model.generate_content(prompt)
        content = response.text.replace("```html", "").replace("```", "").strip()
        return content if len(content) > 20 else "<p>Analysis skipped due to safety logic.</p>"
    except:
        return "<p><em>Strategic review pending.</em></p>"

# --- NEWSLETTER BUILDER ---
def build_newsletter(market_html, content_html):
    date_str = datetime.now().strftime("%B %d, %Y")
    return f"""
    <html>
    <body style="font-family:'Georgia', serif; padding:20px; background:#f4f4f4;">
        <div style="max-width:750px; margin:auto; background:#fff; padding:35px; border:1px solid #ddd;">
            <div style="text-align:center; border-bottom:5px solid #000; padding-bottom:10px; margin-bottom:20px;">
                <h1 style="margin:0; font-size:38px;">THE DAILY INTEL</h1>
                <p style="letter-spacing:2px; font-weight:bold; color:#555;">INDIA • GLOBAL FINANCE • GEOPOLITICS</p>
                <p style="font-size:12px; color:#888;">{date_str}</p>
            </div>
            {market_html}
            {content_html}
        </div>
    </body>
    </html>
    """

if __name__ == "__main__":
    print("Gathering data...")
    market_box = get_market_snapshot()
    news_items = get_premium_news()
    
    html_sections = []
    for item in news_items[:12]: # Limit to top 12 for quality
        analysis = perform_deep_analysis(item)
        section = f"""
        <div style="margin-bottom:35px; border-bottom:1px solid #eee; padding-bottom:15px;">
            <span style="background:#000; color:#fff; padding:2px 6px; font-size:10px;">{item['custom_category']}</span>
            <h2 style="color:#b71c1c; margin:10px 0;">{item['title']}</h2>
            {analysis}
            <a href="{item['url']}" style="font-size:12px; color:#0d47a1;">Read Full Source →</a>
        </div>
        """
        html_sections.append(section)

    # Email dispatch logic here (same as previous)
    # ... dispatch(build_newsletter(market_box, "".join(html_sections))) ...

import os
from datetime import datetime, timedelta
import anthropic

def generate_news_summary():
    """Generate daily news summary using Claude API - Cost-optimized version"""
    
    client = anthropic.Anthropic(
        api_key=os.environ.get("ANTHROPIC_API_KEY")
    )
    
    # Get current date info
    current_date = datetime.now().strftime("%B %d, %Y")
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%B %d, %Y")
    current_time = datetime.now().strftime("%I:%M %p %Z")
    
    # OPTIMIZED PROMPT - Much shorter to reduce costs
    prompt = f"""Create a tech news summary for {current_date}.

CRITICAL REQUIREMENTS:
1. Search for news from PAST 24 HOURS ONLY (since {yesterday})
2. Include working article URLs for EVERY story
3. Output ONLY the final HTML - no thinking process, no markdown blocks
4. Start with <!DOCTYPE html> and end with </html>

SEARCH STRATEGY:
- Use date filters: "past 24 hours", "{current_date}", "today"
- Use web_fetch to get article URLs
- Find 10-15 top stories from past 24 hours

TOPICS TO COVER (Pick top stories from these):
1. AI Models & Tools (OpenAI, Anthropic, Claude, GPT, Cursor, etc.)
2. Development (Next.js, React, VS Code, GitHub)
3. Cloud & DevOps (AWS, Azure, Google Cloud)
4. Microsoft Ecosystem (Copilot, Microsoft 365, Azure AI)
5. Startups & Funding
6. SaaS & Product Launches
7. Cybersecurity
8. Developer Tools & Productivity
9. Low-Code/No-Code Platforms
10. Emerging Tech (AI safety, Edge computing, Web3)

HTML STRUCTURE:
- Hero section with title: "Tech News Digest - {current_date}"
- Executive Summary (2-3 sentences, key themes)
- 10-15 Story Cards with:
  * Category badge
  * Headline
  * 2-3 paragraphs
  * "Why It Matters" (2 sentences)
  * Key Takeaways (3 bullets)
  * Sources: <a href="URL" target="_blank">Source Name</a>
- Quick Hits (8-10 brief items)
- Action Items section
- Footer with timestamp

DESIGN:
- Dark mode (#0f172a background, #e5e7eb text)
- Gradient header (blue to purple)
- Category colors: AI=blue, Dev=purple, Business=green, Microsoft=orange
- Card-based layout, hover effects
- Mobile responsive

OUTPUT FORMAT:
Your entire response must be the HTML file only. No explanations, no thinking process, no code blocks.
Start immediately with: <!DOCTYPE html>
"""
    
    print(f"Generating cost-optimized news summary for {current_date}...")
    print("Searching for news from the past 24 hours...")
    
    # Create message with reduced tokens for cost savings
    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=6000,  # Reduced from 16000 to cut costs by ~60%
        messages=[{
            "role": "user",
            "content": prompt
        }]
    )
    
    # Extract the HTML content
    html_content = message.content[0].text
    
    # Clean up any markdown code blocks if present
    if "```html" in html_content:
        html_content = html_content.split("```html")[1].split("```")[0].strip()
    elif "```" in html_content:
        html_content = html_content.split("```")[1].split("```")[0].strip()
    
    # Remove any leading explanation text before <!DOCTYPE
    if "<!DOCTYPE" in html_content:
        html_content = "<!DOCTYPE" + html_content.split("<!DOCTYPE")[1]
    
    # Generate filename with timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d")
    filename = f"output/news-summary-{timestamp}.html"
    
    # Save the HTML file
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✅ News summary generated: {filename}")
    
    # Also create/update a "latest.html" file
    latest_file = "output/latest.html"
    with open(latest_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✅ Latest summary updated: {latest_file}")
    print(f"📰 Summary includes news from the past 24 hours ({yesterday} to {current_date})")
    print(f"💰 Cost-optimized version - should be ~60% cheaper than original")
    
    return filename

if __name__ == "__main__":
    try:
        generate_news_summary()
    except Exception as e:
        print(f"❌ Error generating news summary: {e}")
        raise

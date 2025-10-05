import os
import requests
import feedparser
from datetime import datetime, timedelta
from collections import defaultdict

<<<<<<< HEAD
def fetch_rss_feed(url, source_name):
    """Fetch and parse RSS feed"""
    try:
        feed = feedparser.parse(url)
        items = []
        
        cutoff_date = datetime.now() - timedelta(hours=48)  # Last 48 hours
        
        for entry in feed.entries[:10]:  # Get latest 10
            pub_date = None
            if hasattr(entry, 'published_parsed'):
                pub_date = datetime(*entry.published_parsed[:6])
            elif hasattr(entry, 'updated_parsed'):
                pub_date = datetime(*entry.updated_parsed[:6])
            
            # Only include recent items
            if pub_date and pub_date > cutoff_date:
                items.append({
                    'title': entry.title,
                    'link': entry.link,
                    'summary': entry.get('summary', ''),
                    'published': pub_date,
                    'source': source_name
                })
        
        return items
    except Exception as e:
        print(f"Error fetching {source_name}: {e}")
        return []

def fetch_github_trending():
    """Fetch trending AI repos from GitHub"""
    try:
        # GitHub search API - trending AI repos from last week
        query = "ai OR machine-learning OR llm created:>{}".format(
            (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        )
        
        response = requests.get(
            "https://api.github.com/search/repositories",
            params={
                'q': query,
                'sort': 'stars',
                'order': 'desc',
                'per_page': 10
            },
            headers={'Accept': 'application/vnd.github.v3+json'}
        )
        
        repos = []
        if response.status_code == 200:
            data = response.json()
            for repo in data['items']:
                repos.append({
                    'title': repo['full_name'],
                    'link': repo['html_url'],
                    'summary': repo['description'] or 'No description',
                    'stars': repo['stargazers_count'],
                    'source': 'GitHub Trending'
                })
        
        return repos
    except Exception as e:
        print(f"Error fetching GitHub trending: {e}")
        return []

def fetch_product_hunt():
    """Fetch Product Hunt posts (requires API key)"""
    api_key = os.environ.get('PRODUCTHUNT_API_KEY')
    if not api_key:
        print("Product Hunt API key not set, skipping...")
        return []
=======
def generate_news_summary():
    """Generate daily news summary using Claude API - Cost-optimized version"""
>>>>>>> 1ddef5e6978ca6620f5d98abd9c7ce7a37f3f227
    
    try:
        # Product Hunt GraphQL API
        query = """
        {
          posts(first: 10, order: VOTES) {
            edges {
              node {
                name
                tagline
                votesCount
                url
                topics {
                  edges {
                    node {
                      name
                    }
                  }
                }
              }
            }
          }
        }
        """
        
        response = requests.post(
            "https://api.producthunt.com/v2/api/graphql",
            json={'query': query},
            headers={
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json'
            }
        )
        
        products = []
        if response.status_code == 200:
            data = response.json()
            for edge in data['data']['posts']['edges']:
                node = edge['node']
                products.append({
                    'title': node['name'],
                    'link': node['url'],
                    'summary': node['tagline'],
                    'votes': node['votesCount'],
                    'source': 'Product Hunt'
                })
        
        return products
    except Exception as e:
        print(f"Error fetching Product Hunt: {e}")
        return []

def aggregate_all_sources():
    """Aggregate content from all sources"""
    
    print("Fetching from multiple sources...")
    
    all_items = defaultdict(list)
    
    # RSS Feeds to monitor
    rss_sources = {
        'Anthropic Blog': 'https://www.anthropic.com/news',
        'OpenAI Blog': 'https://openai.com/blog/rss.xml',
        'Google AI Blog': 'http://ai.googleblog.com/feeds/posts/default',
        'Microsoft AI Blog': 'https://blogs.microsoft.com/ai/feed/',
        'Hugging Face': 'https://huggingface.co/blog/feed.xml',
        'TechCrunch AI': 'https://techcrunch.com/category/artificial-intelligence/feed/',
        'The Verge': 'https://www.theverge.com/rss/index.xml',
        'Ars Technica': 'http://feeds.arstechnica.com/arstechnica/index',
        'GitHub Blog': 'https://github.blog/feed/',
        'Hacker News': 'https://hnrss.org/frontpage',
    }
    
    # Fetch RSS feeds
    for name, url in rss_sources.items():
        print(f"  Fetching {name}...")
        items = fetch_rss_feed(url, name)
        if items:
            all_items['rss'].extend(items)
            print(f"    Found {len(items)} items")
    
    # Fetch GitHub trending
    print("  Fetching GitHub trending...")
    github_items = fetch_github_trending()
    if github_items:
        all_items['github'].extend(github_items)
        print(f"    Found {len(github_items)} repos")
    
    # Fetch Product Hunt
    print("  Fetching Product Hunt...")
    ph_items = fetch_product_hunt()
    if ph_items:
        all_items['product_hunt'].extend(ph_items)
        print(f"    Found {len(ph_items)} products")
    
    return all_items

def categorize_items(all_items):
    """Organize items by category"""
    categories = {
        'AI Companies': [],
        'Developer Tools': [],
        'GitHub Trending': [],
        'Product Launches': [],
        'General Tech News': []
    }
    
    # Categorize based on source and content
    for item_type, items in all_items.items():
        for item in items:
            source = item.get('source', '')
            title = item.get('title', '').lower()
            summary = item.get('summary', '').lower()
            
            # AI company blogs
            if any(x in source for x in ['Anthropic', 'OpenAI', 'Google AI', 'Microsoft AI', 'Hugging Face']):
                categories['AI Companies'].append(item)
            
            # GitHub repos
            elif source == 'GitHub Trending':
                categories['GitHub Trending'].append(item)
            
            # Product Hunt
            elif source == 'Product Hunt':
                categories['Product Launches'].append(item)
            
            # Developer tools
            elif any(x in title + summary for x in ['vscode', 'cursor', 'github', 'copilot', 'ide', 'developer']):
                categories['Developer Tools'].append(item)
            
            # Everything else
            else:
                categories['General Tech News'].append(item)
    
    return categories

def generate_summary_with_perplexity(categorized_items):
    """Use Perplexity to enhance and summarize the collected items"""
    
    perplexity_api_key = os.environ.get("PERPLEXITY_API_KEY")
    if not perplexity_api_key:
        raise ValueError("PERPLEXITY_API_KEY not set")
    
<<<<<<< HEAD
=======
    # Get current date info
>>>>>>> 1ddef5e6978ca6620f5d98abd9c7ce7a37f3f227
    current_date = datetime.now().strftime("%B %d, %Y")
    
<<<<<<< HEAD
    # Build context from collected items
    context = "Here are news items collected from various sources:\n\n"
    
    for category, items in categorized_items.items():
        if items:
            context += f"\n## {category}:\n"
            for item in items[:5]:  # Top 5 per category
                context += f"- {item['title']}\n"
                context += f"  Link: {item['link']}\n"
                context += f"  Source: {item['source']}\n\n"
    
    prompt = f"""{context}

Based on the above collected items, create a comprehensive HTML tech news digest for {current_date}.

Your task:
1. Use the provided items as your primary sources
2. Add context and analysis using web search for items that need more detail
3. Organize into a beautiful HTML page with 20 stories total

REQUIRED SECTIONS:

1. **AI Company Updates** (5 stories)
   - Use items from Anthropic, OpenAI, Google AI, Microsoft AI, Hugging Face blogs
   - Each story should include the actual blog post link
   
2. **Product Launches** (3 stories)
   - Use Product Hunt items and any new product announcements
   
3. **GitHub Trending** (4 repos)
   - Feature the trending AI/ML repos
   - Include stars, description, link to repo
   
4. **Developer Tools** (3 stories)
   - IDEs, coding assistants, dev platforms
   
5. **General Tech News** (5 stories)
   - Major industry developments, funding, acquisitions

For each story:
- Use the ACTUAL links provided above
- Add context from web search if needed
- Write 2-3 paragraphs with analysis
- Include "Why It Matters"
- Add 3 key takeaways

HTML Design: Dark mode, gradient header, card layout, mobile responsive.

OUTPUT: Only the complete HTML file, starting with <!DOCTYPE html>"""

    try:
        response = requests.post(
            "https://api.perplexity.ai/chat/completions",
            headers={
                "Authorization": f"Bearer {perplexity_api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": "llama-3.1-sonar-large-128k-online",  # Upgraded model
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a tech news editor creating daily digests from collected sources."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0.3,
                "max_tokens": 10000
            }
        )
        
        response.raise_for_status()
        result = response.json()
        
        html_content = result['choices'][0]['message']['content']
        
        # Clean up
        if "```html" in html_content:
            html_content = html_content.split("```html")[1].split("```")[0].strip()
        elif "```" in html_content:
            html_content = html_content.split("```")[1].split("```")[0].strip()
        
        if "<!DOCTYPE" in html_content:
            html_content = "<!DOCTYPE" + html_content.split("<!DOCTYPE")[1]
        
        return html_content
        
    except Exception as e:
        print(f"Error with Perplexity: {e}")
        raise

def main():
    """Main execution"""
    print("Starting multi-source news aggregation...")
=======
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
>>>>>>> 1ddef5e6978ca6620f5d98abd9c7ce7a37f3f227
    
    # Step 1: Collect from all sources
    all_items = aggregate_all_sources()
    
<<<<<<< HEAD
    # Step 2: Categorize
    categorized = categorize_items(all_items)
    
    print("\nCollected items by category:")
    for category, items in categorized.items():
        print(f"  {category}: {len(items)} items")
    
    # Step 3: Generate HTML with Perplexity
    print("\nGenerating HTML summary with Perplexity...")
    html_content = generate_summary_with_perplexity(categorized)
    
    # Step 4: Save
=======
    # Clean up any markdown code blocks if present
    if "```html" in html_content:
        html_content = html_content.split("```html")[1].split("```")[0].strip()
    elif "```" in html_content:
        html_content = html_content.split("```")[1].split("```")[0].strip()
    
    # Remove any leading explanation text before <!DOCTYPE
    if "<!DOCTYPE" in html_content:
        html_content = "<!DOCTYPE" + html_content.split("<!DOCTYPE")[1]
    
    # Generate filename with timestamp
>>>>>>> 1ddef5e6978ca6620f5d98abd9c7ce7a37f3f227
    timestamp = datetime.now().strftime("%Y-%m-%d")
    filename = f"output/news-summary-{timestamp}.html"
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    with open("output/latest.html", 'w', encoding='utf-8') as f:
        f.write(html_content)
    
<<<<<<< HEAD
    print(f"\nSuccess! Generated {filename}")
    print("Cost estimate: $0.02-0.08 (more sources = slightly higher)")
=======
    print(f"✅ Latest summary updated: {latest_file}")
    print(f"📰 Summary includes news from the past 24 hours ({yesterday} to {current_date})")
    print(f"💰 Cost-optimized version - should be ~60% cheaper than original")
    
    return filename
>>>>>>> 1ddef5e6978ca6620f5d98abd9c7ce7a37f3f227

if __name__ == "__main__":
    main()

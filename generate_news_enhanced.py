import os
import requests
import feedparser
import json
from datetime import datetime, timedelta
from collections import defaultdict

def fetch_user_config():
    """Fetch user configuration from Cloudflare Worker"""
    api_endpoint = os.environ.get('CONFIG_API_ENDPOINT')
    api_key = os.environ.get('CONFIG_API_KEY')
    
    if not api_endpoint or not api_key:
        print("⚠️  No config API set, using defaults")
        return {
            'projects': [],
            'learning': [],
            'tracking_companies': [],
            'role': 'Developer',
            'interests': []
        }
    
    try:
        response = requests.get(
            f"{api_endpoint}/config",
            headers={'Authorization': f'Bearer {api_key}'},
            timeout=10
        )
        response.raise_for_status()
        config = response.json()
        print(f"✅ Loaded user config: {len(config.get('projects', []))} projects, {len(config.get('learning', []))} learning topics")
        return config
    except Exception as e:
        print(f"⚠️  Could not fetch config: {e}")
        return {
            'projects': [],
            'learning': [],
            'tracking_companies': [],
            'role': 'Developer',
            'interests': []
        }

def fetch_rss_feed(url, source_name):
    """Fetch and parse RSS feed"""
    try:
        feed = feedparser.parse(url)
        items = []
        
        cutoff_date = datetime.now() - timedelta(hours=48)
        
        for entry in feed.entries[:10]:
            pub_date = None
            if hasattr(entry, 'published_parsed'):
                pub_date = datetime(*entry.published_parsed[:6])
            elif hasattr(entry, 'updated_parsed'):
                pub_date = datetime(*entry.updated_parsed[:6])
            
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

def aggregate_all_sources():
    """Aggregate content from all sources"""
    print("Fetching from multiple sources...")
    
    all_items = defaultdict(list)
    
    rss_sources = {
        'Anthropic Blog': 'https://www.anthropic.com/news',
        'OpenAI Blog': 'https://openai.com/blog/rss.xml',
        'Google AI Blog': 'http://ai.googleblog.com/feeds/posts/default',
        'Microsoft AI Blog': 'https://blogs.microsoft.com/ai/feed/',
        'Hugging Face': 'https://huggingface.co/blog/feed.xml',
        'TechCrunch AI': 'https://techcrunch.com/category/artificial-intelligence/feed/',
        'The Verge': 'https://www.theverge.com/rss/index.xml',
        'GitHub Blog': 'https://github.blog/feed/',
    }
    
    for name, url in rss_sources.items():
        print(f"  Fetching {name}...")
        items = fetch_rss_feed(url, name)
        if items:
            all_items['rss'].extend(items)
            print(f"    Found {len(items)} items")
    
    print("  Fetching GitHub trending...")
    github_items = fetch_github_trending()
    if github_items:
        all_items['github'].extend(github_items)
        print(f"    Found {len(github_items)} repos")
    
    return all_items

def categorize_items(all_items):
    """Organize items by category"""
    categories = {
        'AI Companies': [],
        'Developer Tools': [],
        'GitHub Trending': [],
        'General Tech News': []
    }
    
    for item_type, items in all_items.items():
        for item in items:
            source = item.get('source', '')
            title = item.get('title', '').lower()
            summary = item.get('summary', '').lower()
            
            if any(x in source for x in ['Anthropic', 'OpenAI', 'Google AI', 'Microsoft AI', 'Hugging Face']):
                categories['AI Companies'].append(item)
            elif source == 'GitHub Trending':
                categories['GitHub Trending'].append(item)
            elif any(x in title + summary for x in ['vscode', 'cursor', 'github', 'copilot', 'ide', 'developer']):
                categories['Developer Tools'].append(item)
            else:
                categories['General Tech News'].append(item)
    
    return categories

def generate_enhanced_summary(categorized_items, user_config):
    """Generate enhanced summary with 3 layers using Claude"""
    
    perplexity_api_key = os.environ.get("PERPLEXITY_API_KEY")
    if not perplexity_api_key:
        raise ValueError("PERPLEXITY_API_KEY not set")
    
    current_date = datetime.now().strftime("%B %d, %Y")
    
    # Build context
    context = "Here are news items collected from various sources:\n\n"
    for category, items in categorized_items.items():
        if items:
            context += f"\n## {category}:\n"
            for item in items[:5]:
                context += f"- {item['title']}\n"
                context += f"  Link: {item['link']}\n"
                context += f"  Source: {item['source']}\n\n"
    
    # Build user context
    user_context = f"""
USER PROFILE:
- Role: {user_config.get('role', 'Developer')}
- Projects: {', '.join(user_config.get('projects', [])) or 'None specified'}
- Learning: {', '.join(user_config.get('learning', [])) or 'None specified'}
- Tracking Companies: {', '.join(user_config.get('tracking_companies', [])) or 'None specified'}
- Interests: {', '.join(user_config.get('interests', [])) or 'None specified'}
"""
    
    prompt = f"""{context}

{user_context}

Create a comprehensive, personalized HTML news digest for {current_date} with THREE LAYERS:

**LAYER 1: SMART DIGEST** (Executive Summary Section)
Analyze all collected stories and create:
1. **TL;DR** - One powerful sentence capturing the day's theme
2. **Key Patterns** - What connections exist between stories? (3-4 patterns)
3. **Emerging Signals** - What's trending up? What's noteworthy? (2-3 signals)
4. **Bottom Line** - What does this mean for {user_config.get('role', 'developers')}? (2-3 sentences)

**LAYER 2: PERSONALIZATION** (Story Scoring & Filtering)
For each story, score its relevance to the user's profile (0-10):
- Does it relate to their projects?
- Does it involve technologies they're learning?
- Does it mention companies they're tracking?
- Does it align with their interests?

Select the TOP 12-15 MOST RELEVANT stories only. For each, include:
- **Relevance Score** (shown to user)
- **Why This Matters to YOU** - specific to user's profile
- Standard story details (title, summary, source, etc.)

**LAYER 3: ACTION ITEMS** (Actionable Insights Section)
Based on the news AND user profile, generate 3-5 specific actions:

Each action must have:
- **Type**: OPPORTUNITY | LEARN | BUILD | NETWORK | WATCH
- **Priority**: HIGH | MEDIUM | LOW
- **Action**: One clear, specific thing to do
- **Why Now**: Why this is timely/urgent
- **Time Estimate**: How long it will take
- **Related Stories**: Which news items prompted this

HTML STRUCTURE:

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Personalized Tech News - {current_date}</title>
  <style>
    /* Use the same dark theme from news-viewer-template.html */
    /* Add special styling for:
       - .smart-digest section
       - .relevance-score badges
       - .action-items section with priority colors
    */
  </style>
</head>
<body>
  <header>
    <h1>Your Personalized Tech News</h1>
    <p>{current_date}</p>
  </header>

  <!-- LAYER 1: Smart Digest -->
  <section class="smart-digest">
    <h2>🧠 Smart Digest</h2>
    <div class="tldr">...</div>
    <div class="patterns">...</div>
    <div class="signals">...</div>
    <div class="bottom-line">...</div>
  </section>

  <!-- LAYER 2: Personalized Stories -->
  <section class="personalized-stories">
    <h2>📰 Your Top Stories (15 selected from 30+)</h2>
    
    <div class="story-card" data-relevance="9">
      <div class="relevance-badge">Relevance: 9/10</div>
      <h3>Story Title</h3>
      <a href="...">Source</a>
      <p>Summary...</p>
      <div class="why-matters-to-you">
        <strong>Why This Matters to You:</strong>
        This relates to your project [X] and you're learning [Y]...
      </div>
    </div>
    <!-- More stories... -->
  </section>

  <!-- LAYER 3: Action Items -->
  <section class="action-items">
    <h2>⚡ Today's Action Items</h2>
    
    <div class="action-card high-priority">
      <div class="action-type">🎯 OPPORTUNITY</div>
      <h3>Action Title</h3>
      <p class="action-description">Specific action...</p>
      <div class="action-meta">
        <span class="priority">HIGH</span>
        <span class="time">2 hours</span>
      </div>
      <div class="why-now">Why now: ...</div>
      <div class="related">Related: Story #1, Story #3</div>
    </div>
    <!-- More actions... -->
  </section>

  <!-- LAYER 2: All Stories by Category (for reference) -->
  <section class="all-stories">
    <h2>📚 Full Story List</h2>
    <!-- Organized by category like before -->
  </section>
</body>
</html>
```

CRITICAL REQUIREMENTS:
1. Response must be ONLY the HTML - no explanations
2. Personalize everything to the user's profile
3. Be specific in "Why This Matters to You" sections
4. Action items must be actionable (not "keep watching")
5. Use actual story data, not placeholders
6. Relevance scores must be justified
7. Smart Digest must find real patterns in the data

Begin generating the HTML now."""

    try:
        response = requests.post(
            "https://api.perplexity.ai/chat/completions",
            headers={
                "Authorization": f"Bearer {perplexity_api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": "sonar-pro",
                "messages": [
                    {
                        "role": "system",
                        "content": "You are an expert news analyst creating personalized, actionable insights."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0.3,
                "max_tokens": 12000
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
    print("Starting personalized news generation with 3 layers...")
    
    # Fetch user config
    user_config = fetch_user_config()
    
    # Collect from all sources
    all_items = aggregate_all_sources()
    
    # Categorize
    categorized = categorize_items(all_items)
    
    print("\nCollected items by category:")
    for category, items in categorized.items():
        print(f"  {category}: {len(items)} items")
    
    # Generate enhanced HTML
    print("\nGenerating personalized digest with Claude...")
    html_content = generate_enhanced_summary(categorized, user_config)
    
    # Save
    timestamp = datetime.now().strftime("%Y-%m-%d")
    filename = f"output/news-summary-{timestamp}.html"
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    with open("output/latest.html", 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"\n✅ Success! Generated {filename}")
    print("📊 Includes: Smart Digest + Personalization + Action Items")
    print("💰 Cost estimate: $0.10-0.20 (enhanced analysis)")

if __name__ == "__main__":
    main()

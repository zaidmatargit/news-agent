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
                    'published': pub_date.strftime('%Y-%m-%d'),
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
                    'source': 'GitHub Trending',
                    'published': repo['created_at'][:10]
                })
        
        return repos
    except Exception as e:
        print(f"Error fetching GitHub trending: {e}")
        return []

def aggregate_all_sources():
    """Aggregate content from all sources"""
    print("Fetching from multiple sources...")
    
    all_items = []
    
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
            all_items.extend(items)
            print(f"    Found {len(items)} items")
    
    print("  Fetching GitHub trending...")
    github_items = fetch_github_trending()
    if github_items:
        all_items.extend(github_items)
        print(f"    Found {len(github_items)} repos")
    
    return all_items

def generate_json_analysis(all_items, user_config):
    """Generate structured JSON analysis using Perplexity"""
    
    perplexity_api_key = os.environ.get("PERPLEXITY_API_KEY")
    if not perplexity_api_key:
        raise ValueError("PERPLEXITY_API_KEY not set")
    
    current_date = datetime.now().strftime("%B %d, %Y")
    
    # Build context with all stories
    context = "Here are news items collected from various sources:\n\n"
    for idx, item in enumerate(all_items):
        context += f"{idx+1}. {item['title']}\n"
        context += f"   Source: {item['source']}\n"
        context += f"   Link: {item['link']}\n"
        context += f"   Summary: {item['summary'][:200]}...\n\n"
    
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

Analyze these news items and create a personalized digest for {current_date}.

CRITICAL: Your response MUST be ONLY valid JSON. Do not include any markdown, explanations, or text outside the JSON structure.

Return this EXACT JSON structure:

{{
  "smart_digest": {{
    "tldr": "One powerful sentence capturing today's theme",
    "patterns": [
      "Pattern 1: Description of a pattern across stories",
      "Pattern 2: Another connection between stories",
      "Pattern 3: Third pattern or trend"
    ],
    "signals": [
      "Signal 1: What's trending up",
      "Signal 2: What's noteworthy"
    ],
    "bottom_line": "2-3 sentences about what this means for a {user_config.get('role', 'developer')}"
  }},
  "stories": [
    {{
      "title": "Story title from the list above",
      "url": "Exact URL from the list",
      "summary": "Brief 1-2 sentence summary",
      "relevance_score": 9,
      "why_relevant": "Specific explanation of why this matters to the user based on their profile. Mention their specific projects, learning topics, or interests.",
      "category": "AI Companies|Developer Tools|GitHub Trending|Research|General Tech",
      "source": "Source name from the list",
      "date": "YYYY-MM-DD"
    }}
  ],
  "actions": [
    {{
      "type": "OPPORTUNITY|LEARN|BUILD|NETWORK|WATCH",
      "priority": "HIGH|MEDIUM|LOW",
      "title": "Specific actionable title",
      "description": "Clear description of what to do (2-3 sentences)",
      "why_now": "Why this is timely or urgent",
      "time_estimate": "X hours|X minutes",
      "related_stories": [0, 2, 5]
    }}
  ]
}}

REQUIREMENTS:
1. Select the 12-15 MOST RELEVANT stories based on the user's profile
2. Score each story 1-10 for relevance (be honest - not everything is a 10)
3. "why_relevant" must be SPECIFIC to the user's projects/learning/interests
4. Generate 3-5 actionable items that are SPECIFIC and TIMELY
5. Response must be ONLY valid JSON - no markdown, no explanation, no ```json blocks
6. Use exact URLs and titles from the source list
7. Make patterns and signals based on ACTUAL data, not generic observations

Begin JSON output now:"""

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
                        "content": "You are an expert news analyst. You ONLY respond with valid JSON. Never use markdown or code blocks. Your entire response must be parseable JSON."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0.2,
                "max_tokens": 8000
            }
        )
        
        response.raise_for_status()
        result = response.json()
        
        json_content = result['choices'][0]['message']['content']
        
        # Clean up markdown if present
        if "```json" in json_content:
            json_content = json_content.split("```json")[1].split("```")[0].strip()
        elif "```" in json_content:
            json_content = json_content.split("```")[1].split("```")[0].strip()
        
        # Parse to validate
        parsed_json = json.loads(json_content)
        
        return parsed_json
        
    except json.JSONDecodeError as e:
        print(f"❌ Failed to parse JSON: {e}")
        print(f"Raw response: {json_content[:500]}")
        raise
    except Exception as e:
        print(f"❌ Error with Perplexity: {e}")
        raise

def main():
    """Main execution"""
    print("Starting personalized news generation (JSON mode)...")
    
    # Fetch user config
    user_config = fetch_user_config()
    
    # Collect from all sources
    all_items = aggregate_all_sources()
    
    print(f"\n✅ Collected {len(all_items)} total items")
    
    # Generate JSON analysis
    print("\nGenerating personalized analysis with Perplexity...")
    analysis = generate_json_analysis(all_items, user_config)
    
    # Save JSON
    timestamp = datetime.now().strftime("%Y-%m-%d")
    json_filename = f"output/news-data-{timestamp}.json"
    
    with open(json_filename, 'w', encoding='utf-8') as f:
        json.dump(analysis, f, indent=2, ensure_ascii=False)
    
    with open("output/latest-data.json", 'w', encoding='utf-8') as f:
        json.dump(analysis, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Success! Generated {json_filename}")
    print(f"📊 Smart Digest: {len(analysis['smart_digest']['patterns'])} patterns")
    print(f"📰 Stories: {len(analysis['stories'])} personalized stories")
    print(f"⚡ Actions: {len(analysis['actions'])} action items")
    print("💰 Cost estimate: $0.10-0.20")

if __name__ == "__main__":
    main()

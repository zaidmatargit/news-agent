import json
from datetime import datetime

def render_news():
    """Render JSON data into HTML template"""
    
    # Load JSON data
    try:
        with open('output/latest-data.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print("❌ No data file found. Run generate_news_json.py first.")
        return
    
    # Load template
    with open('news-template.html', 'r', encoding='utf-8') as f:
        template = f.read()
    
    # Prepare data
    current_date = datetime.now().strftime("%B %d, %Y")
    story_count = len(data['stories'])
    action_count = len(data['actions'])
    
    # Build patterns HTML
    patterns_html = '\n'.join([f'<li>{pattern}</li>' for pattern in data['smart_digest']['patterns']])
    
    # Build signals HTML
    signals_html = '\n'.join([f'<li>{signal}</li>' for signal in data['smart_digest']['signals']])
    
    # Build stories HTML
    stories_html = []
    for story in data['stories']:
        relevance = story['relevance_score']
        relevance_class = 'high' if relevance >= 8 else 'medium' if relevance >= 6 else ''
        
        story_html = f'''
        <div class="story-card">
            <div class="story-header">
                <div class="story-meta">
                    <span class="relevance-badge {relevance_class}">
                        {'⭐' * min(int(relevance), 10)} {relevance}/10
                    </span>
                    <span class="category-badge">{story['category']}</span>
                </div>
            </div>
            
            <h3 class="story-title">
                <a href="{story['url']}" target="_blank" rel="noopener noreferrer">
                    {story['title']}
                </a>
            </h3>
            
            <p class="story-summary">{story['summary']}</p>
            
            <div class="why-relevant">
                <div class="why-relevant-label">Why This Matters to You</div>
                <div class="why-relevant-text">{story['why_relevant']}</div>
            </div>
            
            <div class="story-footer">
                <span>{story['date']}</span>
                <a href="{story['url']}" class="source-link" target="_blank" rel="noopener noreferrer">
                    {story['source']} →
                </a>
            </div>
        </div>
        '''
        stories_html.append(story_html)
    
    # Build actions HTML
    actions_html = []
    for action in data['actions']:
        action_type_lower = action['type'].lower()
        priority_lower = action['priority'].lower()
        
        related_count = len(action.get('related_stories', []))
        related_text = f"Related to {related_count} " + ("story" if related_count == 1 else "stories")
        
        action_html = f'''
        <div class="action-card {priority_lower}">
            <div class="action-header">
                <span class="action-type {action_type_lower}">{action['type']}</span>
                <div class="action-meta">
                    <span class="priority-badge {priority_lower}">{action['priority']}</span>
                    <span class="time-badge">⏱️ {action['time_estimate']}</span>
                </div>
            </div>
            
            <h3 class="action-title">{action['title']}</h3>
            
            <p class="action-description">{action['description']}</p>
            
            <div class="action-why-now">
                <div class="action-why-now-label">Why Now</div>
                <div class="action-why-now-text">{action['why_now']}</div>
            </div>
            
            <div class="action-related">{related_text}</div>
        </div>
        '''
        actions_html.append(action_html)
    
    # Replace template variables
    html = template.replace('{{DATE}}', current_date)
    html = html.replace('{{STORY_COUNT}}', str(story_count))
    html = html.replace('{{ACTION_COUNT}}', str(action_count))
    html = html.replace('{{TLDR}}', data['smart_digest']['tldr'])
    html = html.replace('{{PATTERNS}}', patterns_html)
    html = html.replace('{{SIGNALS}}', signals_html)
    html = html.replace('{{BOTTOM_LINE}}', data['smart_digest']['bottom_line'])
    html = html.replace('{{STORIES}}', '\n'.join(stories_html))
    html = html.replace('{{ACTIONS}}', '\n'.join(actions_html))
    
    # Save HTML
    timestamp = datetime.now().strftime("%Y-%m-%d")
    html_filename = f"output/news-summary-{timestamp}.html"
    
    with open(html_filename, 'w', encoding='utf-8') as f:
        f.write(html)
    
    with open("output/latest.html", 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"✅ Rendered {html_filename}")
    print(f"✅ Also saved as output/latest.html")

if __name__ == "__main__":
    render_news()

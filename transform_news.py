import os
import json
import re
from datetime import datetime
from bs4 import BeautifulSoup

def extract_stories_from_html(html_file):
    """Extract stories from generated news HTML"""
    with open(html_file, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')
    
    # Extract date
    date_elem = soup.select_one('header p')
    date_str = date_elem.text.strip() if date_elem else datetime.now().strftime("%A, %B %d, %Y")
    
    stories_by_category = {
        'ai': [],
        'products': [],
        'github': [],
        'dev': [],
        'news': []
    }
    
    # Map section headers to categories
    category_map = {
        'AI Company Updates': 'ai',
        'Product Launches': 'products',
        'GitHub Trending': 'github',
        'Developer Tools': 'dev',
        'General Tech News': 'news'
    }
    
    # Extract each section
    sections = soup.find_all('section')
    
    for section in sections:
        section_title = section.find('h2')
        if not section_title:
            continue
            
        category_name = section_title.text.strip()
        category_key = category_map.get(category_name)
        
        if not category_key:
            continue
        
        # Find all cards in this section
        cards = section.find_all('div', class_='card')
        
        for card in cards:
            story = {}
            
            # Title
            title_elem = card.find('h3')
            story['title'] = title_elem.text.strip() if title_elem else ''
            
            # Link(s)
            links = card.find_all('a')
            story['links'] = [{'url': a.get('href', ''), 'text': a.text.strip()} for a in links]
            
            # Content paragraphs
            paragraphs = card.find_all('p', recursive=False)
            story['content'] = [p.text.strip() for p in paragraphs if 'why-matters' not in p.get('class', [])]
            
            # Why it matters
            why_matters = card.find('div', class_='why-matters')
            if why_matters:
                why_text = why_matters.text.replace('Why It Matters:', '').strip()
                story['why_matters'] = why_text
            
            # Takeaways
            takeaways_ul = card.find('ul', class_='takeaways')
            if takeaways_ul:
                story['takeaways'] = [li.text.strip() for li in takeaways_ul.find_all('li')]
            
            stories_by_category[category_key].append(story)
    
    return {
        'date': date_str,
        'categories': stories_by_category
    }

def generate_story_card_html(story):
    """Generate HTML for a single story card"""
    
    # Links
    links_html = '\n'.join([
        f'<a href="{link["url"]}" class="story-link" target="_blank" rel="noopener">{link["text"]}</a><br>'
        for link in story.get('links', [])
    ])
    
    # Content
    content_html = '\n'.join([
        f'<p>{para}</p>'
        for para in story.get('content', [])
    ])
    
    # Why it matters
    why_matters_html = ''
    if story.get('why_matters'):
        why_matters_html = f'''
        <div class="why-matters">
            <h4>Why It Matters</h4>
            <p>{story['why_matters']}</p>
        </div>
        '''
    
    # Takeaways
    takeaways_html = ''
    if story.get('takeaways'):
        takeaways_items = '\n'.join([
            f'<li>{takeaway}</li>'
            for takeaway in story['takeaways']
        ])
        takeaways_html = f'''
        <div class="takeaways">
            <h4>Key Takeaways</h4>
            <ul>
                {takeaways_items}
            </ul>
        </div>
        '''
    
    return f'''
    <div class="story-card">
        <h3 class="story-title">{story.get('title', 'Untitled')}</h3>
        {links_html}
        <div class="story-content">
            {content_html}
        </div>
        {why_matters_html}
        {takeaways_html}
    </div>
    '''

def create_interactive_viewer(stories_data, output_file):
    """Create interactive news viewer from stories data"""
    
    # Read template
    template_path = 'news-viewer-template.html'
    with open(template_path, 'r', encoding='utf-8') as f:
        template = f.read()
    
    # Generate story cards for each category
    category_html = {
        'ai': '',
        'products': '',
        'github': '',
        'dev': '',
        'news': ''
    }
    
    for category, stories in stories_data['categories'].items():
        category_html[category] = '\n'.join([
            generate_story_card_html(story)
            for story in stories
        ])
    
    # Inject stories into template
    html = template
    
    # Replace date
    html = html.replace("document.getElementById('news-date').textContent = allStories.date;",
                       f"document.getElementById('news-date').textContent = '{stories_data['date']}';")
    
    # Inject story HTML
    html = html.replace('id="ai-stories">\n                <!-- Stories will be injected here -->\n            </div>',
                       f'id="ai-stories">\n{category_html["ai"]}\n            </div>')
    
    html = html.replace('id="products-stories">\n                <!-- Stories will be injected here -->\n            </div>',
                       f'id="products-stories">\n{category_html["products"]}\n            </div>')
    
    html = html.replace('id="github-stories">\n                <!-- Stories will be injected here -->\n            </div>',
                       f'id="github-stories">\n{category_html["github"]}\n            </div>')
    
    html = html.replace('id="dev-stories">\n                <!-- Stories will be injected here -->\n            </div>',
                       f'id="dev-stories">\n{category_html["dev"]}\n            </div>')
    
    html = html.replace('id="news-stories">\n                <!-- Stories will be injected here -->\n            </div>',
                       f'id="news-stories">\n{category_html["news"]}\n            </div>')
    
    # Update counts
    for category, stories in stories_data['categories'].items():
        count = len(stories)
        unit = 'repos' if category == 'github' else ('story' if count == 1 else 'stories')
        html = html.replace(f'data-count="{category}">{count} stories</span>',
                          f'data-count="{category}">{count} {unit}</span>')
    
    # Write output
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html)

def update_archive_json(date_str, filename):
    """Update archive.json with new summary"""
    archive_file = 'archive.json'
    
    # Load existing archive
    if os.path.exists(archive_file):
        with open(archive_file, 'r') as f:
            archive = json.load(f)
    else:
        archive = {'summaries': []}
    
    # Parse date
    try:
        date_obj = datetime.strptime(date_str, "%A, %B %d, %Y")
        formatted_date = date_obj.strftime("%Y-%m-%d")
    except:
        formatted_date = datetime.now().strftime("%Y-%m-%d")
    
    # Add new entry (avoid duplicates)
    new_entry = {
        'date': formatted_date,
        'display_date': date_str,
        'file': filename
    }
    
    # Remove if already exists
    archive['summaries'] = [s for s in archive['summaries'] if s['date'] != formatted_date]
    
    # Add and sort by date (newest first)
    archive['summaries'].append(new_entry)
    archive['summaries'].sort(key=lambda x: x['date'], reverse=True)
    
    # Keep only last 30 days
    archive['summaries'] = archive['summaries'][:30]
    
    # Save
    with open(archive_file, 'w') as f:
        json.dump(archive, f, indent=2)
    
    print(f"✅ Archive updated: {len(archive['summaries'])} summaries")

def main():
    """Main process"""
    print("Converting news summary to interactive viewer...")
    
    # Find the latest generated HTML
    source_file = 'output/latest.html'
    
    if not os.path.exists(source_file):
        print(f"❌ Source file not found: {source_file}")
        return
    
    # Extract stories
    print("📖 Extracting stories...")
    stories_data = extract_stories_from_html(source_file)
    
    # Count total stories
    total = sum(len(stories) for stories in stories_data['categories'].values())
    print(f"   Found {total} stories across {len(stories_data['categories'])} categories")
    
    # Create interactive viewer
    print("🎨 Creating interactive viewer...")
    output_file = 'output/latest.html'
    create_interactive_viewer(stories_data, output_file)
    
    # Also create dated version
    timestamp = datetime.now().strftime("%Y-%m-%d")
    dated_file = f'output/news-summary-{timestamp}.html'
    create_interactive_viewer(stories_data, dated_file)
    
    # Update archive
    print("📚 Updating archive...")
    update_archive_json(stories_data['date'], f'output/news-summary-{timestamp}.html')
    
    print(f"✅ Interactive viewer created: {output_file}")
    print(f"✅ Dated version saved: {dated_file}")
    print("🎉 Done!")

if __name__ == "__main__":
    main()

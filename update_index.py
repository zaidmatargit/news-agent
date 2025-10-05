import json
import os

def update_landing_page():
    """Update index.html with latest archive entries"""
    
    # Load archive
    archive_file = 'archive.json'
    if not os.path.exists(archive_file):
        print("❌ archive.json not found - run transform_news.py first")
        return
    
    with open(archive_file, 'r') as f:
        archive = json.load(f)
    
    # Read index.html
    index_file = 'index.html'
    if not os.path.exists(index_file):
        print("❌ index.html not found")
        return
    
    with open(index_file, 'r') as f:
        index_html = f.read()
    
    # Generate archive cards HTML
    archive_html = ""
    for summary in archive['summaries'][:7]:  # Last 7 days
        archive_html += f'''                <a href="./{summary['file']}" class="archive-card">
                    <div class="archive-date">{summary['display_date']}</div>
                    <div class="archive-preview">View comprehensive tech news digest with 20 stories, analysis, and actionable insights.</div>
                </a>
'''
    
    # Find and replace archive section
    start_marker = '<div class="archive-grid" id="archive-list">'
    end_marker = '</div>\n        </div>\n\n        <div class="sources-section">'
    
    if start_marker not in index_html or end_marker not in index_html:
        print("❌ Could not find archive section markers in index.html")
        return
    
    before = index_html.split(start_marker)[0]
    after = index_html.split(end_marker)[1]
    
    new_html = before + start_marker + '\n' + archive_html + '            ' + end_marker + after
    
    # Write back
    with open(index_file, 'w') as f:
        f.write(new_html)
    
    print(f"✅ Landing page updated with {len(archive['summaries'][:7])} recent summaries")

if __name__ == "__main__":
    update_landing_page()

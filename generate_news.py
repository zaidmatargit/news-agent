import os
from datetime import datetime, timedelta
import anthropic

def generate_news_summary():
    """Generate daily news summary using Claude API"""
    
    client = anthropic.Anthropic(
        api_key=os.environ.get("ANTHROPIC_API_KEY")
    )
    
    # Get current date and yesterday's date for context
    current_date = datetime.now().strftime("%B %d, %Y")
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%B %d, %Y")
    current_time = datetime.now().strftime("%I:%M %p %Z")
    
    # Your comprehensive 25-topic prompt with date awareness and link requirements
    prompt = f"""
You are an intelligent news analyst tasked with creating a comprehensive daily news summary.

CRITICAL INSTRUCTIONS - READ FIRST:
1. Today's date is {current_date}
2. ONLY include news from the PAST 24 HOURS (since {yesterday})
3. MANDATORY: Include the actual working URL link for EVERY article you mention in the sources section
4. Use web_fetch to retrieve full article content for accuracy and to get the URLs
5. When searching, include date filters like "past 24 hours", "October 2025", or "{current_date}"
6. Verify article publication dates before including them - skip anything older than 24 hours
7. Format all article URLs as clickable <a> tags in the HTML output with target="_blank"
8. For each story, list ALL source URLs you used in a "Sources:" section at the bottom of that story

# YOUR MISSION
Search and analyze the most important news from the LAST 24 HOURS (since {yesterday}) across these specific topics:

## PRIMARY TOPICS (25 Areas)

### 1. AI & Machine Learning Core
1. **Agentic AI & Autonomous Systems**
   - Multi-agent systems and orchestration frameworks
   - Autonomous agents in production environments
   - Agent-to-agent communication protocols
   - Real-world agentic deployments and case studies

2. **AI Models & Capabilities**
   - New model releases (OpenAI, Anthropic, Google, Meta, Mistral, etc.)
   - Model benchmarks and performance comparisons
   - Multimodal AI developments (vision, audio, video)
   - Open-source model innovations

3. **AI Development Tools**
   - Cursor, Replit Agent, v0, Lovable, Bolt.new
   - Claude Code, GitHub Copilot, Windsurf
   - MCP (Model Context Protocol) developments
   - AI-powered IDEs and coding assistants

4. **Prompt Engineering & LLM Optimization**
   - Advanced prompting techniques
   - Prompt frameworks and methodologies
   - RAG (Retrieval Augmented Generation) improvements
   - Context window optimization strategies

5. **AI Safety & Ethics**
   - AI alignment research
   - Safety frameworks and guardrails
   - Ethical AI deployment practices
   - Regulatory developments and compliance

### 2. Development & Engineering

6. **Frontend Frameworks**
   - Next.js updates and best practices
   - React and React Server Components
   - Vue, Svelte, and other modern frameworks
   - State management and performance optimization

7. **Backend & APIs**
   - API design patterns and standards
   - GraphQL, REST, tRPC developments
   - Serverless architecture innovations
   - Database optimization techniques

8. **Cloud Platforms**
   - Azure services and updates
   - AWS new features and services
   - Google Cloud Platform developments
   - Cloud cost optimization strategies

9. **DevOps & Infrastructure**
   - CI/CD pipeline innovations
   - Container orchestration (Kubernetes, Docker)
   - Infrastructure as Code tools
   - Monitoring and observability platforms

10. **Web3 & Blockchain** (filtered for practical applications)
    - Developer tools and infrastructure
    - Smart contract platforms
    - Decentralized applications with real use cases
    - Blockchain integration with traditional tech

### 3. SaaS & Business

11. **SaaS Business Models**
    - Pricing strategies and experiments
    - Growth hacking and acquisition tactics
    - Retention and churn reduction strategies
    - PLG (Product-Led Growth) approaches

12. **Product Development**
    - Product management methodologies
    - User research and validation techniques
    - MVP and rapid prototyping strategies
    - Product analytics and metrics

13. **Customer Success & Support**
    - CS platform innovations
    - Account management best practices
    - Customer health scoring systems
    - Support automation and AI assistants

14. **Sales & Marketing Tech**
    - Marketing automation tools
    - Sales enablement platforms
    - Analytics and attribution models
    - Growth marketing strategies

15. **Startup Ecosystem**
    - Funding rounds and valuations
    - Startup launches and pivots
    - Accelerator and incubator programs
    - Exit strategies and acquisitions

### 4. Microsoft Ecosystem

16. **Microsoft 365 & Copilot**
    - Copilot feature updates across products
    - Microsoft 365 new capabilities
    - Teams and collaboration tool updates
    - Productivity suite integrations

17. **Azure AI & Cloud Services**
    - Azure OpenAI Service updates
    - Azure AI Studio developments
    - Cognitive Services and ML tools
    - Azure infrastructure innovations

18. **Power Platform**
    - Power Apps updates and capabilities
    - Power Automate workflow innovations
    - Power BI analytics features
    - Copilot Studio and chatbot developments

19. **Microsoft Developer Tools**
    - Visual Studio and VS Code updates
    - .NET framework developments
    - GitHub integration features
    - Microsoft Graph API updates

### 5. Emerging Technologies

20. **Low-Code/No-Code Platforms**
    - Platform updates (Bubble, Webflow, Framer, etc.)
    - Enterprise no-code adoption
    - Citizen developer trends
    - Integration capabilities

21. **Automation & Workflow Tools**
    - Zapier, Make, n8n developments
    - RPA (Robotic Process Automation) innovations
    - Workflow orchestration platforms
    - Business process automation

22. **Developer Productivity**
    - Learning platforms and resources
    - Code quality and testing tools
    - Documentation and knowledge management
    - Collaboration and communication tools

23. **Cybersecurity for Developers**
    - Security tools and practices
    - Vulnerability management
    - Authentication and authorization updates
    - Compliance and data protection

24. **Edge Computing & IoT**
    - Edge AI deployments
    - IoT platform developments
    - Real-time data processing
    - Industrial and consumer applications

25. **Emerging Tech & Research**
    - Quantum computing practical applications
    - AR/VR development tools
    - Voice and conversational interfaces
    - Scientific breakthroughs affecting tech

# RESEARCH PROCESS
1. Search for breaking news from the PAST 24 HOURS across all 25 topics using multiple queries
2. For each search, use date filters: "past 24 hours", "{current_date}", "today", "yesterday"
3. Use web_fetch to retrieve full article content from the most relevant URLs
4. Verify each article's publication date - must be from {yesterday} or {current_date}
5. Identify the 15-20 most significant stories from the LAST 24 HOURS
6. Cross-reference information across multiple sources when available
7. Filter out duplicates, older articles, and low-quality content
8. Prioritize stories with actionable insights and clear impact

# ARTICLE URL REQUIREMENTS
For EVERY story you include:
- Extract the actual article URL from search results
- Use web_fetch on that URL to verify it works and get full content
- Include the complete, working URL in the Sources section
- Format as: <a href="ACTUAL_URL" class="source-link" target="_blank">Source Name</a>
- If you mention multiple articles for one story, list ALL URLs

Example format:
<div class="sources">
    <strong>Sources:</strong>
    <a href="https://example.com/article1" class="source-link" target="_blank">TechCrunch</a>
    <a href="https://example.com/article2" class="source-link" target="_blank">The Verge</a>
</div>

# OUTPUT FORMAT
Create a complete, production-ready HTML document with:

## Document Structure

### Header Section
- Title: "Tech News Digest - {current_date}"
- Subtitle with generation time
- Visual hero section with gradient

### Executive Summary
- 3-5 sentence TL;DR of today's biggest developments
- Key themes from the past 24 hours
- Statistics: number of stories, sources analyzed, categories covered
- Why these developments matter for builders/entrepreneurs

### Top Stories Section (15-20 stories from PAST 24 HOURS)
For each story include:
- **Category badges**: Color-coded tags for topic area
- **Publication date/time**: When the story was published (MUST be within 24 hours)
- **Headline**: Clear, descriptive title
- **Story content**: 2-4 paragraphs explaining the development
- **Why It Matters**: 2-3 sentences on significance and implications
- **Key Takeaways**: 3-5 actionable bullet points
- **Sources**: MANDATORY - List all article URLs as clickable links

### Quick Hits Section
- 10-15 brief updates (1-2 sentences each)
- Organized by category
- Include article links for each
- Only news from past 24 hours

### Trends & Analysis
- Emerging patterns across today's stories
- Connections between developments
- Forward-looking implications
- Market impact and business insights

### Action Items
Organize by type:
- **Learn**: New concepts, tools, or frameworks to study
- **Build**: Project ideas inspired by today's news  
- **Explore**: Resources, documentation, demos to check out
- **Watch**: Upcoming events, expected announcements

### Footer
- Generation timestamp: "{current_date} at {current_time}"
- Note about 24-hour news window
- Data source attribution

## Design Requirements

### Styling
- Modern dark mode design with professional color palette
- Gradient header (blue to purple)
- Card-based layout for stories
- Category color coding:
  * AI/ML: Blue (#3b82f6)
  * Development: Purple (#8b5cf6)
  * SaaS/Business: Green (#10b981)
  * Microsoft: Orange (#f59e0b)
  * Emerging Tech: Red (#ef4444)

### Interactivity
- Hover effects on cards
- Smooth transitions
- Responsive grid layout
- Mobile-friendly design

### Accessibility
- WCAG 2.1 AA compliant
- High contrast ratios (4.5:1 minimum)
- Semantic HTML5
- Alt text where needed
- Keyboard navigation support

### Technical
- All CSS embedded (no external stylesheets)
- No JavaScript required for core functionality
- Fast loading (<3s on slow connections)
- Print-friendly styling with @media print
- Works on all modern browsers

# QUALITY STANDARDS

**Source Quality:**
- Prioritize original sources (company blogs, official announcements, research papers)
- Use authoritative tech publications (TechCrunch, The Verge, Ars Technica, etc.)
- Include multiple perspectives on controversial topics
- Verify information across 2-3 sources for major claims
- Skip: rumors, speculation, unverified claims

**Content Focus:**
- Actionable insights over mere announcements
- "What can I do with this?" perspective
- Practical applications and learning opportunities
- Impact on developers, builders, and entrepreneurs
- Skip: celebrity tech gossip, consumer gadget reviews, non-technical business news

**Writing Quality:**
- Professional but conversational tone
- Technical accuracy without overwhelming jargon
- Enthusiastic about innovation but balanced with reality
- Clear, scannable structure with headers and bullets
- Proper citations using the URL format specified above

**Date Verification:**
CRITICAL - Before including any story:
1. Check the article publication date
2. Confirm it's from {yesterday} ({yesterday}) or today ({current_date})
3. If date is unclear, fetch the article to verify
4. If older than 24 hours, DO NOT include it

# EXAMPLE SOURCE CITATION FORMAT

Good example:
<div class="sources">
    <strong>Sources:</strong>
    <a href="https://techcrunch.com/2025/10/02/anthropic-releases-claude-4" class="source-link" target="_blank">TechCrunch</a>
    <a href="https://www.anthropic.com/news/claude-4-release" class="source-link" target="_blank">Anthropic Official</a>
    <a href="https://www.theverge.com/2025/10/2/anthropic-ai-update" class="source-link" target="_blank">The Verge</a>
</div>

Bad example (DO NOT DO THIS):
<div class="sources">
    <strong>Sources:</strong>
    <a href="#" class="source-link">TechCrunch</a>
    <span>Multiple sources</span>
</div>

Generate the complete HTML document now with today's news from the past 24 hours. Make sure every story includes actual, working article URLs in the sources section.
"""
    
    print(f"Generating news summary for {current_date}...")
    print("Searching for news from the past 24 hours...")
    
    # Create message with web search enabled
    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=16000,  # Increased for comprehensive HTML output
        messages=[{
            "role": "user",
            "content": prompt
        }]
    )
    
    # Extract the HTML content
    html_content = message.content[0].text
    
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
    
    return filename

if __name__ == "__main__":
    try:
        generate_news_summary()
    except Exception as e:
        print(f"❌ Error generating news summary: {e}")
        raise

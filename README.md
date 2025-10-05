# 📰 AI-Powered Daily News Agent

Automatically generates comprehensive daily news summaries covering 25 technology topics including AI, development tools, SaaS, Microsoft ecosystem, and emerging tech.

## ✨ Features

- **Automated Daily Summaries**: Runs via GitHub Actions every day at 7 AM UTC
- **25 Topic Categories**: Comprehensive coverage of AI, development, business, and emerging tech
- **Last 24 Hours Only**: Always fresh news from the past day
- **Source Links**: Every article includes working URLs to original sources
- **Beautiful HTML Output**: Modern dark-mode design with category color-coding
- **Actionable Insights**: Key takeaways and action items for builders and developers

## 🚀 Quick Start

### 1. Fork/Clone This Repository

```bash
git clone https://github.com/YOUR_USERNAME/news-agent.git
cd news-agent
```

### 2. Set Up Anthropic API Key

1. Get your API key from [Anthropic Console](https://console.anthropic.com/)
2. Go to your GitHub repository **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Add:
   - **Name**: `ANTHROPIC_API_KEY`
   - **Value**: Your Anthropic API key

### 3. Enable GitHub Actions

1. Go to the **Actions** tab in your repository
2. Click **I understand my workflows, go ahead and enable them**
3. The workflow will run automatically at 7 AM UTC daily

### 4. Manual Run (Optional)

To generate a summary immediately:
1. Go to **Actions** tab
2. Click **Daily News Summary** workflow
3. Click **Run workflow** → **Run workflow**
4. Wait 2-3 minutes for completion
5. Check the `output/` folder for your HTML summary

## 📁 Project Structure

```
news-agent/
├── .github/
│   └── workflows/
│       └── news-summary.yml       # GitHub Actions workflow
├── output/
│   ├── latest.html                # Most recent summary
│   └── news-summary-YYYY-MM-DD.html  # Daily archives
├── generate_news.py               # Main script
├── requirements.txt               # Python dependencies
└── README.md                      # This file
```

## 📋 Topics Covered

### AI & Machine Learning (5 topics)
1. Agentic AI & Autonomous Systems
2. AI Models & Capabilities
3. AI Development Tools
4. Prompt Engineering & LLM Optimization
5. AI Safety & Ethics

### Development & Engineering (5 topics)
6. Frontend Frameworks
7. Backend & APIs
8. Cloud Platforms
9. DevOps & Infrastructure
10. Web3 & Blockchain

### SaaS & Business (5 topics)
11. SaaS Business Models
12. Product Development
13. Customer Success & Support
14. Sales & Marketing Tech
15. Startup Ecosystem

### Microsoft Ecosystem (4 topics)
16. Microsoft 365 & Copilot
17. Azure AI & Cloud Services
18. Power Platform
19. Microsoft Developer Tools

### Emerging Technologies (6 topics)
20. Low-Code/No-Code Platforms
21. Automation & Workflow Tools
22. Developer Productivity
23. Cybersecurity for Developers
24. Edge Computing & IoT
25. Emerging Tech & Research

## ⚙️ Customization

### Change Schedule

Edit `.github/workflows/news-summary.yml`:

```yaml
schedule:
  # Daily at 7 AM UTC
  - cron: '0 7 * * *'
  
  # Every 6 hours
  - cron: '0 */6 * * *'
  
  # Twice daily (7 AM and 7 PM UTC)
  - cron: '0 7,19 * * *'
```

Use [crontab.guru](https://crontab.guru/) to create custom schedules.

### Modify Topics

Edit `generate_news.py` and adjust the topic list in the prompt section.

### Change Styling

The HTML output has embedded CSS. Modify the `:root` variables in the `<style>` section to change colors:

```css
:root {
    --bg-primary: #0f172a;      /* Dark background */
    --accent-blue: #3b82f6;     /* AI topics */
    --accent-purple: #8b5cf6;   /* Development */
    --accent-green: #10b981;    /* SaaS/Business */
    --accent-orange: #f59e0b;   /* Microsoft */
    --accent-red: #ef4444;      /* Emerging Tech */
}
```

## 🌐 View Online (Optional)

Enable GitHub Pages to view summaries in your browser:

1. Go to **Settings** → **Pages**
2. Under **Source**, select **Deploy from a branch**
3. Select branch: `main`
4. Select folder: `/output`
5. Click **Save**

Your summaries will be available at:
`https://YOUR_USERNAME.github.io/news-agent/latest.html`

## 💰 Cost Estimate

- **Claude API**: ~$0.50-1.50 per summary (depends on news volume)
- **Daily**: ~$15-45/month
- **Every 6 hours**: ~$60-180/month
- **GitHub Actions**: Free (2000 minutes/month for private repos)

## 🛠️ Local Development

### Run Locally

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variable
export ANTHROPIC_API_KEY="your-api-key-here"

# Generate summary
python generate_news.py

# View output
open output/latest.html
```

### Test Changes

Before committing, test your prompt changes locally to ensure they work as expected.

## 📊 Output Features

Each daily summary includes:

- **Executive Summary**: TL;DR of the day's biggest developments
- **15-20 Detailed Stories**: Full context, analysis, and implications
- **Quick Hits**: 10-15 brief updates across categories
- **Trends & Insights**: Patterns and forward-looking analysis
- **Action Items**: Organized by Learn, Build, Explore, and Watch
- **Source Links**: Every article includes working URLs
- **Stats Dashboard**: Stories count, sources analyzed, topics covered

## 🤝 Contributing

Feel free to:
- Add new topic categories
- Improve the HTML design
- Enhance the analysis quality
- Share your customizations

## 📝 License

MIT License - Feel free to use and modify for your own needs.

## 🙏 Credits

Built with:
- [Anthropic Claude API](https://www.anthropic.com/) - AI-powered analysis
- [GitHub Actions](https://github.com/features/actions) - Automation
- Modern web standards - Beautiful HTML/CSS

## 📮 Questions?

Open an issue or reach out if you need help getting started!

---

**Generated with ❤️ by your AI News Agent**

# Quick Start Guide

## 🚀 Get Started in 3 Steps

### Step 1: Install Dependencies

```bash
cd /Users/nithinyanna/Downloads/ai-job-source-agent
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Step 2: Set Up API Keys

1. Copy the example environment file:
```bash
cp .env.example .env
```

2. Edit `.env` and add your API keys:
   - **Required**: Get Scrapin API key: https://scrapin.io/
   - **Optional**: Get SerpAPI key: https://serpapi.com/ (for automatic job search)

```bash
SCRAPIN_API_KEY=your_actual_key_here
SERPAPI_KEY=your_optional_key_here  # Optional
```

⚠️ **Note**: Proxycurl has been shut down (January 2025). You don't need it anymore.

### Step 3: Run the Agent

**Recommended Method** - Use a direct LinkedIn job URL:

```python
from job_source_agent import JobSourceAgent
import os
from dotenv import load_dotenv

load_dotenv()

agent = JobSourceAgent(scrapin_api_key=os.getenv("SCRAPIN_API_KEY"))
result = agent.run_from_job_url('https://www.linkedin.com/jobs/view/123/')
print(result)
```

Or use the example script:
```bash
python example_usage.py
```

## 📋 Expected Output

```
============================================================
Starting Job Source Agent Pipeline
============================================================
Discovering job listings for keyword: software engineer
Found 5 job listings
Processing job: https://www.linkedin.com/jobs/view/123/
Extracting company data from: https://www.linkedin.com/jobs/view/123/
Extracted company: Notion, website: https://www.notion.so
Finding career page for: https://www.notion.so
Found career page: https://www.notion.so/careers
Extracting job posting from: https://www.notion.so/careers
Found job posting: https://www.notion.so/jobs/backend-engineer
============================================================
Pipeline Complete
Company: Notion
Career Page: https://www.notion.so/careers
Open Position: https://www.notion.so/jobs/backend-engineer
============================================================

RESULTS
============================================================
company_name: Notion
career_page_url: https://www.notion.so/careers
open_position_url: https://www.notion.so/jobs/backend-engineer
linkedin_job_url: https://www.linkedin.com/jobs/view/123/
company_website: https://www.notion.so
============================================================
```

## 🔍 Troubleshooting

### Issue: "No job listings found"
- If using automatic search: Check your SerpAPI key is correct
- **Recommended**: Use `run_from_job_url()` with a direct LinkedIn job URL instead
- Verify you have API credits available (if using SerpAPI)

### Issue: "Failed to extract company data"
- Check your Scrapin API key is correct
- Verify the LinkedIn job URL is valid and accessible
- Check API rate limits
- Make sure the job URL is a valid LinkedIn job posting URL

### Issue: "Career page not found"
- Some companies may not have public career pages
- The agent will return partial results (company name + website)

### Issue: "No job postings found"
- The career page may use JavaScript to load jobs
- Some companies may not list jobs on their career page
- Try a different job listing

## 💡 Tips

- Start with common job keywords like "software engineer" or "data scientist"
- The agent processes the first job from search results
- You can modify `page_size` to get more job options
- Check the logs for detailed information about each step


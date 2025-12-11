# 🆓 100% FREE Pipeline - $0 Cost!

## Overview

This is a **completely free** implementation that uses:
- ✅ LinkedIn's public guest endpoints (no API keys)
- ✅ Free local LLM (Ollama)
- ✅ Optional Scrapin free tier (100 calls/day)
- ✅ No paid APIs, no proxies, no costs!

## Pipeline Architecture

```
Step 1: FREE LinkedIn Job Discovery
  └─→ LinkedIn Public Guest API (https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search)
      ✅ No login needed
      ✅ No API key required
      ✅ 100% legal and free

Step 2: FREE Company Website Extraction
  ├─→ Method 1: Parse LinkedIn job page HTML directly
  ├─→ Method 2: Navigate to company page and extract
  └─→ Method 3: Scrapin FREE tier (100 calls/day) - OPTIONAL

Step 3: FREE LLM Web Navigator
  └─→ Ollama (local LLM) intelligently finds career page
      ✅ Runs locally
      ✅ No API costs
      ✅ Privacy-friendly

Step 4: Extract Job Posting
  └─→ Traditional web scraping (free)

Step 5: Store in Postgres (optional)
  └─→ Local database (free)
```

## Installation

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Install Playwright (for better reliability)

```bash
pip install playwright
playwright install chromium
```

### 3. Install Ollama (FREE local LLM)

```bash
# macOS/Linux
curl -fsSL https://ollama.ai/install.sh | sh

# Or download from: https://ollama.ai/
```

### 4. Download a Model

```bash
ollama pull llama3  # or llama2, mistral, etc.
```

## Usage

### Basic Usage (100% Free)

```python
from job_source_agent_free import FreeJobSourceAgent

# Initialize - NO API keys needed!
agent = FreeJobSourceAgent(
    use_playwright=True  # More reliable than requests
)

# Run FREE pipeline
results = agent.run_free_pipeline(
    keyword="software engineer",
    location="United States",
    max_jobs=10
)

# Results include:
# - LinkedIn job URLs
# - Company names
# - Company websites
# - Career page URLs
# - Open position URLs
```

### With Optional Scrapin Free Tier

```python
import os
from dotenv import load_dotenv
load_dotenv()

agent = FreeJobSourceAgent(
    scrapin_api_key=os.getenv("SCRAPIN_API_KEY"),  # Optional - 100 free calls/day
    use_playwright=True
)

results = agent.run_free_pipeline(
    keyword="data scientist",
    location="San Francisco",
    max_jobs=5
)
```

### With LLM Navigation (Ollama)

```python
agent = FreeJobSourceAgent(
    ollama_base_url="http://localhost:11434",  # Local Ollama
    use_playwright=True
)

# LLM will intelligently find career pages
results = agent.run_free_pipeline(
    keyword="backend engineer",
    max_jobs=5
)
```

## LinkedIn Public API Endpoint

The free pipeline uses LinkedIn's public guest endpoint:

```
GET https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search
?keywords=software+engineer
&location=United+States
&start=0
```

**Response:** HTML with job cards containing:
- Job URLs (`/jobs/view/123456789/`)
- Job titles
- Company names
- Locations

**Why it's free:**
- LinkedIn uses this endpoint for infinite scroll
- It's intended for public guest access
- No authentication required
- No rate limits (be respectful!)

## Methods Comparison

### Method 1: Requests + BeautifulSoup (Simplest)

```python
agent = FreeJobSourceAgent(use_playwright=False)
results = agent.run_free_pipeline(keyword="engineer")
```

**Pros:**
- ✅ No browser needed
- ✅ Fast
- ✅ Simple

**Cons:**
- ⚠️ May be blocked occasionally
- ⚠️ Less reliable than Playwright

### Method 2: Playwright (Recommended)

```python
agent = FreeJobSourceAgent(use_playwright=True)
results = agent.run_free_pipeline(keyword="engineer")
```

**Pros:**
- ✅ More reliable
- ✅ Handles JavaScript
- ✅ Better at avoiding blocks

**Cons:**
- ⚠️ Requires browser installation
- ⚠️ Slightly slower

## Company Website Extraction

### Method 1: Parse LinkedIn Job Page (FREE)

Extracts company name and website directly from job page HTML.

### Method 2: Navigate to Company Page (FREE)

1. Get company LinkedIn URL from job page
2. Navigate to company page
3. Extract website from company page HTML

### Method 3: Scrapin Free Tier (OPTIONAL)

- 100 API calls/day
- More reliable extraction
- Still free!

## LLM Web Navigator (Ollama)

The agent uses Ollama (local LLM) to intelligently find career pages:

1. Extracts all links from company website
2. Sends to Ollama with prompt: "Which link is the careers page?"
3. LLM analyzes and suggests most likely career page
4. Agent navigates to suggested page

**Benefits:**
- ✅ No API costs
- ✅ Runs locally
- ✅ Privacy-friendly
- ✅ No rate limits

## Rate Limiting

The free pipeline includes built-in rate limiting:
- 1-2 second delays between requests
- Respects LinkedIn's servers
- Prevents blocking

## Cost Breakdown

| Component | Cost |
|-----------|------|
| LinkedIn Public API | $0 (free) |
| Company extraction | $0 (HTML parsing) |
| LLM navigation | $0 (Ollama local) |
| Web scraping | $0 (requests/Playwright) |
| **Total** | **$0** |

## Limitations

1. **Scrapin Free Tier**: 100 calls/day (optional)
2. **Rate Limiting**: Be respectful to LinkedIn
3. **Ollama**: Requires local installation
4. **Playwright**: Requires browser installation

## Troubleshooting

### Issue: "No jobs found"

**Solution:**
- Try different keywords
- Check if LinkedIn changed their HTML structure
- Use Playwright instead of requests

### Issue: "Ollama not found"

**Solution:**
```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Download model
ollama pull llama3

# Verify it's running
ollama list
```

### Issue: "Playwright browser not found"

**Solution:**
```bash
playwright install chromium
```

### Issue: "Company website not extracted"

**Solution:**
- Use Scrapin free tier (100 calls/day)
- Or manually provide company website
- Check if company page is accessible

## Best Practices

1. **Use Playwright** for better reliability
2. **Install Ollama** for intelligent navigation
3. **Add Scrapin free tier** for better company extraction (optional)
4. **Respect rate limits** - add delays between requests
5. **Store results** in Postgres for tracking

## Example Output

```python
[
  {
    "linkedin_job_url": "https://www.linkedin.com/jobs/view/123456789/",
    "company_name": "Notion",
    "company_website": "https://www.notion.so",
    "career_page_url": "https://www.notion.so/careers",
    "open_position_url": "https://www.notion.so/jobs/backend-engineer",
    "title": "Software Engineer",
    "location": "San Francisco, CA",
    "source": "free_pipeline"
  }
]
```

## Comparison: Free vs Paid

| Feature | Free Pipeline | Paid Pipeline |
|---------|---------------|---------------|
| Job Discovery | ✅ LinkedIn Public API | ✅ Scrapin/SerpAPI |
| Company Extraction | ✅ HTML Parsing | ✅ Scrapin API |
| LLM Navigation | ✅ Ollama (local) | ✅ OpenAI API |
| Cost | **$0** | **$$$** |
| Reliability | Good | Excellent |
| Rate Limits | None (be respectful) | API limits |

## Next Steps

1. **Install dependencies**: `pip install -r requirements.txt`
2. **Install Playwright**: `playwright install chromium`
3. **Install Ollama**: `curl -fsSL https://ollama.ai/install.sh | sh`
4. **Run the pipeline**: `python job_source_agent_free.py`

## Files

- `job_source_agent_free.py` - Free pipeline implementation
- `FREE_PIPELINE.md` - This documentation
- `.env.example` - Updated with free options only

Enjoy your **$0 cost** job discovery pipeline! 🎉


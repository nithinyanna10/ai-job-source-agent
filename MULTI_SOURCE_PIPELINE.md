# 🔄 Hybrid Multi-Source Discovery Pipeline

## Overview

This agent implements a **failover/redundancy system** for job discovery, just like real AI intelligence platforms. If one source fails, it automatically tries the next.

## Pipeline Architecture

```
Step 1: Find LinkedIn Job URLs (with failover)
  ├─→ Try Scrapin Job Search API (PRIMARY - BEST) ✅
  ├─→ Try SerpAPI (FALLBACK 1) ✅
  ├─→ Try PhantomBuster (FALLBACK 2) ✅
  └─→ Try Direct HTML Scraping (LAST RESORT) ⚠️

Step 2: Extract Company Data
  └─→ Scrapin API extracts company name + website

Step 3: LLM Web Navigator
  └─→ Crawls company website to find career page

Step 4: Extract Job Posting
  └─→ Gets one open position URL from career page

Step 5: Store in Postgres
  └─→ Saves all results to database
```

## Source Details

### 1. Scrapin Job Search API (PRIMARY - BEST) ⭐

**Why it's best:**
- ✅ Most reliable
- ✅ Direct LinkedIn job search
- ✅ Returns full job details
- ✅ No rate limit issues
- ✅ Clean API response

**Endpoint:**
```
GET https://api.scrapin.io/linkedin/search/jobs
?keyword=software+engineer
&location=United+States
&limit=100
&apikey=YOUR_KEY
```

**Response:**
```json
[
  {
    "job_id": "123",
    "job_url": "https://www.linkedin.com/jobs/view/123/",
    "company_name": "Notion",
    "company_linkedin_url": "https://www.linkedin.com/company/notion/",
    "company_website": "https://www.notion.so",
    "role": "Software Engineer",
    "location": "San Francisco, CA",
    "date_posted": "2025-01-10"
  }
]
```

### 2. SerpAPI (FALLBACK 1) 🔄

**Why it's good:**
- ✅ 100% legal
- ✅ Extremely stable
- ✅ Good rate limits
- ✅ Reliable fallback

**Endpoint:**
```
GET https://serpapi.com/search
?engine=linkedin_jobs
&q=software+engineer
&location=United+States
&api_key=YOUR_KEY
```

**Response:**
```json
{
  "jobs_results": [
    {
      "link": "https://www.linkedin.com/jobs/view/123/",
      "title": "Software Engineer",
      "company_name": "Notion",
      "location": "San Francisco, CA"
    }
  ]
}
```

### 3. PhantomBuster (FALLBACK 2) 🔄

**Why it's useful:**
- ✅ Scheduled automation
- ✅ User-friendly
- ✅ Can run on schedule
- ✅ Exports to JSON

**Setup:**
1. Create PhantomBuster account
2. Set up "LinkedIn Job Search Export" agent
3. Configure with keyword + location
4. Get API key and agent ID

**Usage:**
- Can trigger agent via API
- Or fetch from scheduled export JSON feed

### 4. Direct HTML Scraping (LAST RESORT) ⚠️

**Why it's last resort:**
- ⚠️ LinkedIn blocks headless browsers
- ⚠️ Requires rotating proxies
- ⚠️ Breaks frequently
- ⚠️ May violate ToS

**Only use when:**
- All APIs have failed
- You have residential proxies
- You understand the risks

## Usage Examples

### Basic Usage (Auto-failover)

```python
from job_source_agent import JobSourceAgent
import os
from dotenv import load_dotenv

load_dotenv()

agent = JobSourceAgent(
    scrapin_api_key=os.getenv("SCRAPIN_API_KEY"),
    serpapi_key=os.getenv("SERPAPI_KEY"),  # Optional
    phantombuster_key=os.getenv("PHANTOMBUSTER_KEY"),  # Optional
    phantombuster_agent_id=os.getenv("PHANTOMBUSTER_AGENT_ID")  # Optional
)

# Run full pipeline - automatically tries all sources
results = agent.run_full_pipeline(
    keyword="software engineer",
    location="United States",
    limit=10
)
```

### With Postgres Storage

```python
postgres_config = {
    "host": "localhost",
    "port": 5432,
    "database": "job_discoveries",
    "user": "postgres",
    "password": "your_password"
}

agent = JobSourceAgent(
    scrapin_api_key=os.getenv("SCRAPIN_API_KEY"),
    postgres_config=postgres_config
)

# Results automatically stored in Postgres
results = agent.run_full_pipeline(keyword="data scientist")
```

### Manual Source Selection

```python
# Try only Scrapin
jobs = agent.discover_job_listings_scrapin("engineer", "US", limit=50)

# Try only SerpAPI
jobs = agent.discover_job_listings_serpapi("engineer", "US")

# Try only PhantomBuster
jobs = agent.discover_job_listings_phantombuster("engineer", "US")

# Try only direct scraping (not recommended)
jobs = agent.discover_job_listings_direct_scraping("engineer", "US")
```

## Failover Behavior

The agent automatically tries sources in this order:

1. **Scrapin** → If fails or returns empty
2. **SerpAPI** → If Scrapin fails
3. **PhantomBuster** → If SerpAPI fails
4. **Direct Scraping** → If all APIs fail

**Logs show:**
```
🔍 [Scrapin] Discovering job listings...
❌ [Scrapin] Error: Rate limit exceeded
⚠️  Scrapin failed, trying SerpAPI...
🔍 [SerpAPI] Discovering job listings...
✅ [SerpAPI] Found 25 job listings
✅ Success via SerpAPI: 25 jobs found
```

## Postgres Schema

The agent creates this table automatically:

```sql
CREATE TABLE job_discoveries (
    id SERIAL PRIMARY KEY,
    linkedin_job_url TEXT,
    company_name TEXT,
    company_website TEXT,
    career_page_url TEXT,
    open_position_url TEXT,
    discovered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    source TEXT,
    metadata JSONB
);
```

## Best Practices

1. **Always use Scrapin as primary** - It's the most reliable
2. **Set up SerpAPI as fallback** - Good insurance
3. **PhantomBuster for scheduled jobs** - If you need automation
4. **Avoid direct scraping** - Only as last resort
5. **Use Postgres for storage** - Track all discoveries
6. **Rate limiting** - Add delays between requests

## Error Handling

The pipeline handles errors gracefully:

- ✅ API failures → Try next source
- ✅ Missing data → Skip job, continue
- ✅ Network errors → Retry with exponential backoff
- ✅ Postgres errors → Log but continue processing

## Performance

- **Scrapin**: ~1-2 seconds per request
- **SerpAPI**: ~2-3 seconds per request
- **PhantomBuster**: ~5-10 seconds (if triggering agent)
- **Direct Scraping**: ~3-5 seconds (if not blocked)

**Total pipeline time:** ~5-10 seconds per job (including company extraction, career page finding, etc.)

## Cost Considerations

- **Scrapin**: Pay per request (check pricing)
- **SerpAPI**: 100 free searches/month, then paid
- **PhantomBuster**: Subscription-based
- **Direct Scraping**: Free but risky

**Recommendation:** Use Scrapin as primary (most cost-effective for reliability).


# ⚠️ Proxycurl Shutdown Notice

## What Happened?

**Proxycurl has been shut down in January 2025** following a lawsuit from LinkedIn/Microsoft.

From the Proxycurl team:
> "In January earlier this year (2025), LinkedIn filed a lawsuit against Proxycurl. Today, we are shutting Proxycurl down. Regardless of the merits of LinkedIn's lawsuit, there is no winning in fighting this."

## Impact on This Project

The original AI Job Source Agent relied on Proxycurl for discovering LinkedIn job listings. The code has been **updated to work without Proxycurl**.

## ✅ Updated Solution

The agent now supports **three methods**:

### 1. **Direct LinkedIn Job URL** (Recommended)
```python
agent.run_from_job_url('https://www.linkedin.com/jobs/view/123/')
```
- **No job search API needed**
- Just provide a LinkedIn job URL you found manually
- Most reliable and cost-effective

### 2. **Company Website** (Skip LinkedIn)
```python
agent.run_from_company_website('https://www.notion.so', 'Notion')
```
- Skip LinkedIn entirely
- Directly find career page from company website

### 3. **SerpAPI** (Optional Alternative)
```python
agent.run(keyword="software engineer")
```
- Requires SerpAPI key (optional)
- Automatically searches for jobs
- Get your key: https://serpapi.com/

## 🔄 Migration Guide

### Old Code (No longer works):
```python
agent = JobSourceAgent(proxycurl_key, scrapin_key)
result = agent.run(keyword="software engineer")
```

### New Code (Recommended):
```python
agent = JobSourceAgent(scrapin_api_key=scrapin_key)
# Method 1: Direct URL
result = agent.run_from_job_url('https://www.linkedin.com/jobs/view/123/')

# Method 2: Company website
result = agent.run_from_company_website('https://company.com', 'Company Name')

# Method 3: Auto search (requires SerpAPI)
agent = JobSourceAgent(scrapin_api_key=scrapin_key, serpapi_key=serpapi_key)
result = agent.run(keyword="software engineer")
```

## 📋 Updated Requirements

- ✅ **Scrapin API Key** (REQUIRED) - Still active and working
- ⚠️ **SerpAPI Key** (OPTIONAL) - Only if you want automatic job search
- ❌ **Proxycurl API Key** (NO LONGER NEEDED) - Service shut down

## 💡 Best Practice

**For most use cases, use Method 1** (direct LinkedIn job URL):
1. Manually find LinkedIn job URLs (via LinkedIn search)
2. Pass them to `run_from_job_url()`
3. Agent extracts company data and finds career pages

This is:
- ✅ Most reliable
- ✅ No additional API costs
- ✅ Works immediately
- ✅ No rate limits from job search APIs

## 🔗 Alternative Services

If you need automatic job search, consider:
- **SerpAPI** - https://serpapi.com/ (LinkedIn Jobs API)
- **Bright Data** - https://brightdata.com/ (Web scraping platform)
- **ScraperAPI** - https://www.scraperapi.com/ (General scraping)

However, **manual URL input is recommended** for best results.

## 📞 Support

If you have questions about the migration, check:
- Updated `README.md` for usage examples
- `API_KEYS.md` for required keys
- `example_usage.py` for code examples


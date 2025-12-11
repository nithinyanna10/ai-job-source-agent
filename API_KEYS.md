# 🔑 Required API Keys

## ⚠️ IMPORTANT UPDATE (January 2025)

**Proxycurl has been shut down** due to a lawsuit from LinkedIn. The agent has been updated to work without Proxycurl.

## 📋 API Keys List

### 1. **Scrapin API Key** (REQUIRED)
- **Purpose**: Extract company name and website from LinkedIn job posts
- **API Service**: [Scrapin](https://scrapin.io/)
- **What it does**: Extracts company data (name, website, LinkedIn profile) from job URLs
- **Environment Variable**: `SCRAPIN_API_KEY`
- **Get your key**: https://scrapin.io/
- **Documentation**: https://scrapin.io/docs

---

## 🚀 Quick Setup

1. **Get your API keys** from the links above
   - **Required**: Scrapin API key
   - **Optional**: SerpAPI key (for automatic job search)

2. **Create `.env` file**:
   ```bash
   cp .env.example .env
   ```

3. **Add your keys to `.env`**:
   ```bash
   SCRAPIN_API_KEY=your_actual_scrapin_key_here
   SERPAPI_KEY=your_actual_serpapi_key_here  # Optional
   ```

4. **Verify setup**:
   ```bash
   python job_source_agent.py
   ```

---

## 📝 API Key Details

### Scrapin API
- **Endpoint**: `https://api.scrapin.io/linkedin/job`
- **Authentication**: API key in query parameter (`?key=YOUR_KEY`)
- **Rate Limits**: Check your plan at https://scrapin.io/pricing
- **Free Tier**: Available (limited requests)

### SerpAPI (Optional)
- **Endpoint**: `https://serpapi.com/search`
- **Authentication**: API key in query parameter (`?api_key=YOUR_KEY`)
- **Rate Limits**: Check your plan at https://serpapi.com/pricing
- **Free Tier**: 100 searches/month

---

## ⚠️ Important Notes

- **Never commit your `.env` file** to version control (it's in `.gitignore`)
- **Keep your API keys secure** - don't share them publicly
- **Check rate limits** - both services have usage limits based on your plan
- **Free tiers available** - both services offer free tiers for testing

---

## 🔍 Testing Your Keys

You can test if your keys work by running:

```bash
python -c "
import os
from dotenv import load_dotenv
load_dotenv()

scrapin = os.getenv('SCRAPIN_API_KEY')
serpapi = os.getenv('SERPAPI_KEY')

print('✅ SCRAPIN_API_KEY:', 'Set' if scrapin else '❌ Missing (REQUIRED)')
print('✅ SERPAPI_KEY:', 'Set' if serpapi else '⚠️  Not set (Optional)')
"
```

---

## 💡 Usage Methods

The agent now supports multiple ways to find jobs:

### Method 1: Direct LinkedIn Job URL (Recommended)
```python
agent.run_from_job_url('https://www.linkedin.com/jobs/view/123/')
```
- No job search API needed
- Just provide a LinkedIn job URL you found manually
- Most reliable method

### Method 2: Company Website
```python
agent.run_from_company_website('https://www.notion.so', 'Notion')
```
- Skip LinkedIn entirely
- Directly find career page from company website

### Method 3: Automatic Search (requires SerpAPI)
```python
agent.run(keyword="software engineer")
```
- Requires SerpAPI key
- Automatically searches for jobs
- Less reliable than manual URL input

## ⚠️ Important Notes

- **Proxycurl is shut down** - Do not try to use it
- **Scrapin is still active** - Required for extracting company data from LinkedIn URLs
- **SerpAPI is optional** - Only needed if you want automatic job search
- **Manual URLs work best** - For most reliable results, provide LinkedIn job URLs directly


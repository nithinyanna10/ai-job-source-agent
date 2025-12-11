# AI Job Source Agent

An autonomous agent that extracts company information from LinkedIn job listings, navigates to career pages, and retrieves open position URLs.

## ⚠️ Important Update (January 2025)

**Proxycurl has been shut down** due to a lawsuit from LinkedIn. The agent has been updated with alternative methods. See [PROXYCURL_SHUTDOWN.md](PROXYCURL_SHUTDOWN.md) for details.

## 🚀 Features

- **Extract company data** (name + website) from LinkedIn job URLs using Scrapin API
- **Detect career pages** automatically from company websites
- **Extract open job positions** from career pages
- **Multiple input methods**: Direct LinkedIn URLs, company websites, or automatic search (optional)
- **Fully autonomous pipeline** - processes jobs end-to-end

## 📋 Prerequisites

- Python 3.8+
- **Required API key**:
  - [Scrapin](https://scrapin.io/) - For LinkedIn job data extraction
- **Optional API key** (for automatic job search):
  - [SerpAPI](https://serpapi.com/) - Alternative to Proxycurl for job discovery

## 🔧 Installation

1. Clone or navigate to this directory:
```bash
cd /Users/nithinyanna/Downloads/ai-job-source-agent
```

2. Create a virtual environment (recommended):
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env and add your API keys
```

## 📝 Usage

### Method 1: Direct LinkedIn Job URL (Recommended)

```python
from job_source_agent import JobSourceAgent
import os
from dotenv import load_dotenv

load_dotenv()

# Initialize agent (only Scrapin key required)
agent = JobSourceAgent(scrapin_api_key=os.getenv("SCRAPIN_API_KEY"))

# Run from a LinkedIn job URL
result = agent.run_from_job_url('https://www.linkedin.com/jobs/view/123/')

# Access results
print(f"Company: {result['company_name']}")
print(f"Career Page: {result['career_page_url']}")
print(f"Open Position: {result['open_position_url']}")
```

### Method 2: Company Website

```python
# Skip LinkedIn, go directly to company website
result = agent.run_from_company_website('https://www.notion.so', 'Notion')
```

### Method 3: Automatic Search (Optional - requires SerpAPI)

```python
# Initialize with SerpAPI for automatic job search
agent = JobSourceAgent(
    scrapin_api_key=os.getenv("SCRAPIN_API_KEY"),
    serpapi_key=os.getenv("SERPAPI_KEY")  # Optional
)

# Run automatic search
result = agent.run(keyword="software engineer")
```

### Command Line Usage

```bash
python job_source_agent.py
```

## 🔄 Workflow

The agent follows this autonomous pipeline:

1. **Input**: LinkedIn job URL (or company website, or automatic search)
2. **Extract Company Data** → Uses Scrapin API to get company name and website
3. **Find Career Page** → Navigates company website to detect career page URL
4. **Extract Job Posting** → Gets one open position URL from the career page

## 📊 Output Format

```json
{
  "company_name": "Notion",
  "career_page_url": "https://www.notion.so/careers",
  "open_position_url": "https://www.notion.so/jobs/backend-engineer",
  "linkedin_job_url": "https://www.linkedin.com/jobs/view/123/",
  "company_website": "https://www.notion.so"
}
```

## 🛠️ API Details

### Scrapin LinkedIn Job API
- **Endpoint**: `https://api.scrapin.io/linkedin/job`
- **Authentication**: API key in query parameter
- **Returns**: Company name, website, and LinkedIn profile

### SerpAPI (Optional)
- **Endpoint**: `https://serpapi.com/search`
- **Engine**: `linkedin_jobs`
- **Authentication**: API key in query parameter
- **Returns**: List of LinkedIn job URLs

## 🔍 How It Works

### Step 1: Input Methods
- **Method 1 (Recommended)**: Provide a LinkedIn job URL directly
- **Method 2**: Provide a company website URL
- **Method 3 (Optional)**: Use SerpAPI to automatically search for jobs

### Step 2: Company Data Extraction
From the LinkedIn job URL, the agent extracts:
- Company name
- Company website URL
- Company LinkedIn profile

### Step 3: Career Page Detection
The agent:
- Visits the company website
- Scans for links containing career-related keywords
- Tries common career page paths (`/careers`, `/jobs`, etc.)
- Returns the first valid career page found

### Step 4: Job Position Extraction
The agent:
- Visits the career page
- Scans for links containing job-related keywords
- Returns the first open position URL found

## ⚙️ Configuration

You can customize the agent behavior:

```python
# Custom search keyword
result = agent.run(keyword="data scientist")

# Custom page size for job discovery
job_urls = agent.discover_job_listings(keyword="engineer", page_size=10)
```

## 🐛 Error Handling

The agent includes comprehensive error handling:
- API request failures
- Missing data in API responses
- Website access issues
- Career page detection failures

All errors are logged and the agent returns partial results when possible.

## 📦 Dependencies

- `requests` - HTTP library for API calls and web scraping
- `beautifulsoup4` - HTML parsing for career page detection
- `python-dotenv` - Environment variable management
- `lxml` - Fast XML/HTML parser

## 🔐 Security

- Never commit your `.env` file to version control
- Keep your API keys secure
- The agent uses standard HTTP headers to avoid blocking

## 📄 License

This project is provided as-is for educational and development purposes.

## 🤝 Contributing

Feel free to extend this agent with:
- Multiple job position extraction
- Job description parsing
- Company information enrichment
- Database storage
- Web interface

## 📞 Support

For issues with:
- **Proxycurl API**: https://nubela.co/proxycurl/docs
- **Scrapin API**: https://scrapin.io/docs


# 🆓 Free Pipeline Quick Start

## Get Started in 3 Steps

### Step 1: Install Dependencies

```bash
cd /Users/nithinyanna/Downloads/ai-job-source-agent
source venv/bin/activate  # Activate virtual environment
pip install -r requirements.txt
```

### Step 2: Install Playwright (Optional but Recommended)

```bash
pip install playwright
playwright install chromium
```

### Step 3: Run the FREE Pipeline

```bash
python job_source_agent_free.py
```

That's it! **No API keys needed!** 🎉

## Optional: Install Ollama for LLM Navigation

If you want intelligent career page finding:

```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Download a model
ollama pull llama3

# Verify it's running
ollama list
```

## Basic Usage

```python
from job_source_agent_free import FreeJobSourceAgent

# Initialize - NO API keys needed!
agent = FreeJobSourceAgent(use_playwright=True)

# Run pipeline
results = agent.run_free_pipeline(
    keyword="software engineer",
    location="United States",
    max_jobs=10
)

# Print results
for result in results:
    print(f"Company: {result['company_name']}")
    print(f"Career Page: {result['career_page_url']}")
    print(f"Job: {result['open_position_url']}")
    print("---")
```

## What You Get

✅ LinkedIn job URLs (from public API)  
✅ Company names  
✅ Company websites  
✅ Career page URLs  
✅ Open position URLs  

**All for $0!**

## Troubleshooting

### "No jobs found"
- Try different keywords
- Check your internet connection
- Try using Playwright: `use_playwright=True`

### "Ollama not found"
- Install Ollama: `curl -fsSL https://ollama.ai/install.sh | sh`
- Or skip LLM navigation (still works without it)

### "Playwright browser not found"
```bash
playwright install chromium
```

## Cost: $0

- ✅ LinkedIn Public API: Free
- ✅ HTML Parsing: Free
- ✅ Ollama (local LLM): Free
- ✅ Playwright: Free
- ✅ Total: **$0**

Enjoy your free job discovery pipeline! 🚀


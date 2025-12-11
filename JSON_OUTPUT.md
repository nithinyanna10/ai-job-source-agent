# 📄 JSON Output Format

## Automatic JSON Saving

The free pipeline **automatically saves results to JSON** after each run.

## File Naming

Files are automatically named with timestamp:
- Format: `jobs_YYYYMMDD_HHMMSS.json`
- Example: `jobs_20251210_193413.json`

## JSON Structure

```json
{
  "metadata": {
    "total_jobs": 5,
    "generated_at": "2025-12-10T19:34:13.123456",
    "source": "free_pipeline"
  },
  "results": [
    {
      "linkedin_job_url": "https://www.linkedin.com/jobs/view/...",
      "company_name": "Netflix",
      "company_website": null,
      "career_page_url": null,
      "open_position_url": null,
      "title": "New Grad Software Engineer (2026)",
      "location": "United States",
      "source": "free_pipeline",
      "status": "partial"
    }
  ]
}
```

## Status Values

- **"complete"**: Full pipeline success (has career page + job posting)
- **"partial"**: Some data extracted (company name, but missing website/career page)
- **"company_extraction_failed"**: Could not extract company data

## Usage

### Default (Auto-save)

```python
results = agent.run_free_pipeline(
    keyword="software engineer",
    max_jobs=10
)
# Automatically saves to jobs_YYYYMMDD_HHMMSS.json
```

### Custom Filename

```python
results = agent.run_free_pipeline(
    keyword="data scientist",
    max_jobs=10,
    json_filename="data_scientist_jobs.json"
)
```

### Disable JSON Saving

```python
results = agent.run_free_pipeline(
    keyword="engineer",
    max_jobs=10,
    save_json=False  # Don't save to JSON
)
```

### Manual Save

```python
results = agent.run_free_pipeline(
    keyword="engineer",
    save_json=False
)

# Save manually later
agent.save_results_to_json(results, "my_custom_file.json")
```

## Reading JSON Files

```python
import json

with open("jobs_20251210_193413.json", "r") as f:
    data = json.load(f)
    
    print(f"Total jobs: {data['metadata']['total_jobs']}")
    
    for job in data['results']:
        print(f"{job['company_name']}: {job['title']}")
```

## File Location

JSON files are saved in the **current working directory** where you run the script.

## Benefits

✅ **Persistent storage** - Results saved automatically  
✅ **Easy to share** - JSON format is universal  
✅ **Easy to parse** - Standard format  
✅ **Timestamped** - Each run creates a new file  
✅ **Complete data** - All job information included  


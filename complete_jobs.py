"""
Script to complete partial job data from JSON file
Takes a JSON file with partial data and completes missing fields
"""

import json
import sys
from job_source_agent_free import FreeJobSourceAgent
import os
from dotenv import load_dotenv

load_dotenv()

def complete_job_data(input_json: str, output_json: str = None):
    """
    Complete job data from JSON file
    
    Args:
        input_json: Path to input JSON file
        output_json: Path to output JSON file (default: input_json with _completed suffix)
    """
    # Load existing data
    with open(input_json, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    if output_json is None:
        output_json = input_json.replace('.json', '_completed.json')
    
    # Initialize agent
    scrapin_key = os.getenv("SCRAPIN_API_KEY")
    ollama_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    ollama_model = os.getenv("OLLAMA_MODEL", "gpt-oss:120b-cloud")
    
    agent = FreeJobSourceAgent(
        scrapin_api_key=scrapin_key,
        ollama_base_url=ollama_url,
        ollama_model=ollama_model,
        use_playwright=False  # Use requests for faster processing
    )
    
    results = data.get("results", [])
    completed_results = []
    
    print(f"📋 Processing {len(results)} jobs to complete data...")
    print("=" * 60)
    
    for i, job in enumerate(results, 1):
        print(f"\n📦 Processing job {i}/{len(results)}: {job.get('title', 'Unknown')}")
        
        linkedin_job_url = job.get("linkedin_job_url")
        company_name = job.get("company_name")
        company_website = job.get("company_website")
        
        # If we already have complete data, skip
        if company_website and job.get("career_page_url") and job.get("open_position_url"):
            print(f"✅ Already complete, skipping")
            completed_results.append(job)
            continue
        
        # Try to get company website if missing
        if not company_website and linkedin_job_url:
            print(f"🔍 Extracting company website...")
            company_data = agent.extract_company_website_from_linkedin_job(linkedin_job_url)
            if company_data:
                company_name, company_website = company_data
                job["company_name"] = company_name
                job["company_website"] = company_website
                print(f"✅ Found website: {company_website}")
        
        # If still no website, try name lookup
        if not company_website and company_name:
            print(f"🔍 Trying website lookup by name...")
            company_website = agent._get_company_website_by_name(company_name)
            if company_website:
                job["company_website"] = company_website
                print(f"✅ Found via lookup: {company_website}")
        
        # Find career page if we have website
        if company_website and not job.get("career_page_url"):
            print(f"🌐 Finding career page...")
            career_page = agent.find_career_page_with_llm(company_website)
            if career_page:
                job["career_page_url"] = career_page
                print(f"✅ Found career page: {career_page}")
        
        # Extract job posting if we have career page
        if job.get("career_page_url") and not job.get("open_position_url"):
            print(f"💼 Extracting job posting...")
            open_job = agent.extract_one_job(job["career_page_url"])
            if open_job:
                job["open_position_url"] = open_job
                print(f"✅ Found job posting: {open_job}")
        
        # Update status
        if job.get("open_position_url"):
            job["status"] = "complete"
        elif job.get("career_page_url"):
            job["status"] = "partial"
        elif job.get("company_website"):
            job["status"] = "partial"
        else:
            job["status"] = "incomplete"
        
        completed_results.append(job)
        print(f"📊 Status: {job['status']}")
    
    # Save completed data
    output_data = {
        "metadata": {
            **data.get("metadata", {}),
            "completed_at": __import__("datetime").datetime.now().isoformat(),
            "source": "free_pipeline_completed"
        },
        "results": completed_results
    }
    
    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    # Print summary
    complete = sum(1 for r in completed_results if r.get("status") == "complete")
    partial = sum(1 for r in completed_results if r.get("status") == "partial")
    incomplete = sum(1 for r in completed_results if r.get("status") == "incomplete")
    
    print("\n" + "=" * 60)
    print("✅ COMPLETION SUMMARY")
    print("=" * 60)
    print(f"✅ Complete: {complete}")
    print(f"⚠️  Partial: {partial}")
    print(f"❌ Incomplete: {incomplete}")
    print(f"💾 Saved to: {output_json}")
    print("=" * 60)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python complete_jobs.py <input_json_file> [output_json_file]")
        print("\nExample:")
        print("  python complete_jobs.py jobs_20251210_193413.json")
        print("  python complete_jobs.py jobs_20251210_193413.json completed_jobs.json")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    if not os.path.exists(input_file):
        print(f"❌ Error: File not found: {input_file}")
        sys.exit(1)
    
    complete_job_data(input_file, output_file)


"""
Example usage of the Job Source Agent
Demonstrates different ways to use the agent

NOTE: Proxycurl has been shut down (January 2025). 
The agent now supports multiple input methods.
"""

import os
from dotenv import load_dotenv
from job_source_agent import JobSourceAgent

# Load environment variables
load_dotenv()


def example_from_linkedin_url():
    """Example 1: Using a direct LinkedIn job URL (RECOMMENDED)"""
    print("\n" + "="*60)
    print("Example 1: Direct LinkedIn Job URL (Recommended)")
    print("="*60)
    
    scrapin_key = os.getenv("SCRAPIN_API_KEY")
    if not scrapin_key:
        print("Error: SCRAPIN_API_KEY must be set in .env file")
        return
    
    agent = JobSourceAgent(scrapin_api_key=scrapin_key)
    
    # Provide a LinkedIn job URL directly
    linkedin_job_url = "https://www.linkedin.com/jobs/view/123/"  # Replace with actual URL
    result = agent.run_from_job_url(linkedin_job_url)
    
    print("\nResults:")
    for key, value in result.items():
        print(f"  {key}: {value}")


def example_from_company_website():
    """Example 2: Starting from a company website"""
    print("\n" + "="*60)
    print("Example 2: Company Website Input")
    print("="*60)
    
    scrapin_key = os.getenv("SCRAPIN_API_KEY")
    if not scrapin_key:
        print("Error: SCRAPIN_API_KEY must be set in .env file")
        return
    
    agent = JobSourceAgent(scrapin_api_key=scrapin_key)
    
    # Skip LinkedIn, go directly to company website
    result = agent.run_from_company_website(
        company_website="https://www.notion.so",
        company_name="Notion"
    )
    
    print("\nResults:")
    for key, value in result.items():
        print(f"  {key}: {value}")


def example_automatic_search():
    """Example 3: Automatic job search using SerpAPI (Optional)"""
    print("\n" + "="*60)
    print("Example 3: Automatic Search via SerpAPI")
    print("="*60)
    
    scrapin_key = os.getenv("SCRAPIN_API_KEY")
    serpapi_key = os.getenv("SERPAPI_KEY")
    
    if not scrapin_key:
        print("Error: SCRAPIN_API_KEY must be set in .env file")
        return
    
    if not serpapi_key:
        print("Warning: SERPAPI_KEY not set. Automatic search requires SerpAPI.")
        print("Use example_from_linkedin_url() instead with a direct LinkedIn job URL.")
        return
    
    agent = JobSourceAgent(
        scrapin_api_key=scrapin_key,
        serpapi_key=serpapi_key
    )
    
    # Automatic search (requires SerpAPI)
    result = agent.run(keyword="software engineer")
    
    print("\nResults:")
    for key, value in result.items():
        print(f"  {key}: {value}")


def example_step_by_step():
    """Example 4: Step-by-step execution"""
    print("\n" + "="*60)
    print("Example 4: Step-by-Step Execution")
    print("="*60)
    
    scrapin_key = os.getenv("SCRAPIN_API_KEY")
    if not scrapin_key:
        print("Error: SCRAPIN_API_KEY must be set in .env file")
        return
    
    agent = JobSourceAgent(scrapin_api_key=scrapin_key)
    
    # Provide a LinkedIn job URL
    linkedin_job_url = "https://www.linkedin.com/jobs/view/123/"  # Replace with actual URL
    
    # Step 1: Extract company data
    print("\nStep 1: Extracting company data...")
    company_data = agent.extract_company_data(linkedin_job_url)
    if company_data:
        company_name, company_website = company_data
        print(f"Company: {company_name}")
        print(f"Website: {company_website}")
        
        # Step 2: Find career page
        print("\nStep 2: Finding career page...")
        career_page = agent.find_career_page(company_website)
        print(f"Career Page: {career_page}")
        
        if career_page:
            # Step 3: Extract job posting
            print("\nStep 3: Extracting job posting...")
            job_posting = agent.extract_one_job(career_page)
            print(f"Job Posting: {job_posting}")


def example_multiple_jobs():
    """Example 5: Processing multiple LinkedIn job URLs"""
    print("\n" + "="*60)
    print("Example 5: Processing Multiple Job URLs")
    print("="*60)
    
    scrapin_key = os.getenv("SCRAPIN_API_KEY")
    if not scrapin_key:
        print("Error: SCRAPIN_API_KEY must be set in .env file")
        return
    
    agent = JobSourceAgent(scrapin_api_key=scrapin_key)
    
    # List of LinkedIn job URLs to process
    job_urls = [
        "https://www.linkedin.com/jobs/view/123/",
        "https://www.linkedin.com/jobs/view/456/",
        # Add more URLs as needed
    ]
    
    results = []
    for i, job_url in enumerate(job_urls, 1):
        print(f"\nProcessing job {i}/{len(job_urls)}: {job_url}")
        result = agent.run_from_job_url(job_url)
        results.append(result)
    
    print("\n" + "="*60)
    print("Summary of Results")
    print("="*60)
    for i, result in enumerate(results, 1):
        print(f"\nResult {i}:")
        for key, value in result.items():
            print(f"  {key}: {value}")


if __name__ == "__main__":
    print("="*60)
    print("AI Job Source Agent - Usage Examples")
    print("="*60)
    print("\n⚠️  NOTE: Proxycurl has been shut down (January 2025)")
    print("The agent now works with direct LinkedIn job URLs or company websites.")
    print("\nRecommended: Use example_from_linkedin_url() with a LinkedIn job URL")
    print("="*60)
    
    # Check if required API key is set
    if not os.getenv("SCRAPIN_API_KEY"):
        print("\nError: Please set SCRAPIN_API_KEY in .env file")
        print("See API_KEYS.md for details")
        exit(1)
    
    # Run examples
    try:
        # Uncomment the example you want to run:
        
        # Recommended: Direct LinkedIn URL
        # example_from_linkedin_url()
        
        # Alternative: Company website
        # example_from_company_website()
        
        # Optional: Automatic search (requires SerpAPI)
        # example_automatic_search()
        
        # Step-by-step
        # example_step_by_step()
        
        # Multiple jobs
        # example_multiple_jobs()
        
        print("\n" + "="*60)
        print("No example selected. Uncomment an example function above to run it.")
        print("="*60)
        
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()

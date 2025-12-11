"""
AI Job Source Agent - Hybrid Multi-Source Discovery Pipeline
Automatically discovers job listings with failover/redundancy, extracts company information,
finds career pages, and retrieves open position URLs.

Pipeline:
Step 1: Find LinkedIn job URLs (with failover)
  → Try Scrapin Job Search API (BEST)
  → Try SerpAPI (fallback 1)
  → Try PhantomBuster (fallback 2)
  → Try Direct HTML Scraping (last resort)

Step 2: Extract company data via Scrapin
Step 3: LLM Web Navigator crawls company website
Step 4: Find career page + job
Step 5: Store in Postgres
"""

import requests
import logging
from typing import Optional, Dict, List, Tuple
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, quote_plus
import re
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Keywords to identify career/job pages
CAREER_KEYWORDS = ["career", "careers", "jobs", "join", "work", "team", "hiring", "opportunities"]
JOB_KEYWORDS = ["job", "opening", "position", "role", "vacancy", "apply"]


class JobSourceAgent:
    """Autonomous agent with multi-source failover for job discovery"""
    
    def __init__(
        self,
        scrapin_api_key: str,
        serpapi_key: Optional[str] = None,
        phantombuster_key: Optional[str] = None,
        phantombuster_agent_id: Optional[str] = None,
        postgres_config: Optional[Dict] = None
    ):
        """
        Initialize the Job Source Agent with multi-source support
        
        Args:
            scrapin_api_key: API key for Scrapin (required for job search and company extraction)
            serpapi_key: Optional API key for SerpAPI (fallback 1)
            phantombuster_key: Optional API key for PhantomBuster (fallback 2)
            phantombuster_agent_id: Optional PhantomBuster agent ID for scheduled exports
            postgres_config: Optional dict with Postgres connection details
        """
        self.scrapin_key = scrapin_api_key
        self.serpapi_key = serpapi_key
        self.phantombuster_key = phantombuster_key
        self.phantombuster_agent_id = phantombuster_agent_id
        self.postgres_config = postgres_config
        
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
    
    # ==================== STEP 1: MULTI-SOURCE JOB DISCOVERY ====================
    
    def discover_job_listings_scrapin(
        self,
        keyword: str = "software engineer",
        location: str = "United States",
        limit: int = 100
    ) -> List[Dict]:
        """
        PRIMARY: Scrapin Job Search API (BEST, MOST RELIABLE)
        
        Args:
            keyword: Job search keyword
            location: Job location
            limit: Maximum results per request
            
        Returns:
            List of job dictionaries with job_url, company_name, etc.
        """
        try:
            endpoint = "https://api.scrapin.io/linkedin/search/jobs"
            params = {
                "keyword": keyword,
                "location": location,
                "limit": limit,
                "apikey": self.scrapin_key
            }
            
            logger.info(f"🔍 [Scrapin] Discovering job listings for: {keyword} in {location}")
            res = self.session.get(endpoint, params=params, timeout=30)
            res.raise_for_status()
            
            data = res.json()
            jobs = []
            
            # Scrapin returns jobs with full details
            if isinstance(data, list):
                jobs = data
            elif isinstance(data, dict) and "jobs" in data:
                jobs = data["jobs"]
            elif isinstance(data, dict) and "results" in data:
                jobs = data["results"]
            
            logger.info(f"✅ [Scrapin] Found {len(jobs)} job listings")
            return jobs
            
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ [Scrapin] Error: {e}")
            return []
        except Exception as e:
            logger.error(f"❌ [Scrapin] Unexpected error: {e}")
            return []
    
    def discover_job_listings_serpapi(
        self,
        keyword: str = "software engineer",
        location: str = "United States"
    ) -> List[Dict]:
        """
        FALLBACK 1: SerpAPI LinkedIn Jobs Search
        
        Args:
            keyword: Job search keyword
            location: Job location
            
        Returns:
            List of job dictionaries
        """
        if not self.serpapi_key:
            logger.warning("⚠️  [SerpAPI] Key not provided, skipping")
            return []
        
        try:
            url = "https://serpapi.com/search"
            params = {
                "engine": "linkedin_jobs",
                "q": keyword,
                "location": location,
                "api_key": self.serpapi_key
            }
            
            logger.info(f"🔍 [SerpAPI] Discovering job listings for: {keyword}")
            res = self.session.get(url, params=params, timeout=30)
            res.raise_for_status()
            
            data = res.json()
            jobs = []
            
            # Extract jobs from SerpAPI response
            if "jobs_results" in data:
                for job in data["jobs_results"]:
                    jobs.append({
                        "job_url": job.get("link"),
                        "company_name": job.get("company_name"),
                        "title": job.get("title"),
                        "location": job.get("location"),
                        "date_posted": job.get("date")
                    })
            
            logger.info(f"✅ [SerpAPI] Found {len(jobs)} job listings")
            return jobs
            
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ [SerpAPI] Error: {e}")
            return []
        except Exception as e:
            logger.error(f"❌ [SerpAPI] Unexpected error: {e}")
            return []
    
    def discover_job_listings_phantombuster(
        self,
        keyword: str = "software engineer",
        location: str = "United States"
    ) -> List[Dict]:
        """
        FALLBACK 2: PhantomBuster LinkedIn Job Search
        
        Args:
            keyword: Job search keyword
            location: Job location
            
        Returns:
            List of job dictionaries
        """
        if not self.phantombuster_key or not self.phantombuster_agent_id:
            logger.warning("⚠️  [PhantomBuster] Key or Agent ID not provided, skipping")
            return []
        
        try:
            # Option 1: Trigger agent run
            trigger_url = f"https://api.phantombuster.com/api/v2/agents/fetch-output"
            params = {
                "id": self.phantombuster_agent_id,
                "argument": {
                    "searchQuery": keyword,
                    "location": location
                }
            }
            headers = {"X-Phantombuster-Key": self.phantombuster_key}
            
            logger.info(f"🔍 [PhantomBuster] Triggering agent for: {keyword}")
            res = self.session.post(trigger_url, json=params, headers=headers, timeout=60)
            res.raise_for_status()
            
            # Option 2: Or fetch from scheduled export (if agent is already running)
            # This would require checking agent status and fetching results
            
            data = res.json()
            jobs = []
            
            if "output" in data and isinstance(data["output"], list):
                jobs = data["output"]
            
            logger.info(f"✅ [PhantomBuster] Found {len(jobs)} job listings")
            return jobs
            
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ [PhantomBuster] Error: {e}")
            return []
        except Exception as e:
            logger.error(f"❌ [PhantomBuster] Unexpected error: {e}")
            return []
    
    def discover_job_listings_direct_scraping(
        self,
        keyword: str = "software engineer",
        location: str = "United States"
    ) -> List[Dict]:
        """
        LAST RESORT: Direct HTML Scraping of LinkedIn (brittle, may break)
        
        WARNING: LinkedIn blocks headless browsers. This is fragile.
        Use only as last resort fallback.
        
        Args:
            keyword: Job search keyword
            location: Job location
            
        Returns:
            List of job dictionaries
        """
        try:
            # Build LinkedIn search URL
            search_url = f"https://www.linkedin.com/jobs/search/?keywords={quote_plus(keyword)}&location={quote_plus(location)}"
            
            logger.info(f"🔍 [Direct Scraping] Attempting to scrape: {search_url}")
            logger.warning("⚠️  [Direct Scraping] This method is brittle and may be blocked by LinkedIn")
            
            res = self.session.get(search_url, timeout=15, allow_redirects=True)
            
            # LinkedIn often returns login page or blocks requests
            if "login" in res.url.lower() or res.status_code != 200:
                logger.error("❌ [Direct Scraping] Blocked by LinkedIn (login required or rate limited)")
                return []
            
            soup = BeautifulSoup(res.text, "html.parser")
            jobs = []
            
            # Try to find job listings in HTML (structure may change)
            job_cards = soup.find_all("div", class_=re.compile(r"job.*card|result.*card", re.I))
            
            for card in job_cards[:20]:  # Limit to first 20
                try:
                    link_elem = card.find("a", href=re.compile(r"/jobs/view/"))
                    if link_elem:
                        job_url = link_elem.get("href")
                        if not job_url.startswith("http"):
                            job_url = "https://www.linkedin.com" + job_url
                        
                        title_elem = card.find("h3") or card.find("a")
                        title = title_elem.text.strip() if title_elem else "Unknown"
                        
                        jobs.append({
                            "job_url": job_url,
                            "title": title
                        })
                except:
                    continue
            
            logger.info(f"✅ [Direct Scraping] Found {len(jobs)} job listings (may be incomplete)")
            return jobs
            
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ [Direct Scraping] Error: {e}")
            return []
        except Exception as e:
            logger.error(f"❌ [Direct Scraping] Unexpected error: {e}")
            return []
    
    def discover_job_listings_with_failover(
        self,
        keyword: str = "software engineer",
        location: str = "United States",
        limit: int = 100
    ) -> List[Dict]:
        """
        HYBRID MULTI-SOURCE DISCOVERY WITH FAILOVER
        
        Tries sources in order:
        1. Scrapin (BEST)
        2. SerpAPI (fallback 1)
        3. PhantomBuster (fallback 2)
        4. Direct scraping (last resort)
        
        Args:
            keyword: Job search keyword
            location: Job location
            limit: Maximum results
            
        Returns:
            List of job dictionaries
        """
        logger.info("=" * 60)
        logger.info("🚀 Starting Multi-Source Job Discovery Pipeline")
        logger.info("=" * 60)
        
        # Try Scrapin (PRIMARY - BEST)
        jobs = self.discover_job_listings_scrapin(keyword, location, limit)
        if jobs:
            logger.info(f"✅ Success via Scrapin: {len(jobs)} jobs found")
            return jobs
        
        # Try SerpAPI (FALLBACK 1)
        logger.info("⚠️  Scrapin failed, trying SerpAPI...")
        jobs = self.discover_job_listings_serpapi(keyword, location)
        if jobs:
            logger.info(f"✅ Success via SerpAPI: {len(jobs)} jobs found")
            return jobs
        
        # Try PhantomBuster (FALLBACK 2)
        logger.info("⚠️  SerpAPI failed, trying PhantomBuster...")
        jobs = self.discover_job_listings_phantombuster(keyword, location)
        if jobs:
            logger.info(f"✅ Success via PhantomBuster: {len(jobs)} jobs found")
            return jobs
        
        # Try Direct Scraping (LAST RESORT)
        logger.warning("⚠️  All APIs failed, trying direct scraping (brittle)...")
        jobs = self.discover_job_listings_direct_scraping(keyword, location)
        if jobs:
            logger.warning(f"⚠️  Success via Direct Scraping: {len(jobs)} jobs found (may be incomplete)")
            return jobs
        
        logger.error("❌ All discovery methods failed")
        return []
    
    # ==================== STEP 2: EXTRACT COMPANY DATA ====================
    
    def extract_company_data(self, job_url: str) -> Optional[Tuple[str, str]]:
        """
        Extract company name + website using Scrapin API
        
        Args:
            job_url: LinkedIn job URL
            
        Returns:
            Tuple of (company_name, company_website) or None if error
        """
        try:
            endpoint = "https://api.scrapin.io/linkedin/job"
            params = {"url": job_url, "key": self.scrapin_key}
            
            logger.info(f"📋 Extracting company data from: {job_url}")
            res = self.session.get(endpoint, params=params, timeout=30)
            res.raise_for_status()
            
            data = res.json()
            company_name = data.get("company", {}).get("name")
            company_website = data.get("company", {}).get("website")
            
            if not company_name or not company_website:
                logger.warning(f"⚠️  Missing company data: name={company_name}, website={company_website}")
                return None
            
            logger.info(f"✅ Extracted: {company_name} → {company_website}")
            return company_name, company_website
            
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Error extracting company data: {e}")
            return None
        except Exception as e:
            logger.error(f"❌ Unexpected error: {e}")
            return None
    
    # ==================== STEP 3: FIND CAREER PAGE ====================
    
    def find_career_page(self, company_website: str) -> Optional[str]:
        """
        LLM Web Navigator: Detect Career Page from company website
        
        Args:
            company_website: Company website URL
            
        Returns:
            Career page URL or None if not found
        """
        try:
            if not company_website.startswith(('http://', 'https://')):
                company_website = 'https://' + company_website
            
            logger.info(f"🌐 Finding career page for: {company_website}")
            
            res = self.session.get(company_website, timeout=10, allow_redirects=True)
            res.raise_for_status()
            
            soup = BeautifulSoup(res.text, "html.parser")
            base_url = f"{urlparse(company_website).scheme}://{urlparse(company_website).netloc}"
            
            # Search for career links
            for a in soup.find_all("a", href=True):
                href = a.get("href", "").lower()
                text = (a.text or "").lower().strip()
                
                if any(keyword in href for keyword in CAREER_KEYWORDS) or \
                   any(keyword in text for keyword in CAREER_KEYWORDS):
                    
                    if href.startswith("http"):
                        career_url = href
                    elif href.startswith("/"):
                        career_url = base_url + href
                    else:
                        career_url = urljoin(company_website, href)
                    
                    logger.info(f"✅ Found career page: {career_url}")
                    return career_url
            
            # Try common paths
            common_paths = ["/careers", "/career", "/jobs", "/join-us", "/work-with-us"]
            for path in common_paths:
                try:
                    test_url = urljoin(company_website, path)
                    test_res = self.session.get(test_url, timeout=5, allow_redirects=True)
                    if test_res.status_code == 200:
                        logger.info(f"✅ Found career page via common path: {test_url}")
                        return test_url
                except:
                    continue
            
            logger.warning(f"⚠️  Career page not found for: {company_website}")
            return None
            
        except Exception as e:
            logger.error(f"❌ Error finding career page: {e}")
            return None
    
    # ==================== STEP 4: EXTRACT JOB POSTING ====================
    
    def extract_one_job(self, career_page_url: str) -> Optional[str]:
        """
        Extract ONE open job posting from Career Page
        
        Args:
            career_page_url: Career page URL
            
        Returns:
            URL of one open job position or None if not found
        """
        try:
            logger.info(f"💼 Extracting job posting from: {career_page_url}")
            
            res = self.session.get(career_page_url, timeout=10, allow_redirects=True)
            res.raise_for_status()
            
            soup = BeautifulSoup(res.text, "html.parser")
            base_url = f"{urlparse(career_page_url).scheme}://{urlparse(career_page_url).netloc}"
            
            job_links = []
            for a in soup.find_all("a", href=True):
                href = a.get("href", "").lower()
                text = (a.text or "").lower().strip()
                
                if any(keyword in href for keyword in JOB_KEYWORDS) or \
                   any(keyword in text for keyword in JOB_KEYWORDS):
                    
                    if href.startswith("http"):
                        job_url = href
                    elif href.startswith("/"):
                        job_url = base_url + href
                    else:
                        job_url = urljoin(career_page_url, href)
                    
                    if job_url not in job_links and "career" not in job_url.lower():
                        job_links.append(job_url)
            
            if job_links:
                selected_job = job_links[0]
                logger.info(f"✅ Found job posting: {selected_job}")
                return selected_job
            
            logger.warning(f"⚠️  No job postings found on: {career_page_url}")
            return None
            
        except Exception as e:
            logger.error(f"❌ Error extracting job posting: {e}")
            return None
    
    # ==================== STEP 5: POSTGRES STORAGE ====================
    
    def store_in_postgres(self, job_data: Dict) -> bool:
        """
        Store job data in Postgres database
        
        Args:
            job_data: Dictionary with job information
            
        Returns:
            True if successful, False otherwise
        """
        if not self.postgres_config:
            logger.warning("⚠️  Postgres config not provided, skipping storage")
            return False
        
        try:
            import psycopg2
            from psycopg2.extras import execute_values
            
            conn = psycopg2.connect(
                host=self.postgres_config.get("host"),
                port=self.postgres_config.get("port", 5432),
                database=self.postgres_config.get("database"),
                user=self.postgres_config.get("user"),
                password=self.postgres_config.get("password")
            )
            
            cur = conn.cursor()
            
            # Create table if not exists
            cur.execute("""
                CREATE TABLE IF NOT EXISTS job_discoveries (
                    id SERIAL PRIMARY KEY,
                    linkedin_job_url TEXT,
                    company_name TEXT,
                    company_website TEXT,
                    career_page_url TEXT,
                    open_position_url TEXT,
                    discovered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    source TEXT,
                    metadata JSONB
                )
            """)
            
            # Insert job data
            cur.execute("""
                INSERT INTO job_discoveries 
                (linkedin_job_url, company_name, company_website, career_page_url, open_position_url, source, metadata)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                job_data.get("linkedin_job_url"),
                job_data.get("company_name"),
                job_data.get("company_website"),
                job_data.get("career_page_url"),
                job_data.get("open_position_url"),
                job_data.get("source", "unknown"),
                str(job_data)
            ))
            
            conn.commit()
            cur.close()
            conn.close()
            
            logger.info("✅ Stored job data in Postgres")
            return True
            
        except ImportError:
            logger.warning("⚠️  psycopg2 not installed. Install with: pip install psycopg2-binary")
            return False
        except Exception as e:
            logger.error(f"❌ Error storing in Postgres: {e}")
            return False
    
    # ==================== FULL PIPELINE ====================
    
    def run_full_pipeline(
        self,
        keyword: str = "software engineer",
        location: str = "United States",
        limit: int = 10
    ) -> List[Dict]:
        """
        Complete autonomous pipeline with failover
        
        Steps:
        1. Multi-source job discovery (with failover)
        2. Extract company data
        3. Find career page
        4. Extract job posting
        5. Store in Postgres
        
        Args:
            keyword: Job search keyword
            location: Job location
            limit: Number of jobs to process
            
        Returns:
            List of complete job data dictionaries
        """
        logger.info("=" * 60)
        logger.info("🚀 Starting Full Autonomous Pipeline")
        logger.info("=" * 60)
        
        # Step 1: Discover jobs with failover
        jobs = self.discover_job_listings_with_failover(keyword, location, limit)
        if not jobs:
            logger.error("❌ No jobs discovered")
            return []
        
        results = []
        for i, job in enumerate(jobs[:limit], 1):
            logger.info(f"\n📦 Processing job {i}/{min(len(jobs), limit)}")
            
            job_url = job.get("job_url") or job.get("link")
            if not job_url:
                continue
            
            # Step 2: Extract company data
            company_data = self.extract_company_data(job_url)
            if not company_data:
                continue
            
            company_name, company_website = company_data
            
            # Step 3: Find career page
            career_page = self.find_career_page(company_website)
            
            # Step 4: Extract job posting
            open_job = self.extract_one_job(career_page) if career_page else None
            
            result = {
                "linkedin_job_url": job_url,
                "company_name": company_name,
                "company_website": company_website,
                "career_page_url": career_page,
                "open_position_url": open_job,
                "source": job.get("source", "unknown"),
                "title": job.get("title"),
                "location": job.get("location")
            }
            
            # Step 5: Store in Postgres
            if self.postgres_config:
                self.store_in_postgres(result)
            
            results.append(result)
            time.sleep(1)  # Rate limiting
        
        logger.info("=" * 60)
        logger.info(f"✅ Pipeline Complete: {len(results)} jobs processed")
        logger.info("=" * 60)
        
        return results


def main():
    """Example usage"""
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    scrapin_key = os.getenv("SCRAPIN_API_KEY")
    serpapi_key = os.getenv("SERPAPI_KEY")
    phantombuster_key = os.getenv("PHANTOMBUSTER_KEY")
    phantombuster_agent_id = os.getenv("PHANTOMBUSTER_AGENT_ID")
    
    postgres_config = None
    if os.getenv("POSTGRES_HOST"):
        postgres_config = {
            "host": os.getenv("POSTGRES_HOST"),
            "port": os.getenv("POSTGRES_PORT", 5432),
            "database": os.getenv("POSTGRES_DB"),
            "user": os.getenv("POSTGRES_USER"),
            "password": os.getenv("POSTGRES_PASSWORD")
        }
    
    if not scrapin_key:
        print("Error: SCRAPIN_API_KEY must be set")
        return
    
    agent = JobSourceAgent(
        scrapin_api_key=scrapin_key,
        serpapi_key=serpapi_key,
        phantombuster_key=phantombuster_key,
        phantombuster_agent_id=phantombuster_agent_id,
        postgres_config=postgres_config
    )
    
    # Run full pipeline
    results = agent.run_full_pipeline(keyword="software engineer", limit=5)
    
    print("\n" + "=" * 60)
    print("RESULTS")
    print("=" * 60)
    for i, result in enumerate(results, 1):
        print(f"\nJob {i}:")
        for key, value in result.items():
            print(f"  {key}: {value}")


if __name__ == "__main__":
    main()

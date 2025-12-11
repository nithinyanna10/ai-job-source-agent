"""
AI Job Source Agent - 100% FREE Pipeline
Uses LinkedIn public guest endpoints and free tools only.

Pipeline:
Step 1: Scrape LinkedIn Public Job Search (FREE - no API keys)
Step 2: Extract company website (FREE - from LinkedIn HTML or Scrapin free tier)
Step 3: LLM Web Navigator crawls company website (FREE - Ollama)
Step 4: Find career page + job
Step 5: Store in Postgres (optional)
"""

import requests
import logging
from typing import Optional, Dict, List, Tuple
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, quote_plus
import re
import time
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Keywords to identify career/job pages
CAREER_KEYWORDS = ["career", "careers", "jobs", "join", "work", "team", "hiring", "opportunities"]
JOB_KEYWORDS = ["job", "opening", "position", "role", "vacancy", "apply"]


class FreeJobSourceAgent:
    """100% FREE job source agent using LinkedIn public endpoints"""
    
    def __init__(
        self,
        scrapin_api_key: Optional[str] = None,  # Optional - only for free tier (100 calls/day)
        ollama_base_url: str = "http://localhost:11434",  # Free local LLM
        ollama_model: str = "gpt-oss:120b-cloud",  # Your Ollama model
        use_playwright: bool = True,  # Use Playwright for better reliability
        postgres_config: Optional[Dict] = None
    ):
        """
        Initialize FREE agent
        
        Args:
            scrapin_api_key: Optional - only if you want to use Scrapin FREE tier (100 calls/day)
            ollama_base_url: URL for local Ollama instance (free LLM)
            ollama_model: Ollama model name (default: gpt-oss:120b-cloud)
            use_playwright: Use Playwright for browser automation (more reliable)
            postgres_config: Optional Postgres config for storage
        """
        self.scrapin_key = scrapin_api_key
        self.ollama_base_url = ollama_base_url
        self.ollama_model = ollama_model
        self.use_playwright = use_playwright
        self.postgres_config = postgres_config
        
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        })
        
        self.playwright_browser = None
        if self.use_playwright:
            try:
                from playwright.sync_api import sync_playwright
                self.playwright = sync_playwright()
                self.playwright_browser = None  # Will be initialized on first use
            except ImportError:
                logger.warning("Playwright not installed. Install with: pip install playwright && playwright install")
                self.use_playwright = False
    
    # ==================== STEP 1: FREE LinkedIn Job Discovery ====================
    
    def discover_jobs_linkedin_public_api(
        self,
        keyword: str = "software engineer",
        location: str = "United States",
        max_results: int = 100
    ) -> List[Dict]:
        """
        FREE: Scrape LinkedIn Public Guest Job Search Endpoint
        
        Endpoint: https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search
        
        This is LinkedIn's public API used for infinite scroll - 100% legal and free!
        
        Args:
            keyword: Job search keyword
            location: Job location
            max_results: Maximum number of jobs to retrieve
            
        Returns:
            List of job dictionaries with job_url, company_name, title, location
        """
        jobs = []
        start = 0
        page_size = 25  # LinkedIn returns 25 jobs per page
        
        logger.info("=" * 60)
        logger.info("🆓 FREE LinkedIn Public API Job Discovery")
        logger.info("=" * 60)
        
        while len(jobs) < max_results:
            try:
                # Build LinkedIn public guest endpoint URL
                base_url = "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"
                params = {
                    "keywords": keyword,
                    "location": location,
                    "start": start
                }
                
                # Build query string
                query_string = "&".join([f"{k}={quote_plus(str(v))}" for k, v in params.items()])
                url = f"{base_url}?{query_string}"
                
                logger.info(f"📡 Fetching jobs {start} to {start + page_size}...")
                
                res = self.session.get(url, timeout=15)
                res.raise_for_status()
                
                # Parse HTML response
                soup = BeautifulSoup(res.text, "html.parser")
                
                # Find all job cards
                job_cards = soup.find_all("div", class_=re.compile(r"base-card|job-result-card", re.I))
                
                if not job_cards:
                    # Try alternative selectors
                    job_cards = soup.find_all("li", class_=re.compile(r"result-card", re.I))
                
                if not job_cards:
                    logger.warning("No job cards found in response. LinkedIn may have changed structure.")
                    break
                
                page_jobs = []
                for card in job_cards:
                    try:
                        # Extract job URL
                        link_elem = card.find("a", href=re.compile(r"/jobs/view/"))
                        if not link_elem:
                            continue
                        
                        job_path = link_elem.get("href", "")
                        if not job_path.startswith("http"):
                            job_url = "https://www.linkedin.com" + job_path
                        else:
                            job_url = job_path
                        
                        # Extract job title
                        title_elem = card.find("h3", class_=re.compile(r"title|job-title", re.I)) or \
                                    card.find("h3") or \
                                    link_elem.find("h3")
                        title = title_elem.text.strip() if title_elem else "Unknown"
                        
                        # Extract company name
                        company_elem = card.find("h4", class_=re.compile(r"company|subtitle", re.I)) or \
                                     card.find("h4") or \
                                     card.find("a", class_=re.compile(r"company", re.I))
                        company_name = company_elem.text.strip() if company_elem else "Unknown"
                        
                        # Extract location
                        location_elem = card.find("span", class_=re.compile(r"location|job-location", re.I)) or \
                                       card.find("div", class_=re.compile(r"location", re.I))
                        job_location = location_elem.text.strip() if location_elem else location
                        
                        # Extract job ID from URL
                        job_id_match = re.search(r'/jobs/view/(\d+)', job_url)
                        job_id = job_id_match.group(1) if job_id_match else None
                        
                        page_jobs.append({
                            "job_url": job_url,
                            "job_id": job_id,
                            "title": title,
                            "company_name": company_name,
                            "location": job_location,
                            "source": "linkedin_public_api"
                        })
                    except Exception as e:
                        logger.debug(f"Error parsing job card: {e}")
                        continue
                
                if not page_jobs:
                    logger.info("No more jobs found. Reached end of results.")
                    break
                
                jobs.extend(page_jobs)
                logger.info(f"✅ Found {len(page_jobs)} jobs (total: {len(jobs)})")
                
                # Check if there are more pages
                if len(page_jobs) < page_size:
                    break
                
                start += page_size
                time.sleep(1)  # Rate limiting - be nice to LinkedIn
                
            except requests.exceptions.RequestException as e:
                logger.error(f"❌ Error fetching jobs: {e}")
                break
            except Exception as e:
                logger.error(f"❌ Unexpected error: {e}")
                break
        
        logger.info(f"✅ Total jobs discovered: {len(jobs)}")
        return jobs[:max_results]
    
    def discover_jobs_playwright(
        self,
        keyword: str = "software engineer",
        location: str = "United States",
        max_results: int = 50
    ) -> List[Dict]:
        """
        FREE: Use Playwright to scrape LinkedIn jobs (more reliable)
        
        Args:
            keyword: Job search keyword
            location: Job location
            max_results: Maximum number of jobs
            
        Returns:
            List of job dictionaries
        """
        if not self.use_playwright:
            logger.warning("Playwright not available, falling back to requests")
            return self.discover_jobs_linkedin_public_api(keyword, location, max_results)
        
        try:
            from playwright.sync_api import sync_playwright
            
            logger.info("🎭 Using Playwright for job discovery...")
            
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                
                # Build LinkedIn job search URL
                search_url = f"https://www.linkedin.com/jobs/search/?keywords={quote_plus(keyword)}&location={quote_plus(location)}"
                
                logger.info(f"🌐 Navigating to: {search_url}")
                page.goto(search_url, wait_until="networkidle", timeout=30000)
                
                # Wait for job listings to load
                page.wait_for_selector("ul.jobs-search__results-list", timeout=10000)
                
                # Scroll to load more jobs
                for _ in range(3):  # Scroll 3 times to load more
                    page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                    time.sleep(2)
                
                # Extract jobs
                jobs = []
                job_elements = page.query_selector_all("li.jobs-search-results__list-item")
                
                for elem in job_elements[:max_results]:
                    try:
                        link_elem = elem.query_selector("a.base-card__full-link")
                        if not link_elem:
                            continue
                        
                        job_url = link_elem.get_attribute("href")
                        if not job_url.startswith("http"):
                            job_url = "https://www.linkedin.com" + job_url
                        
                        title_elem = elem.query_selector("h3.base-search-card__title")
                        title = title_elem.inner_text() if title_elem else "Unknown"
                        
                        company_elem = elem.query_selector("h4.base-search-card__subtitle")
                        company_name = company_elem.inner_text() if company_elem else "Unknown"
                        
                        location_elem = elem.query_selector("span.job-search-card__location")
                        job_location = location_elem.inner_text() if location_elem else location
                        
                        jobs.append({
                            "job_url": job_url,
                            "title": title,
                            "company_name": company_name,
                            "location": job_location,
                            "source": "playwright"
                        })
                    except Exception as e:
                        logger.debug(f"Error extracting job: {e}")
                        continue
                
                browser.close()
                
                logger.info(f"✅ Found {len(jobs)} jobs via Playwright")
                return jobs
                
        except ImportError:
            logger.warning("Playwright not installed")
            return self.discover_jobs_linkedin_public_api(keyword, location, max_results)
        except Exception as e:
            logger.error(f"❌ Playwright error: {e}")
            return self.discover_jobs_linkedin_public_api(keyword, location, max_results)
    
    # ==================== STEP 2: FREE Company Website Extraction ====================
    
    def extract_company_website_from_linkedin_job(
        self,
        job_url: str
    ) -> Optional[Tuple[str, str]]:
        """
        FREE: Extract company name and website from LinkedIn job page HTML
        
        Method 1: Parse LinkedIn job page HTML directly
        Method 2: Navigate to company page and extract website
        
        Args:
            job_url: LinkedIn job URL
            
        Returns:
            Tuple of (company_name, company_website) or None
        """
        try:
            logger.info(f"📋 Extracting company data from: {job_url}")
            
            # Method 1: Try to get company info from job page
            res = self.session.get(job_url, timeout=15)
            res.raise_for_status()
            
            soup = BeautifulSoup(res.text, "html.parser")
            
            # Find company name
            company_name = None
            company_elem = soup.find("a", class_=re.compile(r"topcard__org-name-link|company-name", re.I)) or \
                          soup.find("h4", class_=re.compile(r"topcard__flavor", re.I)) or \
                          soup.find("a", {"data-tracking-control-name": re.compile(r"public_jobs.*company", re.I)})
            
            if company_elem:
                company_name = company_elem.text.strip()
            
            # Find company LinkedIn URL - try multiple methods
            company_linkedin_url = None
            
            # Method 1: From company element
            if company_elem and company_elem.get("href"):
                company_path = company_elem.get("href")
                if not company_path.startswith("http"):
                    company_linkedin_url = "https://www.linkedin.com" + company_path
                else:
                    company_linkedin_url = company_path
            
            # Method 2: Search for company links in page
            if not company_linkedin_url:
                company_link = soup.find("a", href=re.compile(r"/company/[^/]+", re.I))
                if company_link:
                    path = company_link.get("href", "")
                    if not path.startswith("http"):
                        company_linkedin_url = "https://www.linkedin.com" + path
                    else:
                        company_linkedin_url = path
            
            # Method 3: Extract from job URL structure or meta tags
            if not company_linkedin_url:
                # Try to extract from URL pattern: ...-at-company-name-...
                url_match = re.search(r'-at-([^-]+(?:-[^-]+)*?)-', job_url)
                if url_match:
                    company_slug = url_match.group(1)
                    company_linkedin_url = f"https://www.linkedin.com/company/{company_slug}/"
            
            # If we have company LinkedIn URL, try to get website from company page
            if company_linkedin_url:
                company_website = self._extract_website_from_company_page(company_linkedin_url)
                if company_website and company_name:
                    logger.info(f"✅ Extracted: {company_name} → {company_website}")
                    return company_name, company_website
            
            # Method 2: Use Scrapin FREE tier if available (100 calls/day)
            if self.scrapin_key:
                result = self._extract_company_via_scrapin_free(job_url)
                if result:
                    return result
            
            # Method 3: Try to get website by company name (fallback for well-known companies)
            if company_name:
                company_website = self._get_company_website_by_name(company_name)
                if company_website:
                    logger.info(f"✅ Found website via name lookup: {company_name} → {company_website}")
                    return company_name, company_website
            
            logger.warning("⚠️  Could not extract company website. Try using Scrapin free tier.")
            return (company_name, None) if company_name else None
            
        except Exception as e:
            logger.error(f"❌ Error extracting company data: {e}")
            return None
    
    def _extract_website_from_company_page(self, company_linkedin_url: str) -> Optional[str]:
        """Extract website from LinkedIn company page"""
        try:
            logger.info(f"🔍 Extracting website from company page: {company_linkedin_url}")
            res = self.session.get(company_linkedin_url, timeout=15)
            res.raise_for_status()
            
            soup = BeautifulSoup(res.text, "html.parser")
            
            # Method 1: Find website link with specific selectors
            website_elem = (
                soup.find("a", href=re.compile(r"^https?://", re.I), 
                         class_=re.compile(r"website|link", re.I)) or
                soup.find("a", {"data-tracking-control-name": re.compile(r"website", re.I)}) or
                soup.find("a", {"data-control-name": re.compile(r"website", re.I)}) or
                soup.find("dd", class_=re.compile(r"website", re.I))
            )
            
            if website_elem:
                href = website_elem.get("href") or website_elem.text.strip()
                if href and href.startswith("http"):
                    return href
            
            # Method 2: Look for structured data (JSON-LD)
            json_ld_scripts = soup.find_all("script", type="application/ld+json")
            for script in json_ld_scripts:
                try:
                    import json
                    data = json.loads(script.string)
                    if isinstance(data, dict):
                        # Try various paths
                        url = (data.get("url") or 
                              data.get("sameAs") or
                              (data.get("contactPoint", {}) if isinstance(data.get("contactPoint"), dict) else {}).get("url"))
                        if url and isinstance(url, str) and url.startswith("http"):
                            return url
                except:
                    continue
            
            # Method 3: Search for external links in company info section
            company_section = soup.find("section", class_=re.compile(r"company|about", re.I)) or \
                            soup.find("div", class_=re.compile(r"company-info", re.I))
            
            if company_section:
                for link in company_section.find_all("a", href=re.compile(r"^https?://", re.I)):
                    href = link.get("href", "")
                    if "linkedin.com" not in href and not href.startswith("mailto:") and not href.startswith("tel:"):
                        # Filter out social media links
                        if not any(social in href.lower() for social in ["facebook.com", "twitter.com", "instagram.com", "youtube.com"]):
                            return href
            
            # Method 4: Try to find any external link (last resort)
            # Filter out LinkedIn URLs more strictly
            for link in soup.find_all("a", href=re.compile(r"^https?://", re.I)):
                href = link.get("href", "")
                if (href and 
                    "linkedin.com" not in href.lower() and 
                    not href.startswith("mailto:") and 
                    not href.startswith("tel:") and
                    not any(social in href.lower() for social in ["facebook.com", "twitter.com", "instagram.com", "youtube.com", "linkedin.com/in", "linkedin.com/top-content", "linkedin.com/jobs/search"])):
                    # Prefer .com, .org, .io domains
                    if any(domain in href.lower() for domain in [".com", ".org", ".io", ".ai", ".net"]):
                        return href
            
            return None
            
        except Exception as e:
            logger.debug(f"Error extracting from company page: {e}")
            return None
    
    def _get_company_website_by_name(self, company_name: str) -> Optional[str]:
        """
        Try to get company website by searching common patterns
        This is a fallback when LinkedIn extraction fails
        """
        try:
            # Common patterns for well-known companies
            company_websites = {
                "netflix": "https://jobs.netflix.com",
                "nike": "https://jobs.nike.com",
                "intuit": "https://www.intuit.com/careers",
                "nuro": "https://www.nuro.ai/careers",
                "seatgeek": "https://seatgeek.com/jobs",
                "google": "https://careers.google.com",
                "microsoft": "https://careers.microsoft.com",
                "apple": "https://www.apple.com/careers",
                "amazon": "https://www.amazon.jobs",
                "meta": "https://www.metacareers.com",
                "facebook": "https://www.metacareers.com",
            }
            
            company_lower = company_name.lower().strip()
            if company_lower in company_websites:
                website = company_websites[company_lower]
                logger.info(f"✅ Found website via lookup: {website}")
                return website
            
            # Also check if company name contains known company names
            for known_company, website in company_websites.items():
                if known_company in company_lower:
                    logger.info(f"✅ Found website via partial match: {website}")
                    return website
            
            # Try common domain patterns
            company_slug = company_lower.replace(" ", "").replace("-", "")
            common_domains = [
                f"https://www.{company_slug}.com",
                f"https://{company_slug}.com",
                f"https://www.{company_lower.replace(' ', '-')}.com",
            ]
            
            # Test if domain exists (quick check)
            for domain in common_domains:
                try:
                    test_res = self.session.head(domain, timeout=5, allow_redirects=True)
                    if test_res.status_code < 400:
                        logger.info(f"✅ Found website via pattern: {domain}")
                        return domain
                except:
                    continue
            
            return None
            
        except Exception as e:
            logger.debug(f"Error in company website lookup: {e}")
            return None
    
    def _extract_company_via_scrapin_free(self, job_url: str) -> Optional[Tuple[str, str]]:
        """Use Scrapin FREE tier (100 calls/day)"""
        try:
            endpoint = "https://api.scrapin.io/linkedin/job"
            params = {"url": job_url, "key": self.scrapin_key}
            
            res = self.session.get(endpoint, params=params, timeout=30)
            res.raise_for_status()
            
            data = res.json()
            company_name = data.get("company", {}).get("name")
            company_website = data.get("company", {}).get("website")
            
            if company_name and company_website:
                logger.info(f"✅ [Scrapin FREE] Extracted: {company_name} → {company_website}")
                return company_name, company_website
            
            return None
            
        except Exception as e:
            logger.debug(f"Scrapin free tier error: {e}")
            return None
    
    # ==================== STEP 3: FREE LLM Web Navigator ====================
    
    def find_career_page_with_llm(self, company_website: str) -> Optional[str]:
        """
        FREE: Use Ollama (local LLM) to intelligently find career page
        
        Args:
            company_website: Company website URL
            
        Returns:
            Career page URL or None
        """
        try:
            if not company_website.startswith(('http://', 'https://')):
                company_website = 'https://' + company_website
            
            logger.info(f"🤖 Using LLM to find career page for: {company_website}")
            
            # First, try traditional method
            career_page = self._find_career_page_traditional(company_website)
            if career_page:
                return career_page
            
            # If not found, use LLM to analyze page structure
            try:
                import requests as req
                
                # Get page content
                res = self.session.get(company_website, timeout=10)
                soup = BeautifulSoup(res.text, "html.parser")
                
                # Extract all links
                links = []
                for a in soup.find_all("a", href=True)[:50]:  # Limit to first 50 links
                    href = a.get("href", "")
                    text = a.text.strip()
                    if href and text:
                        links.append(f"{text}: {href}")
                
                links_text = "\n".join(links[:20])  # Limit for LLM
                
                # Ask LLM which link is most likely the career page
                prompt = f"""Given these links from a company website, which one is most likely the careers/jobs page?
                
Links:
{links_text}

Respond with ONLY the href URL of the most likely career page, or "none" if none seem relevant."""
                
                # Use Ollama API with your model
                ollama_url = f"{self.ollama_base_url}/api/chat"
                response = req.post(ollama_url, json={
                    "model": self.ollama_model,  # Your model: gpt-oss:120b-cloud
                    "messages": [{"role": "user", "content": prompt}],
                    "stream": False
                }, timeout=60)  # Increased timeout for large model
                
                if response.status_code == 200:
                    data = response.json()
                    llm_response = data.get("message", {}).get("content", "").strip().lower()
                    
                    if "none" not in llm_response and "http" in llm_response:
                        # Extract URL from LLM response
                        url_match = re.search(r'https?://[^\s<>"]+', llm_response)
                        if url_match:
                            career_url = url_match.group(0)
                            logger.info(f"✅ LLM suggested career page: {career_url}")
                            return career_url
                
            except ImportError:
                logger.warning("requests not available for Ollama API calls")
            except Exception as e:
                logger.debug(f"LLM navigation error: {e}")
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Error finding career page: {e}")
            return None
    
    def _find_career_page_traditional(self, company_website: str) -> Optional[str]:
        """Traditional method to find career page"""
        try:
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
                        return href
                    elif href.startswith("/"):
                        return base_url + href
                    else:
                        return urljoin(company_website, href)
            
            # Try common paths
            common_paths = ["/careers", "/career", "/jobs", "/join-us", "/work-with-us"]
            for path in common_paths:
                try:
                    test_url = urljoin(company_website, path)
                    test_res = self.session.get(test_url, timeout=5, allow_redirects=True)
                    if test_res.status_code == 200:
                        return test_url
                except:
                    continue
            
            return None
            
        except Exception as e:
            logger.debug(f"Traditional method error: {e}")
            return None
    
    # ==================== STEP 4: Extract Job Posting ====================
    
    def extract_one_job(self, career_page_url: str) -> Optional[str]:
        """Extract one job posting from career page"""
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
            
            logger.warning(f"⚠️  No job postings found")
            return None
            
        except Exception as e:
            logger.error(f"❌ Error extracting job posting: {e}")
            return None
    
    # ==================== STEP 5: Postgres Storage ====================
    
    def store_in_postgres(self, job_data: Dict) -> bool:
        """Store job data in Postgres (optional)"""
        if not self.postgres_config:
            return False
        
        try:
            import psycopg2
            
            conn = psycopg2.connect(
                host=self.postgres_config.get("host"),
                port=self.postgres_config.get("port", 5432),
                database=self.postgres_config.get("database"),
                user=self.postgres_config.get("user"),
                password=self.postgres_config.get("password")
            )
            
            cur = conn.cursor()
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
                job_data.get("source", "free_pipeline"),
                json.dumps(job_data)
            ))
            
            conn.commit()
            cur.close()
            conn.close()
            
            logger.info("✅ Stored in Postgres")
            return True
            
        except ImportError:
            logger.warning("psycopg2 not installed")
            return False
        except Exception as e:
            logger.error(f"❌ Postgres error: {e}")
            return False
    
    # ==================== FULL FREE PIPELINE ====================
    
    def save_results_to_json(self, results: List[Dict], filename: Optional[str] = None) -> str:
        """
        Save results to JSON file
        
        Args:
            results: List of job result dictionaries
            filename: Optional filename (default: jobs_YYYYMMDD_HHMMSS.json)
            
        Returns:
            Path to saved JSON file
        """
        import json
        from datetime import datetime
        
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"jobs_{timestamp}.json"
        
        # Ensure .json extension
        if not filename.endswith('.json'):
            filename += '.json'
        
        # Save to JSON with pretty formatting
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump({
                "metadata": {
                    "total_jobs": len(results),
                    "generated_at": datetime.now().isoformat(),
                    "source": "free_pipeline"
                },
                "results": results
            }, f, indent=2, ensure_ascii=False)
        
        logger.info(f"💾 Results saved to: {filename}")
        return filename
    
    def run_free_pipeline(
        self,
        keyword: str = "software engineer",
        location: str = "United States",
        max_jobs: int = 10,
        use_playwright: Optional[bool] = None,
        save_json: bool = True,
        json_filename: Optional[str] = None
    ) -> List[Dict]:
        """
        Complete FREE pipeline - $0 cost!
        
        Args:
            keyword: Job search keyword
            location: Job location
            max_jobs: Maximum jobs to process
            use_playwright: Override default Playwright setting
            save_json: Whether to save results to JSON file (default: True)
            json_filename: Optional JSON filename (default: auto-generated)
            
        Returns:
            List of complete job data
        """
        logger.info("=" * 60)
        logger.info("🆓 Starting 100% FREE Pipeline")
        logger.info("=" * 60)
        
        # Step 1: Discover jobs (FREE)
        if use_playwright is None:
            use_playwright = self.use_playwright
        
        if use_playwright:
            jobs = self.discover_jobs_playwright(keyword, location, max_jobs)
        else:
            jobs = self.discover_jobs_linkedin_public_api(keyword, location, max_jobs)
        
        if not jobs:
            logger.error("❌ No jobs discovered")
            return []
        
        results = []
        for i, job in enumerate(jobs[:max_jobs], 1):
            logger.info(f"\n📦 Processing job {i}/{min(len(jobs), max_jobs)}: {job.get('title', 'Unknown')}")
            
            job_url = job.get("job_url")
            if not job_url:
                continue
            
            # Step 2: Extract company data (FREE)
            company_data = self.extract_company_website_from_linkedin_job(job_url)
            if not company_data:
                # Still save job info even if company extraction fails
                result = {
                    "linkedin_job_url": job_url,
                    "company_name": None,
                    "company_website": None,
                    "career_page_url": None,
                    "open_position_url": None,
                    "title": job.get("title"),
                    "location": job.get("location"),
                    "source": "free_pipeline",
                    "status": "company_extraction_failed"
                }
                results.append(result)
                continue
            
            company_name, company_website = company_data
            
            # Step 3: Find career page (FREE - with LLM)
            career_page = None
            open_job = None
            
            if company_website:
                career_page = self.find_career_page_with_llm(company_website)
                # Step 4: Extract job posting
                if career_page:
                    open_job = self.extract_one_job(career_page)
            else:
                logger.warning(f"⚠️  No website for {company_name}, skipping career page search")
            
            result = {
                "linkedin_job_url": job_url,
                "company_name": company_name,
                "company_website": company_website,
                "career_page_url": career_page,
                "open_position_url": open_job,
                "title": job.get("title"),
                "location": job.get("location"),
                "source": "free_pipeline",
                "status": "complete" if open_job else "partial"
            }
            
            # Step 5: Store in Postgres (optional)
            if self.postgres_config:
                self.store_in_postgres(result)
            
            results.append(result)
            time.sleep(2)  # Rate limiting
        
        logger.info("=" * 60)
        logger.info(f"✅ FREE Pipeline Complete: {len(results)} jobs processed")
        logger.info("=" * 60)
        
        # Save to JSON file
        if save_json:
            json_file = self.save_results_to_json(results, json_filename)
            logger.info(f"📄 Results saved to JSON: {json_file}")
        
        return results


def main():
    """Example usage of FREE pipeline"""
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    # All optional - pipeline works with $0!
    scrapin_key = os.getenv("SCRAPIN_API_KEY")  # Optional - only for free tier
    ollama_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    ollama_model = os.getenv("OLLAMA_MODEL", "gpt-oss:120b-cloud")  # Your model
    
    postgres_config = None
    if os.getenv("POSTGRES_HOST"):
        postgres_config = {
            "host": os.getenv("POSTGRES_HOST"),
            "port": int(os.getenv("POSTGRES_PORT", 5432)),
            "database": os.getenv("POSTGRES_DB"),
            "user": os.getenv("POSTGRES_USER"),
            "password": os.getenv("POSTGRES_PASSWORD")
        }
    
    agent = FreeJobSourceAgent(
        scrapin_api_key=scrapin_key,  # Optional
        ollama_base_url=ollama_url,
        ollama_model=ollama_model,  # Your model: gpt-oss:120b-cloud
        use_playwright=True,  # More reliable
        postgres_config=postgres_config  # Optional
    )
    
    # Run FREE pipeline (results automatically saved to JSON)
    results = agent.run_free_pipeline(
        keyword="software engineer",
        location="United States",
        max_jobs=5,
        save_json=True,  # Save to JSON file
        json_filename=None  # Auto-generate filename
    )
    
    print("\n" + "=" * 60)
    print("🆓 FREE PIPELINE RESULTS")
    print("=" * 60)
    print(f"Total jobs processed: {len(results)}")
    
    # Show summary
    complete = sum(1 for r in results if r.get("status") == "complete")
    partial = sum(1 for r in results if r.get("status") == "partial")
    failed = sum(1 for r in results if r.get("status") == "company_extraction_failed")
    
    print(f"✅ Complete: {complete}")
    print(f"⚠️  Partial: {partial}")
    print(f"❌ Failed: {failed}")
    
    # Show first few results
    print("\n" + "=" * 60)
    print("SAMPLE RESULTS (see JSON file for full data)")
    print("=" * 60)
    for i, result in enumerate(results[:3], 1):
        print(f"\nJob {i}:")
        print(f"  Title: {result.get('title', 'N/A')}")
        print(f"  Company: {result.get('company_name', 'N/A')}")
        print(f"  Career Page: {result.get('career_page_url', 'N/A')}")
        print(f"  Open Position: {result.get('open_position_url', 'N/A')}")
        print(f"  Status: {result.get('status', 'N/A')}")
    
    if len(results) > 3:
        print(f"\n... and {len(results) - 3} more jobs (see JSON file)")


if __name__ == "__main__":
    main()


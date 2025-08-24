#!/usr/bin/env python3
"""
Enhanced Web Scraper for Reviu.pk
Uses free tools and advanced techniques for better data extraction
"""

import json
import logging
import requests
import time
from typing import List, Dict, Any, Optional
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin, urlparse, quote_plus
import random
from fake_useragent import UserAgent
import concurrent.futures
from dataclasses import dataclass

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class ScrapedBusiness:
    """Structured scraped business data"""
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    website: Optional[str] = None
    business_type: Optional[str] = None
    category: Optional[str] = None
    city: Optional[str] = None
    description: Optional[str] = None
    social_media: Optional[Dict[str, str]] = None
    verified: bool = False
    source: str = "enhanced_scraper"
    confidence_score: float = 0.0

class EnhancedScraper:
    """Enhanced web scraper with advanced techniques"""
    
    def __init__(self):
        """Initialize the enhanced scraper"""
        self.session = requests.Session()
        self.ua = UserAgent()
        
        # Free proxy rotation (public proxies - use with caution)
        self.proxy_list = self._load_free_proxies()
        self.current_proxy_index = 0
        
        # Enhanced headers rotation
        self.headers_list = [
            {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            },
            {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
            },
            {
                'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.8',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
            }
        ]
        
        # Rate limiting and retry settings
        self.min_delay = 2
        self.max_delay = 5
        self.max_retries = 3
        self.last_request_time = 0
        
        # Business directory sources
        self.business_sources = {
            "pakistan_business_directory": {
                "base_url": "https://www.pakistanbusinessdirectory.com",
                "search_pattern": "search?q={query}",
                "business_selectors": [
                    ".business-listing", ".company-item", ".business-card",
                    ".listing-item", ".company-listing", ".business-result"
                ],
                "name_selectors": ["h2", "h3", ".business-name", ".company-name"],
                "contact_selectors": [".contact-info", ".business-details", ".company-details"]
            },
            "yellow_pages_pk": {
                "base_url": "https://www.yellowpages.pk",
                "search_pattern": "search?category={category}&city={city}",
                "business_selectors": [
                    ".business-listing", ".company-item", ".listing-item",
                    ".business-card", ".company-card", ".result-item"
                ],
                "name_selectors": ["h3", "h4", ".business-name", ".company-name"],
                "contact_selectors": [".contact-details", ".business-info", ".company-info"]
            },
            "pakistan_companies": {
                "base_url": "https://www.pakistan-companies.com",
                "search_pattern": "search?q={query}",
                "business_selectors": [
                    ".company-listing", ".business-item", ".company-card",
                    ".business-result", ".company-result", ".listing-item"
                ],
                "name_selectors": ["h2", "h3", ".company-name", ".business-name"],
                "contact_selectors": [".company-details", ".business-details", ".contact-info"]
            }
        }
    
    def _load_free_proxies(self) -> List[str]:
        """Load free proxy list (use with caution)"""
        try:
            # Free proxy list from multiple sources
            proxy_sources = [
                "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt",
                "https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list-raw.txt"
            ]
            
            proxies = []
            for source in proxy_sources:
                try:
                    response = requests.get(source, timeout=10)
                    if response.status_code == 200:
                        proxy_lines = response.text.strip().split('\n')
                        proxies.extend([line.strip() for line in proxy_lines if line.strip()])
                except:
                    continue
            
            # Filter valid proxies
            valid_proxies = []
            for proxy in proxies[:50]:  # Limit to 50 proxies
                if re.match(r'^\d+\.\d+\.\d+\.\d+:\d+$', proxy):
                    valid_proxies.append(proxy)
            
            logger.info(f"Loaded {len(valid_proxies)} free proxies")
            return valid_proxies
            
        except Exception as e:
            logger.warning(f"Could not load free proxies: {e}")
            return []
    
    def _get_next_proxy(self) -> Optional[str]:
        """Get next proxy from rotation"""
        if not self.proxy_list:
            return None
        
        proxy = self.proxy_list[self.current_proxy_index]
        self.current_proxy_index = (self.current_proxy_index + 1) % len(self.proxy_list)
        return proxy
    
    def _get_random_headers(self) -> Dict[str, str]:
        """Get random headers for request"""
        return random.choice(self.headers_list)
    
    def _rate_limit(self):
        """Implement smart rate limiting"""
        current_time = time.time()
        if current_time - self.last_request_time < self.min_delay:
            delay = random.uniform(self.min_delay, self.max_delay)
            time.sleep(delay)
        self.last_request_time = time.time()
    
    def _make_request(self, url: str, retries: int = 0) -> Optional[requests.Response]:
        """Make HTTP request with retry logic and proxy rotation"""
        try:
            self._rate_limit()
            
            headers = self._get_random_headers()
            proxy = self._get_next_proxy() if retries > 0 else None
            
            proxies = {"http": f"http://{proxy}", "https": f"http://{proxy}"} if proxy else None
            
            response = self.session.get(
                url, 
                headers=headers, 
                proxies=proxies,
                timeout=15,
                allow_redirects=True
            )
            
            if response.status_code == 200:
                return response
            elif response.status_code in [429, 503] and retries < self.max_retries:
                logger.warning(f"Rate limited, retrying with proxy... (attempt {retries + 1})")
                time.sleep(random.uniform(5, 15))  # Longer delay for rate limits
                return self._make_request(url, retries + 1)
            else:
                logger.error(f"Request failed: {response.status_code} for {url}")
                return None
                
        except Exception as e:
            if retries < self.max_retries:
                logger.warning(f"Request failed, retrying... (attempt {retries + 1}): {e}")
                time.sleep(random.uniform(2, 8))
                return self._make_request(url, retries + 1)
            else:
                logger.error(f"Request failed after {self.max_retries} retries: {e}")
                return None
    
    def _extract_contact_info(self, text: str) -> Dict[str, str]:
        """Extract contact information using advanced regex patterns"""
        contact_info = {}
        
        # Enhanced phone patterns for Pakistan
        phone_patterns = [
            r'\+92[\s-]?\d{2}[\s-]?\d{3}[\s-]?\d{4}',  # +92 XX XXX XXXX
            r'\+92[\s-]?\d{3}[\s-]?\d{7}',               # +92 XXX XXXXXXX
            r'0\d{2}[\s-]?\d{3}[\s-]?\d{4}',            # 0XX XXX XXXX
            r'\+92[\s-]?\d{4}[\s-]?\d{6}',               # +92 XXXX XXXXXX
            r'Tel[:\s]*([\d\s\-\+]+)',
            r'Phone[:\s]*([\d\s\-\+]+)',
            r'Call[:\s]*([\d\s\-\+]+)',
            r'Contact[:\s]*([\d\s\-\+]+)'
        ]
        
        for pattern in phone_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                phone = matches[0].strip()
                if len(phone) >= 10:  # Minimum phone length
                    contact_info['phone'] = phone
                    break
        
        # Enhanced email patterns
        email_patterns = [
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            r'Email[:\s]*([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,})',
            r'Mail[:\s]*([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,})',
            r'Contact[:\s]*([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,})'
        ]
        
        for pattern in email_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                email = matches[0].strip()
                if '@' in email and '.' in email.split('@')[1]:
                    contact_info['email'] = email
                    break
        
        # Enhanced address patterns
        address_patterns = [
            r'Address[:\s]*([^,\n\r]+(?:Street|Road|Avenue|Lane|Plaza|Mall|Center|Building|Tower|Complex)[^,\n\r]*)',
            r'Location[:\s]*([^,\n\r]+(?:Street|Road|Avenue|Lane|Plaza|Mall|Center|Building|Tower|Complex)[^,\n\r]*)',
            r'([^,\n\r]+(?:Street|Road|Avenue|Lane|Plaza|Mall|Center|Building|Tower|Complex)[^,\n\r]*)',
            r'([^,\n\r]+(?:Karachi|Lahore|Islamabad|Rawalpindi|Faisalabad|Multan|Peshawar|Quetta)[^,\n\r]*)'
        ]
        
        for pattern in address_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                address = matches[0].strip()
                if len(address) > 10:  # Minimum address length
                    contact_info['address'] = address
                    break
        
        # Extract website
        website_patterns = [
            r'Website[:\s]*(https?://[^\s\n\r]+)',
            r'Site[:\s]*(https?://[^\s\n\r]+)',
            r'Web[:\s]*(https?://[^\s\n\r]+)',
            r'(https?://[^\s\n\r]+)'
        ]
        
        for pattern in website_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                website = matches[0].strip()
                if website.startswith(('http://', 'https://')):
                    contact_info['website'] = website
                    break
        
        return contact_info
    
    def _calculate_confidence_score(self, business: ScrapedBusiness) -> float:
        """Calculate confidence score for scraped business data"""
        score = 0.0
        
        # Base score for having a name
        if business.name and len(business.name.strip()) >= 3:
            score += 0.3
        
        # Contact information scores
        if business.email:
            score += 0.25
        if business.phone:
            score += 0.2
        if business.website:
            score += 0.15
        if business.address:
            score += 0.1
        
        # Business type and category matching
        if business.business_type and business.category:
            if business.business_type.lower() in business.category.lower():
                score += 0.1
        
        # Source reliability
        if business.source in ["pakistan_business_directory", "yellow_pages_pk"]:
            score += 0.05
        
        return min(score, 1.0)
    
    def scrape_business_directory(self, source_name: str, category: str, city: str) -> List[ScrapedBusiness]:
        """Scrape business directory with enhanced techniques"""
        if source_name not in self.business_sources:
            logger.error(f"Unknown source: {source_name}")
            return []
        
        source_config = self.business_sources[source_name]
        businesses = []
        
        try:
            # Construct search URL
            if "{category}" in source_config["search_pattern"] and "{city}" in source_config["search_pattern"]:
                search_url = source_config["base_url"] + "/" + source_config["search_pattern"].format(
                    category=quote_plus(category),
                    city=quote_plus(city)
                )
            else:
                query = f"{category} {city} pakistan"
                search_url = source_config["base_url"] + "/" + source_config["search_pattern"].format(
                    query=quote_plus(query)
                )
            
            logger.info(f"🔍 Scraping {source_name}: {search_url}")
            
            # Make request
            response = self._make_request(search_url)
            if not response:
                return []
            
            # Parse HTML
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find business listings
            business_elements = []
            for selector in source_config["business_selectors"]:
                elements = soup.select(selector)
                if elements:
                    business_elements.extend(elements)
                    break
            
            if not business_elements:
                logger.warning(f"No business elements found in {source_name}")
                return []
            
            logger.info(f"Found {len(business_elements)} business elements in {source_name}")
            
            # Extract business data
            for element in business_elements[:20]:  # Limit to 20 per source
                business_data = self._extract_business_from_element(
                    element, source_config, category, city, source_name
                )
                if business_data:
                    businesses.append(business_data)
            
        except Exception as e:
            logger.error(f"Error scraping {source_name}: {e}")
        
        return businesses
    
    def _extract_business_from_element(self, element, source_config: Dict, category: str, city: str, source_name: str) -> Optional[ScrapedBusiness]:
        """Extract business information from HTML element"""
        try:
            # Extract business name
            name = None
            for selector in source_config["name_selectors"]:
                name_elem = element.select_one(selector)
                if name_elem:
                    name = name_elem.get_text(strip=True)
                    break
            
            if not name or len(name.strip()) < 3:
                return None
            
            # Create business object
            business = ScrapedBusiness(
                name=name,
                business_type=category,
                city=city,
                source=source_name
            )
            
            # Extract contact information
            text_content = element.get_text()
            contact_info = self._extract_contact_info(text_content)
            
            business.email = contact_info.get('email')
            business.phone = contact_info.get('phone')
            business.address = contact_info.get('address')
            business.website = contact_info.get('website')
            
            # Calculate confidence score
            business.confidence_score = self._calculate_confidence_score(business)
            
            # Only return businesses with reasonable confidence
            if business.confidence_score >= 0.3:
                return business
            
            return None
            
        except Exception as e:
            logger.error(f"Error extracting business data: {e}")
            return None
    
    def scrape_multiple_sources(self, category: str, city: str, max_businesses: int = 100) -> List[ScrapedBusiness]:
        """Scrape multiple business directories concurrently"""
        logger.info(f"🚀 Starting multi-source scraping for {category} in {city}")
        
        all_businesses = []
        
        # Scrape all sources concurrently
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            future_to_source = {
                executor.submit(self.scrape_business_directory, source_name, category, city): source_name
                for source_name in self.business_sources.keys()
            }
            
            for future in concurrent.futures.as_completed(future_to_source):
                source_name = future_to_source[future]
                try:
                    businesses = future.result()
                    all_businesses.extend(businesses)
                    logger.info(f"✅ {source_name}: {len(businesses)} businesses found")
                except Exception as e:
                    logger.error(f"❌ {source_name}: {e}")
        
        # Remove duplicates and sort by confidence
        unique_businesses = self._remove_duplicates(all_businesses)
        sorted_businesses = sorted(unique_businesses, key=lambda x: x.confidence_score, reverse=True)
        
        # Limit results
        final_businesses = sorted_businesses[:max_businesses]
        
        logger.info(f"🎯 Total unique businesses found: {len(final_businesses)}")
        return final_businesses
    
    def _remove_duplicates(self, businesses: List[ScrapedBusiness]) -> List[ScrapedBusiness]:
        """Remove duplicate businesses based on name and phone"""
        seen = set()
        unique_businesses = []
        
        for business in businesses:
            # Create unique identifier
            identifier = f"{business.name.lower().strip()}_{business.phone or 'no_phone'}_{business.city or 'no_city'}"
            
            if identifier not in seen:
                seen.add(identifier)
                unique_businesses.append(business)
        
        return unique_businesses
    
    def get_scraping_statistics(self) -> Dict[str, Any]:
        """Get scraping statistics"""
        return {
            "total_sources": len(self.business_sources),
            "proxy_count": len(self.proxy_list),
            "headers_variations": len(self.headers_list),
            "rate_limiting": f"{self.min_delay}-{self.max_delay} seconds",
            "max_retries": self.max_retries,
            "sources": list(self.business_sources.keys())
        }

# Example usage
if __name__ == "__main__":
    scraper = EnhancedScraper()
    
    # Test the enhanced scraper
    businesses = scraper.scrape_multiple_sources("Technology", "Karachi", 15)
    
    print(f"\n🎯 Found {len(businesses)} businesses:")
    for i, business in enumerate(businesses, 1):
        print(f"\n{i}. {business.name}")
        print(f"   Type: {business.business_type}")
        print(f"   City: {business.city}")
        print(f"   Confidence: {business.confidence_score:.2f}")
        if business.email:
            print(f"   Email: {business.email}")
        if business.phone:
            print(f"   Phone: {business.phone}")
        if business.website:
            print(f"   Website: {business.website}")
    
    print(f"\n📊 Scraping Statistics:")
    stats = scraper.get_scraping_statistics()
    for key, value in stats.items():
        print(f"   {key}: {value}")

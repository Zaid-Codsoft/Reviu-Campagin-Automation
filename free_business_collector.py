#!/usr/bin/env python3
"""
Free Business Collector for Reviu.pk
Uses free APIs and enhanced scraping techniques
"""

import json
import random
import logging
import requests
import time
from typing import List, Dict, Any, Optional
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin, urlparse
import concurrent.futures
from dataclasses import dataclass

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class BusinessData:
    """Structured business data"""
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    website: Optional[str] = None
    business_type: Optional[str] = None
    category: Optional[str] = None
    city: Optional[str] = None
    verified: bool = False
    source: str = "free_api"

class FreeBusinessCollector:
    """Free business collector using free APIs and enhanced scraping"""
    
    def __init__(self):
        """Initialize the free business collector"""
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        
        # Free API endpoints
        self.nominatim_base = "https://nominatim.openstreetmap.org"
        self.duckduckgo_base = "https://api.duckduckgo.com"
        
        # Enhanced scraping sources
        self.scraping_sources = {
            "pakistan_business_directory": "https://www.pakistanbusinessdirectory.com",
            "yellow_pages_pk": "https://www.yellowpages.pk",
            "pakistan_companies": "https://www.pakistan-companies.com"
        }
        
        # Rate limiting
        self.last_request_time = 0
        self.min_delay = 1  # 1 second between requests
        
    def _rate_limit(self):
        """Implement rate limiting"""
        current_time = time.time()
        if current_time - self.last_request_time < self.min_delay:
            time.sleep(self.min_delay - (current_time - self.last_request_time))
        self.last_request_time = time.time()
    
    def search_businesses_duckduckgo(self, query: str, city: str) -> List[BusinessData]:
        """Search for businesses using DuckDuckGo (free)"""
        try:
            self._rate_limit()
            
            # DuckDuckGo doesn't have a public API, but we can scrape their results
            search_url = f"https://duckduckgo.com/html/?q={query}+{city}+pakistan+business"
            
            response = self.session.get(search_url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            businesses = []
            
            # Extract business information from search results
            for result in soup.find_all('div', class_='result'):
                title_elem = result.find('h2')
                if not title_elem:
                    continue
                    
                title = title_elem.get_text(strip=True)
                snippet = result.find('div', class_='snippet')
                snippet_text = snippet.get_text(strip=True) if snippet else ""
                
                # Extract website if available
                website = None
                link_elem = result.find('a', class_='result__url')
                if link_elem:
                    website = link_elem.get_text(strip=True)
                
                # Create business data
                business = BusinessData(
                    name=title,
                    business_type=query,
                    city=city,
                    source="duckduckgo_search"
                )
                
                # Try to extract more details from snippet
                if snippet_text:
                    # Extract phone numbers
                    phone_match = re.search(r'(\+92[\d\s-]+|[\d\s-]{10,})', snippet_text)
                    if phone_match:
                        business.phone = phone_match.group(1)
                    
                    # Extract email addresses
                    email_match = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', snippet_text)
                    if email_match:
                        business.email = email_match.group(0)
                
                businesses.append(business)
            
            logger.info(f"Found {len(businesses)} businesses from DuckDuckGo for {query} in {city}")
            return businesses[:20]  # Limit results
            
        except Exception as e:
            logger.error(f"Error searching DuckDuckGo: {e}")
            return []
    
    def get_location_data_nominatim(self, city: str, country: str = "Pakistan") -> Optional[Dict]:
        """Get location data using OpenStreetMap Nominatim (free)"""
        try:
            self._rate_limit()
            
            search_query = f"{city}, {country}"
            url = f"{self.nominatim_base}/search"
            params = {
                'q': search_query,
                'format': 'json',
                'limit': 1
            }
            
            response = self.session.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            if data:
                location = data[0]
                return {
                    'lat': float(location['lat']),
                    'lon': float(location['lon']),
                    'display_name': location['display_name'],
                    'city': city
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting location data from Nominatim: {e}")
            return None
    
    def scrape_business_directory(self, category: str, city: str) -> List[BusinessData]:
        """Scrape business directories for Pakistan businesses"""
        businesses = []
        
        # Enhanced scraping with multiple sources
        for source_name, base_url in self.scraping_sources.items():
            try:
                self._rate_limit()
                
                # Construct search URL based on source
                if "pakistan_business_directory" in source_name:
                    search_url = f"{base_url}/search?q={category}+{city}"
                elif "yellow_pages_pk" in source_name:
                    search_url = f"{base_url}/search?category={category}&city={city}"
                else:
                    search_url = f"{base_url}/search?q={category}+{city}+pakistan"
                
                response = self.session.get(search_url, timeout=10)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Extract business listings (generic approach)
                business_elements = soup.find_all(['div', 'li', 'tr'], class_=re.compile(r'(business|company|listing|item)', re.I))
                
                for elem in business_elements[:15]:  # Limit per source
                    business_data = self._extract_business_from_element(elem, category, city, source_name)
                    if business_data:
                        businesses.append(business_data)
                
                logger.info(f"Scraped {len(business_elements)} potential businesses from {source_name}")
                
            except Exception as e:
                logger.error(f"Error scraping {source_name}: {e}")
                continue
        
        return businesses
    
    def _extract_business_from_element(self, element, category: str, city: str, source: str) -> Optional[BusinessData]:
        """Extract business information from HTML element"""
        try:
            # Try to find business name
            name_elem = element.find(['h1', 'h2', 'h3', 'h4', 'strong', 'b'])
            if not name_elem:
                return None
                
            name = name_elem.get_text(strip=True)
            if not name or len(name) < 3:
                return None
            
            # Create business data
            business = BusinessData(
                name=name,
                business_type=category,
                city=city,
                source=source
            )
            
            # Try to extract contact information
            text_content = element.get_text()
            
            # Extract phone numbers
            phone_patterns = [
                r'\+92[\d\s-]+',
                r'[\d\s-]{10,}',
                r'Tel[:\s]*([\d\s-]+)',
                r'Phone[:\s]*([\d\s-]+)'
            ]
            
            for pattern in phone_patterns:
                phone_match = re.search(pattern, text_content)
                if phone_match:
                    business.phone = phone_match.group(0).strip()
                    break
            
            # Extract email addresses
            email_match = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text_content)
            if email_match:
                business.email = email_match.group(0)
            
            # Extract website
            website_elem = element.find('a', href=True)
            if website_elem:
                href = website_elem['href']
                if href.startswith('http'):
                    business.website = href
                else:
                    business.website = urljoin(self.scraping_sources.get(source, ''), href)
            
            # Extract address
            address_patterns = [
                r'Address[:\s]*([^,\n]+)',
                r'Location[:\s]*([^,\n]+)',
                r'([^,\n]+(?:Street|Road|Avenue|Lane|Plaza|Mall|Center))'
            ]
            
            for pattern in address_patterns:
                address_match = re.search(pattern, text_content)
                if address_match:
                    business.address = address_match.group(1).strip()
                    break
            
            return business
            
        except Exception as e:
            logger.error(f"Error extracting business data: {e}")
            return None
    
    def collect_businesses(self, category: str, city: str, target_count: int = 100) -> List[BusinessData]:
        """Collect businesses using multiple free sources"""
        logger.info(f"🚀 Collecting businesses for {category} in {city} (target: {target_count})")
        
        all_businesses = []
        
        # Method 1: DuckDuckGo search
        logger.info("🔍 Searching DuckDuckGo...")
        ddg_businesses = self.search_businesses_duckduckgo(category, city)
        all_businesses.extend(ddg_businesses)
        
        # Method 2: Business directory scraping
        logger.info("🌐 Scraping business directories...")
        scraped_businesses = self.scrape_business_directory(category, city)
        all_businesses.extend(scraped_businesses)
        
        # Method 3: Get location data for validation
        logger.info("📍 Getting location data...")
        location_data = self.get_location_data_nominatim(city)
        if location_data:
            logger.info(f"📍 Location validated: {location_data['display_name']}")
        
        # Remove duplicates and filter
        unique_businesses = self._remove_duplicates(all_businesses)
        filtered_businesses = self._filter_businesses(unique_businesses, category, city)
        
        # Limit to target count
        final_businesses = filtered_businesses[:target_count]
        
        logger.info(f"✅ Collected {len(final_businesses)} unique businesses")
        return final_businesses
    
    def _remove_duplicates(self, businesses: List[BusinessData]) -> List[BusinessData]:
        """Remove duplicate businesses based on name and phone"""
        seen = set()
        unique_businesses = []
        
        for business in businesses:
            # Create a unique identifier
            identifier = f"{business.name.lower().strip()}_{business.phone or 'no_phone'}"
            
            if identifier not in seen:
                seen.add(identifier)
                unique_businesses.append(business)
        
        return unique_businesses
    
    def _filter_businesses(self, businesses: List[BusinessData], category: str, city: str) -> List[BusinessData]:
        """Filter businesses based on relevance"""
        filtered = []
        
        for business in businesses:
            # Must have a name
            if not business.name or len(business.name.strip()) < 3:
                continue
            
            # Must be in the target city (case-insensitive)
            if business.city and city.lower() not in business.city.lower():
                continue
            
            # Must match category (case-insensitive)
            if business.business_type and category.lower() not in business.business_type.lower():
                continue
            
            filtered.append(business)
        
        return filtered
    
    def get_categories(self) -> List[str]:
        """Get available business categories"""
        return [
            "Technology", "Healthcare", "Education", "Finance", "Real Estate",
            "Restaurant", "Retail", "Manufacturing", "Consulting", "Legal",
            "Marketing", "Transportation", "Construction", "Entertainment", "Automotive"
        ]
    
    def get_cities(self) -> List[str]:
        """Get available cities in Pakistan"""
        return [
            "Karachi", "Lahore", "Islamabad", "Rawalpindi", "Faisalabad",
            "Multan", "Peshawar", "Quetta", "Gujranwala", "Sialkot",
            "Bahawalpur", "Sargodha", "Sukkur", "Jhang", "Sheikhupura"
        ]
    
    def get_scraping_statistics(self) -> Dict[str, Any]:
        """Get scraping statistics"""
        return {
            "total_sources": len(self.scraping_sources),
            "free_apis_used": ["DuckDuckGo", "OpenStreetMap Nominatim"],
            "scraping_methods": ["Enhanced Directory Scraping", "Search Engine Results"],
            "rate_limiting": f"{self.min_delay} second delay between requests"
        }

# Example usage
if __name__ == "__main__":
    collector = FreeBusinessCollector()
    
    # Test the collector
    businesses = collector.collect_businesses("Technology", "Karachi", 10)
    
    print(f"Found {len(businesses)} businesses:")
    for business in businesses:
        print(f"- {business.name} ({business.business_type}) in {business.city}")
        if business.email:
            print(f"  Email: {business.email}")
        if business.phone:
            print(f"  Phone: {business.phone}")
        print()

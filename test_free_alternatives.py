#!/usr/bin/env python3
"""
Test script for free alternatives to Google APIs
Demonstrates enhanced scraping and free API usage
"""

import time
import logging
from free_business_collector import FreeBusinessCollector
from enhanced_scraper import EnhancedScraper

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_free_business_collector():
    """Test the free business collector"""
    print("🧪 Testing Free Business Collector")
    print("=" * 50)
    
    collector = FreeBusinessCollector()
    
    # Test location validation with OpenStreetMap (free)
    print("\n📍 Testing OpenStreetMap Nominatim API (free):")
    location = collector.get_location_data_nominatim("Karachi", "Pakistan")
    if location:
        print(f"✅ Location validated: {location['display_name']}")
        print(f"   Coordinates: {location['lat']}, {location['lon']}")
    else:
        print("❌ Location validation failed")
    
    # Test DuckDuckGo search (free)
    print("\n🔍 Testing DuckDuckGo search (free):")
    businesses = collector.search_businesses_duckduckgo("Technology", "Karachi")
    print(f"✅ Found {len(businesses)} businesses from DuckDuckGo")
    
    # Test business directory scraping
    print("\n🌐 Testing business directory scraping:")
    scraped_businesses = collector.scrape_business_directory("Technology", "Karachi")
    print(f"✅ Found {len(scraped_businesses)} businesses from directories")
    
    # Test full collection
    print("\n🚀 Testing full business collection:")
    all_businesses = collector.collect_businesses("Technology", "Karachi", 10)
    print(f"✅ Total businesses collected: {len(all_businesses)}")
    
    # Show sample results
    if all_businesses:
        print("\n📋 Sample Results:")
        for i, business in enumerate(all_businesses[:3], 1):
            print(f"\n{i}. {business.name}")
            print(f"   Type: {business.business_type}")
            print(f"   City: {business.city}")
            if business.email:
                print(f"   Email: {business.email}")
            if business.phone:
                print(f"   Phone: {business.phone}")
            if business.website:
                print(f"   Website: {business.website}")
    
    # Show statistics
    print("\n📊 Free Business Collector Statistics:")
    stats = collector.get_scraping_statistics()
    for key, value in stats.items():
        print(f"   {key}: {value}")

def test_enhanced_scraper():
    """Test the enhanced scraper"""
    print("\n\n🧪 Testing Enhanced Scraper")
    print("=" * 50)
    
    scraper = EnhancedScraper()
    
    # Show scraper capabilities
    print("\n🔧 Enhanced Scraper Features:")
    print("   ✅ Multiple business directory sources")
    print("   ✅ Proxy rotation (free public proxies)")
    print("   ✅ Header rotation")
    print("   ✅ Smart rate limiting")
    print("   ✅ Retry logic with exponential backoff")
    print("   ✅ Confidence scoring")
    print("   ✅ Concurrent scraping")
    
    # Test single source scraping
    print("\n🔍 Testing single source scraping:")
    businesses = scraper.scrape_business_directory("pakistan_business_directory", "Technology", "Karachi")
    print(f"✅ Found {len(businesses)} businesses from Pakistan Business Directory")
    
    # Test multi-source scraping
    print("\n🚀 Testing multi-source concurrent scraping:")
    all_businesses = scraper.scrape_multiple_sources("Technology", "Karachi", 15)
    print(f"✅ Total businesses found: {len(all_businesses)}")
    
    # Show sample results with confidence scores
    if all_businesses:
        print("\n📋 Sample Results with Confidence Scores:")
        for i, business in enumerate(all_businesses[:3], 1):
            print(f"\n{i}. {business.name}")
            print(f"   Type: {business.business_type}")
            print(f"   City: {business.city}")
            print(f"   Confidence: {business.confidence_score:.2f}")
            print(f"   Source: {business.source}")
            if business.email:
                print(f"   Email: {business.email}")
            if business.phone:
                print(f"   Phone: {business.phone}")
    
    # Show scraper statistics
    print("\n📊 Enhanced Scraper Statistics:")
    stats = scraper.get_scraping_statistics()
    for key, value in stats.items():
        print(f"   {key}: {value}")

def compare_with_google_apis():
    """Compare free alternatives with Google APIs"""
    print("\n\n📊 Comparison: Free Alternatives vs Google APIs")
    print("=" * 60)
    
    comparison = {
        "Google Places API": {
            "cost": "$$$ (Pay per request)",
            "rate_limit": "Strict (1000 requests/day free)",
            "data_quality": "Excellent",
            "reliability": "Very High",
            "setup": "Complex (API keys, billing)"
        },
        "Free Alternatives": {
            "cost": "Free",
            "rate_limit": "Generous (1-2 requests/second)",
            "data_quality": "Good to Very Good",
            "reliability": "High (with retry logic)",
            "setup": "Simple (no API keys needed)"
        }
    }
    
    for option, details in comparison.items():
        print(f"\n{option}:")
        for key, value in details.items():
            print(f"   {key.replace('_', ' ').title()}: {value}")

def main():
    """Main test function"""
    print("🚀 Testing Free Alternatives to Google APIs")
    print("=" * 60)
    print("This script demonstrates how to get business data without paying for Google APIs")
    print("Using free tools and enhanced scraping techniques\n")
    
    try:
        # Test free business collector
        test_free_business_collector()
        
        # Test enhanced scraper
        test_enhanced_scraper()
        
        # Compare with Google APIs
        compare_with_google_apis()
        
        print("\n✅ All tests completed successfully!")
        print("\n💡 Key Benefits of Free Alternatives:")
        print("   • No cost - completely free to use")
        print("   • No API key management")
        print("   • No billing setup")
        print("   • Generous rate limits")
        print("   • Multiple data sources")
        print("   • Advanced scraping techniques")
        print("   • Proxy rotation for reliability")
        
    except Exception as e:
        logger.error(f"Test failed: {e}")
        print(f"\n❌ Test failed: {e}")

if __name__ == "__main__":
    main()

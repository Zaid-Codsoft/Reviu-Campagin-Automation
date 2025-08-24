#!/usr/bin/env python3
"""
Email Validation Demo - Shows how the system prevents bounced emails
"""

import logging
from business_collector import BusinessCollector
from email_validator import EmailValidator
from data_manager import DataManager

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    """Demonstrate automatic email validation during lead generation"""
    print("🚀 Reviu.pk Automatic Email Validation Demo")
    print("=" * 50)
    
    # Initialize components
    collector = BusinessCollector()
    data_manager = DataManager()
    
    print("\n🔍 Step 1: Collecting businesses...")
    businesses = collector.collect_businesses('Technology', 'Karachi', 10)
    print(f"✅ Collected {len(businesses)} businesses")
    
    # Show some sample businesses
    print("\n📋 Sample businesses collected:")
    for i, business in enumerate(businesses[:5]):
        print(f"  {i+1}. {business['name']} - {business['email']}")
    
    print("\n🔍 Step 2: Email validation happens automatically during collection...")
    print(f"✅ Only businesses with valid, deliverable emails are returned")
    
    print("\n🔍 Step 3: Saving validated businesses...")
    saved_count = data_manager.save_leads(businesses)
    print(f"✅ Saved {saved_count} validated businesses to CSV")
    
    print("\n💡 Key Benefits of Automatic Email Validation:")
    print("  • Email validation happens automatically during lead generation")
    print("  • No separate validation step needed")
    print("  • Prevents bounced emails like 'info@greencitydigital.com'")
    print("  • Only businesses with deliverable emails are collected")
    print("  • Improves email campaign success rates from the start")
    
    print("\n🎯 Next Steps:")
    print("  1. Generate personalized emails for validated businesses")
    print("  2. Send emails with confidence they'll be delivered")
    print("  3. Monitor campaign results")
    
    print("\n" + "=" * 50)
    print("✅ Email validation demo completed!")

if __name__ == "__main__":
    main()

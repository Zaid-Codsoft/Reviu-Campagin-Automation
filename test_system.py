#!/usr/bin/env python3
"""
Test Script for Reviu.pk Lead Generation System
Tests all major components to ensure they work correctly
"""

import os
import sys
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_imports():
    """Test if all required modules can be imported"""
    try:
        logger.info("🔍 Testing module imports...")
        
        from business_collector import BusinessCollector
        logger.info("✅ BusinessCollector imported successfully")
        
        from email_generator import EmailGenerator
        logger.info("✅ EmailGenerator imported successfully")
        
        from email_sender import EmailSender
        logger.info("✅ EmailSender imported successfully")
        
        from data_manager import DataManager
        logger.info("✅ DataManager imported successfully")
        
        return True
        
    except ImportError as e:
        logger.error(f"❌ Import error: {e}")
        return False

def test_business_collector():
    """Test the business collector"""
    try:
        logger.info("🔍 Testing BusinessCollector...")
        
        from business_collector import BusinessCollector
        collector = BusinessCollector()
        
        # Test categories
        categories = collector.get_categories()
        logger.info(f"✅ Found {len(categories)} categories: {categories[:3]}...")
        
        # Test cities
        cities = collector.get_cities()
        logger.info(f"✅ Found {len(cities)} cities: {cities[:3]}...")
        
        # Test business collection
        businesses = collector.collect_businesses("Technology", "Karachi", 5)
        logger.info(f"✅ Collected {len(businesses)} businesses")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ BusinessCollector test failed: {e}")
        return False

def test_data_manager():
    """Test the data manager"""
    try:
        logger.info("🔍 Testing DataManager...")
        
        from data_manager import DataManager
        data_manager = DataManager()
        
        # Test file creation
        logger.info("✅ DataManager initialized successfully")
        
        # Test statistics
        stats = data_manager.get_campaign_statistics()
        logger.info(f"✅ Campaign statistics: {stats}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ DataManager test failed: {e}")
        return False

def test_environment():
    """Test environment variables"""
    try:
        logger.info("🔍 Testing environment variables...")
        
        required_vars = [
            'GEMINI_API_KEY',
            'SMTP_SERVER',
            'SMTP_PORT',
            'SMTP_USERNAME',
            'SMTP_PASSWORD'
        ]
        
        missing_vars = []
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if missing_vars:
            logger.warning(f"⚠️ Missing environment variables: {missing_vars}")
            logger.warning("Please check your .env file")
            return False
        else:
            logger.info("✅ All required environment variables found")
            return True
            
    except Exception as e:
        logger.error(f"❌ Environment test failed: {e}")
        return False

def test_flask_app():
    """Test if Flask app can be created"""
    try:
        logger.info("🔍 Testing Flask app creation...")
        
        # Temporarily disable logging to avoid import warnings
        logging.getLogger('werkzeug').setLevel(logging.ERROR)
        
        from app import app
        logger.info("✅ Flask app created successfully")
        
        # Test basic routes
        with app.test_client() as client:
            response = client.get('/')
            if response.status_code == 200:
                logger.info("✅ Main route accessible")
            else:
                logger.warning(f"⚠️ Main route returned status {response.status_code}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Flask app test failed: {e}")
        return False

def main():
    """Run all tests"""
    logger.info("🚀 Starting Reviu.pk Lead Generation System Tests...")
    
    tests = [
        ("Module Imports", test_imports),
        ("Environment Variables", test_environment),
        ("Business Collector", test_business_collector),
        ("Data Manager", test_data_manager),
        ("Flask App", test_flask_app)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        logger.info(f"\n{'='*50}")
        logger.info(f"🧪 Running: {test_name}")
        logger.info(f"{'='*50}")
        
        try:
            success = test_func()
            results.append((test_name, success))
            
            if success:
                logger.info(f"✅ {test_name}: PASSED")
            else:
                logger.error(f"❌ {test_name}: FAILED")
                
        except Exception as e:
            logger.error(f"❌ {test_name}: ERROR - {e}")
            results.append((test_name, False))
    
    # Summary
    logger.info(f"\n{'='*50}")
    logger.info("📊 TEST SUMMARY")
    logger.info(f"{'='*50}")
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        logger.info(f"{status} {test_name}")
    
    logger.info(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("🎉 All tests passed! System is ready to use.")
        return True
    else:
        logger.error(f"⚠️ {total - passed} tests failed. Please check the errors above.")
        return False

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        logger.info("\n⏹️ Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        sys.exit(1)

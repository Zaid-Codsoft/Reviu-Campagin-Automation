#!/usr/bin/env python3
"""
Test script for Gemini integration in the Flask app
"""

import requests
import json
import time

def test_gemini_lead_generation():
    """Test Gemini-powered lead generation"""
    print("🧠 Testing Gemini-Powered Lead Generation")
    print("=" * 50)
    
    try:
        response = requests.post('http://localhost:5000/api/generate_leads', 
                               json={
                                   'category': 'Technology',
                                   'city': 'Islamabad',
                                   'target_count': 10,
                                   'use_ai': True
                               })
        
        if response.status_code == 200:
            data = response.json()
            if data['success']:
                print(f"✅ Success: {data['message']}")
                print(f"📊 Generated {data['leads_count']} leads")
                if 'ai_insights' in data:
                    insights = data['ai_insights']
                    print(f"🎯 High Priority: {insights['high_priority']}")
                    print(f"🎯 Medium Priority: {insights['medium_priority']}")
                    print(f"🎯 Low Priority: {insights['low_priority']}")
                    print(f"📈 Average Lead Score: {insights['average_lead_score']}%")
                return True
            else:
                print(f"❌ Failed: {data['message']}")
                return False
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Make sure Flask app is running")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_gemini_campaign_generation():
    """Test Gemini-powered campaign generation"""
    print("\n🎯 Testing Gemini-Powered Campaign Generation")
    print("=" * 50)
    
    try:
        response = requests.post('http://localhost:5000/api/generate_gemini_campaign', 
                               json={
                                   'category': 'Technology',
                                   'city': 'Islamabad',
                                   'target_count': 10
                               })
        
        if response.status_code == 200:
            data = response.json()
            if data['success']:
                print(f"✅ Success: {data['message']}")
                print(f"📧 Generated {data['email_templates_count']} email templates")
                if 'email_templates' in data:
                    for i, template in enumerate(data['email_templates'], 1):
                        print(f"   {i}. Subject: {template['subject']}")
                return True
            else:
                print(f"❌ Failed: {data['message']}")
                return False
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Make sure Flask app is running")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_gemini_insights():
    """Test Gemini insights endpoint"""
    print("\n📊 Testing Gemini Insights")
    print("=" * 50)
    
    try:
        response = requests.get('http://localhost:5000/api/get_gemini_insights')
        
        if response.status_code == 200:
            data = response.json()
            if data['success']:
                print(f"✅ Success: {data['message']}")
                insights = data['insights']
                print(f"📈 Total Leads: {insights['total_leads']}")
                print(f"✅ Verified Leads: {insights['verified_leads']}")
                print(f"📊 Verification Rate: {insights['verification_rate']}%")
                if insights['categories']:
                    print(f"🏷️ Categories: {', '.join(insights['categories'])}")
                if insights['cities']:
                    print(f"🏙️ Cities: {', '.join(insights['cities'])}")
                return True
            else:
                print(f"❌ Failed: {data['message']}")
                return False
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Make sure Flask app is running")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    print("🚀 Gemini Integration Test Suite")
    print("=" * 60)
    print("Make sure your Flask app is running on http://localhost:5000")
    print("=" * 60)
    
    results = {}
    results['lead_gen'] = test_gemini_lead_generation()
    results['campaign_gen'] = test_gemini_campaign_generation()
    results['insights'] = test_gemini_insights()
    
    print("\n" + "=" * 60)
    print("📋 Test Results Summary")
    print("=" * 60)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name.replace('_', ' ').title()}: {status}")
    
    all_passed = all(results.values())
    if all_passed:
        print("\n🎉 All tests passed! Gemini integration is working correctly.")
    else:
        print("\n⚠️ Some tests failed. Check the Flask app logs for errors.")
    
    return all_passed

if __name__ == "__main__":
    main()

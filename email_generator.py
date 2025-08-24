#!/usr/bin/env python3
"""
Professional Email Generator for Reviu.pk
Uses Google Gemini API to generate personalized outreach emails
"""

import os
import logging
import google.generativeai as genai
from typing import Dict, Any, List
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class EmailGenerator:
    """Professional email generator using Gemini API"""
    
    def __init__(self):
        """Initialize the email generator with Gemini API"""
        try:
            # Configure Gemini API
            api_key = os.getenv('GEMINI_API_KEY')
            if not api_key:
                raise ValueError("GEMINI_API_KEY not found in environment variables")
            
            genai.configure(api_key=api_key)
            
            # Initialize Gemini model
            self.model = genai.GenerativeModel('gemini-2.5-pro')
            logger.info("✅ Gemini API initialized with model: gemini-2.5-pro")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Gemini API: {e}")
            raise
    
    def generate_personalized_email(self, business: Dict[str, Any]) -> str:
        """Generate a personalized email for a specific business"""
        try:
            business_name = business.get('name', 'Business')
            business_type = business.get('business_type', 'Business')
            city = business.get('address', '').split(', ')[-1] if business.get('address') else 'Pakistan'
            
            # Enhanced prompt for professional email generation
            enhanced_prompt = f"""
Generate a professional, personalized outreach email for a business listing service. 

Business Details:
- Name: {business_name}
- Type: {business_type}
- Location: {city}

Requirements:
1. Start with "Dear {business_name} Team,"
2. Introduce yourself as Zaid from Reviu.pk
3. Explain the benefits of listing their business in Pakistan's leading business directory
4. Mention specific benefits like increased visibility, customer reach, and business growth
5. Include your contact information: info@reviu.pk, www.reviu.pk, 03556924128
6. Ask them to register using: https://www.reviu.pk/auth/business/signup
7. Keep it professional, polite, and under 150 words
8. Make it specific to their business type and location
9. End with a professional closing

Generate ONLY the email content, no explanations or additional text.
"""
            
            # Generate email using Gemini
            response = self.model.generate_content(enhanced_prompt)
            
            if response and response.text:
                email_content = response.text.strip()
                # Clean the generated content
                cleaned_email = self._clean_email_content(email_content, business_name)
                logger.info(f"✅ Generated personalized email for {business_name}")
                return cleaned_email
            else:
                logger.warning(f"⚠️ Empty response from Gemini for {business_name}")
                return self._generate_fallback_email(business)
                
        except Exception as e:
            logger.error(f"❌ Error generating email for {business.get('name', 'Unknown')}: {e}")
            return self._generate_fallback_email(business)
    
    def _clean_email_content(self, content: str, business_name: str) -> str:
        """Clean and format the generated email content"""
        try:
            # Remove common unwanted prefixes
            unwanted_prefixes = [
                "Of course.", "Here is a professional email:", "Here's a professional email:",
                "I'll help you create a professional email:", "Here's a personalized email:",
                "Here's a professional outreach email:", "Here's a personalized outreach email:"
            ]
            
            cleaned_content = content
            for prefix in unwanted_prefixes:
                if cleaned_content.startswith(prefix):
                    cleaned_content = cleaned_content[len(prefix):].strip()
            
            # Remove markdown formatting
            cleaned_content = cleaned_content.replace('**', '').replace('*', '')
            
            # Ensure proper greeting
            if not cleaned_content.startswith(f"Dear {business_name} Team,"):
                cleaned_content = f"Dear {business_name} Team,\n\n{cleaned_content}"
            
            # Ensure proper closing
            if not cleaned_content.strip().endswith(("Best regards,", "Sincerely,", "Thank you,")):
                cleaned_content += "\n\nBest regards,\nZaid\nReviu.pk Team"
            
            return cleaned_content.strip()
            
        except Exception as e:
            logger.error(f"❌ Error cleaning email content: {e}")
            return content
    
    def _generate_fallback_email(self, business: Dict[str, Any]) -> str:
        """Generate a fallback email if Gemini fails"""
        business_name = business.get('name', 'Business')
        business_type = business.get('business_type', 'Business')
        city = business.get('address', '').split(', ')[-1] if business.get('address') else 'Pakistan'
        
        fallback_email = f"""Dear {business_name} Team,

I hope this email finds you well. My name is Zaid, and I'm reaching out from Reviu.pk, Pakistan's leading business directory platform.

I noticed your {business_type} business in {city} and believe you would greatly benefit from listing with us. Our platform offers:

• Increased online visibility and customer reach
• Professional business profile with contact details
• Integration with our extensive network of potential customers
• Enhanced credibility and trust among local consumers

We would love to help showcase your business to our growing community of users looking for quality services in {city}.

To get started, please visit: https://www.reviu.pk/auth/business/signup

If you have any questions, feel free to reach out to me directly at info@reviu.pk or call 03556924128.

Looking forward to partnering with you!

Best regards,
Zaid
Reviu.pk Team
info@reviu.pk | www.reviu.pk | 03556924128"""
        
        return fallback_email
    
    def generate_bulk_emails(self, businesses: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate emails for multiple businesses"""
        try:
            logger.info(f"📧 Generating personalized emails for {len(businesses)} businesses...")
            
            generated_emails = []
            
            for i, business in enumerate(businesses, 1):
                try:
                    email_content = self.generate_personalized_email(business)
                    
                    generated_email = {
                        'business_name': business.get('name', 'Unknown'),
                        'business_type': business.get('business_type', 'Unknown'),
                        'email': business.get('email', ''),
                        'city': business.get('address', '').split(', ')[-1] if business.get('address') else 'Unknown',
                        'generated_email': email_content,
                        'status': 'generated'
                    }
                    
                    generated_emails.append(generated_email)
                    logger.info(f"✅ Generated email {i}/{len(businesses)} for {business.get('name', 'Unknown')}")
                    
                except Exception as e:
                    logger.error(f"❌ Error generating email for {business.get('name', 'Unknown')}: {e}")
                    
                    # Add failed email with fallback
                    fallback_email = self._generate_fallback_email(business)
                    generated_email = {
                        'business_name': business.get('name', 'Unknown'),
                        'business_type': business.get('business_type', 'Unknown'),
                        'email': business.get('email', ''),
                        'city': business.get('address', '').split(', ')[-1] if business.get('address') else 'Unknown',
                        'generated_email': fallback_email,
                        'status': 'fallback_generated'
                    }
                    
                    generated_emails.append(generated_email)
            
            logger.info(f"🎯 Successfully generated {len(generated_emails)} emails")
            return generated_emails
            
        except Exception as e:
            logger.error(f"❌ Error in bulk email generation: {e}")
            return []
    
    def test_connection(self) -> bool:
        """Test the Gemini API connection"""
        try:
            test_prompt = "Generate a simple test email greeting."
            response = self.model.generate_content(test_prompt)
            if response and response.text:
                logger.info("✅ Gemini API connection test successful")
                return True
            else:
                logger.warning("⚠️ Gemini API connection test failed - empty response")
                return False
        except Exception as e:
            logger.error(f"❌ Gemini API connection test failed: {e}")
            return False

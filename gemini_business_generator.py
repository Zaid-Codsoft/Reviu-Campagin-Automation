#!/usr/bin/env python3
"""
Gemini Business Generator
Uses Google's Gemini AI to generate realistic business data for specific categories and cities
"""

import os
import json
import logging
import csv
from typing import List, Dict, Any, Set
from dataclasses import dataclass
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class BusinessData:
    """Business data structure"""
    name: str
    email: str
    phone: str
    address: str
    website: str
    business_type: str
    category: str
    city: str
    verified: bool
    source: str
    description: str = ""
    employees: str = ""
    founded_year: str = ""
    services: str = ""

class GeminiBusinessGenerator:
    """Generate business data using Gemini AI"""
    
    def __init__(self):
        """Initialize Gemini API"""
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            logger.warning("⚠️ GEMINI_API_KEY not found in environment variables. Using fallback mode only.")
            self.model = None
            self.fallback_mode = True
        else:
            try:
                genai.configure(api_key=api_key)
                self.model = genai.GenerativeModel('gemini-1.5-flash')
                self.fallback_mode = False
                logger.info("✅ Gemini Business Generator initialized successfully")
            except Exception as e:
                logger.error(f"❌ Failed to initialize Gemini API: {e}")
                logger.warning("⚠️ Falling back to sample data mode")
                self.model = None
                self.fallback_mode = True
        
        # Initialize duplicate prevention
        self.existing_names: Set[str] = set()
        self.existing_emails: Set[str] = set()
        self._load_existing_leads()
    
    def _load_existing_leads(self):
        """Load existing leads from lead history to prevent duplicates"""
        try:
            lead_history_file = "data/lead_history.csv"
            if os.path.exists(lead_history_file):
                with open(lead_history_file, 'r', encoding='utf-8') as file:
                    reader = csv.DictReader(file)
                    for row in reader:
                        # Store existing names and emails for duplicate checking
                        if row.get('name'):
                            self.existing_names.add(row['name'].strip().lower())
                        if row.get('email'):
                            self.existing_emails.add(row['email'].strip().lower())
                
                logger.info(f"✅ Loaded {len(self.existing_names)} existing business names and {len(self.existing_emails)} emails for duplicate prevention")
            else:
                logger.info("📁 No existing lead history found, starting fresh")
        except Exception as e:
            logger.warning(f"⚠️ Could not load existing leads for duplicate prevention: {e}")
    
    def _is_duplicate(self, business: BusinessData) -> bool:
        """Check if a business is a duplicate based on name or email"""
        business_name = business.name.strip().lower()
        business_email = business.email.strip().lower()
        
        # Check for exact matches
        if business_name in self.existing_names:
            logger.debug(f"Duplicate name found: {business.name}")
            return True
        
        if business_email in self.existing_emails:
            logger.debug(f"Duplicate email found: {business.email}")
            return True
        
        # Check for similar names (fuzzy matching for common variations)
        for existing_name in self.existing_names:
            if self._names_are_similar(business_name, existing_name):
                logger.debug(f"Similar name found: {business.name} vs {existing_name}")
                return True
        
        return False
    
    def _names_are_similar(self, name1: str, name2: str) -> bool:
        """Check if two business names are similar (fuzzy matching)"""
        # Remove common words and punctuation
        common_words = {'pvt', 'ltd', 'limited', 'company', 'co', 'corp', 'corporation', 'solutions', 'services', 'group', 'systems'}
        
        words1 = set(name1.replace('-', ' ').replace('.', ' ').split()) - common_words
        words2 = set(name2.replace('-', ' ').replace('.', ' ').split()) - common_words
        
        # If more than 70% of words match, consider them similar
        if words1 and words2:
            intersection = words1.intersection(words2)
            union = words1.union(words2)
            similarity = len(intersection) / len(union)
            return similarity > 0.7
        
        return False
    
    def generate_businesses(self, category: str, city: str, target_count: int = 10) -> List[BusinessData]:
        """Generate business data using Gemini AI or fallback with duplicate prevention"""
        if self.fallback_mode or not self.model:
            logger.info(f"🔄 Using fallback mode to generate {target_count} businesses for {category} in {city}")
            return self._get_fallback_businesses_with_duplicate_prevention(category, city, target_count)
        
        try:
            logger.info(f"🚀 Generating {target_count} unique businesses for {category} in {city} using Gemini AI")
            
            unique_businesses = []
            attempts = 0
            max_attempts = target_count * 3  # Allow up to 3x attempts to find unique businesses
            
            while len(unique_businesses) < target_count and attempts < max_attempts:
                attempts += 1
                
                # Generate businesses (request more than needed to account for duplicates)
                batch_size = min(target_count * 2, 20)  # Generate up to 20 at a time
                prompt = self._create_business_prompt(category, city, batch_size)
                
                response = self.model.generate_content(prompt)
                businesses = self._parse_gemini_response(response.text, category, city)
                
                # Filter for valid emails and check duplicates
                for business in businesses:
                    if (business.email and '@' in business.email and 
                        business.email != 'info@unknown.com' and 
                        not self._is_duplicate(business)):
                        
                        unique_businesses.append(business)
                        
                        # Add to existing sets to prevent future duplicates in this session
                        self.existing_names.add(business.name.strip().lower())
                        self.existing_emails.add(business.email.strip().lower())
                        
                        if len(unique_businesses) >= target_count:
                            break
                
                logger.info(f"🔄 Attempt {attempts}: Found {len(unique_businesses)} unique businesses out of {len(businesses)} generated")
                
                if len(unique_businesses) < target_count:
                    logger.info(f"🔄 Need {target_count - len(unique_businesses)} more unique businesses, generating another batch...")
            
            if len(unique_businesses) < target_count:
                logger.warning(f"⚠️ Could only generate {len(unique_businesses)} unique businesses out of {target_count} requested after {attempts} attempts")
            
            logger.info(f"✅ Generated {len(unique_businesses)} unique businesses with valid emails using Gemini AI")
            return unique_businesses
            
        except Exception as e:
            logger.error(f"❌ Error generating businesses with Gemini: {e}")
            # Return sample data as fallback with duplicate prevention
            return self._get_fallback_businesses_with_duplicate_prevention(category, city, target_count)
    
    def _create_business_prompt(self, category: str, city: str, target_count: int) -> str:
        """Create a detailed prompt for Gemini"""
        return f"""
        Generate {target_count} realistic business listings for {category} companies in {city}, Pakistan.
        
        For each business, provide:
        - A realistic business name (should sound like a real Pakistani company)
        - A valid email format (info@companyname.com, contact@companyname.pk, etc.)
        - A Pakistani phone number format (+92-XX-XXXXXXX)
        - A realistic address in {city}
        - A website URL (www.companyname.com or www.companyname.pk)
        - Business type and category
        - A brief description of services
        - Number of employees (small: 5-20, medium: 21-100, large: 100+)
        - Founded year (between 2000-2024)
        - Main services offered
        
        Return the data in this exact JSON format:
        {{
            "businesses": [
                {{
                    "name": "Business Name",
                    "email": "email@domain.com",
                    "phone": "+92-XX-XXXXXXX",
                    "address": "Full Address, {city}",
                    "website": "www.website.com",
                    "business_type": "{category}",
                    "category": "{category}",
                    "city": "{city}",
                    "verified": true/false,
                    "source": "gemini_ai",
                    "description": "Brief description",
                    "employees": "5-20",
                    "founded_year": "2020",
                    "services": "Service 1, Service 2, Service 3"
                }}
            ]
        }}
        
        CRITICAL REQUIREMENTS:
        1. Every business MUST have a valid email address
        2. Make sure the businesses are realistic and varied
        3. Include both small startups and established companies
        4. All emails should be in valid format (info@company.com, contact@company.pk, etc.)
        """
    
    def _parse_gemini_response(self, response_text: str, category: str, city: str) -> List[BusinessData]:
        """Parse Gemini's response and convert to BusinessData objects"""
        try:
            # Try to extract JSON from the response
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            
            if json_start == -1 or json_end == 0:
                logger.warning("No JSON found in Gemini response, using fallback data")
                return self._get_fallback_businesses(category, city, 5)
            
            json_str = response_text[json_start:json_end]
            data = json.loads(json_str)
            
            businesses = []
            for business_data in data.get('businesses', []):
                try:
                    # Check if email exists and is valid
                    email = business_data.get('email', '')
                    if not email or email == 'info@unknown.com' or '@' not in email:
                        logger.warning(f"Skipping business '{business_data.get('name', 'Unknown')}' - no valid email")
                        continue
                    
                    business = BusinessData(
                        name=business_data.get('name', 'Unknown Business'),
                        email=email,
                        phone=business_data.get('phone', '+92-XX-XXXXXXX'),
                        address=business_data.get('address', f'Unknown Address, {city}'),
                        website=business_data.get('website', 'www.unknown.com'),
                        business_type=business_data.get('business_type', category),
                        category=business_data.get('category', category),
                        city=business_data.get('city', city),
                        verified=business_data.get('verified', False),
                        source=business_data.get('source', 'gemini_ai'),
                        description=business_data.get('description', ''),
                        employees=business_data.get('employees', ''),
                        founded_year=business_data.get('founded_year', ''),
                        services=business_data.get('services', '')
                    )
                    businesses.append(business)
                except Exception as e:
                    logger.warning(f"Failed to parse business data: {e}")
                    continue
            
            logger.info(f"✅ Generated {len(businesses)} businesses with valid emails")
            return businesses
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON from Gemini response: {e}")
            return self._get_fallback_businesses_with_duplicate_prevention(category, city, 5)
        except Exception as e:
            logger.error(f"Error parsing Gemini response: {e}")
            return self._get_fallback_businesses_with_duplicate_prevention(category, city, 5)
    
    def _get_fallback_businesses_with_duplicate_prevention(self, category: str, city: str, count: int) -> List[BusinessData]:
        """Provide fallback business data when Gemini fails, with duplicate prevention"""
        logger.info(f"🔄 Using fallback data for {category} in {city} with duplicate prevention")
        
        # Extended list of business names to ensure we can find enough unique ones
        if category.lower() == "technology":
            fallback_names = [
                "TechVision Solutions", "Digital Dynamics", "InnovateTech Systems", "SmartCode Solutions", "FutureTech Hub",
                "CyberTech Services", "DataFlow Technologies", "CloudTech Solutions", "MobileTech Innovations", "WebTech Pro",
                "TechGenius Labs", "Digital Forge", "Innovate Solutions", "Smart Systems", "Future Dynamics",
                "Cyber Dynamics", "Data Solutions", "Cloud Systems", "Mobile Solutions", "Web Dynamics",
                "Tech Masters", "Digital Solutions", "Innovate Labs", "Smart Tech", "Future Solutions",
                "Cyber Labs", "Data Tech", "Cloud Labs", "Mobile Tech", "Web Solutions", "Tech Dynamics"
            ]
        elif category.lower() == "healthcare":
            fallback_names = [
                "MedCare Plus", "HealthFirst Clinic", "Wellness Solutions", "CareTech Medical", "HealthHub Services",
                "MedTech Innovations", "PatientCare Solutions", "HealthTech Systems", "CareFirst Medical", "WellTech Services",
                "MedCare Solutions", "HealthFirst Plus", "Wellness Tech", "CareTech Solutions", "HealthHub Plus",
                "MedTech Solutions", "PatientCare Plus", "HealthTech Plus", "CareFirst Solutions", "WellTech Plus",
                "MedCare Tech", "HealthFirst Solutions", "Wellness Plus", "CareTech Plus", "HealthHub Tech",
                "MedTech Plus", "PatientCare Tech", "HealthTech Solutions", "CareFirst Tech", "WellTech Solutions"
            ]
        elif category.lower() == "education":
            fallback_names = [
                "EduTech Solutions", "Learning Hub", "Knowledge Center", "Smart Education", "EduVision Pro",
                "Learning Technologies", "Knowledge Hub", "EduTech Innovations", "Smart Learning", "Education Plus",
                "EduTech Plus", "Learning Solutions", "Knowledge Plus", "Smart Tech", "EduVision Solutions",
                "Learning Plus", "Knowledge Tech", "EduTech Hub", "Smart Solutions", "Education Tech",
                "EduTech Center", "Learning Tech", "Knowledge Solutions", "Smart Plus", "EduVision Tech"
            ]
        else:
            # Generic category with more variations
            base_names = [
                f"{category} Solutions Pvt Ltd", f"Elite {category} Services", f"Prime {category} Hub",
                f"Next Gen {category}", f"Smart {category} Co", f"Advanced {category} Systems",
                f"Professional {category} Group", f"Modern {category} Solutions", f"Expert {category} Services",
                f"Premium {category} Co", f"{category} Dynamics", f"Elite {category} Solutions",
                f"Prime {category} Services", f"Next Gen {category} Solutions", f"Smart {category} Services",
                f"Advanced {category} Solutions", f"Professional {category} Solutions", f"Modern {category} Services",
                f"Expert {category} Solutions", f"Premium {category} Services", f"{category} Tech", f"Elite {category} Tech",
                f"Prime {category} Tech", f"Next Gen {category} Tech", f"Smart {category} Tech", f"Advanced {category} Tech",
                f"Professional {category} Tech", f"Modern {category} Tech", f"Expert {category} Tech", f"Premium {category} Tech"
            ]
            fallback_names = base_names
        
        # Realistic addresses for different cities
        city_addresses = {
            "Islamabad": ["Blue Area", "F-7 Markaz", "G-8 Markaz", "I-8 Markaz", "F-10 Markaz", "G-11 Markaz", "I-11 Markaz", "F-8 Markaz", "G-9 Markaz", "I-9 Markaz"],
            "Lahore": ["Gulberg", "Defence", "Model Town", "Johar Town", "Bahria Town", "DHA Phase 1", "DHA Phase 2", "DHA Phase 3", "DHA Phase 4", "DHA Phase 5"],
            "Karachi": ["Clifton", "Defence", "Gulshan-e-Iqbal", "North Nazimabad", "Gulistan-e-Jauhar", "Malir", "Landhi", "Korangi", "Saddar", "Lyari"],
            "Rawalpindi": ["Saddar", "Raja Bazar", "Bank Road", "Mall Road", "Peshawar Road", "Grand Trunk Road", "Airport Road", "Murree Road", "Lehtrar Road", "Adiala Road"]
        }
        
        addresses = city_addresses.get(city, [f"Business District {i+1}" for i in range(20)])
        
        # Realistic phone numbers
        city_codes = {
            "Islamabad": "51",
            "Lahore": "42", 
            "Karachi": "21",
            "Rawalpindi": "51"
        }
        city_code = city_codes.get(city, "30")
        
        unique_businesses = []
        used_names = set()
        used_emails = set()
        
        for i in range(len(fallback_names)):
            if len(unique_businesses) >= count:
                break
                
            name = fallback_names[i]
            # Generate realistic email - ensure it's always valid
            company_name = name.lower().replace(' ', '').replace('.', '').replace('-', '').replace('&', '')
            email = f"info@{company_name}.com"
            
            # Check if this name or email is already used in this session
            if name.lower() in used_names or email.lower() in used_emails:
                continue
                
            # Check if this name or email already exists in lead history
            if name.lower() in self.existing_names or email.lower() in self.existing_emails:
                continue
            
            # Generate realistic phone number
            phone_suffix = 1000000 + (i * 10000) + (i * 123)  # More varied numbers
            phone = f"+92-{city_code}-{phone_suffix}"
            
            # Generate realistic website
            website = f"www.{company_name}.com"
            
            # Generate realistic description
            descriptions = [
                f"Leading {category.lower()} company in {city} providing innovative solutions and professional services.",
                f"Established {category.lower()} business serving {city} with quality services and customer satisfaction.",
                f"Professional {category.lower()} services in {city} with years of experience and expertise.",
                f"Trusted {category.lower()} company in {city} offering comprehensive solutions and support.",
                f"Innovative {category.lower()} business in {city} focused on delivering excellence and results."
            ]
            
            business = BusinessData(
                name=name,
                email=email,
                phone=phone,
                address=f"{addresses[i % len(addresses)]}, {city}",
                website=website,
                business_type=category,
                category=category,
                city=city,
                verified=len(unique_businesses) < 5,  # First 5 are verified
                source="realistic_fallback_data",
                description=descriptions[i % len(descriptions)],
                employees="10-50" if len(unique_businesses) < 5 else "5-20",
                founded_year=str(2015 + (i % 10)),
                services=f"{category} Consulting, Development, Support, Training, Maintenance"
            )
            
            unique_businesses.append(business)
            used_names.add(name.lower())
            used_emails.add(email.lower())
            
            # Add to existing sets to prevent future duplicates
            self.existing_names.add(name.lower())
            self.existing_emails.add(email.lower())
        
        logger.info(f"✅ Generated {len(unique_businesses)} unique fallback businesses with valid emails")
        return unique_businesses
    
    def get_generation_statistics(self) -> Dict[str, Any]:
        """Get statistics about the generation process"""
        if self.fallback_mode:
            return {
                "generator_type": "Fallback Generator",
                "model_used": "sample_data",
                "status": "fallback_mode",
                "features": [
                    "Sample business data generation",
                    "Realistic Pakistani business data",
                    "No API key required",
                    "Instant generation"
                ]
            }
        else:
            return {
                "generator_type": "Gemini AI",
                "model_used": "gemini-1.5-flash",
                "status": "active",
                "features": [
                    "AI-powered business generation",
                    "Realistic Pakistani business data",
                    "Fallback data support",
                    "JSON response parsing"
                ]
            }

if __name__ == "__main__":
    # Test the generator
    try:
        generator = GeminiBusinessGenerator()
        businesses = generator.generate_businesses("Technology", "Islamabad", 5)
        
        print(f"Generated {len(businesses)} businesses:")
        for business in businesses:
            print(f"- {business.name} ({business.email})")
            
    except Exception as e:
        print(f"Error: {e}")

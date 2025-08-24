#!/usr/bin/env python3
"""
Configuration file for Reviu.pk Lead Generation System
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Configuration
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
GEMINI_MODEL = os.getenv('GEMINI_MODEL', 'gemini-1.5-flash')

# SMTP Configuration
SMTP_SERVER = os.getenv('SMTP_SERVER')
SMTP_PORT = int(os.getenv('SMTP_PORT', 465))
SMTP_USERNAME = os.getenv('SMTP_USERNAME')
SMTP_PASSWORD = os.getenv('SMTP_PASSWORD')

# Email Generation
EMAIL_GENERATION_PROMPT = os.getenv('EMAIL_GENERATION_PROMPT')

# File Paths
LEADS_FILE = 'leads_data.csv'
EMAILS_FILE = 'generated_emails.csv'
RESULTS_FILE = 'campaign_results.csv'

# Validation
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found in environment variables")

if not SMTP_SERVER or not SMTP_USERNAME or not SMTP_PASSWORD:
    raise ValueError("SMTP configuration incomplete")

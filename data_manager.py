#!/usr/bin/env python3
"""
Professional Data Manager for Reviu.pk
Handles CSV operations, data storage, and campaign management
"""

import os
import csv
import json
import pandas as pd
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DataManager:
    """Professional data manager for lead generation and email campaigns"""
    
    def __init__(self):
        """Initialize the data manager"""
        self.base_dir = Path.cwd()
        self.data_dir = self.base_dir / "data"
        self.data_dir.mkdir(exist_ok=True)
        
        # CSV file paths
        self.leads_file = self.data_dir / "leads_data.csv"
        self.emails_file = self.data_dir / "generated_emails.csv"
        self.results_file = self.data_dir / "campaign_results.csv"
        
        # History files for duplicate prevention
        self.lead_history_file = self.data_dir / "lead_history.csv"
        self.email_history_file = self.data_dir / "email_history.csv"
        self.sent_emails_file = self.data_dir / "sent_emails.csv"
        
        # JSON files for campaign records
        self.campaign_records_file = self.data_dir / "campaign_records.json"
        
        # Initialize files if they don't exist
        self._initialize_files()
        
        logger.info("✅ Data manager initialized successfully")
    
    def _initialize_files(self):
        """Initialize CSV and JSON files with headers if they don't exist"""
        try:
            # Initialize leads file
            if not self.leads_file.exists():
                leads_headers = ['name', 'email', 'phone', 'address', 'website', 'business_type', 'verified', 'source', 'city', 'timestamp']
                self._create_csv_file(self.leads_file, leads_headers)
                logger.info("📁 Created leads_data.csv")
            
            # Initialize emails file
            if not self.emails_file.exists():
                emails_headers = ['business_name', 'business_type', 'email', 'city', 'generated_email', 'status', 'timestamp']
                self._create_csv_file(self.emails_file, emails_headers)
                logger.info("📁 Created generated_emails.csv")
            
            # Initialize results file
            if not self.results_file.exists():
                results_headers = ['business_name', 'email', 'status', 'message', 'business_type', 'city', 'timestamp']
                self._create_csv_file(self.results_file, results_headers)
                logger.info("📁 Created campaign_results.csv")
            
            # Initialize history files
            if not self.lead_history_file.exists():
                self._create_csv_file(self.lead_history_file, ['name', 'email', 'phone', 'address', 'website', 'business_type', 'verified', 'source', 'city', 'timestamp'])
                logger.info("📁 Created lead_history.csv")
            
            if not self.email_history_file.exists():
                self._create_csv_file(self.email_history_file, ['business_name', 'business_type', 'email', 'city', 'generated_email', 'status', 'timestamp'])
                logger.info("📁 Created email_history.csv")
            
            if not self.sent_emails_file.exists():
                self._create_csv_file(self.sent_emails_file, ['business_name', 'email', 'status', 'message', 'business_type', 'city', 'timestamp'])
                logger.info("📁 Created sent_emails.csv")
            
            # Initialize campaign records JSON
            if not self.campaign_records_file.exists():
                initial_records = {
                    'campaigns': [],
                    'statistics': {
                        'total_campaigns': 0,
                        'total_leads_generated': 0,
                        'total_emails_sent': 0,
                        'success_rate': 0.0
                    },
                    'last_updated': datetime.now().isoformat()
                }
                self._save_json_file(self.campaign_records_file, initial_records)
                logger.info("📁 Created campaign_records.json")
                
        except Exception as e:
            logger.error(f"❌ Error initializing files: {e}")
            raise
    
    def _create_csv_file(self, file_path: Path, headers: List[str]):
        """Create a CSV file with headers"""
        with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(headers)
    
    def _save_json_file(self, file_path: Path, data: Dict[str, Any]):
        """Save data to JSON file"""
        with open(file_path, 'w', encoding='utf-8') as jsonfile:
            json.dump(data, jsonfile, indent=2, ensure_ascii=False)
    
    def _load_json_file(self, file_path: Path) -> Dict[str, Any]:
        """Load data from JSON file"""
        try:
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as jsonfile:
                    return json.load(jsonfile)
            return {}
        except Exception as e:
            logger.error(f"❌ Error loading JSON file {file_path}: {e}")
            return {}
    
    def save_leads(self, leads: List[Dict[str, Any]]) -> bool:
        """Save leads to CSV and history files"""
        try:
            if not leads:
                logger.warning("⚠️ No leads to save")
                return False
            
            # Add timestamp to leads
            timestamp = datetime.now().isoformat()
            for lead in leads:
                lead['timestamp'] = timestamp
            
            # Save to current session file
            self._save_to_csv(self.leads_file, leads)
            
            # Save to history file
            self._save_to_csv(self.lead_history_file, leads, append=True)
            
            # Update campaign records
            self._update_campaign_records('leads_generated', len(leads))
            
            logger.info(f"✅ Saved {len(leads)} leads to CSV and history files")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error saving leads: {e}")
            return False
    
    def save_generated_emails(self, emails: List[Dict[str, Any]]) -> bool:
        """Save generated emails to CSV and history files"""
        try:
            if not emails:
                logger.warning("⚠️ No emails to save")
                return False
            
            # Add timestamp to emails
            timestamp = datetime.now().isoformat()
            for email in emails:
                email['timestamp'] = timestamp
            
            # Save to current session file
            self._save_to_csv(self.emails_file, emails)
            
            # Save to history file
            self._save_to_csv(self.email_history_file, emails, append=True)
            
            logger.info(f"✅ Saved {len(emails)} generated emails to CSV and history files")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error saving generated emails: {e}")
            return False
    
    def save_campaign_results(self, results: List[Dict[str, Any]]) -> bool:
        """Save campaign results to CSV and history files"""
        try:
            if not results:
                logger.warning("⚠️ No results to save")
                return False
            
            # Add timestamp to results
            timestamp = datetime.now().isoformat()
            for result in results:
                result['timestamp'] = timestamp
            
            # Save to current session file
            self._save_to_csv(self.results_file, results)
            
            # Save to history file
            self._save_to_csv(self.sent_emails_file, results, append=True)
            
            # Update campaign records
            success_count = sum(1 for r in results if r.get('status') == 'sent')
            self._update_campaign_records('emails_sent', len(results), success_count)
            
            logger.info(f"✅ Saved {len(results)} campaign results to CSV and history files")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error saving campaign results: {e}")
            return False
    
    def _save_to_csv(self, file_path: Path, data: List[Dict[str, Any]], append: bool = False):
        """Save data to CSV file"""
        try:
            mode = 'a' if append else 'w'
            with open(file_path, mode, newline='', encoding='utf-8') as csvfile:
                if not append:
                    # Write headers for new files
                    if data:
                        fieldnames = list(data[0].keys())
                        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                        writer.writeheader()
                
                # Write data
                if data:
                    fieldnames = list(data[0].keys())
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    writer.writerows(data)
                    
        except Exception as e:
            logger.error(f"❌ Error saving to CSV {file_path}: {e}")
            raise
    
    def load_leads(self) -> List[Dict[str, Any]]:
        """Load leads from CSV file"""
        try:
            if not self.leads_file.exists():
                return []
            
            df = pd.read_csv(self.leads_file, encoding='utf-8')
            df = df.fillna('')  # Replace NaN with empty string
            
            # Convert DataFrame to list of dictionaries
            leads = df.to_dict('records')
            logger.info(f"📊 Loaded {len(leads)} leads from CSV")
            return leads
            
        except Exception as e:
            logger.error(f"❌ Error loading leads: {e}")
            return []
    
    def load_emails(self) -> List[Dict[str, Any]]:
        """Load generated emails from CSV file"""
        try:
            if not self.emails_file.exists():
                return []
            
            df = pd.read_csv(self.emails_file, encoding='utf-8')
            df = df.fillna('')  # Replace NaN with empty string
            
            # Convert DataFrame to list of dictionaries
            emails = df.to_dict('records')
            logger.info(f"📊 Loaded {len(emails)} emails from CSV")
            return emails
            
        except Exception as e:
            logger.error(f"❌ Error loading emails: {e}")
            return []
    
    def load_results(self) -> List[Dict[str, Any]]:
        """Load campaign results from CSV file"""
        try:
            if not self.results_file.exists():
                return []
            
            df = pd.read_csv(self.results_file, encoding='utf-8')
            df = df.fillna('')  # Replace NaN with empty string
            
            # Convert DataFrame to list of dictionaries
            results = df.to_dict('records')
            logger.info(f"📊 Loaded {len(results)} results from CSV")
            return results
            
        except Exception as e:
            logger.error(f"❌ Error loading results: {e}")
            return []
    
    def _update_campaign_records(self, action: str, count: int, success_count: int = 0):
        """Update campaign records with new statistics"""
        try:
            records = self._load_json_file(self.campaign_records_file)
            
            # Add new campaign record
            campaign_record = {
                'action': action,
                'count': count,
                'success_count': success_count,
                'timestamp': datetime.now().isoformat()
            }
            
            if 'campaigns' not in records:
                records['campaigns'] = []
            records['campaigns'].append(campaign_record)
            
            # Update statistics
            if 'statistics' not in records:
                records['statistics'] = {}
            
            if action == 'leads_generated':
                records['statistics']['total_leads_generated'] = records['statistics'].get('total_leads_generated', 0) + count
            elif action == 'emails_sent':
                records['statistics']['total_emails_sent'] = records['statistics'].get('total_emails_sent', 0) + count
                records['statistics']['total_campaigns'] = records['statistics'].get('total_campaigns', 0) + 1
                
                # Calculate success rate
                total_sent = records['statistics']['total_emails_sent']
                total_success = sum(c['success_count'] for c in records['campaigns'] if c['action'] == 'emails_sent')
                if total_sent > 0:
                    records['statistics']['success_rate'] = round((total_success / total_sent) * 100, 2)
            
            records['last_updated'] = datetime.now().isoformat()
            
            # Save updated records
            self._save_json_file(self.campaign_records_file, records)
            
        except Exception as e:
            logger.error(f"❌ Error updating campaign records: {e}")
    
    def get_campaign_statistics(self) -> Dict[str, Any]:
        """Get campaign statistics"""
        try:
            records = self._load_json_file(self.campaign_records_file)
            return records.get('statistics', {})
        except Exception as e:
            logger.error(f"❌ Error getting campaign statistics: {e}")
            return {}
    
    def clear_session_data(self):
        """Clear current session data (leads, emails, results) but keep history"""
        try:
            # Clear current session files
            if self.leads_file.exists():
                self.leads_file.unlink()
            if self.emails_file.exists():
                self.emails_file.unlink()
            if self.results_file.exists():
                self.results_file.unlink()
            
            # Reinitialize files
            self._initialize_files()
            
            logger.info("🧹 Session data cleared successfully")
            
        except Exception as e:
            logger.error(f"❌ Error clearing session data: {e}")
    
    def get_duplicate_analysis(self) -> Dict[str, Any]:
        """Analyze duplicates in historical data"""
        try:
            if not self.lead_history_file.exists():
                return {
                    'status': 'no_history',
                    'message': 'No lead history file found',
                    'duplicate_prevention_active': False
                }
            
            df = pd.read_csv(self.lead_history_file, encoding='utf-8')
            
            if df.empty:
                return {
                    'status': 'empty_history',
                    'message': 'Lead history is empty',
                    'duplicate_prevention_active': True
                }
            
            # Analyze duplicates
            email_duplicates = df[df.duplicated(subset=['email'], keep=False)]
            name_duplicates = df[df.duplicated(subset=['name'], keep=False)]
            
            analysis = {
                'status': 'active',
                'total_leads_in_history': len(df),
                'duplicate_prevention_active': True,
                'duplicates_by_email': len(email_duplicates),
                'duplicates_by_name': len(name_duplicates),
                'total_potential_duplicates': max(len(email_duplicates), len(name_duplicates)),
                'duplicate_rate': round((max(len(email_duplicates), len(name_duplicates)) / len(df)) * 100, 2) if len(df) > 0 else 0,
                'last_checked': datetime.now().isoformat()
            }
            
            return analysis
            
        except Exception as e:
            logger.error(f"❌ Error getting duplicate analysis: {e}")
            return {
                'status': 'error',
                'message': f'Error analyzing duplicates: {str(e)}',
                'duplicate_prevention_active': False
            }

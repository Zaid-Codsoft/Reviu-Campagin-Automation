#!/usr/bin/env python3
"""
Professional Email Sender for Reviu.pk
Handles SMTP email sending with SSL support
"""

import os
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Any, List, Tuple
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class EmailSender:
    """Professional email sender with SMTP SSL support"""
    
    def __init__(self):
        """Initialize the email sender with SMTP configuration"""
        try:
            # Load SMTP configuration from environment
            self.smtp_server = os.getenv('SMTP_SERVER', 'smtpout.secureserver.net')
            self.smtp_port = int(os.getenv('SMTP_PORT', '465'))
            self.smtp_username = os.getenv('SMTP_USERNAME', 'info@reviu.pk')
            self.smtp_password = os.getenv('SMTP_PASSWORD', '')
            
            # Validate configuration
            if not self.smtp_password:
                raise ValueError("SMTP_PASSWORD not found in environment variables")
            
            # Email configuration
            self.sender_name = "Zaid - Reviu.pk"
            self.sender_email = self.smtp_username
            self.subject_prefix = "Join Reviu.pk - Pakistan's Leading Business Directory"
            
            logger.info(f"✅ Email sender initialized for {self.smtp_server}:{self.smtp_port}")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize email sender: {e}")
            raise
    
    def send_single_email(self, recipient_email: str, business_name: str, email_content: str) -> Tuple[bool, str]:
        """Send a single email to one recipient"""
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = f"{self.sender_name} <{self.sender_email}>"
            msg['To'] = recipient_email
            msg['Subject'] = f"{self.subject_prefix} - {business_name}"
            
            # Add email body
            msg.attach(MIMEText(email_content, 'plain', 'utf-8'))
            
            # Send email
            with smtplib.SMTP_SSL(self.smtp_server, self.smtp_port) as server:
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)
            
            logger.info(f"✅ Email sent successfully to {recipient_email} for {business_name}")
            return True, "Email sent successfully"
            
        except smtplib.SMTPAuthenticationError:
            error_msg = "SMTP authentication failed - check username and password"
            logger.error(f"❌ {error_msg}")
            return False, error_msg
            
        except smtplib.SMTPRecipientsRefused as e:
            error_msg = f"Recipient email rejected: {recipient_email}"
            logger.error(f"❌ {error_msg}")
            return False, error_msg
            
        except smtplib.SMTPServerDisconnected:
            error_msg = "SMTP server disconnected unexpectedly"
            logger.error(f"❌ {error_msg}")
            return False, error_msg
            
        except Exception as e:
            error_msg = f"Unexpected error sending email: {str(e)}"
            logger.error(f"❌ {error_msg}")
            return False, error_msg
    
    def send_bulk_emails(self, generated_emails: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Send bulk emails to multiple recipients"""
        try:
            logger.info(f"📧 Starting bulk email campaign for {len(generated_emails)} recipients...")
            
            results = []
            successful_sends = 0
            failed_sends = 0
            
            for i, email_data in enumerate(generated_emails, 1):
                try:
                    recipient_email = email_data.get('email', '')
                    business_name = email_data.get('business_name', 'Unknown')
                    email_content = email_data.get('generated_email', '')
                    
                    if not recipient_email or not email_content:
                        logger.warning(f"⚠️ Skipping email {i} - missing email or content")
                        results.append({
                            'business_name': business_name,
                            'email': recipient_email,
                            'status': 'skipped',
                            'message': 'Missing email or content'
                        })
                        failed_sends += 1
                        continue
                    
                    # Send email
                    success, message = self.send_single_email(recipient_email, business_name, email_content)
                    
                    # Record result
                    result = {
                        'business_name': business_name,
                        'email': recipient_email,
                        'status': 'sent' if success else 'failed',
                        'message': message,
                        'business_type': email_data.get('business_type', 'Unknown'),
                        'city': email_data.get('city', 'Unknown')
                    }
                    
                    results.append(result)
                    
                    if success:
                        successful_sends += 1
                        logger.info(f"✅ Email {i}/{len(generated_emails)} sent successfully to {business_name}")
                    else:
                        failed_sends += 1
                        logger.error(f"❌ Email {i}/{len(generated_emails)} failed for {business_name}: {message}")
                    
                    # Add small delay to avoid overwhelming the SMTP server
                    import time
                    time.sleep(0.5)
                    
                except Exception as e:
                    logger.error(f"❌ Error processing email {i} for {email_data.get('business_name', 'Unknown')}: {e}")
                    results.append({
                        'business_name': email_data.get('business_name', 'Unknown'),
                        'email': email_data.get('email', ''),
                        'status': 'error',
                        'message': f'Processing error: {str(e)}',
                        'business_type': email_data.get('business_type', 'Unknown'),
                        'city': email_data.get('city', 'Unknown')
                    })
                    failed_sends += 1
            
            # Log campaign summary
            logger.info(f"🎯 Bulk email campaign completed!")
            logger.info(f"  ✅ Successful: {successful_sends}")
            logger.info(f"  ❌ Failed: {failed_sends}")
            logger.info(f"  📊 Total: {len(generated_emails)}")
            
            return results
            
        except Exception as e:
            logger.error(f"❌ Error in bulk email campaign: {e}")
            return []
    
    def test_connection(self) -> Tuple[bool, str]:
        """Test SMTP connection and authentication"""
        try:
            logger.info("🔍 Testing SMTP connection...")
            
            with smtplib.SMTP_SSL(self.smtp_server, self.smtp_port) as server:
                server.login(self.smtp_username, self.smtp_password)
                
                # Test sending a simple message to ourselves
                test_msg = MIMEMultipart()
                test_msg['From'] = f"{self.sender_name} <{self.sender_email}>"
                test_msg['To'] = self.sender_email
                test_msg['Subject'] = "SMTP Connection Test - Reviu.pk"
                test_msg.attach(MIMEText("This is a test email to verify SMTP connection.", 'plain', 'utf-8'))
                
                server.send_message(test_msg)
            
            logger.info("✅ SMTP connection test successful")
            return True, "SMTP connection test successful"
            
        except smtplib.SMTPAuthenticationError:
            error_msg = "SMTP authentication failed - check username and password"
            logger.error(f"❌ {error_msg}")
            return False, error_msg
            
        except Exception as e:
            error_msg = f"SMTP connection test failed: {str(e)}"
            logger.error(f"❌ {error_msg}")
            return False, error_msg
    
    def get_smtp_info(self) -> Dict[str, str]:
        """Get SMTP configuration information (without password)"""
        return {
            'server': self.smtp_server,
            'port': str(self.smtp_port),
            'username': self.smtp_username,
            'sender_name': self.sender_name
        }

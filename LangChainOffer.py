"""
LangChain Agentic AI System for Disney Channel 25% Off Annual Subscription Campaign

Agents:
1. AdminAgent - Configure offer settings in offer_disney.properties
2. UserLookupAgent - Fetch users from public API
3. CampaignAgent - Send email/SMS notifications
4. MonitorAgent - Track acceptance/decline metrics
"""

import os
import json
import sqlite3
from datetime import datetime
from typing import Any, List, Dict, Optional
from configparser import ConfigParser
import requests
from abc import ABC, abstractmethod

# For LangChain integration (install with: pip install langchain langchain-community)
try:
    from langchain.agents import Tool, AgentExecutor, create_react_agent
    from langchain_community.llms import OpenAI
    from langchain import hub
except ImportError:
    print("Note: Install LangChain with: pip install langchain langchain-community")


# ============================================================================
# DATABASE SETUP
# ============================================================================

class CampaignDatabase:
    """SQLite database manager for campaign tracking"""
    
    def __init__(self, db_path: str = "./campaign_tracking.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize SQLite database with required tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                phone TEXT,
                status TEXT DEFAULT 'ELIGIBLE',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Campaign tracking table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS campaign_tracking (
                tracking_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                offer_id TEXT NOT NULL,
                notification_type TEXT,
                notification_status TEXT,
                response_status TEXT DEFAULT 'PENDING',
                response_date TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        """)
        
        # Offer configuration table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS offer_config (
                config_id INTEGER PRIMARY KEY AUTOINCREMENT,
                config_key TEXT NOT NULL UNIQUE,
                config_value TEXT NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        conn.close()
    
    def get_connection(self):
        """Get database connection"""
        return sqlite3.connect(self.db_path)
    
    def execute_query(self, query: str, params: tuple = ()) -> List[tuple]:
        """Execute SELECT query"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(query, params)
        results = cursor.fetchall()
        conn.close()
        return results
    
    def execute_update(self, query: str, params: tuple = ()) -> int:
        """Execute INSERT/UPDATE/DELETE query"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()
        last_id = cursor.lastrowid
        conn.close()
        return last_id


# ============================================================================
# ADMIN AGENT
# ============================================================================

class AdminAgent(ABC):
    """
    AdminAgent: Responsible for configuring the offer in offer_disney.properties file
    """
    
    def __init__(self, properties_file: str = "./offer_disney.properties"):
        self.properties_file = properties_file
        self.config = ConfigParser()
        self.load_config()
    
    def load_config(self) -> Dict[str, Any]:
        """Load offer configuration from properties file"""
        if os.path.exists(self.properties_file):
            self.config.read(self.properties_file)
            return self.config._sections
        return {}
    
    def save_config(self) -> bool:
        """Save configuration to properties file"""
        try:
            with open(self.properties_file, 'w') as f:
                self.config.write(f)
            return True
        except Exception as e:
            print(f"Error saving config: {e}")
            return False
    
    def get_offer_details(self) -> Dict[str, Any]:
        """Retrieve current offer details"""
        try:
            offer_details = {
                'name': self.config.get('project', 'offer.name', fallback='Disney Channel Premium'),
                'discount_percentage': self.config.get('project', 'offer.discount.percentage', fallback='25'),
                'original_price': self.config.get('project', 'offer.original.price', fallback='120.00'),
                'discounted_price': self.config.get('project', 'offer.discounted.price', fallback='90.00'),
                'campaign_status': self.config.get('project', 'campaign.status', fallback='ACTIVE'),
                'start_date': self.config.get('project', 'campaign.start.date', fallback='2026-05-04'),
                'end_date': self.config.get('project', 'campaign.end.date', fallback='2026-06-04'),
            }
            return offer_details
        except Exception as e:
            return {'error': str(e)}
    
    def update_offer_settings(self, setting_key: str, setting_value: str) -> bool:
        """Update specific offer setting"""
        try:
            if not self.config.has_section('project'):
                self.config.add_section('project')
            
            self.config.set('project', setting_key, setting_value)
            return self.save_config()
        except Exception as e:
            print(f"Error updating setting: {e}")
            return False
    
    def validate_offer_config(self) -> Dict[str, Any]:
        """Validate offer configuration"""
        validation_result = {
            'valid': True,
            'errors': [],
            'warnings': []
        }
        
        try:
            discount = float(self.config.get('project', 'offer.discount.percentage', fallback='0'))
            if discount <= 0 or discount > 100:
                validation_result['valid'] = False
                validation_result['errors'].append("Discount percentage must be between 0 and 100")
            
            original_price = float(self.config.get('project', 'offer.original.price', fallback='0'))
            discounted_price = float(self.config.get('project', 'offer.discounted.price', fallback='0'))
            
            if discounted_price >= original_price:
                validation_result['valid'] = False
                validation_result['errors'].append("Discounted price must be less than original price")
            
            if not self.config.get('project', 'campaign.status', fallback=''):
                validation_result['warnings'].append("Campaign status not set")
        
        except ValueError as e:
            validation_result['valid'] = False
            validation_result['errors'].append(f"Invalid price format: {str(e)}")
        
        return validation_result


# ============================================================================
# USER LOOKUP AGENT
# ============================================================================

class UserLookupAgent(ABC):
    """
    UserLookupAgent: Responsible for querying users who qualify for the offer
    Uses JSONPlaceholder API (free public API) to fetch user data
    """
    
    def __init__(self, db: CampaignDatabase):
        self.db = db
        self.api_base_url = "https://jsonplaceholder.typicode.com"
        self.users_endpoint = "/users"
    
    def fetch_users_from_api(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Fetch users from JSONPlaceholder API
        
        Args:
            limit: Number of users to fetch (max 10, JSONPlaceholder has 10 users)
        
        Returns:
            List of user dictionaries
        """
        try:
            url = f"{self.api_base_url}{self.users_endpoint}"
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            
            users = response.json()[:limit]
            return users
        except requests.exceptions.RequestException as e:
            print(f"Error fetching users from API: {e}")
            return []
    
    def qualify_users(self, users: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Apply qualification logic to users
        Example: Filter users from specific regions/criteria
        
        Args:
            users: List of users from API
        
        Returns:
            List of qualified users
        """
        qualified_users = []
        
        for user in users:
            # Qualification criteria
            qualified_user = {
                'user_id': user.get('id'),
                'name': user.get('name'),
                'email': user.get('email'),
                'phone': user.get('phone', ''),
                'company': user.get('company', {}).get('name', ''),
                'qualified': True,
                'reason': 'Meets qualification criteria'
            }
            qualified_users.append(qualified_user)
        
        return qualified_users
    
    def store_qualified_users(self, qualified_users: List[Dict[str, Any]]) -> int:
        """
        Store qualified users in database
        
        Args:
            qualified_users: List of qualified users
        
        Returns:
            Number of users stored
        """
        count = 0
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        try:
            for user in qualified_users:
                cursor.execute("""
                    INSERT OR IGNORE INTO users (user_id, name, email, phone, status)
                    VALUES (?, ?, ?, ?, 'ELIGIBLE')
                """, (
                    user.get('user_id'),
                    user.get('name'),
                    user.get('email'),
                    user.get('phone', '')
                ))
                count += 1
            
            conn.commit()
        except Exception as e:
            print(f"Error storing users: {e}")
            conn.rollback()
        finally:
            conn.close()
        
        return count
    
    def get_qualified_users(self) -> List[Dict[str, Any]]:
        """
        Get all qualified users from database
        
        Returns:
            List of qualified users
        """
        query = "SELECT user_id, name, email, phone FROM users WHERE status = 'ELIGIBLE'"
        results = self.db.execute_query(query)
        
        users = []
        for row in results:
            users.append({
                'user_id': row[0],
                'name': row[1],
                'email': row[2],
                'phone': row[3]
            })
        
        return users
    
    def lookup_and_qualify_users(self, count: int = 10) -> Dict[str, Any]:
        """
        Complete user lookup and qualification process
        
        Args:
            count: Number of users to fetch
        
        Returns:
            Summary of lookup operation
        """
        print(f"\n{'='*60}")
        print(f"USER LOOKUP AGENT - Fetching {count} Users")
        print(f"{'='*60}")
        
        # Fetch users from API
        api_users = self.fetch_users_from_api(limit=count)
        print(f"✓ Fetched {len(api_users)} users from JSONPlaceholder API")
        
        # Qualify users
        qualified = self.qualify_users(api_users)
        print(f"✓ Qualified {len(qualified)} users")
        
        # Store in database
        stored = self.store_qualified_users(qualified)
        print(f"✓ Stored {stored} users in database")
        
        return {
            'status': 'SUCCESS',
            'api_users_fetched': len(api_users),
            'users_qualified': len(qualified),
            'users_stored': stored,
            'qualified_users': qualified
        }


# ============================================================================
# CAMPAIGN AGENT
# ============================================================================

class CampaignAgent(ABC):
    """
    CampaignAgent: Responsible for sending email and SMS notifications
    """
    
    def __init__(self, db: CampaignDatabase, admin_agent: AdminAgent):
        self.db = db
        self.admin_agent = admin_agent
        self.email_count = 0
        self.sms_count = 0
    
    def send_email(self, recipient_email: str, recipient_name: str, 
                   offer_details: Dict[str, Any]) -> Dict[str, Any]:
        """
        Mock email sending function
        
        Args:
            recipient_email: Email address
            recipient_name: Recipient name
            offer_details: Offer details dict
        
        Returns:
            Email sending result
        """
        try:
            # Mock email sending (in production, use SendGrid, AWS SES, etc.)
            email_body = f"""
Dear {recipient_name},

Exclusive Offer: 25% OFF Annual Subscription to Disney Channel!

Original Price: ${offer_details.get('original_price', '120.00')}
Your Price: ${offer_details.get('discounted_price', '90.00')}
Discount: {offer_details.get('discount_percentage', '25')}%

Valid Until: {offer_details.get('end_date', '2026-06-04')}

Click here to claim your offer: https://disneyplus.com/offer/25off

Terms & Conditions Apply.

Best Regards,
Disney Channel Team
            """
            
            result = {
                'success': True,
                'type': 'EMAIL',
                'recipient': recipient_email,
                'recipient_name': recipient_name,
                'timestamp': datetime.now().isoformat(),
                'message_preview': email_body[:100] + "..."
            }
            
            self.email_count += 1
            return result
        
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def send_sms(self, recipient_phone: str, recipient_name: str, 
                 offer_details: Dict[str, Any]) -> Dict[str, Any]:
        """
        Mock SMS sending function
        
        Args:
            recipient_phone: Phone number
            recipient_name: Recipient name
            offer_details: Offer details dict
        
        Returns:
            SMS sending result
        """
        try:
            # Mock SMS sending (in production, use Twilio, AWS SNS, etc.)
            sms_body = f"Hi {recipient_name}! 🎉 Get 25% OFF Disney Channel Annual Subscription! ${offer_details.get('discounted_price', '90')} instead of ${offer_details.get('original_price', '120')}. Valid until {offer_details.get('end_date')}. Click: https://disney.link/offer25"
            
            result = {
                'success': True,
                'type': 'SMS',
                'recipient': recipient_phone,
                'recipient_name': recipient_name,
                'timestamp': datetime.now().isoformat(),
                'message': sms_body
            }
            
            self.sms_count += 1
            return result
        
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def send_notifications(self, users: List[Dict[str, Any]], 
                          offer_details: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send email and SMS notifications to all users
        
        Args:
            users: List of users to notify
            offer_details: Offer details
        
        Returns:
            Campaign execution summary
        """
        print(f"\n{'='*60}")
        print(f"CAMPAIGN AGENT - Sending Notifications")
        print(f"{'='*60}")
        
        email_results = []
        sms_results = []
        
        for user in users:
            user_id = user['user_id']
            name = user['name']
            email = user['email']
            phone = user['phone']
            
            # Send email
            email_result = self.send_email(email, name, offer_details)
            email_results.append(email_result)
            
            # Record in database
            if email_result.get('success'):
                conn = self.db.get_connection()
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO campaign_tracking 
                    (user_id, offer_id, notification_type, notification_status, response_status)
                    VALUES (?, ?, ?, ?, ?)
                """, (user_id, 'DISNEY_25_OFF', 'EMAIL', 'SENT', 'PENDING'))
                conn.commit()
                conn.close()
            
            # Send SMS if phone available
            if phone:
                sms_result = self.send_sms(phone, name, offer_details)
                sms_results.append(sms_result)
                
                # Record in database
                if sms_result.get('success'):
                    conn = self.db.get_connection()
                    cursor = conn.cursor()
                    cursor.execute("""
                        INSERT INTO campaign_tracking 
                        (user_id, offer_id, notification_type, notification_status, response_status)
                        VALUES (?, ?, ?, ?, ?)
                    """, (user_id, 'DISNEY_25_OFF', 'SMS', 'SENT', 'PENDING'))
                    conn.commit()
                    conn.close()
        
        print(f"✓ Sent {len(email_results)} emails")
        print(f"✓ Sent {len(sms_results)} SMS messages")
        
        return {
            'status': 'SUCCESS',
            'total_users': len(users),
            'emails_sent': len([r for r in email_results if r.get('success')]),
            'sms_sent': len([r for r in sms_results if r.get('success')]),
            'email_details': email_results,
            'sms_details': sms_results
        }


# ============================================================================
# MONITOR AGENT
# ============================================================================

class MonitorAgent(ABC):
    """
    MonitorAgent: Responsible for counting acceptances and declines
    """
    
    def __init__(self, db: CampaignDatabase):
        self.db = db
    
    def record_user_response(self, user_id: int, response: str) -> bool:
        """
        Record user's response to the offer (ACCEPTED/DECLINED)
        
        Args:
            user_id: User ID
            response: ACCEPTED or DECLINED
        
        Returns:
            Success status
        """
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE campaign_tracking
                SET response_status = ?, response_date = CURRENT_TIMESTAMP
                WHERE user_id = ? AND offer_id = 'DISNEY_25_OFF'
            """, (response, user_id))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error recording response: {e}")
            return False
    
    def get_campaign_metrics(self) -> Dict[str, Any]:
        """
        Get comprehensive campaign metrics
        
        Returns:
            Campaign metrics dictionary
        """
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            # Total notifications sent
            cursor.execute("""
                SELECT COUNT(*) FROM campaign_tracking 
                WHERE offer_id = 'DISNEY_25_OFF'
            """)
            total_sent = cursor.fetchone()[0]
            
            # Acceptances
            cursor.execute("""
                SELECT COUNT(*) FROM campaign_tracking 
                WHERE offer_id = 'DISNEY_25_OFF' AND response_status = 'ACCEPTED'
            """)
            accepted = cursor.fetchone()[0]
            
            # Declines
            cursor.execute("""
                SELECT COUNT(*) FROM campaign_tracking 
                WHERE offer_id = 'DISNEY_25_OFF' AND response_status = 'DECLINED'
            """)
            declined = cursor.fetchone()[0]
            
            # Pending
            cursor.execute("""
                SELECT COUNT(*) FROM campaign_tracking 
                WHERE offer_id = 'DISNEY_25_OFF' AND response_status = 'PENDING'
            """)
            pending = cursor.fetchone()[0]
            
            conn.close()
            
            acceptance_rate = (accepted / total_sent * 100) if total_sent > 0 else 0
            
            return {
                'total_notifications_sent': total_sent,
                'accepted': accepted,
                'declined': declined,
                'pending': pending,
                'acceptance_rate_percent': round(acceptance_rate, 2),
                'decline_rate_percent': round((declined / total_sent * 100) if total_sent > 0 else 0, 2)
            }
        
        except Exception as e:
            return {'error': str(e)}
    
    def get_detailed_responses(self) -> List[Dict[str, Any]]:
        """
        Get detailed response data for all users
        
        Returns:
            List of detailed response records
        """
        try:
            query = """
                SELECT 
                    ct.tracking_id,
                    ct.user_id,
                    u.name,
                    u.email,
                    ct.notification_type,
                    ct.response_status,
                    ct.created_at
                FROM campaign_tracking ct
                JOIN users u ON ct.user_id = u.user_id
                WHERE ct.offer_id = 'DISNEY_25_OFF'
                ORDER BY ct.created_at DESC
            """
            
            results = self.db.execute_query(query)
            
            detailed_responses = []
            for row in results:
                detailed_responses.append({
                    'tracking_id': row[0],
                    'user_id': row[1],
                    'user_name': row[2],
                    'user_email': row[3],
                    'notification_type': row[4],
                    'response_status': row[5],
                    'sent_at': row[6]
                })
            
            return detailed_responses
        
        except Exception as e:
            print(f"Error fetching detailed responses: {e}")
            return []
    
    def generate_monitoring_report(self) -> Dict[str, Any]:
        """
        Generate comprehensive monitoring report
        
        Returns:
            Complete monitoring report
        """
        print(f"\n{'='*60}")
        print(f"MONITOR AGENT - Campaign Monitoring Report")
        print(f"{'='*60}")
        
        metrics = self.get_campaign_metrics()
        detailed_responses = self.get_detailed_responses()
        
        report = {
            'report_generated_at': datetime.now().isoformat(),
            'campaign_metrics': metrics,
            'detailed_responses': detailed_responses,
            'summary': {
                'total_users_contacted': metrics.get('total_notifications_sent', 0),
                'total_acceptances': metrics.get('accepted', 0),
                'total_declines': metrics.get('declined', 0),
                'pending_responses': metrics.get('pending', 0),
                'acceptance_rate': f"{metrics.get('acceptance_rate_percent', 0)}%",
                'decline_rate': f"{metrics.get('decline_rate_percent', 0)}%"
            }
        }
        
        print(f"\nTotal Users Contacted: {metrics.get('total_notifications_sent', 0)}")
        print(f"Acceptances: {metrics.get('accepted', 0)} ({metrics.get('acceptance_rate_percent', 0)}%)")
        print(f"Declines: {metrics.get('declined', 0)} ({metrics.get('decline_rate_percent', 0)}%)")
        print(f"Pending: {metrics.get('pending', 0)}")
        
        return report


# ============================================================================
# MAIN ORCHESTRATOR
# ============================================================================

class DisneyOfferCampaignOrchestrator:
    """
    Main orchestrator to run the complete Disney offer campaign
    """
    
    def __init__(self, properties_file: str = "./offer_disney.properties",
                 db_path: str = "./campaign_tracking.db"):
        self.db = CampaignDatabase(db_path)
        self.admin_agent = AdminAgent(properties_file)
        self.user_lookup_agent = UserLookupAgent(self.db)
        self.campaign_agent = CampaignAgent(self.db, self.admin_agent)
        self.monitor_agent = MonitorAgent(self.db)
    
    def run_complete_campaign(self, num_users: int = 10) -> Dict[str, Any]:
        """
        Execute complete campaign workflow
        
        Args:
            num_users: Number of users to target
        
        Returns:
            Complete campaign execution result
        """
        campaign_result = {}
        
        # Step 1: Admin Agent - Validate Offer Configuration
        print(f"\n{'#'*60}")
        print(f"STEP 1: ADMIN AGENT - Validating Offer Configuration")
        print(f"{'#'*60}")
        
        offer_details = self.admin_agent.get_offer_details()
        validation = self.admin_agent.validate_offer_config()
        
        print(f"Offer Details: {json.dumps(offer_details, indent=2)}")
        print(f"Configuration Valid: {validation['valid']}")
        if validation['errors']:
            print(f"Errors: {validation['errors']}")
        
        campaign_result['admin_config'] = {
            'offer_details': offer_details,
            'validation': validation
        }
        
        if not validation['valid']:
            print("❌ Campaign aborted due to configuration errors")
            return campaign_result
        
        # Step 2: User Lookup Agent - Fetch and Qualify Users
        print(f"\n{'#'*60}")
        print(f"STEP 2: USER LOOKUP AGENT - Fetching Qualified Users")
        print(f"{'#'*60}")
        
        lookup_result = self.user_lookup_agent.lookup_and_qualify_users(num_users)
        campaign_result['user_lookup'] = lookup_result
        
        qualified_users = self.user_lookup_agent.get_qualified_users()
        
        # Step 3: Campaign Agent - Send Notifications
        print(f"\n{'#'*60}")
        print(f"STEP 3: CAMPAIGN AGENT - Sending Notifications")
        print(f"{'#'*60}")
        
        campaign_result_data = self.campaign_agent.send_notifications(qualified_users, offer_details)
        campaign_result['campaign_execution'] = campaign_result_data
        
        # Step 4: Monitor Agent - Track Initial Metrics
        print(f"\n{'#'*60}")
        print(f"STEP 4: MONITOR AGENT - Initial Campaign Metrics")
        print(f"{'#'*60}")
        
        monitoring_report = self.monitor_agent.generate_monitoring_report()
        campaign_result['monitoring'] = monitoring_report
        
        return campaign_result
    
    def simulate_user_responses(self, acceptance_percentage: int = 70):
        """
        Simulate user responses to test monitoring agent
        
        Args:
            acceptance_percentage: % of users who accept offer
        """
        print(f"\n{'='*60}")
        print(f"Simulating User Responses (Acceptance Rate: {acceptance_percentage}%)")
        print(f"{'='*60}")
        
        qualified_users = self.user_lookup_agent.get_qualified_users()
        
        for idx, user in enumerate(qualified_users):
            # Simulate acceptance based on percentage
            if idx < len(qualified_users) * acceptance_percentage / 100:
                response = 'ACCEPTED'
                print(f"✓ User {user['name']} ACCEPTED the offer")
            else:
                response = 'DECLINED'
                print(f"✗ User {user['name']} DECLINED the offer")
            
            self.monitor_agent.record_user_response(user['user_id'], response)
        
        # Generate final report
        print(f"\n{'='*60}")
        print(f"FINAL MONITORING REPORT")
        print(f"{'='*60}")
        
        final_report = self.monitor_agent.generate_monitoring_report()
        print(f"\nFinal Report: {json.dumps(final_report['summary'], indent=2)}")
        
        return final_report


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

def main():
    """
    Main execution function
    """
    print(f"\n{'='*60}")
    print(f"DISNEY CHANNEL 25% OFF ANNUAL SUBSCRIPTION CAMPAIGN")
    print(f"LangChain Agentic AI System")
    print(f"{'='*60}")
    
    # Initialize orchestrator
    script_dir = os.path.dirname(os.path.abspath(__file__))
    properties_file = os.path.join(script_dir, "offer_disney.properties")
    db_path = os.path.join(script_dir, "campaign_tracking.db")
    
    orchestrator = DisneyOfferCampaignOrchestrator(
        properties_file=properties_file,
        db_path=db_path
    )
    
    # Run complete campaign
    campaign_results = orchestrator.run_complete_campaign(num_users=10)
    
    # Simulate user responses
    orchestrator.simulate_user_responses(acceptance_percentage=70)
    
    # Save results to JSON
    results_file = os.path.join(script_dir, "campaign_results.json")
    with open(results_file, 'w') as f:
        json.dump(campaign_results, f, indent=2, default=str)
    
    print(f"\n✓ Campaign results saved to {results_file}")
    print(f"✓ Campaign database saved to {db_path}")


if __name__ == "__main__":
    main()

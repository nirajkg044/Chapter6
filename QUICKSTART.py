"""
Disney Campaign Quick Start Guide
Complete Examples for Running the System
"""

# ============================================================================
# EXAMPLE 1: Complete Campaign Execution
# ============================================================================

def example_complete_campaign():
    """
    Run the complete campaign from start to finish
    """
    from LangChain import DisneyOfferCampaignOrchestrator
    
    print("\n" + "="*70)
    print("EXAMPLE 1: Complete Campaign Execution")
    print("="*70)
    
    # Initialize orchestrator
    orchestrator = DisneyOfferCampaignOrchestrator(
        properties_file="./offer_disney.properties",
        db_path="./campaign_tracking.db"
    )
    
    # Run complete campaign
    results = orchestrator.run_complete_campaign(num_users=10)
    
    return results


# ============================================================================
# EXAMPLE 2: Using AdminAgent Only
# ============================================================================

def example_admin_agent():
    """
    Use AdminAgent to configure and validate offer settings
    """
    from LangChain import AdminAgent
    
    print("\n" + "="*70)
    print("EXAMPLE 2: AdminAgent - Configuration Management")
    print("="*70)
    
    # Initialize admin agent
    admin = AdminAgent("./offer_disney.properties")
    
    # Get current offer details
    print("\n1. Current Offer Details:")
    offer_details = admin.get_offer_details()
    for key, value in offer_details.items():
        print(f"   {key}: {value}")
    
    # Validate configuration
    print("\n2. Validating Configuration:")
    validation = admin.validate_offer_config()
    print(f"   Valid: {validation['valid']}")
    if validation['errors']:
        print(f"   Errors: {validation['errors']}")
    if validation['warnings']:
        print(f"   Warnings: {validation['warnings']}")
    
    # Update a setting
    print("\n3. Updating Discount to 30%:")
    success = admin.update_offer_settings("offer.discount.percentage", "30")
    print(f"   Update successful: {success}")
    
    # Revalidate
    validation = admin.validate_offer_config()
    print(f"   Configuration valid: {validation['valid']}")


# ============================================================================
# EXAMPLE 3: Using UserLookupAgent Only
# ============================================================================

def example_user_lookup_agent():
    """
    Use UserLookupAgent to fetch and qualify users
    """
    from LangChain import UserLookupAgent, CampaignDatabase
    
    print("\n" + "="*70)
    print("EXAMPLE 3: UserLookupAgent - User Qualification")
    print("="*70)
    
    # Initialize database and lookup agent
    db = CampaignDatabase("./campaign_tracking.db")
    lookup = UserLookupAgent(db)
    
    # Fetch and qualify users
    print("\n1. Fetching users from JSONPlaceholder API...")
    result = lookup.lookup_and_qualify_users(count=10)
    
    print(f"\n2. Lookup Results:")
    print(f"   API Users Fetched: {result['api_users_fetched']}")
    print(f"   Users Qualified: {result['users_qualified']}")
    print(f"   Users Stored: {result['users_stored']}")
    
    # Get qualified users
    print(f"\n3. Qualified Users (from database):")
    qualified_users = lookup.get_qualified_users()
    for user in qualified_users:
        print(f"   - {user['name']} ({user['email']})")


# ============================================================================
# EXAMPLE 4: Using CampaignAgent Only
# ============================================================================

def example_campaign_agent():
    """
    Use CampaignAgent to send notifications
    """
    from LangChain import CampaignAgent, AdminAgent, CampaignDatabase, UserLookupAgent
    
    print("\n" + "="*70)
    print("EXAMPLE 4: CampaignAgent - Sending Notifications")
    print("="*70)
    
    # Initialize components
    db = CampaignDatabase("./campaign_tracking.db")
    admin = AdminAgent("./offer_disney.properties")
    lookup = UserLookupAgent(db)
    campaign = CampaignAgent(db, admin)
    
    # Get offer details
    offer_details = admin.get_offer_details()
    print(f"\n1. Offer Details:")
    print(f"   Name: {offer_details['name']}")
    print(f"   Discount: {offer_details['discount_percentage']}%")
    print(f"   Price: ${offer_details['original_price']} → ${offer_details['discounted_price']}")
    
    # Get qualified users
    qualified_users = lookup.get_qualified_users()
    print(f"\n2. Target Users: {len(qualified_users)}")
    
    # Send notifications
    print(f"\n3. Sending Notifications...")
    result = campaign.send_notifications(qualified_users, offer_details)
    
    print(f"\n4. Notification Results:")
    print(f"   Emails Sent: {result['emails_sent']}")
    print(f"   SMS Sent: {result['sms_sent']}")


# ============================================================================
# EXAMPLE 5: Using MonitorAgent Only
# ============================================================================

def example_monitor_agent():
    """
    Use MonitorAgent to track and monitor campaign responses
    """
    from LangChain import MonitorAgent, CampaignDatabase
    
    print("\n" + "="*70)
    print("EXAMPLE 5: MonitorAgent - Campaign Monitoring")
    print("="*70)
    
    # Initialize monitor
    db = CampaignDatabase("./campaign_tracking.db")
    monitor = MonitorAgent(db)
    
    # Record sample responses
    print("\n1. Recording User Responses...")
    users_responses = [
        (1, 'ACCEPTED'),
        (2, 'ACCEPTED'),
        (3, 'DECLINED'),
        (4, 'ACCEPTED'),
        (5, 'PENDING'),
        (6, 'ACCEPTED'),
        (7, 'DECLINED'),
        (8, 'ACCEPTED'),
        (9, 'ACCEPTED'),
        (10, 'ACCEPTED'),
    ]
    
    for user_id, response in users_responses:
        monitor.record_user_response(user_id, response)
        print(f"   User {user_id}: {response}")
    
    # Get metrics
    print("\n2. Campaign Metrics:")
    metrics = monitor.get_campaign_metrics()
    print(f"   Total Sent: {metrics['total_notifications_sent']}")
    print(f"   Accepted: {metrics['accepted']} ({metrics['acceptance_rate_percent']}%)")
    print(f"   Declined: {metrics['declined']} ({metrics['decline_rate_percent']}%)")
    print(f"   Pending: {metrics['pending']}")
    
    # Generate report
    print("\n3. Generating Full Report...")
    report = monitor.generate_monitoring_report()
    print(f"   Report generated at: {report['report_generated_at']}")


# ============================================================================
# EXAMPLE 6: Simulating User Responses
# ============================================================================

def example_simulate_responses():
    """
    Simulate user responses to the campaign
    """
    from LangChain import DisneyOfferCampaignOrchestrator
    
    print("\n" + "="*70)
    print("EXAMPLE 6: Simulating User Responses")
    print("="*70)
    
    orchestrator = DisneyOfferCampaignOrchestrator(
        properties_file="./offer_disney.properties",
        db_path="./campaign_tracking.db"
    )
    
    # Simulate 75% acceptance rate
    print("\nSimulating campaign with 75% acceptance rate...")
    report = orchestrator.simulate_user_responses(acceptance_percentage=75)
    
    return report


# ============================================================================
# EXAMPLE 7: Database Query Examples
# ============================================================================

def example_database_queries():
    """
    Query the database directly for detailed analytics
    """
    from LangChain import CampaignDatabase
    
    print("\n" + "="*70)
    print("EXAMPLE 7: Database Query Examples")
    print("="*70)
    
    db = CampaignDatabase("./campaign_tracking.db")
    
    # Query 1: All users in campaign
    print("\n1. All Users in Campaign:")
    query1 = "SELECT name, email, status FROM users LIMIT 5"
    results = db.execute_query(query1)
    for row in results:
        print(f"   {row[0]}: {row[1]} ({row[2]})")
    
    # Query 2: Campaign tracking summary
    print("\n2. Campaign Tracking Summary:")
    query2 = """
        SELECT response_status, COUNT(*) as count 
        FROM campaign_tracking 
        WHERE offer_id = 'DISNEY_25_OFF' 
        GROUP BY response_status
    """
    results = db.execute_query(query2)
    for row in results:
        print(f"   {row[0]}: {row[1]}")
    
    # Query 3: Email notifications
    print("\n3. Email Notifications Sent:")
    query3 = """
        SELECT COUNT(*) FROM campaign_tracking 
        WHERE offer_id = 'DISNEY_25_OFF' AND notification_type = 'EMAIL'
    """
    results = db.execute_query(query3)
    print(f"   Total: {results[0][0]}")


# ============================================================================
# EXAMPLE 8: Custom Campaign Flow
# ============================================================================

def example_custom_flow():
    """
    Build a custom campaign with manual control
    """
    from LangChain import (
        AdminAgent, 
        UserLookupAgent, 
        CampaignAgent, 
        MonitorAgent, 
        CampaignDatabase
    )
    
    print("\n" + "="*70)
    print("EXAMPLE 8: Custom Campaign Flow")
    print("="*70)
    
    # Initialize all components
    db = CampaignDatabase("./campaign_tracking.db")
    admin = AdminAgent("./offer_disney.properties")
    lookup = UserLookupAgent(db)
    campaign = CampaignAgent(db, admin)
    monitor = MonitorAgent(db)
    
    # Step 1: Validate offer
    print("\nStep 1: Validating Offer Configuration...")
    offer_details = admin.get_offer_details()
    print(f"✓ Offer: {offer_details['name']}")
    print(f"✓ Discount: {offer_details['discount_percentage']}%")
    
    # Step 2: Fetch qualified users
    print("\nStep 2: Fetching Qualified Users...")
    result = lookup.lookup_and_qualify_users(count=5)  # Fetch only 5 users
    print(f"✓ Qualified: {result['users_qualified']} users")
    
    # Step 3: Filter users (example: first 3 users)
    qualified = lookup.get_qualified_users()
    filtered_users = qualified[:3]
    print(f"✓ Filtered to: {len(filtered_users)} users for initial test")
    
    # Step 4: Send campaign
    print("\nStep 3: Sending Campaign to Filtered Users...")
    campaign_result = campaign.send_notifications(filtered_users, offer_details)
    print(f"✓ Emails sent: {campaign_result['emails_sent']}")
    
    # Step 5: Monitor results
    print("\nStep 4: Monitoring Campaign Results...")
    metrics = monitor.get_campaign_metrics()
    print(f"✓ Total contacted: {metrics['total_notifications_sent']}")
    print(f"✓ Acceptance rate: {metrics['acceptance_rate_percent']}%")


# ============================================================================
# EXAMPLE 9: Error Handling
# ============================================================================

def example_error_handling():
    """
    Demonstrate error handling in the system
    """
    from LangChain import AdminAgent, UserLookupAgent, CampaignDatabase
    
    print("\n" + "="*70)
    print("EXAMPLE 9: Error Handling")
    print("="*70)
    
    # Test 1: Invalid configuration file
    print("\n1. Testing with invalid configuration...")
    try:
        admin = AdminAgent("./non_existent_file.properties")
        print("   ✗ File loaded (should not happen)")
    except Exception as e:
        print(f"   ✓ Error caught: File doesn't exist")
    
    # Test 2: API connection error
    print("\n2. Testing with API connection...")
    db = CampaignDatabase("./campaign_tracking.db")
    lookup = UserLookupAgent(db)
    
    users = lookup.fetch_users_from_api(limit=10)
    if users:
        print(f"   ✓ Successfully fetched {len(users)} users from API")
    else:
        print("   ✗ API fetch failed (handled gracefully)")
    
    # Test 3: Configuration validation
    print("\n3. Testing configuration validation...")
    admin = AdminAgent("./offer_disney.properties")
    validation = admin.validate_offer_config()
    print(f"   Config valid: {validation['valid']}")
    if validation['errors']:
        print(f"   Errors: {validation['errors']}")


# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    import json
    
    print("\n" + "#"*70)
    print("# Disney Channel Campaign - Quick Start Examples")
    print("# Run individual examples or all at once")
    print("#"*70)
    
    # Uncomment the example you want to run:
    
    # example_admin_agent()
    # example_user_lookup_agent()
    # example_campaign_agent()
    # example_monitor_agent()
    # example_database_queries()
    # example_custom_flow()
    # example_error_handling()
    
    # Run complete campaign (uncomment to run)
    print("\nRunning complete campaign...\n")
    results = example_complete_campaign()
    
    print("\n" + "="*70)
    print("Campaign Summary:")
    print("="*70)
    print(json.dumps(results['monitoring']['summary'], indent=2))
    
    # Simulate responses
    print("\n" + "="*70)
    print("Simulating user responses...\n")
    report = example_simulate_responses()
    
    print("\n" + "="*70)
    print("Final Results:")
    print("="*70)
    print(json.dumps(report['summary'], indent=2))

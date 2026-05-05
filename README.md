# Disney Channel 25% Off Annual Subscription Campaign
## LangChain Agentic AI System

A comprehensive multi-agent system built with LangChain for managing the Disney Channel "25% Off Annual Subscription" campaign.

---

## 📋 Overview

This system implements **4 autonomous AI agents** that work together to execute a complete marketing campaign:

### Agents

1. **AdminAgent** 🔧
   - Configures offer settings in `offer_disney.properties`
   - Validates offer configuration
   - Manages campaign parameters (discount, duration, status, etc.)

2. **UserLookupAgent** 🔍
   - Queries 3rd-party APIs to fetch eligible users
   - Uses JSONPlaceholder API (free public API) - fetches 10 users
   - Applies qualification logic
   - Stores qualified users in SQLite database

3. **CampaignAgent** 📧
   - Sends email notifications to qualified users
   - Sends SMS notifications (when phone available)
   - Records notification status in database
   - Includes personalized offer details in communications

4. **MonitorAgent** 📊
   - Tracks user responses (ACCEPTED/DECLINED)
   - Calculates acceptance and decline rates
   - Generates comprehensive monitoring reports
   - Provides detailed response analytics

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│  DisneyOfferCampaignOrchestrator (Main Controller)     │
└─────────────────────────────────────────────────────────┘
         │
         ├─→ AdminAgent (Configuration)
         ├─→ UserLookupAgent (Data Retrieval)
         ├─→ CampaignAgent (Communication)
         └─→ MonitorAgent (Analytics)
         │
         └─→ CampaignDatabase (SQLite)
```

---

## 📁 Files

```
LangChain/
├── LangChainOffer.py              # Main implementation
├── offer_disney.properties        # Configuration file
├── __init__.py                    # Package initialization
├── campaign_tracking.db           # SQLite database (auto-created)
└── campaign_results.json          # Results log (auto-created)
```

---

## 🗄️ Database Schema

### Users Table
```sql
CREATE TABLE users (
    user_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT NOT NULL,
    phone TEXT,
    status TEXT DEFAULT 'ELIGIBLE',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

### Campaign Tracking Table
```sql
CREATE TABLE campaign_tracking (
    tracking_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    offer_id TEXT NOT NULL,
    notification_type TEXT,           -- EMAIL or SMS
    notification_status TEXT,         -- SENT or FAILED
    response_status TEXT DEFAULT 'PENDING',  -- PENDING, ACCEPTED, DECLINED
    response_date TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
)
```

### Offer Config Table
```sql
CREATE TABLE offer_config (
    config_id INTEGER PRIMARY KEY AUTOINCREMENT,
    config_key TEXT NOT NULL UNIQUE,
    config_value TEXT NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

---

## ⚙️ Configuration (offer_disney.properties)

```properties
# Offer Details
offer.name=Disney Channel Premium Annual Subscription
offer.discount.percentage=25
offer.original.price=120.00
offer.discounted.price=90.00
offer.currency=USD
offer.duration.months=12

# Campaign Configuration
campaign.name=Disney 25% Off Annual Subscription
campaign.start.date=2026-05-04
campaign.end.date=2026-06-04
campaign.status=ACTIVE

# Target Audience
campaign.target.users.min=10
campaign.target.users.max=1000

# Notification Settings
notification.email.enabled=true
notification.sms.enabled=true

# Database
db.type=sqlite
db.path=./campaign_tracking.db
db.auto.create=true
```

---

## 🚀 Installation & Setup

### Requirements
- Python 3.8+
- pip

### Step 1: Install Dependencies

```bash
pip install requests configparser langchain langchain-community
```

Or using requirements.txt:

```bash
pip install -r requirements.txt
```

### Step 2: Verify Files

Ensure these files exist in the `LangChain/` directory:
- `LangChainOffer.py`
- `offer_disney.properties`
- `__init__.py`

### Step 3: Run Campaign

```bash
python LangChainOffer.py
```

---

## 💻 Usage Examples

### Basic Campaign Execution

```python
from LangChain import DisneyOfferCampaignOrchestrator

# Initialize orchestrator
orchestrator = DisneyOfferCampaignOrchestrator()

# Run complete campaign
results = orchestrator.run_complete_campaign(num_users=10)
```

### Individual Agent Usage

#### AdminAgent - Configuration Management

```python
from LangChain import AdminAgent

admin = AdminAgent("./offer_disney.properties")

# Get offer details
offer = admin.get_offer_details()
print(offer)

# Update settings
admin.update_offer_settings("offer.discount.percentage", "30")

# Validate configuration
validation = admin.validate_offer_config()
print(validation)
```

#### UserLookupAgent - Fetch Qualified Users

```python
from LangChain import UserLookupAgent, CampaignDatabase

db = CampaignDatabase()
lookup = UserLookupAgent(db)

# Fetch and qualify users
result = lookup.lookup_and_qualify_users(count=10)
print(f"Qualified users: {result['users_qualified']}")

# Get all qualified users from database
users = lookup.get_qualified_users()
```

#### CampaignAgent - Send Notifications

```python
from LangChain import CampaignAgent, AdminAgent, CampaignDatabase

db = CampaignDatabase()
admin = AdminAgent()
campaign = CampaignAgent(db, admin)

offer_details = admin.get_offer_details()
users = [
    {'user_id': 1, 'name': 'John Doe', 'email': 'john@example.com', 'phone': '+1234567890'},
    {'user_id': 2, 'name': 'Jane Smith', 'email': 'jane@example.com', 'phone': '+0987654321'}
]

# Send notifications
result = campaign.send_notifications(users, offer_details)
print(f"Emails sent: {result['emails_sent']}")
print(f"SMS sent: {result['sms_sent']}")
```

#### MonitorAgent - Track Responses

```python
from LangChain import MonitorAgent, CampaignDatabase

db = CampaignDatabase()
monitor = MonitorAgent(db)

# Record user response
monitor.record_user_response(user_id=1, response='ACCEPTED')

# Get metrics
metrics = monitor.get_campaign_metrics()
print(f"Acceptance Rate: {metrics['acceptance_rate_percent']}%")

# Generate report
report = monitor.generate_monitoring_report()
```

### Simulate User Responses

```python
orchestrator = DisneyOfferCampaignOrchestrator()

# Simulate 70% acceptance rate
final_report = orchestrator.simulate_user_responses(acceptance_percentage=70)
```

---

## 📊 Output Examples

### Campaign Metrics
```json
{
  "total_notifications_sent": 10,
  "accepted": 7,
  "declined": 2,
  "pending": 1,
  "acceptance_rate_percent": 70.0,
  "decline_rate_percent": 20.0
}
```

### Campaign Results (campaign_results.json)
```json
{
  "admin_config": {
    "offer_details": {
      "name": "Disney Channel Premium Annual Subscription",
      "discount_percentage": "25",
      "original_price": "120.00",
      "discounted_price": "90.00",
      "campaign_status": "ACTIVE",
      "start_date": "2026-05-04",
      "end_date": "2026-06-04"
    },
    "validation": {
      "valid": true,
      "errors": [],
      "warnings": []
    }
  },
  "user_lookup": {
    "status": "SUCCESS",
    "api_users_fetched": 10,
    "users_qualified": 10,
    "users_stored": 10
  },
  "campaign_execution": {
    "status": "SUCCESS",
    "total_users": 10,
    "emails_sent": 10,
    "sms_sent": 10
  },
  "monitoring": {
    "report_generated_at": "2026-05-04T14:30:00",
    "campaign_metrics": {
      "total_notifications_sent": 10,
      "accepted": 7,
      "declined": 2,
      "pending": 1
    }
  }
}
```

---

## 🔌 API Integration

### JSONPlaceholder API (User Data Source)

- **Endpoint**: `https://jsonplaceholder.typicode.com/users`
- **Method**: GET
- **Returns**: Array of 10 mock users with fields:
  - `id`: User ID
  - `name`: Full name
  - `email`: Email address
  - `phone`: Phone number
  - `company`: Company information

---

## 🗄️ Database Operations

### Query User Responses

```sql
SELECT u.name, u.email, ct.response_status, ct.response_date
FROM campaign_tracking ct
JOIN users u ON ct.user_id = u.user_id
WHERE ct.offer_id = 'DISNEY_25_OFF'
ORDER BY ct.response_date DESC;
```

### Get Acceptance Statistics

```sql
SELECT 
  response_status,
  COUNT(*) as count,
  ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM campaign_tracking WHERE offer_id = 'DISNEY_25_OFF'), 2) as percentage
FROM campaign_tracking
WHERE offer_id = 'DISNEY_25_OFF'
GROUP BY response_status;
```

### Email Notification History

```sql
SELECT u.name, u.email, ct.notification_status, ct.created_at
FROM campaign_tracking ct
JOIN users u ON ct.user_id = u.user_id
WHERE ct.offer_id = 'DISNEY_25_OFF' AND ct.notification_type = 'EMAIL'
ORDER BY ct.created_at DESC;
```

---

## 📈 Campaign Flow

```
1. AdminAgent
   ├─ Load offer_disney.properties
   ├─ Validate configuration
   └─ Report: OK/ERROR

2. UserLookupAgent
   ├─ Call JSONPlaceholder API
   ├─ Apply qualification logic
   ├─ Store in SQLite DB
   └─ Report: 10 users qualified

3. CampaignAgent
   ├─ For each user:
   │  ├─ Send email notification
   │  ├─ Send SMS notification
   │  └─ Record in database
   └─ Report: 10 emails sent, 10 SMS sent

4. MonitorAgent
   ├─ Record user responses
   ├─ Calculate metrics
   └─ Generate report: 70% acceptance rate
```

---

## 🛠️ Extending the System

### Add Custom API Integration

```python
class UserLookupAgent(ABC):
    def fetch_users_from_custom_api(self, api_key: str):
        url = "https://your-api.com/users"
        headers = {"Authorization": f"Bearer {api_key}"}
        response = requests.get(url, headers=headers)
        return response.json()
```

### Add Email Service Integration

```python
# Replace mock email with real SendGrid integration
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

def send_email(self, recipient_email, recipient_name, offer_details):
    message = Mail(
        from_email='offers@disneychannel.com',
        to_emails=recipient_email,
        subject=offer_details['subject'],
        html_content=self.render_email_template(offer_details)
    )
    sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
    sg.send(message)
```

### Add SMS Service Integration

```python
# Replace mock SMS with real Twilio integration
from twilio.rest import Client

def send_sms(self, recipient_phone, recipient_name, offer_details):
    client = Client(ACCOUNT_SID, AUTH_TOKEN)
    message = client.messages.create(
        body=self.render_sms_template(offer_details),
        from_=self.sms_from_number,
        to=recipient_phone
    )
```

---

## ⚠️ Error Handling

The system includes comprehensive error handling:

- API connection failures gracefully return empty results
- Database errors are caught and logged
- Configuration validation prevents invalid campaigns
- All operations return status indicators

---

## 📝 Logging

Enable detailed logging by adding:

```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
```

---

## 🔒 Security Considerations

1. **API Keys**: Store securely in environment variables
   ```python
   api_key = os.environ.get('SENDGRID_API_KEY')
   ```

2. **Database**: Use password-protected database in production
   ```python
   db_password = os.environ.get('DB_PASSWORD')
   ```

3. **User Data**: Comply with GDPR/CCPA regulations
   - Implement data retention policies
   - Provide user opt-out options
   - Encrypt sensitive data

---

## 📚 References

- [LangChain Documentation](https://docs.langchain.com/)
- [JSONPlaceholder API](https://jsonplaceholder.typicode.com/)
- [SQLite Documentation](https://www.sqlite.org/docs.html)
- [Python Requests Library](https://requests.readthedocs.io/)

---

## 🤝 Contributing

To extend this system:

1. Add new agent classes inheriting from ABC
2. Implement required methods
3. Register with orchestrator
4. Test with sample data

---

## 📄 License

This project is open source and available under the MIT License.

---

## 👤 Author

Created for Disney Channel Campaign Management
Date: May 4, 2026

---

## 🎯 Next Steps

1. ✅ Run `python LangChainOffer.py` to execute campaign
2. ✅ Check `campaign_results.json` for results
3. ✅ Query `campaign_tracking.db` for detailed data
4. ✅ Integrate with real email/SMS services
5. ✅ Add user interface dashboard

---

## 📞 Support

For issues or questions:
1. Check the Configuration section
2. Review error messages in console output
3. Examine campaign_results.json for detailed logs
4. Verify database integrity using SQLite browser


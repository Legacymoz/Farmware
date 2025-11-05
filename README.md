# SMC² - Secure Mobile Communication Core
## Cryptographic Verification for Agricultural Advisories

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/flask-2.3+-green.svg)](https://flask.palletsprojects.com/)

> **Solving fraud and trust issues in critical agricultural advisories through cryptographic verification over basic SMS/USSD channels.**

---

## 🌾 The Problem We Solve

In Kenya and across Sub-Saharan Africa, **farmers rely on SMS for critical agricultural advisories** - pest alerts, weather warnings, fertilizer recommendations. However, **fraudulent messages from bad actors** can devastate harvests and livelihoods.

**Traditional SMS has no authentication** - farmers cannot verify if a critical message about pest control or market prices is genuine or spoofed.

## 🔐 Our Solution: SMC²

**SMC² (Secure Mobile Communication Core)** is a **cryptographic verification system** that ensures message authenticity for agricultural advisories, designed specifically for **feature phones and low-tech environments**.

### 🎯 Core Innovation
- **Verification Codes (VC)** generated using advanced cryptography (FPE/HMAC)
- **USSD-based verification** that works on any basic phone (*123*VC#)
- **Decentralized security** - no internet required for farmers to verify messages

### ✅ How It Works
1. **Advisory Created** → SMC² generates cryptographic VC
2. **SMS Sent** → "Weather Alert: Heavy rain expected. Verify: 123456 *123*123456#"
3. **Farmer Verifies** → Dials *123*123456# on any phone
4. **Instant Confirmation** → USSD returns full message details + authenticity proof

---

## 🏗️ Architecture

SMC² uses a **modular architecture** separating the cryptographic core from the deployment environment:

```
┌─────────────────────────────────────────────────────────────┐
│                    SMC² ECOSYSTEM                           │
├─────────────────────────────────────────────────────────────┤
│  🔐 SMC² CORE (The Engine)                                 │
│  ├── Cryptographic Middleware                              │
│  ├── VC Generation (FPE/HMAC)                             │
│  ├── VC Validation & Decryption                           │
│  └── Message Authentication Logic                          │
├─────────────────────────────────────────────────────────────┤
│  🖥️  SERVER (The Interface)                                │
│  ├── Flask Web Dashboard                                   │
│  ├── Database Management (Farmers, Keys, Advisories)      │
│  ├── USSD Callback Routing                                │
│  ├── Dual SMS Provider Integration                        │
│  └── Real-time Monitoring & Logs                          │
└─────────────────────────────────────────────────────────────┘
```

### Component Relationship
- **SMC² Core**: Stateless cryptographic engine (reusable library)
- **Server**: Production environment that calls SMC² for verification
- **Integration**: Server → SMC² Core → Cryptographic Operations → Response

---

## 🎯 Target Users

| User Group | Description | Use Case |
|------------|-------------|----------|
| **🏢 Primary Customers** | Agricultural Advisory Organizations<br/>*(iShamba, NGOs, Farmer Cooperatives)* | Deploy SMC² to secure existing SMS channels |
| **👨‍🌾 End Beneficiaries** | Farmers with feature phones | Receive & verify authentic agricultural advisories |
| **👩‍💼 Administrators** | IT Staff & Program Managers | Use web dashboard to send verified advisories |

---

## 🚀 Key Features

### 🔐 **Cryptographic Security**
- **Advanced Verification Codes** using Format Preserving Encryption (FPE)
- **HMAC Authentication** for message integrity
- **Decentralized verification** - no internet required for farmers

### 📱 **Universal Compatibility**
- **Works on any phone** - feature phones, smartphones, old Nokia devices
- **USSD-based verification** (*123*VC#) - available on all GSM networks
- **SMS delivery** through multiple providers with automatic failover

### 🌐 **Production-Ready Interface**
- **Web Dashboard** for administrators to create and send advisories
- **Real-time monitoring** of message delivery and verification rates
- **Database management** for farmers, keys, and advisory content

### 🔄 **Reliable Message Delivery**
- **Dual SMS Provider** support (Africa's Talking + Celcom)
- **Automatic failover** if primary provider fails
- **Delivery confirmation** and retry mechanisms

---

## 📊 Business Impact

### For Agricultural Organizations
- ✅ **Eliminate advisory fraud** - farmers trust your messages
- ✅ **Increase engagement** - verified messages have higher action rates
- ✅ **Reduce support calls** - farmers can self-verify authenticity
- ✅ **Scale with confidence** - cryptographic security that grows with you

### For Farmers
- ✅ **Trust critical advisories** - know messages are authentic
- ✅ **Verify on any phone** - no smartphone or internet required
- ✅ **Protect livelihoods** - avoid fraudulent advice that damages crops
- ✅ **Easy verification** - simple USSD code (*123*VC#)

---

## 🛠️ Quick Start

### Prerequisites
- Python 3.8+
- PostgreSQL database
- SMS provider account (Africa's Talking or Celcom)
- USSD code registered with telecom provider

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/smc-core.git
cd smc-core

# Set up virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your credentials and API keys
```

### Configuration

```bash
# Edit .env file with your settings
DATABASE_URL=postgresql://user:pass@localhost:5432/smc_db
SMS_PROVIDER=celcom
AFRICASTALKING_API_KEY=your_at_key_here
CELCO_API_KEY=your_celcom_key_here
SMC_SECRET_KEY=your_cryptographic_master_key
```

### Database Setup

```bash
cd Server

# Initialize database
flask db upgrade

# Create sample farmers and advisories
python populate_db.py create-sample-data

# Verify setup
python populate_db.py status
```

### Launch SMC²

```bash
# Start the Server (Web Dashboard + API)
python main.py

# Access web dashboard
# http://localhost:5000
```

---

## 📱 Usage Examples

### 1. Send Verified Advisory via Web Dashboard
1. Navigate to http://localhost:5000
2. Select an advisory from the table
3. Choose target farmer
4. Click "Send Advisory SMS"
5. SMC² generates VC and sends SMS with verification instructions

### 2. Send Advisory via API
```bash
curl -X POST http://localhost:5000/send-advisory \
  -H "Content-Type: application/json" \
  -d '{
    "message_id": "1",
    "phone_number": "+254701016878"
  }'
```

### 3. Farmer Verification Process
**Farmer receives SMS:**
```
Weather Alert: Heavy rain expected tomorrow. 
Protect crops immediately. 
Verify: 123456 *123*123456#
```

**Farmer dials:** `*123*123456#`

**USSD Response:**
```
✅ VERIFIED MESSAGE
From: iShamba Agricultural Services
Full Message: Weather Alert: Heavy rain 
expected tomorrow. Protect crops immediately.
Advisory ID: WTH-2024-001
Sent: 2024-11-06 14:30
```

---

## 🔧 API Reference

### Core Endpoints

| Endpoint | Method | Description | SMC² Role |
|----------|--------|-------------|-----------|
| `/send-advisory` | POST | Send verified advisory to farmer | Generates VC using SMC² Core |
| `/ussd-callback` | POST | Handle farmer verification requests | Validates VC using SMC² Core |
| `/verify-advisory` | POST | Manual verification endpoint | Direct SMC² Core validation |

### Example: Send Advisory
```bash
POST /send-advisory
Content-Type: application/json

{
  "message_id": "1",
  "phone_number": "+254701016878"
}
```

**Response:**
```json
{
  "success": true,
  "message_id": "1",
  "phone_number": "+254701016878",
  "advisory_title": "Weather Alert: Heavy Rain Expected",
  "verification_code": "123456",
  "sms_content": "Weather Alert: Heavy Rain Expected. Verify: 123456 *123*123456#",
  "sms_status": "sent"
}
```

---

## 🗄️ Database Management

### Add New Farmers
```bash
# Add individual farmer
python populate_db.py create-farmer --phone '+254XXXXXXXXX' --secret-key 'FarmerSecret2024'

# Add multiple sample farmers
python populate_db.py create-sample-farmers

# View all farmers
python populate_db.py show-farmers
```

### Manage Advisories
```bash
# Add new advisory
python populate_db.py create-advisory --title "Pest Alert" --message "Cutworms detected in region"

# View all advisories
python populate_db.py show-advisories

# Database status
python populate_db.py status
```

---

## 🧪 Testing & Verification

### Test SMC² Core Functions
```bash
# Test VC generation
curl -X POST http://localhost:5001/get-messageID \
  -H "Content-Type: application/json" \
  -d '{
    "vc": "123456",
    "secret_key": "TestSecret2024"
  }'
```

### Test End-to-End Workflow
```bash
# 1. Send advisory (generates VC)
curl -X POST http://localhost:5000/send-advisory \
  -H "Content-Type: application/json" \
  -d '{"message_id": "1", "phone_number": "+254701016878"}'

# 2. Simulate farmer verification
curl -X POST http://localhost:5000/ussd-callback \
  -H "Content-Type: application/json" \
  -d '{
    "sessionId": "test123",
    "serviceCode": "*123#",
    "phoneNumber": "+254701016878",
    "text": "123456"
  }'
```

---

## 🌍 Deployment

### Self-Hosted (Recommended)
```bash
# Production deployment with proper secrets management
# Use environment-specific .env files
# Deploy on dedicated server or private cloud

# Example: Ubuntu server deployment
sudo systemctl enable postgresql
sudo systemctl start postgresql
# Configure nginx reverse proxy
# Set up SSL certificates
# Configure firewall rules
```

### Environment Configuration
- **Development**: Local server + ngrok for USSD testing
- **Staging**: Cloud instance with test SMS providers
- **Production**: Dedicated server with proper SMS provider accounts

---

## 🔐 Security Considerations

### Cryptographic Security
- **Master Keys**: Store SMC_SECRET_KEY securely (environment variables, key vaults)
- **Farmer Keys**: Individual cryptographic keys per farmer stored as binary data
- **VC Generation**: Uses Format Preserving Encryption for phone-friendly codes

### Network Security
- **HTTPS**: Required for production USSD callbacks
- **API Authentication**: Secure all API endpoints
- **Database**: Use encrypted connections and proper access controls

### Operational Security
- **Key Rotation**: Regular rotation of master keys
- **Audit Logs**: Complete logging of all verification requests
- **Access Control**: Role-based access to web dashboard

---

## 📋 System Requirements

### Minimum Requirements
- **CPU**: 2 cores, 2.4GHz
- **RAM**: 4GB
- **Storage**: 20GB SSD
- **Network**: Stable internet for SMS provider APIs
- **Database**: PostgreSQL 12+

### Recommended for Production
- **CPU**: 4+ cores, 3.0GHz
- **RAM**: 8GB+
- **Storage**: 50GB+ SSD with backups
- **Network**: Redundant internet connections
- **Database**: PostgreSQL cluster with replication

---

## 🤝 Contributing

We welcome contributions to SMC²! Here's how to get started:

### Development Setup
```bash
# Fork the repository
git clone https://github.com/yourusername/smc-core.git
cd smc-core

# Create development environment
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run tests
pytest tests/

# Start development servers
python Server/main.py  # Server on port 5000
python SMC/smc_server.py  # SMC Core on port 5001
```

### Contribution Guidelines
1. **Fork** the repository
2. **Create** feature branch (`git checkout -b feature/amazing-feature`)
3. **Write tests** for new functionality
4. **Ensure** all tests pass
5. **Commit** changes (`git commit -m 'Add amazing feature'`)
6. **Push** to branch (`git push origin feature/amazing-feature`)
7. **Open** Pull Request

---

## 📞 Support & Community

### Getting Help
- **Documentation**: See `/docs` folder for detailed guides
- **Issues**: Report bugs via GitHub Issues
- **Discussions**: Join our community discussions

### Enterprise Support
For production deployments and enterprise support:
- **Technical Consulting**: Architecture and deployment guidance
- **Custom Integration**: Tailored solutions for your organization
- **SLA Support**: Production support with guaranteed response times

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **Africa's Talking** - SMS service provider
- **Celcom Africa** - Alternative SMS provider
- **iShamba** - Agricultural advisory inspiration
- **Kenyan Farmers** - The beneficiaries who inspired this solution
- **Flask Framework** - Web application foundation
- **PostgreSQL** - Reliable database foundation


**SMC² - Securing Agricultural Communications, One Message at a Time** 🌾🔐

*Built with ❤️ for farmers across Sub-Saharan Africa*
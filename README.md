# DARI Wallet Backend

A secure, semi-custodial, multi-chain blockchain wallet backend built with FastAPI that supports Ethereum, BSC, Tron, Solana, Bitcoin, XRP, and more.

## 🚀 Features

### Core Features
- **Multi-chain Support**: Ethereum, BSC, Tron, Solana, Bitcoin, XRP
- **Semi-custodial**: Users control their private keys (encrypted)
- **Role-based Access**: User, Admin, Support roles
- **JWT Authentication**: Secure token-based authentication
- **Username Resolution**: `username@dari` system for easy transfers
- **Default Currency Selection**: Users can select their preferred default currency during registration
- **Comprehensive Notifications**: App, Email, and SMS notifications for all wallet activities
- **OTP Verification**: Email and SMS OTP verification for enhanced login security (admin configurable)

### Wallet Management
- **Wallet Generation**: Create wallets for all supported chains
- **Balance Tracking**: Real-time balance updates
- **Transaction History**: Complete transaction logs
- **Token Support**: ERC20, TRC20, SPL tokens

### Security Features
- **Encrypted Storage**: Private keys encrypted with AES
- **Rate Limiting**: API rate limiting protection
- **Input Validation**: Comprehensive input sanitization
- **Audit Logging**: Complete activity logging
- **PIN Verification**: All transfers require PIN verification with OTP setup
- **Admin OTP Login**: Admin and role-based admin logins require OTP verification
- **Comprehensive Login Logging**: Device info, IP, location, and fraud analysis
- **Transaction Fraud Detection**: Real-time fraud analysis with risk scoring
- **Peak Usage Analytics**: Monitor user activity patterns and frequent transfers
- **Admin Security Controls**: User unblocking and suspicious activity monitoring

### Admin Features
- **User Management**: Admin dashboard for user control
- **System Monitoring**: Real-time system statistics
- **Token Management**: Add/remove supported tokens
- **Broadcast Messages**: Send notifications to users
- **Currency Management**: Add/remove supported currencies
- **Notification Templates**: Manage notification templates for different events
- **Notification Settings**: Configure email and SMS services
- **OTP Management**: Configure OTP settings for login security

## 📋 Prerequisites

- Python 3.11+
- PostgreSQL 15+
- Redis 7+
- Docker & Docker Compose (optional)

## 🛠️ Installation

### Option 1: Docker (Recommended)

1. Clone the repository:
```bash
git clone <repository-url>
cd dari-wallet-backend
```

2. Copy environment file:
```bash
cp env.example .env
```

3. Edit `.env` file with your configuration:
```bash
# Database Configuration
DATABASE_URL=postgresql://dari_user:dari_password@localhost:5432/dari_wallet
ASYNC_DATABASE_URL=postgresql+asyncpg://dari_user:dari_password@localhost:5432/dari_wallet

# Security
SECRET_KEY=your-secret-key-here-make-it-long-and-random
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Blockchain RPC URLs
ETHEREUM_RPC_URL=https://mainnet.infura.io/v3/your-project-id
BSC_RPC_URL=https://bsc-dataseed1.binance.org
TRON_RPC_URL=https://api.trongrid.io
SOLANA_RPC_URL=https://api.mainnet-beta.solana.com
BITCOIN_RPC_URL=http://localhost:8332
XRP_RPC_URL=https://s1.ripple.com:51234

# Third-party API Keys
COINGECKO_API_KEY=your-coingecko-api-key
ETHERSCAN_API_KEY=your-etherscan-api-key
BSCSCAN_API_KEY=your-bscscan-api-key

# Email Configuration
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# SMS Configuration
SMS_API_KEY=your-sms-api-key
SMS_API_URL=https://api.sms-service.com/send
```

4. Start the services:
```bash
docker-compose up -d
```

5. Initialize the database and run security migrations:
```bash
docker-compose exec app python -c "from app.core.database import engine; from app.models import *; Base.metadata.create_all(bind=engine)"
docker-compose exec app python scripts/migrate_pin_and_logging.py
```

### Option 2: Local Development

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Set up PostgreSQL and Redis

3. Copy and configure environment file:
```bash
cp env.example .env
# Edit .env with your configuration
```

4. Initialize the database and run security migrations:
```bash
python -c "from app.core.database import engine; from app.models import *; Base.metadata.create_all(bind=engine)"
python scripts/migrate_pin_and_logging.py
```

5. Run the application:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Option 3: Linux Server Deployment

1. Transfer code to your Linux server:
```bash
# Using SCP
scp -r /path/to/your/DARI\ WALLET\ BACKEND/ user@your-server-ip:/home/user/

# Or using Git
git clone https://your-repo-url.git
cd DARI-WALLET-BACKEND
```

2. Set up environment:
```bash
# Install dependencies
pip install -r requirements.txt

# Or using virtual environment
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

3. Configure environment variables:
```bash
nano .env
```

Add your production configuration:
```env
# Database
DATABASE_URL=postgresql://username:password@localhost:5432/wallet_db

# Security
SECRET_KEY=your-super-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# OTP Configuration
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# CORS
ALLOWED_ORIGINS=["https://yourdomain.com", "http://localhost:3000"]

# Debug mode (set to False for production)
DEBUG=False
```

4. Run database migrations:
```bash
python scripts/migrate_pin_and_logging.py
```

5. Test the implementation:
```bash
python test_security_features.py
```

6. Start the application:
```bash
# Direct start
uvicorn app.main:app --host 0.0.0.0 --port 8000

# Or using systemd service
sudo systemctl enable wallet-backend
sudo systemctl start wallet-backend
```

## 📚 API Documentation

Once the application is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## 🔐 Authentication

### Register a new user:
```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "username": "testuser",
    "password": "securepassword123",
    "full_name": "Test User",
    "default_currency_id": 1
  }'
```

### Login:
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepassword123"
  }'
```

## 💼 Wallet Operations

### Create a wallet:
```bash
curl -X POST "http://localhost:8000/api/v1/wallet/create" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "chain": "ethereum"
  }'
```

### Get wallet balance:
```bash
curl -X GET "http://localhost:8000/api/v1/wallet/ethereum" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Send transaction (with PIN verification):
```bash
curl -X POST "http://localhost:8000/api/v1/wallet/transaction/send" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "transaction_data": {
      "chain": "ethereum",
      "to_address": "0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6",
      "amount": 0.001
    },
    "pin_verify": {
      "pin": "1234"
    }
  }'
```

## 📛 Username Resolution

### Set username alias:
```bash
curl -X POST "http://localhost:8000/api/v1/alias/set" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "alice"
  }'
```

### Resolve username:
```bash
curl -X GET "http://localhost:8000/api/v1/alias/resolve/alice"
```

## 🔧 Admin Operations

### Get system statistics:
```bash
curl -X GET "http://localhost:8000/api/v1/admin/stats" \
  -H "Authorization: Bearer ADMIN_ACCESS_TOKEN"
```

### Get all users:
```bash
curl -X GET "http://localhost:8000/api/v1/admin/users" \
  -H "Authorization: Bearer ADMIN_ACCESS_TOKEN"
```

### Get login statistics:
```bash
curl -X GET "http://localhost:8000/api/v1/admin/login-statistics" \
  -H "Authorization: Bearer ADMIN_ACCESS_TOKEN"
```

### Get suspicious activity:
```bash
curl -X GET "http://localhost:8000/api/v1/admin/suspicious-activity" \
  -H "Authorization: Bearer ADMIN_ACCESS_TOKEN"
```

### Unblock user from PIN restrictions:
```bash
curl -X POST "http://localhost:8000/api/v1/admin/user/1/unblock" \
  -H "Authorization: Bearer ADMIN_ACCESS_TOKEN"
```

## 💰 Currency Management

### Get all currencies:
```bash
curl -X GET "http://localhost:8000/api/v1/currencies"
```

### Create a new currency (admin only):
```bash
curl -X POST "http://localhost:8000/api/v1/currencies" \
  -H "Authorization: Bearer ADMIN_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "code": "ADA",
    "name": "Cardano",
    "symbol": "₳",
    "is_crypto": true
  }'
```

## 🔐 PIN Management

### Set PIN (requires OTP verification):
```bash
curl -X POST "http://localhost:8000/api/v1/pin/set" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "otp_verify": {
      "email": "user@example.com",
      "otp_code": "123456",
      "otp_type": "login"
    },
    "pin": "1234"
  }'
```

### Get PIN status:
```bash
curl -X GET "http://localhost:8000/api/v1/pin/status" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## 📊 Analytics & Security

### Get frequent transfers:
```bash
curl -X GET "http://localhost:8000/api/v1/wallet/analytics/frequent-transfers" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Get fraud indicators:
```bash
curl -X GET "http://localhost:8000/api/v1/wallet/analytics/fraud-indicators" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Get comprehensive transaction history:
```bash
curl -X GET "http://localhost:8000/api/v1/wallet/transaction/history/comprehensive" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Get peak usage times:
```bash
curl -X GET "http://localhost:8000/api/v1/wallet/analytics/peak-usage" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## 🔔 Notification Management

### Get user notifications:
```bash
curl -X GET "http://localhost:8000/api/v1/notifications" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Update notification settings:
```bash
curl -X PUT "http://localhost:8000/api/v1/notifications/settings" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "email_enabled": true,
    "sms_enabled": false,
    "transfer_notifications": true,
    "login_notifications": true
  }'
```

### Send notification to user (admin only):
```bash
curl -X POST "http://localhost:8000/api/v1/notifications/admin/send" \
  -H "Authorization: Bearer ADMIN_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 1,
    "notification_type": "promotion",
    "title": "New Feature Available",
    "message": "Check out our new wallet features!"
  }'
```

## 🔐 OTP Verification

### Request OTP for login:
```bash
curl -X POST "http://localhost:8000/api/v1/otp/request" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "otp_type": "login",
    "channel": "email"
  }'
```

### Verify OTP:
```bash
curl -X POST "http://localhost:8000/api/v1/otp/verify" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "otp_code": "123456",
    "otp_type": "login"
  }'
```

### Verify OTP for admin login:
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login/verify-otp" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@example.com",
    "otp_code": "123456"
  }'
```

### Check OTP status:
```bash
curl -X GET "http://localhost:8000/api/v1/otp/status?otp_type=login&channel=email"
```

### Manage OTP configurations (admin only):
```bash
# Get all OTP configs
curl -X GET "http://localhost:8000/api/v1/otp/admin/configs" \
  -H "Authorization: Bearer ADMIN_ACCESS_TOKEN"

# Enable login OTP
curl -X PUT "http://localhost:8000/api/v1/otp/admin/configs/1" \
  -H "Authorization: Bearer ADMIN_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "is_enabled": true
  }'
```

## 🏗️ Project Structure

```
dari-wallet-backend/
├── app/
│   ├── core/           # Core configuration and database
│   ├── models/         # Database models
│   ├── routes/         # API routes
│   ├── schemas/        # Pydantic schemas
│   ├── services/       # Business logic
│   ├── utils/          # Utility functions
│   └── main.py         # FastAPI application
├── logs/               # Application logs
├── config/             # Configuration files
├── requirements.txt    # Python dependencies
├── Dockerfile          # Docker configuration
├── docker-compose.yml  # Docker services
└── README.md          # This file
```

## 🔒 Security Considerations

1. **Private Key Encryption**: All private keys are encrypted using AES-256
2. **Rate Limiting**: API endpoints are protected with rate limiting
3. **Input Validation**: All inputs are validated and sanitized
4. **Audit Logging**: All sensitive operations are logged
5. **CORS Protection**: Configured CORS policies
6. **HTTPS**: Use HTTPS in production
7. **PIN Verification**: All transfers require PIN verification with OTP setup
8. **Admin OTP Login**: Admin and role-based admin logins require OTP verification
9. **Comprehensive Login Logging**: Device info, IP, location, and fraud analysis
10. **Transaction Fraud Detection**: Real-time fraud analysis with risk scoring
11. **Failed Attempt Tracking**: Users blocked after 10 failed PIN attempts
12. **Admin Security Controls**: User unblocking and suspicious activity monitoring

## 🚀 Deployment

### Production Deployment

1. Set up a production server with PostgreSQL and Redis
2. Configure environment variables for production
3. Use a reverse proxy (nginx) for SSL termination
4. Set up monitoring and logging
5. Use Docker for containerized deployment
6. Run security migrations: `python scripts/migrate_pin_and_logging.py`
7. Test security features: `python test_security_features.py`

### Environment Variables

Key environment variables for production:

```bash
# Security
SECRET_KEY=your-production-secret-key
ENVIRONMENT=production
DEBUG=false

# Database
DATABASE_URL=postgresql://user:password@host:5432/dari_wallet

# Redis
REDIS_URL=redis://host:6379/0

# Blockchain RPC URLs
ETHEREUM_RPC_URL=https://mainnet.infura.io/v3/your-project-id
BSC_RPC_URL=https://bsc-dataseed1.binance.org
# ... other RPC URLs

# API Keys
COINGECKO_API_KEY=your-api-key
ETHERSCAN_API_KEY=your-api-key
# ... other API keys

# OTP Configuration
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# CORS
ALLOWED_ORIGINS=["https://yourdomain.com", "http://localhost:3000"]
```

### Linux Server Deployment

For direct deployment to Linux server:

```bash
# 1. Transfer code to server
scp -r /path/to/your/DARI\ WALLET\ BACKEND/ user@your-server-ip:/home/user/

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
nano .env

# 4. Run migrations
python scripts/migrate_pin_and_logging.py

# 5. Test security features
python test_security_features.py

# 6. Start application
uvicorn app.main:app --host 0.0.0.0 --port 8000

# Or using systemd service
sudo systemctl enable wallet-backend
sudo systemctl start wallet-backend
```

### Security Features Testing

After deployment, test all security features:

```bash
# Test PIN management
curl -X POST "http://your-domain.com/api/v1/pin/set" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"otp_verify": {"email": "user@example.com", "otp_code": "123456", "otp_type": "login"}, "pin": "1234"}'

# Test transfer with PIN
curl -X POST "http://your-domain.com/api/v1/wallet/transaction/send" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"transaction_data": {"chain": "ethereum", "to_address": "0x...", "amount": "1.0"}, "pin_verify": {"pin": "1234"}}'

# Test admin login with OTP
curl -X POST "http://your-domain.com/api/v1/auth/login/verify-otp" \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@example.com", "otp_code": "123456"}'
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Create an issue on GitHub
- Check the API documentation at `/docs`
- Review the logs in the `logs/` directory

## 🔄 Roadmap

- [x] **PIN Verification System** - All transfers require PIN verification
- [x] **Admin OTP Login** - Admin and role-based admin logins require OTP
- [x] **Comprehensive Login Logging** - Device info, IP, location tracking
- [x] **Transaction Fraud Detection** - Real-time fraud analysis with risk scoring
- [x] **Peak Usage Analytics** - User activity patterns and frequent transfers
- [x] **Admin Security Controls** - User unblocking and suspicious activity monitoring
- [ ] Hardware wallet support
- [ ] Mobile app SDK
- [ ] Advanced analytics dashboard
- [ ] DeFi integration
- [ ] Cross-chain bridges
- [ ] NFT support
- [ ] Staking features 
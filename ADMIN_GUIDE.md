# DARI Wallet Admin Management Guide

## 📋 Table of Contents
1. [Admin Account Types](#admin-account-types)
2. [Creating Admin Accounts](#creating-admin-accounts)
3. [Admin Login](#admin-login)
4. [Admin API Endpoints](#admin-api-endpoints)
5. [Role-Based Access Control](#role-based-access-control)
6. [Testing with Ganache](#testing-with-ganache)
7. [Production Deployment](#production-deployment)

## 🔐 Admin Account Types

### Super Admin
- **Access**: Full system access
- **Permissions**: All admin functions + user management + system configuration
- **Default Email**: `admin@dari.com`
- **Default Password**: `admin123456`

### Admin
- **Access**: Limited admin functions
- **Permissions**: User management, terms management, basic admin functions
- **Default Email**: `moderator@dari.com`
- **Default Password**: `moderator123456`

## 👤 Creating Admin Accounts

### Method 1: Using Database Script (Recommended)

1. **Run the initialization script**:
```bash
python scripts/init_db.py
```

This creates:
- Super Admin: `admin@dari.com` / `admin123456`
- Admin: `moderator@dari.com` / `moderator123456`

### Method 2: Manual Database Insert

```sql
-- Create Super Admin
INSERT INTO users (email, username, hashed_password, full_name, is_active, is_verified, role_id)
VALUES (
    'admin@dari.com',
    'superadmin',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj3bp.gS.Oi.', -- admin123456
    'Super Administrator',
    true,
    true,
    1
);

-- Create Admin
INSERT INTO users (email, username, hashed_password, full_name, is_active, is_verified, role_id)
VALUES (
    'moderator@dari.com',
    'admin',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj3bp.gS.Oi.', -- moderator123456
    'Administrator',
    true,
    true,
    2
);
```

### Method 3: Using API (After first admin is created)

```bash
# Create new admin via API
curl -X POST "http://localhost:8000/api/v1/admin/users/create" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "newadmin@dari.com",
    "username": "newadmin",
    "password": "securepassword123",
    "full_name": "New Administrator",
    "role": "admin"
  }'
```

## 🔑 Admin Login

### Login Request
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@dari.com",
    "password": "admin123456"
  }'
```

### Login Response
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

## 🛠️ Admin API Endpoints

### User Management

#### Get All Users
```bash
curl -X GET "http://localhost:8000/api/v1/admin/users" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

#### Get User by ID
```bash
curl -X GET "http://localhost:8000/api/v1/admin/users/1" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

#### Create New User
```bash
curl -X POST "http://localhost:8000/api/v1/admin/users/create" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "username": "newuser",
    "password": "password123",
    "full_name": "New User",
    "role": "user"
  }'
```

#### Update User
```bash
curl -X PUT "http://localhost:8000/api/v1/admin/users/1" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "Updated Name",
    "is_active": true
  }'
```

#### Delete User
```bash
curl -X DELETE "http://localhost:8000/api/v1/admin/users/1" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

### Terms and Conditions Management

#### Get All Terms
```bash
curl -X GET "http://localhost:8000/api/v1/terms" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

#### Create New Terms
```bash
curl -X POST "http://localhost:8000/api/v1/terms" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "version": "2.0",
    "title": "Updated Terms and Conditions",
    "content": "# New Terms\n\nUpdated terms content...",
    "status": "active",
    "is_current": true
  }'
```

#### Update Terms
```bash
curl -X PUT "http://localhost:8000/api/v1/terms/1" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "# Updated Terms\n\nNew content...",
    "status": "active"
  }'
```

### System Analytics

#### Get System Statistics
```bash
curl -X GET "http://localhost:8000/api/v1/admin/analytics/overview" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

#### Get User Activity
```bash
curl -X GET "http://localhost:8000/api/v1/admin/analytics/user-activity" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

#### Get Transaction Analytics
```bash
curl -X GET "http://localhost:8000/api/v1/admin/analytics/transactions" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

## 🔒 Role-Based Access Control

### Super Admin Permissions
- ✅ User management (CRUD)
- ✅ Terms and conditions management
- ✅ System configuration
- ✅ Analytics and reports
- ✅ Security settings
- ✅ Database management

### Admin Permissions
- ✅ User management (Read, Update)
- ✅ Terms and conditions management
- ✅ Basic analytics
- ❌ System configuration
- ❌ Security settings
- ❌ Database management

## 🧪 Testing with Ganache

### 1. Install Ganache
```bash
# Install Ganache CLI
npm install -g ganache-cli

# Or download Ganache Desktop from https://trufflesuite.com/ganache/
```

### 2. Start Ganache
```bash
# Start Ganache CLI
ganache-cli --port 8545 --network-id 1337

# Or start Ganache Desktop and note the RPC URL
```

### 3. Configure Environment
```bash
# Add to your .env file
GANACHE_RPC_URL=http://localhost:8545
```

### 4. Test Ganache Integration

#### Create Wallet on Ganache
```bash
curl -X POST "http://localhost:8000/api/v1/wallet/create" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "chain": "ganache"
  }'
```

#### Get Ganache Wallet Balance
```bash
curl -X GET "http://localhost:8000/api/v1/wallet/ganache" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### Send Test Transaction
```bash
curl -X POST "http://localhost:8000/api/v1/wallet/transaction/send" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "transaction_data": {
      "chain": "ganache",
      "to_address": "0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6",
      "amount": 0.001
    },
    "pin_verify": {
      "pin": "1234"
    }
  }'
```

### 5. Ganache Testing Tips
- **Network ID**: 1337 (default)
- **Chain ID**: 1337
- **Gas Limit**: 21000 (for simple transfers)
- **Gas Price**: Auto-calculated
- **Accounts**: 10 pre-funded accounts with 100 ETH each

## 🚀 Production Deployment

### 1. Environment Configuration
```bash
# Production .env
ENVIRONMENT=production
DEBUG=false
DATABASE_URL=postgresql://prod_user:prod_password@prod_host:5432/dari_wallet_prod
SECRET_KEY=your-super-secure-production-secret-key
ALLOWED_ORIGINS=["https://mybbi.in", "https://dariwallet.com"]
```

### 2. Database Migration
```bash
# Create production database
python scripts/create_tables.py

# Initialize production data
python scripts/init_db.py
python scripts/init_currencies.py
python scripts/init_notifications.py
python scripts/init_otp_configs.py
python scripts/init_terms.py
```

### 3. Docker Deployment
```bash
# Build and run with Docker
docker-compose up -d

# Or build custom image
docker build -t dari-wallet-backend .
docker run -d -p 8000:8000 --env-file .env dari-wallet-backend
```

### 4. Security Checklist
- [ ] Change default admin passwords
- [ ] Configure SSL/TLS certificates
- [ ] Set up proper firewall rules
- [ ] Enable rate limiting
- [ ] Configure backup strategy
- [ ] Set up monitoring and logging
- [ ] Enable CORS for production domains only

## 📊 API Documentation

### Swagger UI
Access the interactive API documentation at:
- **Development**: http://localhost:8000/docs
- **Production**: https://your-domain.com/docs

### ReDoc
Alternative documentation at:
- **Development**: http://localhost:8000/redoc
- **Production**: https://your-domain.com/redoc

## 🔧 Troubleshooting

### Common Issues

#### 1. Admin Login Fails
```bash
# Check if admin user exists
python -c "
from app.core.database import SessionLocal
from app.models.user import User
db = SessionLocal()
admin = db.query(User).filter(User.email == 'admin@dari.com').first()
print(f'Admin exists: {admin is not None}')
db.close()
"
```

#### 2. Ganache Connection Issues
```bash
# Test Ganache connection
curl -X POST http://localhost:8545 \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"eth_blockNumber","params":[],"id":1}'
```

#### 3. CORS Issues
```bash
# Check CORS configuration
curl -H "Origin: https://mybbi.in" \
  -H "Access-Control-Request-Method: POST" \
  -H "Access-Control-Request-Headers: Content-Type" \
  -X OPTIONS http://localhost:8000/api/v1/auth/login
```

## 📞 Support

For admin-related issues:
- **Email**: admin@dari.com
- **Documentation**: /docs
- **GitHub Issues**: [Repository Issues](https://github.com/your-repo/issues)

---

**⚠️ Security Note**: Always change default passwords in production and use strong, unique passwords for admin accounts. 
# DARI Wallet Backend Testing Guide

## 📋 Table of Contents
1. [Quick Start Testing](#quick-start-testing)
2. [API Testing](#api-testing)
3. [Ganache Testing](#ganache-testing)
4. [Database Testing](#database-testing)
5. [Security Testing](#security-testing)
6. [Performance Testing](#performance-testing)
7. [Integration Testing](#integration-testing)

## 🚀 Quick Start Testing

### 1. Start the Application
```bash
# Start all services with Docker
docker-compose up -d

# Or start locally
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 2. Initialize Database
```bash
# Create tables
python scripts/create_tables.py

# Initialize data
python scripts/init_db.py
python scripts/init_currencies.py
python scripts/init_notifications.py
python scripts/init_otp_configs.py
python scripts/init_terms.py
```

### 3. Verify Setup
```bash
# Check health endpoint
curl http://localhost:8000/health

# Check API documentation
open http://localhost:8000/docs
```

## 🔧 API Testing

### Authentication Testing

#### 1. Admin Login
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@dari.com",
    "password": "admin123456"
  }'
```

**Expected Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

#### 2. User Registration
```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "testuser@example.com",
    "username": "testuser",
    "password": "testpassword123",
    "full_name": "Test User",
    "accept_terms": true
  }'
```

#### 3. User Login
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "testuser@example.com",
    "password": "testpassword123"
  }'
```

### Wallet Testing

#### 1. Create Wallet
```bash
# Get user token first
TOKEN="your-user-token-here"

curl -X POST "http://localhost:8000/api/v1/wallet/create" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "chain": "ethereum"
  }'
```

#### 2. Get Wallet Balances
```bash
curl -X GET "http://localhost:8000/api/v1/wallet/balances" \
  -H "Authorization: Bearer $TOKEN"
```

#### 3. Create Ganache Wallet
```bash
curl -X POST "http://localhost:8000/api/v1/wallet/create" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "chain": "ganache"
  }'
```

### PIN Management Testing

#### 1. Set PIN
```bash
curl -X POST "http://localhost:8000/api/v1/pin/set" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "otp_verify": {
      "email": "testuser@example.com",
      "otp_code": null,
      "otp_type": "login"
    },
    "pin": "1234"
  }'
```

#### 2. Get PIN Status
```bash
curl -X GET "http://localhost:8000/api/v1/pin/status" \
  -H "Authorization: Bearer $TOKEN"
```

### Transaction Testing

#### 1. Send Transaction (with PIN)
```bash
curl -X POST "http://localhost:8000/api/v1/wallet/transaction/send" \
  -H "Authorization: Bearer $TOKEN" \
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

### Terms and Conditions Testing

#### 1. Get Current Terms
```bash
curl -X GET "http://localhost:8000/api/v1/terms/current" \
  -H "Authorization: Bearer $TOKEN"
```

#### 2. Agree to Terms
```bash
curl -X POST "http://localhost:8000/api/v1/terms/agree" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "terms_id": 1
  }'
```

### QR Code Testing

#### 1. Generate QR Code
```bash
curl -X GET "http://localhost:8000/api/v1/wallet/ethereum/qr?amount=0.001&memo=Test" \
  -H "Authorization: Bearer $TOKEN"
```

## 🧪 Ganache Testing

### 1. Start Ganache
```bash
# Using Docker
docker-compose up ganache -d

# Or locally
ganache-cli --port 8545 --network-id 1337 --accounts 10 --defaultBalanceEther 100
```

### 2. Test Ganache Connection
```bash
curl -X POST http://localhost:8545 \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "eth_blockNumber",
    "params": [],
    "id": 1
  }'
```

### 3. Complete Ganache Testing Flow

```bash
#!/bin/bash

# Test script for Ganache integration
echo "🧪 Testing Ganache Integration..."

# 1. Register user
echo "1. Registering user..."
REGISTER_RESPONSE=$(curl -s -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "ganache@test.com",
    "username": "ganacheuser",
    "password": "testpass123",
    "full_name": "Ganache Test User",
    "accept_terms": true
  }')

echo "Register response: $REGISTER_RESPONSE"

# 2. Login
echo "2. Logging in..."
LOGIN_RESPONSE=$(curl -s -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "ganache@test.com",
    "password": "testpass123"
  }')

TOKEN=$(echo $LOGIN_RESPONSE | jq -r '.access_token')
echo "Token: $TOKEN"

# 3. Set PIN
echo "3. Setting PIN..."
curl -s -X POST "http://localhost:8000/api/v1/pin/set" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "otp_verify": {
      "email": "ganache@test.com",
      "otp_code": null,
      "otp_type": "login"
    },
    "pin": "1234"
  }'

# 4. Create Ganache wallet
echo "4. Creating Ganache wallet..."
WALLET_RESPONSE=$(curl -s -X POST "http://localhost:8000/api/v1/wallet/create" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "chain": "ganache"
  }')

echo "Wallet response: $WALLET_RESPONSE"

# 5. Get balance
echo "5. Getting balance..."
BALANCE_RESPONSE=$(curl -s -X GET "http://localhost:8000/api/v1/wallet/balances" \
  -H "Authorization: Bearer $TOKEN")

echo "Balance response: $BALANCE_RESPONSE"

echo "✅ Ganache testing completed!"
```

## 🗄️ Database Testing

### 1. Database Connection Test
```bash
python -c "
from app.core.database import SessionLocal
from sqlalchemy import text

db = SessionLocal()
try:
    result = db.execute(text('SELECT version()')).fetchone()
    print(f'Database connected: {result[0]}')
except Exception as e:
    print(f'Database connection failed: {e}')
finally:
    db.close()
"
```

### 2. Table Verification
```bash
python -c "
from app.core.database import SessionLocal
from sqlalchemy import text

db = SessionLocal()
try:
    tables = db.execute(text(\"\"\"
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public'
        ORDER BY table_name;
    \"\"\")).fetchall()
    
    print('Database tables:')
    for table in tables:
        print(f'  - {table[0]}')
        
except Exception as e:
    print(f'Error: {e}')
finally:
    db.close()
"
```

### 3. Data Integrity Test
```bash
python -c "
from app.core.database import SessionLocal
from app.models.user import User
from app.models.role import Role
from app.models.terms import TermsAndConditions

db = SessionLocal()
try:
    # Check users
    user_count = db.query(User).count()
    print(f'Users: {user_count}')
    
    # Check roles
    roles = db.query(Role).all()
    print(f'Roles: {[role.name for role in roles]}')
    
    # Check terms
    terms = db.query(TermsAndConditions).filter(TermsAndConditions.is_current == True).first()
    if terms:
        print(f'Current terms: {terms.title} v{terms.version}')
    else:
        print('No current terms found')
        
except Exception as e:
    print(f'Error: {e}')
finally:
    db.close()
"
```

## 🔒 Security Testing

### 1. Authentication Tests
```bash
# Test invalid credentials
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "wrong@email.com",
    "password": "wrongpassword"
  }'

# Test missing token
curl -X GET "http://localhost:8000/api/v1/wallet/balances"

# Test invalid token
curl -X GET "http://localhost:8000/api/v1/wallet/balances" \
  -H "Authorization: Bearer invalid-token"
```

### 2. PIN Security Tests
```bash
# Test transaction without PIN
curl -X POST "http://localhost:8000/api/v1/wallet/transaction/send" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "transaction_data": {
      "chain": "ganache",
      "to_address": "0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6",
      "amount": 0.001
    },
    "pin_verify": {
      "pin": ""
    }
  }'

# Test wrong PIN
curl -X POST "http://localhost:8000/api/v1/wallet/transaction/send" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "transaction_data": {
      "chain": "ganache",
      "to_address": "0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6",
      "amount": 0.001
    },
    "pin_verify": {
      "pin": "9999"
    }
  }'
```

### 3. Rate Limiting Tests
```bash
# Test rate limiting by making many requests
for i in {1..100}; do
  curl -s -X GET "http://localhost:8000/api/v1/wallet/balances" \
    -H "Authorization: Bearer $TOKEN" > /dev/null
  echo "Request $i"
done
```

## ⚡ Performance Testing

### 1. Load Testing with Apache Bench
```bash
# Install Apache Bench
# Ubuntu/Debian: sudo apt-get install apache2-utils
# macOS: brew install httpd

# Test wallet balances endpoint
ab -n 100 -c 10 -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8000/api/v1/wallet/balances"

# Test user registration
ab -n 50 -c 5 -p register_data.json -T application/json \
  "http://localhost:8000/api/v1/auth/register"
```

### 2. Database Performance Test
```bash
python -c "
import time
from app.core.database import SessionLocal
from app.models.user import User
from app.models.wallet import Wallet

db = SessionLocal()
try:
    # Test user query performance
    start_time = time.time()
    users = db.query(User).all()
    user_time = time.time() - start_time
    print(f'User query time: {user_time:.4f}s for {len(users)} users')
    
    # Test wallet query performance
    start_time = time.time()
    wallets = db.query(Wallet).all()
    wallet_time = time.time() - start_time
    print(f'Wallet query time: {wallet_time:.4f}s for {len(wallets)} wallets')
    
except Exception as e:
    print(f'Error: {e}')
finally:
    db.close()
"
```

## 🔗 Integration Testing

### 1. Complete User Flow Test
```bash
#!/bin/bash

echo "🔄 Testing Complete User Flow..."

# 1. Register user
echo "1. Registering user..."
REGISTER_RESPONSE=$(curl -s -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "integration@test.com",
    "username": "integrationuser",
    "password": "testpass123",
    "full_name": "Integration Test User",
    "accept_terms": true
  }')

if [[ $REGISTER_RESPONSE == *"access_token"* ]]; then
    echo "✅ Registration successful"
else
    echo "❌ Registration failed: $REGISTER_RESPONSE"
    exit 1
fi

# 2. Extract token
TOKEN=$(echo $REGISTER_RESPONSE | jq -r '.access_token')

# 3. Set PIN
echo "2. Setting PIN..."
PIN_RESPONSE=$(curl -s -X POST "http://localhost:8000/api/v1/pin/set" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "otp_verify": {
      "email": "integration@test.com",
      "otp_code": null,
      "otp_type": "login"
    },
    "pin": "1234"
  }')

if [[ $PIN_RESPONSE == *"successfully"* ]]; then
    echo "✅ PIN set successfully"
else
    echo "❌ PIN setting failed: $PIN_RESPONSE"
fi

# 4. Create wallets
echo "3. Creating wallets..."
CHAINS=("ethereum" "ganache" "bsc")

for chain in "${CHAINS[@]}"; do
    WALLET_RESPONSE=$(curl -s -X POST "http://localhost:8000/api/v1/wallet/create" \
      -H "Authorization: Bearer $TOKEN" \
      -H "Content-Type: application/json" \
      -d "{\"chain\": \"$chain\"}")
    
    if [[ $WALLET_RESPONSE == *"address"* ]]; then
        echo "✅ $chain wallet created"
    else
        echo "❌ $chain wallet creation failed: $WALLET_RESPONSE"
    fi
done

# 5. Get balances
echo "4. Getting balances..."
BALANCE_RESPONSE=$(curl -s -X GET "http://localhost:8000/api/v1/wallet/balances" \
  -H "Authorization: Bearer $TOKEN")

if [[ $BALANCE_RESPONSE == *"chain"* ]]; then
    echo "✅ Balances retrieved successfully"
else
    echo "❌ Balance retrieval failed: $BALANCE_RESPONSE"
fi

# 6. Generate QR code
echo "5. Generating QR code..."
QR_RESPONSE=$(curl -s -X GET "http://localhost:8000/api/v1/wallet/ethereum/qr" \
  -H "Authorization: Bearer $TOKEN")

if [[ $QR_RESPONSE == *"qr_code"* ]]; then
    echo "✅ QR code generated successfully"
else
    echo "❌ QR code generation failed: $QR_RESPONSE"
fi

echo "🎉 Integration testing completed!"
```

### 2. Admin Flow Test
```bash
#!/bin/bash

echo "👑 Testing Admin Flow..."

# 1. Admin login
echo "1. Admin login..."
ADMIN_RESPONSE=$(curl -s -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@dari.com",
    "password": "admin123456"
  }')

if [[ $ADMIN_RESPONSE == *"access_token"* ]]; then
    echo "✅ Admin login successful"
    ADMIN_TOKEN=$(echo $ADMIN_RESPONSE | jq -r '.access_token')
else
    echo "❌ Admin login failed: $ADMIN_RESPONSE"
    exit 1
fi

# 2. Get all users
echo "2. Getting all users..."
USERS_RESPONSE=$(curl -s -X GET "http://localhost:8000/api/v1/admin/users" \
  -H "Authorization: Bearer $ADMIN_TOKEN")

if [[ $USERS_RESPONSE == *"email"* ]]; then
    echo "✅ Users retrieved successfully"
else
    echo "❌ Users retrieval failed: $USERS_RESPONSE"
fi

# 3. Get terms
echo "3. Getting terms..."
TERMS_RESPONSE=$(curl -s -X GET "http://localhost:8000/api/v1/terms" \
  -H "Authorization: Bearer $ADMIN_TOKEN")

if [[ $TERMS_RESPONSE == *"version"* ]]; then
    echo "✅ Terms retrieved successfully"
else
    echo "❌ Terms retrieval failed: $TERMS_RESPONSE"
fi

echo "🎉 Admin testing completed!"
```

## 📊 Test Results Reporting

### Create Test Report
```bash
#!/bin/bash

echo "📊 DARI Wallet Test Report" > test_report.txt
echo "Generated: $(date)" >> test_report.txt
echo "================================" >> test_report.txt

# Health check
echo "Health Check:" >> test_report.txt
curl -s http://localhost:8000/health >> test_report.txt
echo "" >> test_report.txt

# Database status
echo "Database Status:" >> test_report.txt
python -c "
from app.core.database import SessionLocal
from sqlalchemy import text
db = SessionLocal()
try:
    result = db.execute(text('SELECT COUNT(*) FROM users')).fetchone()
    print(f'Users: {result[0]}')
    result = db.execute(text('SELECT COUNT(*) FROM wallets')).fetchone()
    print(f'Wallets: {result[0]}')
    result = db.execute(text('SELECT COUNT(*) FROM transactions')).fetchone()
    print(f'Transactions: {result[0]}')
except Exception as e:
    print(f'Error: {e}')
finally:
    db.close()
" >> test_report.txt

echo "Test report generated: test_report.txt"
```

## 🚨 Troubleshooting

### Common Issues

#### 1. Database Connection Issues
```bash
# Check if PostgreSQL is running
sudo systemctl status postgresql

# Check database connection
psql -U dari_user -h localhost -d dari_wallet -c "SELECT version();"
```

#### 2. Ganache Connection Issues
```bash
# Check if Ganache is running
curl -X POST http://localhost:8545 \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"eth_blockNumber","params":[],"id":1}'
```

#### 3. CORS Issues
```bash
# Test CORS preflight
curl -H "Origin: https://mybbi.in" \
  -H "Access-Control-Request-Method: POST" \
  -H "Access-Control-Request-Headers: Content-Type" \
  -X OPTIONS http://localhost:8000/api/v1/auth/login
```

#### 4. Rate Limiting Issues
```bash
# Check rate limit headers
curl -I -X GET "http://localhost:8000/api/v1/wallet/balances" \
  -H "Authorization: Bearer $TOKEN"
```

## 📞 Support

For testing issues:
- **Email**: admin@dari.com
- **Documentation**: http://localhost:8000/docs
- **Logs**: Check application logs for detailed error messages

---

**🎯 Testing Checklist:**
- [ ] Health endpoint responds
- [ ] Admin login works
- [ ] User registration works
- [ ] PIN management works
- [ ] Wallet creation works
- [ ] Balance retrieval works
- [ ] QR code generation works
- [ ] Ganache integration works
- [ ] Terms and conditions work
- [ ] Security features work
- [ ] Performance is acceptable 
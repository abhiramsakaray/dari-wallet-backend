# Deployment Checklist for Security Features

## ✅ Pre-Deployment Verification

### 1. Database Migration
- [ ] Run the migration script: `python scripts/migrate_pin_and_logging.py`
- [ ] Verify all new tables and columns are created
- [ ] Check that indexes are created for performance

### 2. Code Verification
- [ ] All new models are properly imported in `app/models/__init__.py`
- [ ] PIN router is registered in `app/main.py` with correct prefix
- [ ] All service imports are working correctly
- [ ] All schema imports are working correctly

### 3. File Structure Verification
- [ ] `app/models/login_log.py` - Login logging model
- [ ] `app/services/pin.py` - PIN management service
- [ ] `app/services/login_logger.py` - Login logging service
- [ ] `app/services/analytics.py` - Analytics service
- [ ] `app/services/transaction_history.py` - Transaction history service
- [ ] `app/routes/pin.py` - PIN management routes
- [ ] `app/schemas/pin.py` - PIN schemas
- [ ] `scripts/migrate_pin_and_logging.py` - Database migration script
- [ ] `SECURITY_FEATURES.md` - Documentation
- [ ] `test_security_features.py` - Test script

## 🔧 Configuration Setup

### 1. Environment Variables
Ensure these are set in your environment:
```bash
# Database
DATABASE_URL=your_database_url

# Security
SECRET_KEY=your_secret_key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# OTP Configuration
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email
SMTP_PASSWORD=your_password

# CORS
ALLOWED_ORIGINS=["http://localhost:3000", "https://yourdomain.com"]
```

### 2. PIN Configuration
Default settings (can be customized):
- Max failed attempts: 10
- Block duration: 24 hours
- PIN hash algorithm: Same as password hashing

### 3. Fraud Detection Thresholds
Default settings (can be customized):
- High transaction amount: $10,000
- Rapid transactions: 3+ in 5 minutes
- Multiple locations: 3+ different locations
- Multiple IPs: 5+ different IP addresses

## 🧪 Testing

### 1. Run Test Script
```bash
python test_security_features.py
```
Expected output: All 5 tests should pass

### 2. Manual API Testing
Test these endpoints manually:

#### PIN Management
```bash
# Set PIN (requires OTP first)
curl -X POST "http://localhost:8000/api/v1/pin/set" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"otp_verify": {"email": "user@example.com", "otp_code": "123456", "otp_type": "login"}, "pin": "1234"}'

# Get PIN status
curl -X GET "http://localhost:8000/api/v1/pin/status" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### Transfer with PIN
```bash
# Send transaction with PIN verification
curl -X POST "http://localhost:8000/api/v1/wallet/transaction/send" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"transaction_data": {"chain": "ethereum", "to_address": "0x...", "amount": "1.0"}, "pin_verify": {"pin": "1234"}}'
```

#### Admin Login with OTP
```bash
# Login (will return OTP requirement for admin)
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@example.com", "password": "password123"}'

# Verify OTP for admin login
curl -X POST "http://localhost:8000/api/v1/auth/login/verify-otp" \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@example.com", "otp_code": "123456"}'
```

#### Analytics Endpoints
```bash
# Get frequent transfers
curl -X GET "http://localhost:8000/api/v1/wallet/analytics/frequent-transfers" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Get fraud indicators
curl -X GET "http://localhost:8000/api/v1/wallet/analytics/fraud-indicators" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Get comprehensive transaction history
curl -X GET "http://localhost:8000/api/v1/wallet/transaction/history/comprehensive" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## 🚀 Deployment Steps

### 1. Database Setup
```bash
# Run migration
python scripts/migrate_pin_and_logging.py

# Verify tables exist
# Check: users table has hashed_pin, pin_failed_attempts, pin_blocked_until columns
# Check: transactions table has device_info, ip_address, location, pin_attempts columns
# Check: login_logs table exists
```

### 2. Application Deployment
```bash
# Install dependencies
pip install -r requirements.txt

# Run tests
python test_security_features.py

# Start application
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 3. Post-Deployment Verification

#### Check API Documentation
- Visit `http://localhost:8000/docs`
- Verify all new endpoints are documented:
  - `/api/v1/pin/*` endpoints
  - `/api/v1/wallet/analytics/*` endpoints
  - `/api/v1/wallet/transaction/history/comprehensive`
  - `/api/v1/auth/login/verify-otp`
  - `/api/v1/admin/login-statistics`
  - `/api/v1/admin/suspicious-activity`
  - `/api/v1/admin/login-logs`

#### Test Core Functionality
1. **User Registration/Login**: Verify normal user login works
2. **Admin Login**: Verify admin login requires OTP
3. **PIN Management**: Test PIN set/reset with OTP
4. **Transfer Security**: Test transfer with PIN verification
5. **Analytics**: Test analytics endpoints return data
6. **Admin Controls**: Test admin unblock functionality

## 🔒 Security Verification

### 1. PIN Security
- [ ] PINs are properly hashed
- [ ] Failed attempts are tracked correctly
- [ ] Blocking works after 10 failed attempts
- [ ] Admin can unblock users

### 2. OTP Security
- [ ] Admin logins require OTP
- [ ] OTP verification works correctly
- [ ] Failed OTP attempts are logged

### 3. Logging Security
- [ ] All login attempts are logged
- [ ] Device info, IP, and location are captured
- [ ] Failed attempts are logged with reasons
- [ ] Admin login attempts are flagged

### 4. Transaction Security
- [ ] All transfers require PIN verification
- [ ] Device info, IP, and location are logged
- [ ] PIN attempts are tracked per transaction
- [ ] Fraud indicators are calculated

## 📊 Monitoring Setup

### 1. Log Monitoring
Set up monitoring for:
- Failed PIN attempts
- Failed login attempts
- Admin login attempts
- High-risk fraud scores
- Suspicious activity patterns

### 2. Alert Configuration
Configure alerts for:
- Multiple failed PIN attempts (>5 in 1 hour)
- Logins from multiple locations (>3 in 24 hours)
- High-risk fraud scores (>70)
- Admin login attempts from unusual locations
- Rapid successive transactions (>5 in 10 minutes)

### 3. Dashboard Metrics
Monitor these key metrics:
- Login success/failure rates
- PIN verification success rates
- Fraud risk score distribution
- Peak usage times
- Most frequent transfer addresses
- Suspicious activity patterns

## 🚨 Troubleshooting

### Common Issues

1. **Migration Errors**
   - Check database permissions
   - Verify DATABASE_URL is correct
   - Ensure database exists

2. **Import Errors**
   - Check all `__init__.py` files have proper imports
   - Verify file paths are correct
   - Check Python path includes project root

3. **OTP Issues**
   - Verify SMTP configuration
   - Check OTP service is working
   - Test OTP generation manually

4. **PIN Issues**
   - Check PIN service is imported correctly
   - Verify PIN hashing is working
   - Test PIN verification manually

5. **Analytics Issues**
   - Check database queries are working
   - Verify transaction data exists
   - Test analytics endpoints manually

### Debug Commands
```bash
# Check database tables
python -c "from app.core.database import engine; from app.models import *; Base.metadata.create_all(engine); print('Tables created successfully')"

# Test PIN service
python -c "from app.services.pin import PINService; print('PIN service imported successfully')"

# Test login logger
python -c "from app.services.login_logger import LoginLogger; print('Login logger imported successfully')"

# Test analytics service
python -c "from app.services.analytics import AnalyticsService; print('Analytics service imported successfully')"
```

## ✅ Final Checklist

- [ ] Database migration completed successfully
- [ ] All tests pass (`python test_security_features.py`)
- [ ] All endpoints are accessible and working
- [ ] PIN verification works for transfers
- [ ] Admin login requires OTP
- [ ] Login logging captures all required data
- [ ] Analytics endpoints return data
- [ ] Admin controls work correctly
- [ ] Documentation is complete (`SECURITY_FEATURES.md`)
- [ ] Monitoring and alerts are configured
- [ ] Security best practices are implemented

## 🎉 Deployment Complete

Once all items are checked, your security features are ready for production use!

**Key Features Deployed:**
- ✅ PIN verification before transfers
- ✅ OTP verification for admin login
- ✅ Comprehensive login logging
- ✅ Transaction history with fraud analysis
- ✅ Peak usage monitoring
- ✅ Frequent transfer tracking
- ✅ Admin controls and monitoring 
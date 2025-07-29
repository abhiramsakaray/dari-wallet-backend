# OTP Verification System

## 🔐 Overview

The DARI Wallet backend now includes a comprehensive OTP (One-Time Password) verification system for enhanced login security. The system supports both email and SMS OTP delivery and is fully configurable by administrators.

## 🚀 Key Features

### **OTP Types Supported**
1. **Login OTP** - For enhanced login security
2. **Email Verification OTP** - For email verification
3. **Password Reset OTP** - For password reset functionality
4. **Two-Factor OTP** - For 2FA implementation

### **Delivery Channels**
1. **Email OTP** - Sent via SMTP
2. **SMS OTP** - Sent via SMS API (optional)

### **Security Features**
- **Configurable OTP Length** (4-8 digits)
- **Expiry Time** (1-60 minutes)
- **Maximum Attempts** (1-10 attempts)
- **Cooldown Period** (1-60 minutes between requests)
- **Admin Control** - Only admins can enable/disable OTP
- **Audit Logging** - All OTP activities are logged

## ⚙️ Configuration

### **Default Settings (All Disabled)**
By default, all OTP configurations are **DISABLED** for security. Admins must explicitly enable them.

```python
# Default OTP Configurations
{
    "login_email_otp": {
        "is_enabled": False,
        "otp_length": 6,
        "expiry_minutes": 10,
        "max_attempts": 3,
        "cooldown_minutes": 1
    },
    "login_sms_otp": {
        "is_enabled": False,
        "otp_length": 6,
        "expiry_minutes": 10,
        "max_attempts": 3,
        "cooldown_minutes": 1
    }
}
```

### **Environment Variables**
```bash
# Email Configuration (Required for Email OTP)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# SMS Configuration (Optional for SMS OTP)
SMS_API_KEY=your-sms-api-key
SMS_API_URL=https://api.sms-service.com/send
```

## 🔧 Setup Instructions

### **1. Initialize OTP Configurations**
```bash
python scripts/init_otp_configs.py
```

### **2. Enable OTP (Admin Only)**
```bash
# Enable Email OTP for Login
curl -X PUT "http://localhost:8000/api/v1/otp/admin/configs/1" \
  -H "Authorization: Bearer ADMIN_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"is_enabled": true}'

# Enable SMS OTP for Login (if SMS provider is configured)
curl -X PUT "http://localhost:8000/api/v1/otp/admin/configs/2" \
  -H "Authorization: Bearer ADMIN_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"is_enabled": true}'
```

## 📱 User Flow

### **Login with OTP Enabled**

1. **User attempts login**
   ```bash
   curl -X POST "http://localhost:8000/api/v1/auth/login" \
     -H "Content-Type: application/json" \
     -d '{
       "email": "user@example.com",
       "password": "password123"
     }'
   ```

2. **System checks OTP status**
   ```json
   {
     "message": "OTP verification required",
     "requires_otp": true,
     "email_otp_enabled": true,
     "sms_otp_enabled": false
   }
   ```

3. **User requests OTP**
   ```bash
   curl -X POST "http://localhost:8000/api/v1/otp/request" \
     -H "Content-Type: application/json" \
     -d '{
       "email": "user@example.com",
       "otp_type": "login",
       "channel": "email"
     }'
   ```

4. **User receives OTP via email/SMS**
   ```
   Your DARI Wallet Login OTP is: 123456
   This OTP will expire in 10 minutes.
   ```

5. **User verifies OTP**
   ```bash
   curl -X POST "http://localhost:8000/api/v1/otp/verify" \
     -H "Content-Type: application/json" \
     -d '{
       "email": "user@example.com",
       "otp_code": "123456",
       "otp_type": "login"
     }'
   ```

6. **System returns access tokens**
   ```json
   {
     "message": "OTP verified successfully",
     "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
     "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
     "token_type": "bearer",
     "expires_in": 1800
   }
   ```

## 🔧 Admin Management

### **View OTP Configurations**
```bash
curl -X GET "http://localhost:8000/api/v1/otp/admin/configs" \
  -H "Authorization: Bearer ADMIN_ACCESS_TOKEN"
```

### **Update OTP Configuration**
```bash
curl -X PUT "http://localhost:8000/api/v1/otp/admin/configs/1" \
  -H "Authorization: Bearer ADMIN_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "is_enabled": true,
    "otp_length": 6,
    "expiry_minutes": 10,
    "max_attempts": 3,
    "cooldown_minutes": 1
  }'
```

### **Get OTP Statistics**
```bash
curl -X GET "http://localhost:8000/api/v1/otp/admin/stats" \
  -H "Authorization: Bearer ADMIN_ACCESS_TOKEN"
```

### **Cleanup Expired OTPs**
```bash
curl -X POST "http://localhost:8000/api/v1/otp/admin/cleanup" \
  -H "Authorization: Bearer ADMIN_ACCESS_TOKEN"
```

## 📊 API Endpoints

### **User Endpoints**
- `POST /api/v1/otp/request` - Request OTP
- `POST /api/v1/otp/verify` - Verify OTP
- `GET /api/v1/otp/status` - Check OTP status

### **Admin Endpoints**
- `GET /api/v1/otp/admin/configs` - Get all configurations
- `POST /api/v1/otp/admin/configs` - Create configuration
- `PUT /api/v1/otp/admin/configs/{id}` - Update configuration
- `DELETE /api/v1/otp/admin/configs/{id}` - Delete configuration
- `GET /api/v1/otp/admin/stats` - Get OTP statistics
- `POST /api/v1/otp/admin/cleanup` - Cleanup expired OTPs

## 🔒 Security Considerations

### **OTP Security Features**
1. **Rate Limiting** - Cooldown period between OTP requests
2. **Expiry Time** - OTPs expire after configurable time
3. **Maximum Attempts** - Limit failed verification attempts
4. **Audit Logging** - All OTP activities are tracked
5. **Admin Control** - Only admins can enable/disable OTP

### **Best Practices**
1. **Start Disabled** - All OTP configurations are disabled by default
2. **Test in Development** - Test OTP functionality before enabling in production
3. **Monitor Usage** - Use admin statistics to monitor OTP usage
4. **Regular Cleanup** - Run cleanup to remove expired OTPs
5. **Secure Configuration** - Use environment variables for sensitive data

## 🚨 Error Handling

### **Common Error Responses**
```json
{
  "detail": "OTP is not enabled for login via email"
}
```
```json
{
  "detail": "Please wait 1 minutes before requesting another OTP"
}
```
```json
{
  "detail": "Invalid OTP code"
}
```
```json
{
  "detail": "OTP has expired"
}
```
```json
{
  "detail": "Maximum OTP attempts exceeded"
}
```

## 🔄 Integration with Existing Features

### **Login Integration**
- OTP verification is integrated into the login flow
- If OTP is enabled, users must verify OTP after password authentication
- If OTP is disabled, normal login flow continues

### **Notification Integration**
- OTP requests and verifications are logged
- Failed OTP attempts can trigger security notifications
- Successful OTP verification can trigger login notifications

### **Admin Integration**
- OTP management is integrated into admin dashboard
- OTP statistics are available in admin panel
- OTP configurations can be managed through admin API

## 📝 Database Schema

### **OTP Table**
```sql
CREATE TABLE otps (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    otp_code VARCHAR(6) NOT NULL,
    otp_type VARCHAR(20) NOT NULL,
    channel VARCHAR(10) NOT NULL,
    status VARCHAR(10) DEFAULT 'pending',
    attempts INTEGER DEFAULT 0,
    max_attempts INTEGER DEFAULT 3,
    expires_at TIMESTAMP NOT NULL,
    verified_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### **OTP Config Table**
```sql
CREATE TABLE otp_configs (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,
    is_enabled BOOLEAN DEFAULT FALSE,
    otp_type VARCHAR(20) NOT NULL,
    channel VARCHAR(10) NOT NULL,
    otp_length INTEGER DEFAULT 6,
    expiry_minutes INTEGER DEFAULT 10,
    max_attempts INTEGER DEFAULT 3,
    cooldown_minutes INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 🎯 Implementation Notes

### **Current Status**
- ✅ OTP system fully implemented
- ✅ Email OTP delivery working
- ✅ SMS OTP delivery ready (requires SMS provider)
- ✅ Admin management interface complete
- ✅ Integration with login flow complete
- ⚠️ **All OTP configurations disabled by default**

### **Next Steps**
1. **Test OTP functionality** in development environment
2. **Configure email settings** in production
3. **Enable OTP** when ready for production
4. **Configure SMS provider** (optional)
5. **Monitor OTP usage** through admin panel

### **SMS Provider Integration**
The SMS OTP feature is ready but requires:
1. SMS API provider account (Twilio, AWS SNS, etc.)
2. SMS API credentials in environment variables
3. SMS API endpoint configuration

Once SMS provider is configured, SMS OTP can be enabled through admin panel. 
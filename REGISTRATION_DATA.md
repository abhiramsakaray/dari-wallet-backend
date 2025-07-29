# User Registration Data & Notification System

## 📝 User Registration Data

When a user registers for the DARI wallet, the following data is collected:

### Required Fields
- **Email**: User's email address (unique, used for login)
- **Username**: Unique username for the platform
- **Password**: Secure password (hashed before storage)
- **Default Currency ID**: User's preferred default currency (optional)

### Optional Fields
- **Full Name**: User's full name
- **Phone Number**: User's phone number (for SMS notifications)

### System-Generated Fields
- **User ID**: Unique identifier
- **Role ID**: Default role assignment (usually "user")
- **Encryption Key**: User-specific encryption key for wallet security
- **Two-Factor Secret**: For 2FA setup (if enabled)
- **Created At**: Registration timestamp
- **Updated At**: Last update timestamp
- **Is Active**: Account status (default: true)
- **Is Verified**: Email verification status (default: false)
- **Last Login**: Last login timestamp

### Example Registration Request
```json
{
  "email": "user@example.com",
  "username": "alice",
  "password": "securepassword123",
  "full_name": "Alice Johnson",
  "phone": "+1234567890",
  "default_currency_id": 1
}
```

### Example Registration Response
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

## 🔔 Notification System Features

### Notification Types
1. **Login Notifications**: Sent when user logs in
2. **Transfer Sent**: When user sends funds
3. **Transfer Received**: When user receives funds
4. **Promotion Messages**: Marketing and promotional content
5. **Security Alerts**: Security-related notifications
6. **System Updates**: Platform updates and maintenance
7. **Wallet Created**: When new wallet is created
8. **Alias Created**: When username alias is set
9. **Verification**: Email verification links

### Notification Channels
1. **App Notifications**: In-app notifications
2. **Email Notifications**: Email delivery
3. **SMS Notifications**: Text message delivery

### User Notification Settings
Users can control their notification preferences:

```json
{
  "email_enabled": true,
  "sms_enabled": true,
  "app_enabled": true,
  "login_notifications": true,
  "transfer_notifications": true,
  "promotion_notifications": true,
  "security_notifications": true,
  "system_notifications": true
}
```

### Admin Notification Management

#### Notification Templates
Admins can create and manage notification templates:

```json
{
  "name": "transfer_sent_email",
  "type": "transfer_sent",
  "channel": "email",
  "title_template": "Transfer Sent Successfully",
  "message_template": "Your transfer of {amount} {currency} has been sent successfully. Transaction ID: {tx_id}"
}
```

#### Send Notifications
Admins can send notifications to specific users or all users:

```json
{
  "user_id": 1,
  "notification_type": "promotion",
  "title": "New Feature Available",
  "message": "Check out our new wallet features!"
}
```

### Default Currencies Available
The system comes with these default currencies:

#### Fiat Currencies
- USD (US Dollar) - $
- EUR (Euro) - €
- GBP (British Pound) - £
- JPY (Japanese Yen) - ¥

#### Cryptocurrencies
- BTC (Bitcoin) - ₿
- ETH (Ethereum) - Ξ
- BNB (Binance Coin) - BNB
- SOL (Solana) - ◎
- XRP (Ripple) - XRP
- TRX (TRON) - TRX

### API Endpoints

#### Currency Management
- `GET /api/v1/currencies` - Get all currencies
- `GET /api/v1/currencies/{id}` - Get specific currency
- `POST /api/v1/currencies` - Create currency (admin)
- `PUT /api/v1/currencies/{id}` - Update currency (admin)
- `DELETE /api/v1/currencies/{id}` - Delete currency (admin)

#### Notification Management
- `GET /api/v1/notifications` - Get user notifications
- `GET /api/v1/notifications/{id}` - Get specific notification
- `PUT /api/v1/notifications/{id}/read` - Mark as read
- `PUT /api/v1/notifications/read-all` - Mark all as read
- `GET /api/v1/notifications/settings` - Get notification settings
- `PUT /api/v1/notifications/settings` - Update notification settings

#### Admin Notification Management
- `GET /api/v1/notifications/admin/templates` - Get templates
- `POST /api/v1/notifications/admin/templates` - Create template
- `PUT /api/v1/notifications/admin/templates/{id}` - Update template
- `DELETE /api/v1/notifications/admin/templates/{id}` - Delete template
- `POST /api/v1/notifications/admin/send` - Send to specific user
- `POST /api/v1/notifications/admin/send-bulk` - Send to all users

### Configuration

#### Email Configuration
```bash
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

#### SMS Configuration
```bash
SMS_API_KEY=your-sms-api-key
SMS_API_URL=https://api.sms-service.com/send
```

### Security Features
- All notifications are logged for audit purposes
- Failed notifications are tracked with error messages
- User can control which types of notifications they receive
- Admins can only send notifications to users who have opted in
- Sensitive information is not included in SMS notifications
- Email notifications include proper headers and formatting

### Integration Points
- **Login Integration**: Automatic login notifications
- **Transfer Integration**: Automatic transfer notifications
- **Wallet Creation**: Notifications when wallets are created
- **Alias Creation**: Notifications when aliases are set
- **Admin Dashboard**: Interface for managing notifications
- **User Settings**: Interface for controlling notification preferences 
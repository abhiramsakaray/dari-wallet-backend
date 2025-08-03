# DARI Wallet Production Database Migration Guide

## 📋 Overview

This guide covers the complete process of setting up the DARI Wallet backend database for production deployment, including all necessary migrations, initial data setup, and verification steps.

## 🗄️ Database Setup

### 1. PostgreSQL Database Creation

```sql
-- Create production database
CREATE DATABASE dari_wallet_prod;

-- Create production user
CREATE USER dari_wallet_user WITH PASSWORD 'your-secure-password';

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE dari_wallet_prod TO dari_wallet_user;
GRANT CONNECT ON DATABASE dari_wallet_prod TO dari_wallet_user;

-- Connect to the database
\c dari_wallet_prod

-- Grant schema privileges
GRANT ALL ON SCHEMA public TO dari_wallet_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO dari_wallet_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO dari_wallet_user;
```

### 2. Environment Configuration

```bash
# Production .env file
DATABASE_URL=postgresql://dari_wallet_user:your-secure-password@localhost:5432/dari_wallet_prod
ASYNC_DATABASE_URL=postgresql+asyncpg://dari_wallet_user:your-secure-password@localhost:5432/dari_wallet_prod
ENVIRONMENT=production
DEBUG=false
SECRET_KEY=your-super-secure-production-secret-key-here
```

## 🚀 Migration Process

### Step 1: Create Database Tables

```bash
# Run the table creation script
python scripts/create_tables.py
```

**Expected Output:**
```
Creating DARI Wallet Backend database tables...
Creating database tables...
All tables created successfully!
```

### Step 2: Initialize Core Data

```bash
# Initialize roles and admin users
python scripts/init_db.py

# Initialize currencies
python scripts/init_currencies.py

# Initialize notification templates
python scripts/init_notifications.py

# Initialize OTP configurations
python scripts/init_otp_configs.py

# Initialize terms and conditions
python scripts/init_terms.py
```

### Step 3: Verify Database Setup

```bash
# Verify all tables exist
python -c "
from app.core.database import SessionLocal
from sqlalchemy import text

db = SessionLocal()
try:
    # Check if tables exist
    tables = db.execute(text(\"\"\"
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public'
        ORDER BY table_name;
    \"\"\")).fetchall()
    
    print('Created tables:')
    for table in tables:
        print(f'  - {table[0]}')
        
    # Check admin user
    admin = db.execute(text(\"\"\"
        SELECT email, username, is_active 
        FROM users 
        WHERE email = 'admin@dari.com';
    \"\"\")).fetchone()
    
    if admin:
        print(f'\\nAdmin user: {admin[0]} ({admin[1]}) - Active: {admin[2]}')
    else:
        print('\\n❌ Admin user not found!')
        
    # Check terms
    terms = db.execute(text(\"\"\"
        SELECT version, title, status 
        FROM terms_and_conditions 
        WHERE is_current = true;
    \"\"\")).fetchone()
    
    if terms:
        print(f'\\nCurrent terms: {terms[1]} v{terms[0]} - Status: {terms[2]}')
    else:
        print('\\n❌ Terms and conditions not found!')
        
except Exception as e:
    print(f'Error: {e}')
finally:
    db.close()
"
```

## 📊 Database Schema Verification

### Expected Tables

After running all migration scripts, you should have these tables:

1. **users** - User accounts and authentication
2. **roles** - User roles (admin, user, etc.)
3. **wallets** - User cryptocurrency wallets
4. **transactions** - Transaction history
5. **tokens** - Supported cryptocurrencies
6. **token_balances** - User token balances
7. **aliases** - Username resolution
8. **logs** - System logs
9. **currencies** - Supported fiat currencies
10. **notifications** - User notifications
11. **notification_templates** - Notification templates
12. **notification_settings** - User notification preferences
13. **otps** - OTP records
14. **otp_configs** - OTP configuration
15. **login_logs** - Login attempt logs
16. **terms_and_conditions** - Terms and conditions
17. **user_terms_agreements** - User agreements to terms
18. **qr_codes** - Stored QR code images

### Verification Script

```bash
# Create verification script
cat > verify_migration.py << 'EOF'
#!/usr/bin/env python3
"""
Database migration verification script
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import SessionLocal
from sqlalchemy import text

def verify_migration():
    """Verify all database tables and initial data"""
    db = SessionLocal()
    
    try:
        print("🔍 Verifying DARI Wallet Database Migration...")
        print("=" * 50)
        
        # Check tables
        tables_query = """
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """
        tables = db.execute(text(tables_query)).fetchall()
        
        expected_tables = [
            'users', 'roles', 'wallets', 'transactions', 'tokens',
            'token_balances', 'aliases', 'logs', 'currencies',
            'notifications', 'notification_templates', 'notification_settings',
            'otps', 'otp_configs', 'login_logs', 'terms_and_conditions',
            'user_terms_agreements', 'qr_codes'
        ]
        
        print(f"📋 Found {len(tables)} tables:")
        found_tables = [table[0] for table in tables]
        
        for table in expected_tables:
            if table in found_tables:
                print(f"  ✅ {table}")
            else:
                print(f"  ❌ {table} - MISSING!")
        
        # Check admin user
        admin_query = """
            SELECT email, username, is_active 
            FROM users 
            WHERE email = 'admin@dari.com';
        """
        admin = db.execute(text(admin_query)).fetchone()
        
        if admin:
            print(f"\n👤 Admin user: {admin[0]} ({admin[1]}) - Active: {admin[2]}")
        else:
            print("\n❌ Admin user not found!")
        
        # Check roles
        roles_query = "SELECT name FROM roles ORDER BY name;"
        roles = db.execute(text(roles_query)).fetchall()
        
        print(f"\n🔐 Roles ({len(roles)}):")
        for role in roles:
            print(f"  - {role[0]}")
        
        # Check currencies
        currencies_query = "SELECT code, name FROM currencies ORDER BY code;"
        currencies = db.execute(text(currencies_query)).fetchall()
        
        print(f"\n💰 Currencies ({len(currencies)}):")
        for currency in currencies:
            print(f"  - {currency[0]} ({currency[1]})")
        
        # Check terms
        terms_query = """
            SELECT version, title, status 
            FROM terms_and_conditions 
            WHERE is_current = true;
        """
        terms = db.execute(text(terms_query)).fetchone()
        
        if terms:
            print(f"\n📜 Current terms: {terms[1]} v{terms[0]} - Status: {terms[2]}")
        else:
            print("\n❌ Terms and conditions not found!")
        
        # Check OTP configs
        otp_configs_query = "SELECT name, is_enabled FROM otp_configs;"
        otp_configs = db.execute(text(otp_configs_query)).fetchall()
        
        print(f"\n🔐 OTP Configurations ({len(otp_configs)}):")
        for config in otp_configs:
            status = "✅ Enabled" if config[1] else "❌ Disabled"
            print(f"  - {config[0]}: {status}")
        
        print("\n" + "=" * 50)
        print("✅ Migration verification completed!")
        
    except Exception as e:
        print(f"❌ Error during verification: {e}")
        return False
    finally:
        db.close()
    
    return True

if __name__ == "__main__":
    verify_migration()
EOF

# Run verification
python verify_migration.py
```

## 🔧 Production Configuration

### 1. Update Environment Variables

```bash
# Production .env
ENVIRONMENT=production
DEBUG=false
DATABASE_URL=postgresql://dari_wallet_user:your-secure-password@localhost:5432/dari_wallet_prod
ASYNC_DATABASE_URL=postgresql+asyncpg://dari_wallet_user:your-secure-password@localhost:5432/dari_wallet_prod
SECRET_KEY=your-super-secure-production-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Production CORS
ALLOWED_ORIGINS=["https://mybbi.in", "https://dariwallet.com", "https://www.mybbi.in", "https://www.dariwallet.com"]

# Production API Keys
COINGECKO_API_KEY=your-production-coingecko-api-key
ETHERSCAN_API_KEY=your-production-etherscan-api-key
BSCSCAN_API_KEY=your-production-bscscan-api-key

# Production Email/SMS
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-production-email@gmail.com
SMTP_PASSWORD=your-production-app-password

# Production Rate Limiting
RATE_LIMIT_PER_MINUTE=60
RATE_LIMIT_PER_HOUR=1000

# Production Logging
LOG_LEVEL=INFO
LOG_FILE=/var/log/dari_wallet/dari_wallet.log
```

### 2. Database Backup Strategy

```bash
# Create backup script
cat > backup_database.sh << 'EOF'
#!/bin/bash

# Database backup script
BACKUP_DIR="/var/backups/dari_wallet"
DATE=$(date +%Y%m%d_%H%M%S)
DB_NAME="dari_wallet_prod"
DB_USER="dari_wallet_user"

# Create backup directory
mkdir -p $BACKUP_DIR

# Create backup
pg_dump -U $DB_USER -h localhost $DB_NAME > $BACKUP_DIR/dari_wallet_$DATE.sql

# Compress backup
gzip $BACKUP_DIR/dari_wallet_$DATE.sql

# Keep only last 7 days of backups
find $BACKUP_DIR -name "dari_wallet_*.sql.gz" -mtime +7 -delete

echo "Backup created: $BACKUP_DIR/dari_wallet_$DATE.sql.gz"
EOF

chmod +x backup_database.sh

# Add to crontab for daily backups
echo "0 2 * * * /path/to/backup_database.sh" | crontab -
```

### 3. Database Performance Optimization

```sql
-- Create indexes for better performance
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_wallets_user_id ON wallets(user_id);
CREATE INDEX idx_wallets_chain ON wallets(chain);
CREATE INDEX idx_transactions_user_id ON transactions(user_id);
CREATE INDEX idx_transactions_created_at ON transactions(created_at);
CREATE INDEX idx_aliases_username ON aliases(username);
CREATE INDEX idx_otps_email ON otps(email);
CREATE INDEX idx_otps_created_at ON otps(created_at);
CREATE INDEX idx_login_logs_email ON login_logs(email);
CREATE INDEX idx_login_logs_created_at ON login_logs(created_at);

-- Analyze tables for query optimization
ANALYZE users;
ANALYZE wallets;
ANALYZE transactions;
ANALYZE aliases;
ANALYZE otps;
ANALYZE login_logs;
```

## 🚀 Deployment Checklist

### Pre-Deployment
- [ ] Database created and configured
- [ ] All migration scripts run successfully
- [ ] Verification script passes
- [ ] Environment variables configured
- [ ] SSL certificates installed
- [ ] Firewall rules configured
- [ ] Backup strategy implemented

### Post-Deployment
- [ ] Admin login works
- [ ] User registration works
- [ ] Wallet creation works
- [ ] Transaction sending works
- [ ] API documentation accessible
- [ ] Monitoring and logging working
- [ ] Backup script tested

## 🔍 Troubleshooting

### Common Issues

#### 1. Database Connection Failed
```bash
# Check database connection
psql -U dari_wallet_user -h localhost -d dari_wallet_prod -c "SELECT version();"
```

#### 2. Migration Scripts Fail
```bash
# Check database permissions
psql -U dari_wallet_user -h localhost -d dari_wallet_prod -c "\du"
```

#### 3. Admin User Not Created
```bash
# Manually create admin user
python -c "
from app.core.database import SessionLocal
from app.models.user import User
from app.models.role import Role
from app.core.security import get_password_hash

db = SessionLocal()
try:
    # Get admin role
    admin_role = db.query(Role).filter(Role.name == 'admin').first()
    
    # Create admin user
    admin_user = User(
        email='admin@dari.com',
        username='superadmin',
        hashed_password=get_password_hash('admin123456'),
        full_name='Super Administrator',
        is_active=True,
        is_verified=True,
        role_id=admin_role.id
    )
    
    db.add(admin_user)
    db.commit()
    print('Admin user created successfully!')
except Exception as e:
    print(f'Error: {e}')
    db.rollback()
finally:
    db.close()
"
```

## 📞 Support

For migration issues:
- **Email**: admin@dari.com
- **Documentation**: /docs
- **Logs**: Check application logs for detailed error messages

---

**⚠️ Important**: Always backup your database before running migrations in production! 
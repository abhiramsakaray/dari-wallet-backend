from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from app.models.transaction import Transaction
from app.models.user import User
from app.models.login_log import LoginLog


class TransactionHistoryService:
    def __init__(self, db: Session):
        self.db = db

    def get_comprehensive_transaction_history(
        self, 
        user_id: int, 
        chain: Optional[str] = None,
        limit: int = 50, 
        offset: int = 0
    ) -> List[Dict]:
        """Get comprehensive transaction history with fraud analysis data"""
        query = self.db.query(Transaction).filter(Transaction.user_id == user_id)
        
        if chain:
            query = query.filter(Transaction.chain == chain)
        
        transactions = query.order_by(Transaction.created_at.desc()).offset(offset).limit(limit).all()
        
        history = []
        for tx in transactions:
            # Get related login logs for this time period
            login_context = self._get_login_context(user_id, tx.created_at)
            
            history.append({
                "id": tx.id,
                "tx_hash": tx.tx_hash,
                "chain": tx.chain,
                "from_address": tx.from_address,
                "to_address": tx.to_address,
                "amount": float(tx.amount),
                "status": tx.status,
                "created_at": tx.created_at.isoformat(),
                "confirmed_at": tx.confirmed_at.isoformat() if tx.confirmed_at else None,
                "device_info": tx.device_info,
                "ip_address": tx.ip_address,
                "location": tx.location,
                "pin_attempts": tx.pin_attempts,
                "fraud_indicators": self._get_fraud_indicators(tx, login_context),
                "login_context": login_context
            })
        
        return history

    def _get_login_context(self, user_id: int, transaction_time: datetime) -> Dict:
        """Get login context around the transaction time"""
        # Look for logins within 1 hour before the transaction
        start_time = transaction_time - timedelta(hours=1)
        end_time = transaction_time + timedelta(minutes=30)
        
        login_logs = self.db.query(LoginLog).filter(
            LoginLog.user_id == user_id,
            LoginLog.created_at >= start_time,
            LoginLog.created_at <= end_time
        ).all()
        
        if not login_logs:
            return {"recent_logins": [], "suspicious_activity": False}
        
        # Check for suspicious activity
        suspicious = any(
            log.ip_address != login_logs[0].ip_address or 
            log.location != login_logs[0].location
            for log in login_logs
        )
        
        return {
            "recent_logins": [
                {
                    "time": log.created_at.isoformat(),
                    "ip_address": log.ip_address,
                    "location": log.location,
                    "device_info": log.device_info,
                    "success": log.success
                }
                for log in login_logs
            ],
            "suspicious_activity": suspicious
        }

    def _get_fraud_indicators(self, transaction: Transaction, login_context: Dict) -> List[str]:
        """Get fraud indicators for a transaction"""
        indicators = []
        
        # Check for multiple PIN attempts
        if transaction.pin_attempts > 1:
            indicators.append(f"Multiple PIN attempts: {transaction.pin_attempts}")
        
        # Check for location mismatch with recent logins
        if login_context.get("recent_logins"):
            recent_login = login_context["recent_logins"][0]
            if (transaction.location and recent_login["location"] and 
                transaction.location != recent_login["location"]):
                indicators.append("Location mismatch with recent login")
        
        # Check for IP mismatch
        if login_context.get("recent_logins"):
            recent_login = login_context["recent_logins"][0]
            if (transaction.ip_address and recent_login["ip_address"] and 
                transaction.ip_address != recent_login["ip_address"]):
                indicators.append("IP address mismatch with recent login")
        
        # Check for unusual transaction amount
        if float(transaction.amount) > 10000:  # Threshold can be configurable
            indicators.append("Unusually high transaction amount")
        
        # Check for rapid successive transactions
        recent_transactions = self.db.query(Transaction).filter(
            Transaction.user_id == transaction.user_id,
            Transaction.created_at >= transaction.created_at - timedelta(minutes=5),
            Transaction.created_at <= transaction.created_at + timedelta(minutes=5)
        ).count()
        
        if recent_transactions > 3:
            indicators.append("Rapid successive transactions")
        
        return indicators

    def get_transaction_patterns(self, user_id: int, days: int = 30) -> Dict:
        """Analyze transaction patterns for fraud detection"""
        start_date = datetime.utcnow() - timedelta(days=days)
        
        transactions = self.db.query(Transaction).filter(
            Transaction.user_id == user_id,
            Transaction.created_at >= start_date
        ).all()
        
        if not transactions:
            return {"message": "No transactions found in the specified period"}
        
        # Calculate patterns
        total_transactions = len(transactions)
        total_amount = sum(float(tx.amount) for tx in transactions)
        avg_amount = total_amount / total_transactions
        
        # Unique addresses
        unique_to_addresses = len(set(tx.to_address for tx in transactions))
        
        # Transactions by chain
        chain_distribution = {}
        for tx in transactions:
            chain_distribution[tx.chain] = chain_distribution.get(tx.chain, 0) + 1
        
        # Time distribution
        hour_distribution = {}
        for tx in transactions:
            hour = tx.created_at.hour
            hour_distribution[hour] = hour_distribution.get(hour, 0) + 1
        
        # Failed PIN attempts
        total_pin_attempts = sum(tx.pin_attempts for tx in transactions)
        transactions_with_pin_attempts = len([tx for tx in transactions if tx.pin_attempts > 0])
        
        return {
            "total_transactions": total_transactions,
            "total_amount": total_amount,
            "average_amount": avg_amount,
            "unique_recipients": unique_to_addresses,
            "chain_distribution": chain_distribution,
            "peak_hours": sorted(hour_distribution.items(), key=lambda x: x[1], reverse=True)[:5],
            "pin_attempts": {
                "total_attempts": total_pin_attempts,
                "transactions_with_attempts": transactions_with_pin_attempts
            },
            "fraud_risk_score": self._calculate_fraud_risk_score(transactions)
        }

    def _calculate_fraud_risk_score(self, transactions: List[Transaction]) -> int:
        """Calculate fraud risk score based on transaction patterns"""
        risk_score = 0
        
        # High transaction frequency
        if len(transactions) > 20:
            risk_score += 20
        
        # High average amount
        avg_amount = sum(float(tx.amount) for tx in transactions) / len(transactions)
        if avg_amount > 1000:
            risk_score += 15
        
        # Multiple PIN attempts
        total_pin_attempts = sum(tx.pin_attempts for tx in transactions)
        if total_pin_attempts > 10:
            risk_score += 25
        
        # Multiple locations
        unique_locations = len(set(tx.location for tx in transactions if tx.location))
        if unique_locations > 3:
            risk_score += 20
        
        # Multiple IPs
        unique_ips = len(set(tx.ip_address for tx in transactions if tx.ip_address))
        if unique_ips > 5:
            risk_score += 20
        
        return min(risk_score, 100)

    def get_frequent_recipients(self, user_id: int, limit: int = 10) -> List[Dict]:
        """Get most frequently transferred addresses"""
        frequent_recipients = self.db.query(
            Transaction.to_address,
            Transaction.chain,
            func.count(Transaction.id).label('count'),
            func.sum(Transaction.amount).label('total_amount')
        ).filter(
            Transaction.user_id == user_id,
            Transaction.status == 'confirmed'
        ).group_by(
            Transaction.to_address,
            Transaction.chain
        ).order_by(
            desc('count')
        ).limit(limit).all()
        
        return [
            {
                'address': recipient.to_address,
                'chain': recipient.chain,
                'transaction_count': recipient.count,
                'total_amount': float(recipient.total_amount)
            }
            for recipient in frequent_recipients
        ] 
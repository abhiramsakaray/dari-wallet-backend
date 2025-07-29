from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from app.models.transaction import Transaction
from app.models.user import User


class AnalyticsService:
    def __init__(self, db: Session):
        self.db = db

    def track_frequent_transfers(self, user_id: int, to_address: str, chain: str) -> None:
        """Track frequently transferred addresses for quick access"""
        # This could be stored in a separate table for frequent transfers
        # For now, we'll just log it in the transaction
        pass

    def get_frequent_transfers(self, user_id: int, limit: int = 10) -> List[Dict]:
        """Get user's most frequently transferred addresses"""
        frequent_transfers = self.db.query(
            Transaction.to_address,
            Transaction.chain,
            func.count(Transaction.id).label('transfer_count')
        ).filter(
            Transaction.user_id == user_id,
            Transaction.status == 'confirmed'
        ).group_by(
            Transaction.to_address,
            Transaction.chain
        ).order_by(
            desc('transfer_count')
        ).limit(limit).all()

        return [
            {
                'address': transfer.to_address,
                'chain': transfer.chain,
                'count': transfer.transfer_count
            }
            for transfer in frequent_transfers
        ]

    def get_peak_usage_times(self, user_id: int, days: int = 30) -> Dict:
        """Get user's peak usage times"""
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Get transactions by hour of day
        hourly_stats = self.db.query(
            func.extract('hour', Transaction.created_at).label('hour'),
            func.count(Transaction.id).label('count')
        ).filter(
            Transaction.user_id == user_id,
            Transaction.created_at >= start_date
        ).group_by(
            func.extract('hour', Transaction.created_at)
        ).order_by(
            desc('count')
        ).all()

        # Get transactions by day of week
        daily_stats = self.db.query(
            func.extract('dow', Transaction.created_at).label('day'),
            func.count(Transaction.id).label('count')
        ).filter(
            Transaction.user_id == user_id,
            Transaction.created_at >= start_date
        ).group_by(
            func.extract('dow', Transaction.created_at)
        ).order_by(
            desc('count')
        ).all()

        return {
            'peak_hours': [{'hour': int(stat.hour), 'count': stat.count} for stat in hourly_stats[:5]],
            'peak_days': [{'day': int(stat.day), 'count': stat.count} for stat in daily_stats[:3]]
        }

    def get_transaction_patterns(self, user_id: int) -> Dict:
        """Analyze transaction patterns for fraud detection"""
        recent_transactions = self.db.query(Transaction).filter(
            Transaction.user_id == user_id,
            Transaction.created_at >= datetime.utcnow() - timedelta(days=7)
        ).all()

        # Analyze patterns
        total_transactions = len(recent_transactions)
        total_amount = sum(float(tx.amount) for tx in recent_transactions)
        avg_amount = total_amount / total_transactions if total_transactions > 0 else 0
        
        # Check for unusual patterns
        unusual_patterns = []
        if total_transactions > 20:  # More than 20 transactions in a week
            unusual_patterns.append("High transaction frequency")
        
        if avg_amount > 1000:  # Average transaction amount > $1000
            unusual_patterns.append("High average transaction amount")

        return {
            'total_transactions_7d': total_transactions,
            'total_amount_7d': total_amount,
            'average_amount': avg_amount,
            'unusual_patterns': unusual_patterns
        }

    def get_fraud_indicators(self, user_id: int) -> Dict:
        """Get fraud indicators based on transaction history"""
        recent_transactions = self.db.query(Transaction).filter(
            Transaction.user_id == user_id,
            Transaction.created_at >= datetime.utcnow() - timedelta(days=30)
        ).all()

        # Check for multiple failed PIN attempts
        failed_pin_attempts = sum(1 for tx in recent_transactions if tx.pin_attempts > 0)
        
        # Check for transactions from multiple locations
        unique_locations = len(set(tx.location for tx in recent_transactions if tx.location))
        
        # Check for transactions from multiple IPs
        unique_ips = len(set(tx.ip_address for tx in recent_transactions if tx.ip_address))
        
        fraud_indicators = []
        risk_score = 0

        if failed_pin_attempts > 5:
            fraud_indicators.append("Multiple failed PIN attempts")
            risk_score += 30

        if unique_locations > 3:
            fraud_indicators.append("Transactions from multiple locations")
            risk_score += 20

        if unique_ips > 5:
            fraud_indicators.append("Transactions from multiple IP addresses")
            risk_score += 25

        return {
            'risk_score': min(risk_score, 100),
            'fraud_indicators': fraud_indicators,
            'failed_pin_attempts': failed_pin_attempts,
            'unique_locations': unique_locations,
            'unique_ips': unique_ips
        } 
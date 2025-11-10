from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from datetime import datetime, timedelta
import sys
from pathlib import Path

root_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(root_dir))

from database import UserPreference, PriceHistory, OptimizationResult

class PreferenceService:
    @staticmethod
    def save_preferences(db: Session, preferences: dict, user_id: str = "default_user"):
        """Save or update user preferences"""
        existing = db.query(UserPreference).filter(
            UserPreference.user_id == user_id
        ).first()
        
        if existing:
            existing.avoid_hours = preferences.get("avoid_hours", existing.avoid_hours)
            existing.priority_appliances = preferences.get("priority_appliances", existing.priority_appliances)
            existing.updated_at = datetime.utcnow()
            db.commit()
            return existing
        else:
            new_pref = UserPreference(
                user_id=user_id,
                avoid_hours=preferences.get("avoid_hours", []),
                priority_appliances=preferences.get("priority_appliances", [])
            )
            db.add(new_pref)
            db.commit()
            db.refresh(new_pref)
            return new_pref
    
    @staticmethod
    def get_preferences(db: Session, user_id: str = "default_user"):
        """Get user preferences"""
        pref = db.query(UserPreference).filter(
            UserPreference.user_id == user_id
        ).first()
        
        if pref:
            return {
                "avoid_hours": pref.avoid_hours,
                "priority_appliances": pref.priority_appliances
            }
        else:
            return {
                "avoid_hours": [0, 1, 2, 3, 4, 5],
                "priority_appliances": []
            }

class PriceService:
    @staticmethod
    def save_prices(db: Session, prices_df):
        """Save price history to database"""
        try:
            db.query(PriceHistory).delete()
            db.commit()
            
            for _, row in prices_df.iterrows():
                price_record = PriceHistory(
                    time=str(row['time']),
                    price=float(row['price']),
                    source="comed"
                )
                db.add(price_record)
            
            db.commit()
            return True
        except Exception as e:
            db.rollback()
            raise e
    
    @staticmethod
    def get_all_prices(db: Session):
        """Get all current prices"""
        prices = db.query(PriceHistory).order_by(PriceHistory.timestamp).all()
        return [{
            "time": p.time,
            "price": p.price,
            "timestamp": p.timestamp.isoformat()
        } for p in prices]
    
    @staticmethod
    def get_price_history(db: Session, hours: int = 24):
        """Get price history for specified hours"""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        prices = db.query(PriceHistory).filter(
            PriceHistory.timestamp >= cutoff_time
        ).order_by(desc(PriceHistory.timestamp)).all()
        
        return [{
            "time": p.time,
            "price": p.price,
            "timestamp": p.timestamp.isoformat()
        } for p in reversed(prices)]
    
    @staticmethod
    def get_peak_hours(db: Session):
        """Get peak pricing hours"""
        prices = db.query(PriceHistory).all()
        if not prices:
            return []
        
        prices_list = [p.price for p in prices]
        avg_price = sum(prices_list) / len(prices_list)
        threshold = avg_price * 1.5
        
        peak_hours = [p.time for p in prices if p.price >= threshold]
        return peak_hours

class OptimizationService:
    @staticmethod
    def save_result(db: Session, result: dict, user_id: str = "default_user"):
        """Save optimization result"""
        opt_result = OptimizationResult(
            user_id=user_id,
            appliances=result.get("appliances"),
            schedule=result.get("schedule"),
            total_cost=result.get("total_cost"),
            comfort_score=result.get("comfort_score"),
            optimization_type=result.get("optimization_type", "lp")
        )
        db.add(opt_result)
        db.commit()
        db.refresh(opt_result)
        return opt_result
    
    @staticmethod
    def get_recent_results(db: Session, user_id: str = "default_user", limit: int = 10):
        """Get recent optimization results"""
        results = db.query(OptimizationResult).filter(
            OptimizationResult.user_id == user_id
        ).order_by(desc(OptimizationResult.created_at)).limit(limit).all()
        
        return [{
            "id": r.id,
            "schedule": r.schedule,
            "total_cost": r.total_cost,
            "comfort_score": r.comfort_score,
            "optimization_type": r.optimization_type,
            "created_at": r.created_at.isoformat()
        } for r in results]

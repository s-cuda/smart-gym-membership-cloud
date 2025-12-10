from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
import models
from ai_recommender import GymRecommender
from datetime import datetime, date, timedelta

app = FastAPI(
    title="Smart Gym Membership API",
    description="AI-powered gym management system with personalized class recommendations",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create tables
models.Base.metadata.create_all(bind=models.engine)

@app.get("/")
def read_root():
    return {
        "message": "Smart Gym Membership API",
        "version": "1.0.0",
        "features": ["Member Management", "Class Scheduling", "AI Recommendations", "Billing"],
        "docs": "/docs"
    }

# ============================================
# MEMBERS ENDPOINTS
# ============================================

@app.get("/members/")
def get_members(skip: int = 0, limit: int = 100, db: Session = Depends(models.get_db)):
    """Get all members"""
    members = db.query(models.Member).offset(skip).limit(limit).all()
    return members

@app.get("/members/{member_id}")
def get_member(member_id: int, db: Session = Depends(models.get_db)):
    """Get specific member by ID"""
    member = db.query(models.Member).filter(models.Member.member_id == member_id).first()
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")
    return member

@app.post("/members/")
def create_member(
    first_name: str,
    last_name: str,
    email: str,
    membership_level: str,
    phone: str = None,
    preferred_days: str = None,
    preferred_time_slot: str = None,
    db: Session = Depends(models.get_db)
):
    """Register new member"""
    
    # Check if email already exists
    existing = db.query(models.Member).filter(models.Member.email == email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    new_member = models.Member(
        first_name=first_name,
        last_name=last_name,
        email=email,
        membership_level=membership_level,
        phone=phone,
        join_date=datetime.now(),
        preferred_days=preferred_days,
        preferred_time_slot=preferred_time_slot
    )
    db.add(new_member)
    db.commit()
    db.refresh(new_member)
    return new_member

# ============================================
# CLASSES ENDPOINTS
# ============================================

@app.get("/classes/")
def get_classes(db: Session = Depends(models.get_db)):
    """Get all available classes"""
    classes = db.query(models.Class).all()
    return classes

@app.get("/classes/{class_id}")
def get_class(class_id: int, db: Session = Depends(models.get_db)):
    """Get specific class details"""
    class_info = db.query(models.Class).filter(models.Class.class_id == class_id).first()
    if not class_info:
        raise HTTPException(status_code=404, detail="Class not found")
    return class_info

# ============================================
# SCHEDULE ENDPOINTS
# ============================================

@app.get("/schedule/")
def get_schedule(day: str = None, db: Session = Depends(models.get_db)):
    """Get class schedule, optionally filtered by day"""
    query = db.query(models.ClassSchedule)
    if day:
        query = query.filter(models.ClassSchedule.day_of_week == day)
    schedules = query.all()
    return schedules

@app.get("/schedule/{schedule_id}")
def get_schedule_details(schedule_id: int, db: Session = Depends(models.get_db)):
    """Get detailed info about a scheduled class including capacity"""
    schedule = db.query(models.ClassSchedule).filter(
        models.ClassSchedule.schedule_id == schedule_id
    ).first()
    
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    
    # Get registration count
    registered = db.query(models.ClassRegistration).filter(
        models.ClassRegistration.schedule_id == schedule_id,
        models.ClassRegistration.attendance_status.in_(['Registered', 'Attended'])
    ).count()
    
    return {
        "schedule": schedule,
        "registered_count": registered,
        "max_capacity": schedule.class_info.max_capacity,
        "spots_available": schedule.class_info.max_capacity - registered,
        "is_full": registered >= schedule.class_info.max_capacity
    }

# ============================================
# REGISTRATION ENDPOINTS
# ============================================

@app.post("/registrations/")
def register_for_class(
    member_id: int,
    schedule_id: int,
    db: Session = Depends(models.get_db)
):
    """Register member for a class"""
    
    # Check if member exists
    member = db.query(models.Member).filter(models.Member.member_id == member_id).first()
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")
    
    # Check if schedule exists
    schedule = db.query(models.ClassSchedule).filter(
        models.ClassSchedule.schedule_id == schedule_id
    ).first()
    
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    
    # Check if already registered
    existing = db.query(models.ClassRegistration).filter(
        models.ClassRegistration.member_id == member_id,
        models.ClassRegistration.schedule_id == schedule_id
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Already registered for this class")
    
    # Check capacity
    count = db.query(models.ClassRegistration).filter(
        models.ClassRegistration.schedule_id == schedule_id,
        models.ClassRegistration.attendance_status.in_(['Registered', 'Attended'])
    ).count()
    
    if count >= schedule.class_info.max_capacity:
        raise HTTPException(status_code=400, detail="Class is full")
    
    registration = models.ClassRegistration(
        member_id=member_id,
        schedule_id=schedule_id,
        registration_date=datetime.now()
    )
    db.add(registration)
    db.commit()
    db.refresh(registration)
    return {"message": "Successfully registered", "registration": registration}

@app.get("/members/{member_id}/registrations")
def get_member_registrations(member_id: int, db: Session = Depends(models.get_db)):
    """Get all registrations for a member"""
    registrations = db.query(models.ClassRegistration).filter(
        models.ClassRegistration.member_id == member_id
    ).all()
    return registrations

# ============================================
# AI RECOMMENDATION ENDPOINTS
# ============================================

@app.get("/members/{member_id}/recommendations")
def get_recommendations(member_id: int, top_n: int = 5, db: Session = Depends(models.get_db)):
    """Get AI-powered class recommendations for member"""
    recommender = GymRecommender(db)
    recommendations = recommender.get_class_recommendations(member_id, top_n)
    return {
        "member_id": member_id,
        "recommendations": recommendations,
        "total_found": len(recommendations)
    }

@app.get("/members/{member_id}/weekly-schedule")
def get_weekly_schedule(member_id: int, db: Session = Depends(models.get_db)):
    """Generate personalized weekly schedule"""
    recommender = GymRecommender(db)
    schedule = recommender.generate_weekly_schedule(member_id)
    return {
        "member_id": member_id,
        "weekly_schedule": schedule,
        "total_days": len(schedule)
    }

@app.get("/members/{member_id}/insights")
def get_member_insights(member_id: int, db: Session = Depends(models.get_db)):
    """Get AI-powered fitness insights"""
    recommender = GymRecommender(db)
    insights = recommender.get_member_insights(member_id)
    return {
        "member_id": member_id,
        "insights": insights
    }

# ============================================
# BILLING ENDPOINTS
# ============================================

@app.get("/members/{member_id}/billing")
def get_member_billing(member_id: int, db: Session = Depends(models.get_db)):
    """Get billing history for member"""
    billings = db.query(models.Billing).filter(
        models.Billing.member_id == member_id
    ).all()
    return billings

@app.get("/billing/pending")
def get_pending_payments(db: Session = Depends(models.get_db)):
    """Get all pending payments"""
    pending = db.query(models.Billing).filter(
        models.Billing.payment_status == "Pending"
    ).all()
    return pending

# ============================================
# MEMBERSHIP PLANS ENDPOINTS
# ============================================

@app.get("/membership-plans/")
def get_membership_plans(db: Session = Depends(models.get_db)):
    """Get all membership plan options"""
    plans = db.query(models.MembershipPlan).all()
    return plans

# ============================================
# ADMIN DASHBOARD ENDPOINTS
# ============================================

@app.post("/billing/")
def create_billing(
    member_id: int,
    billing_date: str,
    amount: float,
    payment_status: str = "Pending",
    payment_method: str = "Auto-pay",
    next_billing_date: str = None,
    db: Session = Depends(models.get_db)
):
    """Create new billing record"""
    member = db.query(models.Member).filter(models.Member.member_id == member_id).first()
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")
    
    billing_date_obj = datetime.strptime(billing_date, "%Y-%m-%d").date()
    next_billing_date_obj = datetime.strptime(next_billing_date, "%Y-%m-%d").date() if next_billing_date else None
    
    new_billing = models.Billing(
        member_id=member_id,
        billing_date=billing_date_obj,
        amount=amount,
        payment_status=payment_status,
        payment_method=payment_method,
        next_billing_date=next_billing_date_obj
    )
    
    db.add(new_billing)
    db.commit()
    db.refresh(new_billing)
    
    return {"message": "Billing created successfully", "billing": new_billing}

@app.get("/admin/stats")
def get_admin_stats(db: Session = Depends(models.get_db)):
    """Get comprehensive admin dashboard statistics"""
    
    # Total members
    total_members = db.query(models.Member).count()
    active_members = db.query(models.Member).filter(
        models.Member.membership_status == "Active"
    ).count()
    
    # New members this month
    start_of_month = datetime.now().replace(day=1)
    new_this_month = db.query(models.Member).filter(
        models.Member.join_date >= start_of_month
    ).count()
    
    # Membership tier distribution
    membership_tiers = db.query(
        models.Member.membership_level,
        func.count(models.Member.member_id)
    ).group_by(models.Member.membership_level).all()
    
    tier_data = [{"name": tier[0], "count": tier[1]} for tier in membership_tiers]
    
    # Revenue calculations
    monthly_revenue = db.query(func.sum(models.Billing.amount)).filter(
        models.Billing.billing_date >= start_of_month,
        models.Billing.payment_status == "Paid"
    ).scalar() or 0
    
    outstanding = db.query(func.sum(models.Billing.amount)).filter(
        models.Billing.payment_status == "Pending"
    ).scalar() or 0
    
    # Total classes
    total_classes = db.query(models.Class).count()
    
    # Average attendance
    avg_attendance = 75
    
    # Popular classes - SIMPLIFIED (aggregate by schedule_id first)
    popular_classes_data = []
    try:
        # Get registration counts by schedule_id
        popular_schedules = db.query(
            models.ClassRegistration.schedule_id,
            func.count(models.ClassRegistration.registration_id).label('count')
        ).group_by(
            models.ClassRegistration.schedule_id
        ).order_by(
            func.count(models.ClassRegistration.registration_id).desc()
        ).limit(10).all()
        
        # For each popular schedule, get the class name
        class_bookings = {}
        for sched_id, count in popular_schedules:
            schedule = db.query(models.ClassSchedule).filter(
                models.ClassSchedule.schedule_id == sched_id
            ).first()
            
            if schedule:
                class_obj = db.query(models.Class).filter(
                    models.Class.class_id == schedule.class_id
                ).first()
                
                if class_obj:
                    class_name = class_obj.class_name
                    if class_name in class_bookings:
                        class_bookings[class_name] += count
                    else:
                        class_bookings[class_name] = count
        
        # Convert to list and sort
        popular_classes_data = [
            {"name": name, "bookings": bookings} 
            for name, bookings in sorted(class_bookings.items(), key=lambda x: x[1], reverse=True)[:5]
        ]
        
    except Exception as e:
        print(f"Error in popular_classes: {str(e)}")
        import traceback
        traceback.print_exc()
        popular_classes_data = []
    
    # Recent activity - SIMPLIFIED
    recent_activity = []
    try:
        # Get recent registrations
        recent_regs = db.query(models.ClassRegistration).order_by(
            models.ClassRegistration.registration_date.desc()
        ).limit(10).all()
        
        for reg in recent_regs:
            # Get member info
            member = db.query(models.Member).filter(
                models.Member.member_id == reg.member_id
            ).first()
            
            # Get schedule info
            schedule = db.query(models.ClassSchedule).filter(
                models.ClassSchedule.schedule_id == reg.schedule_id
            ).first()
            
            # Get class info
            class_obj = None
            if schedule:
                class_obj = db.query(models.Class).filter(
                    models.Class.class_id == schedule.class_id
                ).first()
            
            if member:
                activity = {
                    "icon": "🆕",
                    "title": f"{member.first_name} {member.last_name} registered",
                    "description": f"Registered for {class_obj.class_name}" if class_obj else "New class registration",
                    "time": reg.registration_date.strftime("%b %d, %Y") if reg.registration_date else "Recently"
                }
                recent_activity.append(activity)
        
    except Exception as e:
        print(f"Error in recent_activity: {str(e)}")
        import traceback
        traceback.print_exc()
        recent_activity = []
    
    return {
        "total_members": total_members,
        "active_members": active_members,
        "new_this_month": new_this_month,
        "monthly_revenue": float(monthly_revenue),
        "outstanding": float(outstanding),
        "total_classes": total_classes,
        "avg_attendance": avg_attendance,
        "membership_tiers": tier_data,
        "popular_classes": popular_classes_data,
        "recent_activity": recent_activity
    }
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
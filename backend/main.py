from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
import models
from ai_recommender import GymRecommender
from datetime import datetime, date

app = FastAPI(
    title="Smart Gym Membership API",
    description="AI-powered gym management system with personalized class recommendations",
    version="1.0.0"
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
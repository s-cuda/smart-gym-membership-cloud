from sqlalchemy import create_engine, Column, Integer, String, Date, DateTime, DECIMAL, ForeignKey, Text, Time
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from datetime import datetime

Base = declarative_base()

class Member(Base):
    __tablename__ = 'members'
    
    member_id = Column(Integer, primary_key=True, autoincrement=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    phone = Column(String(15))
    date_of_birth = Column(Date)
    membership_level = Column(String(20), nullable=False)
    join_date = Column(DateTime, nullable=False, default=datetime.now)
    membership_status = Column(String(20), default='Active')
    preferred_days = Column(String(100))
    preferred_time_slot = Column(String(50))
    height_cm = Column(Integer)
    weight_kg = Column(Integer)
    age = Column(Integer)
    gender = Column(String(10))
    
    billings = relationship("Billing", back_populates="member")
    registrations = relationship("ClassRegistration", back_populates="member")

class MembershipPlan(Base):
    __tablename__ = 'membership_plans'
    
    plan_id = Column(Integer, primary_key=True)
    plan_name = Column(String(50), nullable=False)
    monthly_fee = Column(DECIMAL(10, 2), nullable=False)
    class_access_limit = Column(Integer)
    features = Column(Text)

class Class(Base):
    __tablename__ = 'classes'
    
    class_id = Column(Integer, primary_key=True, autoincrement=True)
    class_name = Column(String(100), nullable=False)
    instructor_name = Column(String(100))
    duration_minutes = Column(Integer)
    max_capacity = Column(Integer)
    difficulty_level = Column(String(20))
    required_membership = Column(String(20))
    description = Column(Text)
    
    schedules = relationship("ClassSchedule", back_populates="class_info")

class ClassSchedule(Base):
    __tablename__ = 'class_schedule'
    
    schedule_id = Column(Integer, primary_key=True, autoincrement=True)
    class_id = Column(Integer, ForeignKey('classes.class_id'), nullable=False)
    day_of_week = Column(String(10), nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    room_location = Column(String(50))
    
    class_info = relationship("Class", back_populates="schedules")
    registrations = relationship("ClassRegistration", back_populates="schedule")

class ClassRegistration(Base):
    __tablename__ = 'class_registrations'
    
    registration_id = Column(Integer, primary_key=True, autoincrement=True)
    member_id = Column(Integer, ForeignKey('members.member_id'), nullable=False)
    schedule_id = Column(Integer, ForeignKey('class_schedule.schedule_id'), nullable=False)
    registration_date = Column(DateTime, nullable=False, default=datetime.now)
    attendance_status = Column(String(20), default='Registered')
    
    member = relationship("Member", back_populates="registrations")
    schedule = relationship("ClassSchedule", back_populates="registrations")

class Billing(Base):
    __tablename__ = 'billing'
    
    billing_id = Column(Integer, primary_key=True, autoincrement=True)
    member_id = Column(Integer, ForeignKey('members.member_id'), nullable=False)
    billing_date = Column(Date, nullable=False)
    amount = Column(DECIMAL(10, 2), nullable=False)
    payment_status = Column(String(20), default='Pending')
    payment_method = Column(String(50))
    next_billing_date = Column(Date)
    
    member = relationship("Member", back_populates="billings")

# Database setup
DATABASE_URL = "sqlite:///./gym_membership.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
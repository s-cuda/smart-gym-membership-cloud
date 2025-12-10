from models import engine, SessionLocal, Base, Member, MembershipPlan, Class, ClassSchedule, Billing, ClassRegistration
from datetime import datetime, date, time, timedelta
import random

def init_database():
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    if db.query(Member).first():
        print("Database already initialized")
        return
    
    print("Initializing database with sample data...")
    
    plans = [
        MembershipPlan(plan_id=1, plan_name="Standard", monthly_fee=29.99, class_access_limit=4, 
                      features="Basic gym access, 4 classes per week"),
        MembershipPlan(plan_id=2, plan_name="Premium", monthly_fee=49.99, class_access_limit=12,
                      features="Full gym access, 12 classes per week, guest pass"),
        MembershipPlan(plan_id=3, plan_name="Platinum", monthly_fee=79.99, class_access_limit=None,
                      features="Unlimited access, all classes, personal trainer session")
    ]
    db.add_all(plans)
    
    classes_data = [
        ("Yoga", "Sarah Johnson", 60, 20, "Beginner", "Standard", "Relaxing yoga for flexibility and mindfulness"),
        ("Spin", "Mike Chen", 45, 25, "Intermediate", "Standard", "High-energy cycling workout"),
        ("Pilates", "Emma Davis", 50, 18, "Beginner", "Standard", "Core strengthening and flexibility"),
        ("Zumba", "Maria Garcia", 50, 30, "Beginner", "Standard", "Fun Latin-inspired dance workout"),
        ("Stretching", "Lisa Anderson", 30, 25, "Beginner", "Standard", "Gentle stretching and mobility"),
        ("HIIT", "Chris Brown", 45, 20, "Intermediate", "Premium", "High intensity interval training"),
        ("CrossFit", "John Smith", 60, 15, "Advanced", "Premium", "Intense functional fitness training"),
        ("Boxing", "Tom Wilson", 60, 12, "Advanced", "Premium", "Technical boxing and conditioning"),
        ("Personal Training", "Alex Rodriguez", 60, 1, "All Levels", "Platinum", "One-on-one customized training session with elite coach"),
        ("Olympic Lifting", "Marcus Chen", 75, 8, "Advanced", "Platinum", "Advanced barbell techniques - snatch, clean & jerk with professional coaching"),
        ("Recovery & Massage", "Dr. Emma Thompson", 45, 6, "All Levels", "Platinum", "Sports massage and recovery techniques for optimal performance"),
    ]
        
    classes = []
    for name, instructor, duration, capacity, difficulty, required, desc in classes_data:
        c = Class(
            class_name=name,
            instructor_name=instructor,
            duration_minutes=duration,
            max_capacity=capacity,
            difficulty_level=difficulty,
            required_membership=required,
            description=desc
        )
        classes.append(c)
    db.add_all(classes)
    db.commit()
    
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    times_slots = [
        (time(6, 0), time(7, 0)),
        (time(9, 0), time(10, 0)),
        (time(12, 0), time(13, 0)),
        (time(17, 0), time(18, 0)),
        (time(18, 30), time(19, 30))
    ]
    
    schedules = []
    for class_obj in classes:
        selected_days = random.sample(days[:5], 3)
        for day in selected_days:
            start, end = random.choice(times_slots)
            schedule = ClassSchedule(
                class_id=class_obj.class_id,
                day_of_week=day,
                start_time=start,
                end_time=end,
                room_location=f"Room {random.randint(1, 5)}"
            )
            schedules.append(schedule)
    db.add_all(schedules)
    
    first_names = ["John", "Jane", "Mike", "Sarah", "Chris", "Emma", "David", "Lisa", "Tom", "Amy",
                   "Kevin", "Rachel", "Steve", "Nicole", "Brian", "Jessica", "Mark", "Lauren", "Dan", "Megan"]
    last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Wilson", "Moore",
                  "Taylor", "Anderson", "Thomas", "Jackson", "White", "Harris", "Martin", "Thompson", "Martinez", "Robinson"]
    membership_levels = ["Standard", "Premium", "Platinum"]
    time_slots = ["Morning", "Afternoon", "Evening"]
    
    members = []
    genders = ["Male", "Female"]
    for i in range(50):
        gender = random.choice(genders)
        birth_year = random.randint(1970, 2000)
        age = 2025 - birth_year
        
        if gender == "Male":
            height = random.randint(165, 195)
            weight = random.randint(65, 105)
        else:
            height = random.randint(155, 180)
            weight = random.randint(50, 85)
        
        member = Member(
            first_name=random.choice(first_names),
            last_name=random.choice(last_names),
            email=f"member{i+1}@gym.com",
            phone=f"555-{random.randint(1000, 9999)}",
            date_of_birth=date(birth_year, random.randint(1, 12), random.randint(1, 28)),
            membership_level=random.choice(membership_levels),
            join_date=datetime.now() - timedelta(days=random.randint(0, 365)),
            membership_status="Active",
            preferred_days="Monday,Wednesday,Friday",
            preferred_time_slot=random.choice(time_slots),
            height_cm=height,
            weight_kg=weight,
            age=age,
            gender=gender
        )
        members.append(member)
    db.add_all(members)
    db.commit()
    
    for member in members:
        plan = db.query(MembershipPlan).filter(
            MembershipPlan.plan_name == member.membership_level
        ).first()
        
        billing = Billing(
            member_id=member.member_id,
            billing_date=date.today(),
            amount=plan.monthly_fee,
            payment_status=random.choice(["Paid", "Pending", "Paid", "Paid"]),
            payment_method="Credit Card",
            next_billing_date=date.today() + timedelta(days=30)
        )
        db.add(billing)
    
    for _ in range(100):
        member = random.choice(members)
        schedule = random.choice(schedules)
        
        exists = db.query(ClassRegistration).filter(
            ClassRegistration.member_id == member.member_id,
            ClassRegistration.schedule_id == schedule.schedule_id
        ).first()
        
        if not exists:
            registration = ClassRegistration(
                member_id=member.member_id,
                schedule_id=schedule.schedule_id,
                registration_date=datetime.now() - timedelta(days=random.randint(0, 30)),
                attendance_status=random.choice(["Attended", "Registered", "Attended", "Attended"])
            )
            db.add(registration)
    
    db.commit()
    print(f"✅ Database initialized with:")
    print(f"   - {len(members)} members")
    print(f"   - {len(classes)} class types")
    print(f"   - {len(schedules)} scheduled sessions")
    print(f"   - 3 membership plans")
    print(f"   - Sample billing and registration data")
    db.close()

if __name__ == "__main__":
    init_database()
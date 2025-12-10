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
        ("Tai Chi", "Master Zhang Wei", 45, 20, "Beginner", "Standard", "Ancient Chinese martial art promoting balance and inner peace"),
        ("Cardio Kickboxing", "Jessica Martinez", 50, 22, "Beginner", "Standard", "High-energy martial arts inspired cardio workout"),
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
    
    first_names_male = ["John", "Mike", "Chris", "David", "Tom", "Kevin", "Steve", "Brian", "Mark", "Dan",
                        "James", "Robert", "Michael", "William", "Richard", "Joseph", "Thomas", "Charles", "Daniel", "Matthew"]
    first_names_female = ["Jane", "Sarah", "Emma", "Lisa", "Amy", "Rachel", "Nicole", "Jessica", "Lauren", "Megan",
                          "Emily", "Michelle", "Ashley", "Jennifer", "Amanda", "Stephanie", "Rebecca", "Laura", "Maria", "Anna"]
    last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Wilson", "Moore",
                  "Taylor", "Anderson", "Thomas", "Jackson", "White", "Harris", "Martin", "Thompson", "Martinez", "Robinson",
                  "Clark", "Rodriguez", "Lewis", "Lee", "Walker", "Hall", "Allen", "Young", "King", "Wright"]
    
    membership_levels = ["Standard", "Premium", "Platinum"]
    time_slots = ["Morning", "Afternoon", "Evening"]
    
    day_combinations = [
        "Monday,Wednesday,Friday",
        "Tuesday,Thursday",
        "Monday,Wednesday",
        "Tuesday,Thursday,Saturday",
        "Monday,Friday",
        "Wednesday,Friday",
        "Saturday,Sunday",
        "Monday,Tuesday,Wednesday",
        "Thursday,Friday,Saturday"
    ]
    
    members = []
    for i in range(300):
        gender = random.choice(["Male", "Female"])
        
        birth_year = random.randint(1960, 2005)
        age = 2025 - birth_year
        
        if gender == "Male":
            first_name = random.choice(first_names_male)
            if age < 25:
                height = random.randint(170, 190)
                weight = random.randint(65, 90)
            elif age < 40:
                height = random.randint(168, 188)
                weight = random.randint(70, 100)
            elif age < 55:
                height = random.randint(165, 185)
                weight = random.randint(75, 105)
            else:
                height = random.randint(163, 180)
                weight = random.randint(70, 100)
        else:
            first_name = random.choice(first_names_female)
            if age < 25:
                height = random.randint(158, 175)
                weight = random.randint(50, 70)
            elif age < 40:
                height = random.randint(155, 173)
                weight = random.randint(52, 75)
            elif age < 55:
                height = random.randint(153, 170)
                weight = random.randint(55, 80)
            else:
                height = random.randint(150, 168)
                weight = random.randint(55, 78)
        
        membership = random.choice(membership_levels)
        
        member = Member(
            first_name=first_name,
            last_name=random.choice(last_names),
            email=f"member{i+1}@gym.com",
            phone=f"555-{random.randint(1000, 9999)}",
            date_of_birth=date(birth_year, random.randint(1, 12), random.randint(1, 28)),
            membership_level=membership,
            join_date=datetime.now() - timedelta(days=random.randint(0, 730)),
            membership_status="Active",
            preferred_days=random.choice(day_combinations),
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
            payment_status=random.choice(["Paid", "Paid", "Paid", "Pending"]),
            payment_method="Credit Card",
            next_billing_date=date.today() + timedelta(days=30)
        )
        db.add(billing)
    
    for _ in range(500):
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
                registration_date=datetime.now() - timedelta(days=random.randint(0, 60)),
                attendance_status=random.choice(["Attended", "Attended", "Attended", "Registered"])
            )
            db.add(registration)
    
    db.commit()
    print(f"✅ Database initialized with:")
    print(f"   - {len(members)} members")
    print(f"   - {len(classes)} class types (7 Standard, 3 Premium, 3 Platinum)")
    print(f"   - {len(schedules)} scheduled sessions")
    print(f"   - 3 membership plans")
    print(f"   - ~500 class registrations")
    print(f"   - Sample billing data")
    db.close()

if __name__ == "__main__":
    init_database()
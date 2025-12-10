from sqlalchemy.orm import Session
import models
import openai
import json
import os
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

class GymRecommender:
    def __init__(self, db: Session):
        self.db = db
    
    def _get_member_profile(self, member_id: int):
        member = self.db.query(models.Member).filter(
            models.Member.member_id == member_id
        ).first()
        
        if not member:
            return None
        
        past_registrations = self.db.query(models.ClassRegistration).filter(
            models.ClassRegistration.member_id == member_id,
            models.ClassRegistration.attendance_status == "Attended"
        ).all()
        
        past_classes = [reg.schedule.class_info.class_name for reg in past_registrations]
        
        return {
            "member_id": member.member_id,
            "name": f"{member.first_name} {member.last_name}",
            "membership_level": member.membership_level,
            "preferred_time": member.preferred_time_slot,
            "preferred_days": member.preferred_days,
            "past_classes": past_classes,
            "total_classes_attended": len(past_classes)
        }
    
    def _get_available_classes(self, membership_level: str = None):
        query = self.db.query(models.Class)
        
        all_classes = query.all()
        
        result = []
        for cls in all_classes:
            can_access = False
            if membership_level == "Platinum":
                can_access = True
            elif membership_level == "Premium" and cls.required_membership in ["Standard", "Premium"]:
                can_access = True
            elif membership_level == "Standard" and cls.required_membership == "Standard":
                can_access = True
            
            if can_access or membership_level is None:
                result.append({
                    "class_id": cls.class_id,
                    "name": cls.class_name,
                    "instructor": cls.instructor_name,
                    "difficulty": cls.difficulty_level,
                    "duration": cls.duration_minutes,
                    "required_membership": cls.required_membership,
                    "description": cls.description,
                    "max_capacity": cls.max_capacity
                })
        
        return result
    
    def _check_class_schedule(self, class_id: int, preferred_time: str = None):
        schedules = self.db.query(models.ClassSchedule).filter(
            models.ClassSchedule.class_id == class_id
        ).all()
        
        result = []
        for schedule in schedules:
            hour = schedule.start_time.hour
            time_slot = "Morning" if hour < 12 else "Afternoon" if hour < 17 else "Evening"
            
            if preferred_time and time_slot != preferred_time:
                continue
            
            registered = self.db.query(models.ClassRegistration).filter(
                models.ClassRegistration.schedule_id == schedule.schedule_id,
                models.ClassRegistration.attendance_status.in_(["Registered", "Attended"])
            ).count()
            
            result.append({
                "day": schedule.day_of_week,
                "time": f"{schedule.start_time.strftime('%H:%M')}-{schedule.end_time.strftime('%H:%M')}",
                "time_slot": time_slot,
                "room": schedule.room_location,
                "spots_available": schedule.class_info.max_capacity - registered,
                "capacity": schedule.class_info.max_capacity
            })
        
        return result
    
    def _calculate_match_score(self, member_id: int, class_id: int):
        member = self.db.query(models.Member).filter(
            models.Member.member_id == member_id
        ).first()
        
        class_obj = self.db.query(models.Class).filter(
            models.Class.class_id == class_id
        ).first()
        
        if not member or not class_obj:
            return {"score": 0, "factors": {}}
        
        factors = {}
        
        difficulty_score = 0
        if member.membership_level == "Standard" and class_obj.difficulty_level == "Beginner":
            difficulty_score = 30
        elif member.membership_level == "Premium" and class_obj.difficulty_level in ["Beginner", "Intermediate"]:
            difficulty_score = 30
        elif member.membership_level == "Platinum":
            difficulty_score = 25
        factors["difficulty_match"] = difficulty_score
        
        access_score = 0
        if class_obj.required_membership == "Standard":
            access_score = 25
        elif class_obj.required_membership == "Premium" and member.membership_level in ["Premium", "Platinum"]:
            access_score = 25
        factors["membership_access"] = access_score
        
        schedules = self._check_class_schedule(class_id, member.preferred_time_slot)
        time_score = 35 if len(schedules) > 0 else 0
        factors["time_availability"] = time_score
        
        total_score = sum(factors.values())
        
        return {
            "score": total_score,
            "factors": factors,
            "percentage": min(100, total_score)
        }
    
    def _get_similar_member_preferences(self, member_id: int):
        member = self.db.query(models.Member).filter(
            models.Member.member_id == member_id
        ).first()
        
        if not member:
            return {"popular_classes": []}
        
        similar_members = self.db.query(models.Member).filter(
            models.Member.membership_level == member.membership_level,
            models.Member.preferred_time_slot == member.preferred_time_slot,
            models.Member.member_id != member_id
        ).limit(10).all()
        
        class_popularity = {}
        for similar in similar_members:
            registrations = self.db.query(models.ClassRegistration).filter(
                models.ClassRegistration.member_id == similar.member_id,
                models.ClassRegistration.attendance_status == "Attended"
            ).all()
            
            for reg in registrations:
                class_name = reg.schedule.class_info.class_name
                class_popularity[class_name] = class_popularity.get(class_name, 0) + 1
        
        popular = sorted(class_popularity.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return {
            "popular_classes": [name for name, _ in popular],
            "similar_members_count": len(similar_members)
        }
    
    def get_class_recommendations(self, member_id: int, top_n: int = 4):
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "get_member_profile",
                    "description": "Get member's fitness profile including preferences, membership level, and class history",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "member_id": {"type": "integer", "description": "The member's ID"}
                        },
                        "required": ["member_id"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_available_classes",
                    "description": "Get all gym classes the member can access based on their membership level",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "membership_level": {"type": "string", "description": "Standard, Premium, or Platinum"}
                        },
                        "required": ["membership_level"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "check_class_schedule",
                    "description": "Check when a specific class is offered and if it matches member's preferred time",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "class_id": {"type": "integer", "description": "The class ID"},
                            "preferred_time": {"type": "string", "description": "Morning, Afternoon, or Evening"}
                        },
                        "required": ["class_id"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "calculate_match_score",
                    "description": "Calculate how well a class matches the member's profile and preferences",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "member_id": {"type": "integer"},
                            "class_id": {"type": "integer"}
                        },
                        "required": ["member_id", "class_id"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_similar_member_preferences",
                    "description": "Find what classes similar members with same membership level and time preference enjoy",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "member_id": {"type": "integer"}
                        },
                        "required": ["member_id"]
                    }
                }
            }
        ]
        
        messages = [
            {
                "role": "system",
                "content": """You are an expert fitness AI that provides personalized, evidence-based gym class recommendations. 

Your recommendations should be:
1. Technically informed - reference physiological adaptation, training principles, periodization
2. Data-driven - use match scores, attendance patterns, capacity data
3. Convincing - explain WHY each class benefits their specific goals
4. Progressive - consider their experience level and past classes

Use available tools to gather data, then provide recommendations in JSON format."""
            },
            {
                "role": "user",
                "content": f"""Analyze member {member_id}'s profile and recommend the top {top_n} classes.

Use the tools to:
1. Get their profile and history
2. Find accessible classes
3. Check schedules for time compatibility
4. Calculate match scores
5. See what similar members enjoy

Provide exactly {top_n} recommendations from classes they can ACCESS based on their membership level.

Each recommendation should have:
- Technical reasoning (mention adaptation, progressive overload, recovery, etc.)
- Specific data points (match score, schedule details, capacity)
- Convincing explanations tailored to their level and goals

Return ONLY this JSON structure:
{{
  "recommendations": [
    {{
      "class_name": "string",
      "instructor": "string",
      "difficulty": "string",
      "duration": integer,
      "match_percentage": integer,
      "schedule_preview": "Monday 09:00, Wednesday 09:00",
      "spots_available": integer,
      "reasons": [
        "Technical reason with physiological benefit",
        "Data-driven reason with specific metric",
        "Social proof or progression reason"
      ]
    }}
  ]
}}"""
            }
        ]
        
        try:
            response = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                tools=tools,
                tool_choice="auto",
                temperature=0.7
            )
            
            while response.choices[0].message.tool_calls:
                messages.append(response.choices[0].message)
                
                for tool_call in response.choices[0].message.tool_calls:
                    function_name = tool_call.function.name
                    function_args = json.loads(tool_call.function.arguments)
                    
                    if function_name == "get_member_profile":
                        result = self._get_member_profile(function_args["member_id"])
                    elif function_name == "get_available_classes":
                        result = self._get_available_classes(function_args["membership_level"])
                    elif function_name == "check_class_schedule":
                        result = self._check_class_schedule(
                            function_args["class_id"],
                            function_args.get("preferred_time")
                        )
                    elif function_name == "calculate_match_score":
                        result = self._calculate_match_score(
                            function_args["member_id"],
                            function_args["class_id"]
                        )
                    elif function_name == "get_similar_member_preferences":
                        result = self._get_similar_member_preferences(function_args["member_id"])
                    
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": json.dumps(result)
                    })
                
                response = openai.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=messages,
                    tools=tools,
                    tool_choice="auto",
                    temperature=0.7
                )
            
            result = response.choices[0].message.content.strip()
            
            if result.startswith("```json"):
                result = result[7:]
            if result.endswith("```"):
                result = result[:-3]
            result = result.strip()
            
            recommendations_data = json.loads(result)
            return recommendations_data.get("recommendations", [])
            
        except Exception as e:
            print(f"OpenAI Error: {e}")
            return self._fallback_recommendations(member_id, top_n)
    
    def _fallback_recommendations(self, member_id: int, top_n: int):
        member_profile = self._get_member_profile(member_id)
        if not member_profile:
            return []
        
        available_classes = self._get_available_classes(member_profile["membership_level"])
        
        recommendations = []
        for cls in available_classes:
            if cls["name"] in member_profile["past_classes"]:
                continue
            
            score_data = self._calculate_match_score(member_id, cls["class_id"])
            schedules = self._check_class_schedule(cls["class_id"], member_profile["preferred_time"])
            
            if score_data["score"] > 0 and len(schedules) > 0:
                schedule_preview = ", ".join([f"{s['day']} {s['time']}" for s in schedules[:2]])
                
                recommendations.append({
                    "class_name": cls["name"],
                    "instructor": cls["instructor"],
                    "difficulty": cls["difficulty"],
                    "duration": cls["duration"],
                    "match_percentage": score_data["percentage"],
                    "schedule_preview": schedule_preview,
                    "spots_available": schedules[0]["spots_available"] if schedules else 0,
                    "reasons": [
                        f"Matches your {member_profile['membership_level']} membership level",
                        f"Available during your preferred {member_profile['preferred_time']} time slot",
                        f"{cls['difficulty']} difficulty appropriate for your experience"
                    ]
                })
        
        recommendations.sort(key=lambda x: x["match_percentage"], reverse=True)
        return recommendations[:top_n]        
    
    def generate_weekly_schedule(self, member_id: int):
        member = self.db.query(models.Member).filter(
            models.Member.member_id == member_id
        ).first()
        
        if not member:
            return {}
        
        recommended_classes = self.get_class_recommendations(member_id, top_n=15)
        
        weekly_schedule = {}
        preferred_days = member.preferred_days.split(',') if member.preferred_days else []
        
        for rec in recommended_classes:
            class_obj = self.db.query(models.Class).filter(
                models.Class.class_name == rec['class_name']
            ).first()
            
            if not class_obj:
                continue
            
            schedules = self.db.query(models.ClassSchedule).filter(
                models.ClassSchedule.class_id == class_obj.class_id
            ).all()
            
            for schedule in schedules:
                if schedule.day_of_week in preferred_days or not preferred_days:
                    hour = schedule.start_time.hour
                    time_matches = False
                    
                    if member.preferred_time_slot == "Morning" and hour < 12:
                        time_matches = True
                    elif member.preferred_time_slot == "Afternoon" and 12 <= hour < 17:
                        time_matches = True
                    elif member.preferred_time_slot == "Evening" and hour >= 17:
                        time_matches = True
                    
                    if time_matches:
                        if schedule.day_of_week not in weekly_schedule:
                            weekly_schedule[schedule.day_of_week] = []
                        
                        registered_count = self.db.query(models.ClassRegistration).filter(
                            models.ClassRegistration.schedule_id == schedule.schedule_id,
                            models.ClassRegistration.attendance_status.in_(['Registered', 'Attended'])
                        ).count()
                        
                        spots_left = schedule.class_info.max_capacity - registered_count
                        
                        weekly_schedule[schedule.day_of_week].append({
                            "schedule_id": schedule.schedule_id,
                            "class_name": rec['class_name'],
                            "time": f"{schedule.start_time.strftime('%H:%M')}-{schedule.end_time.strftime('%H:%M')}",
                            "room": schedule.room_location,
                            "instructor": rec['instructor'],
                            "difficulty": rec['difficulty'],
                            "duration": rec['duration'],
                            "capacity": f"{registered_count}/{schedule.class_info.max_capacity}",
                            "spots_left": spots_left,
                            "match_score": rec['match_percentage']
                        })
        
        for day in weekly_schedule:
            weekly_schedule[day].sort(key=lambda x: x['time'])
            weekly_schedule[day] = weekly_schedule[day][:3]
        
        return weekly_schedule
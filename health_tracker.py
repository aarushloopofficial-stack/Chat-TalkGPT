"""
Chat&Talk GPT - Health & Fitness Tracker Module
Provides comprehensive health and fitness tracking features
"""
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime, date, timedelta
from enum import Enum

logger = logging.getLogger("HealthTracker")

# Data storage path
DATA_DIR = Path("backend/memory")
HEALTH_FILE = DATA_DIR / "health_data.json"


class ActivityType(Enum):
    """Types of physical activities"""
    WALKING = "walking"
    RUNNING = "running"
    CYCLING = "cycling"
    SWIMMING = "swimming"
    YOGA = "yoga"
    GYM = "gym"
    HIIT = "hiit"
    STRETCHING = "stretching"
    SPORTS = "sports"
    OTHER = "other"


class MealType(Enum):
    """Types of meals"""
    BREAKFAST = "breakfast"
    LUNCH = "lunch"
    DINNER = "dinner"
    SNACK = "snack"


class HealthTracker:
    """Comprehensive health and fitness tracking"""

    def __init__(self):
        self.data = self._load_data()
        self._ensure_user_profile()
        logger.info("HealthTracker initialized")

    def _load_data(self) -> Dict:
        """Load health data from file"""
        try:
            if HEALTH_FILE.exists():
                with open(HEALTH_FILE, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Error loading health data: {e}")
        return {"user_profile": {}, "activities": [], "meals": [], "water": [], "sleep": []}

    def _save_data(self):
        """Save health data to file"""
        try:
            DATA_DIR.mkdir(parents=True, exist_ok=True)
            with open(HEALTH_FILE, 'w') as f:
                json.dump(self.data, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Error saving health data: {e}")

    def _ensure_user_profile(self):
        """Ensure user profile exists"""
        if "user_profile" not in self.data:
            self.data["user_profile"] = {}
        if "goals" not in self.data:
            self.data["goals"] = {
                "daily_steps": 10000,
                "daily_water": 8,  # glasses
                "daily_calories": 2000,
                "sleep_hours": 8
            }

    # ========== User Profile ==========
    def set_user_profile(self, name: str, age: int, gender: str, height: float, weight: float) -> Dict:
        """Set user health profile"""
        self.data["user_profile"] = {
            "name": name,
            "age": age,
            "gender": gender,
            "height_cm": height,
            "weight_kg": weight,
            "bmi": self._calculate_bmi(height, weight),
            "updated_at": datetime.now().isoformat()
        }
        self._save_data()
        return self.data["user_profile"]

    def get_user_profile(self) -> Dict:
        """Get user health profile"""
        return self.data.get("user_profile", {})

    def _calculate_bmi(self, height_cm: float, weight_kg: float) -> float:
        """Calculate BMI"""
        height_m = height_cm / 100
        bmi = weight_kg / (height_m * height_m)
        return round(bmi, 1)

    def get_bmi_category(self, bmi: float) -> str:
        """Get BMI category"""
        if bmi < 18.5:
            return "Underweight"
        elif bmi < 25:
            return "Normal weight"
        elif bmi < 30:
            return "Overweight"
        else:
            return "Obese"

    # ========== Exercise/Activity Tracking ==========
    def log_activity(
        self,
        activity_type: str,
        duration_minutes: int,
        calories_burned: Optional[int] = None,
        distance_km: Optional[float] = None,
        notes: str = ""
    ) -> Dict:
        """Log a physical activity"""
        # Calculate calories if not provided
        if calories_burned is None:
            calories_burned = self._estimate_calories(activity_type, duration_minutes)

        activity = {
            "id": len(self.data.get("activities", [])) + 1,
            "date": date.today().isoformat(),
            "time": datetime.now().isoformat(),
            "type": activity_type,
            "duration_minutes": duration_minutes,
            "calories_burned": calories_burned,
            "distance_km": distance_km,
            "notes": notes
        }

        if "activities" not in self.data:
            self.data["activities"] = []
        self.data["activities"].append(activity)
        self._save_data()

        return {
            "success": True,
            "activity": activity,
            "total_calories_today": self.get_total_calories_burned_today()
        }

    def _estimate_calories(self, activity_type: str, duration_minutes: int) -> int:
        """Estimate calories burned for an activity"""
        # Calories per minute estimates
        cal_per_min = {
            "walking": 4,
            "running": 10,
            "cycling": 8,
            "swimming": 9,
            "yoga": 3,
            "gym": 7,
            "hiit": 12,
            "stretching": 2,
            "sports": 8,
            "other": 5
        }
        rate = cal_per_min.get(activity_type, 5)
        return rate * duration_minutes

    def get_activities_today(self) -> List[Dict]:
        """Get today's activities"""
        today = date.today().isoformat()
        return [a for a in self.data.get("activities", []) if a.get("date") == today]

    def get_total_calories_burned_today(self) -> int:
        """Get total calories burned today"""
        activities = self.get_activities_today()
        return sum(a.get("calories_burned", 0) for a in activities)

    def get_weekly_stats(self) -> Dict:
        """Get weekly activity statistics"""
        week_ago = (date.today() - timedelta(days=7)).isoformat()
        activities = [a for a in self.data.get("activities", []) if a.get("date", "") >= week_ago]

        total_duration = sum(a.get("duration_minutes", 0) for a in activities)
        total_calories = sum(a.get("calories_burned", 0) for a in activities)
        total_distance = sum(a.get("distance_km", 0) for a in activities)

        # Group by day
        daily_stats = {}
        for a in activities:
            day = a.get("date", "")
            if day not in daily_stats:
                daily_stats[day] = {"duration": 0, "calories": 0}
            daily_stats[day]["duration"] += a.get("duration_minutes", 0)
            daily_stats[day]["calories"] += a.get("calories_burned", 0)

        return {
            "total_activities": len(activities),
            "total_duration_minutes": total_duration,
            "total_calories": total_calories,
            "total_distance_km": round(total_distance, 2),
            "daily_average_calories": round(total_calories / 7, 1) if activities else 0,
            "daily_stats": daily_stats
        }

    # ========== Water Intake Tracking ==========
    def log_water(self, glasses: int = 1) -> Dict:
        """Log water intake"""
        water_entry = {
            "id": len(self.data.get("water", [])) + 1,
            "date": date.today().isoformat(),
            "time": datetime.now().isoformat(),
            "glasses": glasses
        }

        if "water" not in self.data:
            self.data["water"] = []
        self.data["water"].append(water_entry)
        self._save_data()

        return {
            "success": True,
            "water_entry": water_entry,
            "total_glasses_today": self.get_water_today(),
            "goal": self.data.get("goals", {}).get("daily_water", 8),
            "remaining": max(0, self.data.get("goals", {}).get("daily_water", 8) - self.get_water_today())
        }

    def get_water_today(self) -> int:
        """Get today's water intake"""
        today = date.today().isoformat()
        return sum(w.get("glasses", 0) for w in self.data.get("water", []) if w.get("date") == today)

    def get_water_history(self, days: int = 7) -> List[Dict]:
        """Get water intake history"""
        start_date = (date.today() - timedelta(days=days-1)).isoformat()
        water_data = self.data.get("water", [])

        # Group by day
        daily_water = {}
        for w in water_data:
            day = w.get("date", "")
            if day >= start_date:
                if day not in daily_water:
                    daily_water[day] = 0
                daily_water[day] += w.get("glasses", 0)

        return [{"date": day, "glasses": count} for day, count in sorted(daily_water.items())]

    # ========== Meal/Calorie Tracking ==========
    def log_meal(
        self,
        meal_type: str,
        foods: List[Dict],
        total_calories: Optional[int] = None
    ) -> Dict:
        """Log a meal"""
        if total_calories is None:
            total_calories = sum(food.get("calories", 0) for food in foods)

        meal = {
            "id": len(self.data.get("meals", [])) + 1,
            "date": date.today().isoformat(),
            "time": datetime.now().isoformat(),
            "type": meal_type,
            "foods": foods,
            "total_calories": total_calories
        }

        if "meals" not in self.data:
            self.data["meals"] = []
        self.data["meals"].append(meal)
        self._save_data()

        return {
            "success": True,
            "meal": meal,
            "total_calories_today": self.get_total_calories_consumed_today()
        }

    def get_meals_today(self) -> List[Dict]:
        """Get today's meals"""
        today = date.today().isoformat()
        return [m for m in self.data.get("meals", []) if m.get("date") == today]

    def get_total_calories_consumed_today(self) -> int:
        """Get total calories consumed today"""
        meals = self.get_meals_today()
        return sum(m.get("total_calories", 0) for m in meals)

    def get_daily_summary(self) -> Dict:
        """Get comprehensive daily health summary"""
        today = date.today().isoformat()
        goals = self.data.get("goals", {})

        # Activity stats
        activities = self.get_activities_today()
        exercise_calories = sum(a.get("calories_burned", 0) for a in activities)
        exercise_minutes = sum(a.get("duration_minutes", 0) for a in activities)

        # Meal stats
        meals = self.get_meals_today()
        consumed_calories = sum(m.get("total_calories", 0) for m in meals)

        # Water stats
        water_glasses = self.get_water_today()

        # Net calories
        net_calories = consumed_calories - exercise_calories

        return {
            "date": today,
            "exercise": {
                "calories_burned": exercise_calories,
                "duration_minutes": exercise_minutes,
                "goal": goals.get("daily_calories", 2000),
                "activities_count": len(activities)
            },
            "nutrition": {
                "calories_consumed": consumed_calories,
                "calories_goal": goals.get("daily_calories", 2000),
                "remaining": max(0, goals.get("daily_calories", 2000) - consumed_calories),
                "net_calories": net_calories,
                "meals_count": len(meals)
            },
            "hydration": {
                "glasses": water_glasses,
                "goal": goals.get("daily_water", 8),
                "remaining": max(0, goals.get("daily_water", 8) - water_glasses),
                "percentage": round((water_glasses / goals.get("daily_water", 8)) * 100, 1)
            },
            "steps": {
                "count": 0,  # Would need step counter integration
                "goal": goals.get("daily_steps", 10000)
            }
        }

    # ========== Sleep Tracking ==========
    def log_sleep(self, hours: float, quality: str = "good") -> Dict:
        """Log sleep duration"""
        sleep_entry = {
            "id": len(self.data.get("sleep", [])) + 1,
            "date": date.today().isoformat(),
            "time": datetime.now().isoformat(),
            "hours": hours,
            "quality": quality
        }

        if "sleep" not in self.data:
            self.data["sleep"] = []
        self.data["sleep"].append(sleep_entry)
        self._save_data()

        return {
            "success": True,
            "sleep_entry": sleep_entry,
            "goal": self.data.get("goals", {}).get("sleep_hours", 8),
            "remaining": max(0, self.data.get("goals", {}).get("sleep_hours", 8) - hours)
        }

    def get_sleep_today(self) -> Optional[Dict]:
        """Get today's sleep data"""
        today = date.today().isoformat()
        sleep_data = self.data.get("sleep", [])
        for s in reversed(sleep_data):
            if s.get("date") == today:
                return s
        return None

    def get_sleep_history(self, days: int = 7) -> List[Dict]:
        """Get sleep history"""
        start_date = (date.today() - timedelta(days=days-1)).isoformat()
        sleep_data = self.data.get("sleep", [])

        return [s for s in sleep_data if s.get("date", "") >= start_date]

    # ========== Goals ==========
    def set_goals(self, goals: Dict) -> Dict:
        """Set health goals"""
        if "goals" not in self.data:
            self.data["goals"] = {}

        self.data["goals"].update(goals)
        self._save_data()
        return self.data["goals"]

    def get_goals(self) -> Dict:
        """Get current health goals"""
        return self.data.get("goals", {
            "daily_steps": 10000,
            "daily_water": 8,
            "daily_calories": 2000,
            "sleep_hours": 8
        })

    # ========== BMI Calculator ==========
    def calculate_bmi(self, height_cm: float, weight_kg: float) -> Dict:
        """Calculate BMI with category"""
        bmi = self._calculate_bmi(height_cm, weight_kg)
        category = self.get_bmi_category(bmi)

        # Calculate ideal weight range
        min_weight = 18.5 * (height_cm / 100) ** 2
        max_weight = 25 * (height_cm / 100) ** 2

        return {
            "bmi": bmi,
            "category": category,
            "ideal_weight_min_kg": round(min_weight, 1),
            "ideal_weight_max_kg": round(max_weight, 1),
            "height_cm": height_cm,
            "weight_kg": weight_kg
        }

    # ========== Motivational ==========
    def get_health_tips(self) -> List[str]:
        """Get health tips"""
        tips = [
            "Stay hydrated! Drink at least 8 glasses of water daily.",
            "Aim for 10,000 steps per day for better cardiovascular health.",
            "Get 7-9 hours of quality sleep each night.",
            "Include protein in every meal for muscle maintenance.",
            "Take short breaks every hour when working.",
            "Practice deep breathing exercises for stress relief.",
            "Stretch daily to improve flexibility and reduce injury risk.",
            "Eat colorful fruits and vegetables for essential vitamins.",
            "Limit processed foods and added sugars.",
            "Track your progress to stay motivated!"
        ]
        import random
        return random.sample(tips, 3)


# Singleton instance
health_tracker = HealthTracker()

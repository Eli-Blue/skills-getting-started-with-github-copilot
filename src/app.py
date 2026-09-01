"""
High School Management System API

A super simple FastAPI application that allows students to view and sign up
for extracurricular activities at Mergington High School.
"""

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
import os
from pathlib import Path


def is_valid_email(email: str) -> bool:
    """Validate email format (basic check)."""
    return "@" in email and "." in email.split("@")[1] if "@" in email else False


def activity_exists(activity_name: str, activities: dict) -> bool:
    """Check if an activity exists in the activities dictionary."""
    return activity_name in activities


def is_participant_already_signed_up(activity_name: str, email: str, activities: dict) -> bool:
    """Check if a participant is already signed up for an activity."""
    if activity_name not in activities:
        return False
    return email in activities[activity_name]["participants"]


def has_available_capacity(activity_name: str, activities: dict) -> bool:
    """Check if an activity has available capacity for new participants."""
    if activity_name not in activities:
        return False
    activity = activities[activity_name]
    return len(activity["participants"]) < activity["max_participants"]


app = FastAPI(title="Mergington High School API",
              description="API for viewing and signing up for extracurricular activities")

# Mount the static files directory
current_dir = Path(__file__).parent
app.mount("/static", StaticFiles(directory=os.path.join(Path(__file__).parent,
          "static")), name="static")

# In-memory activity database
activities = {
    "Chess Club": {
        "description": "Learn strategies and compete in chess tournaments",
        "schedule": "Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 12,
        "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
    },
    "Programming Class": {
        "description": "Learn programming fundamentals and build software projects",
        "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
        "max_participants": 20,
        "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
    },
    "Gym Class": {
        "description": "Physical education and sports activities",
        "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
        "max_participants": 30,
        "participants": ["john@mergington.edu", "olivia@mergington.edu"]
    }
}


@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")


@app.get("/activities")
def get_activities():
    return activities


@app.post("/activities/{activity_name}/signup")
def signup_for_activity(activity_name: str, email: str):
    """Sign up a student for an activity"""
    # Validate email format
    if not is_valid_email(email):
        raise HTTPException(status_code=400, detail="Invalid email format")
    
    # Validate activity exists
    if not activity_exists(activity_name, activities):
        raise HTTPException(status_code=404, detail="Activity not found")

    # Check if participant is already signed up
    if is_participant_already_signed_up(activity_name, email, activities):
        raise HTTPException(status_code=409, detail="Already signed up for this activity")
    
    # Check if activity has available capacity
    if not has_available_capacity(activity_name, activities):
        raise HTTPException(status_code=400, detail="Activity is at maximum capacity")

    # Add student
    activities[activity_name]["participants"].append(email)
    return {"message": f"Signed up {email} for {activity_name}"}

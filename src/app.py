@app.post("/activities/{activity_name}/signup")
def signup_for_activity(activity_name: str, email: str):
   """Sign up a student for an activity"""
   # Validate activity exists
   if activity_name not in activities:
      raise HTTPException(status_code=404, detail="Activity not found")

   # Get the activity
   activity = activities[activity_name]
"Soccer Team": {
   "description": "Competitive soccer training and matches",
   "schedule": "Tuesdays and Thursdays, 5:00 PM - 7:00 PM",
   "max_participants": 18,
   "participants": []
},
"Tennis Club": {
   "description": "Tennis lessons and tournaments",
   "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
   "max_participants": 16,
   "participants": []
},
"Photography Club": {
   "description": "Learn photography techniques and photo editing",
   "schedule": "Thursdays, 4:00 PM - 5:30 PM",
   "max_participants": 20,
   "participants": []
},
"Music Band": {
   "description": "Collaborative music performance and composition",
   "schedule": "Wednesdays and Fridays, 4:00 PM - 5:30 PM",
   "max_participants": 25,
   "participants": []
},
"Robotics Club": {
   "description": "Build and program robots for competitions",
   "schedule": "Mondays, 4:00 PM - 6:00 PM",
   "max_participants": 12,
   "participants": []
},
"Math Olympiad Team": {
   "description": "Advanced mathematics problem-solving and competitions",
   "schedule": "Fridays, 4:00 PM - 5:30 PM",
   "max_participants": 10,
   "participants": []
}
   # Validate student is not already signed up
   if email in activity["participants"]:
     raise HTTPException(status_code=400, detail="Student is already signed up")

   # Add student
   activity["participants"].append(email)
   return {"message": f"Signed up {email} for {activity_name}"}
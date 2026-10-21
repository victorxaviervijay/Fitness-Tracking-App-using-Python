
import pandas as pd
import numpy as np
import csv
import os
import json
import datetime
import random
from groq import Groq

# FITNESS TRACKER CLASS
class FitnessTracker:
   # Constructor
    def __init__(self):

        # Create data folder
        self.data_folder = "fitness_data"
        os.makedirs(self.data_folder, exist_ok=True)

        # File paths
        self.users_file = os.path.join(self.data_folder, "users.csv")
        self.activities_file = os.path.join(self.data_folder, "activities.csv")
        self.goals_file = os.path.join(self.data_folder, "goals.json")

        # Initialize files
        self.initialize_files()

        # Initialize Groq
        self.client = None
        api_key = os.getenv("GROQ_API_KEY")

        if api_key:
            try:
                self.client = Groq(api_key=api_key)
                print("✅ Groq AI Connected Successfully")
            except Exception as e:
                print("❌ Groq Connection Error:", e)
        else:
            print("⚠ GROQ_API_KEY not found")

    # Initialize Files
    def initialize_files(self):

        try:
            if not os.path.exists(self.users_file):
                pd.DataFrame(columns=[
                    "Name", "Age", "Gender", "Height_cm",
                    "Weight_kg", "BMI", "BMI_Category"
                ]).to_csv(self.users_file, index=False)

            if not os.path.exists(self.activities_file):
                pd.DataFrame(columns=[
                    "Date", "Name", "Activity", "Duration_min",
                    "Calories_Burned", "Steps", "Distance_km"
                ]).to_csv(self.activities_file, index=False)

            if not os.path.exists(self.goals_file):
                with open(self.goals_file, "w") as f:
                    json.dump({}, f, indent=4)

            print("✅ Data files initialized successfully")

        except Exception as e:
            print("❌ File Initialization Error:", e)

    # BMI CALCULATION
    def calculate_bmi(self, weight, height_cm):

        height_m = height_cm / 100
        bmi = weight / (height_m ** 2)

        if bmi < 18.5:
            category = "Underweight"
        elif bmi < 25:
            category = "Normal Weight"
        elif bmi < 30:
            category = "Overweight"
        else:
            category = "Obese"

        return round(bmi, 2), category
   # CREATE USER PROFILE
    def create_user_profile(self):

        print("\n========== CREATE USER PROFILE ==========")

        try:
            name = input("Enter Name: ").strip().title()
            age = int(input("Enter Age: "))
            gender = input("Enter Gender: ").strip().title()
            height = float(input("Enter Height (cm): "))
            weight = float(input("Enter Weight (kg): "))

            bmi, category = self.calculate_bmi(weight, height)

            with open(self.users_file, "a", newline="") as f:
                writer = csv.writer(f)
                writer.writerow([name, age, gender, height, weight, bmi, category])

            print("\n✅ USER PROFILE CREATED SUCCESSFULLY")

        except ValueError:
            print("❌ Invalid input.")

    # DISPLAY USERS
    def display_users(self):

        print("\n========== USER PROFILES ==========")

        try:
            df = pd.read_csv(self.users_file)
            print(df.to_string(index=False))
        except Exception as e:
            print("❌ Error:", e)

    # SET GOAL
    def set_goal(self):

        print("\n========== SET FITNESS GOAL ==========")

        try:
            name = input("Enter Name: ").strip().title()
            target_weight = float(input("Target Weight (kg): "))
            daily_steps = int(input("Daily Step Goal: "))
            weekly_minutes = int(input("Weekly Workout Minutes: "))

            with open(self.goals_file, "r") as f:
                goals = json.load(f)

            goals[name] = {
                "Target Weight": target_weight,
                "Daily Steps": daily_steps,
                "Weekly Workout Minutes": weekly_minutes
            }

            with open(self.goals_file, "w") as f:
                json.dump(goals, f, indent=4)

            print("\n✅ GOALS SAVED")

        except Exception as e:
            print("❌ Error:", e)


    # LOG ACTIVITY
    def log_activity(self):

        print("\n========== LOG ACTIVITY ==========")

        try:
            name = input("Enter Name: ").strip().title()
            activity = input("Activity: ").strip().title()
            duration = int(input("Duration (min): "))

            calories = duration * 5
            steps = duration * 100
            distance = round(duration * 0.08, 2)

            today = datetime.date.today().isoformat()

            with open(self.activities_file, "a", newline="") as f:
                writer = csv.writer(f)
                writer.writerow([today, name, activity, duration, calories, steps, distance])

            print("\n✅ ACTIVITY LOGGED")

        except Exception as e:
            print("❌ Error:", e)
 # VIEW HISTORY
    def view_activity_history(self):

        name = input("Enter Name: ").strip().title()

        df = pd.read_csv(self.activities_file)
        data = df[df["Name"] == name]

        if data.empty:
            print("❌ No data found")
        else:
            print(data)

    # REPORT
    def generate_report(self):

        name = input("Enter Name: ").strip().title()

        df = pd.read_csv(self.activities_file)
        data = df[df["Name"] == name]

        if data.empty:
            print("❌ No data")
            return

        print("\n===== REPORT =====")
        print("Workouts:", len(data))
        print("Calories:", data["Calories_Burned"].sum())
        print("Steps:", data["Steps"].sum())
        print("Distance:", round(data["Distance_km"].sum(), 2))
    # DELETE USER
    def delete_user(self):

        name = input("Enter Name: ").strip().title()

        df_users = pd.read_csv(self.users_file)
        df_users = df_users[df_users["Name"] != name]
        df_users.to_csv(self.users_file, index=False)

        df_act = pd.read_csv(self.activities_file)
        df_act = df_act[df_act["Name"] != name]
        df_act.to_csv(self.activities_file, index=False)

        with open(self.goals_file, "r") as f:
            goals = json.load(f)

        goals.pop(name, None)

        with open(self.goals_file, "w") as f:
            json.dump(goals, f, indent=4)

        print("✅ USER DELETED")
    # AI ASSISTANT
    def ai_assistant(self):

        if not self.client:
            print("❌ AI not enabled")
            return

        question = input("Ask: ")

        response = self.client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": "You are a fitness trainer"},
                {"role": "user", "content": question}
            ]
        )
        print(response.choices[0].message.content)
    # QUOTE
    def motivational_quote(self):

        quotes = [
            "Push yourself!",
            "Stay strong!",
            "Consistency wins!",
            "No excuses!",
            "Train hard!"
        ]

        print(random.choice(quotes))
      # MAIN MENU
    def run(self):

        while True:

            print("\n====== FITNESS SYSTEM ======")
            print("1. Create Profile")
            print("2. View Users")
            print("3. Set Goal")
            print("4. Log Activity")
            print("5. View History")
            print("6. Report")
            print("7. Delete User")
            print("8. Quote")
            print("9. AI Assistant")
            print("10. Exit")

            choice = input("Enter choice: ")

            if choice == "1":
                self.create_user_profile()
            elif choice == "2":
                self.display_users()
            elif choice == "3":
                self.set_goal()
            elif choice == "4":
                self.log_activity()
            elif choice == "5":
                self.view_activity_history()
            elif choice == "6":
                self.generate_report()
            elif choice == "7":
                self.delete_user()
            elif choice == "8":
                self.motivational_quote()
            elif choice == "9":
                self.ai_assistant()
            elif choice == "10":
                print("Goodbye 💪")
                break
            else:
                print("Invalid choice")
 # MAIN
if __name__ == "__main__":
    tracker = FitnessTracker()
    tracker.run()
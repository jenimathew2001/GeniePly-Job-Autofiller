
import json
from supabase import create_client, Client

url = "https://rhszylxaumugoiloyxgj.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJoc3p5bHhhdW11Z29pbG95eGdqIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDMwMTMwMzAsImV4cCI6MjA1ODU4OTAzMH0.Zf0VHHkvUjfAuuVU3pPzPgodqFsopk-STRyI9uVp40E"

supabase = create_client(url, key)

email = "new"  # Replace with an actual user email
structured_data = {"name": "EWW John Doe", "skills": ["Python", "Machine Learning"]}

response = (
    supabase.table("users")
    .update({"cv_json": structured_data})  # Ensure structured_data is a dictionary
    .eq("email", email)
    .execute()
)
print(response)
response = (
    supabase.table("users")
    .update({"cv_json": json.dumps(structured_data)})  # Convert to JSON string
    .eq("email", email)  # Ensure the email filter is correct
    .execute()
)

print(response)

response = (
    supabase.table("users")
    .update({"cv_json": json.dumps(structured_data)})
    .eq("email", email.lower())  # Convert email to lowercase
    .execute()
)
print(response)
from supabase import create_client, Client
import datetime

projectID = "https://onkdiwxfmnfhbcteyspf.supabase.co"
anon = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im9ua2Rpd3hmbW5maGJjdGV5c3BmIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Nzg3NzI5MzYsImV4cCI6MjA5NDM0ODkzNn0.Nuy9-sqdN6-Vceq4rrkm0dufDHtJfp4FoRu0epc20ww"

supabase: Client = create_client(projectID, anon)

def signup(name, email_id, phone, password):
    data = {
        "name": name,
        "email_id": email_id,
        "phone": phone,
        "password": password
    }
    supabase.table("users").insert(data).execute()

def login(name, password):
    response = supabase.table("users").select("name, password").eq("name", name).execute()
    if response.data:
        stored_password = response.data[0]["password"]
        if stored_password == password:
            return True, response.data[0]["name"]
    return False, None


def setAppointment(name, sport, date, timeStart, timeEnd):
    data = {
        "name": name,
        "sport": sport,
        "date": date, 
        "timeStart": timeStart,
        "timeEnd": timeEnd
    }
    supabase.table("sessions").insert(data).execute()


def find(my_name, sport, date, timeStart, timeEnd, min_overlap_hours=0.5):
    def convert_to_time(value):
        value = int(value)
        hours = value // 100
        minutes = value % 100
        return datetime.time(hours, minutes)

    input_start = convert_to_time(timeStart)
    input_end = convert_to_time(timeEnd)

    base_date = datetime.date.today()
    dt_input_start = datetime.datetime.combine(base_date, input_start)
    dt_input_end = datetime.datetime.combine(base_date, input_end)

    groups = []
   
    response = supabase.table("sessions").select("*")\
        .eq("sport", sport)\
        .eq("date", date)\
        .neq("name", my_name)\
        .execute()

    for row in response.data:
        user_start = convert_to_time(row["timeStart"])
        user_end = convert_to_time(row["timeEnd"])
        
        dt_user_start = datetime.datetime.combine(base_date, user_start)
        dt_user_end = datetime.datetime.combine(base_date, user_end)
        
        latest_start = max(dt_input_start, dt_user_start)
        earliest_end = min(dt_input_end, dt_user_end)
        
        if earliest_end > latest_start:
            overlap_hours = (earliest_end - latest_start).total_seconds() / 3600
            if overlap_hours >= min_overlap_hours:
                groups.append({
                    "name": row["name"], 
                    "overlap": round(overlap_hours, 2),
                    "start": row["timeStart"],
                    "end": row["timeEnd"],
                    "sport": row["sport"]
                })
    return groups

def getAppointments(name):

    response = supabase.table("sessions").select("*").eq("name", name).order("date").execute()
    return response.data

def getContactInfo(name):
   
    response = supabase.table("users").select("email_id, phone").eq("name", name).execute()
    if response.data:
        return response.data[0]
    return None
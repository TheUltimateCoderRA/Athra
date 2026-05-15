import streamlit as st
from helper import *
import datetime


if "user_name" not in st.session_state:
    st.session_state.user_name = None

col1, col2 = st.columns([3, 1])

with col1:
    st.title("ATHRA")
    st.caption("Find your next playing partner.")

with col2:
    # Try/Except prevents the app from crashing if the logo is missing
    try:
        st.image("logo.png", width=200) # Reduced width for better fit
    except:
        st.write("⚽") # Fallback emoji if logo.png isn't found


page  = st.sidebar.radio("Page", ["Registration", "Appointments", "Matches"])



if page == "Registration":
    loginT, signupT = st.tabs(["Login", "Signup"])
    
    with loginT:
        with st.form("Login"):
            name = st.text_input("Name")
            password = st.text_input("Password", type="password")
            if st.form_submit_button("Log In"):
                success, logged_in_name = login(name, password)
                if success:
                    st.session_state.user_name = logged_in_name
                    st.success(f"Welcome back, {st.session_state.user_name}!")
                else:
                    st.error("Invalid name or password.")

    with signupT:
        with st.form("Signup"):
            name = st.text_input("Name")
            emailID = st.text_input("Email ID")
            phone = st.text_input("Phone")
            password = st.text_input("Password", type="password")
            if st.form_submit_button("Sign Up"):
                signup(name, emailID, phone, password)
                st.success("Signup successful! Please log in.")

elif page == "Appointments":
    if st.session_state.user_name is not None:
        st.header(f"Schedule a Session, {st.session_state.user_name}")
        
        with st.form("Set Appointment"):
            sport_options = ["Football", "Basketball", "Tennis", "Cricket", "Badminton"]
            sport = st.selectbox("Select Sport", sport_options)
            
     
            d = st.date_input("Select Date", min_value=datetime.date.today())
            
            t_start = st.time_input("Start Time", value=datetime.time(10, 0))
            t_end = st.time_input("End Time", value=datetime.time(11, 0))
            
            if st.form_submit_button("Set Appointment"):
     
                date_int = d.year * 10000 + d.month * 100 + d.day 
     
                timeStart_int = t_start.hour * 100 + t_start.minute
                timeEnd_int = t_end.hour * 100 + t_end.minute
                
                setAppointment(st.session_state.user_name, sport, date_int, timeStart_int, timeEnd_int)
                st.success(f"Appointment for {sport} set!")

     
        st.divider()
        st.subheader("Your Upcoming Appointments")
        currentAppointments = getAppointments(st.session_state.user_name)
        
        if currentAppointments:
            for appt in currentAppointments:
                raw_d = str(appt['date'])
                readable_date = f"{raw_d[:4]}-{raw_d[4:6]}-{raw_d[6:]}"
                
                with st.container(border=True):
                    st.write(f"### {appt['sport']}")
                    st.write(f"📅 **Date:** {readable_date}")
                    st.write(f"⏰ **Time:** {appt['timeStart']} to {appt['timeEnd']}")
        else:
            st.write("No appointments found.")
    else:
        st.warning("Please go to the Registration page and Log In first.")

elif page == "Matches":
    if st.session_state.user_name is not None:
        st.header("Find Playing Partners")
        my_sessions = getAppointments(st.session_state.user_name)
        
        if not my_sessions:
            st.info("Set an appointment first to find matches!")
        else:
            st.write("Select one of your sessions to find partners:")
            for s in my_sessions:
                raw_d = str(s['date'])
                readable_date = f"{raw_d[:4]}-{raw_d[4:6]}-{raw_d[6:]}"
                
                with st.expander(f"{s['sport']} on {readable_date}"):
                    if st.button(f"Search for {s['sport']} partners", key=f"btn_{s['id']}"):
                        matches = find(st.session_state.user_name, s['sport'], s['date'], s['timeStart'], s['timeEnd'])
                        
                        if matches:
                            st.write("### Partners found:")
                            for m in matches:
                                with st.expander(f"{m['name']}"):
                                    contact_info = getContactInfo(m['name'])
                                    if contact_info:
                                        st.write(f"📧 Email: {contact_info['email_id']}")
                                        st.write(f"📞 Phone: {contact_info['phone']}")

                                        st.write(f"**Sport:** {m['sport']}")
                                        st.write(f"**Date:** {readable_date}")
                                        st.write(f"**Time:** {m['start']} to {m['end']}")
                                    else:
                                        st.write("No contact info available.")
                        else:
                            st.error("No matches found for this session yet.")
    else:
        st.warning("Please log in first.")
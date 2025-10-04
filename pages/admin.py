import streamlit as st
import json, os
import smtplib
from email.message import EmailMessage 
import calendar
from datetime import datetime, timedelta

# --- Config ---
st.set_page_config(page_title="Admin - Manage Bookings", layout="wide")

SENDER_EMAIL = st.secrets["SENDER_EMAIL"]
APP_PASSWORD = st.secrets["APP_PASSWORD"]
ADMIN_PASSWORD = st.secrets["ADMIN_PASSWORD"]  # add this in your secrets.toml

BOOKINGS_FILE = "bookings.json"

# --- Helper functions ---
def load_bookings():
    if os.path.exists(BOOKINGS_FILE):
        with open(BOOKINGS_FILE, "r") as f:
            return json.load(f)
    return []

def save_bookings(bookings):
    with open(BOOKINGS_FILE, "w") as f:
        json.dump(bookings, f, indent=2)

def send_email(to_email, subject, content):
    msg = EmailMessage()
    msg.set_content(content)
    msg['Subject'] = subject
    msg['From'] = SENDER_EMAIL
    msg['To'] = to_email
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(SENDER_EMAIL, APP_PASSWORD)
            smtp.send_message(msg)
        st.success(f"Email sent to {to_email}")
    except Exception as e:
        st.error(f"Error sending email: {e}")

# --- Login system ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🔒 Admin Login")
    password_input = st.text_input("Enter Admin Password", type="password")
    if st.button("Login"):
        if password_input == ADMIN_PASSWORD:
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.error("Incorrect password.")
    st.stop()

# --- Admin Dashboard ---
st.title("🛠️ Admin - Manage Bookings")

bookings = load_bookings()
pending = [b for b in bookings if b["status"] == "pending"]
approved = [b for b in bookings if b["status"] == "approved"]

st.header("Pending Booking Requests")
if not pending:
    st.info("No pending booking requests 🎉")
else:
    for idx, booking in enumerate(pending):
        with st.expander(f"{booking['date']} - {booking['name']}"):
            st.write(f"📧 Email: {booking['email']}")
            st.write(f"📞 Phone: {booking['phone']}")
            st.write(f"📍 Location: {booking['location']}")
            st.write(f"👥 Workers: {booking['total_workers']} "
                     f"(Painters: {booking['face_painters']}, "
                     f"Balloons: {booking['balloon_twisters']}, "
                     f"Glitter: {booking['glitter_tattoo_artists']})")
            st.write(f"🕒 Time: {booking['start_time']} - {booking['end_time']}")
            st.write(f"💰 Total: ${booking['total_price']:.2f}, Deposit: ${booking['deposit']:.2f}")
            st.write(f" Status: {booking['status']}")
            

            #text input for workers names
            worker_input = st.text_input(
                f"Assign worker(s) for {booking['name']} (comma-seperated",
                key=f"workers_{idx}"
            )
            
            col1, col2, col3 = st.columns(3)
            if col1.button("✅ Approve", key=f"approve_{idx}"):
                #split input by commas and strip extra spaces
                assigned_workers = [w.strip() for w in worker_input.split(",") if w.strip()]
                booking["workers_assiggned"] = assigned_workers
                booking["status"] = "approved"
                save_bookings(bookings)
                
                send_email(
                    booking["email"],
                    "Booking Approved",
                    f"""
                    Hi {booking['name']},\n\nYour booking has been APPROVED! Please pay your deposit to confirm your booking!
                    The remaining price total will be due the day of the scheduled event.
                    
                    ---Payment methods--- 
                    PayPal: @LadyLady123
                    Venmo: @kasspulliam
                    Cash App: $kass1234567890
                    Zelle: (901)674-0885
                    
                    ---Booking Info---
                    date: {booking['date']}
                    start time: {booking['start_time']}
                    end time: {booking['end_time']}
                    location: {booking['location']}
                    face painters: {booking['face_painters']}
                    balloon twisters: {booking['balloon_twisters']}
                    glitter tattoo artists: {booking['glitter_tattoo_artists']}
                    hours: {booking['hours']}
                    total price: ${booking['total_price']}
                    deposit: ${booking['deposit']}
                    
                    Please reach out to pixiepoppartiess@gmail.com or reply to this email if you have any questions!
                    """
                )
                st.rerun()

        if col2.button("❌ Deny", key=f"deny_{idx}"):
            booking["status"] = "denied"
            save_bookings(bookings)
            send_email(
                booking["email"],
                "Booking Denied",
                f"""
                Hi {booking['name']},\n\nUnfortunately, we cannot accommodate your booking request at this time as we are unavailable on that date/time.
                 ---Booking Info---
                    date: {booking['date']}
                    start time: {booking['start_time']}
                    end time: {booking['end_time']}
                    location: {booking['location']}
                    face painters: {booking['face_painters']}
                    balloon twisters: {booking['balloon_twisters']}
                    glitter tattoo artists: {booking['glitter_tattoo_artists']}
                    hours: {booking['hours']}
                    total price: ${booking['total_price']}
                    deposit: ${booking['deposit']}
                    """
             )
            st.rerun()

        if col3.button("Delete", key=f"delete_{idx}"):
            #remove the booking from the list completely 
            bookings.pop(idx)
            save_bookings(bookings)
            st.success("Booking deleted!")
            st.rerun()

# --- Calendar view for approved bookings ---
st.header("📅 Worker Schedule")
if "month_offset" not in st.session_state:
    st.session_state.month_offset = 0

col1, col2, col3 = st.columns([1,2,1])
with col1:
    if st.button("<-- previous month"):
        st.session_state.month_offset -= 1
with col3:
    if st.button("Next Month -->"):
        st.session_state.month_offset += 1 


#---calendar---
today = datetime.today()
first_day_of_month = datetime(today.year, today.month, 1) + timedelta(days=st.session_state.month_offset*30)
year = first_day_of_month.year
month = first_day_of_month.month
month_name = calendar.month_name[month]
st.subheader(f"{month_name} {year}")

month_calendar = calendar.monthcalendar(year, month)
for week in month_calendar:
    cols = st.columns(7)
    for i, day in enumerate(week):
        if day == 0:
            cols[i].write("")
        else:
            day_str = f"{year}-{month:02d}-{day:02d}"
            day_events = [b for b in approved if b["date"] == day_str]
            #highlight today 
            if day == today.day and month == today.month and year == today.year:
                day_label = f"<div style='background-color:pink; text-align:center; border-radius:5px;'>{day}</div>"
                cols[i].markdown(day_label, unsafe_allow_html=True)

            # Calendar button for the day
            if day == today.day and month == today.month and year == today.year:
                day_label = f"<div style='background-color:pink; text-align:center; border-radius:5px;'>{day}</div>"
                cols[i].markdown(day_label, unsafe_allow_html=True)
                st.write(f"### Events on {day_str}")
                    for event_idx, event in enumerate(day_events):
                        with st.expander(f"{event['start_time']} - {event['end_time']}: {event['name']}"):
                            st.write(f"📍 Location: {event['location']}")
                            st.write(f"👥 Workers: {', '.join(event.get('workers_assigned', []))}")
                            st.write(f"💰 Total: ${event['total_price']:.2f}, Deposit: ${event['deposit']:.2f}")
                            st.write(f"📌 Status: {event['status']}")

                            col1, col2 = st.columns(2)
                            if col1.button("🗑️ Delete", key=f"delete_{day}_{event_idx}"):
                                main_idx = next((i for i, b in enumerate(bookings) if b == event), None)
                                if main_idx is not None:
                                    bookings.pop(main_idx)
                                    save_bookings(bookings)
                                    st.success(f"Deleted {event['name']} on {event['date']}")
                                    st.rerun()
            else:
                cols[i].button(f"{day}", key=f"day_{day}_empty")

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
        #indent marker for button 
        if col3.button("🗑️ Delete", key=f"delete_pending_{idx}"):
            bookings.pop(idx)
            save_bookings(bookings)
            st.success(f"Deleted pending booking {booking['name']} on {booking['date']}")
            st.rerun()
        
        if main_idx is not None:
            bookings.pop(main_idx)
            save_bookings(bookings)
            st.success(f"Deleted {event['name']} on {event['date']}")
            st.rerun()

# --- Calendar view for approved bookings ---
st.header("📅 Schedule")
# ensure month_offset exists
if "month_offset" not in st.session_state:
    st.session_state["month_offset"] = 0

# navigation buttons (previous / next month)
nav_col1, nav_col2, nav_col3 = st.columns([1,6,1])
with nav_col1:
    if st.button("⬅ Previous Month"):
        st.session_state.month_offset -= 1
with nav_col3:
    if st.button("Next Month ➡"):
        st.session_state.month_offset += 1

# compute month/year correctly from offset
today = datetime.today()
offset = st.session_state.get("month_offset", 0)
# compute year/month by moving months, not by adding 30 days
month = (today.month - 1 + offset) % 12 + 1
year = today.year + ((today.month - 1 + offset) // 12)
month_name = calendar.month_name[month]
st.subheader(f"{month_name} {year}")

# recompute approved bookings from the master bookings list (in case it changed)
bookings = load_bookings()
approved = [b for b in bookings if b.get("status") == "approved"]

month_calendar = calendar.monthcalendar(year, month)

for week in month_calendar:
    cols = st.columns(7)
    for i, day in enumerate(week):
        if day == 0:
            cols[i].write("")  # empty cell
            continue

        # build day string like "2025-10-03"
        day_str = f"{year}-{month:02d}-{day:02d}"
        day_events = [b for b in approved if b.get("date") == day_str]

        # render day number, highlight today in pink
        is_today = (day == today.day and month == today.month and year == today.year)
        if is_today:
            cols[i].markdown(
                f"<div style='background-color:pink; text-align:center; border-radius:6px; padding:6px;'>{day}</div>",
                unsafe_allow_html=True
            )
        else:
            cols[i].write(f"{day}")

        # if there are events, show a small button that opens the day's events
        if day_events:
            label = f"{len(day_events)} event{'s' if len(day_events) > 1 else ''}"
            # clicking this renders the event list below the calendar (Streamlit will rerun)
            if cols[i].button(label, key=f"day_{year}_{month}_{day}"):
                st.write(f"### Events on {day_str}")
                for evt_idx, evt in enumerate(day_events):
                    with st.expander(f"{evt.get('start_time', '')} - {evt.get('end_time','')}: {evt.get('name','(no name)')}"):
                        st.write(f"📍 Location: {evt.get('location','')}")
                        st.write(f"👥 Workers: {', '.join(evt.get('workers_assigned', [])) if evt.get('workers_assigned') else 'None assigned'}")
                        st.write(f"💰 Total: ${evt.get('total_price',0):.2f}, Deposit: ${evt.get('deposit',0):.2f}")
                        st.write(f"📌 Status: {evt.get('status','')}")
                        st.write("---")

                        # Reliable delete: find booking by a set of stable fields (fallback to equality)
                        def find_booking_index(target):
                            # prefer unique id if present
                            if target.get("id"):
                                for idx, b in enumerate(bookings):
                                    if b.get("id") == target.get("id"):
                                        return idx
                            # otherwise match on combination of fields (date, start_time, email, name)
                            for idx, b in enumerate(bookings):
                                if (
                                    b.get("date") == target.get("date") and
                                    b.get("start_time") == target.get("start_time") and
                                    b.get("email") == target.get("email") and
                                    b.get("name") == target.get("name")
                                ):
                                    return idx
                            # last resort: exact dict match
                            for idx, b in enumerate(bookings):
                                if b == target:
                                    return idx
                            return None

                        col_del, col_blank = st.columns([1,3])
                        if col_del.button("🗑️ Delete", key=f"delete_{day}_{evt_idx}"):
                            main_idx = find_booking_index(evt)
                            if main_idx is not None:
                                bookings.pop(main_idx)
                                save_bookings(bookings)
                                st.success(f"Deleted {evt.get('name','event')} on {evt.get('date')}")
                                st.rerun()
                            else:
                                st.error("Could not find the booking to delete (it may have changed).")
        else:
            cols[i].button("", key=f"day_{year}_{month}_{day}_empty")  # placeholder for alignment

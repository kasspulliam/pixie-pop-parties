import streamlit as st
import json, os
import smtplib
from email.message import EmailMessage 

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

            #text input for workers names
            worker_input = st.text_input(
                f"Assign worker(s) for {booking['name']} (comma-seperated",
                key=f"workers_{idx}"
            )
            col1, col2 = st.columns(2)
            if col1.button("✅ Approve", key=f"approve_{idx}"):
                #split input by commas and strip extra spaces
                assigned_workers = [name.strip() for name in worker_input.split(",") if name.strip()]
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

# --- Calendar view for approved bookings ---
st.header("📅 Worker Schedule")

# Collect all approved bookings
approved_bookings = [b for b in bookings if b["status"] == "approved"]

if not approved_bookings:
    st.info("No approved bookings yet.")
else:
    # Build a dictionary mapping worker -> list of gigs
    schedule = {}
    for booking in approved_bookings:
        workers = booking.get("workers_assiggned", [])  # make sure this key matches what you used above
        for worker in workers:
            if worker not in schedule:
                schedule[worker] = []
            schedule[worker].append({
                "date": booking["date"],
                "time": f"{booking['start_time']} - {booking['end_time']}",
                "customer": booking["name"],
                "location": booking["location"]
            })

    # Display schedule
    for worker, gigs in schedule.items():
        with st.expander(f"{worker} ({len(gigs)} gigs)"):
            # Sort gigs by date
            gigs_sorted = sorted(gigs, key=lambda x: x["date"])
            for gig in gigs_sorted:
                st.write(f"📅 {gig['date']} | 🕒 {gig['time']} | 👤 {gig['customer']} | 📍 {gig['location']}")

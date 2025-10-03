import streamlit as st
import os
import json
import smtplib
from email.message import EmailMessage
from datetime import datetime

# ---------- CONFIG ----------
ADMIN_PASSWORD = st.secrets["ADMIN_PASSWORD"]  # store your password in Streamlit secrets
SENDER_EMAIL = st.secrets["SENDER_EMAIL"]
APP_PASSWORD = st.secrets["APP_PASSWORD"]

BOOKINGS_FILE = "bookings.json"  # store pending bookings

# ---------- HELPER FUNCTIONS ----------
def send_email(to_email, subject, content):
    msg = EmailMessage()
    msg.set_content(content)
    msg["Subject"] = subject
    msg["From"] = SENDER_EMAIL
    msg["To"] = to_email

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(SENDER_EMAIL, APP_PASSWORD)
            smtp.send_message(msg)
    except Exception as e:
        st.error(f"Error sending email: {e}")


def load_bookings():
    if os.path.exists(BOOKINGS_FILE):
        with open(BOOKINGS_FILE, "r") as f:
            return json.load(f)
    return []


def save_bookings(bookings):
    with open(BOOKINGS_FILE, "w") as f:
        json.dump(bookings, f, indent=4)


# ---------- PAGE ----------
st.set_page_config(page_title="Pixie Pop Admin", layout="wide")
st.title("🗓️ Pixie Pop Admin Panel")

# Password check
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    pwd = st.text_input("Enter admin password:", type="password")
    if st.button("Login"):
        if pwd == ADMIN_PASSWORD:
            st.session_state.authenticated = True
            st.success("✅ Access granted!")
        else:
            st.error("❌ Incorrect password.")
else:
    st.info("You are logged in as admin.")

    # Load pending bookings
    bookings = load_bookings()
    if not bookings:
        st.warning("No pending bookings.")
    else:
        st.header("Pending Bookings")
        for i, booking in enumerate(bookings):
            st.subheader(f"{booking['customer_firstname']} {booking['customer_lastname']} — {booking['event_date']}")
            st.write(f"Email: {booking['customer_email']}")
            st.write(f"Phone: {booking['customer_phone']}")
            st.write(f"Location: {booking['location']}")
            st.write(f"Time: {booking['start_time']} - {booking['end_time']}")
            st.write(f"Workers — Face Painters: {booking['num_painters']}, Balloon Twisters: {booking['num_balloon']}, Glitter: {booking['num_glitter']}")
            st.write(f"Total: ${booking['total_price']:.2f}, Deposit: ${booking['deposit']:.2f}")

            col1, col2 = st.columns(2)
            with col1:
                if st.button(f"✅ Approve {i}"):
                    # Send confirmation email to customer
                    content = f"""
                    Hi {booking['customer_firstname']},

                    Your event on {booking['event_date']} has been APPROVED!
                    Total: ${booking['total_price']:.2f}
                    Deposit required: ${booking['deposit']:.2f}

                    Please pay your deposit to secure the booking.

                    Thanks,
                    Pixie Pop Parties
                    """
                    send_email(booking["customer_email"], "Pixie Pop Parties Booking Approved", content)

                    # Remove booking from pending list
                    bookings.pop(i)
                    save_bookings(bookings)
                    st.success("Booking approved and email sent!")
                    st.experimental_rerun()

            with col2:
                if st.button(f"❌ Deny {i}"):
                    # Send denial email to customer
                    content = f"""
                    Hi {booking['customer_firstname']},

                    Unfortunately, we are not available for your requested date and time.
                    You may submit another booking request for a different date.

                    Thanks,
                    Pixie Pop Parties
                    """
                    send_email(booking["customer_email"], "Pixie Pop Parties Booking Denied", content)

                    # Remove booking from pending list
                    bookings.pop(i)
                    save_bookings(bookings)
                    st.success("Booking denied and email sent!")
                    st.experimental_rerun()

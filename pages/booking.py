import streamlit as st
from datetime import datetime, date, time, timedelta
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

#if the user clicked the button on home page 
if "page" in st.session_state and st.session_state.page == "booking":
    st.switch_page("pages/booking.py")

# Page configuration
st.set_page_config(page_title="Pixie Pop Parties Booking", page_icon="🗓️", layout="wide")

st.title("📅 Book Your Event")
st.write("Fill out the form below to request your booking.")

#---EMAIL SETUP----
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL")

def send_email(to_email, subject, content):
    message = Mail(
        from_email=SENDER_EMAIL,
        to_emails=to_email,
        subject=subject,
        plain_text_content=content
    )
    try:
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        sg.send(message)
    except Exception as e:
        st.error(f"Error sending email: {e}")

# ----- Event Details -----
st.header("Event Details")

event_date = st.date_input("Event Date", min_value=date.today())
start_time = st.time_input("Start Time", value=time(10,0))
end_time = st.time_input("End Time", value=time(12,0))
location = st.text_input("Event Address")
event_desc = st.text_input("Please briefly describe the type of event")

# ----- Services -----
st.header("Services")

num_painters = st.number_input("Number of Face Painters", min_value=0, max_value=5, value=1, step=1)
num_balloon = st.number_input("Number of Balloon Twisters", min_value=0, max_value=5, value=0, step=1)
num_glitter = st.number_input("Number of Glitter Tattoo Artists", min_value=0, max_value=5, value=0, step=1)

# ----- Contact Info -----
st.header("Contact Information")

customer_email = st.text_input("Email")
customer_phone = st.text_input("Phone Number")
customer_firstname = st.text_input("First name")
customer_lastname = st.text_input("Last name")

# ----- Price Calculation -----
st.header("Price Summary")

# Calculate total number of workers and hours
num_workers = num_painters + num_balloon
duration_hours = (datetime.combine(date.today(), end_time) - datetime.combine(date.today(), start_time)).seconds / 3600
#time logic
if duration_hours <= 0:
    st.error("End time must be after start time.")
else:
    #proceeds with total price calulation 

hourly_rate = 125
hourly_glitter = 90

total_price = hourly_rate * num_workers * duration_hours + (num_glitter * duration_hours * hourly_glitter)
deposit = total_price * 0.4

st.markdown(f"**Total Price:** ${total_price:.2f}")
st.markdown(f"**Deposit Required:** ${deposit:.2f}")

# ----- Submit -----
if st.button("Submit Booking Request"):
    if not customer_email or not customer_phone or not customer_firstname or not customer_lastname or num_workers == 0:
        st.error("Please fill out all required fields and select at least one worker.")
    else:
        st.success(f"🎉 Thank you! Your booking request for {event_date} from {start_time} to {end_time} has been received.")

        #email content for admin
        admin_content = f"""
        NEW BOOKING REQUEST

        Name: {customer_firstname} {customer_lastname}
        Email: {customer_email}
        Phone: {customer_phone}
        Date: {event_date}
        Time: {start_time} - {end_time}
        Location: {location}
        Face painters: {num_painters}
        Balloon twisters: {num_balloon}
        glitter tattoo artists: {num_glitter}
        total workers: {num_workers}
        hours: {duration_hours}
        total price: ${total_price:.2f}
        deposit: ${deposit:.2f}

        to approve, reply with: APPROVE {customer_email}
        to deny, reply with: DENY {customer_email}
        """

        send_email(ADMIN_EMAIL, 'New booking request', admin_content)
        st.info('Your request has been sent to the admin for approval. You will receive an email once it is reviewed.')








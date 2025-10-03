import streamlit as st 




#page configuration 
st.set_page_config(page_title="Pixie Pop Parties", page_icon="✨", layout="wide")

#-----header section-----
st.markdown(
    """
    <h1 style="
        color: #FFD700;
        text-align: center;
        font-size: 60px;
        border: 4px solid #E6B800;
        padding: 15px;
        border-radius: 12px;
        background-color: #fffbea;
    ">
    ✨ Welcome to Pixie Pop Parties!
    </h1>
    """,
    unsafe_allow_html=True
)
scol1, col2, col3 = st.columns([1,2,1])  # Create 3 columns, middle is widest

with col2:  
    st.image("images/pixie_pop_parties_full_logo.jpg", width=750)  
    st.markdown("<p style='text-align:center;'><em>Bringing smiles to every event!</em></p>", unsafe_allow_html=True)

#----about section------
st.header("✨About Us✨")
st.markdown("""
<p style='font-size:20px; line-height:1.5;'>
At Pixie Pop Parties, we specialize in Face Painting and Balloon Twisting to make your events magical!
From birthdays to festivals, our team brings color, fun, and joy. Our goal is to make every event
unforgettable for kids and adults alike!
</p>
""", unsafe_allow_html=True)

#-----gallery section-----
st.header("🌌💫Our Gallery")

#list of pictures 
image_files = [
    "images/balloon_parrot.jpg", "images/balloon_spider.jpg", "images/big_balloon_unicorn.jpg", "images/face_paint_darth_maul.jpg",
    "images/face_paint_mermaid.jpg", "images/face_paint_rose_front_face.JPG", "images/face_paint_rose_side face.JPG", "images/face_paint_unicorn.jpg",
    "images/hulk_face_paint.jpg", "images/rideable_balloon_unicorn.jpg", "images/turtle_paint.jpg", "images/stitch_balloon.jpg"
]

#display images in rows of 3
for i in range(0, len(image_files), 3):
    cols = st.columns(3)
    for j, col in enumerate(cols):
        if i + j < len(image_files):
            col.image(image_files[i + j], use_container_width=True)

#------booking instrutions------
st.header("Where to go to Book!")
st.write(
    """
    To find the booking page, look at the top left of your screen. 
    You should see two arrows. Click the two arrows and it will open the sidebar.
    You should see a list of pages. From the list click "booking". Then just fill out your booking form!
    """
)

#-------booking and payment info------
st.header("How Booking and Payment Works")
st.write("""
1. Submit a booking request: choose your event date, location, start/end times, and number/type of workers.
2. Approval email & text: we will review your request aand confirm availability!
3. Deposit to secure your event: Once approved, you will recieve a confirmation email with payment links, total cost, and the cost of the deposit. 
4. Event day!: We will arrive to the given location 30 minutes (or more depending on the event) before the selected start time to set up. The remaining balance of the total is due the day of the event. 
5. Sit back and enjoy the party! ✨🪄🥳🦄🎨🎈

""")

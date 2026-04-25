# --- UPDATED ACTIVITY & CATEGORY SECTIONS ---
# Find this section in your sidebar code:
with st.expander("➕ Add New Vehicle"):
    vy = st.selectbox("Year", range(2027, 1980, -1))
    vma = st.text_input("Make")
    vmo = st.text_input("Model")
    # UPDATED CATEGORIES
    vct = st.radio("Category", ["Car/SUV", "Truck", "Motorcycle", "E-Bike"]) 

# Find this section in your main dashboard code:
with st.container(border=True):
    # UPDATED ACTIVITIES
    l_t = st.selectbox("Activity", [
        "Oil Change", "Repair", "Diagnostic", 
        "Audio/Electrical", "Battery Service", 
        "Tire Service", "3D Printed Part", "Legal"
    ])

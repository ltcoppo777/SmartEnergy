import streamlit as st
from optimizer import optimize_schedule

st.title("⚡ SmartEnergy+ Optimizer")
st.write("Plan your appliance usage to save money and energy!")

# Upload prices CSV
prices_file = st.file_uploader("Upload hourly price data (CSV with 'price' column)", type=["csv"])

# Example appliance setup
default_appliances = [
    {"name": "Washer", "power": 0.5, "duration": 2},
    {"name": "Dryer", "power": 1.0, "duration": 1},
    {"name": "Dishwasher", "power": 1.2, "duration": 2}
]

# Show example
st.write("### Example appliances")
st.dataframe(default_appliances)

# Run optimizer
if prices_file is not None:
    st.write("Running optimization...")
    schedule = optimize_schedule(prices_file, default_appliances)
    st.success("Optimal Schedule:")
    st.json(schedule)
else:
    st.info("Please upload a price data CSV to start optimization.")

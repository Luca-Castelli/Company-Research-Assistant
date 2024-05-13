import streamlit as st

from main import (
    run_agent,  # Ensure main.py is in the same directory or adjust the import path accordingly
)

# Streamlit page configuration
st.set_page_config(page_title="Company Research Tool", layout="wide")

# Title of the app
st.title("Company Research Assistant")

# Text input for user query
user_query = st.text_input("Enter your question about a company:")

# Button to trigger the analysis
if st.button("Analyze"):
    if user_query:
        # Call the function from main.py
        response = run_agent(user_query)
        # Display the result
        st.markdown(response, unsafe_allow_html=True)
    else:
        st.error("Please enter a question to proceed.")

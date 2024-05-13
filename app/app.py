import streamlit as st

from main import run_agent

st.set_page_config(page_title="Company Research", layout="wide")

st.title("Company Research Assistant")

user_query = st.text_input("Enter a company website URL:")

if st.button("Analyze"):
    if user_query:
        response = run_agent(user_query)
        st.markdown(response, unsafe_allow_html=True)
    else:
        st.error("Please enter a question to proceed.")

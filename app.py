import requests
import streamlit as st

API_URL = "http://localhost:8000/api"

if "history" not in st.session_state:
    st.session_state.history = []

st.title("Support Buddy")

case_description = st.text_area("Case Description")
investigation_steps = st.text_area("Investigation Steps")

if st.button("Suggest Next Steps"):
    try:
        with st.spinner("Generating suggestions..."):
            response = requests.post(
                f"{API_URL}/suggest",
                json={
                    "case_description": case_description,
                    "investigation_steps": investigation_steps,
                },
            )
            response.raise_for_status()
            suggestions = response.json()["suggestions"]

            st.session_state.history.append({
                "type": "suggestion",
                "case": case_description,
                "response": suggestions,
            })

        st.subheader("Suggested Next Steps")
        st.markdown(suggestions)

    except Exception as e:
        st.error(f"Error generating suggestions: {e}")

customer_message = st.text_area("Customer Message")

if st.button("Improve Message"):
    try:
        with st.spinner("Improving message..."):
            response = requests.post(
                f"{API_URL}/improve",
                json={
                    "customer_message": customer_message,
                    "case_description": case_description,
                    "investigation_steps": investigation_steps,
                },
            )
            response.raise_for_status()
            improved_message = response.json()["improved_message"]

            st.session_state.history.append({
                "type": "message",
                "case": case_description,
                "response": improved_message,
            })

        st.subheader("Improved Customer Message")
        st.markdown(improved_message)

    except Exception as e:
        st.error(f"Error improving message: {e}")

st.divider()
st.header("History")

for item in st.session_state.history:
    st.subheader(item["type"])
    st.write("Case:")
    st.write(item["case"])
    st.write("Response:")
    st.markdown(item["response"])

st.divider()
st.header("Saved Cases")

try:
    cases = requests.get(f"{API_URL}/cases").json()
    for case in cases:
        st.subheader(f"Case #{case['id']}")
        st.write(case["case_description"])
        with st.expander("Investigation Steps"):
            st.write(case["investigation_steps"])
        with st.expander("AI Response"):
            st.write(case["ai_response"])
except Exception as e:
    st.error(f"Could not load saved cases: {e}")
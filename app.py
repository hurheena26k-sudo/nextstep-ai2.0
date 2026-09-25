import streamlit as st

st.set_page_config(
    page_title="NextStep AI",
    page_icon="🧭",
    layout="wide"
)

# Sidebar
with st.sidebar:
    st.title("🧭 NextStep AI")
    st.write("Public Services Assistant")

    st.divider()

    if st.button("➕ New Conversation", use_container_width=True):
        st.rerun()

    st.subheader("Previous Conversations")
    st.write("No conversations yet.")

# Main area
st.title("🧭 NextStep AI")
st.subheader("How can I help you today?")

user_message = st.text_input(
    "Tell me what you need help with",
    placeholder="Example: I want to report a streetlight problem..."
)

if user_message:
    st.info("Your request will be processed by NextStep AI.")

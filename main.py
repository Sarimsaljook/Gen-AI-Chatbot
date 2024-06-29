import streamlit as st
import requests

st.title("Sarim Bot")

language = st.sidebar.selectbox("Language", ["English", "Spanish"])
uploaded_file = st.sidebar.file_uploader("Upload a PDF file", type="pdf")

if uploaded_file is not None:
    files = {'file': uploaded_file.getvalue()}
    response = requests.post("http://localhost:8000/upload_pdf", files=files)
    knowledge_base = response.json()["knowledge_base"]
else:
    knowledge_base = ""

freeform_text = st.sidebar.text_area(label="What is your question?", max_chars=100, key="freeform_text_input")

if st.sidebar.button("Ask Question"):
    if freeform_text:
        query = {
            "language": language,
            "freeform_text": freeform_text,
            "knowledge_base": knowledge_base
        }
        response = requests.post("http://localhost:8000/ask", json=query)
        result = response.json()["response"]
        st.markdown(f"""
        <div style='padding: 10px; background-color: #262730; border-radius: 10px; margin: 10px 0;'>
            {result}
        </div>
        """, unsafe_allow_html=True)
        freeform_text = ""

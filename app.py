import streamlit as st
from utils.institution import get_institution_info
from utils.ipc_bot import ipc_qa
from utils.doc_qa import setup_doc_qa
import tempfile

# --- Configuration ---
PAGE_TITLE = "Gen AI"
PAGE_ICON = "⚖️"
LAYOUT = "wide"

# --- Page Setup ---
st.set_page_config(page_title=PAGE_TITLE, page_icon=PAGE_ICON, layout=LAYOUT)

# --- Custom CSS Styling ---
st.markdown("""
    <style>
        body {
            background-color: #f7f9fc;
            color: #1f2937;
            font-family: 'Segoe UI', sans-serif;
        }
        .main {
            background-color: #ffffff;
            padding: 30px;
            border-radius: 12px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
            margin-top: 20px;
        }
        h1, h2, h3 {
            color: #003366;
        }
        .stButton>button {
            background-color: #003366;
            color: white;
            border-radius: 8px;
            padding: 0.75em 1.5em;
            font-size: 16px;
            border: none;
        }
        .stButton>button:hover {
            background-color: #00509e;
            color: #fff;
        }
        .stTextInput>div>div>input {
            border-radius: 6px;
            padding: 10px;
            border: 1px solid #ced4da;
        }
        .css-1aumxhk {
            background-color: #e8f0fe;
        }
    </style>
""", unsafe_allow_html=True)

# --- Persistent Tab State ---
if "active_tab" not in st.session_state:
    st.session_state.active_tab = "Academia Insight"

# --- Top Navigation Bar ---
def render_top_nav():
    st.markdown("### ⚖️ Gen AI Assistant", unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🏛 Academia Insight", use_container_width=True):
            st.session_state.active_tab = "Academia Insight"
    with col2:
        if st.button("⚖️ IPC Chatbot", use_container_width=True):
            st.session_state.active_tab = "IPC Chatbot"
    with col3:
        if st.button("📄 Document QA", use_container_width=True):
            st.session_state.active_tab = "Document QA"

# --- Main Content ---
def main():
    render_top_nav()

    with st.container():
        if st.session_state.active_tab == "Academia Insight":
            st.header("🏛 Institution Information Finder")
            institution_name = st.text_input("Enter Institution Name")

            if st.button("Fetch Details"):
                with st.spinner("Searching..."):
                    try:
                        details = get_institution_info(institution_name)
                        st.subheader(details.name)
                        st.write(f"**Founder:** {details.founder}")
                        st.write(f"**Year Founded:** {details.founded_year}")
                        st.markdown("**Branches:**")
                        for branch in details.branches:
                            st.markdown(f"- {branch}")
                        employees = details.employees
                        if isinstance(employees, (int, float)):
                            st.write(f"**Employees:** {employees:,}")
                        else:
                            st.write(f"**Employees:** {employees}")

                        st.markdown("**Summary:**")
                        st.info(details.summary)
                    except Exception as e:
                        st.error(f"Error: {str(e)}")

        elif st.session_state.active_tab == "IPC Chatbot":
            st.header("⚖️ Indian Penal Code Chatbot")
            ipc_question = st.text_input("Ask about IPC")

            if st.button("Get Answer"):
                with st.spinner("Searching IPC..."):
                    try:
                        answer = ipc_qa(ipc_question)
                        st.success(answer)
                    except Exception as e:
                        st.error(f"Error: {str(e)}")

        elif st.session_state.active_tab == "Document QA":
            st.header("📄 Document Question Answering")
            uploaded_file = st.file_uploader("Upload PDF/TXT/DOCX", type=["pdf", "txt", "docx"])

            if uploaded_file:
                with tempfile.NamedTemporaryFile(delete=False) as tmp:
                    tmp.write(uploaded_file.read())
                    file_path = tmp.name

                doc_qa = setup_doc_qa(file_path, file_type=uploaded_file.name.split(".")[-1])

                doc_question = st.text_input("Ask about the document")
                if st.button("Search Document"):
                    with st.spinner("Analyzing..."):
                        try:
                            answer = doc_qa.run(doc_question)
                            st.success(answer)
                        except Exception as e:
                            st.error(f"Error: {str(e)}")

if __name__ == "__main__":
    main()

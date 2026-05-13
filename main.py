
import streamlit as st

USERNAME = "admin"
PASSWORD = "admin123"

def login_page():
    st.set_page_config(page_title="CiscoIQ", layout="wide")

    st.markdown("""
    <style>
    .login-wrap{
        max-width:420px;
        margin:120px auto;
        padding:36px;
        border-radius:20px;
        background:white;
        border:1px solid #e5e7eb;
        box-shadow:0 10px 24px rgba(0,0,0,.05);
    }
    .title{
        font-size:32px;
        font-weight:900;
        text-align:center;
        margin-bottom:24px;
        color:#111827;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="login-wrap">', unsafe_allow_html=True)
    st.markdown('<div class="title">CiscoIQ Login</div>', unsafe_allow_html=True)

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login", use_container_width=True):
        if username == USERNAME and password == PASSWORD:
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.error("Invalid username or password")

    st.markdown('</div>', unsafe_allow_html=True)


def sidebar():
    with st.sidebar:
        st.markdown("## ▥ CiscoIQ")

        pages = {
            "Dashboard":"dashboard",
            "Track Uploads":"uploads",
            "Reports":"reports",
            "Excel Report":"excel",
            "AI Chatbot":"chatbot",
            "Settings":"settings"
        }

        for label,key in pages.items():
            if st.button(label, use_container_width=True):
                st.session_state.page = key
                st.rerun()


def upload_page():
    st.markdown("""
    <style>
    .main .block-container{
        padding-top:1rem;
        max-width:100%;
    }
    .topbar{
        background:white;
        padding:20px;
        border-bottom:1px solid #e5e7eb;
        margin-bottom:20px;
    }
    .title{
        font-size:24px;
        font-weight:800;
    }
    .card{
        background:white;
        border:1px solid #e5e7eb;
        border-radius:18px;
        padding:16px;
        min-height:420px;
    }
    .save{
        background:#eef4ff;
        padding:12px;
        border-radius:12px;
        margin-top:12px;
        color:#2563eb;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="topbar"><div class="title">CiscoIQ Performance Report App</div></div>', unsafe_allow_html=True)
    st.subheader("Program Track Uploads")

    cols = st.columns(4)

    data = [
        ("API Metrics (.json)", ["json"], "Generate API Results"),
        ("UI Metrics (.csv)", ["csv"], "Generate UI Results"),
        ("Cloud Assist Connector (.csv)", ["csv"], "Generate Cloud Results"),
        ("Customer Inventory Benchmarking (.csv)", ["csv"], "Generate Inventory Results")
    ]

    for col, item in zip(cols, data):
        title, types, btn = item
        with col:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown(f"### {title}")
            st.file_uploader("Upload files", type=types, accept_multiple_files=True)
            st.checkbox("Save for team visibility", value=True)
            st.button(btn, use_container_width=True)
            st.markdown('<div class="save">No saved reports yet.</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)


def simple_page(title):
    st.title(title)
    st.info(f"{title} page")


def app():
    sidebar()

    page = st.session_state.get("page", "uploads")

    if page == "uploads":
        upload_page()
    elif page == "dashboard":
        simple_page("Dashboard")
    elif page == "reports":
        simple_page("Reports")
    elif page == "excel":
        simple_page("Excel Report")
    elif page == "chatbot":
        simple_page("AI Chatbot")
    elif page == "settings":
        simple_page("Settings")


def run_app():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    if not st.session_state.logged_in:
        login_page()
    else:
        app()

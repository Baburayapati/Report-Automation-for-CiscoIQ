
import streamlit as st

st.set_page_config(layout="wide")

def render_sidebar():

    st.markdown("""
    <style>

    [data-testid="stSidebar"]{
        background:linear-gradient(180deg,#03143d 0%, #001b5e 100%);
        width:220px !important;
    }

    [data-testid="stSidebar"] *{
        color:white;
    }

    .sidebar-logo{
        font-size:34px;
        text-align:center;
        margin-top:10px;
        margin-bottom:35px;
    }

    .nav-btn button{
        width:100%;
        border-radius:14px;
        height:54px;
        margin-bottom:12px;
        border:none;
        font-weight:700;
        background:transparent;
        color:white;
        text-align:left;
    }

    .nav-active button{
        background:linear-gradient(90deg,#3b82f6,#9333ea) !important;
        color:white !important;
        box-shadow:0 0 18px rgba(147,51,234,.45);
    }

    .main .block-container{
        padding-top:0.7rem;
        padding-left:1.5rem;
        padding-right:1.5rem;
        max-width:100%;
    }

    .topbar{
        background:white;
        border-bottom:1px solid #e5e7eb;
        padding:22px 24px;
        border-radius:0;
        margin-bottom:22px;
    }

    .app-title{
        font-size:22px;
        font-weight:800;
        color:#111827;
    }

    .section-title{
        font-size:18px;
        font-weight:800;
        color:#142c6e;
        margin-bottom:20px;
    }

    .upload-card{
        background:white;
        border:1px solid #e5e7eb;
        border-radius:18px;
        padding:16px;
        min-height:430px;
        margin-bottom:18px;
    }

    .upload-card h4{
        font-size:18px;
        font-weight:800;
        margin-bottom:18px;
        color:#111827;
    }

    .upload-box{
        border:2px dashed #d7dcff;
        border-radius:18px;
        padding:16px;
        background:#fbfcff;
        margin-bottom:14px;
    }

    .saved-box{
        background:#eef4ff;
        border-radius:12px;
        padding:14px;
        color:#2563eb;
        min-height:72px;
        font-weight:500;
        margin-top:12px;
    }

    .generate-btn button{
        width:100%;
        height:44px;
        border:none;
        border-radius:12px;
        color:white;
        font-weight:700;
        background:linear-gradient(90deg,#2563eb,#9333ea);
    }

    </style>
    """, unsafe_allow_html=True)

    with st.sidebar:

        st.markdown(
            '<div class="sidebar-logo">▥</div>',
            unsafe_allow_html=True
        )

        nav_items = [
            ("🏠 Dashboard", "dashboard"),
            ("📂 Track Uploads", "uploads"),
            ("📑 Reports", "reports"),
            ("📊 Excel Report", "excel"),
            ("💬 AI Chatbot", "chatbot"),
            ("⚙️ Settings", "settings")
        ]

        for label, value in nav_items:

            active = st.session_state.get("page", "uploads") == value

            cls = "nav-btn nav-active" if active else "nav-btn"

            st.markdown(f'<div class="{cls}">', unsafe_allow_html=True)

            if st.button(label, key=value):
                st.session_state.page = value
                st.rerun()

            st.markdown('</div>', unsafe_allow_html=True)

def render_track_uploads_page():

    st.markdown("""
        <div class="topbar">
            <div class="app-title">CiscoIQ Performance Report App</div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown(
        '<div class="section-title">Program Track Uploads</div>',
        unsafe_allow_html=True
    )

    c1, c2, c3, c4 = st.columns(4)

    cards = [
        (
            c1,
            "API Metrics (.json)",
            "Upload API Metrics JSON file(s)",
            ["json"],
            "200MB per file • JSON",
            "Generate API Results",
            "No saved API reports yet.",
            "api"
        ),
        (
            c2,
            "UI Metrics (.csv)",
            "Upload UI CSV files",
            ["csv"],
            "200MB per file • CSV",
            "Generate UI Results",
            "No saved UI reports yet.",
            "ui"
        ),
        (
            c3,
            "Cloud Assist Connector (.csv)",
            "Upload Cloud Assist CSV files",
            ["csv"],
            "200MB per file • CSV",
            "Generate Cloud Results",
            "No saved Cloud Assist Connector reports yet.",
            "cloud"
        ),
        (
            c4,
            "Customer Inventory Benchmarking (.csv)",
            "Upload Customer Inventory Benchmarking CSV files",
            ["csv"],
            "200MB per file • CSV",
            "Generate Inventory Results",
            "No saved Customer Inventory Benchmarking reports yet.",
            "inventory"
        ),
    ]

    for col, title, upload_label, file_types, caption, btn_text, save_text, key in cards:

        with col:

            st.markdown('<div class="upload-card">', unsafe_allow_html=True)

            st.markdown(f"<h4>{title}</h4>", unsafe_allow_html=True)

            st.markdown('<div class="upload-box">', unsafe_allow_html=True)

            st.file_uploader(
                upload_label,
                type=file_types,
                accept_multiple_files=True,
                key=f"upload_{key}"
            )

            st.caption(caption)

            st.markdown('</div>', unsafe_allow_html=True)

            st.checkbox(
                "Save for team visibility",
                value=True,
                key=f"check_{key}"
            )

            st.markdown('<div class="generate-btn">', unsafe_allow_html=True)

            st.button(
                btn_text,
                key=f"btn_{key}",
                use_container_width=True
            )

            st.markdown('</div>', unsafe_allow_html=True)

            st.markdown(
                f'<div class="saved-box">{save_text}</div>',
                unsafe_allow_html=True
            )

            st.markdown('</div>', unsafe_allow_html=True)

def render_dashboard():
    st.title("Dashboard")
    st.info("Executive Dashboard page")

def render_reports():
    st.title("Reports")
    st.info("Uploaded JSON and CSV reports")

def render_excel():
    st.title("Excel Report")
    st.info("Generated Excel reports")

def render_chatbot():
    st.title("AI Chatbot")
    st.info("Chatbot interface")

def render_settings():
    st.title("Settings")
    st.info("Profile, logout and preferences")

if "page" not in st.session_state:
    st.session_state.page = "uploads"

render_sidebar()

page = st.session_state.page

if page == "uploads":
    render_track_uploads_page()

elif page == "dashboard":
    render_dashboard()

elif page == "reports":
    render_reports()

elif page == "excel":
    render_excel()

elif page == "chatbot":
    render_chatbot()

elif page == "settings":
    render_settings()

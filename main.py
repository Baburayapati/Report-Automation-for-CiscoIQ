
import streamlit as st

st.set_page_config(page_title="CiscoIQ Performance Report App", layout="wide")

# ---------------- LOGIN ----------------

def login_page():

    st.markdown("""
    <style>
    .stApp{
        background:#f5f7fb;
    }

    .login-card{
        width:420px;
        margin:120px auto;
        background:white;
        padding:40px;
        border-radius:22px;
        box-shadow:0 8px 30px rgba(0,0,0,.08);
    }

    .login-title{
        text-align:center;
        font-size:32px;
        font-weight:900;
        margin-bottom:30px;
        color:#111827;
    }

    </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="login-card">', unsafe_allow_html=True)
    st.markdown('<div class="login-title">CiscoIQ Login</div>', unsafe_allow_html=True)

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login", use_container_width=True):
        if username == "admin" and password == "admin123":
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.error("Invalid credentials")

    st.markdown('</div>', unsafe_allow_html=True)


# ---------------- STYLES ----------------

def load_styles():

    st.markdown("""
    <style>

    .stApp{
        background:#f5f7fb;
    }

    [data-testid="stSidebar"]{
        background:linear-gradient(180deg,#02133d 0%, #001a5b 100%);
        width:240px !important;
    }

    [data-testid="stSidebar"] *{
        color:white;
    }

    .sidebar-logo{
        font-size:42px;
        text-align:center;
        margin-top:10px;
        margin-bottom:40px;
        font-weight:800;
    }

    .nav-btn{
        margin-bottom:12px;
    }

    .nav-btn button{
        width:100%;
        height:58px;
        border:none;
        border-radius:16px;
        background:transparent;
        color:white;
        font-size:18px;
        font-weight:700;
        text-align:left;
    }

    .nav-active button{
        background:linear-gradient(90deg,#3568ff,#8b3dff) !important;
        box-shadow:0 0 16px rgba(139,61,255,.35);
    }

    .main .block-container{
        padding-top:0rem;
        padding-left:1.4rem;
        padding-right:1.4rem;
        max-width:100%;
    }

    .topbar{
        height:80px;
        background:white;
        border-bottom:1px solid #e5e7eb;
        display:flex;
        align-items:center;
        justify-content:space-between;
        padding:0 26px;
        margin-bottom:24px;
    }

    .title{
        font-size:22px;
        font-weight:800;
        color:#111827;
    }

    .top-icons{
        display:flex;
        gap:20px;
        align-items:center;
        font-size:18px;
        font-weight:700;
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
        min-height:420px;
        box-shadow:0 2px 8px rgba(0,0,0,.03);
    }

    .upload-card h4{
        font-size:18px;
        font-weight:800;
        margin-bottom:16px;
        color:#111827;
    }

    .upload-box{
        border:2px dashed #dbe3ff;
        border-radius:18px;
        padding:16px;
        background:#fbfcff;
        margin-bottom:16px;
    }

    .generate-btn button{
        width:100%;
        height:42px;
        border:none;
        border-radius:12px;
        background:linear-gradient(90deg,#2f67ff,#8a3ffc);
        color:white;
        font-weight:700;
    }

    .saved-box{
        background:#eef4ff;
        border-radius:12px;
        padding:14px;
        margin-top:14px;
        color:#2563eb;
        min-height:72px;
    }

    </style>
    """, unsafe_allow_html=True)


# ---------------- SIDEBAR ----------------

def render_sidebar():

    with st.sidebar:

        st.markdown('<div class="sidebar-logo">▥</div>', unsafe_allow_html=True)

        items = [
            ("🏠 Dashboard","dashboard"),
            ("📂 Track Uploads","uploads"),
            ("📑 Reports","reports"),
            ("📊 Excel Report","excel"),
            ("💬 AI Chatbot","chatbot"),
            ("⚙️ Settings","settings")
        ]

        for label,key in items:

            active = st.session_state.get("page","uploads") == key
            cls = "nav-btn nav-active" if active else "nav-btn"

            st.markdown(f'<div class="{cls}">', unsafe_allow_html=True)

            if st.button(label, key=key):
                st.session_state.page = key
                st.rerun()

            st.markdown('</div>', unsafe_allow_html=True)


# ---------------- TOPBAR ----------------

def render_topbar():

    st.markdown("""
    <div class="topbar">

        <div class="title">
            CiscoIQ Performance Report App
        </div>

        <div class="top-icons">
            <span>Share</span>
            <span>⭐</span>
            <span>🖊️</span>
            <span>🐙</span>
        </div>

    </div>
    """, unsafe_allow_html=True)


# ---------------- TRACK UPLOADS ----------------

def render_uploads():

    render_topbar()

    st.markdown(
        '<div class="section-title">Program Track Uploads</div>',
        unsafe_allow_html=True
    )

    cols = st.columns(4)

    cards = [
        ("API Metrics (.json)", ["json"], "Generate API Results", "No saved API reports yet."),
        ("UI Metrics (.csv)", ["csv"], "Generate UI Results", "No saved UI reports yet."),
        ("Cloud Assist Connector (.csv)", ["csv"], "Generate Cloud Results", "No saved Cloud Assist Connector reports yet."),
        ("Customer Inventory Benchmarking (.csv)", ["csv"], "Generate Inventory Results", "No saved Customer Inventory Benchmarking reports yet.")
    ]

    for col, data in zip(cols, cards):

        title, types, btn, save = data

        with col:

            st.markdown('<div class="upload-card">', unsafe_allow_html=True)

            st.markdown(f"<h4>{title}</h4>", unsafe_allow_html=True)

            st.markdown('<div class="upload-box">', unsafe_allow_html=True)

            st.file_uploader(
                "Upload files",
                type=types,
                accept_multiple_files=True,
                key=title
            )

            st.caption(f"200MB per file • {types[0].upper()}")

            st.markdown('</div>', unsafe_allow_html=True)

            st.checkbox("Save for team visibility", value=True, key=f"check_{title}")

            st.markdown('<div class="generate-btn">', unsafe_allow_html=True)

            st.button(btn, use_container_width=True, key=btn)

            st.markdown('</div>', unsafe_allow_html=True)

            st.markdown(
                f'<div class="saved-box">{save}</div>',
                unsafe_allow_html=True
            )

            st.markdown('</div>', unsafe_allow_html=True)


def simple_page(name):

    render_topbar()

    st.title(name)
    st.info(f"{name} page")


# ---------------- APP ----------------

def app():

    load_styles()
    render_sidebar()

    if "page" not in st.session_state:
        st.session_state.page = "uploads"

    page = st.session_state.page

    if page == "uploads":
        render_uploads()

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


if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    login_page()
else:
    app()

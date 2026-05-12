
from __future__ import annotations

from pathlib import Path
import re
import json
import hashlib
import tempfile
import uuid
from io import BytesIO
from typing import Dict, List, Tuple
from datetime import datetime

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import streamlit.components.v1 as components

from main import build_report, build_comparison_report, build_single_report_frames


APP_TITLE = "CiscoIQ Performance Report App"
SAVED_REPORT_LIMIT = 15
PROGRAM_SAAS = "Cisco IQ SaaS Support Services"
TRACK_API = "API"
TRACK_UI = "UI"
TRACK_CLOUD = "Cloud Assist Connector"
TRACK_INVENTORY = "Customer Inventory Benchmarking"

UI_SLA_THRESHOLDS = {
    "FCP": 1.8,
    "LCP": 2.5,
    "TBT": 0.2,
    "CLS": 0.1,
    "SI": 3.4,
    "PERFORMANCE": 90.0,
}
NON_API_LATENCY_SLA_SEC = {
    TRACK_CLOUD: 2.0,
    TRACK_INVENTORY: 2.0,
}

st.set_page_config(page_title=APP_TITLE, layout="wide")


st.markdown("""
<style>
.stFileUploader {
    background: white;
    border-radius: 18px;
    padding: 14px;
    border: 1px solid #dbe4f0;
    box-shadow: 0 8px 24px rgba(15,23,42,.05);
}
.stButton>button[kind="primary"] {
    background: linear-gradient(90deg,#2563eb,#7c3aed) !important;
    border: none !important;
    border-radius: 12px !important;
    font-weight: 700 !important;
    height: 48px !important;
}
.stButton>button {
    white-space: nowrap !important;
}

/* v59 main page exact polish */
.hero-title-box {
    display: table;
    margin: 12px auto 8px auto;
    width: auto;
    max-width: fit-content;
    background: linear-gradient(135deg,#07132f 0%, #102a63 55%, #2d2b7f 100%);
    color: white;
    border-radius: 13px;
    padding: 10px 16px;
    box-shadow: 0 10px 22px rgba(7,19,47,.16);
}
.hero-title-box h1 {
    margin: 0;
    font-size: 19px;
    line-height: 1.12;
    font-weight: 850;
    white-space: nowrap;
}
.hero-subtitle {
    text-align: center;
    color: #334155;
    font-size: 14px;
    margin: 0 auto 16px auto;
    max-width: 980px;
}

/* v61 dashboard header + tabs polish */
.top-nav {
    background: linear-gradient(90deg,#06122f 0%, #081a3f 54%, #0b1f55 100%) !important;
    color:white !important;
    border-radius: 0 0 16px 16px !important;
    padding: 14px 22px !important;
    margin: -0.6rem -1rem 12px -1rem !important;
    box-shadow: 0 10px 28px rgba(6,18,47,.22) !important;
}
.brand-icon {
    width:40px !important;
    height:40px !important;
    border-radius:12px !important;
    background:linear-gradient(135deg,#2563eb,#7c3aed) !important;
    font-size:20px !important;
}
.brand-title {
    font-size:22px !important;
    font-weight:900 !important;
    letter-spacing:-.35px !important;
}
.brand-sub {
    font-size:12px !important;
    opacity:.82 !important;
}
.nav-time {
    font-size:12px !important;
    opacity:.88 !important;
}

.region-field-label {
    font-size: 14px !important;
    font-weight: 700 !important;
    color: #0f2b68 !important;
    margin: 0 0 6px 2px !important;
}

.track-upload-card {
    background: #ffffff;
    border: 1px solid #dbe4f0;
    border-radius: 14px;
    padding: 12px 14px;
    box-shadow: 0 8px 24px rgba(15,23,42,.05);
    margin-bottom: 10px;
}

/* Streamlit radio used as dashboard tabs */
div[role="radiogroup"] {
    display:flex !important;
    justify-content:center !important;
    gap:14px !important;
    background: #ffffff !important;
    border: 1px solid #dbe4f0 !important;
    border-radius: 14px !important;
    padding: 10px !important;
    margin: 0 0 14px 0 !important;
    box-shadow: 0 8px 20px rgba(15,23,42,.045) !important;
}
div[role="radiogroup"] label {
    background: #f8fbff !important;
    border: 1px solid #e0e7f3 !important;
    border-radius: 12px !important;
    padding: 8px 14px !important;
    min-width: 118px !important;
    text-align: center !important;
    font-weight: 800 !important;
    color: #0f2b68 !important;
    transition: .15s ease-in-out !important;
}
div[role="radiogroup"] label:hover {
    border-color:#2563eb !important;
    box-shadow:0 8px 18px rgba(37,99,235,.12) !important;
}
div[role="radiogroup"] label[data-baseweb="radio"] > div:first-child {
    display:none !important;
}
div[role="radiogroup"] label:has(input:checked) {
    background: linear-gradient(90deg,#4f46e5,#2563eb) !important;
    color: white !important;
    border-color: transparent !important;
    box-shadow: 0 12px 24px rgba(37,99,235,.28) !important;
}

/* Overview title strip */
.overview-title-card {
    background:#ffffff;
    border:1px solid #dbe4f0;
    border-radius:16px;
    padding:0;
    box-shadow:0 8px 22px rgba(15,23,42,.05);
    margin-bottom:12px;
}
.overview-title-pill {
    display:inline-block;
    background:linear-gradient(90deg,#2333a3,#3152d9);
    color:white;
    padding:9px 18px;
    border-radius:12px 12px 12px 0;
    font-size:15px;
    font-weight:900;
    letter-spacing:.2px;
    margin:0 0 8px 0;
}
.overview-title-sub {
    color:#667085;
    font-size:13px;
    padding:0 18px 12px 18px;
}


/* v62 Aggregated summary cards like reference image */
.agg-summary-card {
    background:#ffffff;
    border:1px solid #dbe4f0;
    border-radius:18px;
    padding:0 0 12px 0;
    box-shadow:0 18px 42px rgba(15,23,42,.075);
    margin-bottom:16px;
    overflow:hidden;
}
.agg-summary-title {
    display:inline-block;
    background:linear-gradient(90deg,#0f2b68,#2563eb 60%,#7c3aed);
    color:#ffffff;
    padding:9px 18px;
    border-radius:0 0 14px 0;
    font-size:15px;
    font-weight:900;
    letter-spacing:.2px;
    margin:0 0 8px 0;
}
.agg-kpi-row {
    display:grid;
    grid-template-columns: repeat(6, 1fr);
    gap:0;
    padding:10px 16px 0 16px;
}
.agg-kpi {
    display:flex;
    align-items:center;
    gap:14px;
    min-height:122px;
    padding:10px 18px;
    border-right:1px solid #e5edf7;
}
.agg-kpi:last-child {
    border-right:none;
}
.agg-icon {
    width:48px;
    height:48px;
    border-radius:14px;
    color:#fff;
    display:flex;
    align-items:center;
    justify-content:center;
    font-size:23px;
    font-weight:900;
    box-shadow:0 10px 20px rgba(15,23,42,.16);
    flex:0 0 48px;
}
.agg-label {
    font-size:13px;
    font-weight:850;
    color:#111827;
    margin-bottom:8px;
}
.agg-value {
    font-size:28px;
    font-weight:900;
    color:#111827;
    line-height:1.0;
    letter-spacing:-.4px;
}
.agg-suffix {
    font-size:13px;
    color:#667085;
    font-weight:650;
    margin-left:5px;
}
.agg-delta {
    font-size:12px;
    margin-top:10px;
    color:#667085;
    font-weight:650;
}
.agg-delta.good { color:#15803d; }
.agg-delta.bad { color:#ef4444; }
.agg-spark {
    width:132px;
    height:24px;
    margin-top:9px;
}
@media(max-width:1100px){
  .agg-kpi-row {grid-template-columns: repeat(2, 1fr);}
  .agg-kpi:nth-child(2n){border-right:none;}
}


/* v66 clickable top dashboard buttons */
.nav-button-row {
    background:#ffffff;
    border:1px solid #dbe4f0;
    border-radius:14px;
    padding:10px;
    margin-bottom:14px;
    box-shadow:0 8px 20px rgba(15,23,42,.045);
}
.nav-button-row + div button, .stButton > button {
    border-radius:12px !important;
    font-weight:800 !important;
}

/* v79 Executive main background polish */
.stApp {
  background:
    radial-gradient(circle at 8% 8%, rgba(37,99,235,.10), transparent 28%),
    radial-gradient(circle at 92% 10%, rgba(124,58,237,.12), transparent 24%),
    linear-gradient(135deg,#eef5ff 0%, #f8fbff 44%, #f2f5ff 100%) !important;
}
.main-page-card, .upload-card {
  border: 1px solid rgba(37,99,235,.12) !important;
  box-shadow: 0 14px 34px rgba(15,23,42,.08) !important;
}
.main-page-card {
  background:rgba(255,255,255,.94) !important;
  border-radius:20px !important;
  backdrop-filter: blur(12px) !important;
}
.stFileUploader {
  background: rgba(255,255,255,.92) !important;
  border: 1px dashed rgba(37,99,235,.28) !important;
  border-radius: 18px !important;
  padding: 14px !important;
  box-shadow: 0 10px 28px rgba(15,23,42,.06) !important;
}
.stButton > button, .stDownloadButton > button {
  border-radius:14px !important;
  border:1px solid rgba(37,99,235,.18) !important;
  box-shadow:0 10px 24px rgba(15,23,42,.07) !important;
  min-height:44px !important;
}
.stButton > button:hover, .stDownloadButton > button:hover {
  border-color:#2563eb !important;
  box-shadow:0 14px 28px rgba(37,99,235,.16) !important;
  transform:translateY(-1px) !important;
}
.stDataFrame, [data-testid="stDataFrame"] {
  border-radius:16px !important;
  overflow:hidden !important;
  box-shadow:0 12px 28px rgba(15,23,42,.045) !important;
}

</style>
""", unsafe_allow_html=True)

params = st.query_params
view_param = str(params.get("view", "")).strip().strip("./ ").lower()
dashboard_only = view_param == "dashboard"
team_upload_view = not dashboard_only
run_id = params.get("run_id", "")


@st.cache_resource
def get_dashboard_store():
    return {}


dashboard_store = get_dashboard_store()


st.markdown(
    """
<style>
:root {
  --navy:#07132f;
  --navy2:#0a1b3f;
  --blue:#2563eb;
  --purple:#6d28d9;
  --green:#16a34a;
  --red:#dc2626;
  --orange:#f59e0b;
  --card:#ffffff;
  --border:#dbe4f0;
  --muted:#667085;
}
.stApp {
  background: #f4f7fb;
  color: #111827;
}
[data-testid="stHeader"] { background: transparent; }
.block-container {
  max-width: 1560px;
  padding: 0.6rem 1rem 1.6rem 1rem;
}
#MainMenu, footer { visibility: hidden; }
.app-shell {
  background: white;
  border: 1px solid #dce3ef;
  border-radius: 18px;
  padding: 12px;
  box-shadow: 0 10px 30px rgba(10,27,63,0.06);
}
.hero {
  background:
    radial-gradient(circle at 20% 20%, rgba(59,130,246,.22), transparent 28%),
    radial-gradient(circle at 80% 10%, rgba(124,58,237,.28), transparent 26%),
    linear-gradient(135deg,#07132f 0%, #0a1b3f 50%, #0f2b68 100%);
  color:white;
  border-radius: 18px;
  padding: 12px 22px;
  box-shadow: 0 14px 32px rgba(7,19,47,.18);
  margin-bottom: 18px;
}
.hero h1 {
  margin: 0;
  font-size: 20px;
  line-height: 1.15;
  font-weight: 850;
  letter-spacing:-.4px;
}
.hero p {
  margin: 8px 0 0 0;
  color: rgba(255,255,255,.82);
  font-size: 14px;
}
.hero-actions {
  display:flex;
  gap:12px;
  align-items:center;
  margin-top: 18px;
  flex-wrap: wrap;
}
.primary-pill {
  display:inline-block;
  background: linear-gradient(90deg,#4f46e5,#2563eb);
  color:white !important;
  text-decoration:none !important;
  padding: 10px 16px;
  border-radius: 12px;
  font-weight:750;
  box-shadow: 0 12px 24px rgba(37,99,235,.24);
}
.secondary-pill {
  display:inline-block;
  background: rgba(255,255,255,.10);
  border: 1px solid rgba(255,255,255,.20);
  color:white !important;
  text-decoration:none !important;
  padding: 9px 14px;
  border-radius: 12px;
  font-weight:650;
}
.top-nav {
  display:flex;
  align-items:center;
  justify-content:space-between;
  background:linear-gradient(90deg,#0f2b68,#2563eb 55%,#7c3aed);
  color:white;
  border-radius: 0 0 22px 22px;
  padding: 16px 22px;
  margin: -0.6rem -1rem 16px -1rem;
  box-shadow: 0 18px 42px rgba(7,19,47,.20);
  border-bottom: 1px solid rgba(255,255,255,.16);
}
.brand {
  display:flex;
  align-items:center;
  gap: 12px;
}
.brand-icon {
  width:34px;height:34px;border-radius:10px;
  background:linear-gradient(135deg,#4f46e5,#06b6d4);
  display:flex;align-items:center;justify-content:center;
  font-size:18px;
}
.brand-title { font-size:21px;font-weight:900;line-height:1.1;letter-spacing:-.25px; }
.brand-sub { font-size:12px;color:rgba(255,255,255,.78);margin-top:3px;}
.nav-tabs {
  display:flex;
  gap: 8px;
  align-items:center;
}
.nav-tab {
  color:white;
  padding:8px 12px;
  border-radius:10px;
  font-size:13px;
  font-weight:650;
  opacity:.9;
}
.nav-tab.active {
  background: linear-gradient(90deg,#4f46e5,#2563eb);
  box-shadow:0 8px 16px rgba(37,99,235,.28);
}
.nav-time {font-size:11px;color:rgba(255,255,255,.82);text-align:right;}
.panel {
  background: rgba(255,255,255,.94);
  border: 1px solid rgba(148,163,184,.24);
  border-radius: 18px;
  padding: 18px;
  box-shadow: 0 18px 42px rgba(15,23,42,.075);
  margin-bottom: 16px;
  backdrop-filter: blur(10px);
}
.panel-title {
  font-size: 15px;
  font-weight: 900;
  color: #102a63;
  margin-bottom: 14px;
  display:flex;
  align-items:center;
  justify-content:space-between;
  letter-spacing:.16px;
}
.panel-title .tag {
  font-size:11px;
  background:linear-gradient(90deg,#eef4ff,#f5f3ff);
  color:#1d4ed8;
  padding:4px 10px;
  border-radius:999px;
  border:1px solid #dbeafe;
}
.kpi-grid {
  display:grid;
  grid-template-columns: repeat(6, 1fr);
  gap: 10px;
}
.kpi-card {
  background:white;
  border:1px solid var(--border);
  border-radius:14px;
  padding:14px;
  min-height:96px;
  box-shadow: 0 6px 18px rgba(15,23,42,.045);
  display:flex;
  gap:12px;
  align-items:flex-start;
}
.kpi-icon {
  width:38px;height:38px;border-radius:10px;
  display:flex;align-items:center;justify-content:center;
  color:white;font-size:19px;flex:0 0 38px;
  box-shadow: 0 10px 18px rgba(0,0,0,.12);
}
.kpi-label { font-size:12px;color:#111827;font-weight:750; }
.kpi-value { font-size:24px;font-weight:850;color:#111827;margin-top:6px;line-height:1.0; }
.kpi-sub { font-size:11px;color:var(--muted);margin-top:8px; }
.kpi-sub.good { color:#15803d; }
.kpi-sub.bad { color:#dc2626; }
.grid-3 {
  display:grid;
  grid-template-columns: 1.1fr 1fr 1fr;
  gap:12px;
}
.grid-2 {
  display:grid;
  grid-template-columns: 1.1fr .9fr;
  gap:12px;
}
.side-card {
  background: rgba(255,255,255,.94);
  border:1px solid rgba(148,163,184,.24);
  border-radius:18px;
  padding:16px;
  box-shadow: 0 18px 40px rgba(15,23,42,.075);
  margin-bottom:16px;
  backdrop-filter: blur(10px);
}
.insight-item {
  display:flex;
  gap:10px;
  align-items:flex-start;
  margin: 10px 0;
  font-size:13px;
  color:#1f2937;
}
.dot {
  width:22px;height:22px;border-radius:50%;
  display:flex;align-items:center;justify-content:center;
  color:white;font-size:12px;font-weight:800;flex:0 0 22px;
}
.filter-card {
  background:#f8fbff;
  border:1px solid var(--border);
  border-radius:12px;
  padding: 12px;
}
.chat-card {
  background:white;
  border: 1px solid #c7b7ff;
  border-radius:13px;
  padding:14px;
  box-shadow: 0 8px 22px rgba(109,40,217,.10);
}
.chat-header {
  background:linear-gradient(90deg,#6d28d9,#7c3aed);
  color:white;
  padding:10px 12px;
  border-radius:10px;
  font-size:13px;
  font-weight:800;
  margin:-2px -2px 12px -2px;
}
.mini-link {
  color:#2563eb !important;
  font-size:12px;
  font-weight:700;
  text-decoration:none !important;
}
.stButton > button {
  border-radius: 10px !important;
  font-weight: 750 !important;
}
.stDownloadButton > button {
  border-radius: 10px !important;
  font-weight: 750 !important;
}
[data-testid="stFileUploader"] {
  background:white;
  border:1px dashed #a6b4ca;
  border-radius:14px;
  padding: 16px;
}
[data-testid="stMetric"] {
  background:white;
  border-radius: 12px;
}
.upload-card {
  max-width: 1100px;
  margin: 0 auto;
}
.main-page-card {
  background:white;
  border:1px solid var(--border);
  border-radius:16px;
  padding:22px;
  box-shadow: 0 12px 30px rgba(15,23,42,.06);
  margin-bottom:16px;
}
.login-form-wrap {
  max-width: 660px;
  margin: 18px auto 0 auto;
}
.login-form-wrap [data-testid="stTextInput"] {
  margin-bottom: 14px;
}
.login-form-wrap [data-testid="stTextInput"] input {
  min-height: 48px !important;
  border: 1.5px solid #1f2937 !important;
  border-radius: 4px !important;
  background: #ffffff !important;
}
.login-form-wrap [data-testid="stTextInput"] label {
  color: #1f2937 !important;
  font-size: 18px !important;
  font-weight: 700 !important;
  padding-bottom: 4px !important;
}
.login-form-wrap .stButton > button {
  margin-top: 8px;
}
.feature-grid {
  display:grid;
  grid-template-columns: repeat(3, 1fr);
  gap:12px;
  margin-top:14px;
}
.feature {
  border:1px solid #e3e9f5;
  border-radius:14px;
  padding:14px;
  background:#fbfdff;
}
.feature h4 { margin:0 0 6px 0;font-size:14px;color:#0f2b68; }
.feature p { margin:0;color:#667085;font-size:12px; }
@media(max-width:1100px){
  .kpi-grid,.grid-3,.grid-2,.feature-grid {grid-template-columns:1fr;}
  .nav-tabs {display:none;}
}

/* Executive KPI metric styling */
div[data-testid="stMetric"] {
    background: #ffffff !important;
    border: 1px solid #dbe4f0 !important;
    border-radius: 14px !important;
    padding: 16px 16px !important;
    box-shadow: 0 8px 20px rgba(15,23,42,.055) !important;
    min-height: 104px !important;
}
div[data-testid="stMetricLabel"] {
    font-weight: 800 !important;
    color: #111827 !important;
}
div[data-testid="stMetricValue"] {
    font-weight: 850 !important;
    color: #111827 !important;
}

</style>
""",
    unsafe_allow_html=True,
)


def get_store():
    return dashboard_store


def infer_program_track(label: str) -> Tuple[str, str]:
    name = str(label or "").upper()
    if "ONPREM" in name and "RISK" in name:
        return "Cisco IQ Onprem - Risk App", TRACK_API
    if "ONPREM" in name and "ASSET" in name:
        return "Cisco IQ Onprem - Assets", TRACK_API
    if "CX AI ASSISTANT" in name or "CX_AI_ASSISTANT" in name:
        return "CX AI Assistant", TRACK_API

    if "CLOUD" in name and "CONNECTOR" in name:
        return PROGRAM_SAAS, TRACK_CLOUD
    if "BENCHMARK" in name or "INVENTORY" in name:
        return PROGRAM_SAAS, TRACK_INVENTORY
    if "LIGHTHOUSE" in name or re.search(r"(?:^|[_\-])UI(?:[_\-]|$)", name):
        return PROGRAM_SAAS, TRACK_UI
    return PROGRAM_SAAS, TRACK_API


def add_ui_sla_columns(apis_df: pd.DataFrame) -> pd.DataFrame:
    df = apis_df.copy()
    if df.empty:
        return df
    df["Feature"] = df["Feature"].astype(str)
    df["Scenario"] = df.get("Scenario", "").astype(str)
    df["Endpoint"] = df.get("Endpoint", "").astype(str)
    df["API"] = df["Feature"] + "/" + df["Scenario"] + "/" + df["Endpoint"]
    for col in [
        "Avg ResTime in sec", "Min ResTime in sec", "MaxRes Time in sec",
        "90thPercentile Resp Time in Sec", "95thPercentile Resp Time in Sec",
        "99thPercentile Resp Time in Sec", "sampleCount", "errorCount", "errorPct",
    ]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
    df["SLA Sec"] = df["Feature"].str.upper().str.startswith("ASKAI").map({True: 10, False: 2})
    df["SLA Status"] = (
        (df["Avg ResTime in sec"] <= df["SLA Sec"])
        & (df["Min ResTime in sec"] <= df["SLA Sec"])
        & (df["MaxRes Time in sec"] <= df["SLA Sec"])
        & (df["95thPercentile Resp Time in Sec"] <= df["SLA Sec"])
    ).map({True: "PASS", False: "FAIL"})
    df["SLA Breach Sec"] = (df["Avg ResTime in sec"] - df["SLA Sec"]).clip(lower=0).round(2)
    df["Track Type"] = df["Feature"].str.upper().str.startswith("ASKAI").map({True: "AskAI", False: "Other"})
    return df


def process_uploaded_file(path: Path, label: str) -> Dict[str, pd.DataFrame]:
    frames = build_single_report_frames(path)
    frames["APIs"] = add_ui_sla_columns(frames["APIs"])
    frames["Label"] = label
    frames["Region"] = region_from_frames(frames)
    return frames


def region_from_frames(frames: Dict[str, pd.DataFrame]) -> str:
    info = frames.get("Run_Info")
    if info is not None and not info.empty and "Region" in info.columns:
        region = str(info.iloc[0].get("Region", "N/A")).strip()
        if region and region.upper() != "N/A":
            return region
    label = str(frames.get("Label", ""))
    upper = label.upper()
    for region in ["APJC", "EMEA", "US", "AMER", "EU", "LATAM", "INDIA"]:
        if re.search(rf"(?:^|[_\-\s]){region}(?:$|[_\-\s])", upper):
            return region
    return "Unknown"


def add_region_to_frames(run_frames: List[Dict[str, pd.DataFrame]]) -> List[Dict[str, pd.DataFrame]]:
    for frames in run_frames:
        frames["Region"] = region_from_frames(frames)
    return run_frames


def summarize_run(df: pd.DataFrame) -> Dict[str, float]:
    if df.empty:
        return dict(avg_sec=0, success_rate=0, error_rate=0, transactions=0, performance_score=0, sla_compliance=0, errors=0, samples=0, p95_sec=0, max_sec=0)
    samples = pd.to_numeric(df.get("sampleCount", 0), errors="coerce").fillna(0).sum()
    errors = pd.to_numeric(df.get("errorCount", 0), errors="coerce").fillna(0).sum()
    success_rate = round(((samples - errors) / samples) * 100, 2) if samples else 0
    error_rate = round((errors / samples) * 100, 2) if samples else 0
    sla_pass_pct = round(df["SLA Status"].eq("PASS").sum() / len(df) * 100, 2) if len(df) else 0
    score = round(max(0, min(100, sla_pass_pct - error_rate)), 2)
    return dict(
        avg_sec=round(float(df["Avg ResTime in sec"].mean()), 2),
        success_rate=success_rate,
        error_rate=error_rate,
        transactions=int(len(df)),
        performance_score=score,
        sla_compliance=sla_pass_pct,
        errors=int(errors),
        samples=int(samples),
        p95_sec=round(float(df["95thPercentile Resp Time in Sec"].mean()), 2) if "95thPercentile Resp Time in Sec" in df.columns else 0,
        max_sec=round(float(df["MaxRes Time in sec"].max()), 2) if "MaxRes Time in sec" in df.columns else 0,
    )


def safe_cols(df: pd.DataFrame, cols: List[str]) -> List[str]:
    return [c for c in cols if c in df.columns]


def track_summary(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame()
    out = (
        df.groupby(["Feature", "Track Type"], dropna=False)
        .agg(
            APIs=("API", "count"),
            Avg_Sec=("Avg ResTime in sec", "mean"),
            P95_Sec=("95thPercentile Resp Time in Sec", "mean"),
            Max_Sec=("MaxRes Time in sec", "max"),
            Errors=("errorCount", "sum"),
            ErrorPct=("errorPct", "mean"),
            SLA_Fails=("SLA Status", lambda x: (x == "FAIL").sum()),
            Samples=("sampleCount", "sum"),
        )
        .reset_index()
    )
    out["SLA Fail %"] = (out["SLA_Fails"] / out["APIs"] * 100).round(2)
    for col in ["Avg_Sec", "P95_Sec", "Max_Sec", "ErrorPct"]:
        out[col] = pd.to_numeric(out[col], errors="coerce").fillna(0).round(2)
    return out.sort_values(["P95_Sec", "Avg_Sec", "Errors"], ascending=False)


def sla_color_for_track(track_name: str, p95_value: float) -> float:
    threshold = 10 if str(track_name).upper().startswith("ASKAI") else 2
    return 1 if float(p95_value or 0) < threshold else 0


def combined_df(run_frames: List[Dict[str, pd.DataFrame]]) -> pd.DataFrame:
    parts = []
    for frames in run_frames:
        tmp = frames["APIs"].copy()
        tmp["Run"] = frames["Label"]
        tmp["Region"] = frames.get("Region", region_from_frames(frames))
        parts.append(tmp)
    return pd.concat(parts, ignore_index=True) if parts else pd.DataFrame()







def render_dashboard_header() -> None:
    st.markdown(
        f"""
<div class="top-nav">
  <div class="brand">
    <div class="brand-icon">📈</div>
    <div>
      <div class="brand-title">CiscoIQ Performance Report App</div>
      <div class="brand-sub">Real-time performance insights across regions</div>
    </div>
  </div>
  <div class="nav-time">Dashboard View<br/>Last Updated</div>
</div>
""",
        unsafe_allow_html=True,
    )


def dashboard_view_tabs() -> str:
    current_tab = params.get("tab", "") or st.session_state.get("dashboard_tab", "Overview")
    if "nav_target" in st.session_state:
        current_tab = st.session_state.pop("nav_target")

    valid_tabs = ["Overview", "Track Comparison", "Detailed Report", "Chatbot"]
    legacy_tabs = {"Drilldown": "Detailed Report", "Compare": "Track Comparison", "Reports": "Overview", "Trends": "Overview"}
    current_tab = legacy_tabs.get(current_tab, current_tab)
    if current_tab not in valid_tabs:
        current_tab = "Overview"
    st.session_state["dashboard_tab"] = current_tab
    current_run_id = params.get("run_id", "") or st.session_state.get("run_id", "")
    tabs = [
        ("Overview", "Overview"),
        ("Track Comparison", "Track Comparison"),
        ("Detailed Report", "Detailed Report"),
        ("Chatbot", "AI Chatbot"),
    ]
    icons = {
        "Overview": "◆",
        "Track Comparison": "▦",
        "Detailed Report": "⌕",
        "Chatbot": "●",
    }
    tab_cols = st.columns(len(tabs), gap="small")
    selected_tab = current_tab
    for col, (tab_value, tab_label) in zip(tab_cols, tabs):
        if col.button(f"{icons[tab_value]} {tab_label}", key=f"dashboard_view_{tab_value}", type="primary" if current_tab == tab_value else "secondary", use_container_width=True):
            selected_tab = tab_value
    st.session_state["dashboard_tab"] = selected_tab
    if current_run_id:
        st.query_params["view"] = "dashboard"
        st.query_params["run_id"] = current_run_id
        st.query_params["tab"] = selected_tab
    return selected_tab


def kpi_cards(df: pd.DataFrame, previous_df: pd.DataFrame | None = None, title: str = "AGGREGATED PERFORMANCE OVERVIEW METRICS", compact: bool = False) -> None:
    s = summarize_run(df)
    sla_fail = round(100 - s["sla_compliance"], 2) if s["transactions"] else 0

    previous = summarize_run(previous_df) if previous_df is not None else None

    def delta_html(current: float, previous_value: float | None, suffix: str = "", lower_is_better: bool = False) -> str:
        if previous_value is None:
            return ""
        diff = round(float(current or 0) - float(previous_value or 0), 2)
        good = diff <= 0 if lower_is_better else diff >= 0
        arrow = "▲" if diff >= 0 else "▼"
        css_class = "good" if good else "bad"
        sign = "+" if diff > 0 else ""
        return f'<div class="agg-delta {css_class}">{arrow} {sign}{diff:g}{suffix} vs prev</div>'

    previous_sla_fail = round(100 - previous["sla_compliance"], 2) if previous else None
    health_delta = delta_html(s["performance_score"], previous["performance_score"] if previous else None)
    sla_pass_delta = delta_html(s["sla_compliance"], previous["sla_compliance"] if previous else None, "%")
    sla_fail_delta = delta_html(sla_fail, previous_sla_fail, "%", lower_is_better=True)
    apis_delta = delta_html(s["transactions"], previous["transactions"] if previous else None)
    samples_delta = delta_html(s["samples"], previous["samples"] if previous else None)
    errors_delta = delta_html(s["errors"], previous["errors"] if previous else None, lower_is_better=True)

    if not health_delta:
        health_delta = """
        <svg class="agg-spark" viewBox="0 0 130 28" xmlns="http://www.w3.org/2000/svg">
          <polyline points="2,20 16,19 29,20 42,17 55,18 68,11 81,16 94,18 107,9 124,14 129,8"
            fill="none" stroke="#22a447" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
        """
    if not sla_pass_delta:
        sla_pass_delta = '<div class="agg-delta good">▲ APIs meeting SLA</div>'
    if not sla_fail_delta:
        sla_fail_delta = '<div class="agg-delta bad">▼ APIs breaching SLA</div>'
    if not apis_delta:
        apis_delta = '<div class="agg-delta good">▲ Compared APIs</div>'
    if not samples_delta:
        samples_delta = '<div class="agg-delta good">▲ Executed samples</div>'
    if not errors_delta:
        errors_delta = '<div class="agg-delta bad">▼ Failed samples</div>'

    extra_cards = "" if compact else f"""
    <div class="agg-kpi">
      <div class="agg-icon" style="background:linear-gradient(135deg,#2563eb,#3152d9);">♜</div>
      <div>
        <div class="agg-label">Total APIs</div>
        <div class="agg-value">{s['transactions']:,}</div>
        {apis_delta}
      </div>
    </div>

    <div class="agg-kpi">
      <div class="agg-icon" style="background:linear-gradient(135deg,#7c3aed,#a855f7);">◉</div>
      <div>
        <div class="agg-label">Total Samples</div>
        <div class="agg-value">{s['samples']:,}</div>
        {samples_delta}
      </div>
    </div>

    <div class="agg-kpi">
      <div class="agg-icon" style="background:#dc2626;">⚠</div>
      <div>
        <div class="agg-label">Total Errors</div>
        <div class="agg-value">{s['errors']:,}</div>
        {errors_delta}
      </div>
    </div>
    """

    columns = 3 if compact else 6
    component_height = 205 if not compact else 190

    html = f"""
<!DOCTYPE html>
<html>
<head>
<style>
body {{
    margin: 0;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    background: transparent;
}}
.agg-summary-card {{
    background:#ffffff;
    border:1px solid #dbe4f0;
    border-radius:14px;
    padding:0 0 12px 0;
    box-shadow:0 8px 22px rgba(15,23,42,.045);
}}
.agg-summary-title {{
    display:inline-block;
    background:linear-gradient(90deg,#2333a3,#3152d9);
    color:#ffffff;
    padding:9px 18px;
    border-radius:12px 12px 12px 0;
    font-size:15px;
    font-weight:900;
    letter-spacing:.2px;
    margin:0 0 8px 0;
}}
.agg-kpi-row {{
    display:grid;
    grid-template-columns: repeat({columns}, 1fr);
    gap:0;
    padding:10px 16px 0 16px;
}}
.agg-kpi {{
    display:flex;
    align-items:center;
    gap:14px;
    min-height:130px;
    padding:10px 18px;
    border-right:1px solid #e5edf7;
}}
.agg-kpi:last-child {{
    border-right:none;
}}
.agg-icon {{
    width:44px;
    height:44px;
    border-radius:10px;
    color:#fff;
    display:flex;
    align-items:center;
    justify-content:center;
    font-size:23px;
    font-weight:900;
    box-shadow:0 10px 20px rgba(15,23,42,.16);
    flex:0 0 44px;
}}
.agg-label {{
    font-size:13px;
    font-weight:850;
    color:#111827;
    margin-bottom:8px;
}}
.agg-value {{
    font-size:28px;
    font-weight:900;
    color:#111827;
    line-height:1.0;
    letter-spacing:-.4px;
}}
.agg-suffix {{
    font-size:13px;
    color:#667085;
    font-weight:650;
    margin-left:5px;
}}
.agg-delta {{
    font-size:13px;
    margin-top:10px;
    color:#667085;
    font-weight:700;
    line-height:1.25;
    white-space:normal;
}}
.agg-delta.good {{ color:#15803d; }}
.agg-delta.bad {{ color:#ef4444; }}
.agg-spark {{
    width:132px;
    height:24px;
    margin-top:9px;
}}
@media(max-width:1100px){{
  .agg-kpi-row {{ grid-template-columns: repeat(2, 1fr); }}
  .agg-kpi:nth-child(2n){{border-right:none;}}
}}
</style>
</head>
<body>
<div class="agg-summary-card">
  <div class="agg-summary-title">{title}</div>
  <div class="agg-kpi-row">

    <div class="agg-kpi">
      <div class="agg-icon" style="background:linear-gradient(135deg,#2563eb,#4f46e5);">🛡</div>
      <div>
        <div class="agg-label">Health Score</div>
        <div class="agg-value">{s['performance_score']}<span class="agg-suffix">/100</span></div>
        {health_delta}
      </div>
    </div>

    <div class="agg-kpi">
      <div class="agg-icon" style="background:#16843a;">✓</div>
      <div>
        <div class="agg-label">SLA Pass %</div>
        <div class="agg-value">{s['sla_compliance']}%</div>
        {sla_pass_delta}
      </div>
    </div>

    <div class="agg-kpi">
      <div class="agg-icon" style="background:#dc2626;">×</div>
      <div>
        <div class="agg-label">SLA Fail %</div>
        <div class="agg-value">{sla_fail}%</div>
        {sla_fail_delta}
      </div>
    </div>

    {extra_cards}

  </div>
</div>
</body>
</html>
"""
    components.html(html, height=component_height, scrolling=False)


def build_run_summary_table(run_frames: List[Dict[str, pd.DataFrame]]) -> pd.DataFrame:
    rows = []
    baseline = None
    for index, frames in enumerate(run_frames):
        row = summarize_run(frames["APIs"])
        if baseline is None:
            baseline = row.copy()
        sla_fail = round(100 - row["sla_compliance"], 2)
        rows.append({
            "Result": run_display_label(frames),
            "Region": frames.get("Region", region_from_frames(frames)),
            "Health Score": row["performance_score"],
            "SLA Pass %": row["sla_compliance"],
            "SLA Fail %": sla_fail,
        })
    return pd.DataFrame(rows)


def render_aggregated_or_comparison_summary(run_frames: List[Dict[str, pd.DataFrame]]) -> None:
    if len(run_frames) <= 1:
        kpi_cards(combined_df(run_frames), compact=True)
        return

    current_df = run_frames[-1]["APIs"]
    previous_df = run_frames[-2]["APIs"] if len(run_frames) > 1 else None
    kpi_cards(current_df, previous_df=previous_df, title="AGGREGATED PERFORMANCE OVERVIEW METRICS", compact=True)

    summary = build_run_summary_table(run_frames)
    st.markdown('<div class="panel"><div class="panel-title">COMPARISON SUMMARY</div>', unsafe_allow_html=True)
    st.dataframe(summary, use_container_width=True, hide_index=True, height=min(245, 72 + 42 * len(summary)))
    st.markdown("</div>", unsafe_allow_html=True)


def sla_donut(df: pd.DataFrame):
    counts = df["SLA Status"].value_counts().reset_index()
    counts.columns = ["SLA Status", "Count"]
    fig = px.pie(
        counts,
        names="SLA Status",
        values="Count",
        hole=0.62,
        color="SLA Status",
        color_discrete_map={"PASS": "#2ca02c", "FAIL": "#ef4444"},
    )
    s = summarize_run(df)
    fig.update_layout(
        height=280,
        margin=dict(l=5, r=5, t=15, b=5),
        legend=dict(orientation="v", yanchor="middle", y=.5, xanchor="left", x=.82),
        annotations=[dict(text=f"<b>{s['sla_compliance']}%</b><br>PASS", x=.39, y=.5, font_size=18, showarrow=False)],
    )
    return fig


def get_filtered_frames(run_frames: List[Dict[str, pd.DataFrame]], forced_region: str = "All", forced_track: str = "API") -> List[Dict[str, pd.DataFrame]]:
    rows = []
    for frames in run_frames:
        info = frames.get("Run_Info")
        info_row = info.iloc[0].to_dict() if info is not None and not info.empty else {}
        label = frames["Label"]
        inferred = infer_saved_report_info(label)
        region = frames.get("Region", region_from_frames(frames))
        if not region or region == "Unknown":
            region = inferred.get("region", "Unknown")
        date = str(info_row.get("Date", "N/A"))
        if not date or date == "N/A":
            date = inferred.get("date", "N/A")
        duration = str(info_row.get("Duration", "N/A"))
        if not duration or duration == "N/A":
            duration = inferred.get("duration", "N/A")
        rows.append({
            "Label": label,
            "Display": run_display_label(frames),
            "Region": region,
            "Date": date,
            "Duration": duration,
            "Track": infer_program_track(label)[1],
        })
    meta = pd.DataFrame(rows)
    if meta.empty:
        return run_frames

    meta = meta[meta["Track"] == forced_track].copy()
    if meta.empty:
        return []

    meta = meta.head(9).copy()

    files = meta["Display"].tolist()
    dates = sorted(meta["Date"].astype(str).unique().tolist())
    regions = sorted(meta["Region"].astype(str).unique().tolist())

    file_options = [f"Compare Selected ({len(files)})"] + files
    date_options = [f"All Dates ({len(dates)})"] + dates
    region_options = [", ".join(regions) + f" ({len(regions)})"] + regions

    with st.container(border=True):
        st.markdown(
            """
<style>
.filter-card-title {
    color:#0f2b68;
    font-size:18px;
    font-weight:900;
    letter-spacing:.2px;
    margin-bottom:12px;
}
.filter-help {
    color:#667085;
    font-size:12px;
    margin:-4px 0 12px 0;
}
</style>
<div class="filter-card-title">DATA & FILTERS</div>
<div class="filter-help">Choose reports, test date and region, then apply.</div>
""",
            unsafe_allow_html=True,
        )

        selected_file_choice = st.selectbox("Result File", file_options, index=0, key="dashboard_filter_file_choice")
        selected_date_choice = st.selectbox("Date", date_options, index=0, key="dashboard_filter_date_choice")
        selected_region_choice = st.selectbox("Region", region_options, index=0, key="dashboard_filter_region_choice")

        apply_clicked = st.button("Apply Filters", type="primary", use_container_width=True, key="dashboard_apply_filters")
        reset_clicked = st.button("Reset Filters", use_container_width=True, key="dashboard_reset_filters")

        if reset_clicked:
            st.session_state["applied_dashboard_filters"] = {
                "file": file_options[0],
                "date": date_options[0],
                "region": region_options[0],
            }
            st.rerun()
        if apply_clicked or "applied_dashboard_filters" not in st.session_state:
            st.session_state["applied_dashboard_filters"] = {
                "file": selected_file_choice,
                "date": selected_date_choice,
                "region": selected_region_choice,
            }

        active_filters = st.session_state.get("applied_dashboard_filters", {
            "file": file_options[0],
            "date": date_options[0],
            "region": region_options[0],
        })

    selected_files = files if active_filters.get("file") == file_options[0] else [active_filters.get("file")]
    selected_dates = dates if active_filters.get("date") == date_options[0] else [active_filters.get("date")]
    selected_regions = regions if active_filters.get("region") == region_options[0] else [active_filters.get("region")]
    if forced_region and forced_region != "All":
        selected_regions = [forced_region]

    if not selected_files or not selected_dates or not selected_regions:
        return []

    keep_labels = meta[
        meta["Display"].isin(selected_files)
        & meta["Date"].astype(str).isin(selected_dates)
        & meta["Region"].astype(str).isin(selected_regions)
    ]["Label"].tolist()
    return [frames for frames in run_frames if frames["Label"] in keep_labels]


def auto_insights(run_frames: List[Dict[str, pd.DataFrame]]) -> List[Tuple[str, str, str]]:
    df = combined_df(run_frames)
    s = summarize_run(df)
    tracks = track_summary(df)
    result = []
    if len(run_frames) > 1:
        summary_rows = []
        for frames in run_frames:
            row = summarize_run(frames["APIs"])
            row["Region"] = frames.get("Region", region_from_frames(frames))
            summary_rows.append(row)
        summary = pd.DataFrame(summary_rows)
        best = summary.sort_values("sla_compliance", ascending=False).iloc[0]
        worst = summary.sort_values("error_rate", ascending=False).iloc[0]
        result.append(("✓", "#16a34a", f"{best['Region']} has best SLA compliance at {best['sla_compliance']}%."))
        result.append(("!", "#ef4444", f"{worst['Region']} has highest error rate at {worst['error_rate']}%."))
    if not tracks.empty:
        worst_track = tracks.iloc[0]
        result.append(("⚠", "#f59e0b", f"{worst_track['Feature']} is top contributor for P95 latency at {worst_track['P95_Sec']}s."))
    result.append(("i", "#2563eb", f"Overall SLA compliance is {s['sla_compliance']}% with {s['errors']:,} errors."))
    return result[:5]



def response_bucket(value: float, is_askai: bool) -> str:
    value = float(value or 0)
    if is_askai:
        if value <= 10:
            return "0-10s %"
        if value <= 20:
            return "10-20s %"
        if value <= 30:
            return "20-30s %"
        return ">30s %"
    if value <= 2:
        return "0-2s %"
    if value <= 4:
        return "3-4s %"
    if value <= 6:
        return "4-6s %"
    return ">6s %"


def metric_bucket_summary(df: pd.DataFrame, track: str, metric: str, is_askai: bool) -> List[float]:
    col_map = {
        "Avg": "Avg ResTime in sec",
        "Min": "Min ResTime in sec",
        "Max": "MaxRes Time in sec",
    }
    col = col_map[metric]
    rows = df[df["Feature"].astype(str) == str(track)].copy()
    if rows.empty or col not in rows.columns:
        return [0, 0, 0, 0, 0]

    bucket_names = ["0-10s %", "10-20s %", "20-30s %", ">30s %"] if is_askai else ["0-2s %", "3-4s %", "4-6s %", ">6s %"]
    counts = dict.fromkeys(bucket_names, 0)
    values = pd.to_numeric(rows[col], errors="coerce").fillna(0)
    for value in values:
        counts[response_bucket(float(value), is_askai)] += 1
    total = len(values) if len(values) else 1
    percentages = [round(counts[name] / total * 100, 2) for name in bucket_names]
    return percentages + [round(float(values.max()), 2)]



def build_dashboard_track_comparison(run_frames: List[Dict[str, pd.DataFrame]]) -> Tuple[pd.DataFrame, pd.DataFrame]:
    if not run_frames:
        return pd.DataFrame(), pd.DataFrame()

    all_tracks = sorted(set().union(*[set(frames["APIs"]["Feature"].dropna().astype(str)) for frames in run_frames]))
    all_tracks = [t for t in all_tracks if t.lower() != "total" and "select customer" not in t.lower()]

    askai_tracks = [t for t in all_tracks if t.upper().startswith("ASKAI")]
    other_tracks = [t for t in all_tracks if not t.upper().startswith("ASKAI")]

    def metric_bucket_summary_for_rows(rows: pd.DataFrame, metric: str, is_askai: bool) -> List[float]:
        col_map = {
            "Avg": "Avg ResTime in sec",
            "Min": "Min ResTime in sec",
            "Max": "MaxRes Time in sec",
        }
        col = col_map[metric]
        bucket_names = ["0-10sec %", "10-20sec %", "20-30sec %", ">30sec %"] if is_askai else ["0-2sec %", "3-4sec %", "4-6sec %", ">6sec %"]
        if rows.empty or col not in rows.columns:
            return [0, 0, 0, 0, 0]

        counts = dict.fromkeys(bucket_names, 0)
        values = pd.to_numeric(rows[col], errors="coerce").fillna(0)
        for value in values:
            bucket = response_bucket(float(value), is_askai).replace("s %", "sec %")
            counts[bucket] = counts.get(bucket, 0) + 1
        total = len(values) if len(values) else 1
        percentages = [round(counts[name] / total * 100, 2) for name in bucket_names]
        return percentages + [round(float(values.max()), 2)]

    def build_section(tracks: List[str], is_askai: bool) -> pd.DataFrame:
        rows = []
        bucket_names = ["0-10sec %", "10-20sec %", "20-30sec %", ">30sec %"] if is_askai else ["0-2sec %", "3-4sec %", "4-6sec %", ">6sec %"]
        row_targets = ["Total"] + tracks

        for target in row_targets:
            first_target_row = True
            for frames in run_frames:
                api_df = frames["APIs"].copy()
                if target == "Total":
                    api_rows = api_df[api_df["Feature"].astype(str).isin(tracks)] if tracks else api_df
                else:
                    api_rows = api_df[api_df["Feature"].astype(str) == str(target)]

                display_label = run_display_label(frames)
                for metric_index, metric in enumerate(["Avg", "Min", "Max"]):
                    values = metric_bucket_summary_for_rows(api_rows, metric, is_askai)
                    row = {
                        "_TrackKey": target,
                        "Track": target if first_target_row else "",
                        "Result": display_label if metric_index == 0 else "",
                        "Metric": metric,
                    }
                    for name, value in zip(bucket_names + ["Max Seconds"], values):
                        row[name] = value
                    rows.append(row)
                    first_target_row = False

        return pd.DataFrame(rows)

    return build_section(askai_tracks, True), build_section(other_tracks, False)


def display_track_comparison_df(df: pd.DataFrame) -> pd.DataFrame:
    return df.drop(columns=["_TrackKey"], errors="ignore")


def render_track_comparison_dashboard(run_frames: List[Dict[str, pd.DataFrame]]) -> None:
    askai_df, other_df = build_dashboard_track_comparison(run_frames)

    def render_section(title: str, data: pd.DataFrame, height: int) -> None:
        if data.empty:
            return
        with st.container(border=True):
            st.markdown(f'<div class="panel-title">{title}</div>', unsafe_allow_html=True)
            total = data[data["_TrackKey"] == "Total"].copy()
            detail = data[data["_TrackKey"] != "Total"].copy()
            if not total.empty:
                st.caption("Total response distribution by uploaded result. Percent columns show APIs inside each response bucket.")
                st.dataframe(display_track_comparison_df(total), use_container_width=True, hide_index=True, height=min(220, 72 + 38 * len(total)))
            if not detail.empty:
                st.caption("Track-level breakdown using Avg, Min and Max response metrics.")
                st.dataframe(display_track_comparison_df(detail), use_container_width=True, hide_index=True, height=height)

    if askai_df.empty and other_df.empty:
        return

    st.markdown('<div class="panel-title" style="margin-top:12px;">TRACK COMPARISON DASHBOARD</div>', unsafe_allow_html=True)
    render_section("CIQ Support Capabilities (Assets, Assessments and Support)", other_df, 360)
    render_section("CIQ Support Capabilities (Ask AI)", askai_df, 300)


def render_compare_tab(run_frames: List[Dict[str, pd.DataFrame]]) -> None:
    st.markdown('<div class="panel"><div class="panel-title">TRACK COMPARISON <span class="tag">Grouped by result</span></div>', unsafe_allow_html=True)

    askai_df, other_df = build_dashboard_track_comparison(run_frames)

    st.markdown("### AskAI Tracks")
    st.caption("Result includes the region. Repeated Track and Result cells are intentionally blank to keep Avg, Min and Max rows grouped together.")
    if not askai_df.empty:
        st.dataframe(display_track_comparison_df(askai_df), use_container_width=True, hide_index=True, height=420)
    else:
        st.info("No AskAI tracks found.")

    st.markdown("### Assets / Assessments / Home / Settings / Support Tracks")
    st.caption("Result includes the region. Repeated Track and Result cells are intentionally blank to keep Avg, Min and Max rows grouped together.")
    if not other_df.empty:
        st.dataframe(display_track_comparison_df(other_df), use_container_width=True, hide_index=True, height=620)
    else:
        st.info("No non-AskAI tracks found.")

    st.markdown("</div>", unsafe_allow_html=True)


def render_trends_tab(run_frames: List[Dict[str, pd.DataFrame]], compact: bool = False, show_table: bool = True) -> None:
    if not compact:
        st.markdown('<div class="panel"><div class="panel-title">TRENDS ACROSS RESULTS</div>', unsafe_allow_html=True)
    rows = []
    for frames in run_frames:
        row = summarize_run(frames["APIs"])
        row["Run"] = frames["Label"]
        row["Region"] = frames.get("Region", region_from_frames(frames))
        rows.append(row)
    summary = pd.DataFrame(rows)
    if len(summary) > 0:
        display_summary = summary.copy()
        display_summary["Result"] = [run_display_label(frames) for frames in run_frames]
        fig1 = px.line(display_summary, x="Result", y=["avg_sec", "p95_sec", "max_sec"], markers=True, title="Response Trend")
        fig1.update_layout(height=330 if compact else 420, xaxis_title="", yaxis_title="Seconds", margin=dict(l=8, r=8, t=40, b=95), legend_title="Metric")
        st.plotly_chart(fig1, use_container_width=True)

        if show_table:
            table = display_summary.rename(columns={
                "avg_sec": "Avg Sec",
                "p95_sec": "P95 Sec",
                "max_sec": "Max Sec",
                "success_rate": "Success %",
                "error_rate": "Error %",
                "sla_compliance": "SLA Pass %",
                "performance_score": "Health Score",
                "errors": "Errors",
                "samples": "Samples",
            })
            needed_cols = ["Result", "Region", "Avg Sec", "P95 Sec", "Max Sec", "Success %", "Error %", "SLA Pass %", "Health Score"]
            st.dataframe(table[safe_cols(table, needed_cols)], use_container_width=True, hide_index=True, height=220 if compact else None)
    if not compact:
        st.markdown("</div>", unsafe_allow_html=True)


def render_detailed_report_tab(run_frames: List[Dict[str, pd.DataFrame]]) -> None:
    df = combined_df(run_frames)
    st.markdown('<div class="panel"><div class="panel-title">DETAILED REPORT</div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    tracks = sorted(df["Feature"].dropna().astype(str).unique().tolist())
    selected_tracks = c1.multiselect("Track", tracks, default=tracks[: min(10, len(tracks))])
    selected_status = c2.multiselect("SLA Status", ["PASS", "FAIL"], default=["PASS", "FAIL"])
    sort_col = c3.selectbox("Sort by", ["Avg ResTime in sec", "95thPercentile Resp Time in Sec", "99thPercentile Resp Time in Sec", "MaxRes Time in sec", "errorCount", "sampleCount"])
    filtered = df[df["Feature"].isin(selected_tracks) & df["SLA Status"].isin(selected_status)].sort_values(sort_col, ascending=False)
    st.dataframe(filtered[standard_api_cols(filtered)], use_container_width=True, hide_index=True, height=650)
    st.markdown("</div>", unsafe_allow_html=True)


def goto_tab_button(label: str, tab_name: str, key: str) -> None:
    if st.button(label, key=key):
        st.session_state["nav_target"] = tab_name
        st.rerun()



def render_executive_dashboard(run_frames: List[Dict[str, pd.DataFrame]]) -> None:
    render_dashboard_header()

    st.markdown('<div class="panel-title">PROGRAMS</div>', unsafe_allow_html=True)
    program_options = [
        PROGRAM_SAAS,
        "Cisco IQ Onprem - Assets",
        "Cisco IQ Onprem - Risk App",
        "CX AI Assistant",
    ]
    active_program = st.session_state.get("active_program", PROGRAM_SAAS)
    if active_program not in program_options:
        active_program = PROGRAM_SAAS
    pcols = st.columns(4, gap="small")
    for col, program_name in zip(pcols, program_options):
        if col.button(program_name, key=f"program_tab_{program_name}", type="primary" if active_program == program_name else "secondary", use_container_width=True):
            st.session_state["active_program"] = program_name
            active_program = program_name
            st.rerun()

    if active_program != PROGRAM_SAAS:
        with st.container(border=True):
            st.markdown('<div class="panel-title">Coming Soon</div>', unsafe_allow_html=True)
            st.info(f"{active_program} is planned for Q4FY26. Dashboard enablement is in upcoming release windows.")
            render_saved_reports_table(show_title=False)
        return

    st.markdown('<div class="panel-title">PROGRAM TRACKS</div>', unsafe_allow_html=True)
    track_options = ["API", "UI", "Cloud Assist Connector", "Customer Inventory Benchmarking"]
    active_track = st.session_state.get("active_track", "API")
    if active_track not in track_options:
        active_track = "API"
    top_track_row = st.columns([4.3, 1.2], gap="small")
    with top_track_row[1]:
        st.markdown('<div class="region-field-label">Region</div>', unsafe_allow_html=True)
        region_focus = st.selectbox("Region", ["All", "US", "EMEA", "APJC"], key="dashboard_region_focus", label_visibility="collapsed")

    t1, t2, t3, t4 = top_track_row[0].columns([1.2, 1, 1.3, 1.6], gap="small")
    for col, track_name in zip([t1, t2, t3, t4], track_options):
        if col.button(track_name, key=f"track_tab_{track_name}", type="primary" if active_track == track_name else "secondary", use_container_width=True):
            st.session_state["active_track"] = track_name
            active_track = track_name
            st.rerun()

    if active_track != "API":
        with st.container(border=True):
            st.markdown(f'<div class="panel-title">{active_track}</div>', unsafe_allow_html=True)
            render_non_api_track_view(active_track)
        return

    selected_tab = dashboard_view_tabs()

    main_col, side_col = st.columns([4.35, .95], gap="medium")

    with side_col:
        selected_frames = get_filtered_frames(run_frames, forced_region=region_focus, forced_track=active_track)
        insights = auto_insights(selected_frames)
        st.markdown('<div class="side-card"><div class="panel-title">REPORT ACTIONS</div>', unsafe_allow_html=True)
        if st.session_state.get("excel_bytes"):
            st.download_button(
                "Download Excel Report",
                data=st.session_state.excel_bytes,
                file_name=st.session_state.report_file_name,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key="side_panel_excel_download",
                use_container_width=True,
            )
        else:
            st.info("Excel report is not available in this dashboard session.")
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown('<div class="side-card"><div class="panel-title">INSIGHTS</div>', unsafe_allow_html=True)
        for icon, color, text in insights:
            st.markdown(f'<div class="insight-item"><div class="dot" style="background:{color};">{icon}</div><div>{text}</div></div>', unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        try:
            dashboard_url = st.secrets.get("DASHBOARD_URL", "")
        except Exception:
            dashboard_url = ""
        if dashboard_url:
            st.markdown(f'<a class="primary-pill" href="{dashboard_url}?view=dashboard&tab=Overview" target="_blank" style="width:100%;text-align:center;">Open Dashboard in New Tab ↗</a>', unsafe_allow_html=True)

    with main_col:
        if not selected_frames:
            st.warning("No reports match the selected filters. Please update Data & Filters.")
            return

        df = combined_df(selected_frames)

        if selected_tab == "Track Comparison":
            render_compare_tab(selected_frames)
            return

        if selected_tab == "Chatbot":
            st.markdown('<div class="panel"><div class="panel-title">AI CHATBOT</div>', unsafe_allow_html=True)
            render_chatbot(selected_frames, key_suffix='tab')
            st.markdown("</div>", unsafe_allow_html=True)
            return
        if selected_tab == "Detailed Report":
            render_detailed_report_tab(selected_frames)
            return
        render_aggregated_or_comparison_summary(selected_frames)

        st.markdown('<div class="grid-3">', unsafe_allow_html=True)
        # Streamlit does not nest into raw grid well; use columns instead.
        st.markdown("</div>", unsafe_allow_html=True)

        c1, c2 = st.columns([1.35, 1], gap="medium")
        tracks = track_summary(df)

        with c1:
            with st.container(border=True):
                st.markdown('<div class="panel-title">Response Time</div>', unsafe_allow_html=True)
                if not tracks.empty:
                    chart_df = tracks.head(8).sort_values("P95_Sec")
                    plot_df = chart_df[["Feature", "Avg_Sec", "P95_Sec", "Max_Sec"]].rename(
                        columns={
                            "Avg_Sec": "Avg",
                            "P95_Sec": "95th Percentile",
                            "Max_Sec": "Max",
                        }
                    )
                    long_df = plot_df.melt(id_vars="Feature", var_name="Metric", value_name="Seconds")
                    fig = px.bar(long_df, x="Feature", y="Seconds", color="Metric", barmode="group", text="Seconds")
                    fig.update_traces(texttemplate="%{text:.1f}s", textposition="outside")
                    fig.update_layout(height=330, margin=dict(l=8, r=10, t=5, b=95), xaxis_title="", yaxis_title="Seconds", legend_title="")
                    st.plotly_chart(fig, use_container_width=True)
                goto_tab_button('View all APIs →', 'Detailed Report', 'view_all_apis_btn')

        with c2:
            with st.container(border=True):
                st.markdown('<div class="panel-title">SLA Status</div>', unsafe_allow_html=True)
                st.plotly_chart(sla_donut(df), use_container_width=True)
                goto_tab_button('View SLA Breaches →', 'Detailed Report', 'view_sla_breaches_btn')

        with st.container(border=True):
            st.markdown('<div class="panel-title">TRENDS DASHBOARD</div>', unsafe_allow_html=True)
            render_trends_tab(selected_frames, compact=True, show_table=True)

        with st.container(border=True):
            st.markdown('<div class="panel-title">SAVED REPORTS AVAILABLE</div>', unsafe_allow_html=True)
            render_saved_reports_table(show_title=False)

        with st.container(border=True):
            st.markdown('<div class="panel-title">TRACK COMPARISON SUMMARY <span class="tag">Total rows only</span></div>', unsafe_allow_html=True)
            askai_compare, other_compare = build_dashboard_track_comparison(selected_frames)

            if not askai_compare.empty:
                st.markdown("#### AskAI Tracks - Total")
                askai_total = askai_compare[askai_compare["_TrackKey"] == "Total"].copy()
                st.dataframe(display_track_comparison_df(askai_total), use_container_width=True, hide_index=True, height=220)

            if not other_compare.empty:
                st.markdown("#### Assets / Assessments / Home / Settings / Support Tracks - Total")
                other_total = other_compare[other_compare["_TrackKey"] == "Total"].copy()
                st.dataframe(display_track_comparison_df(other_total), use_container_width=True, hide_index=True, height=220)

            goto_tab_button('Open Full Track Comparison →', 'Track Comparison', 'overview_full_compare_btn')


def standard_api_cols(df: pd.DataFrame) -> List[str]:
    return safe_cols(df, ["Feature", "Scenario", "Endpoint", "sampleCount", "errorCount", "errorPct", "Avg ResTime in sec", "Min ResTime in sec", "MaxRes Time in sec", "90thPercentile Resp Time in Sec", "95thPercentile Resp Time in Sec", "99thPercentile Resp Time in Sec", "SLA Sec", "SLA Status", "SLA Breach Sec"])


def extract_top_n(question: str, default: int = 10) -> int:
    match = re.search(r"\btop\s+(\d+)|\bfirst\s+(\d+)|\b(\d+)\s+(?:slow|error|fail|api|apis)", question.lower())
    nums = [g for g in match.groups() if g] if match else []
    return max(1, min(100, int(nums[0]))) if nums else default


def metric_col(question: str) -> str:
    q = question.lower()
    if "p99" in q or "99" in q: return "99thPercentile Resp Time in Sec"
    if "p95" in q or "95" in q: return "95thPercentile Resp Time in Sec"
    if "p90" in q or "90" in q: return "90thPercentile Resp Time in Sec"
    if "max" in q or "maximum" in q: return "MaxRes Time in sec"
    if "min" in q or "minimum" in q: return "Min ResTime in sec"
    return "Avg ResTime in sec"


def match_rows(df: pd.DataFrame, question: str) -> pd.DataFrame:
    if df.empty: return df
    q = question.lower()
    searchable_cols = safe_cols(df, ["Feature","Scenario","Endpoint","API","SLA Status","Track Type"])
    stop = {"show","give","tell","what","which","where","when","how","the","and","or","for","api","apis","track","tracks","report","details","data","list","top","bottom","is","are","was","were","in","of","to","me","with","on","by","about","please"}
    tokens = [t for t in re.findall(r"[a-zA-Z0-9_./-]+", q) if len(t) >= 3 and t not in stop]
    if not tokens or not searchable_cols: return df.head(0)
    combined = pd.Series("", index=df.index, dtype=str)
    for col in searchable_cols:
        combined = combined + " " + df[col].astype(str).str.lower()
    mask = pd.Series(False, index=df.index)
    for token in tokens:
        mask = mask | combined.str.contains(re.escape(token), na=False)
    return df[mask].copy()



def chat_answer(question: str, run_frames: List[Dict[str, pd.DataFrame]]) -> Tuple[str, pd.DataFrame | None]:
    q = question.lower().strip()
    if not run_frames:
        return "Hi! Upload and generate a dashboard first, then I can answer questions about SLA, slow APIs, errors, regions, tracks, and comparisons.", None

    df = combined_df(run_frames)
    label = "selected report(s)"
    n = extract_top_n(q)
    mcol = metric_col(q)

    s = summarize_run(df)
    run_count = len(run_frames)
    regions = sorted(set([frames.get("Region", region_from_frames(frames)) for frames in run_frames]))
    region_text = ", ".join([r for r in regions if r and r != "Unknown"]) or "selected region(s)"

    # Friendly small talk.
    greetings = {"hi", "hello", "hey", "hii", "hai", "good morning", "good afternoon", "good evening"}
    farewells = {"bye", "goodbye", "see you", "thanks bye", "thank you bye"}
    thanks = {"thanks", "thank you", "thx", "super", "good", "great", "awesome"}

    if q in greetings or any(q.startswith(g + " ") for g in greetings):
        return (
            f"Hi! I’m ready to help with this JMeter report. "
            f"Current summary: **{s['transactions']:,} APIs**, **{s['samples']:,} samples**, "
            f"**{s['sla_compliance']}% SLA pass**, **{s['error_rate']}% error rate**, "
            f"and regions/runs: **{region_text}**. Ask me about slow APIs, SLA breaches, errors, tracks, or comparison.",
            None,
        )

    if q in farewells or any(w in q for w in ["bye", "goodbye", "see you"]):
        return (
            "Bye! Quick reminder before you go: the dashboard has SLA status, slow APIs, error APIs, region comparison, and Track Comparison. "
            "Come back anytime and ask me about any API, track, region, or SLA breach.",
            None,
        )

    if q in thanks or any(w in q for w in ["thank", "thanks", "awesome", "great job"]):
        return (
            "You’re welcome! I can still help with report questions like: top slow APIs, SLA breaches, worst tracks, top errors, P95/P99, sample count, or region comparison.",
            None,
        )

    if any(w in q for w in ["help", "what can you do", "examples", "sample questions", "how to ask"]):
        return (
            "You can ask me things like:\n\n"
            "- What is the overall SLA summary?\n"
            "- Which APIs breached SLA?\n"
            "- Show top 10 slow APIs by P95 or P99.\n"
            "- Which tracks are worst?\n"
            "- Show top error APIs.\n"
            "- Compare APJC vs EMEA vs US.\n"
            "- What is the report date, duration, users and devices?\n"
            "- Search for an API, endpoint, scenario, or track name.",
            None,
        )

    if any(w in q for w in ["context","date","duration","region","users","devices","concurrent"]):
        rows = []
        for f in run_frames:
            info = f.get("Run_Info")
            if info is not None and not info.empty:
                row = info.iloc[0].to_dict()
                row["Run"] = f["Label"]
                row["Region"] = f.get("Region", region_from_frames(f))
                rows.append(row)
        if rows:
            context = pd.DataFrame(rows)
            return "Here is the report context I found from the uploaded run/file details.", context[safe_cols(context, ["Run","Region","Concurrent Users","Devices Count","Date","Duration"])]
        return "Report context was not available in the uploaded file names or parsed metadata.", None

    if any(w in q for w in ["health","summary","overall","status","executive","overview"]):
        return (
            f"Overall for **{label}**: Health Score **{s['performance_score']}/100**, "
            f"SLA Compliance **{s['sla_compliance']}%**, Success Rate **{s['success_rate']}%**, "
            f"Error Rate **{s['error_rate']}%**, Avg Response **{s['avg_sec']} sec**, "
            f"P95 **{s['p95_sec']} sec**, Total APIs **{s['transactions']:,}**, "
            f"Samples **{s['samples']:,}**, Errors **{s['errors']:,}**.",
            None,
        )

    if any(w in q for w in ["compare", "comparison", "regression", "improve", "degrade", "apjc", "emea", "us"]):
        rows = []
        for frames in run_frames:
            row = summarize_run(frames["APIs"])
            row["Run"] = frames["Label"]
            row["Region"] = frames.get("Region", region_from_frames(frames))
            rows.append(row)
        comp = pd.DataFrame(rows)
        if not comp.empty:
            cols = ["Region", "Run", "avg_sec", "p95_sec", "max_sec", "success_rate", "error_rate", "sla_compliance", "performance_score", "errors", "samples"]
            return "Here is the comparison across uploaded runs/regions.", comp[safe_cols(comp, cols)].sort_values(["Region", "Run"])
        return "I could not find multiple run/region data to compare.", None

    if any(w in q for w in ["sla","breach","breached","violate","violation","pass","failed","fail"]):
        fail = df[df["SLA Status"] == "FAIL"].sort_values("SLA Breach Sec", ascending=False)
        if "pass" in q and "fail" not in q and "breach" not in q:
            ok = df[df["SLA Status"] == "PASS"].copy()
            return f"APIs passing SLA: **{len(ok):,}** out of **{len(df):,}** APIs.", ok[standard_api_cols(ok)].head(n)
        if fail.empty:
            return "Good news: I don’t see any SLA breaches in the selected report data.", None
        return f"Top {min(n,len(fail))} SLA breaches. SLA is based on AskAI <10 sec and other APIs <2 sec.", fail[standard_api_cols(fail)].head(n)

    if any(w in q for w in ["error","errors","failure","failures","errorpct"]):
        err = df[pd.to_numeric(df.get("errorCount",0), errors="coerce").fillna(0)>0].copy()
        if err.empty:
            return "No API errors found in the selected report data.", None
        sort_col = "errorPct" if "percent" in q or "pct" in q else "errorCount"
        return f"Top {min(n,len(err))} error APIs sorted by **{sort_col}**.", err.sort_values(sort_col, ascending=False)[standard_api_cols(err)].head(n)

    if any(w in q for w in ["track","tracks","feature","features"]):
        ts = track_summary(df)
        if ts.empty:
            return "No track/feature data found in the selected report.", None
        return "Worst tracks by P95, Avg Sec, Max Sec, Errors, and SLA Fail %.", ts.head(n)

    if any(w in q for w in ["sample","samples","count","volume","load"]):
        sample_df = df.sort_values("sampleCount", ascending=False)
        return f"Top {min(n,len(sample_df))} APIs by sample count.", sample_df[standard_api_cols(sample_df)].head(n)

    if any(w in q for w in ["p90","p95","p99","percentile","90","95","99","slow","latency","response","time","avg","maximum","minimum","max","min"]):
        if mcol not in df.columns:
            return f"{mcol} is not available in this report.", None
        top = df.sort_values(mcol, ascending=False)
        return f"Top {min(n,len(top))} APIs based on **{mcol}**.", top[standard_api_cols(top)].head(n)

    matched = match_rows(df, question)
    if not matched.empty:
        return f"I found {len(matched)} matching report rows for your search.", matched.sort_values(["SLA Breach Sec","Avg ResTime in sec","errorCount"], ascending=False)[standard_api_cols(matched)].head(n)

    return (
        "I can answer normal greetings and report-related questions. For this dashboard, please ask about SLA, slow APIs, P95/P99, errors, tracks, regions, samples, report context, or comparisons. "
        "For unrelated topics, I’ll keep the answer focused on this uploaded performance report.",
        None,
    )


def render_chatbot(run_frames: List[Dict[str, pd.DataFrame]], key_suffix: str = 'side') -> None:
    st.markdown('<div class="chat-card"><div class="chat-header">AI ASSISTANT</div>', unsafe_allow_html=True)
    st.write("Hi! I can chat normally and answer questions from this uploaded performance report.")
    with st.expander("Try asking me", expanded=True):
        st.write("- Hi / Bye\n- Give overall summary\n- Top slow APIs by P95 or P99\n- Which APIs breached SLA?\n- Top error APIs\n- Compare APJC, EMEA and US\n- Worst tracks\n- What is report date and duration?")
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg.get("table") is not None:
                st.dataframe(msg["table"], use_container_width=True, hide_index=True)
    question = st.chat_input("Ask anything about performance...", key=f"chat_input_{key_suffix}_{st.session_state.get('run_id', 'no_run')}")
    if question:
        st.session_state.messages.append({"role":"user","content":question,"table":None})
        answer, table = chat_answer(question, run_frames)
        st.session_state.messages.append({"role":"assistant","content":answer,"table":table})
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)


def build_non_api_track_summary(track_name: str) -> pd.DataFrame:
    uploads = normalize_saved_uploads(load_saved_uploads())
    rows = []
    for item in uploads:
        item_track = item.get("track") or infer_program_track(item.get("file_name", ""))[1]
        if item_track != track_name:
            continue
        rows.append({
            "File": item.get("file_name", ""),
            "Region": item.get("region", "Unknown"),
            "Date": item.get("date", "N/A"),
            "Duration": item.get("duration", "N/A"),
            "Uploaded At": item.get("uploaded_at", ""),
        })
    return pd.DataFrame(rows)


def render_non_api_track_view(track_name: str) -> None:
    if track_name == TRACK_UI:
        st.info("UI Lighthouse metrics dashboard (FCP, LCP, TBT, CLS, SI, Performance Score) is enabled for CSV uploads and summary view.")
    elif track_name == TRACK_CLOUD:
        st.info("Cloud Assist Connector dashboard is enabled for CSV uploads and latest report listing.")
    else:
        st.info("Customer Inventory Benchmarking dashboard is enabled for CSV uploads and latest report listing.")

    df = build_non_api_track_summary(track_name)
    if df.empty:
        st.warning(f"No saved {track_name} CSV reports yet. Upload from the main page to populate this view.")
        return
    st.dataframe(df, use_container_width=True, hide_index=True, height=min(440, 72 + 38 * len(df)))





SAVED_REPORTS_DIR = Path("saved_reports")
SAVED_REPORTS_META = SAVED_REPORTS_DIR / "latest_uploads.json"


def ensure_saved_reports_dir() -> None:
    SAVED_REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    if not SAVED_REPORTS_META.exists():
        SAVED_REPORTS_META.write_text("[]", encoding="utf-8")


def load_saved_uploads() -> List[Dict[str, str]]:
    ensure_saved_reports_dir()
    try:
        data = json.loads(SAVED_REPORTS_META.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else []
    except Exception:
        return []



def infer_saved_report_info(file_name: str) -> Dict[str, str]:
    stem = Path(file_name).stem
    upper = stem.upper()

    region = "Unknown"
    for item in ["APJC", "EMEA", "US", "AMER", "EU", "LATAM", "INDIA"]:
        if re.search(rf"(?:^|[_\-\s]){item}(?:$|[_\-\s])", upper):
            region = item
            break

    duration = "N/A"
    duration_match = re.search(r"(\d+)\s*[_\-\s]?\s*(HOUR|HOURS|HR|HRS)", upper)
    if duration_match:
        duration = f"{duration_match.group(1)} Hour"

    date = "N/A"
    date_match = re.search(
        r"(JANUARY|FEBRUARY|MARCH|APRIL|MAY|JUNE|JULY|AUGUST|SEPTEMBER|OCTOBER|NOVEMBER|DECEMBER|JAN|FEB|MAR|APR|JUN|JUL|AUG|SEP|SEPT|OCT|NOV|DEC)[_\- ]?(\d{1,2})[_\-, ]+(\d{4})",
        upper,
    )
    if date_match:
        month = date_match.group(1).title()
        day = date_match.group(2)
        year = date_match.group(3)
        date = f"{month}-{day}-{year}"

    users = "N/A"
    user_patterns = [
        r"(\d+(?:\.\d+)?\s*K?)\s*[_\-\s]*(?:CONCURRENT[_\-\s]*)?USERS?",
        r"(?:CONCURRENT[_\-\s]*)?USERS?[_\-\s]*(\d+(?:\.\d+)?\s*K?)",
        r"(\d+(?:\.\d+)?\s*K?)\s*[_\-\s]*VU\b",
        r"\bVU[_\-\s]*(\d+(?:\.\d+)?\s*K?)",
    ]
    for pattern in user_patterns:
        m = re.search(pattern, upper)
        if m:
            users = m.group(1).replace(" ", "")
            break

    devices = "N/A"
    device_patterns = [
        r"(\d+(?:\.\d+)?\s*K?)\s*[_\-\s]*DEVICES?",
        r"DEVICES?[_\-\s]*(\d+(?:\.\d+)?\s*K?)",
        # Common compact comparison naming: 50VU-100K, 100VU_100K
        r"\d+(?:\.\d+)?\s*K?\s*[_\-\s]*VU[_\-\s]*(\d+(?:\.\d+)?\s*K)\b",
        r"\d+(?:\.\d+)?\s*K?\s*[_\-\s]*USERS?[_\-\s]*(\d+(?:\.\d+)?\s*K)\b",
    ]
    for pattern in device_patterns:
        m = re.search(pattern, upper)
        if m:
            devices = m.group(1).replace(" ", "")
            break
    if devices != "N/A":
        devices = f"{devices} Devices"

    return {
        "region": region,
        "duration": duration,
        "date": date,
        "users": users,
        "devices": devices,
    }


def run_display_label(frames: Dict[str, pd.DataFrame]) -> str:
    """Short comparison label: Region UsersVU-Devices, never full filename."""
    label = str(frames.get("Label", ""))
    info = infer_saved_report_info(label)

    region = frames.get("Region", region_from_frames(frames))
    if not region or region == "Unknown":
        region = info.get("region", "Unknown")

    users = info.get("users", "N/A")
    devices = info.get("devices", "N/A")

    run_info = frames.get("Run_Info")
    if run_info is not None and not run_info.empty:
        row = run_info.iloc[0].to_dict()
        if not users or users == "N/A":
            users = str(row.get("Concurrent Users", row.get("Users", "N/A")))
        if not devices or devices == "N/A":
            devices = str(row.get("Devices Count", row.get("Devices", "N/A")))

    def clean_users(value: str) -> str:
        value = str(value).strip()
        value = re.sub(r"(?i)\s*(concurrent\s*)?users?\s*", "", value).strip()
        value = re.sub(r"(?i)\s*vu\s*", "", value).strip()
        return value if value and value.upper() != "N/A" else "NA"

    def clean_devices(value: str) -> str:
        value = str(value).strip()
        value = re.sub(r"(?i)\s*devices?\s*", "", value).strip()
        return value if value and value.upper() != "N/A" else "NA"

    users_clean = clean_users(users)
    devices_clean = clean_devices(devices)
    region_clean = region if region and region != "Unknown" else "Region"

    return f"{region_clean} {users_clean}VU-{devices_clean}"




def normalize_saved_uploads(existing: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """Remove duplicate saved reports from existing metadata and disk.
    Duplicates are detected by file_hash first, then file_name.
    """
    seen_hashes = set()
    seen_names = set()
    cleaned = []
    duplicates = []

    for item in existing:
        file_name = item.get("file_name", "")
        saved_name = item.get("saved_name", "")
        file_hash = item.get("file_hash", "")

        # Backfill hash for older saved files if missing.
        saved_path = SAVED_REPORTS_DIR / saved_name
        if not file_hash and saved_path.exists():
            try:
                file_hash = hashlib.sha256(saved_path.read_bytes()).hexdigest()
                item["file_hash"] = file_hash
            except Exception:
                file_hash = ""

        duplicate = False
        if file_hash and file_hash in seen_hashes:
            duplicate = True
        if file_name and file_name in seen_names:
            duplicate = True

        if duplicate:
            duplicates.append(item)
            continue

        if file_hash:
            seen_hashes.add(file_hash)
        if file_name:
            seen_names.add(file_name)
        cleaned.append(item)

    # Remove duplicate physical files.
    for item in duplicates:
        try:
            dup_path = SAVED_REPORTS_DIR / item.get("saved_name", "")
            if dup_path.exists():
                dup_path.unlink()
        except Exception:
            pass

    return cleaned


def remove_saved_upload(saved_name: str) -> None:
    ensure_saved_reports_dir()
    existing = load_saved_uploads()
    updated = [item for item in existing if item.get("saved_name") != saved_name]

    try:
        file_path = SAVED_REPORTS_DIR / saved_name
        if file_path.exists():
            file_path.unlink()
    except Exception:
        pass

    SAVED_REPORTS_META.write_text(json.dumps(updated, indent=2), encoding="utf-8")


def save_uploaded_files_to_latest(uploaded_files) -> None:
    ensure_saved_reports_dir()
    existing = normalize_saved_uploads(load_saved_uploads())
    existing_hashes = {item.get("file_hash") for item in existing if item.get("file_hash")}
    existing_names = {item.get("file_name") for item in existing if item.get("file_name")}

    skipped_duplicates = []

    for uploaded_file in uploaded_files:
        clean_name = Path(uploaded_file.name).name.replace(" ", "_")
        file_bytes = uploaded_file.getvalue()
        file_hash = hashlib.sha256(file_bytes).hexdigest()

        # Do not save duplicate reports. Hash match catches same content; file name catches same report uploaded again.
        if file_hash in existing_hashes or clean_name in existing_names:
            skipped_duplicates.append(clean_name)
            continue

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        saved_name = f"{timestamp}_{clean_name}"
        saved_path = SAVED_REPORTS_DIR / saved_name
        saved_path.write_bytes(file_bytes)

        info = infer_saved_report_info(clean_name)
        program_name, track_name = infer_program_track(clean_name)

        existing.insert(0, {
            "uploaded_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "file_name": clean_name,
            "saved_name": saved_name,
            "file_hash": file_hash,
            "region": info["region"],
            "date": info["date"],
            "duration": info["duration"],
            "users": info["users"],
            "devices": info["devices"],
            "program": program_name,
            "track": track_name,
        })

        existing_hashes.add(file_hash)
        existing_names.add(clean_name)

    keep = existing[:SAVED_REPORT_LIMIT]
    keep_names = {item["saved_name"] for item in keep}

    for old in existing[SAVED_REPORT_LIMIT:]:
        try:
            old_path = SAVED_REPORTS_DIR / old.get("saved_name", "")
            if old_path.exists():
                old_path.unlink()
        except Exception:
            pass

    for file_path in SAVED_REPORTS_DIR.glob("*"):
        if not file_path.is_file() or file_path.name == SAVED_REPORTS_META.name:
            continue
        if file_path.name not in keep_names:
            try:
                file_path.unlink()
            except Exception:
                pass

    SAVED_REPORTS_META.write_text(json.dumps(keep, indent=2), encoding="utf-8")

    if skipped_duplicates:
        st.info("Duplicate upload skipped: " + ", ".join(skipped_duplicates[:3]) + (" ..." if len(skipped_duplicates) > 3 else ""))


def save_uploaded_files_for_track(uploaded_files, track_name: str, program_name: str = PROGRAM_SAAS) -> None:
    ensure_saved_reports_dir()
    existing = normalize_saved_uploads(load_saved_uploads())
    existing_hashes = {item.get("file_hash") for item in existing if item.get("file_hash")}
    existing_names = {item.get("file_name") for item in existing if item.get("file_name")}
    skipped_duplicates = []

    for uploaded_file in uploaded_files:
        clean_name = Path(uploaded_file.name).name.replace(" ", "_")
        file_bytes = uploaded_file.getvalue()
        file_hash = hashlib.sha256(file_bytes).hexdigest()
        if file_hash in existing_hashes or clean_name in existing_names:
            skipped_duplicates.append(clean_name)
            continue

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        saved_name = f"{timestamp}_{clean_name}"
        saved_path = SAVED_REPORTS_DIR / saved_name
        saved_path.write_bytes(file_bytes)
        info = infer_saved_report_info(clean_name)

        existing.insert(0, {
            "uploaded_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "file_name": clean_name,
            "saved_name": saved_name,
            "file_hash": file_hash,
            "region": info["region"],
            "date": info["date"],
            "duration": info["duration"],
            "users": info["users"],
            "devices": info["devices"],
            "program": program_name,
            "track": track_name,
        })
        existing_hashes.add(file_hash)
        existing_names.add(clean_name)

    keep = existing[:SAVED_REPORT_LIMIT]
    keep_names = {item["saved_name"] for item in keep}
    for old in existing[SAVED_REPORT_LIMIT:]:
        try:
            old_path = SAVED_REPORTS_DIR / old.get("saved_name", "")
            if old_path.exists():
                old_path.unlink()
        except Exception:
            pass

    for file_path in SAVED_REPORTS_DIR.glob("*"):
        if not file_path.is_file() or file_path.name == SAVED_REPORTS_META.name:
            continue
        if file_path.name not in keep_names:
            try:
                file_path.unlink()
            except Exception:
                pass

    SAVED_REPORTS_META.write_text(json.dumps(keep, indent=2), encoding="utf-8")
    if skipped_duplicates:
        st.info("Duplicate upload skipped: " + ", ".join(skipped_duplicates[:3]) + (" ..." if len(skipped_duplicates) > 3 else ""))




def generate_dashboard_from_json_paths(json_paths: List[Path], labels: List[str]) -> None:
    """Generate the same Excel/Dashboard/Chatbot state from saved JSON files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)
        output_path = tmpdir_path / "JMeter_Report.xlsx"

        run_frames: List[Dict[str, pd.DataFrame]] = []
        for path, label in zip(json_paths, labels):
            run_frames.append(process_uploaded_file(path, label))

        if len(json_paths) == 1:
            build_report(json_paths[0], output_path)
        else:
            build_comparison_report(json_paths, labels, output_path)

        run_frames = add_region_to_frames(run_frames)
        excel_bytes = output_path.read_bytes()
        new_run_id = uuid.uuid4().hex

        dashboard_store[new_run_id] = {
            "run_frames": run_frames,
            "excel_bytes": excel_bytes,
            "report_file_name": "JMeter_Report.xlsx",
        }
        st.session_state.excel_bytes = excel_bytes
        st.session_state.run_frames = run_frames
        st.session_state.report_file_name = "JMeter_Report.xlsx"
        st.session_state.messages = []
        st.session_state.run_id = new_run_id


def sanitize_column_name(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", str(name).strip().lower()).strip("_")


def pick_first_matching_column(df: pd.DataFrame, patterns: List[str]) -> str | None:
    for col in df.columns:
        normalized = sanitize_column_name(col)
        if any(re.search(pattern, normalized) for pattern in patterns):
            return col
    return None


def to_numeric_series(df: pd.DataFrame, col: str | None) -> pd.Series:
    if not col or col not in df.columns:
        return pd.Series(dtype=float)
    series = pd.to_numeric(df[col], errors="coerce").dropna()
    return series.astype(float)


def make_api_like_row(feature: str, scenario: str, values: pd.Series, sla_sec: float, higher_is_better: bool = False) -> Dict[str, object]:
    if values.empty:
        avg_v = min_v = max_v = p90_v = p95_v = p99_v = 0.0
        sample_count = 0
    else:
        avg_v = round(float(values.mean()), 3)
        min_v = round(float(values.min()), 3)
        max_v = round(float(values.max()), 3)
        p90_v = round(float(values.quantile(0.90)), 3)
        p95_v = round(float(values.quantile(0.95)), 3)
        p99_v = round(float(values.quantile(0.99)), 3)
        sample_count = int(values.count())

    if higher_is_better:
        pass_status = avg_v >= float(sla_sec)
        error_count = int((values < float(sla_sec)).sum()) if not values.empty else 0
        breach_sec = round(max(float(sla_sec) - avg_v, 0.0), 3)
    else:
        pass_status = avg_v <= float(sla_sec)
        error_count = int((values > float(sla_sec)).sum()) if not values.empty else 0
        breach_sec = round(max(avg_v - float(sla_sec), 0.0), 3)

    error_pct = round((error_count / sample_count) * 100, 3) if sample_count else 0.0
    return {
        "Feature": feature,
        "Scenario": scenario,
        "Endpoint": scenario,
        "sampleCount": sample_count,
        "errorCount": error_count,
        "errorPct": error_pct,
        "Avg ResTime in sec": avg_v,
        "Min ResTime in sec": min_v,
        "MaxRes Time in sec": max_v,
        "90thPercentile Resp Time in Sec": p90_v,
        "95thPercentile Resp Time in Sec": p95_v,
        "99thPercentile Resp Time in Sec": p99_v,
        "SLA Sec": float(sla_sec),
        "SLA Status": "PASS" if pass_status else "FAIL",
        "SLA Breach Sec": breach_sec,
        "Track Type": feature,
    }


def build_api_like_df_from_csv(csv_path: Path, track_name: str) -> pd.DataFrame:
    raw = pd.read_csv(csv_path)
    if raw.empty:
        return pd.DataFrame(columns=standard_api_cols(pd.DataFrame(columns=[
            "Feature", "Scenario", "Endpoint", "sampleCount", "errorCount", "errorPct",
            "Avg ResTime in sec", "Min ResTime in sec", "MaxRes Time in sec",
            "90thPercentile Resp Time in Sec", "95thPercentile Resp Time in Sec", "99thPercentile Resp Time in Sec",
            "SLA Sec", "SLA Status", "SLA Breach Sec",
        ])))

    rows: List[Dict[str, object]] = []

    if track_name == TRACK_UI:
        metric_map = {
            "FCP": [r"\bfcp\b", r"first_contentful_paint"],
            "LCP": [r"\blcp\b", r"largest_contentful_paint"],
            "TBT": [r"\btbt\b", r"total_blocking_time"],
            "CLS": [r"\bcls\b", r"cumulative_layout_shift"],
            "SI": [r"\bsi\b", r"speed_index"],
            "PERFORMANCE": [r"performance", r"perf_score", r"score"],
        }
        for metric, patterns in metric_map.items():
            col = pick_first_matching_column(raw, patterns)
            series = to_numeric_series(raw, col)
            if series.empty:
                continue
            if metric == "PERFORMANCE":
                rows.append(make_api_like_row("UI", metric, series, UI_SLA_THRESHOLDS[metric], higher_is_better=True))
            else:
                rows.append(make_api_like_row("UI", metric, series, UI_SLA_THRESHOLDS[metric], higher_is_better=False))
    else:
        avg_col = pick_first_matching_column(raw, [r"\bavg\b", r"average", r"mean", r"response_time", r"res_time", r"latency"]) or pick_first_matching_column(raw, [r"\btime\b", r"sec", r"ms"])
        min_col = pick_first_matching_column(raw, [r"\bmin\b"])
        max_col = pick_first_matching_column(raw, [r"\bmax\b"])
        p90_col = pick_first_matching_column(raw, [r"\bp90\b", r"90th"])
        p95_col = pick_first_matching_column(raw, [r"\bp95\b", r"95th"])
        p99_col = pick_first_matching_column(raw, [r"\bp99\b", r"99th"])
        sample_col = pick_first_matching_column(raw, [r"sample", r"count", r"requests", r"hits"])
        error_col = pick_first_matching_column(raw, [r"error_count", r"errors", r"failed", r"failures"])
        error_pct_col = pick_first_matching_column(raw, [r"error_pct", r"error_percent", r"failure_pct", r"failure_percent"])
        feature_col = pick_first_matching_column(raw, [r"feature", r"track", r"module", r"component"])
        scenario_col = pick_first_matching_column(raw, [r"scenario", r"transaction", r"name", r"endpoint", r"api"])

        sla_sec = NON_API_LATENCY_SLA_SEC.get(track_name, 2.0)
        for idx, row in raw.iterrows():
            avg_v = float(pd.to_numeric(row.get(avg_col), errors="coerce") or 0)
            min_v = float(pd.to_numeric(row.get(min_col), errors="coerce") or avg_v)
            max_v = float(pd.to_numeric(row.get(max_col), errors="coerce") or avg_v)
            p90_v = float(pd.to_numeric(row.get(p90_col), errors="coerce") or avg_v)
            p95_v = float(pd.to_numeric(row.get(p95_col), errors="coerce") or avg_v)
            p99_v = float(pd.to_numeric(row.get(p99_col), errors="coerce") or avg_v)
            sample_count = int(pd.to_numeric(row.get(sample_col), errors="coerce") or 1)
            error_count = int(pd.to_numeric(row.get(error_col), errors="coerce") or 0)
            error_pct = float(pd.to_numeric(row.get(error_pct_col), errors="coerce") or (error_count / sample_count * 100 if sample_count else 0))
            feature = str(row.get(feature_col) or track_name)
            scenario = str(row.get(scenario_col) or f"{track_name}-{idx+1}")
            pass_status = (avg_v <= sla_sec and min_v <= sla_sec and max_v <= sla_sec and p95_v <= sla_sec)
            rows.append({
                "Feature": feature,
                "Scenario": scenario,
                "Endpoint": scenario,
                "sampleCount": sample_count,
                "errorCount": error_count,
                "errorPct": round(error_pct, 3),
                "Avg ResTime in sec": round(avg_v, 3),
                "Min ResTime in sec": round(min_v, 3),
                "MaxRes Time in sec": round(max_v, 3),
                "90thPercentile Resp Time in Sec": round(p90_v, 3),
                "95thPercentile Resp Time in Sec": round(p95_v, 3),
                "99thPercentile Resp Time in Sec": round(p99_v, 3),
                "SLA Sec": float(sla_sec),
                "SLA Status": "PASS" if pass_status else "FAIL",
                "SLA Breach Sec": round(max(avg_v - sla_sec, 0.0), 3),
                "Track Type": feature,
            })

    df = pd.DataFrame(rows)
    if df.empty:
        return pd.DataFrame(columns=[
            "Feature", "Scenario", "Endpoint", "sampleCount", "errorCount", "errorPct",
            "Avg ResTime in sec", "Min ResTime in sec", "MaxRes Time in sec",
            "90thPercentile Resp Time in Sec", "95thPercentile Resp Time in Sec", "99thPercentile Resp Time in Sec",
            "SLA Sec", "SLA Status", "SLA Breach Sec", "Track Type",
        ])
    return df


def build_excel_bytes_from_frames(run_frames: List[Dict[str, pd.DataFrame]]) -> bytes:
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        for index, frames in enumerate(run_frames, start=1):
            label = str(frames.get("Label", f"Run_{index}"))
            safe_label = re.sub(r"[^A-Za-z0-9_-]+", "_", label)[:20] or f"Run_{index}"
            apis_df = frames.get("APIs", pd.DataFrame())
            run_info = frames.get("Run_Info", pd.DataFrame())
            apis_df.to_excel(writer, index=False, sheet_name=f"{safe_label}_APIs"[:31])
            run_info.to_excel(writer, index=False, sheet_name=f"{safe_label}_Info"[:31])
    return output.getvalue()


def generate_dashboard_from_saved_csv(track_name: str, csv_path: Path, item: Dict[str, str] | None = None) -> None:
    label = Path((item or {}).get("file_name", csv_path.name)).stem
    inferred = infer_saved_report_info((item or {}).get("file_name", csv_path.name))
    region = (item or {}).get("region") or inferred.get("region", "Unknown")

    apis_df = build_api_like_df_from_csv(csv_path, track_name)
    run_info = pd.DataFrame([{
        "Report File": (item or {}).get("file_name", csv_path.name),
        "Concurrent Users": (item or {}).get("users") or inferred.get("users", "N/A"),
        "Devices Count": (item or {}).get("devices") or inferred.get("devices", "N/A"),
        "Date": (item or {}).get("date") or inferred.get("date", "N/A"),
        "Duration": (item or {}).get("duration") or inferred.get("duration", "N/A"),
        "Region": region,
        "Program": (item or {}).get("program", PROGRAM_SAAS),
        "Track": track_name,
    }])

    run_frames = [{
        "Label": label,
        "Region": region,
        "APIs": apis_df,
        "Transactions": pd.DataFrame(),
        "Errors": apis_df[apis_df.get("errorCount", 0) > 0].copy() if not apis_df.empty else pd.DataFrame(),
        "Run_Info": run_info,
    }]

    excel_bytes = build_excel_bytes_from_frames(run_frames)
    new_run_id = uuid.uuid4().hex
    report_name = f"{track_name.replace(' ', '_')}_Report.xlsx"

    dashboard_store[new_run_id] = {
        "run_frames": run_frames,
        "excel_bytes": excel_bytes,
        "report_file_name": report_name,
    }
    st.session_state.excel_bytes = excel_bytes
    st.session_state.run_frames = run_frames
    st.session_state.report_file_name = report_name
    st.session_state.messages = []
    st.session_state.run_id = new_run_id


def generate_dashboard_from_uploaded_csv_files(track_name: str, uploaded_files) -> None:
    run_frames: List[Dict[str, pd.DataFrame]] = []
    for uploaded_file in uploaded_files:
        with tempfile.NamedTemporaryFile(delete=False, suffix=f"_{Path(uploaded_file.name).name}") as tmp:
            tmp.write(uploaded_file.getvalue())
            temp_path = Path(tmp.name)
        inferred = infer_saved_report_info(uploaded_file.name)
        apis_df = build_api_like_df_from_csv(temp_path, track_name)
        run_info = pd.DataFrame([{
            "Report File": uploaded_file.name,
            "Concurrent Users": inferred.get("users", "N/A"),
            "Devices Count": inferred.get("devices", "N/A"),
            "Date": inferred.get("date", "N/A"),
            "Duration": inferred.get("duration", "N/A"),
            "Region": inferred.get("region", "Unknown"),
            "Program": PROGRAM_SAAS,
            "Track": track_name,
        }])
        run_frames.append({
            "Label": Path(uploaded_file.name).stem,
            "Region": inferred.get("region", "Unknown"),
            "APIs": apis_df,
            "Transactions": pd.DataFrame(),
            "Errors": apis_df[apis_df.get("errorCount", 0) > 0].copy() if not apis_df.empty else pd.DataFrame(),
            "Run_Info": run_info,
        })
        try:
            temp_path.unlink(missing_ok=True)
        except Exception:
            pass

    excel_bytes = build_excel_bytes_from_frames(run_frames)
    new_run_id = uuid.uuid4().hex
    report_name = f"{track_name.replace(' ', '_')}_Report.xlsx"
    dashboard_store[new_run_id] = {
        "run_frames": run_frames,
        "excel_bytes": excel_bytes,
        "report_file_name": report_name,
    }
    st.session_state.excel_bytes = excel_bytes
    st.session_state.run_frames = run_frames
    st.session_state.report_file_name = report_name
    st.session_state.messages = []
    st.session_state.run_id = new_run_id



def render_latest_uploads_panel() -> None:
    uploads = normalize_saved_uploads(load_saved_uploads())
    # Persist duplicate cleanup immediately so user sees clean list.
    try:
        SAVED_REPORTS_META.write_text(json.dumps(uploads[:SAVED_REPORT_LIMIT], indent=2), encoding="utf-8")
    except Exception:
        pass

    st.markdown(
        """
<div class="main-page-card upload-card latest-team-box">
  <h3>Latest Team Uploads</h3>
  <p>Latest 15 uploaded JMeter JSON reports are saved for team reference. Duplicate reports are automatically skipped.</p>
</div>
<style>
.latest-team-box {
    margin-top:10px !important;
    padding:10px 14px !important;
    max-width: 960px !important;
}
.latest-team-box h3 {
    margin:0 0 3px 0 !important;
    color:#0f2b68 !important;
    font-size:17px !important;
    line-height:1.15 !important;
}
.latest-team-box p {
    color:#667085 !important;
    font-size:12px !important;
    margin:0 !important;
}
.hero-title-box {
    padding:13px 20px !important;
}
.hero-title-box h1 {
    font-size:19px !important;
    line-height:1.12 !important;
}
.hero-subtitle {
    font-size:14px !important;
    margin-bottom:14px !important;
}
</style>
""",
        unsafe_allow_html=True,
    )

    if not uploads:
        st.info("No saved uploads yet. Upload JSON files and click Generate Results.")
        return

    saved_paths = []
    saved_labels = []
    for item in uploads:
        file_path = SAVED_REPORTS_DIR / item["saved_name"]
        if file_path.exists():
            saved_paths.append(file_path)
            saved_labels.append(Path(item["file_name"]).stem)

    if saved_paths:
        st.caption(f"Generate an executive dashboard and comparison report using the latest {len(saved_paths)} saved report(s).")
        saved_button_label = "Generate Comparison Dashboard" if len(saved_paths) > 1 else "Generate Dashboard From Latest Upload"
        if st.button(saved_button_label, key="generate_all_saved_uploads", use_container_width=True):
            try:
                generate_dashboard_from_json_paths(saved_paths, saved_labels)
                st.success(f"Generated dashboard, Excel report and chatbot from latest {len(saved_paths)} saved report(s).")
                st.rerun()
            except Exception as exc:
                st.error(f"Failed to generate from saved uploads: {exc}")

    header = st.columns([0.4, 2.8, 0.9, 1.35, 1.45, 1.35, 1.0])
    header[0].markdown("**#**")
    header[1].markdown("**File name**")
    header[2].markdown("**Region**")
    header[3].markdown("**Date / Duration**")
    header[4].markdown("**Uploaded at**")
    header[5].markdown("**Generate**")
    header[6].markdown("**Remove**")

    for index, item in enumerate(uploads, start=1):
        file_path = SAVED_REPORTS_DIR / item["saved_name"]
        inferred = infer_saved_report_info(item.get("file_name", ""))
        region = item.get("region") or inferred.get("region", "Unknown")
        date = item.get("date") or inferred.get("date", "N/A")
        duration = item.get("duration") or inferred.get("duration", "N/A")
        users = item.get("users") or inferred.get("users", "N/A")
        devices = item.get("devices")
        if not devices or str(devices).upper() == "N/A":
            devices = inferred.get("devices", "N/A")
        report_info = f"{date} / {duration}"
        tooltip = f"Generate dashboard for: Region={region}, Date={date}, Duration={duration}, Users={users}, Devices={devices}"

        c1, c2, c3, c4, c5, c6, c7 = st.columns([0.4, 2.8, 0.9, 1.35, 1.45, 1.35, 1.0])
        c1.write(f"#{index}")
        c2.write(item["file_name"])
        c3.write(region)
        c4.write(report_info)
        c5.write(item["uploaded_at"])

        if file_path.exists():
            if c6.button("Generate Results", help=tooltip, key=f"generate_saved_upload_{index}_{item['saved_name']}", use_container_width=True):
                try:
                    generate_dashboard_from_json_paths([file_path], [Path(item["file_name"]).stem])
                    st.success(f"Generated dashboard, Excel report and chatbot for: {item['file_name']} ({region}, {date}, {duration}).")
                    st.rerun()
                except Exception as exc:
                    st.error(f"Failed to generate saved report: {exc}")
        else:
            c6.warning("Missing")

        if c7.button("Remove", key=f"remove_saved_upload_{index}_{item['saved_name']}", use_container_width=True):
            remove_saved_upload(item["saved_name"])
            st.success(f"Removed saved report: {item['file_name']}")
            st.rerun()




def render_main_page(show_subtitle: bool = True) -> None:
    subtitle_html = ""
    st.markdown(
        f"""
<div class="hero-title-box">
  <h1>{APP_TITLE}</h1>
</div>
{subtitle_html}
""",
        unsafe_allow_html=True,
    )


def render_management_landing_page() -> None:
    uploads = normalize_saved_uploads(load_saved_uploads())[:SAVED_REPORT_LIMIT]
    st.markdown(
        f"""
<div class="hero-title-box">
  <h1>{APP_TITLE}</h1>
</div>
<div class="hero-subtitle">
  Management dashboard access is view-only. Please use the dashboard link shared by the performance team to review the latest results.
</div>
""",
        unsafe_allow_html=True,
    )
    st.markdown(
        """
<div class="main-page-card upload-card">
  <h3 style="margin-top:0;color:#0f2b68;">Performance Results Portal</h3>
  <p style="color:#475569;margin-bottom:10px;">Upload and report generation are restricted to the performance team.</p>
  <p style="color:#64748b;margin-bottom:0;">Management users can view dashboards generated from saved reports below.</p>
</div>
""",
        unsafe_allow_html=True,
    )
    if not uploads:
        st.info("No saved reports are available yet. Ask the performance team to upload and save reports.")
        return

    saved_paths = []
    saved_labels = []
    for item in uploads:
        file_path = SAVED_REPORTS_DIR / item.get("saved_name", "")
        if file_path.exists():
            saved_paths.append(file_path)
            saved_labels.append(Path(item.get("file_name", file_path.name)).stem)

    if saved_paths:
        if st.button(f"View Dashboard From Latest {len(saved_paths)} Saved Reports", type="primary", use_container_width=True):
            try:
                generate_dashboard_from_json_paths(saved_paths, saved_labels)
                st.session_state["dashboard_tab"] = "Overview"
                st.rerun()
            except Exception as exc:
                st.error(f"Failed to generate dashboard from saved reports: {exc}")

    render_saved_reports_table(uploads)


def render_api_saved_reports_compact() -> None:
    render_saved_reports_compact_for_track(TRACK_API, title="Saved API Reports", key_prefix="api")


def render_saved_reports_compact_for_track(track_name: str, title: str | None = None, key_prefix: str = "track") -> None:
    uploads = normalize_saved_uploads(load_saved_uploads())
    track_uploads = [
        item for item in uploads
        if (item.get("track") or infer_program_track(item.get("file_name", ""))[1]) == track_name
    ]
    if not track_uploads:
        st.info(f"No saved {track_name} reports yet.")
        return

    if title:
        st.markdown(f"**{title}**")
    else:
        st.markdown(f"**Saved {track_name} Reports**")

    st.markdown(
        """
<style>
.compact-saved-row {
    background: #f8fbff;
    border: 1px solid #dbe4f0;
    border-radius: 10px;
    padding: 10px;
    margin-bottom: 8px;
}
.compact-saved-cell-name {
    font-size: 14px;
    font-weight: 700;
    color: #0f172a;
}
.compact-saved-cell-date {
    font-size: 13px;
    color: #334155;
    text-align: right;
}
</style>
""",
        unsafe_allow_html=True,
    )

    for index, item in enumerate(track_uploads, start=1):
        file_path = SAVED_REPORTS_DIR / item.get("saved_name", "")
        inferred = infer_saved_report_info(item.get("file_name", ""))
        region = item.get("region") or inferred.get("region", "Unknown")
        users = item.get("users") or inferred.get("users", "N/A")
        devices = item.get("devices") or inferred.get("devices", "N/A")
        date = item.get("date") or inferred.get("date", "N/A")
        report_name = f"{region}, {users}VU, {devices}"

        st.markdown('<div class="compact-saved-row">', unsafe_allow_html=True)
        info_col, date_col = st.columns([2.2, 1], gap="small")
        info_col.markdown(f'<div class="compact-saved-cell-name">{report_name}</div>', unsafe_allow_html=True)
        date_col.markdown(f'<div class="compact-saved-cell-date">{date}</div>', unsafe_allow_html=True)

        action_generate_col, action_remove_col = st.columns(2, gap="small")
        if file_path.exists():
            if action_generate_col.button("Generate Results", key=f"{key_prefix}_compact_generate_{index}_{item.get('saved_name','')}", use_container_width=True):
                try:
                    if track_name == TRACK_API:
                        generate_dashboard_from_json_paths([file_path], [Path(item.get("file_name", file_path.name)).stem])
                    else:
                        generate_dashboard_from_saved_csv(track_name, file_path, item)
                    st.success(f"Generated {track_name} results for {item.get('file_name', file_path.name)}")
                    st.rerun()
                except Exception as exc:
                    st.error(f"Failed to generate saved report: {exc}")
        else:
            action_generate_col.warning("Missing")

        if action_remove_col.button("Remove", key=f"{key_prefix}_compact_remove_{index}_{item.get('saved_name','')}", use_container_width=True):
            remove_saved_upload(item.get("saved_name", ""))
            st.success("Removed saved report.")
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)


def saved_reports_rows(uploads: List[Dict[str, str]]) -> pd.DataFrame:
    rows = []
    for item in uploads:
        inferred = infer_saved_report_info(item.get("file_name", ""))
        rows.append({
            "File": item.get("file_name", ""),
            "Program": item.get("program") or infer_program_track(item.get("file_name", ""))[0],
            "Track": item.get("track") or infer_program_track(item.get("file_name", ""))[1],
            "Region": item.get("region") or inferred.get("region", "Unknown"),
            "Date": item.get("date") or inferred.get("date", "N/A"),
            "Duration": item.get("duration") or inferred.get("duration", "N/A"),
            "Users": item.get("users") or inferred.get("users", "N/A"),
            "Devices": item.get("devices") or inferred.get("devices", "N/A"),
            "Uploaded At": item.get("uploaded_at", ""),
        })
    return pd.DataFrame(rows)


def render_saved_reports_table(uploads: List[Dict[str, str]] | None = None, compact: bool = False, show_title: bool = True) -> None:
    if uploads is None:
        uploads = normalize_saved_uploads(load_saved_uploads())[:SAVED_REPORT_LIMIT]
    if show_title:
        st.markdown("#### Saved Reports Available")
    if not uploads:
        st.info("No saved reports are available yet.")
        return
    rows = saved_reports_rows(uploads)
    if compact:
        rows = rows[safe_cols(rows, ["File", "Region", "Date", "Uploaded At"])]
    st.dataframe(rows, use_container_width=True, hide_index=True, height=min(520, 72 + 38 * len(rows)))


def secret_value(*keys: str) -> str:
    for key in keys:
        try:
            value = st.secrets.get(key, "")
        except Exception:
            value = ""
        if value:
            return str(value)
    return ""


def team_upload_access_granted() -> bool:
    if st.session_state.get("team_authenticated"):
        return True

    expected_user = secret_value("UPLOAD_USERNAME", "USERNAME", "APP_USERNAME")
    expected_password = secret_value("UPLOAD_PASSWORD", "PASSWORD", "APP_PASSWORD", "UPLOAD_PASSCODE")
    if not expected_user and not expected_password:
        st.warning("Upload login is not configured. Add UPLOAD_USERNAME and UPLOAD_PASSWORD in Streamlit secrets.")
        return False

    left, center, right = st.columns([1, 1.45, 1])
    with center:
        st.markdown('<div class="login-form-wrap">', unsafe_allow_html=True)
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        login_clicked = st.button("Login to Upload Reports", type="primary", use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    valid_user = True if not expected_user else username == expected_user
    valid_password = password == expected_password
    if login_clicked:
        if valid_user and valid_password:
            st.session_state.team_authenticated = True
            st.rerun()
        st.error("Invalid username or password.")
    return False


def latest_saved_report_paths() -> Tuple[List[Path], List[str]]:
    uploads = normalize_saved_uploads(load_saved_uploads())
    paths = []
    labels = []
    for item in uploads:
        path = SAVED_REPORTS_DIR / item.get("saved_name", "")
        if path.exists():
            paths.append(path)
            labels.append(Path(item.get("file_name", path.name)).stem)
    return paths, labels


def load_static_saved_dashboard() -> bool:
    paths, labels = latest_saved_report_paths()
    if not paths:
        return False
    signature = "|".join(f"{path.name}:{path.stat().st_mtime_ns}" for path in paths if path.exists())
    if st.session_state.get("saved_dashboard_signature") == signature and st.session_state.get("run_frames"):
        return True
    generate_dashboard_from_json_paths(paths, labels)
    st.session_state["saved_dashboard_signature"] = signature
    st.session_state["run_id"] = "saved-dashboard"
    return True



def dashboard_url_for_run(run_id_value: str) -> str:
    return "?view=dashboard"






def render_action_cards() -> None:
    has_report = bool(st.session_state.get("run_id") and st.session_state.get("excel_bytes"))
    run_id_value = st.session_state.get("run_id", "")
    dashboard_href = "?view=dashboard&tab=Overview" if has_report else "#"
    chatbot_href = "?view=dashboard&tab=Chatbot" if has_report else "#"

    st.markdown(
        """
<style>
.action-card-title {
    margin:0 0 8px 0;
    color:#0f2b68;
    font-size:19px;
    font-weight:800;
}
.action-card-text {
    margin:0 0 16px 0;
    color:#667085;
    font-size:13px;
    line-height:1.45;
    min-height:58px;
}
.action-link {
    display:inline-block;
    background:linear-gradient(90deg,#4f46e5,#2563eb);
    color:white !important;
    text-decoration:none !important;
    padding:10px 14px;
    border-radius:12px;
    font-weight:800;
    font-size:13px;
    box-shadow:0 10px 22px rgba(37,99,235,.22);
}
.action-link.purple {
    background:linear-gradient(90deg,#6d28d9,#7c3aed);
}
.action-link.disabled {
    background:#e5e7eb;
    color:#667085 !important;
    box-shadow:none;
    pointer-events:none;
}
</style>
""",
        unsafe_allow_html=True,
    )

    c1, c2, c3 = st.columns(3)

    with c1:
        with st.container(border=True):
            st.markdown('<div class="action-card-title">Executive Dashboard</div>', unsafe_allow_html=True)
            st.markdown('<div class="action-card-text">Open the leadership-ready dashboard with KPIs, region comparison, heatmaps and drilldowns.</div>', unsafe_allow_html=True)
            link_class = "action-link" if has_report else "action-link disabled"
            st.markdown(f'<a class="{link_class}" href="{dashboard_href}" target="_blank">Open Dashboard ↗</a>', unsafe_allow_html=True)

    with c2:
        with st.container(border=True):
            st.markdown('<div class="action-card-title">Excel Report</div>', unsafe_allow_html=True)
            st.markdown('<div class="action-card-text">Download the generated workbook with Insights, APIs, Transactions, Errors and Comparison sheets.</div>', unsafe_allow_html=True)
            if has_report:
                st.download_button(
                    "⬇ Download Excel Report",
                    data=st.session_state.excel_bytes,
                    file_name=st.session_state.report_file_name,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    key="excel_download_inside_card",
                    use_container_width=True,
                )
            else:
                st.button("⬇ Download Excel Report", disabled=True, use_container_width=True, key="excel_download_disabled_inside_card")

    with c3:
        with st.container(border=True):
            st.markdown('<div class="action-card-title">AI Chatbot</div>', unsafe_allow_html=True)
            st.markdown('<div class="action-card-text">Open the dashboard chatbot and ask questions about SLA, slow APIs, errors, regions and comparisons.</div>', unsafe_allow_html=True)
            link_class = "action-link purple" if has_report else "action-link disabled"
            st.markdown(f'<a class="{link_class}" href="{chatbot_href}" target="_blank">Open Chatbot ↗</a>', unsafe_allow_html=True)

# Session state
if "excel_bytes" not in st.session_state: st.session_state.excel_bytes = None
if "run_frames" not in st.session_state: st.session_state.run_frames = []
if "report_file_name" not in st.session_state: st.session_state.report_file_name = "JMeter_Report.xlsx"
if "messages" not in st.session_state: st.session_state.messages = []
if "run_id" not in st.session_state: st.session_state.run_id = ""
if "team_authenticated" not in st.session_state: st.session_state.team_authenticated = False

if dashboard_only and run_id and run_id in dashboard_store:
    st.session_state.run_frames = dashboard_store[run_id]["run_frames"]
    st.session_state.excel_bytes = dashboard_store[run_id].get("excel_bytes")
    st.session_state.report_file_name = dashboard_store[run_id].get("report_file_name", "JMeter_Report.xlsx")

if dashboard_only:
    if not st.session_state.run_frames:
        load_static_saved_dashboard()
    if st.session_state.run_frames:
        render_executive_dashboard(st.session_state.run_frames)
    else:
        render_management_landing_page()
elif team_upload_view:
    if st.session_state.run_frames and not st.session_state.get("team_authenticated"):
        render_executive_dashboard(st.session_state.run_frames)
        st.stop()
    render_main_page(show_subtitle=st.session_state.get("team_authenticated", False))
    access_granted = team_upload_access_granted()
    if access_granted:
        st.markdown('<div class="panel-title">Program Track Uploads</div>', unsafe_allow_html=True)
        api_col, ui_col, cloud_col, inv_col = st.columns(4, gap="small")

        with api_col:
            with st.container(border=True):
                st.markdown("**API Metrics (.json)**")
                uploaded_files = st.file_uploader(
                    "Upload JMeter statistics.json file(s)",
                    type=["json"],
                    accept_multiple_files=True,
                    key="api_json_uploader",
                )
                st.checkbox(
                    "Save for team visibility",
                    value=True,
                    key="save_reports_checkbox",
                )
                generate_clicked = st.button(
                    "Generate API Results",
                    type="primary",
                    disabled=not uploaded_files,
                    key="generate_api_results",
                    use_container_width=True,
                )
                render_api_saved_reports_compact()

        if uploaded_files and generate_clicked:
            if st.session_state.get('save_reports_checkbox', True):
                save_uploaded_files_to_latest(uploaded_files)
            with tempfile.TemporaryDirectory() as tmpdir:
                tmpdir = Path(tmpdir)
                json_paths: List[Path] = []
                labels: List[str] = []
                run_frames: List[Dict[str, pd.DataFrame]] = []
                for idx, uploaded_file in enumerate(uploaded_files, start=1):
                    clean_name = uploaded_file.name.replace(" ", "_")
                    path = tmpdir / f"{idx}_{clean_name}"
                    path.write_bytes(uploaded_file.getvalue())
                    json_paths.append(path)
                    label = Path(uploaded_file.name).stem
                    labels.append(label)
                    run_frames.append(process_uploaded_file(path, label))
                output_path = tmpdir / "JMeter_Report.xlsx"
                try:
                    if len(json_paths) == 1:
                        build_report(json_paths[0], output_path)
                    else:
                        build_comparison_report(json_paths, labels, output_path)
                    run_frames = add_region_to_frames(run_frames)
                    excel_bytes = output_path.read_bytes()
                    new_run_id = uuid.uuid4().hex
                    dashboard_store[new_run_id] = {"run_frames": run_frames, "excel_bytes": excel_bytes, "report_file_name": "JMeter_Report.xlsx"}
                    st.session_state.excel_bytes = excel_bytes
                    st.session_state.run_frames = run_frames
                    st.session_state.report_file_name = "JMeter_Report.xlsx"
                    st.session_state.messages = []
                    st.session_state.run_id = new_run_id
                    st.toast("Report generated successfully.", icon="✅")
                    st.success("Dashboard generated. Share the dashboard link below with management.")
                    st.markdown(f'<a class="primary-pill" href="{dashboard_url_for_run(new_run_id)}" target="_blank">Open Management Dashboard ↗</a>', unsafe_allow_html=True)
                except Exception as exc:
                    st.error(f"Failed to generate report: {exc}")

        with ui_col:
            with st.container(border=True):
                st.markdown("**UI Metrics (.csv)**")
                ui_files = st.file_uploader("Upload UI CSV files", type=["csv"], accept_multiple_files=True, key="ui_csv_uploader")
                st.checkbox("Save for team visibility", value=True, key="save_ui_reports_checkbox")
                if st.button("Generate UI Results", key="generate_ui_results", type="primary", use_container_width=True, disabled=not ui_files):
                    if st.session_state.get("save_ui_reports_checkbox", True):
                        save_uploaded_files_for_track(ui_files, TRACK_UI)
                    generate_dashboard_from_uploaded_csv_files(TRACK_UI, ui_files)
                    st.success("Generated UI dashboard and report.")
                    st.rerun()
                render_saved_reports_compact_for_track(TRACK_UI, title="Saved UI Reports", key_prefix="ui")

        with cloud_col:
            with st.container(border=True):
                st.markdown("**Cloud Assist Connector (.csv)**")
                cloud_files = st.file_uploader("Upload Cloud Assist CSV files", type=["csv"], accept_multiple_files=True, key="cloud_csv_uploader")
                st.checkbox("Save for team visibility", value=True, key="save_cloud_reports_checkbox")
                if st.button("Generate Cloud Results", key="generate_cloud_results", type="primary", use_container_width=True, disabled=not cloud_files):
                    if st.session_state.get("save_cloud_reports_checkbox", True):
                        save_uploaded_files_for_track(cloud_files, TRACK_CLOUD)
                    generate_dashboard_from_uploaded_csv_files(TRACK_CLOUD, cloud_files)
                    st.success("Generated Cloud Assist dashboard and report.")
                    st.rerun()
                render_saved_reports_compact_for_track(TRACK_CLOUD, title="Saved Cloud Reports", key_prefix="cloud")

        with inv_col:
            with st.container(border=True):
                st.markdown("**Customer Inventory Benchmarking (.csv)**")
                inv_files = st.file_uploader("Upload Customer Inventory Benchmarking CSV files", type=["csv"], accept_multiple_files=True, key="inv_csv_uploader")
                st.checkbox("Save for team visibility", value=True, key="save_inventory_reports_checkbox")
                if st.button("Generate Inventory Results", key="generate_inventory_results", type="primary", use_container_width=True, disabled=not inv_files):
                    if st.session_state.get("save_inventory_reports_checkbox", True):
                        save_uploaded_files_for_track(inv_files, TRACK_INVENTORY)
                    generate_dashboard_from_uploaded_csv_files(TRACK_INVENTORY, inv_files)
                    st.success("Generated Customer Inventory Benchmarking dashboard and report.")
                    st.rerun()
                render_saved_reports_compact_for_track(TRACK_INVENTORY, title="Saved Inventory Reports", key_prefix="inventory")

        render_action_cards()
else:
    if st.session_state.run_frames:
        render_executive_dashboard(st.session_state.run_frames)
    else:
        render_management_landing_page()

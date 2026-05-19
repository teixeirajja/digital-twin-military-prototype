from __future__ import annotations

import math
import html
import base64
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from supabase import create_client, Client

st.set_page_config(
    page_title="Military Digital Twin",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# -----------------------------
# Styling only: Supabase data/login/permissions/dashboard logic preserved from the stable version.
# -----------------------------
CSS = """
<style>
/* ------------------------------------------------------------------
   BALANCED PROFESSIONAL MILITARY UI
   Less dark, more readable; data/login/permissions logic preserved.
-------------------------------------------------------------------*/
:root {
    --page: #eef2e6;
    --page2: #f7f8f1;
    --ink: #102015;
    --muted: #68745f;
    --panel: #ffffff;
    --panel-soft: #f9fbf3;
    --border: rgba(34, 75, 40, .16);
    --border-strong: rgba(34, 75, 40, .28);
    --green-900: #05200f;
    --green-800: #0b3418;
    --green-700: #14532d;
    --green-600: #166534;
    --green-500: #22c55e;
    --yellow: #d7b92f;
    --amber: #f59e0b;
    --red: #ef4444;
    --shadow: 0 16px 42px rgba(16, 32, 21, .10);
}

html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"] {
    background:
        radial-gradient(circle at 10% 0%, rgba(34, 197, 94, .10), transparent 28%),
        radial-gradient(circle at 90% 8%, rgba(215, 185, 47, .13), transparent 25%),
        linear-gradient(180deg, var(--page2) 0%, var(--page) 56%, #e7ecd9 100%) !important;
    color: var(--ink) !important;
}
.block-container {
    padding-top: 1.15rem;
    padding-bottom: 2.4rem;
    max-width: 1680px !important;
    width: min(1680px, 96vw) !important;
    padding-left: 2rem;
    padding-right: 2rem;
}
#MainMenu, footer, header {visibility: hidden;}
[data-testid="stToolbar"] {visibility: hidden; height: 0%; position: fixed;}
[data-testid="InputInstructions"] {display:none !important;}
[data-testid="stDecoration"], [data-testid="stStatusWidget"], [data-testid="stHeader"] {display: none;}

h1, h2, h3, h4, h5, h6, p, label, span, div {font-family: "Inter", "Segoe UI", Arial, sans-serif;}
h1, h2, h3, h4 {color: var(--ink) !important;}
[data-testid="stMarkdownContainer"] p {color: var(--muted);}
hr {border-color: rgba(34,75,40,.18) !important;}

/* Inputs */
.stTextInput input, .stPassword input, .stNumberInput input, .stDateInput input,
.stSelectbox [data-baseweb="select"], .stMultiSelect [data-baseweb="select"] {
    background: #ffffff !important;
    color: var(--ink) !important;
    border: 1px solid rgba(20, 83, 45, .23) !important;
    border-radius: 12px !important;
    min-height: 42px;
    box-shadow: 0 6px 18px rgba(16,32,21,.05) !important;
}
.stTextInput input::placeholder {color: rgba(16,32,21,.40) !important;}
.stSelectbox label, .stSlider label, .stCheckbox label, .stRadio label, .stTextInput label {
    color: #213322 !important;
    font-weight: 750 !important;
    font-size: .83rem !important;
}
.stCheckbox span {color:#213322 !important;}
[data-baseweb="popover"] {background:#ffffff !important; color:var(--ink) !important;}

/* Buttons */
.stButton > button, .stFormSubmitButton > button {
    border-radius: 12px !important;
    border: 1px solid rgba(20,83,45,.25) !important;
    background: #ffffff !important;
    color: var(--green-700) !important;
    font-weight: 850 !important;
    letter-spacing: .01em !important;
    min-height: 42px;
    box-shadow: 0 8px 22px rgba(16,32,21,.07) !important;
}
.stButton > button:hover, .stFormSubmitButton > button:hover {
    background: var(--green-700) !important;
    color: #ffffff !important;
    border-color: var(--green-700) !important;
}

/* Login */
.login-shell {max-width: 980px; margin: 6vh auto 0 auto;}
.login-hero {
    padding: 22px 24px;
    border-radius: 22px;
    background: linear-gradient(135deg, var(--green-900), var(--green-700));
    border: 1px solid rgba(255,255,255,.12);
    box-shadow: 0 28px 70px rgba(16,32,21,.26);
    color:#fff;
}
.login-hero-top {display:flex; align-items:center; justify-content:space-between; gap:18px;}
.login-brand {display:flex; align-items:center; gap:16px;}
.login-logo {width:54px; height:54px; border-radius:16px; background:rgba(255,255,255,.12); border:1px solid rgba(255,255,255,.20); display:flex; align-items:center; justify-content:center; font-size:1.45rem;}
.login-title {margin:0; color:#fff8cf !important; font-size:1.55rem; font-weight:950; letter-spacing:.10em; text-transform:uppercase;}
.login-subtitle {margin:6px 0 0 0; color:#d9e9c6 !important; font-size:.84rem; font-weight:700;}
.login-badge {color:#fff8cf; background:rgba(0,0,0,.18); border:1px solid rgba(255,248,207,.25); border-radius:999px; padding:9px 14px; font-size:.76rem; font-weight:900; text-transform:uppercase;}
.login-grid {margin-top:16px; border:1px solid var(--border); border-radius:22px; overflow:hidden; background:#fff; box-shadow: var(--shadow);}
.login-info {display:none;}
.login-form-panel {padding:24px; background:#ffffff;}
.login-form-title {color:var(--green-800) !important; font-size:1rem; font-weight:950; letter-spacing:.06em; text-transform:uppercase; margin:0 0 8px 0;}
.login-form-subtitle {color:var(--muted) !important; margin:0 0 16px 0; font-size:.84rem; font-weight:650;}
.login-demo {max-width:980px; margin:18px auto 0 auto; background:#f5f7ed; color:#475240; border:1px solid var(--border); border-radius:14px; padding:14px 16px; font-size:.80rem;}
.login-demo b {color:var(--green-800);} .login-demo code {background:#e7efdc; color:#14532d; padding:2px 6px; border-radius:7px;}
.login-foot {text-align:center; color:#677160; font-size:.76rem; margin-top:12px;}
[data-testid="stForm"] {
    max-width: 980px !important;
    margin: 16px auto 0 auto !important;
    background: #ffffff !important;
    border: 1px solid var(--border) !important;
    border-radius: 20px !important;
    padding: 18px !important;
    box-shadow: var(--shadow) !important;
}

/* Header */
.main-header {
    border-radius: 24px;
    padding: 20px 24px;
    background: linear-gradient(135deg, var(--green-900) 0%, var(--green-800) 58%, var(--green-700) 100%);
    color: #fff;
    margin: 0 0 18px 0;
    box-shadow: 0 22px 55px rgba(16,32,21,.22);
    display:flex; align-items:center; justify-content:space-between; gap:20px;
}
.header-left h1 {margin:0; color:#fff8cf !important; font-size:1.45rem; font-weight:950; letter-spacing:.10em; text-transform:uppercase;}
.header-left p {margin:7px 0 0 0; color:#d8e7c7 !important; font-size:.83rem; font-weight:700;}
.header-logout {display:inline-flex; align-items:center; justify-content:center; min-width:140px; padding:11px 16px; border-radius:14px; border:1px solid rgba(255,248,207,.30); color:#fff8cf !important; text-decoration:none !important; font-weight:900; background:rgba(0,0,0,.16);}
.header-logout:hover {background:rgba(255,255,255,.13); color:#fff !important;}

/* Navigation - Streamlit radio styled as pills.
   Important: this uses widgets, not href links, so the Supabase login session is not lost. */
.nav-card {
    padding: 8px;
    margin: 0 0 22px 0;
    border-radius: 999px;
    background: rgba(255,255,255,.78);
    border: 1px solid var(--border);
    box-shadow: 0 10px 28px rgba(16,32,21,.07);
}
[data-testid="stRadio"] > label {display:none !important;}
[data-testid="stRadio"] div[role="radiogroup"] {
    display:flex !important;
    flex-direction:row !important;
    flex-wrap:wrap !important;
    gap:8px !important;
    background: rgba(255,255,255,.78) !important;
    border: 1px solid var(--border) !important;
    border-radius: 999px !important;
    padding: 8px !important;
    width: fit-content !important;
    box-shadow: 0 10px 28px rgba(16,32,21,.07) !important;
}
[data-testid="stRadio"] div[role="radiogroup"] label {
    display:flex !important;
    align-items:center !important;
    justify-content:center !important;
    min-height:42px !important;
    padding: 0 18px !important;
    border-radius: 999px !important;
    border: 1px solid rgba(20,83,45,.18) !important;
    background: #ffffff !important;
    color: var(--green-800) !important;
    box-shadow: 0 5px 14px rgba(16,32,21,.05) !important;
    cursor:pointer !important;
    font-weight:850 !important;
}
[data-testid="stRadio"] div[role="radiogroup"] label:hover {
    background:#f3f7ee !important;
    border-color:rgba(20,83,45,.30) !important;
}
[data-testid="stRadio"] div[role="radiogroup"] label:has(input:checked) {
    background: linear-gradient(135deg, var(--green-800), var(--green-600)) !important;
    color:#fff8cf !important;
    border-color: var(--green-600) !important;
}
[data-testid="stRadio"] div[role="radiogroup"] label:has(input:checked) p {color:#fff8cf !important;}
[data-testid="stRadio"] div[role="radiogroup"] label p {
    color:inherit !important;
    font-size:.92rem !important;
    font-weight:850 !important;
}
[data-testid="stRadio"] div[role="radiogroup"] label input {display:none !important;}
[data-testid="stRadio"] div[role="radiogroup"] label > div:first-child {display:none !important;}
/* Section titles/cards */
.section-title {
    color: var(--green-900) !important;
    font-size:1.15rem; font-weight:950; margin:10px 0 14px;
    letter-spacing:.04em;
    border:1px solid var(--border);
    border-left: 6px solid var(--green-700);
    border-radius: 16px;
    padding: 14px 16px;
    background: #ffffff;
    box-shadow: var(--shadow);
}
.metric-card {
    background: #ffffff;
    border: 1px solid var(--border);
    border-radius: 18px;
    padding: 16px 18px;
    height: 148px;
    min-height: 148px;
    color: var(--ink);
    display:flex; flex-direction:column; justify-content:space-between;
    box-shadow: var(--shadow);
    position: relative;
    overflow:hidden;
}
.metric-card:before {content:""; position:absolute; left:0; top:0; bottom:0; width:5px; background: linear-gradient(180deg, var(--green-600), var(--yellow));}
.metric-card small {color:var(--green-700); font-size:.72rem; font-weight:950; text-transform:uppercase; letter-spacing:.07em;}
.metric-card h2 {font-size:clamp(1.45rem, 2.1vw, 2.0rem); line-height:1.08; margin: 10px 0 3px 0; font-weight:950; color:var(--green-900) !important; overflow-wrap:break-word;}
.metric-card p {margin:0; color:var(--muted); font-size:.78rem; font-weight:650;}
.soft-card, .info-card {
    padding: 18px; border-radius: 18px; background:#ffffff;
    border: 1px solid var(--border); box-shadow: var(--shadow);
}
.info-card h3 {margin:0 0 8px 0; font-size:1.05rem; color:var(--green-900) !important;}
.info-card p {margin:0 0 8px 0; color:var(--muted);}
.privacy-note {font-size:.80rem; color:#5d6758; background:#eef5e7; border:1px solid rgba(20,83,45,.13); padding:10px 12px; border-radius:12px; margin-bottom:12px;}
.band-list {display:grid; gap:10px; margin-top:10px;}
.band-row {display:grid; grid-template-columns: 150px 1fr 48px; gap:12px; align-items:center; color:#263427; font-weight:700; font-size:.86rem;}
.band-track {height:10px; border-radius:999px; background:#e4eadc; overflow:hidden; border:1px solid rgba(20,83,45,.12);}
.band-fill {height:100%; border-radius:999px; display:block;}
.action-box {background:linear-gradient(135deg,#ffffff,#f5f8ee); border:1px solid var(--border); border-radius:16px; padding:14px 16px; margin-top:10px;}
.action-box b {color:var(--green-900);} .action-box span {color:var(--muted);}
.footer-note {color:#697463;font-size:0.78rem;margin-top:16px;}

/* Alerts */
.stAlert {background:#ffffff !important; border: 1px solid var(--border) !important; color:var(--ink) !important; border-radius:16px !important; box-shadow: 0 10px 26px rgba(16,32,21,.05) !important;}
.stAlert p {color: var(--ink) !important;}

/* Tables */
.table-card {background:#ffffff; border:1px solid var(--border); border-radius:18px; box-shadow: var(--shadow); overflow:hidden; margin-top:12px; margin-bottom:24px;}
.table-head {padding:14px 16px; background:linear-gradient(90deg, var(--green-900), var(--green-700)); color:#fff8cf; display:flex; align-items:center; justify-content:space-between; gap:12px; border-bottom:1px solid rgba(255,255,255,.15);}
.table-head-title {font-weight:950; font-size:.90rem; letter-spacing:.07em; text-transform:uppercase; color:#fff8cf;}
.table-head-subtitle {font-size:.75rem; color:#dbe8c6; font-weight:750;}
.table-scroll {overflow-x:auto;}
table.pretty-table {width:100%; border-collapse: collapse; font-size:.82rem;}
.pretty-table th {text-align:left; background:#f3f6ed; color:#354333; font-weight:900; padding:10px 11px; border-bottom:1px solid rgba(20,83,45,.12); white-space:nowrap;}
.pretty-table td {padding:10px 11px; border-bottom:1px solid rgba(20,83,45,.08); color:#1d2a1e; vertical-align:middle; white-space:nowrap;}
.pretty-table tr:nth-child(even) td {background:#fbfcf7;}
.pretty-table tr:hover td {background:#eff6e9;}
.pretty-table tr:last-child td {border-bottom:none;}
.name-cell {font-weight:850; color:#102015;} .rank-cell {font-weight:850; color:#14532d;}
.value-wrap {display:flex; align-items:center; gap:8px; min-width:135px;}
.value-number {font-weight:900; min-width:36px; text-align:right; font-variant-numeric:tabular-nums; color:#102015;}
.mini-track {height:8px; flex:1; min-width:70px; border-radius:999px; background:#e3eadc; overflow:hidden; border:1px solid rgba(20,83,45,.10);}
.mini-fill {height:100%; border-radius:999px; display:block;} .fill-good {background:#22c55e;} .fill-warn {background:#f59e0b;} .fill-risk {background:#ef4444;}
.status-pill, .decision-pill {display:inline-flex; align-items:center; justify-content:center; padding:5px 10px; border-radius:999px; font-weight:900; font-size:.70rem; white-space:nowrap;}
.pill-pronto {background:#dcfce7; color:#166534; border:1px solid #86efac;} .pill-atencao {background:#fef3c7; color:#92400e; border:1px solid #fcd34d;} .pill-risco {background:#fee2e2; color:#991b1b; border:1px solid #fca5a5;}
.pill-executa {background:#dcfce7; color:#166534; border:1px solid #86efac;} .pill-monitorizar {background:#fef3c7; color:#92400e; border:1px solid #fcd34d;} .pill-retirar {background:#fee2e2; color:#991b1b; border:1px solid #fca5a5;}
.delta-neg {font-weight:950; color:#dc2626;} .delta-pos {font-weight:950; color:#16a34a;} .delta-zero {font-weight:950; color:#92400e;}

[data-testid="stDataFrame"] {background:#ffffff !important; border:1px solid var(--border) !important; border-radius:18px !important; overflow:hidden; box-shadow: var(--shadow) !important;}
.streamlit-expanderHeader {background:#ffffff !important; color:var(--green-900) !important; border:1px solid var(--border) !important; border-radius:12px !important;}

@media (max-width: 900px) {
    .block-container {padding-left: 1rem; padding-right: 1rem; width: 98vw !important;}
    .main-header {align-items:flex-start; flex-direction:column;}
    .header-left h1 {font-size:1.15rem;}
    .nav-card {width:100%;}
    [data-testid="stRadio"] div[role="radiogroup"] {width:100% !important;}
    [data-testid="stRadio"] div[role="radiogroup"] label {flex:1 !important;}
    .band-row {grid-template-columns: 115px 1fr 42px;}
}


/* Digital Twin individual enhanced */
.twin-hero {
    background: linear-gradient(135deg, rgba(255,255,255,.96), rgba(246,249,239,.96));
    border: 1px solid var(--border);
    border-left: 6px solid var(--green-700);
    border-radius: 22px;
    padding: 18px 20px;
    box-shadow: var(--shadow);
    margin-bottom: 16px;
}
.twin-hero h2 {margin:0; color:var(--green-900) !important; font-weight:950; letter-spacing:.04em;}
.twin-hero p {margin:7px 0 0 0; color:var(--muted) !important; font-weight:650;}
.twin-panel {background:#ffffff; border:1px solid var(--border); border-radius:20px; padding:18px; box-shadow:var(--shadow); margin-bottom:18px;}
.twin-panel h3 {margin:0 0 12px 0; color:var(--green-900) !important; font-size:1.03rem; font-weight:950; letter-spacing:.02em;}
.twin-grid {display:grid; grid-template-columns: repeat(4, minmax(130px, 1fr)); gap:12px; margin: 8px 0 18px 0;}
.twin-mini {background:linear-gradient(135deg,#ffffff,#f8fbf2); border:1px solid var(--border); border-radius:16px; padding:13px 14px; min-height:92px; box-shadow:0 8px 22px rgba(16,32,21,.05);}
.twin-mini small {display:block; color:var(--green-700); font-size:.70rem; font-weight:950; text-transform:uppercase; letter-spacing:.06em; margin-bottom:8px;}
.twin-mini strong {display:block; color:var(--green-900); font-size:1.22rem; line-height:1.1; font-weight:950; word-break:break-word;}
.twin-mini span {display:block; color:var(--muted); font-size:.76rem; margin-top:5px; font-weight:650;}
.twin-rec {border-radius:16px; border:1px solid rgba(20,83,45,.16); background:#f4f8ee; padding:14px 15px; color:#223324; margin-top:10px;}
.twin-rec b {color:var(--green-900);}
.twin-badge-row {display:flex; gap:8px; flex-wrap:wrap; margin-top:10px;}
.twin-badge {display:inline-flex; align-items:center; padding:6px 10px; border-radius:999px; font-size:.75rem; font-weight:900; border:1px solid var(--border); background:#fff; color:var(--green-800);}
.twin-badge.good {background:#dcfce7; border-color:#86efac; color:#166534;}
.twin-badge.warn {background:#fef3c7; border-color:#fcd34d; color:#92400e;}
.twin-badge.risk {background:#fee2e2; border-color:#fca5a5; color:#991b1b;}

.twin-silhouette-card {
    background:
        radial-gradient(circle at 45% 8%, rgba(134,239,172,.18), transparent 28%),
        radial-gradient(circle at 85% 20%, rgba(250,204,21,.14), transparent 24%),
        linear-gradient(180deg, #06110b 0%, #020704 100%);
    border: 1px solid rgba(255,248,207,.22);
    border-radius: 24px;
    padding: 14px;
    box-shadow: 0 24px 60px rgba(3, 7, 18, .30);
    margin-bottom: 18px;
    overflow: hidden;
}
.twin-silhouette-top {
    display:flex;
    align-items:center;
    justify-content:space-between;
    gap:12px;
    padding: 6px 8px 12px 8px;
}
.twin-silhouette-top h3 {
    margin:0 !important;
    color:#fff8cf !important;
    font-size:1.02rem !important;
    font-weight:950 !important;
    letter-spacing:.04em;
    text-transform:uppercase;
}
.twin-model-pill {
    display:inline-flex;
    align-items:center;
    padding:7px 10px;
    border-radius:999px;
    background:rgba(255,255,255,.08);
    border:1px solid rgba(255,248,207,.20);
    color:#fff8cf;
    font-size:.72rem;
    font-weight:900;
}
.twin-silhouette-img {
    width:100%;
    max-height:760px;
    object-fit:contain;
    display:block;
    border-radius:18px;
    background:#020704;
    border:1px solid rgba(255,255,255,.07);
}
.twin-legend-dark {
    display:flex;
    gap:12px;
    flex-wrap:wrap;
    align-items:center;
    justify-content:center;
    margin-top:12px;
    color:#d9e9c6;
    font-size:.78rem;
    font-weight:800;
}
.legend-dot {width:11px; height:11px; border-radius:999px; display:inline-block; margin-right:6px; vertical-align:-1px;}
.legend-green {background:#22c55e;} .legend-yellow {background:#facc15;} .legend-red {background:#f97316;}
.twin-zone-summary {
    margin-top:12px;
    border-radius:16px;
    border:1px solid rgba(255,248,207,.18);
    background:rgba(255,255,255,.06);
    padding:12px 13px;
    color:#d9e9c6;
    font-size:.82rem;
    line-height:1.45;
}
.twin-zone-summary b {color:#fff8cf;}

@media (max-width: 900px) {.twin-grid {grid-template-columns: repeat(2, minmax(130px, 1fr));}}

</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

ROLE_LABELS = {
    "admin": "Administrador",
    "comandante": "Comandante",
    "treinador": "Treinador",
    "militar": "Militar",
}

STATUS_ORDER = ["Pronto", "Atenção", "Risco"]

# -----------------------------
# Supabase connection
# -----------------------------
@st.cache_resource(show_spinner=False)
def base_client() -> Client:
    try:
        url = st.secrets["supabase"]["url"]
        key = st.secrets["supabase"]["anon_key"]
    except Exception:
        st.error("Faltam os secrets do Supabase. Vai a Streamlit Cloud > Manage app > Settings > Secrets.")
        st.code('[supabase]\nurl = "https://...supabase.co"\nanon_key = "..."', language="toml")
        st.stop()
    return create_client(url, key)


def client_with_session() -> Client:
    client = base_client()
    access = st.session_state.get("access_token")
    refresh = st.session_state.get("refresh_token")
    if access and refresh:
        try:
            client.auth.set_session(access, refresh)
        except Exception:
            pass
    return client


def sb_select(table: str, columns: str = "*", order: Optional[str] = None, desc: bool = False, filters: Optional[List[Tuple[str, str, Any]]] = None) -> List[Dict[str, Any]]:
    client = client_with_session()
    query = client.table(table).select(columns)
    if filters:
        for col, op, value in filters:
            if op == "eq":
                query = query.eq(col, value)
            elif op == "in":
                query = query.in_(col, value)
            elif op == "gte":
                query = query.gte(col, value)
            elif op == "lte":
                query = query.lte(col, value)
    if order:
        query = query.order(order, desc=desc)
    res = query.execute()
    return res.data or []


def sb_insert(table: str, payload: Dict[str, Any]) -> None:
    client = client_with_session()
    client.table(table).insert(payload).execute()


def sb_insert_many(table: str, payloads: List[Dict[str, Any]]) -> None:
    if not payloads:
        return
    client = client_with_session()
    client.table(table).insert(payloads).execute()

# -----------------------------
# Auth
# -----------------------------
def logout() -> None:
    try:
        client_with_session().auth.sign_out()
    except Exception:
        pass
    for key in ["access_token", "refresh_token", "profile", "user_email", "page"]:
        st.session_state.pop(key, None)
    try:
        st.query_params.clear()
    except Exception:
        pass
    st.rerun()


def login_page() -> None:
    st.markdown(
        """
        <div class="login-shell">
            <div class="login-hero">
                <div class="login-hero-top">
                    <div class="login-brand">
                        <div class="login-logo">🛡️</div>
                        <div>
                            <h1 class="login-title">Digital Twin Militar</h1>
                            <p class="login-subtitle">Acesso autenticado ao protótipo</p>
                        </div>
                    </div>
                    <div class="login-badge">● Sistema ativo</div>
                </div>
            </div>
            <div class="login-grid">
                <div class="login-info">
                    <h3>Plataforma operacional</h3>
                    <p>Entrada restrita por perfil. O comandante acede à visão da unidade; cada militar vê apenas os seus próprios dados.</p>
                    <div class="login-feature"><div class="login-dot"></div><div><strong>Dashboard de prontidão</strong><span>Estado da força, risco, recuperação e evolução física.</span></div></div>
                    <div class="login-feature"><div class="login-dot"></div><div><strong>Digital Twin individual</strong><span>Disponível para o militar, com carga muscular e alertas personalizados.</span></div></div>
                    <div class="login-feature"><div class="login-dot"></div><div><strong>Simulação de treino</strong><span>Teste de impacto antes da execução real.</span></div></div>
                </div>
                <div class="login-form-panel">
                    <p class="login-form-title">🔐 Identificação</p>
                    <p class="login-form-subtitle">Introduz as credenciais autorizadas para aceder ao sistema.</p>
        """,
        unsafe_allow_html=True,
    )

    with st.form("login_form"):
        email = st.text_input("Utilizador / Email", placeholder="cap.teixeira@militarytwin.pt")
        password = st.text_input("Password", type="password", placeholder="••••••••")
        submitted = st.form_submit_button("Entrar", use_container_width=True)

    if submitted:
        try:
            client = base_client()
            response = client.auth.sign_in_with_password({"email": email.strip(), "password": password})
            session = response.session
            user = response.user
            if not session or not user:
                st.error("Login inválido.")
                st.stop()

            st.session_state["access_token"] = session.access_token
            st.session_state["refresh_token"] = session.refresh_token
            st.session_state["user_email"] = user.email

            auth_client = client_with_session()
            profile_res = auth_client.table("profiles").select("*").eq("id", user.id).single().execute()
            st.session_state["profile"] = profile_res.data
            st.session_state["page"] = "dashboard"
            st.rerun()
        except Exception as exc:
            st.error("Não foi possível iniciar sessão. Confirma o email, password e se o utilizador está criado no Supabase Auth.")
            st.caption(str(exc))

    st.markdown(
        """
                    <div class="login-demo">
                        <b>Credenciais demo</b><br>
                        Comandante: <code>cap.teixeira@militarytwin.pt</code> / <code>Cmd2026!</code><br>
                        Militar: <code>hugo.dias@militarytwin.pt</code> / <code>Mil2026!</code>
                    </div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def require_login() -> Dict[str, Any]:
    profile = st.session_state.get("profile")
    if not profile:
        login_page()
        st.stop()
    return profile

# -----------------------------
# Data helpers
# -----------------------------
def df_from(table: str, **kwargs) -> pd.DataFrame:
    data = sb_select(table, **kwargs)
    return pd.DataFrame(data)


def latest_by(df: pd.DataFrame, group_col: str, date_col: str) -> pd.DataFrame:
    if df.empty:
        return df
    return df.sort_values(date_col).drop_duplicates(group_col, keep="last")


def get_soldiers() -> pd.DataFrame:
    return df_from("soldiers", order="full_name")


def get_soldier_for_profile(profile_id: str) -> Optional[Dict[str, Any]]:
    data = sb_select("soldiers", filters=[("profile_id", "eq", profile_id)])
    return data[0] if data else None


def assemble_snapshot() -> pd.DataFrame:
    soldiers = get_soldiers()
    if soldiers.empty:
        return pd.DataFrame()

    # The soldiers table also has a column called "status" (active/limited/etc.).
    # The dashboard needs the operational readiness status from readiness_scores
    # (Pronto/Atenção/Risco). Rename the soldier status to avoid pandas creating
    # status_x/status_y and breaking the charts.
    soldiers = soldiers.rename(columns={"id": "soldier_id", "status": "availability_status"})

    ids = soldiers["soldier_id"].tolist()
    readiness = df_from("readiness_scores", order="score_date", desc=True, filters=[("soldier_id", "in", ids)])
    tests = df_from("physical_tests", order="test_date", desc=True, filters=[("soldier_id", "in", ids)])
    daily = df_from("daily_records", order="record_date", desc=True, filters=[("soldier_id", "in", ids)])

    readiness_l = latest_by(readiness, "soldier_id", "score_date") if not readiness.empty else pd.DataFrame()
    tests_l = latest_by(tests, "soldier_id", "test_date") if not tests.empty else pd.DataFrame()
    daily_l = latest_by(daily, "soldier_id", "record_date") if not daily.empty else pd.DataFrame()

    df = soldiers.copy()
    if not readiness_l.empty:
        df = df.merge(readiness_l.drop(columns=["id", "created_at"], errors="ignore"), on="soldier_id", how="left")
    if not tests_l.empty:
        df = df.merge(tests_l.drop(columns=["id", "created_at"], errors="ignore"), on="soldier_id", how="left")
    if not daily_l.empty:
        df = df.merge(daily_l.drop(columns=["id", "created_at"], errors="ignore"), on="soldier_id", how="left")

    # Defensive fallback if a future schema change creates status_x/status_y again.
    if "status" not in df.columns:
        if "status_y" in df.columns:
            df["status"] = df["status_y"]
        elif "readiness_status" in df.columns:
            df["status"] = df["readiness_status"]
        else:
            df["status"] = "Atenção"

    for col in ["readiness_score", "injury_risk", "recovery_score", "cooper_m", "fatigue_score", "sleep_hours"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    df["status"] = df["status"].fillna("Atenção").astype(str)
    return df


def status_class(status: str) -> str:
    if status == "Pronto":
        return "pill-pronto"
    if status == "Atenção":
        return "pill-atencao"
    return "pill-risco"


def metric_card(label: str, value: Any, caption: str) -> None:
    st.markdown(f"""
    <div class="metric-card">
        <small>{label}</small>
        <h2>{value}</h2>
        <p>{caption}</p>
    </div>
    """, unsafe_allow_html=True)


def apply_chart_style(fig: go.Figure, height: int = 460) -> go.Figure:
    """Professional light military styling for Plotly figures."""
    fig.update_layout(
        height=height,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="#ffffff",
        font=dict(family="Inter, Arial, sans-serif", color="#213322"),
        title=dict(font=dict(size=16, color="#05200f"), x=0.02),
        margin=dict(l=28, r=24, t=54, b=34),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(color="#354333"),
            bgcolor="rgba(255,255,255,.75)",
        ),
    )
    fig.update_xaxes(gridcolor="rgba(20,83,45,.10)", zerolinecolor="rgba(20,83,45,.18)", linecolor="rgba(20,83,45,.18)")
    fig.update_yaxes(gridcolor="rgba(20,83,45,.10)", zerolinecolor="rgba(20,83,45,.18)", linecolor="rgba(20,83,45,.18)")
    return fig


def _safe(value: Any) -> str:
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return "—"
    return html.escape(str(value))


def _status_pill(value: Any) -> str:
    status = str(value or "Atenção")
    cls = status_class(status)
    return f'<span class="status-pill {cls}">{html.escape(status)}</span>'


def _decision_pill(value: Any) -> str:
    decision = str(value or "—")
    if decision == "Executa":
        cls = "pill-executa"
    elif decision == "Monitorizar":
        cls = "pill-monitorizar"
    else:
        cls = "pill-retirar"
    return f'<span class="decision-pill {cls}">{html.escape(decision)}</span>'


def _bar_cell(value: Any, polarity: str = "good", suffix: str = "") -> str:
    try:
        val = float(value)
    except Exception:
        return _safe(value)
    pct = max(0, min(100, val))
    if polarity == "risk":
        fill = "fill-risk" if pct >= 65 else "fill-warn" if pct >= 40 else "fill-good"
    else:
        fill = "fill-good" if pct >= 75 else "fill-warn" if pct >= 55 else "fill-risk"
    shown = f"{int(round(val))}{suffix}"
    return (
        '<div class="value-wrap">'
        f'<span class="value-number">{shown}</span>'
        '<span class="mini-track">'
        f'<span class="mini-fill {fill}" style="width:{pct:.0f}%"></span>'
        '</span></div>'
    )


def _delta_cell(value: Any) -> str:
    try:
        val = int(round(float(value)))
    except Exception:
        return _safe(value)
    cls = "delta-pos" if val > 0 else "delta-neg" if val < 0 else "delta-zero"
    sign = "+" if val > 0 else ""
    return f'<span class="{cls}">{sign}{val}</span>'


def render_pretty_table(
    df: pd.DataFrame,
    columns: Dict[str, str],
    title: str,
    subtitle: str = "",
    bar_columns: Optional[Dict[str, str]] = None,
    percent_columns: Optional[List[str]] = None,
    delta_columns: Optional[List[str]] = None,
) -> None:
    """Renders small/medium operational tables as product-style HTML cards."""
    if df.empty:
        st.info("Sem dados para apresentar.")
        return

    bar_columns = bar_columns or {}
    percent_columns = percent_columns or []
    delta_columns = delta_columns or []
    use_cols = [c for c in columns.keys() if c in df.columns]

    html_rows = []
    for _, row in df[use_cols].iterrows():
        cells = []
        for col in use_cols:
            value = row[col]
            if col == "status":
                cell = _status_pill(value)
            elif col == "Decisão":
                cell = _decision_pill(value)
            elif col in delta_columns:
                cell = _delta_cell(value)
            elif col in bar_columns:
                cell = _bar_cell(value, polarity=bar_columns[col], suffix="%")
            elif col in percent_columns:
                cell = f"{int(round(float(value)))}%" if pd.notna(value) else "—"
            elif col == "full_name":
                cell = f'<span class="name-cell">{_safe(value)}</span>'
            elif col == "rank":
                cell = f'<span class="rank-cell">{_safe(value)}</span>'
            else:
                if isinstance(value, (int, float, np.integer, np.floating)) and pd.notna(value):
                    cell = f"{value:.1f}" if isinstance(value, float) and not float(value).is_integer() else f"{int(value)}"
                else:
                    cell = _safe(value)
            cells.append(f"<td>{cell}</td>")
        html_rows.append("<tr>" + "".join(cells) + "</tr>")

    head = "".join(f"<th>{html.escape(label)}</th>" for col, label in columns.items() if col in use_cols)
    subtitle_html = f'<div class="table-head-subtitle">{html.escape(subtitle)}</div>' if subtitle else ""
    # Important: keep the HTML left-aligned. If this string is indented,
    # Markdown may render it as a code block instead of real HTML.
    table_html = (
        f'<div class="table-card">'
        f'<div class="table-head">'
        f'<div class="table-head-title">{html.escape(title)}</div>'
        f'{subtitle_html}'
        f'</div>'
        f'<div class="table-scroll">'
        f'<table class="pretty-table">'
        f'<thead><tr>{head}</tr></thead>'
        f'<tbody>{"".join(html_rows)}</tbody>'
        f'</table>'
        f'</div>'
        f'</div>'
    )
    st.markdown(table_html, unsafe_allow_html=True)

# -----------------------------
# Visual digital twin
# -----------------------------
def _to_float(value: Any, default: Optional[float] = None) -> Optional[float]:
    try:
        if value is None or (isinstance(value, float) and math.isnan(value)):
            return default
        return float(value)
    except Exception:
        return default


def _fmt_pct(value: Any) -> str:
    v = _to_float(value)
    return "—" if v is None else f"{int(round(v))}%"


def _fmt_num(value: Any, suffix: str = "", decimals: int = 0) -> str:
    v = _to_float(value)
    if v is None:
        return "—"
    if decimals == 0:
        return f"{int(round(v))}{suffix}"
    return f"{v:.{decimals}f}{suffix}"


def muscle_color(value: Any) -> str:
    v = _to_float(value, 0) or 0
    if v >= 80:
        return "#dc2626"
    if v >= 65:
        return "#f97316"
    if v >= 50:
        return "#facc15"
    return "#22c55e"


def muscle_level(value: Any) -> str:
    v = _to_float(value, 0) or 0
    if v >= 80:
        return "Crítico"
    if v >= 65:
        return "Elevado"
    if v >= 50:
        return "Moderado"
    return "Controlado"



def _read_image_as_data_uri(path: Path) -> Optional[str]:
    try:
        if not path.exists():
            return None
        encoded = base64.b64encode(path.read_bytes()).decode("utf-8")
        return f"data:image/png;base64,{encoded}"
    except Exception:
        return None


def twin_image_asset(sex: str) -> Tuple[Optional[str], str]:
    """Return the dashboard-ready male/female body-scan asset as a data URI."""
    asset_dir = Path(__file__).resolve().parent / "assets"
    is_female = str(sex).upper().strip() == "F"
    file_name = "twin_female.png" if is_female else "twin_male.png"
    label = "Modelo feminino" if is_female else "Modelo masculino"
    return _read_image_as_data_uri(asset_dir / file_name), label


def render_twin_silhouette_asset(muscle: Dict[str, Any], sex: str, info: Dict[str, Any]) -> bool:
    """Render high-quality generated silhouette image; returns False if asset is missing."""
    data_uri, model_label = twin_image_asset(sex)
    if not data_uri:
        return False
    top_group = info.get("top", {}).get("Grupo muscular", "—")
    top_load = int(info.get("top", {}).get("Carga", 0) or 0)
    critical = info.get("critical", []) or []
    attention = info.get("attention", []) or []
    if critical:
        zone_text = f"Zonas críticas: {', '.join(critical)}"
    elif attention:
        zone_text = f"Zonas em atenção: {', '.join(attention)}"
    else:
        zone_text = "Sem zonas musculares em carga crítica."
    st.markdown(
        f"""
        <div class="twin-silhouette-card">
            <div class="twin-silhouette-top">
                <h3>Silhueta de carga muscular</h3>
                <span class="twin-model-pill">{html.escape(model_label)}</span>
            </div>
            <img class="twin-silhouette-img" src="{data_uri}" alt="Digital Twin corporal" />
            <div class="twin-legend-dark">
                <span><i class="legend-dot legend-green"></i>Bom / equilibrado</span>
                <span><i class="legend-dot legend-yellow"></i>Atenção</span>
                <span><i class="legend-dot legend-red"></i>Risco / fadiga</span>
            </div>
            <div class="twin-zone-summary">
                <b>Maior carga atual:</b> {html.escape(str(top_group))} · {top_load}%<br>
                <b>Leitura automática:</b> {html.escape(zone_text)}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    return True

def digital_twin_figure(muscle: Dict[str, Any], sex: str = "M", title: str = "Digital Twin — carga muscular") -> go.Figure:
    """Improved body-map silhouette with male/female proportions and muscle overlays."""
    is_female = str(sex).upper() == "F"
    shoulder_w = 0.30 if is_female else 0.36
    waist_w = 0.18 if is_female else 0.22
    hip_w = 0.28 if is_female else 0.24

    fig = go.Figure()
    base = "rgba(226,232,218,.96)"
    outline = "rgba(15,32,21,.55)"

    fig.add_shape(type="circle", x0=0.435, y0=0.835, x1=0.565, y1=0.965, line=dict(color=outline, width=1.5), fillcolor=base)
    fig.add_shape(type="rect", x0=0.475, y0=0.785, x1=0.525, y1=0.835, line=dict(color=outline, width=1), fillcolor=base)
    torso_path = (
        f"M {0.50-shoulder_w/2:.3f},0.785 "
        f"C {0.50-shoulder_w/2-.030:.3f},0.720 {0.50-waist_w/2:.3f},0.575 {0.50-waist_w/2:.3f},0.465 "
        f"L {0.50-hip_w/2:.3f},0.365 "
        f"L {0.50+hip_w/2:.3f},0.365 "
        f"L {0.50+waist_w/2:.3f},0.465 "
        f"C {0.50+waist_w/2:.3f},0.575 {0.50+shoulder_w/2+.030:.3f},0.720 {0.50+shoulder_w/2:.3f},0.785 Z"
    )
    fig.add_shape(type="path", path=torso_path, line=dict(color=outline, width=1.5), fillcolor=base)
    fig.add_shape(type="path", path="M 0.315,0.745 C 0.235,0.700 0.205,0.575 0.215,0.385 L 0.285,0.385 C 0.290,0.545 0.325,0.640 0.370,0.720 Z", line=dict(color=outline, width=1), fillcolor=base)
    fig.add_shape(type="path", path="M 0.685,0.745 C 0.765,0.700 0.795,0.575 0.785,0.385 L 0.715,0.385 C 0.710,0.545 0.675,0.640 0.630,0.720 Z", line=dict(color=outline, width=1), fillcolor=base)
    fig.add_shape(type="path", path="M 0.385,0.365 L 0.485,0.365 L 0.470,0.070 L 0.375,0.070 Z", line=dict(color=outline, width=1), fillcolor=base)
    fig.add_shape(type="path", path="M 0.515,0.365 L 0.615,0.365 L 0.625,0.070 L 0.530,0.070 Z", line=dict(color=outline, width=1), fillcolor=base)

    zones = [
        ("Ombros", "shoulders", "M 0.325,0.770 C 0.405,0.820 0.595,0.820 0.675,0.770 L 0.630,0.720 C 0.560,0.748 0.440,0.748 0.370,0.720 Z", 0.50, 0.755),
        ("Peito", "chest", "M 0.390,0.705 C 0.445,0.735 0.555,0.735 0.610,0.705 L 0.590,0.610 C 0.540,0.635 0.460,0.635 0.410,0.610 Z", 0.50, 0.665),
        ("Costas", "back", "M 0.405,0.590 L 0.595,0.590 L 0.575,0.500 L 0.425,0.500 Z", 0.50, 0.545),
        ("Core", "core", "M 0.425,0.485 L 0.575,0.485 L 0.555,0.370 L 0.445,0.370 Z", 0.50, 0.425),
        ("Braços", "arms", "M 0.260,0.690 C 0.225,0.610 0.220,0.500 0.230,0.395 L 0.285,0.395 C 0.288,0.520 0.315,0.625 0.352,0.700 Z", 0.265, 0.540),
        ("Braços", "arms", "M 0.740,0.690 C 0.775,0.610 0.780,0.500 0.770,0.395 L 0.715,0.395 C 0.712,0.520 0.685,0.625 0.648,0.700 Z", 0.735, 0.540),
        ("Pernas", "legs", "M 0.390,0.350 L 0.485,0.350 L 0.475,0.185 L 0.385,0.185 Z", 0.435, 0.265),
        ("Pernas", "legs", "M 0.515,0.350 L 0.610,0.350 L 0.615,0.185 L 0.525,0.185 Z", 0.565, 0.265),
        ("Gémeos", "calves", "M 0.385,0.175 L 0.475,0.175 L 0.468,0.075 L 0.378,0.075 Z", 0.425, 0.125),
        ("Gémeos", "calves", "M 0.525,0.175 L 0.615,0.175 L 0.622,0.075 L 0.532,0.075 Z", 0.575, 0.125),
    ]
    for label, key, path, ax, ay in zones:
        val = int(round(_to_float(muscle.get(key), 0) or 0))
        fig.add_shape(type="path", path=path, line=dict(color="rgba(255,255,255,.85)", width=2), fillcolor=muscle_color(val), opacity=0.86)
        fig.add_annotation(x=ax, y=ay, text=f"{label}<br><b>{val}%</b>", showarrow=False, font=dict(color="#ffffff", size=11), align="center")

    fig.add_annotation(x=0.50, y=0.025, text="Verde normal · Amarelo atenção · Laranja/vermelho sobrecarga", showarrow=False, font=dict(color="#52604f", size=11), align="center")
    fig.update_xaxes(visible=False, range=[0, 1], fixedrange=True)
    fig.update_yaxes(visible=False, range=[0, 1], fixedrange=True)
    fig.update_layout(
        height=600,
        title=dict(text=title, x=0.02, font=dict(size=16, color="#05200f")),
        margin=dict(l=6, r=6, t=48, b=18),
        plot_bgcolor="#ffffff",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#213322", family="Inter, Arial, sans-serif"),
    )
    return fig


def render_twin_grid(title: str, items: List[Tuple[str, str, str]]) -> None:
    cards = []
    for label, value, caption in items:
        cards.append(
            '<div class="twin-mini">'
            f'<small>{html.escape(str(label))}</small>'
            f'<strong>{html.escape(str(value))}</strong>'
            f'<span>{html.escape(str(caption))}</span>'
            '</div>'
        )
    st.markdown(
        f'<div class="twin-panel"><h3>{html.escape(title)}</h3><div class="twin-grid">{"".join(cards)}</div></div>',
        unsafe_allow_html=True,
    )


def muscle_summary(muscle: Dict[str, Any]) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    labels = {
        "chest": "Peito",
        "back": "Costas",
        "shoulders": "Ombros",
        "arms": "Braços",
        "core": "Core",
        "legs": "Pernas",
        "calves": "Gémeos",
    }
    rows = []
    for key, label in labels.items():
        val = int(round(_to_float(muscle.get(key), 0) or 0))
        rows.append({"key": key, "Grupo muscular": label, "Carga": val, "Nível": muscle_level(val), "Cor": muscle_color(val)})
    chart = pd.DataFrame(rows)
    top = chart.sort_values("Carga", ascending=False).iloc[0].to_dict()
    low = chart.sort_values("Carga", ascending=True).iloc[0].to_dict()
    upper = float(chart[chart["key"].isin(["chest", "back", "shoulders", "arms"])] ["Carga"].mean())
    lower = float(chart[chart["key"].isin(["legs", "calves"])] ["Carga"].mean())
    push = float(chart[chart["key"].isin(["chest", "shoulders", "arms"])] ["Carga"].mean())
    pull = float(chart[chart["key"].isin(["back"])] ["Carga"].mean())
    critical = chart[chart["Carga"] >= 80]["Grupo muscular"].tolist()
    attention = chart[(chart["Carga"] >= 65) & (chart["Carga"] < 80)]["Grupo muscular"].tolist()
    info = {
        "top": top,
        "low": low,
        "upper": upper,
        "lower": lower,
        "push": push,
        "pull": pull,
        "critical": critical,
        "attention": attention,
        "global_load": int(round(chart["Carga"].mean())),
    }
    return chart, info


def twin_recommendation(info: Dict[str, Any], latest: Dict[str, Any]) -> Tuple[str, str, str]:
    readiness = _to_float(latest.get("readiness_score"), 50) or 50
    risk = _to_float(latest.get("injury_risk"), 50) or 50
    recovery = _to_float(latest.get("recovery_score"), 50) or 50
    top_group = str(info["top"].get("Grupo muscular", "—"))
    if info["critical"]:
        title = "Reduzir carga localizada"
        msg = f"Evitar estímulos intensos em {', '.join(info['critical'])}. Priorizar mobilidade, recuperação ativa e controlo de dor/fadiga."
        status = "risk"
    elif risk >= 65 or recovery < 55 or readiness < 60:
        title = "Treino adaptado recomendado"
        msg = f"O estado atual pede controlo de carga. Manter treino leve/moderado e evitar acumular volume em {top_group}."
        status = "warn"
    elif info["attention"]:
        title = "Controlar volume"
        msg = f"Carga moderada/elevada em {', '.join(info['attention'])}. O treino pode avançar, mas sem novo estímulo intenso consecutivo."
        status = "warn"
    else:
        title = "Carga muscular equilibrada"
        msg = "Não existem zonas críticas. Pode manter o plano, registando feedback pós-treino e resposta de recuperação."
        status = "good"
    return title, msg, status

# -----------------------------
# Pages
# -----------------------------
def top_bar(profile: Dict[str, Any]) -> str:
    role = profile.get("role")
    page_options = ["Dashboard", "Militar", "Digital Twin", "Simular treino", "Admin"]
    if role == "militar":
        page_options = ["Militar", "Digital Twin", "Simular treino"]
    elif role == "comandante":
        page_options = ["Dashboard", "Militar", "Simular treino"]
    elif role == "treinador":
        page_options = ["Dashboard", "Militar", "Digital Twin", "Simular treino"]

    st.markdown(f"""
    <div class="main-header">
        <div class="header-left">
            <h1>Military Digital Twin</h1>
            <p>Sessão iniciada · {html.escape(str(profile.get('rank','')))} {html.escape(str(profile.get('full_name','')))} · {html.escape(str(ROLE_LABELS.get(profile.get('role'), profile.get('role'))))}</p>
        </div>
        <a class="header-logout" href="?logout=1" target="_self">Terminar sessão</a>
    </div>
    """, unsafe_allow_html=True)

    # Do not navigate with raw HTML links here. In Streamlit Cloud, href navigation can
    # restart the browser session and drop st.session_state, which sends the user back
    # to login. A Streamlit radio keeps navigation inside the active authenticated session.
    current = st.session_state.get("page", page_options[0])
    if current not in page_options:
        current = page_options[0]
        st.session_state["page"] = current

    page = st.radio(
        "Navegação",
        page_options,
        index=page_options.index(current),
        horizontal=True,
        label_visibility="collapsed",
        key=f"nav_page_{role}",
    )
    st.session_state["page"] = page
    return page

def commander_dashboard(profile: Dict[str, Any]) -> None:
    st.markdown('<div class="section-title">Dashboard do comandante</div>', unsafe_allow_html=True)
    df = assemble_snapshot()
    if df.empty:
        st.warning("Ainda não há dados acessíveis para este utilizador.")
        return

    states = ["Todos"] + STATUS_ORDER
    c1, c2, c3 = st.columns(3)
    with c1:
        state = st.selectbox("Estado", states)
    with c2:
        min_ready = st.slider("Prontidão mínima", 0, 100, 0)
    with c3:
        show_risk = st.checkbox("Mostrar só risco elevado", value=False)

    view = df.copy()
    if state != "Todos" and "status" in view.columns:
        view = view[view["status"] == state]
    if "readiness_score" in view.columns:
        view = view[view["readiness_score"].fillna(0) >= min_ready]
    if show_risk and "injury_risk" in view.columns:
        view = view[view["injury_risk"].fillna(0) >= 60]

    total = len(df)
    ready = int((df["status"] == "Pronto").sum()) if "status" in df else 0
    attention = int((df["status"] == "Atenção").sum()) if "status" in df else 0
    risk = int((df["status"] == "Risco").sum()) if "status" in df else 0
    avg_ready = int(round(df["readiness_score"].dropna().mean())) if "readiness_score" in df and not df["readiness_score"].dropna().empty else "—"

    m1, m2, m3, m4, m5 = st.columns(5)
    with m1: metric_card("Militares analisados", total, "")
    with m2: metric_card("Prontos", ready, "prontidão ≥ 75")
    with m3: metric_card("Atenção", attention, "55 ≤ prontidão < 75")
    with m4: metric_card("Risco", risk, "prontidão < 55 ou risco alto")
    with m5: metric_card("Prontidão média", f"{avg_ready}%" if avg_ready != "—" else "—", "média da unidade")

    st.divider()
    if view.empty:
        st.warning("Nenhum militar corresponde aos filtros selecionados.")
        return

    g1, g2 = st.columns([1, 1])
    with g1:
        chart_df = view.sort_values("readiness_score", ascending=True).copy()
        fig = px.bar(
            chart_df,
            x="readiness_score",
            y="full_name",
            color="status",
            category_orders={"status": STATUS_ORDER},
            color_discrete_map={"Pronto": "#22c55e", "Atenção": "#f59e0b", "Risco": "#ef4444"},
            labels={"readiness_score": "Prontidão", "full_name": "Militar", "status": "Estado"},
            title="Prontidão por militar",
        )
        fig.update_layout(legend_title_text="Estado")
        fig = apply_chart_style(fig, height=480)
        st.plotly_chart(fig, use_container_width=True)
    with g2:
        fig = px.scatter(
            view,
            x="readiness_score",
            y="injury_risk",
            size="recovery_score",
            color="status",
            category_orders={"status": STATUS_ORDER},
            hover_name="full_name",
            color_discrete_map={"Pronto": "#22c55e", "Atenção": "#f59e0b", "Risco": "#ef4444"},
            labels={"readiness_score": "Prontidão", "injury_risk": "Risco de lesão", "recovery_score": "Recuperação", "status": "Estado"},
            title="Prontidão vs risco de lesão",
        )
        fig = apply_chart_style(fig, height=480)
        st.plotly_chart(fig, use_container_width=True)

    cols = [c for c in ["rank", "full_name", "status", "readiness_score", "injury_risk", "recovery_score", "cooper_m", "fatigue_score", "sleep_hours"] if c in view.columns]
    if cols:
        sort_cols = [c for c in ["status", "readiness_score"] if c in view.columns]
        display_df = view[cols].copy()
        if sort_cols:
            display_df = display_df.sort_values(sort_cols, ascending=[True, False][:len(sort_cols)])
        render_pretty_table(
            display_df,
            columns={
                "rank": "Posto",
                "full_name": "Militar",
                "status": "Estado",
                "readiness_score": "Prontidão",
                "injury_risk": "Risco",
                "recovery_score": "Recuperação",
                "cooper_m": "Cooper",
                "fatigue_score": "Fadiga",
                "sleep_hours": "Sono",
            },
            title="Tabela operacional",
            subtitle="",
            bar_columns={
                "readiness_score": "good",
                "injury_risk": "risk",
                "recovery_score": "good",
                "fatigue_score": "risk",
            },
        )



def _risk_band(value: Any) -> str:
    try:
        val = float(value)
    except Exception:
        return "Sem dados"
    if val >= 70:
        return "Elevado"
    if val >= 45:
        return "Moderado"
    return "Baixo"


def _availability_text(status: str, risk: Any, readiness: Any) -> str:
    try:
        r = float(risk)
        p = float(readiness)
    except Exception:
        return "Avaliação pendente"
    if status == "Risco" or r >= 70 or p < 55:
        return "Não recomendado para esforço intenso"
    if status == "Atenção" or r >= 45 or p < 75:
        return "Apto com controlo de carga"
    return "Apto para treino normal"


def _commander_action(status: str, risk: Any, readiness: Any, recovery: Any) -> str:
    try:
        r = float(risk)
        p = float(readiness)
        rec = float(recovery)
    except Exception:
        return "Completar avaliação antes de planear carga intensa."
    if status == "Risco" or r >= 70:
        return "Reduzir impacto, evitar treino intenso e monitorizar nas próximas 24–48h."
    if p < 65 or rec < 60:
        return "Manter treino, mas com variante adaptada e controlo pós-sessão."
    return "Pode integrar treino planeado; manter recolha de feedback pós-treino."


def _bar_html(label: str, value: Any, polarity: str = "good") -> str:
    try:
        v = max(0, min(100, float(value)))
        n = f"{int(round(v))}%"
    except Exception:
        v = 0
        n = "—"
    if polarity == "risk":
        cls = "fill-risk" if v >= 65 else "fill-warn" if v >= 40 else "fill-good"
    else:
        cls = "fill-good" if v >= 75 else "fill-warn" if v >= 55 else "fill-risk"
    return (
        '<div class="band-row">'
        f'<div>{html.escape(label)}</div>'
        f'<div class="band-track"><div class="band-fill {cls}" style="width:{v:.0f}%"></div></div>'
        f'<strong>{n}</strong>'
        '</div>'
    )


def render_commander_soldier_summary(soldier: Dict[str, Any], latest: Dict[str, Any], dlatest: Dict[str, Any], tlatest: Dict[str, Any], recs: pd.DataFrame) -> None:
    status = str(latest.get("status", "Atenção"))
    readiness = latest.get("readiness_score", "—")
    risk = latest.get("injury_risk", "—")
    recovery = latest.get("recovery_score", "—")
    fatigue = dlatest.get("fatigue_score", "—")
    sleep = dlatest.get("sleep_hours", "—")
    cooper = tlatest.get("cooper_m", "—")

    availability = _availability_text(status, risk, readiness)
    risk_band = _risk_band(risk)
    action = _commander_action(status, risk, readiness, recovery)

    try:
        fatigue_text = f"{int(round(float(fatigue)))}/10"
    except Exception:
        fatigue_text = "—"
    try:
        sleep_text = f"{float(sleep):.1f} h"
    except Exception:
        sleep_text = "—"

    last_rec = "Sem recomendações críticas."
    if not recs.empty:
        r = recs.iloc[0]
        last_rec = f"{r.get('priority','')} · {r.get('title','')} — {r.get('message','')}"

    left, right = st.columns([1.05, 1])
    with left:
        bands_html = _bar_html('Prontidão', readiness, 'good') + _bar_html('Risco', risk, 'risk') + _bar_html('Recuperação', recovery, 'good')
        summary_html = (
            '<div class="info-card">'
            '<h3>Resumo operacional autorizado</h3>'
            '<div class="band-list">' + bands_html + '</div>'
            '<div class="action-box" style="margin-top:14px;">'
            f'<b>Estado atual:</b> <span>{html.escape(status)}</span><br>'
            f'<b>Disponibilidade:</b> <span>{html.escape(availability)}</span><br>'
            f'<b>Risco operacional:</b> <span>{html.escape(risk_band)}</span><br>'
            f'<b>Último Cooper:</b> <span>{html.escape(str(cooper))} m</span><br>'
            f'<b>Fadiga reportada:</b> <span>{html.escape(fatigue_text)}</span> · '
            f'<b>Sono:</b> <span>{html.escape(sleep_text)}</span>'
            '</div>'
            '</div>'
        )
        st.markdown(summary_html, unsafe_allow_html=True)
    with right:
        decision_html = (
            '<div class="info-card">'
            '<h3>Decisão para planeamento</h3>'
            f'<div class="action-box"><b>Ação recomendada:</b><br><span>{html.escape(action)}</span></div>'
            f'<div class="action-box"><b>Recomendação mais recente:</b><br><span>{html.escape(last_rec)}</span></div>'
            '<div class="action-box"><b>Regra de utilização:</b><br><span>Esta vista apoia decisão de treino e não substitui avaliação médica/profissional.</span></div>'
            '</div>'
        )
        st.markdown(decision_html, unsafe_allow_html=True)


def enrich_soldier_filters(soldiers: pd.DataFrame) -> pd.DataFrame:
    """Adds platoon name and a prototype section label for command filtering."""
    df = soldiers.copy()
    platoons = df_from("platoons", order="name")
    platoon_map = {}
    if not platoons.empty and "id" in platoons.columns:
        platoon_map = {row["id"]: row["name"] for _, row in platoons.iterrows()}
    df["platoon_name"] = df.get("platoon_id", pd.Series(index=df.index, dtype=object)).map(platoon_map).fillna("Sem pelotão")
    df["section_label"] = "Sem secção"
    for _, idxs in df.sort_values(["platoon_name", "rank", "full_name"]).groupby("platoon_name", dropna=False).groups.items():
        ordered = list(idxs)
        midpoint = max(1, math.ceil(len(ordered) / 2))
        df.loc[ordered[:midpoint], "section_label"] = "1.ª Secção"
        df.loc[ordered[midpoint:], "section_label"] = "2.ª Secção"
    return df

def soldier_page(profile: Dict[str, Any], forced_soldier_id: Optional[str] = None) -> Optional[str]:
    all_soldiers = get_soldiers()
    if all_soldiers.empty:
        st.warning("Não há militares acessíveis.")
        return None

    role = profile.get("role")
    if role == "militar":
        own = get_soldier_for_profile(profile["id"])
        if not own:
            st.error("Este utilizador ainda não tem militar associado na tabela soldiers.")
            return None
        soldier_id = own["id"]
    else:
        all_soldiers = enrich_soldier_filters(all_soldiers)
        f1, f2, f3 = st.columns([1, 1, 2])
        with f1:
            platoon_options = ["Todos"] + sorted([p for p in all_soldiers["platoon_name"].dropna().unique().tolist() if p != "Sem pelotão"])
            platoon_filter = st.selectbox("Pelotão", platoon_options)
        filtered_soldiers = all_soldiers.copy()
        if platoon_filter != "Todos":
            filtered_soldiers = filtered_soldiers[filtered_soldiers["platoon_name"] == platoon_filter].copy()
        with f2:
            section_options = ["Todas"] + sorted(filtered_soldiers["section_label"].dropna().unique().tolist())
            section_filter = st.selectbox("Secção", section_options)
        if section_filter != "Todas":
            filtered_soldiers = filtered_soldiers[filtered_soldiers["section_label"] == section_filter].copy()
        if filtered_soldiers.empty:
            st.warning("Não há militares para os filtros selecionados.")
            return None
        name_map = {f"{row.get('rank','')} {row['full_name']}": row["id"] for _, row in filtered_soldiers.sort_values(["rank", "full_name"]).iterrows()}
        default_index = 0
        if forced_soldier_id and forced_soldier_id in name_map.values():
            default_index = list(name_map.values()).index(forced_soldier_id)
        with f3:
            chosen = st.selectbox("Selecionar militar", list(name_map.keys()), index=default_index)
        soldier_id = name_map[chosen]

    soldier = all_soldiers[all_soldiers["id"] == soldier_id].iloc[0].to_dict()
    st.markdown(f'<div class="section-title">{soldier.get("rank", "")} {soldier.get("full_name")}</div>', unsafe_allow_html=True)

    readiness = df_from("readiness_scores", order="score_date", desc=True, filters=[("soldier_id", "eq", soldier_id)])
    tests = df_from("physical_tests", order="test_date", desc=True, filters=[("soldier_id", "eq", soldier_id)])
    daily = df_from("daily_records", order="record_date", desc=True, filters=[("soldier_id", "eq", soldier_id)])
    recs = df_from("recommendations", order="rec_date", desc=True, filters=[("soldier_id", "eq", soldier_id)])

    latest = readiness.iloc[0].to_dict() if not readiness.empty else {}
    dlatest = daily.iloc[0].to_dict() if not daily.empty else {}
    tlatest = tests.iloc[0].to_dict() if not tests.empty else {}

    if role != "militar":
        c1, c2, c3, c4 = st.columns(4)
        with c1: metric_card("Prontidão", f"{latest.get('readiness_score', '—')}%", latest.get("status", "sem estado"))
        with c2: metric_card("Risco operacional", _risk_band(latest.get('injury_risk')), "sem detalhes clínicos")
        with c3: metric_card("Disponibilidade", _availability_text(str(latest.get('status', 'Atenção')), latest.get('injury_risk'), latest.get('readiness_score')), "para planeamento")
        with c4: metric_card("Cooper", f"{tlatest.get('cooper_m', '—')} m", "último teste")
        st.divider()
        render_commander_soldier_summary(soldier, latest, dlatest, tlatest, recs)
        return soldier_id

    # Individual landing page: simple, useful first view for the soldier.
    status = str(latest.get("status", "Atenção"))
    readiness_score = latest.get("readiness_score", "—")
    injury_risk = latest.get("injury_risk", "—")
    recovery_score = latest.get("recovery_score", "—")
    availability = _availability_text(status, injury_risk, readiness_score)

    try:
        risk_text = _risk_band(injury_risk)
    except Exception:
        risk_text = "Sem dados"

    try:
        fatigue_text = f"{int(round(float(dlatest.get('fatigue_score'))))}/10"
    except Exception:
        fatigue_text = "—"

    try:
        sleep_text = f"{float(dlatest.get('sleep_hours')):.1f} h"
    except Exception:
        sleep_text = "—"

    cooper_text = f"{tlatest.get('cooper_m', '—')} m" if tlatest else "—"

    if not recs.empty:
        r = recs.iloc[0]
        rec_title = f"{r.get('priority', '')} · {r.get('title', '')}".strip(" ·")
        rec_message = str(r.get("message", ""))
        rec_date = str(r.get("rec_date", ""))
    else:
        rec_title = "Sem recomendações críticas"
        rec_message = "Mantém o plano normal e regista o feedback após o treino."
        rec_date = ""

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        metric_card("Prontidão", f"{readiness_score}%", status)
    with c2:
        metric_card("Treino de hoje", availability, "decisão rápida")
    with c3:
        metric_card("Recuperação", f"{recovery_score}%", "sono/fadiga/carga")
    with c4:
        metric_card("Cooper", cooper_text, "último teste")

    st.divider()

    left, right = st.columns([1.05, 1])
    with left:
        bands_html = (
            _bar_html("Prontidão", readiness_score, "good")
            + _bar_html("Risco", injury_risk, "risk")
            + _bar_html("Recuperação", recovery_score, "good")
        )
        quick_html = (
            '<div class="info-card">'
            '<h3>Resumo rápido</h3>'
            '<div class="band-list">' + bands_html + '</div>'
            '<div class="action-box" style="margin-top:14px;">'
            f'<b>Risco atual:</b> <span>{html.escape(risk_text)}</span><br>'
            f'<b>Fadiga reportada:</b> <span>{html.escape(fatigue_text)}</span><br>'
            f'<b>Sono:</b> <span>{html.escape(sleep_text)}</span>'
            '</div>'
            '</div>'
        )
        st.markdown(quick_html, unsafe_allow_html=True)

    with right:
        today_html = (
            '<div class="info-card">'
            '<h3>O que fazer agora</h3>'
            f'<div class="action-box"><b>{html.escape(rec_title)}</b><br><span>{html.escape(rec_message)}</span></div>'
            '<div class="action-box">'
            f'<b>Estado para planeamento:</b><br><span>{html.escape(availability)}</span>'
            '</div>'
            '<div class="action-box">'
            '<b>Próximo passo:</b><br><span>Usa as abas Digital Twin e Simular treino apenas se quiseres ver detalhe ou testar uma sessão.</span>'
            '</div>'
            '</div>'
        )
        st.markdown(today_html, unsafe_allow_html=True)
        if rec_date:
            st.caption(f"Última atualização: {rec_date}")

    return soldier_id


def select_soldier_for_twin(profile: Dict[str, Any]) -> Tuple[Optional[str], Optional[Dict[str, Any]]]:
    all_soldiers = get_soldiers()
    if all_soldiers.empty:
        st.warning("Não há militares acessíveis.")
        return None, None

    role = profile.get("role")
    if role == "militar":
        own = get_soldier_for_profile(profile["id"])
        if not own:
            st.error("Este utilizador ainda não tem militar associado na tabela soldiers.")
            return None, None
        return own["id"], own

    all_soldiers = enrich_soldier_filters(all_soldiers)
    f1, f2, f3 = st.columns([1, 1, 2])
    with f1:
        platoon_options = ["Todos"] + sorted([p for p in all_soldiers["platoon_name"].dropna().unique().tolist() if p != "Sem pelotão"])
        platoon_filter = st.selectbox("Pelotão", platoon_options, key="twin_platoon_filter")
    filtered = all_soldiers.copy()
    if platoon_filter != "Todos":
        filtered = filtered[filtered["platoon_name"] == platoon_filter].copy()
    with f2:
        section_options = ["Todas"] + sorted(filtered["section_label"].dropna().unique().tolist())
        section_filter = st.selectbox("Secção", section_options, key="twin_section_filter")
    if section_filter != "Todas":
        filtered = filtered[filtered["section_label"] == section_filter].copy()
    if filtered.empty:
        st.warning("Não há militares para os filtros selecionados.")
        return None, None
    name_map = {f"{row.get('rank','')} {row['full_name']}": row["id"] for _, row in filtered.sort_values(["rank", "full_name"]).iterrows()}
    with f3:
        chosen = st.selectbox("Selecionar militar", list(name_map.keys()), key="twin_soldier_select")
    soldier_id = name_map[chosen]
    soldier = all_soldiers[all_soldiers["id"] == soldier_id].iloc[0].to_dict()
    return soldier_id, soldier


def twin_page(profile: Dict[str, Any]) -> None:
    st.markdown('<div class="section-title">Digital Twin individual</div>', unsafe_allow_html=True)
    soldier_id, soldier = select_soldier_for_twin(profile)
    if not soldier_id or not soldier:
        return

    readiness = df_from("readiness_scores", order="score_date", desc=True, filters=[("soldier_id", "eq", soldier_id)])
    tests = df_from("physical_tests", order="test_date", desc=True, filters=[("soldier_id", "eq", soldier_id)])
    daily = df_from("daily_records", order="record_date", desc=True, filters=[("soldier_id", "eq", soldier_id)])
    sessions = df_from("training_sessions", order="session_date", desc=True, filters=[("soldier_id", "eq", soldier_id)])
    injuries = df_from("injury_reports", order="report_date", desc=True, filters=[("soldier_id", "eq", soldier_id)])
    recs = df_from("recommendations", order="rec_date", desc=True, filters=[("soldier_id", "eq", soldier_id)])
    muscle_df = df_from("muscle_loads", order="load_date", desc=True, filters=[("soldier_id", "eq", soldier_id)])

    latest = readiness.iloc[0].to_dict() if not readiness.empty else {}
    dlatest = daily.iloc[0].to_dict() if not daily.empty else {}
    tlatest = tests.iloc[0].to_dict() if not tests.empty else {}
    muscle = muscle_df.iloc[0].to_dict() if not muscle_df.empty else {}

    status = str(latest.get("status", "Atenção"))
    readiness_score = latest.get("readiness_score", "—")
    risk = latest.get("injury_risk", "—")
    recovery = latest.get("recovery_score", "—")
    availability = _availability_text(status, risk, readiness_score)

    if muscle:
        muscle_chart, info = muscle_summary(muscle)
    else:
        muscle_chart = pd.DataFrame()
        info = {"global_load": 0, "top": {"Grupo muscular": "—", "Carga": 0}, "low": {"Grupo muscular": "—", "Carga": 0}, "upper": 0, "lower": 0, "push": 0, "pull": 0, "critical": [], "attention": []}
    rec_title, rec_message, rec_status = twin_recommendation(info, latest)

    load_date = str(muscle.get("load_date", "sem data")) if muscle else "sem dados musculares"
    status_badge_class = "good" if status == "Pronto" else "warn" if status == "Atenção" else "risk"
    st.markdown(
        f"""
        <div class="twin-hero">
            <h2>{html.escape(str(soldier.get('rank','')))} {html.escape(str(soldier.get('full_name','')))}</h2>
            <p>Modelo individual com prontidão, recuperação, carga muscular e recomendações. Última leitura muscular: {html.escape(load_date)}.</p>
            <div class="twin-badge-row">
                <span class="twin-badge {status_badge_class}">Estado: {html.escape(status)}</span>
                <span class="twin-badge {'good' if rec_status == 'good' else 'warn' if rec_status == 'warn' else 'risk'}">{html.escape(rec_title)}</span>
                <span class="twin-badge">Disponibilidade: {html.escape(availability)}</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        metric_card("Prontidão", _fmt_pct(readiness_score), status)
    with c2:
        metric_card("Carga muscular", _fmt_pct(info.get("global_load")), f"maior: {info['top'].get('Grupo muscular', '—')}")
    with c3:
        metric_card("Risco", _risk_band(risk), _fmt_pct(risk))
    with c4:
        metric_card("Recuperação", _fmt_pct(recovery), "sono/fadiga/carga")

    left, right = st.columns([1.12, 1.0])
    with left:
        if muscle:
            rendered_asset = render_twin_silhouette_asset(muscle, sex=str(soldier.get("sex", "M")), info=info)
            if not rendered_asset:
                st.markdown('<div class="twin-panel"><h3>Silhueta de carga muscular</h3>', unsafe_allow_html=True)
                st.plotly_chart(digital_twin_figure(muscle, sex=str(soldier.get("sex", "M")), title="Mapa corporal de carga"), use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("Sem dados de carga muscular para este militar.")

    with right:
        if not muscle_chart.empty:
            chart = muscle_chart.sort_values("Carga", ascending=True)
            fig = go.Figure()
            fig.add_trace(go.Bar(
                y=chart["Grupo muscular"],
                x=chart["Carga"],
                orientation="h",
                marker=dict(color=chart["Cor"], line=dict(color="rgba(20,83,45,.18)", width=1)),
                text=[f"{v}% · {lvl}" for v, lvl in zip(chart["Carga"], chart["Nível"])],
                textposition="outside",
                hovertemplate="%{y}: %{x}%<extra></extra>",
            ))
            fig.update_xaxes(range=[0, 105], title="Carga (%)")
            fig.update_yaxes(title="")
            fig.update_layout(showlegend=False)
            st.plotly_chart(apply_chart_style(fig, height=430), use_container_width=True)

        upper_lower = abs(float(info.get("upper", 0)) - float(info.get("lower", 0)))
        push_pull = abs(float(info.get("push", 0)) - float(info.get("pull", 0)))
        tags = []
        if info.get("critical"):
            tags += [f'<span class="twin-badge risk">Crítico: {html.escape(g)}</span>' for g in info["critical"]]
        if info.get("attention"):
            tags += [f'<span class="twin-badge warn">Atenção: {html.escape(g)}</span>' for g in info["attention"]]
        if not tags:
            tags.append('<span class="twin-badge good">Sem zonas críticas</span>')
        st.markdown(
            '<div class="twin-panel">'
            '<h3>Leitura muscular automática</h3>'
            f'<div class="twin-rec"><b>{html.escape(rec_title)}</b><br>{html.escape(rec_message)}</div>'
            '<div class="twin-badge-row">' + ''.join(tags) + '</div>'
            f'<div class="action-box"><b>Equilíbrio superior/inferior:</b> <span>diferença de {upper_lower:.0f} p.p.</span><br>'
            f'<b>Equilíbrio empurrar/puxar:</b> <span>diferença de {push_pull:.0f} p.p.</span><br>'
            f'<b>Zona menos carregada:</b> <span>{html.escape(str(info["low"].get("Grupo muscular", "—")))} ({int(info["low"].get("Carga", 0))}%)</span></div>'
            '</div>',
            unsafe_allow_html=True,
        )

    try:
        bmi = (_to_float(soldier.get("weight_kg"), 0) or 0) / (((_to_float(soldier.get("height_cm"), 0) or 0) / 100) ** 2)
        bmi_text = f"{bmi:.1f}" if bmi > 0 else "—"
    except Exception:
        bmi_text = "—"

    last_session = sessions.iloc[0].to_dict() if not sessions.empty else {}
    open_injuries = injuries[injuries.get("status", pd.Series(dtype=str)).astype(str).isin(["open", "monitoring"])] if not injuries.empty and "status" in injuries.columns else pd.DataFrame()
    latest_rec = recs.iloc[0].to_dict() if not recs.empty else {}

    render_twin_grid("Dados físicos e biométricos", [
        ("Idade", _fmt_num(soldier.get("age"), " anos"), str(soldier.get("specialty", "especialidade"))),
        ("Altura", _fmt_num(soldier.get("height_cm"), " cm", 1), "registo base"),
        ("Peso", _fmt_num(soldier.get("weight_kg"), " kg", 1), f"IMC {bmi_text}"),
        ("FC repouso", _fmt_num(dlatest.get("resting_hr"), " bpm"), "último registo"),
    ])

    render_twin_grid("Recuperação e carga interna", [
        ("Sono", _fmt_num(dlatest.get("sleep_hours"), " h", 1), "última noite"),
        ("Fadiga", _fmt_num(dlatest.get("fatigue_score"), "/10"), "auto-reportada"),
        ("Dor muscular", _fmt_num(dlatest.get("soreness_score"), "/10"), "auto-reportada"),
        ("Stress", _fmt_num(dlatest.get("stress_score"), "/10"), "auto-reportado"),
    ])

    render_twin_grid("Últimos testes físicos", [
        ("Cooper", _fmt_num(tlatest.get("cooper_m"), " m"), str(tlatest.get("test_date", "último teste"))),
        ("Flexões", _fmt_num(tlatest.get("pushups")), "repetições"),
        ("Abdominais", _fmt_num(tlatest.get("situps")), "repetições"),
        ("Barras", _fmt_num(tlatest.get("pullups")), f"VO₂ est. {_fmt_num(tlatest.get('vo2_est'), '', 1)}"),
    ])

    render_twin_grid("Histórico recente", [
        ("Último treino", str(last_session.get("session_type", "—")), f"{_fmt_num(last_session.get('duration_min'), ' min')} · intensidade {_fmt_num(last_session.get('intensity'))}"),
        ("Carga UA", _fmt_num(last_session.get("load_ua"), " UA", 0), str(last_session.get("session_date", "sem treino"))),
        ("Lesões abertas", str(len(open_injuries)), "open/monitoring"),
        ("Recomendação", str(latest_rec.get("priority", "—")), str(latest_rec.get("title", "sem recomendação"))),
    ])

    if not sessions.empty:
        recent = sessions.head(5).copy()
        render_pretty_table(
            recent,
            columns={
                "session_date": "Data",
                "session_type": "Tipo",
                "duration_min": "Duração",
                "intensity": "Intensidade",
                "load_ua": "Carga UA",
                "focus_area": "Foco",
            },
            title="Últimos treinos registados",
            subtitle="histórico recente do militar",
            bar_columns={"intensity": "risk"},
        )


def build_group_selection(snapshot: pd.DataFrame) -> Tuple[str, pd.DataFrame]:
    """Selects an operational group for command-level simulation."""
    c1, c2, c3 = st.columns(3)
    with c1:
        echelon = st.selectbox("Escalão", ["Companhia", "Pelotão", "Secção"])

    group_label = "Companhia"
    target = snapshot.copy()

    platoons = df_from("platoons", order="name")
    platoon_map = {}
    if not platoons.empty:
        platoon_map = {row["name"]: row["id"] for _, row in platoons.iterrows()}

    if echelon in ["Pelotão", "Secção"]:
        with c2:
            if platoon_map:
                platoon_name = st.selectbox("Pelotão", list(platoon_map.keys()))
                platoon_id = platoon_map[platoon_name]
                target = target[target["platoon_id"] == platoon_id].copy()
                group_label = platoon_name
            else:
                st.warning("Sem pelotões disponíveis na base de dados.")

    if echelon == "Secção":
        target = target.sort_values(["rank", "full_name"]).reset_index(drop=True)
        midpoint = max(1, math.ceil(len(target) / 2))
        section_options = ["1.ª Secção", "2.ª Secção"]
        with c3:
            section = st.selectbox("Secção", section_options)
        if section == "1.ª Secção":
            target = target.iloc[:midpoint].copy()
        else:
            target = target.iloc[midpoint:].copy()
        group_label = f"{group_label} · {section}"
    elif echelon == "Companhia":
        with c2:
            st.info("Toda a companhia selecionada")
        group_label = "Companhia de Reconhecimento"

    return group_label, target


def group_training_inputs() -> Dict[str, Any]:
    training_type = st.selectbox(
        "Tipo de treino",
        [
            "Corrida contínua",
            "Corrida intervalada",
            "Marcha com carga",
            "Circuito de força",
            "Treino técnico-tático",
            "Recuperação ativa",
        ],
    )

    params: Dict[str, Any] = {"training_type": training_type}

    if training_type == "Corrida contínua":
        c1, c2, c3 = st.columns(3)
        with c1: params["duration"] = st.slider("Duração", 20, 90, 45, step=5)
        with c2: params["intensity"] = st.slider("Intensidade", 1, 10, 6)
        with c3: params["pace_zone"] = st.selectbox("Zona de ritmo", ["Leve", "Moderado", "Forte"])
        params["focus"] = "Pernas"
        params["load_factor"] = params["duration"] * params["intensity"] / 10
        params["risk_factor"] = 0.75 if params["pace_zone"] == "Leve" else 0.95 if params["pace_zone"] == "Moderado" else 1.15

    elif training_type == "Corrida intervalada":
        c1, c2, c3, c4 = st.columns(4)
        with c1: params["repetitions"] = st.slider("Repetições", 4, 12, 8)
        with c2: params["distance_m"] = st.selectbox("Distância por repetição", [200, 400, 800, 1000], index=1)
        with c3: params["rest_s"] = st.slider("Recuperação", 30, 180, 90, step=15)
        with c4: params["intensity"] = st.slider("Intensidade", 1, 10, 8)
        params["duration"] = int(params["repetitions"] * (params["distance_m"] / 1000) * 4.2 + params["repetitions"] * params["rest_s"] / 60)
        params["focus"] = "Pernas"
        params["load_factor"] = params["repetitions"] * (params["distance_m"] / 100) * params["intensity"] / 8
        params["risk_factor"] = 1.35

    elif training_type == "Marcha com carga":
        c1, c2, c3, c4 = st.columns(4)
        with c1: params["duration"] = st.slider("Duração", 45, 180, 90, step=15)
        with c2: params["load_kg"] = st.slider("Carga externa", 5, 35, 20, step=5)
        with c3: params["terrain"] = st.selectbox("Terreno", ["Plano", "Misto", "Montanhoso"])
        with c4: params["intensity"] = st.slider("Intensidade", 1, 10, 7)
        terrain_mult = {"Plano": 0.9, "Misto": 1.1, "Montanhoso": 1.35}[params["terrain"]]
        params["focus"] = "Pernas/Core"
        params["load_factor"] = (params["duration"] * params["intensity"] / 12 + params["load_kg"] * 1.15) * terrain_mult
        params["risk_factor"] = 1.25

    elif training_type == "Circuito de força":
        c1, c2, c3, c4 = st.columns(4)
        with c1: params["rounds"] = st.slider("Rondas", 2, 8, 4)
        with c2: params["exercises"] = st.slider("Exercícios", 4, 12, 8)
        with c3: params["intensity"] = st.slider("Intensidade", 1, 10, 7)
        with c4: params["focus"] = st.selectbox("Foco", ["Full-body", "Superior", "Inferior", "Core"])
        params["duration"] = int(params["rounds"] * params["exercises"] * 1.8)
        params["load_factor"] = params["rounds"] * params["exercises"] * params["intensity"] * 0.65
        params["risk_factor"] = 1.05 if params["focus"] in ["Full-body", "Inferior"] else 0.85

    elif training_type == "Treino técnico-tático":
        c1, c2, c3, c4 = st.columns(4)
        with c1: params["duration"] = st.slider("Duração", 30, 180, 75, step=15)
        with c2: params["scenario"] = st.selectbox("Cenário", ["Técnica leve", "Patrulha", "Combate urbano", "Progressão em terreno"])
        with c3: params["equipment"] = st.slider("Carga/equipamento", 0, 30, 12, step=3)
        with c4: params["intensity"] = st.slider("Intensidade", 1, 10, 6)
        scenario_mult = {"Técnica leve": 0.75, "Patrulha": 1.0, "Combate urbano": 1.25, "Progressão em terreno": 1.15}[params["scenario"]]
        params["focus"] = "Full-body"
        params["load_factor"] = (params["duration"] * params["intensity"] / 13 + params["equipment"] * 0.8) * scenario_mult
        params["risk_factor"] = 1.0 * scenario_mult

    else:  # Recuperação ativa
        c1, c2, c3 = st.columns(3)
        with c1: params["duration"] = st.slider("Duração", 15, 60, 30, step=5)
        with c2: params["modality"] = st.selectbox("Modalidade", ["Mobilidade", "Bicicleta leve", "Corrida muito leve", "Alongamentos"])
        with c3: params["intensity"] = st.slider("Intensidade", 1, 5, 2)
        params["focus"] = "Recuperação"
        params["load_factor"] = params["duration"] * params["intensity"] / 20
        params["risk_factor"] = 0.25
        params["recovery_bonus"] = 9

    params.setdefault("recovery_bonus", 0)
    return params


def simulate_group_training(profile: Dict[str, Any]) -> None:
    st.markdown('<div class="section-title">Simulador de treino coletivo</div>', unsafe_allow_html=True)
    snapshot = assemble_snapshot()
    if snapshot.empty:
        st.warning("Não há militares acessíveis para simular.")
        return

    group_label, target = build_group_selection(snapshot)
    if target.empty:
        st.warning("O grupo selecionado não tem militares disponíveis.")
        return

    st.markdown(f"**Grupo selecionado:** {group_label} · **{len(target)} militares**")
    params = group_training_inputs()

    load_factor = float(params.get("load_factor", 0))
    risk_factor = float(params.get("risk_factor", 1.0))
    recovery_bonus = float(params.get("recovery_bonus", 0))

    sim = target.copy()
    for col in ["readiness_score", "injury_risk", "recovery_score"]:
        sim[col] = pd.to_numeric(sim[col], errors="coerce").fillna(50)

    vulnerability = 1 + (sim["injury_risk"] / 140) + ((65 - sim["recovery_score"]).clip(lower=0) / 100)
    sim["Prontidão atual"] = sim["readiness_score"].round(0).astype(int)
    sim["Risco atual"] = sim["injury_risk"].round(0).astype(int)
    sim["Prontidão prevista"] = np.clip(sim["readiness_score"] - load_factor * 0.45 * vulnerability + recovery_bonus, 0, 100).round(0).astype(int)
    sim["Risco previsto"] = np.clip(sim["injury_risk"] + load_factor * 0.40 * risk_factor * vulnerability - recovery_bonus * 0.5, 0, 100).round(0).astype(int)
    sim["Impacto"] = sim["Prontidão prevista"] - sim["Prontidão atual"]
    sim["Decisão"] = np.where(sim["Risco previsto"] >= 75, "Retirar/Adaptar", np.where(sim["Prontidão prevista"] < 55, "Monitorizar", "Executa"))

    avg_now = int(round(sim["Prontidão atual"].mean()))
    avg_after = int(round(sim["Prontidão prevista"].mean()))
    risk_count = int((sim["Risco previsto"] >= 75).sum())
    adapt_count = int((sim["Decisão"] != "Executa").sum())

    c1, c2, c3, c4 = st.columns(4)
    with c1: metric_card("Prontidão média atual", f"{avg_now}%", group_label)
    with c2: metric_card("Prontidão média prevista", f"{avg_after}%", "após treino")
    with c3: metric_card("Militares a adaptar", adapt_count, "monitorizar ou retirar")
    with c4: metric_card("Risco elevado previsto", risk_count, "risco ≥ 75")

    if risk_count > 0:
        st.error(f"Ajustar plano: {risk_count} militar(es) ficariam em risco elevado. Reduzir intensidade/carga ou criar variante adaptada.")
    elif avg_after < 60:
        st.warning("Treino possível, mas agressivo para o estado atual do grupo. Recomenda-se reduzir volume ou intensidade.")
    else:
        st.success("Treino compatível com o estado atual do grupo. Manter monitorização pós-sessão.")

    v1, v2 = st.columns([1.15, 1])
    with v1:
        plot_df = sim.sort_values("Prontidão prevista", ascending=True)
        fig = px.bar(
            plot_df,
            x="Prontidão prevista",
            y="full_name",
            color="Decisão",
            color_discrete_map={"Executa": "#22c55e", "Monitorizar": "#f59e0b", "Retirar/Adaptar": "#ef4444"},
            labels={"full_name": "Militar", "Prontidão prevista": "Prontidão prevista"},
            title="Impacto previsto por militar",
        )
        fig.update_layout(legend_title_text="Decisão")
        fig = apply_chart_style(fig, height=430)
        st.plotly_chart(fig, use_container_width=True)
    with v2:
        fig = px.scatter(
            sim,
            x="Prontidão prevista",
            y="Risco previsto",
            color="Decisão",
            size="recovery_score",
            hover_name="full_name",
            color_discrete_map={"Executa": "#22c55e", "Monitorizar": "#f59e0b", "Retirar/Adaptar": "#ef4444"},
            title="Risco previsto vs prontidão prevista",
        )
        fig = apply_chart_style(fig, height=430)
        st.plotly_chart(fig, use_container_width=True)

    table_cols = ["rank", "full_name", "status", "Prontidão atual", "Prontidão prevista", "Risco atual", "Risco previsto", "Impacto", "Decisão"]
    sim_table = sim[table_cols].sort_values(["Decisão", "Prontidão prevista"]).copy()
    render_pretty_table(
        sim_table,
        columns={
            "rank": "Posto",
            "full_name": "Militar",
            "status": "Estado atual",
            "Prontidão atual": "Prontidão atual",
            "Prontidão prevista": "Prontidão prevista",
            "Risco atual": "Risco atual",
            "Risco previsto": "Risco previsto",
            "Impacto": "Impacto",
            "Decisão": "Decisão",
        },
        title="Resultado operacional da simulação",
        subtitle=f"{params['training_type']} · {group_label} · {len(sim_table)} militar(es)",
        bar_columns={
            "Prontidão atual": "good",
            "Prontidão prevista": "good",
            "Risco atual": "risk",
            "Risco previsto": "risk",
        },
        delta_columns=["Impacto"],
    )

    if st.button("Guardar simulação coletiva", use_container_width=True):
        try:
            payloads = []
            for _, row in sim.iterrows():
                payloads.append({
                    "soldier_id": row["soldier_id"],
                    "created_by": profile["id"],
                    "training_type": f"{params['training_type']} · {group_label}",
                    "duration_min": int(params.get("duration", 45)),
                    "intensity": int(params.get("intensity", 6)),
                    "focus_area": str(params.get("focus", "Grupo")),
                    "predicted_readiness": int(row["Prontidão prevista"]),
                    "predicted_injury_risk": int(row["Risco previsto"]),
                    "recommendation": str(row["Decisão"]),
                })
            sb_insert_many("training_simulations", payloads)
            st.success("Simulação coletiva guardada com sucesso.")
        except Exception as exc:
            st.error("Não foi possível guardar a simulação coletiva.")
            st.caption(str(exc))


def simulate_individual_training(profile: Dict[str, Any]) -> None:
    st.markdown('<div class="section-title">Simulador de treino individual</div>', unsafe_allow_html=True)
    all_soldiers = get_soldiers()
    if all_soldiers.empty:
        st.warning("Não há militares acessíveis.")
        return

    own = get_soldier_for_profile(profile["id"])
    if not own:
        st.error("Este utilizador ainda não tem militar associado.")
        return
    soldier_id = own["id"]
    soldier_name = f"{own.get('rank','')} {own['full_name']}"
    st.info(f"Simulação para: {soldier_name}")

    latest = df_from("readiness_scores", order="score_date", desc=True, filters=[("soldier_id", "eq", soldier_id)])
    if latest.empty:
        st.warning("Sem prontidão atual para simular.")
        return
    base = latest.iloc[0]

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        training_type = st.selectbox("Tipo de treino", ["Corrida contínua", "Corrida intervalada", "Força superior", "Força inferior", "Marcha com carga", "Recuperação ativa"])
    with c2:
        duration = st.slider("Duração", 15, 120, 45, step=5)
    with c3:
        intensity = st.slider("Intensidade", 1, 10, 6)
    with c4:
        focus = st.selectbox("Foco muscular", ["Pernas", "Core", "Braços", "Ombros", "Costas", "Peito", "Full-body"])

    load_factor = duration * intensity / 10
    fatigue_penalty = load_factor * (1.1 if training_type in ["Corrida intervalada", "Marcha com carga", "Força inferior"] else 0.75)
    recovery_bonus = 8 if training_type == "Recuperação ativa" else 0
    predicted_readiness = int(np.clip(base["readiness_score"] - fatigue_penalty + recovery_bonus, 0, 100))
    predicted_risk = int(np.clip(base["injury_risk"] + load_factor * (1.0 if focus in ["Pernas", "Full-body"] else 0.55) - recovery_bonus, 0, 100))

    if predicted_risk >= 70:
        rec = "Não recomendado: risco elevado. Reduzir intensidade/duração ou substituir por recuperação ativa."
        st.error(rec)
    elif predicted_readiness < 55:
        rec = "Atenção: treino possível, mas deve ser ajustado e monitorizado."
        st.warning(rec)
    else:
        rec = "Treino compatível com o estado atual. Monitorizar resposta pós-sessão."
        st.success(rec)

    b1, b2, b3 = st.columns(3)
    with b1: metric_card("Prontidão atual", f"{int(base['readiness_score'])}%", base.get("status", ""))
    with b2: metric_card("Prontidão prevista", f"{predicted_readiness}%", "após treino simulado")
    with b3: metric_card("Risco previsto", f"{predicted_risk}%", "após treino simulado")

    if st.button("Guardar simulação", use_container_width=True):
        try:
            sb_insert("training_simulations", {
                "soldier_id": soldier_id,
                "created_by": profile["id"],
                "training_type": training_type,
                "duration_min": duration,
                "intensity": intensity,
                "focus_area": focus,
                "predicted_readiness": predicted_readiness,
                "predicted_injury_risk": predicted_risk,
                "recommendation": rec,
            })
            st.success("Simulação guardada na base de dados.")
        except Exception as exc:
            st.error("Não foi possível guardar a simulação.")
            st.caption(str(exc))


def simulate_training(profile: Dict[str, Any]) -> None:
    if profile.get("role") == "militar":
        simulate_individual_training(profile)
    else:
        simulate_group_training(profile)

def admin_page(profile: Dict[str, Any]) -> None:
    if profile.get("role") != "admin":
        st.error("Acesso reservado a administrador.")
        return
    st.markdown('<div class="section-title">Administração da base de dados</div>', unsafe_allow_html=True)
    st.info("Nesta versão, a edição principal dos dados é feita no Supabase Dashboard. Esta página serve para consulta rápida.")
    for table in ["profiles", "soldiers", "readiness_scores", "recommendations", "training_simulations"]:
        with st.expander(table):
            st.dataframe(df_from(table, order="created_at", desc=True) if table not in ["profiles", "soldiers"] else df_from(table), use_container_width=True)


def main() -> None:
    try:
        if st.query_params.get("logout"):
            logout()
    except Exception:
        pass

    profile = require_login()
    page = top_bar(profile)

    if page == "Dashboard":
        commander_dashboard(profile)
    elif page == "Militar":
        soldier_page(profile)
    elif page == "Digital Twin":
        twin_page(profile)
    elif page == "Simular treino":
        simulate_training(profile)
    elif page == "Admin":
        admin_page(profile)



if __name__ == "__main__":
    main()

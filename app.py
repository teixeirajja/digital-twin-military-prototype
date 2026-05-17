from __future__ import annotations

import math
import html
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
# Styling
# -----------------------------
CSS = """
<style>
/* ------------------------------------------------------------------
   DARK MILITARY LOCAL-PROTOTYPE STYLE
   Keeps all Supabase data/logic unchanged; only changes presentation.
-------------------------------------------------------------------*/
:root {
    --bg0: #020603;
    --bg1: #06140a;
    --panel: #08190d;
    --panel2: #0c2111;
    --border: rgba(205, 197, 64, .42);
    --line: rgba(197, 188, 55, .25);
    --neon: #9fd134;
    --yellow: #d7c13a;
    --orange: #f59e0b;
    --red: #ef4444;
    --green: #22c55e;
    --text: #f5f7dd;
    --muted: #aeb989;
}

html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"] {
    background:
        radial-gradient(circle at 50% 0%, rgba(30, 84, 37, .30), transparent 36%),
        radial-gradient(circle at 92% 18%, rgba(157, 209, 52, .10), transparent 24%),
        linear-gradient(180deg, #000905 0%, #020a05 45%, #000703 100%) !important;
    color: var(--text) !important;
}
.block-container {
    padding-top: 2.0rem;
    padding-bottom: 2.2rem;
    max-width: 1120px;
}
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
[data-testid="stToolbar"] {visibility: hidden; height: 0%; position: fixed;}
[data-testid="stDecoration"] {display: none;}
[data-testid="stStatusWidget"] {visibility: hidden;}
[data-testid="stHeader"] {display: none;}

/* Core text */
h1, h2, h3, h4, h5, h6, p, label, span, div {font-family: "Inter", "Segoe UI", Arial, sans-serif;}
h1, h2, h3, h4 {color: var(--text) !important;}
[data-testid="stMarkdownContainer"] p {color: var(--muted);}
hr {border-color: var(--line) !important;}

/* Inputs - old local dark look */
.stTextInput input, .stPassword input, .stSelectbox [data-baseweb="select"], .stNumberInput input,
.stDateInput input, .stMultiSelect [data-baseweb="select"] {
    background: #1f2230 !important;
    color: #fffbe6 !important;
    border: 1px solid rgba(215,193,58,.32) !important;
    border-radius: 9px !important;
    min-height: 38px;
}
.stTextInput input::placeholder {color: rgba(245,247,221,.45) !important;}
[data-baseweb="popover"] {background:#0b170d !important; color:var(--text) !important;}
.stSelectbox label, .stSlider label, .stCheckbox label, .stRadio label, .stTextInput label {
    color: #ecf1c3 !important;
    font-weight: 800 !important;
    font-size: .80rem !important;
}
.stSlider [data-testid="stTickBar"] {background: rgba(215,193,58,.15) !important;}
.stCheckbox span {color: #ecf1c3 !important;}

/* Buttons */
.stButton > button, .stFormSubmitButton > button {
    border-radius: 8px !important;
    border: 1px solid rgba(215,193,58,.55) !important;
    background: #0c2111 !important;
    color: #f1df6a !important;
    font-weight: 900 !important;
    letter-spacing: .03em !important;
    box-shadow: 0 0 0 1px rgba(159,209,52,.10) inset !important;
}
.stButton > button:hover, .stFormSubmitButton > button:hover {
    background: #162d17 !important;
    color: #ffffff !important;
    border-color: rgba(159,209,52,.85) !important;
}

/* Login page - same spirit as local prototype */
.login-shell {
    max-width: 760px;
    margin: 7vh auto 0 auto;
}
.login-hero {
    padding: 20px 22px;
    border-radius: 16px;
    background: linear-gradient(135deg, rgba(6,20,10,.96), rgba(9,31,13,.92));
    border: 1px solid rgba(215,193,58,.42);
    box-shadow: 0 24px 60px rgba(0,0,0,.44), inset 0 0 28px rgba(46,125,50,.10);
}
.login-hero-top {display:flex; align-items:center; justify-content:space-between; gap:16px;}
.login-brand {display:flex; align-items:center; gap:14px;}
.login-logo {
    width:52px; height:52px; border-radius:12px;
    background:#0d2210; border:1px solid rgba(215,193,58,.45);
    display:flex; align-items:center; justify-content:center; font-size:1.45rem;
}
.login-title {
    margin:0; color:#fff7b5 !important; font-size:1.58rem; font-weight:950;
    letter-spacing:.18em; text-transform:uppercase;
}
.login-subtitle {margin:6px 0 0 0; color:#d0c264 !important; font-size:.78rem; font-weight:800;}
.login-badge {
    color:#dfff85; background:#071207; border:1px solid rgba(215,193,58,.40);
    border-radius:8px; padding:9px 13px; font-size:.72rem; font-weight:950; text-transform:uppercase;
}
.login-grid {
    margin-top:12px;
    border:1px solid rgba(215,193,58,.36);
    border-radius:16px;
    overflow:hidden;
    background:#06110a;
    box-shadow: 0 18px 50px rgba(0,0,0,.36);
}
.login-info {display:none;}
.login-form-panel {padding:22px 22px 16px 22px; background: rgba(6,17,9,.96);}
.login-form-title {color:#fff7b5 !important; font-size:1rem; font-weight:950; letter-spacing:.08em; text-transform:uppercase; margin:0 0 8px 0;}
.login-form-subtitle {color:#d0c264 !important; margin:0 0 16px 0; font-size:.78rem; font-weight:700;}
.login-demo {
    margin-top:18px; background:#020805; color:#d0c264;
    border:1px solid rgba(215,193,58,.28); border-radius:10px; padding:12px 14px;
    font-size:.78rem;
}
.login-demo b {color:#fff7b5;}
.login-demo code {background:#122116; color:#f4dd63; padding:2px 6px; border-radius:6px;}
.login-foot {text-align:center; color:#8e986d; font-size:.75rem; margin-top:12px;}
[data-testid="stForm"] {border:none !important; padding:0 !important; box-shadow:none !important; background:transparent !important;}

/* Top/header, based on the local dashboard */
.main-header {
    border: 1px solid rgba(215,193,58,.46);
    border-radius: 14px;
    padding: 14px 18px;
    background: linear-gradient(135deg, rgba(4,18,8,.98), rgba(11,34,14,.96));
    color: var(--text);
    margin: 0 auto 8px auto;
    box-shadow: 0 18px 40px rgba(0,0,0,.32), inset 0 0 26px rgba(159,209,52,.07);
    display:flex; align-items:center; justify-content:space-between; gap:16px;
}
.header-left h1 {
    margin:0; color:#fff7b5 !important; font-size:1.34rem; font-weight:950;
    letter-spacing:.16em; text-transform:uppercase;
}
.header-left p {margin:6px 0 0 0; color:#d0c264 !important; font-size:.78rem; font-weight:800;}
.header-logout {
    display:inline-flex; align-items:center; justify-content:center;
    min-width:118px; padding:9px 13px; border-radius:8px;
    border:1px solid rgba(215,193,58,.55);
    color:#f1df6a !important; text-decoration:none !important; font-weight:950; letter-spacing:.04em;
    background:#0b1a0d;
}
.header-logout:hover {background:#182b13; color:#fff !important; border-color:rgba(159,209,52,.8);}
.nav-card {
    padding:10px 12px; margin: 0 0 16px 0; border-radius:12px;
    background: rgba(4,16,8,.75); border:1px solid rgba(215,193,58,.25);
}
.stRadio > div {gap:10px;}
.stRadio [data-baseweb="radio"] {background:transparent !important;}
.stRadio label {color:#efe7a0 !important; font-size:.82rem !important;}

/* Titles and cards */
.section-title {
    color:#fff7b5 !important;
    font-size:1.08rem; font-weight:950; margin:12px 0 12px;
    text-transform:uppercase; letter-spacing:.09em;
    border:1px solid rgba(215,193,58,.38);
    border-radius:10px;
    padding:11px 13px;
    background: rgba(6,20,10,.92);
}
.metric-card {
    background: linear-gradient(180deg, #071609, #0a1d0d);
    border: 1px solid rgba(215,193,58,.34);
    border-radius: 10px;
    padding: 13px 14px;
    min-height: 106px;
    color: var(--text);
    box-shadow: inset 0 0 18px rgba(159,209,52,.05), 0 10px 24px rgba(0,0,0,.18);
}
.metric-card small {color:#d0c264; font-size:.72rem; font-weight:950; text-transform:uppercase; letter-spacing:.08em;}
.metric-card h2 {font-size:1.85rem; margin: 11px 0 3px 0; font-weight:950; color:#f3d93c !important;}
.metric-card p {margin:0; color:#aeb989; font-size:.75rem; font-weight:700;}
.soft-card {
    padding: 16px; border-radius: 12px; background:#06140a;
    border: 1px solid rgba(215,193,58,.35);
    box-shadow: 0 14px 28px rgba(0,0,0,.24);
}
.footer-note {color:#8e986d;font-size:0.78rem;margin-top:16px;}

/* Alerts */
.stAlert {
    background: rgba(6,20,10,.85) !important;
    border: 1px solid rgba(215,193,58,.32) !important;
    color: var(--text) !important;
}
.stAlert p {color: var(--text) !important;}

/* Product tables in local dark style */
.table-card {
    background: #06140a;
    border: 1px solid rgba(215,193,58,.38);
    border-radius: 12px;
    box-shadow: 0 16px 34px rgba(0,0,0,.28);
    overflow: hidden;
    margin-top: 10px;
    margin-bottom: 22px;
}
.table-head {
    padding: 12px 14px;
    background: linear-gradient(90deg, #06140a 0%, #0a2110 72%, #132b0f 100%);
    color: #fff7b5;
    display:flex; align-items:center; justify-content:space-between; gap:12px;
    border-bottom:1px solid rgba(215,193,58,.32);
}
.table-head-title {font-weight: 950; font-size: .88rem; letter-spacing:.10em; text-transform:uppercase; color:#fff7b5;}
.table-head-subtitle {font-size: .72rem; color:#d0c264; font-weight:800;}
.table-scroll {overflow-x:auto;}
table.pretty-table {width:100%; border-collapse: collapse; font-size:.80rem;}
.pretty-table th {
    text-align:left; background:#0d1d0d; color:#d9d06a; font-weight:950;
    padding:9px 10px; border-bottom:1px solid rgba(215,193,58,.28); white-space:nowrap;
}
.pretty-table td {
    padding:8px 10px; border-bottom:1px solid rgba(215,193,58,.13);
    color:#e7edd3; vertical-align:middle; white-space:nowrap;
}
.pretty-table tr:nth-child(even) td {background:rgba(255,255,255,.025);}
.pretty-table tr:hover td {background:rgba(159,209,52,.075);}
.pretty-table tr:last-child td {border-bottom:none;}
.name-cell {font-weight:900; color:#fffde1;}
.rank-cell {font-weight:900; color:#f1df6a;}
.value-wrap {display:flex; align-items:center; gap:8px; min-width:135px;}
.value-number {font-weight:950; min-width:36px; text-align:right; font-variant-numeric:tabular-nums; color:#fff7b5;}
.mini-track {height:7px; flex:1; min-width:70px; border-radius:999px; background:#132116; overflow:hidden; border:1px solid rgba(215,193,58,.18);}
.mini-fill {height:100%; border-radius:999px;}
.fill-good {background:#75cf3a;}
.fill-warn {background:#f59e0b;}
.fill-risk {background:#ef4444;}
.status-pill, .decision-pill {
    display:inline-flex; align-items:center; justify-content:center; padding:4px 9px;
    border-radius:7px; font-weight:950; font-size:.68rem; white-space:nowrap; letter-spacing:.02em;
}
.pill-pronto {background:rgba(34,197,94,.18); color:#95f06e; border:1px solid rgba(34,197,94,.42);}
.pill-atencao {background:rgba(245,158,11,.18); color:#ffd166; border:1px solid rgba(245,158,11,.48);}
.pill-risco {background:rgba(239,68,68,.18); color:#ff8080; border:1px solid rgba(239,68,68,.48);}
.pill-executa {background:rgba(34,197,94,.18); color:#95f06e; border:1px solid rgba(34,197,94,.42);}
.pill-monitorizar {background:rgba(245,158,11,.18); color:#ffd166; border:1px solid rgba(245,158,11,.48);}
.pill-retirar {background:rgba(239,68,68,.18); color:#ff8080; border:1px solid rgba(239,68,68,.48);}
.delta-neg {font-weight:950; color:#ff8080;}
.delta-pos {font-weight:950; color:#95f06e;}
.delta-zero {font-weight:950; color:#d0c264;}

/* Dataframes and expanders */
[data-testid="stDataFrame"] {background:#06140a !important; border:1px solid rgba(215,193,58,.28) !important; border-radius:12px !important; overflow:hidden;}
.streamlit-expanderHeader {background:#06140a !important; color:#fff7b5 !important; border:1px solid rgba(215,193,58,.28) !important; border-radius:10px !important;}

@media (max-width: 900px) {
    .block-container {padding-left: .9rem; padding-right: .9rem;}
    .main-header {align-items:flex-start; flex-direction:column;}
    .header-left h1 {font-size:1.08rem;}
    .login-title {font-size:1.25rem; letter-spacing:.10em;}
    .login-hero-top {align-items:flex-start; flex-direction:column;}
}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)


# Extra classes copied from the original local prototype dashboard
st.markdown(
    """
<style>
.tac-shell {
    border: 1px solid rgba(211,165,38,.42);
    border-radius: 18px;
    padding: 18px 20px 20px 20px;
    background:
      linear-gradient(180deg, rgba(8, 28, 14, 0.98), rgba(3, 14, 8, 0.98)),
      radial-gradient(circle at 15% 20%, rgba(36, 94, 38, 0.20), transparent 35%);
    box-shadow: 0 0 0 1px rgba(0,0,0,.18), 0 14px 34px rgba(0,0,0,.38);
    margin-bottom: 15px;
}
.topbar-local {
    display: flex; align-items: center; justify-content: space-between;
    gap: 14px; margin-bottom: 16px;
}
.title-wrap-local {display:flex; align-items:center; gap:14px;}
.logo-box-local {
    width: 56px; height: 56px; display:flex; align-items:center; justify-content:center;
    border-radius: 12px; background: linear-gradient(180deg, rgba(20,48,25,.96), rgba(3,15,8,.96));
    border: 1px solid rgba(211,165,38,.42); color: #f2bd28; font-size: 27px;
    box-shadow: inset 0 0 18px rgba(242,189,40,.08);
}
.h-title-local {color:#f4ead0; font-size:28px; font-weight:900; line-height:1; letter-spacing:.4px; text-transform:uppercase;}
.h-subtitle-local {color:#a9a47d; font-size:12px; font-weight:700; margin-top:6px;}
.status-wrap-local {display:flex; align-items:center; gap:10px; flex-wrap:wrap; justify-content:flex-end;}
.status-pill-local {
    border: 1px solid rgba(211,165,38,.35); background: rgba(7,25,12,.95);
    border-radius: 9px; padding: 8px 12px; color:#e3d08a; font-size:12px;
    font-weight:800; text-transform:uppercase;
}
.sync-dot-local {color:#66f060; margin-right:5px;}
.filter-row-local {
    border: 1px solid rgba(211,165,38,.30); border-radius: 12px;
    background: rgba(5,18,9,.68); padding: 12px 14px 2px 14px; margin: 0 0 14px 0;
}
.filter-title-local {color:#e3d08a; font-size:12px; font-weight:900; text-transform:uppercase; letter-spacing:.30px; margin-bottom:6px;}
.kpi-card-local {
    background: linear-gradient(180deg, rgba(12,43,20,.96), rgba(4,18,9,.96));
    border: 1px solid rgba(211,165,38,.42); border-radius: 12px; padding:14px 15px;
    min-height:114px; box-shadow: inset 0 0 22px rgba(108,255,104,.035), 0 7px 20px rgba(0,0,0,.22);
    overflow:hidden;
}
.kpi-label-local {font-size:11px; color:#e3d08a; font-weight:900; text-transform:uppercase; letter-spacing:.35px; margin-bottom:7px;}
.kpi-number-local {font-size:38px; line-height:1; font-weight:900; margin:2px 0 6px 0;}
.kpi-detail-local {font-size:12px; font-weight:800; color:#a9a47d;}
.kpi-icon-local {font-size:28px; text-align:right; margin-top:4px;}
.local-green {color:#64d95f !important;} .local-yellow {color:#f2c335 !important;} .local-orange {color:#ff8c22 !important;} .local-red {color:#ff3d2e !important;} .local-gold {color:#f2bd28 !important;}
.section-card-local {
    background: linear-gradient(180deg, rgba(9,34,17,.96), rgba(3,16,8,.96));
    border: 1px solid rgba(211,165,38,.42); border-radius:12px; padding:13px 14px; margin-bottom:12px;
    box-shadow: inset 0 0 20px rgba(242,189,40,.025), 0 7px 18px rgba(0,0,0,.20);
}
.section-title-local {color:#e3d08a; font-size:14px; font-weight:900; text-transform:uppercase; letter-spacing:.35px; margin-bottom:10px;}
.alert-item-local, .rec-item-local {display:flex; align-items:center; justify-content:space-between; gap:12px; padding:9px 0; border-bottom:1px solid rgba(211,165,38,.14);}
.alert-item-local:last-child, .rec-item-local:last-child {border-bottom:none;}
.rec-left-local {display:flex; align-items:center; gap:9px;}
.rec-icon-local {width:26px; height:26px; border-radius:8px; border:1px solid rgba(211,165,38,.28); display:flex; align-items:center; justify-content:center; background:rgba(0,0,0,.18);}
.rec-text-local {color:#f4ead0; font-weight:800; font-size:12px;}
.rec-sub-local {color:#a9a47d; font-weight:700; font-size:11px; margin-top:2px;}
.badge-local {border-radius:999px; padding:3px 8px; border:1px solid rgba(211,165,38,.26); font-size:10px; font-weight:900; text-transform:uppercase;}
.commander-actions-local {display:grid; grid-template-columns:repeat(3,1fr); gap:12px; margin-top:10px;}
.action-card-local {display:flex; align-items:center; gap:14px; border:1px solid rgba(211,165,38,.42); border-radius:12px; background:linear-gradient(180deg, rgba(18,51,25,.78), rgba(6,20,10,.88)); padding:14px 15px; min-height:82px;}
.action-icon-local {width:48px; height:48px; border-radius:99px; display:flex; align-items:center; justify-content:center; border:1px solid rgba(211,165,38,.40); color:#f2bd28; font-size:24px;}
.action-title-local {color:#f4ead0; font-weight:900; text-transform:uppercase; font-size:15px;}
.action-sub-local {color:#a9a47d; font-size:12px; font-weight:700; margin-top:2px;}
.decision-box-local {padding:14px 16px; border-radius:10px; background:rgba(88,92,6,.70); border:1px solid rgba(211,165,38,.32); color:#fff5bd; font-weight:800;}
@media (max-width:900px){.topbar-local{align-items:flex-start; flex-direction:column;} .commander-actions-local{grid-template-columns:1fr;}}
</style>
""",
    unsafe_allow_html=True,
)


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
            <div class="login-foot">Protótipo EITT · Streamlit Cloud + Supabase PostgreSQL/Auth · Dados fictícios</div>
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
    """Applies the original local prototype dark military visual language to Plotly figures."""
    fig.update_layout(
        height=height,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="#06140a",
        font=dict(family="Inter, Arial, sans-serif", color="#dce7b6"),
        title=dict(font=dict(size=15, color="#fff7b5"), x=0.02),
        margin=dict(l=18, r=18, t=50, b=24),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(color="#dce7b6"),
            bgcolor="rgba(0,0,0,0)",
        ),
    )
    fig.update_xaxes(gridcolor="rgba(215,193,58,.16)", zerolinecolor="rgba(215,193,58,.25)", linecolor="rgba(215,193,58,.25)")
    fig.update_yaxes(gridcolor="rgba(215,193,58,.16)", zerolinecolor="rgba(215,193,58,.25)", linecolor="rgba(215,193,58,.25)")
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
    table_html = f"""
    <div class="table-card">
        <div class="table-head">
            <div class="table-head-title">{html.escape(title)}</div>
            {subtitle_html}
        </div>
        <div class="table-scroll">
            <table class="pretty-table">
                <thead><tr>{head}</tr></thead>
                <tbody>{''.join(html_rows)}</tbody>
            </table>
        </div>
    </div>
    """
    st.markdown(table_html, unsafe_allow_html=True)

# -----------------------------
# Visual digital twin
# -----------------------------
def digital_twin_figure(muscle: Dict[str, Any], title: str = "Digital Twin — carga muscular") -> go.Figure:
    # Stylized body map using simple geometric zones.
    zones = [
        ("Ombros", "shoulders", 0.50, 0.78, 0.36, 0.08),
        ("Peito", "chest", 0.50, 0.68, 0.28, 0.11),
        ("Costas", "back", 0.50, 0.58, 0.30, 0.10),
        ("Core", "core", 0.50, 0.47, 0.22, 0.12),
        ("Braços", "arms", 0.25, 0.58, 0.10, 0.30),
        ("Braços", "arms", 0.75, 0.58, 0.10, 0.30),
        ("Pernas", "legs", 0.43, 0.27, 0.13, 0.31),
        ("Pernas", "legs", 0.57, 0.27, 0.13, 0.31),
        ("Gémeos", "calves", 0.43, 0.08, 0.11, 0.18),
        ("Gémeos", "calves", 0.57, 0.08, 0.11, 0.18),
    ]
    fig = go.Figure()
    fig.add_shape(type="circle", x0=0.43, y0=0.84, x1=0.57, y1=0.98, line=dict(color="#111827"), fillcolor="#e5e7eb")
    for label, key, cx, cy, w, h in zones:
        val = int(muscle.get(key) or 0)
        if val >= 75:
            color = "#ef4444"
        elif val >= 55:
            color = "#f59e0b"
        else:
            color = "#22c55e"
        fig.add_shape(type="rect", x0=cx-w/2, y0=cy-h/2, x1=cx+w/2, y1=cy+h/2,
                      line=dict(color="white", width=2), fillcolor=color, opacity=0.82)
        fig.add_annotation(x=cx, y=cy, text=f"{label}<br>{val}%", showarrow=False, font=dict(color="white", size=12))
    fig.update_xaxes(visible=False, range=[0, 1])
    fig.update_yaxes(visible=False, range=[0, 1])
    fig.update_layout(height=520, title=title, margin=dict(l=10, r=10, t=45, b=10), plot_bgcolor="white")
    return fig

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
            <h1>Digital Twin Militar</h1>
            <p>▲ Sessão iniciada · {html.escape(str(profile.get('rank','')))} {html.escape(str(profile.get('full_name','')))} · {html.escape(str(ROLE_LABELS.get(profile.get('role'), profile.get('role'))))}</p>
        </div>
        <a class="header-logout" href="?logout=1" target="_self">Terminar sessão</a>
    </div>
    <div class="nav-card">
    """, unsafe_allow_html=True)
    choice = st.radio("Navegação", page_options, horizontal=True, label_visibility="collapsed")
    st.markdown("</div>", unsafe_allow_html=True)
    return choice


def commander_dashboard(profile: Dict[str, Any]) -> None:
    """Commander page styled to match the original local prototype, but using live Supabase data."""
    df = assemble_snapshot()
    if df.empty:
        st.warning("Ainda não há dados acessíveis para este utilizador.")
        return

    df = df.copy()
    for col in ["readiness_score", "injury_risk", "recovery_score", "fatigue_score", "sleep_hours", "cooper_m"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Operational state used in the old local dashboard.
    def _estado(row: pd.Series) -> str:
        ready = float(row.get("readiness_score") or 0)
        risk = float(row.get("injury_risk") or 0)
        recovery = float(row.get("recovery_score") or 50)
        if ready >= 75 and risk < 35:
            return "Apto"
        if ready >= 60 and risk < 55:
            return "Com limitações"
        if risk >= 70 or ready < 45 or recovery < 45:
            return "Indisponível"
        return "Em risco"

    def _disponibilidade(row: pd.Series) -> str:
        est = row.get("estado_operacional", "Em risco")
        if est == "Apto":
            return "Pronto"
        if est == "Com limitações":
            return "Condicionado"
        if est == "Em risco":
            return "Em risco"
        return "Não recomendado"

    df["estado_operacional"] = df.apply(_estado, axis=1)
    df["disponibilidade"] = df.apply(_disponibilidade, axis=1)

    # Human readable platoon/section names.
    platoons = df_from("platoons", order="name")
    platoon_map = {}
    if not platoons.empty and "id" in platoons.columns:
        platoon_map = dict(zip(platoons["id"], platoons.get("name", platoons["id"])))
    df["unidade"] = df.get("platoon_id", pd.Series([None] * len(df))).map(platoon_map).fillna("Companhia")

    now = pd.Timestamp.now()
    st.markdown(
        f"""
        <div class="tac-shell">
          <div class="topbar-local">
            <div class="title-wrap-local">
              <div class="logo-box-local">⚔️</div>
              <div>
                <div class="h-title-local">Dashboard do Comandante</div>
                <div class="h-subtitle-local">Monitorização da força com dados do digital twin</div>
              </div>
            </div>
            <div class="status-wrap-local">
              <div class="status-pill-local"><span class="sync-dot-local">●</span>Sincronizado</div>
              <div class="status-pill-local">Última atualização&nbsp;&nbsp; {now.strftime('%H:%M:%S')}</div>
              <div class="status-pill-local">{now.strftime('%d %b %Y').upper()}</div>
            </div>
          </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="filter-row-local"><div class="filter-title-local">Filtros disponíveis</div>', unsafe_allow_html=True)
    f1, f2, f3 = st.columns([1, 2.2, 1])
    unidades_all = sorted(df["unidade"].dropna().unique().tolist())
    estados_all = ["Apto", "Com limitações", "Em risco", "Indisponível"]
    with f1:
        unidade = st.selectbox("Pelotão / Secção", ["Todas"] + unidades_all, key="cmd_filter_unidade_v6")
    with f2:
        estado_sel = st.multiselect("Estado operacional", estados_all, default=estados_all, key="cmd_filter_estado_v6")
    with f3:
        ordenar = st.selectbox("Ordenar por", ["Maior risco", "Menor prontidão", "Carga", "Nome"], key="cmd_filter_sort_v6")
    st.markdown('</div>', unsafe_allow_html=True)

    view = df.copy()
    if unidade != "Todas":
        view = view[view["unidade"] == unidade]
    view = view[view["estado_operacional"].isin(estado_sel)] if estado_sel else view.iloc[0:0]

    if ordenar == "Maior risco":
        view = view.sort_values(["injury_risk", "readiness_score"], ascending=[False, True])
    elif ordenar == "Menor prontidão":
        view = view.sort_values(["readiness_score", "injury_risk"], ascending=[True, False])
    elif ordenar == "Carga" and "fatigue_score" in view.columns:
        view = view.sort_values(["fatigue_score", "injury_risk"], ascending=[False, False])
    else:
        view = view.sort_values("full_name")

    total = max(len(view), 1)
    aptos = int((view["estado_operacional"] == "Apto").sum())
    limit = int((view["estado_operacional"] == "Com limitações").sum())
    risco = int((view["estado_operacional"] == "Em risco").sum())
    indis = int((view["estado_operacional"] == "Indisponível").sum())
    alertas_crit = int((view["injury_risk"].fillna(0) >= 70).sum())
    alertas_at = int(((view["injury_risk"].fillna(0) >= 50) & (view["injury_risk"].fillna(0) < 70)).sum())

    def kpi_html(label: str, value: str, detail: str, color: str, icon: str) -> str:
        return f"""
        <div class="kpi-card-local">
          <div class="kpi-label-local local-{color}">{html.escape(label)}</div>
          <div class="kpi-number-local local-{color}">{html.escape(value)}</div>
          <div class="kpi-detail-local">{html.escape(detail)}</div>
          <div class="kpi-icon-local local-{color}">{icon}</div>
        </div>
        """

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(kpi_html("Estado de prontidão", f"{aptos/total*100:.0f}%", f"{aptos} aptos · {limit} com limitações", "green", "✓"), unsafe_allow_html=True)
    with c2:
        st.markdown(kpi_html("Disponibilidade para missão", f"{(aptos+limit)/total*100:.0f}%", f"{aptos+limit} prontos/condicionados", "yellow", "⊙"), unsafe_allow_html=True)
    with c3:
        st.markdown(kpi_html("Alertas ativos", str(alertas_crit + alertas_at), f"Críticos: {alertas_crit} · Atenção: {alertas_at}", "red" if alertas_crit else "yellow", "🔔"), unsafe_allow_html=True)
    with c4:
        st.markdown(kpi_html("Não recomendado", str(indis + risco), f"{risco} em risco · {indis} indisponíveis", "orange", "⚠"), unsafe_allow_html=True)

    st.write("")
    col_table, col_charts, col_alerts = st.columns([1.55, 1.05, 1.1])

    with col_table:
        table = view[["rank", "full_name", "unidade", "readiness_score", "injury_risk", "fatigue_score", "disponibilidade"]].copy()
        table = table.rename(columns={
            "rank": "Posto",
            "full_name": "Militar",
            "unidade": "Unidade",
            "readiness_score": "Prontidão",
            "injury_risk": "Risco",
            "fatigue_score": "Carga",
            "disponibilidade": "Disponibilidade",
        })
        st.markdown('<div class="section-card-local"><div class="section-title-local">▣ Situação dos militares</div>', unsafe_allow_html=True)
        st.dataframe(table, use_container_width=True, hide_index=True, height=390)
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="section-card-local"><div class="section-title-local">◉ Estado geral por pelotão/secção</div>', unsafe_allow_html=True)
        grouped = view.groupby(["unidade", "estado_operacional"]).size().reset_index(name="n")
        if not grouped.empty:
            fig = px.bar(
                grouped,
                x="unidade",
                y="n",
                color="estado_operacional",
                barmode="stack",
                color_discrete_map={"Apto": "#64d95f", "Com limitações": "#f2c335", "Em risco": "#ff8c22", "Indisponível": "#ff3d2e"},
                labels={"unidade": "unidade", "n": "", "estado_operacional": "estado operacional"},
            )
            fig = apply_chart_style(fig, height=260)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.caption("Sem dados para o filtro atual.")
        st.markdown('</div>', unsafe_allow_html=True)

    with col_charts:
        st.markdown('<div class="section-card-local"><div class="section-title-local">📈 Evolução do rendimento físico</div>', unsafe_allow_html=True)
        tests = df_from("physical_tests", order="test_date")
        if not tests.empty:
            tests = tests.copy()
            tests["test_date"] = pd.to_datetime(tests["test_date"], errors="coerce")
            trend = tests.groupby("test_date", as_index=False).agg(
                cooper_m=("cooper_m", "mean"),
                pushups=("pushups", "mean"),
                pullups=("pullups", "mean"),
            ).sort_values("test_date")
            fig = go.Figure()
            if "cooper_m" in trend:
                fig.add_trace(go.Scatter(x=trend["test_date"], y=trend["cooper_m"], mode="lines+markers", name="Cooper médio", line=dict(color="#64d95f", width=3)))
            if "pushups" in trend:
                fig.add_trace(go.Scatter(x=trend["test_date"], y=trend["pushups"] * 45, mode="lines+markers", name="Flexões", line=dict(color="#f2c335", width=3)))
            if "pullups" in trend:
                fig.add_trace(go.Scatter(x=trend["test_date"], y=trend["pullups"] * 160, mode="lines+markers", name="Barras", line=dict(color="#ff8c22", width=3)))
            fig = apply_chart_style(fig, height=260)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.caption("Sem histórico de testes físicos.")
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="section-card-local"><div class="section-title-local">⏱ Carga acumulada</div>', unsafe_allow_html=True)
        carga_media = float(view["fatigue_score"].dropna().mean()) if "fatigue_score" in view and not view.empty else 0
        figg = go.Figure(go.Indicator(
            mode="gauge+number",
            value=carga_media,
            number={"suffix": "/100", "font": {"color": "#f4ead0", "size": 34}},
            gauge={
                "axis": {"range": [0, 100], "tickcolor": "#e8d9a8"},
                "bar": {"color": "#f2bd28"},
                "bgcolor": "rgba(0,0,0,0)",
                "bordercolor": "rgba(211,165,38,.25)",
                "steps": [
                    {"range": [0, 40], "color": "rgba(100,217,95,.65)"},
                    {"range": [40, 70], "color": "rgba(242,195,53,.65)"},
                    {"range": [70, 100], "color": "rgba(255,61,46,.65)"},
                ],
            },
        ))
        figg = apply_chart_style(figg, height=260)
        st.plotly_chart(figg, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col_alerts:
        st.markdown('<div class="section-card-local"><div class="section-title-local">⚠ Alertas de quebra de desempenho</div>', unsafe_allow_html=True)
        alert_df = view[(view["injury_risk"].fillna(0) >= 50) | (view["readiness_score"].fillna(100) < 55)].sort_values("injury_risk", ascending=False)
        if alert_df.empty:
            st.markdown('<div class="rec-sub-local local-green">Sem alertas relevantes na força selecionada.</div>', unsafe_allow_html=True)
        else:
            for _, r in alert_df.head(6).iterrows():
                lvl = "Crítico" if float(r.get("injury_risk") or 0) >= 70 else "Atenção"
                col = "red" if lvl == "Crítico" else "yellow"
                st.markdown(
                    f"""
                    <div class="alert-item-local">
                      <div><div class="rec-text-local local-{col}">{html.escape(str(r.get('full_name', '')))}</div><div class="rec-sub-local">Risco {int(float(r.get('injury_risk') or 0))}% · Prontidão {int(float(r.get('readiness_score') or 0))}%</div></div>
                      <div class="badge-local local-{col}">{lvl}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="section-card-local"><div class="section-title-local">▣ Recomendações práticas</div>', unsafe_allow_html=True)
        rec_cmd = []
        if indis > 0:
            rec_cmd.append(("🩺", "Avaliar militar", f"{indis} não recomendados"))
        if risco > 0:
            rec_cmd.append(("⬇️", "Reduzir carga de treino", f"{risco} em risco"))
        if limit > 0:
            rec_cmd.append(("🛌", "Dar recuperação adicional", f"{limit} condicionados"))
        if aptos > 0:
            rec_cmd.append(("✅", "Selecionar militares aptos", f"{aptos} prontos"))
        if not rec_cmd:
            rec_cmd.append(("✅", "Manter plano atual", "força estável"))
        for icon, title, sub in rec_cmd:
            st.markdown(
                f"""
                <div class="rec-item-local">
                  <div class="rec-left-local"><div class="rec-icon-local">{icon}</div><div><div class="rec-text-local">{html.escape(title)}</div><div class="rec-sub-local">{html.escape(sub)}</div></div></div>
                  <div class="local-gold">›</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="section-card-local"><div class="section-title-local">🎯 Decisão recomendada agora</div>', unsafe_allow_html=True)
        if indis > 0:
            msg = "Há militares não recomendados: retirar de tarefas exigentes e avaliar condição."
        elif risco > 0:
            msg = "Existem militares em risco: reduzir carga e monitorizar nas próximas 24–48h."
        else:
            msg = "Força globalmente estável para manter plano de treino/missão."
        st.markdown(f'<div class="decision-box-local">{html.escape(msg)}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown(
        """
        <h3 style="color:#f4ead0;margin-top:16px;">Ações rápidas do comandante</h3>
        <div class="commander-actions-local">
          <div class="action-card-local"><div class="action-icon-local">✓</div><div><div class="action-title-local">Quem está pronto?</div><div class="action-sub-local">Filtrar aptos para treino/missão</div></div></div>
          <div class="action-card-local"><div class="action-icon-local">⚠</div><div><div class="action-title-local">Quem está em risco?</div><div class="action-sub-local">Ver militares que exigem adaptação</div></div></div>
          <div class="action-card-local"><div class="action-icon-local">🎯</div><div><div class="action-title-local">Que decisão tomar?</div><div class="action-sub-local">Resumo operacional imediato</div></div></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('</div>', unsafe_allow_html=True)


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
        name_map = {f"{row.get('rank','')} {row['full_name']}": row["id"] for _, row in all_soldiers.iterrows()}
        default_index = 0
        if forced_soldier_id and forced_soldier_id in name_map.values():
            default_index = list(name_map.values()).index(forced_soldier_id)
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

    c1, c2, c3, c4 = st.columns(4)
    with c1: metric_card("Prontidão", f"{latest.get('readiness_score', '—')}%", latest.get("status", "sem estado"))
    with c2: metric_card("Risco de lesão", f"{latest.get('injury_risk', '—')}%", "estimativa atual")
    with c3: metric_card("Recuperação", f"{latest.get('recovery_score', '—')}%", "sono/fadiga/carga")
    with c4: metric_card("Cooper", f"{tlatest.get('cooper_m', '—')} m", "último teste")

    st.divider()
    p1, p2 = st.columns([1.2, 1])
    with p1:
        if not readiness.empty:
            trend = readiness.sort_values("score_date")
            fig = px.line(trend, x="score_date", y=["readiness_score", "injury_risk", "recovery_score"], markers=True,
                          labels={"value": "Score", "score_date": "Data", "variable": "Métrica"}, title="Evolução do estado físico")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Sem histórico de prontidão.")
    with p2:
        st.markdown("#### Recomendação atual")
        if not recs.empty:
            for _, r in recs.head(4).iterrows():
                st.markdown(f"**{r['priority']} · {r['title']}**")
                st.write(r["message"])
                st.caption(f"{r['category']} · {r['rec_date']}")
                st.divider()
        else:
            st.success("Sem recomendações críticas.")

    return soldier_id


def twin_page(profile: Dict[str, Any]) -> None:
    st.markdown('<div class="section-title">Digital Twin visual</div>', unsafe_allow_html=True)
    soldier_id = soldier_page(profile)
    if not soldier_id:
        return
    muscle_df = df_from("muscle_loads", order="load_date", desc=True, filters=[("soldier_id", "eq", soldier_id)])
    if muscle_df.empty:
        st.warning("Sem dados de carga muscular para este militar.")
        return
    muscle = muscle_df.iloc[0].to_dict()
    a, b = st.columns([1, 1])
    with a:
        st.plotly_chart(digital_twin_figure(muscle), use_container_width=True)
    with b:
        values = {k: muscle.get(k, 0) for k in ["chest", "back", "shoulders", "arms", "core", "legs", "calves"]}
        pt = {"chest": "Peito", "back": "Costas", "shoulders": "Ombros", "arms": "Braços", "core": "Core", "legs": "Pernas", "calves": "Gémeos"}
        chart = pd.DataFrame({"Grupo muscular": [pt[k] for k in values], "Carga": list(values.values())})
        fig = px.bar(chart, x="Grupo muscular", y="Carga", title="Carga por grupo muscular", range_y=[0, 100])
        st.plotly_chart(fig, use_container_width=True)
        high = chart[chart["Carga"] >= 75]["Grupo muscular"].tolist()
        if high:
            st.error("Zonas críticas: " + ", ".join(high))
        else:
            st.success("Sem zonas musculares em carga crítica.")


def build_group_selection(snapshot: pd.DataFrame) -> Tuple[str, pd.DataFrame]:
    """Selects an operational group for command-level simulation."""
    st.caption("Simulação coletiva: aplica o treino a um escalão operacional e calcula o impacto previsto em cada militar.")
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
            st.success("Simulação coletiva guardada na base de dados, associada a cada militar do grupo.")
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

    st.markdown('<p class="footer-note">Protótipo EITT · Dados fictícios · Streamlit + Supabase PostgreSQL/Auth</p>', unsafe_allow_html=True)


if __name__ == "__main__":
    main()

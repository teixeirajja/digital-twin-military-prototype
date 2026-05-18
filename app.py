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
    fig.update_layout(height=520, title=title, margin=dict(l=10, r=10, t=45, b=10), plot_bgcolor="#ffffff", paper_bgcolor="rgba(0,0,0,0)", font=dict(color="#213322"))
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
        if st.session_state.get("page") != "Dashboard":
            if st.button("← Voltar ao dashboard", key="back_dashboard_from_soldier", use_container_width=False):
                st.session_state["page"] = "Dashboard"
                st.rerun()
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
            fig = apply_chart_style(fig, height=430)
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
    if st.button("← Voltar ao dashboard", key="back_dashboard_from_simulator", use_container_width=False):
        st.session_state["page"] = "Dashboard"
        st.rerun()
    st.markdown(
        '<div class="action-box"><b>Para que serve guardar a simulação?</b><br>'
        '<span>Guarda uma previsão histórica do treino para cada militar do grupo: prontidão prevista, risco previsto e decisão recomendada. '
        'Não altera a prontidão real. Serve para comparar depois o planeado com o resultado observado após o treino.</span></div>',
        unsafe_allow_html=True,
    )
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

    if st.button("Guardar previsão coletiva na base de dados", use_container_width=True):
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
            st.success("Previsão coletiva guardada. A prontidão real não foi alterada.")
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

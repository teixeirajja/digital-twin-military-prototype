from __future__ import annotations

import html
import math
import uuid
import textwrap
from datetime import date
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import streamlit.components.v1 as components
from supabase import Client, create_client

st.set_page_config(
    page_title="Military Digital Twin",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# =========================================================
# CSS — professional military clean UI
# =========================================================
CSS = """
<style>
:root {
  --page: #eef3e6;
  --page2: #fbfaf2;
  --ink: #061f10;
  --muted: #5f6c5b;
  --panel: #ffffff;
  --soft: #f5f8ef;
  --line: rgba(20,83,45,.16);
  --line2: rgba(20,83,45,.28);
  --g900: #05200f;
  --g800: #073618;
  --g700: #14532d;
  --g600: #166534;
  --g500: #22c55e;
  --yel: #d7b92f;
  --amb: #f59e0b;
  --red: #ef4444;
  --shadow: 0 18px 48px rgba(16,32,21,.10);
}
html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"] {
  background:
    radial-gradient(circle at 6% 0%, rgba(34,197,94,.10), transparent 26%),
    radial-gradient(circle at 90% 5%, rgba(215,185,47,.14), transparent 24%),
    linear-gradient(180deg, var(--page2) 0%, var(--page) 55%, #e8eddc 100%) !important;
  color: var(--ink) !important;
}
.block-container {max-width: 1680px !important; width: min(1680px, 96vw) !important; padding: 1.1rem 2rem 2.5rem !important;}
#MainMenu, footer, header {visibility: hidden;}
[data-testid="stToolbar"], [data-testid="stDecoration"], [data-testid="stStatusWidget"], [data-testid="stHeader"], [data-testid="InputInstructions"] {display:none !important;}
h1,h2,h3,h4,h5,h6,p,div,span,label {font-family: Inter, Segoe UI, Arial, sans-serif;}
h1,h2,h3,h4 {color: var(--ink) !important;}
hr {border-color: rgba(20,83,45,.13) !important;}

.stTextInput input, .stPassword input, .stNumberInput input, .stDateInput input,
.stSelectbox [data-baseweb="select"], .stMultiSelect [data-baseweb="select"] {
  background: #fff !important; color: var(--ink) !important; border: 1px solid rgba(20,83,45,.22) !important;
  border-radius: 12px !important; min-height: 42px; box-shadow: 0 6px 18px rgba(16,32,21,.05) !important;
}
.stSlider label, .stSelectbox label, .stTextInput label, .stCheckbox label, .stRadio label {font-weight: 800 !important; color: #243623 !important; font-size: .84rem !important;}
.stButton > button, .stFormSubmitButton > button {
  border-radius: 14px !important; border: 1px solid rgba(20,83,45,.25) !important; background: #fff !important;
  color: var(--g700) !important; font-weight: 950 !important; min-height: 58px; padding: 0 22px !important; font-size: 1.02rem !important; box-shadow: 0 8px 22px rgba(16,32,21,.07) !important;
}
.stButton > button:hover, .stFormSubmitButton > button:hover {background: var(--g700) !important; color: #fff !important;}
[data-testid="stBaseButton-primary"] {background:linear-gradient(135deg,var(--g800),var(--g600)) !important; color:#fff8cf !important; border-color:var(--g700) !important;}
[data-testid="stBaseButton-primary"] p, [data-testid="stBaseButton-primary"] span {color:#fff8cf !important;}
[data-testid="stBaseButton-secondary"] {background:#fff !important; color:var(--g800) !important;}

/* Login */
.login-shell {max-width: 980px; margin: 6vh auto 0 auto;}
.login-hero {padding: 24px; border-radius: 22px; background: linear-gradient(135deg, var(--g900), var(--g700)); box-shadow: 0 26px 70px rgba(16,32,21,.25); color:#fff;}
.login-top {display:flex; justify-content:space-between; align-items:center; gap:18px;}
.login-brand {display:flex; gap:16px; align-items:center;}
.login-logo {width:56px; height:56px; border-radius:16px; background:rgba(255,255,255,.12); border:1px solid rgba(255,255,255,.20); display:flex; align-items:center; justify-content:center; font-size:1.55rem;}
.login-title {margin:0; color:#fff8cf !important; font-size:1.58rem; font-weight:950; letter-spacing:.10em; text-transform:uppercase;}
.login-subtitle {margin:6px 0 0; color:#d8e7c7 !important; font-size:.86rem; font-weight:700;}
.login-badge {color:#fff8cf; background:rgba(0,0,0,.18); border:1px solid rgba(255,248,207,.25); border-radius:999px; padding:9px 14px; font-size:.76rem; font-weight:900; text-transform:uppercase;}
[data-testid="stForm"] {max-width: 980px !important; margin: 16px auto 0 auto !important; background:#fff !important; border:1px solid var(--line) !important; border-radius:20px !important; padding:18px !important; box-shadow: var(--shadow) !important;}
.login-demo {max-width:980px; margin:18px auto 0; background:#f5f7ed; color:#475240; border:1px solid var(--line); border-radius:14px; padding:14px 16px; font-size:.82rem;}
.login-demo b {color:var(--g800);} .login-demo code {background:#e7efdc; color:#14532d; padding:2px 6px; border-radius:7px;}
.login-foot {text-align:center; color:#677160; font-size:.76rem; margin-top:12px;}

/* Header */
.main-header {border-radius:24px; padding:21px 24px; background:linear-gradient(135deg, var(--g900), var(--g800) 60%, var(--g700)); color:#fff; margin-bottom:18px; box-shadow:0 22px 55px rgba(16,32,21,.22); display:flex; justify-content:space-between; align-items:center; gap:20px;}
.main-header h1 {margin:0; color:#fff8cf !important; font-size:1.45rem; font-weight:950; letter-spacing:.10em; text-transform:uppercase;}
.main-header p {margin:7px 0 0; color:#d8e7c7 !important; font-size:.83rem; font-weight:700;}
.header-chip {display:inline-flex; align-items:center; justify-content:center; min-width:150px; padding:11px 16px; border-radius:14px; border:1px solid rgba(255,248,207,.30); color:#fff8cf !important; font-weight:900; background:rgba(0,0,0,.14); text-decoration:none !important;}
.logout-link:hover {background:#fff8cf !important; color:var(--g900) !important; border-color:#fff8cf !important;}

/* Radio navigation */
.nav-label {margin: 18px 0 8px 4px; color: var(--g800); font-size:.78rem; font-weight:950; text-transform:uppercase; letter-spacing:.06em;}
[data-testid="stRadio"] {width:100% !important; max-width:100% !important; margin-bottom:12px !important;}
[data-testid="stRadio"] > div {width:100% !important; max-width:100% !important;}
[data-testid="stRadio"] > label {display:none !important;}
[data-testid="stRadio"] div[role="radiogroup"] {display:flex !important; flex-direction:row !important; flex-wrap:nowrap !important; gap:12px !important; background:rgba(255,255,255,.72) !important; border:1px solid var(--line) !important; border-radius:999px !important; padding:8px !important; width:100% !important; max-width:100% !important; box-shadow:0 10px 28px rgba(16,32,21,.07) !important;}
[data-testid="stRadio"] div[role="radiogroup"] label {display:flex !important; align-items:center !important; justify-content:center !important; flex:1 1 0 !important; min-width:0 !important; min-height:46px !important; padding:0 18px !important; border-radius:999px !important; border:1px solid rgba(20,83,45,.18) !important; background:#fff !important; color:var(--g800) !important; box-shadow:0 5px 14px rgba(16,32,21,.05) !important; cursor:pointer !important; font-weight:950 !important; text-align:center !important;}
[data-testid="stRadio"] div[role="radiogroup"] label:has(input:checked) {background:linear-gradient(135deg, var(--g800), var(--g600)) !important; color:#fff8cf !important; border-color:var(--g600) !important;}
[data-testid="stRadio"] div[role="radiogroup"] label[data-checked="true"],
[data-testid="stRadio"] div[role="radiogroup"] label:has([aria-checked="true"]),
[data-testid="stRadio"] div[role="radiogroup"] label:has(input:checked) {background:linear-gradient(135deg, var(--g800), var(--g600)) !important; color:#fff8cf !important; border-color:var(--g600) !important; box-shadow:0 10px 24px rgba(20,83,45,.23) !important;}
[data-testid="stRadio"] div[role="radiogroup"] label input, [data-testid="stRadio"] div[role="radiogroup"] label > div:first-child {display:none !important;}
[data-testid="stRadio"] div[role="radiogroup"] label p {color:inherit !important; font-size:.94rem !important; font-weight:950 !important; white-space:nowrap !important; overflow:hidden !important; text-overflow:ellipsis !important;}
.header-context {margin-top:12px; padding-top:12px; border-top:1px solid rgba(255,248,207,.18); color:#fff8cf !important; font-size:.98rem !important; font-weight:950 !important; letter-spacing:.05em; text-transform:none;}

.section-card {background:#fff; border:1px solid var(--line); border-radius:18px; padding:18px; box-shadow:var(--shadow); margin-bottom:22px;}
.section-title {background:#fff; border:1px solid var(--line); border-left:6px solid var(--g700); border-radius:14px; padding:16px 18px; font-size:1.1rem; font-weight:950; color:var(--ink); letter-spacing:.05em; margin:10px 0 16px;}
.metric-card {background:#fff; border:1px solid var(--line); border-left:5px solid var(--g700); border-radius:16px; padding:18px 19px; box-shadow:var(--shadow); min-height:132px; margin-bottom:20px;}
.metric-card small {display:block; text-transform:uppercase; color:var(--g700); font-weight:950; letter-spacing:.06em; margin-bottom:12px;}
.metric-card h2 {margin:0 0 9px; font-size:1.86rem; color:var(--ink) !important; font-weight:950;}
.metric-card p {margin:0; color:var(--muted); font-weight:700; font-size:.86rem;}
.info-card {background:#fff; border:1px solid var(--line); border-radius:18px; padding:20px; box-shadow:var(--shadow); margin-bottom:22px;}
.info-card h3 {margin:0 0 12px; font-size:1.1rem; color:var(--ink) !important;}
.info-row {display:flex; justify-content:space-between; gap:12px; padding:9px 0; border-bottom:1px solid rgba(20,83,45,.10); color:#243623;}
.info-row b {color:var(--ink);}

.status-pill {display:inline-flex; align-items:center; justify-content:center; border-radius:999px; padding:6px 12px; font-weight:950; font-size:.78rem; border:1px solid;}
.pill-pronto {background:#dcfce7; color:#166534; border-color:#86efac;}
.pill-atencao {background:#fef3c7; color:#92400e; border-color:#fcd34d;}
.pill-risco {background:#fee2e2; color:#991b1b; border-color:#fca5a5;}
.pill-muted {background:#f1f5f9; color:#334155; border-color:#cbd5e1;}

.bar-wrap {height:8px; width:100%; border-radius:999px; background:#dfe8d9; overflow:hidden; border:1px solid rgba(20,83,45,.12);}
.bar-fill {display:block; height:100%; border-radius:999px;}
.table-shell {border-radius:18px; overflow:hidden; border:1px solid var(--line); background:#fff; box-shadow:var(--shadow); margin:28px 0;}
.table-title {background:var(--g900); color:#fff8cf; padding:14px 16px; font-weight:950; letter-spacing:.08em; text-transform:uppercase; display:flex; justify-content:space-between; align-items:center;}
table.op-table {border-collapse:collapse; width:100%; font-size:.88rem;}
table.op-table th {background:#eef2e6; color:var(--ink); text-align:left; padding:13px 12px; border-bottom:1px solid var(--line);}
table.op-table td {padding:13px 12px; border-bottom:1px solid rgba(20,83,45,.10); color:var(--ink); vertical-align:middle;}
table.op-table tr:nth-child(even) td {background:#fafbf5;}
.rank-cell, .name-cell {font-weight:900; color:#05200f;}
.progress-cell {display:flex; align-items:center; gap:10px; min-width:170px;}
.progress-cell b {min-width:38px;}

.twin-shell {background:linear-gradient(180deg,#07170e,#031008); border:1px solid rgba(255,248,207,.14); border-radius:22px; padding:18px; box-shadow:0 28px 70px rgba(16,32,21,.22);}
.twin-title {display:flex; align-items:center; justify-content:space-between; color:#fff8cf; margin-bottom:12px;}
.twin-title h3 {margin:0; color:#fff8cf !important; font-size:1.25rem; letter-spacing:.08em; text-transform:uppercase;}
.legend-dot {display:inline-block; width:11px; height:11px; border-radius:99px; margin-right:7px; vertical-align:middle;}
.svg-note {color:#b8c9aa; font-size:.78rem; margin-top:10px;}

.streamlit-expanderHeader {font-weight:900 !important;}
@media(max-width:900px){.block-container{padding-left:1rem!important; padding-right:1rem!important}.main-header{flex-direction:column; align-items:flex-start}.metric-card{min-height:110px}}

/* Force navigation buttons to be wide, readable and visibly active */
.stButton > button {min-height:54px !important; font-size:1rem !important; letter-spacing:.02em !important;}
[data-testid="stBaseButton-primary"] {background:linear-gradient(135deg,var(--g900),var(--g700)) !important; color:#fff8cf !important; border-color:var(--g700) !important; box-shadow:0 13px 30px rgba(20,83,45,.23) !important;}
[data-testid="stBaseButton-secondary"] {background:#fff !important; color:var(--g800) !important; border-color:rgba(20,83,45,.30) !important;}

</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

STATUS_ORDER = ["Pronto", "Atenção", "Risco"]
ROLE_LABELS = {
    "admin": "Administrador",
    "company_commander": "Comandante de Companhia",
    "platoon_commander": "Comandante de Pelotão",
    "section_commander": "Comandante de Secção",
    "soldier": "Militar",
}
MUSCLE_LABELS = {
    "chest": "Peito", "back": "Costas", "shoulders": "Ombros", "arms": "Braços",
    "core": "Core", "glutes": "Glúteos", "quads": "Quadríceps", "hamstrings": "Posteriores", "calves": "Gémeos",
}

# High-quality anatomical digital twin base images (embedded WebP, grayscale).
# The app overlays dynamic coloured zones on top according to each soldier's muscle loads.
MALE_TWIN_BASE_WEBP = """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"""
FEMALE_TWIN_BASE_WEBP = """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"""

# =========================================================
# Supabase helpers
# =========================================================
@st.cache_resource(show_spinner=False)
def base_client() -> Client:
    try:
        url = st.secrets["supabase"]["url"]
        key = st.secrets["supabase"]["anon_key"]
    except Exception:
        st.error("Faltam os secrets do Supabase na Streamlit Cloud.")
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


def sb_select(table: str, columns: str = "*", order: Optional[str] = None, desc: bool = False, filters: Optional[List[Tuple[str, str, Any]]] = None, limit: Optional[int] = None) -> List[Dict[str, Any]]:
    query = client_with_session().table(table).select(columns)
    if filters:
        for col, op, value in filters:
            if value is None:
                continue
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
    if limit:
        query = query.limit(limit)
    return query.execute().data or []


def sb_insert_many(table: str, payloads: List[Dict[str, Any]]) -> None:
    if payloads:
        client_with_session().table(table).insert(payloads).execute()

# =========================================================
# Auth
# =========================================================
def logout() -> None:
    try:
        client_with_session().auth.sign_out()
    except Exception:
        pass
    try:
        st.query_params.clear()
    except Exception:
        pass
    for k in ["access_token", "refresh_token", "profile", "user_email", "page", "mode", "nav_radio", "mode_radio"]:
        st.session_state.pop(k, None)
    st.rerun()


def login_page() -> None:
    st.markdown(
        """
        <div class="login-shell">
          <div class="login-hero">
            <div class="login-top">
              <div class="login-brand">
                <div class="login-logo">🛡️</div>
                <div>
                  <h1 class="login-title">Military Digital Twin</h1>
                  <p class="login-subtitle">Plataforma de monitorização, prontidão e simulação de treino militar</p>
                </div>
              </div>
              <div class="login-badge">● Sistema ativo</div>
            </div>
          </div>
        </div>
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
            if not response.session or not response.user:
                st.error("Login inválido.")
                st.stop()
            st.session_state["access_token"] = response.session.access_token
            st.session_state["refresh_token"] = response.session.refresh_token
            st.session_state["user_email"] = response.user.email
            auth_client = client_with_session()
            # Nova BD: profiles.auth_user_id liga ao Supabase Auth user id.
            prof = auth_client.table("profiles").select("*").eq("auth_user_id", response.user.id).maybe_single().execute().data
            if not prof:
                prof = auth_client.table("profiles").select("*").eq("email", response.user.email).maybe_single().execute().data
            if not prof:
                st.error("Login feito, mas este utilizador ainda não está associado a um perfil da aplicação.")
                st.stop()
            st.session_state["profile"] = prof
            st.session_state["page"] = "Dashboard" if prof.get("app_role") != "soldier" else "Militar"
            st.rerun()
        except Exception as exc:
            st.error("Não foi possível iniciar sessão. Confirma email, password e associação Auth → profiles.")
            st.caption(str(exc))
    st.markdown(
        """
        <div class="login-demo">
            <b>Credenciais principais de teste</b><br>
            Companhia: <code>cap.teixeira@militarytwin.pt</code> / <code>Cmd2026!</code><br>
            1.º Pelotão: <code>hugo.dias@militarytwin.pt</code> / <code>Ten2026!</code><br>
            2.º Pelotão: <code>miguel.santos@militarytwin.pt</code> / <code>Ten2026!</code><br>
            Secção: <code>ines.vicente@militarytwin.pt</code> / <code>Sarg2026!</code><br>
            Militar: <code>rafael.costa@militarytwin.pt</code> / <code>Mil2026!</code>
        </div>
        <div class="login-foot">Protótipo com Supabase Auth + PostgreSQL + Streamlit</div>
        """,
        unsafe_allow_html=True,
    )


def require_login() -> Dict[str, Any]:
    profile = st.session_state.get("profile")
    if not profile:
        login_page()
        st.stop()
    return profile

# =========================================================
# General helpers
# =========================================================
def safe(v: Any, default: str = "—") -> str:
    if v is None:
        return default
    if isinstance(v, float) and math.isnan(v):
        return default
    return str(v)


def n(v: Any, default: int = 0) -> int:
    try:
        if v is None or (isinstance(v, float) and math.isnan(v)):
            return default
        return int(round(float(v)))
    except Exception:
        return default


def pct(v: Any) -> str:
    return f"{n(v)}%"


def status_class(status: str) -> str:
    return {"Pronto": "pill-pronto", "Atenção": "pill-atencao", "Risco": "pill-risco"}.get(status, "pill-muted")


def color_for_status(status: str) -> str:
    return {"Pronto": "#22c55e", "Atenção": "#f59e0b", "Risco": "#ef4444"}.get(status, "#64748b")


def color_for_value(v: Any, inverse: bool = False) -> str:
    value = n(v)
    if inverse:
        if value < 35: return "#22c55e"
        if value < 55: return "#d7b92f"
        if value < 75: return "#f59e0b"
        return "#ef4444"
    if value >= 75: return "#22c55e"
    if value >= 55: return "#d7b92f"
    if value >= 40: return "#f59e0b"
    return "#ef4444"


def color_for_load(v: Any) -> str:
    value = n(v)
    if value < 45: return "#22c55e"
    if value < 60: return "#d7b92f"
    if value < 75: return "#f59e0b"
    return "#ef4444"


def load_label(v: Any) -> str:
    value = n(v)
    if value < 45: return "Controlado"
    if value < 60: return "Atenção"
    if value < 75: return "Elevado"
    return "Crítico"


def progress_html(value: Any, inverse: bool = False, label: Optional[str] = None) -> str:
    value_i = max(0, min(100, n(value)))
    color = color_for_value(value_i, inverse=inverse)
    txt = label if label is not None else f"{value_i}%"
    return f'<div class="progress-cell"><b>{html.escape(txt)}</b><div class="bar-wrap"><span class="bar-fill" style="width:{value_i}%; background:{color};"></span></div></div>'


def load_progress_html(value: Any) -> str:
    value_i = max(0, min(100, n(value)))
    color = color_for_load(value_i)
    return f'<div class="progress-cell"><b>{value_i}%</b><div class="bar-wrap"><span class="bar-fill" style="width:{value_i}%; background:{color};"></span></div></div>'


def metric_card(label: str, value: Any, caption: str = "") -> None:
    st.markdown(f"""
    <div class="metric-card">
      <small>{html.escape(label)}</small>
      <h2>{html.escape(str(value))}</h2>
      <p>{html.escape(caption)}</p>
    </div>
    """, unsafe_allow_html=True)


def info_row(label: str, value: Any) -> str:
    return f'<div class="info-row"><span>{html.escape(label)}</span><b>{html.escape(str(value))}</b></div>'


def apply_chart_style(fig: go.Figure, height: int = 420) -> go.Figure:
    fig.update_layout(
        height=height,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="#ffffff",
        font=dict(family="Inter, Arial", color="#213322"),
        margin=dict(l=30, r=25, t=48, b=38),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, bgcolor="rgba(255,255,255,.75)"),
    )
    fig.update_xaxes(gridcolor="rgba(20,83,45,.10)", zerolinecolor="rgba(20,83,45,.16)")
    fig.update_yaxes(gridcolor="rgba(20,83,45,.10)", zerolinecolor="rgba(20,83,45,.16)")
    return fig

# =========================================================
# Data layer for new hierarchy schema
# =========================================================
def profile_role(profile: Dict[str, Any]) -> str:
    return str(profile.get("app_role") or profile.get("role") or "soldier")


def profile_display(profile: Dict[str, Any]) -> str:
    return str(profile.get("display_name") or profile.get("email") or "Utilizador")


def is_command_role(profile: Dict[str, Any]) -> bool:
    return profile_role(profile) in {"company_commander", "platoon_commander", "section_commander", "admin"}


def current_mode(profile: Dict[str, Any]) -> str:
    if not is_command_role(profile):
        return "individual"
    mode = st.session_state.get("mode", "command")
    return mode if mode in {"command", "individual"} else "command"


def get_assignments(profile: Dict[str, Any]) -> pd.DataFrame:
    try:
        data = sb_select("command_assignments", filters=[("profile_id", "eq", profile.get("id"))])
        return pd.DataFrame(data)
    except Exception:
        return pd.DataFrame()


def get_org_units() -> pd.DataFrame:
    try:
        return pd.DataFrame(sb_select("org_units", order="sort_order"))
    except Exception:
        return pd.DataFrame()


def command_scope_label(profile: Dict[str, Any]) -> str:
    role = profile_role(profile)
    if role == "company_commander":
        return "Companhia"
    if role == "platoon_commander":
        return "Pelotão"
    if role == "section_commander":
        return "Secção"
    return "Individual"


def accessible_snapshot(exclude_own: bool = False, profile: Optional[Dict[str, Any]] = None) -> pd.DataFrame:
    """Reads current accessible force snapshot. RLS should restrict by logged-in user.

    In command mode, exclude the logged-in commander's own soldier row so that
    command dashboards/lists represent the force under command, while the
    commander's individual data stays in Meu perfil/Digital Twin.
    """
    try:
        df = pd.DataFrame(sb_select("company_dashboard_current", order="full_name"))
    except Exception as exc:
        st.error("Não foi possível ler a vista company_dashboard_current.")
        st.caption(str(exc))
        return pd.DataFrame()
    if df.empty:
        return df
    if exclude_own and profile and profile.get("soldier_id") and "soldier_id" in df.columns:
        df = df[df["soldier_id"].astype(str) != str(profile.get("soldier_id"))].copy()
    for col in ["readiness_score", "injury_risk", "recovery_score", "sleep_hours", "fatigue_score", "soreness_score", "cooper_m", "pushups", "situps", "pullups", "plank_sec"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    if "readiness_status" not in df.columns and "status" in df.columns:
        df["readiness_status"] = df["status"]
    df["readiness_status"] = df.get("readiness_status", "Atenção").fillna("Atenção")
    return df


def get_profile_soldier(profile: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    sid = profile.get("soldier_id")
    if not sid:
        return None
    rows = sb_select("company_dashboard_current", filters=[("soldier_id", "eq", sid)], limit=1)
    return rows[0] if rows else None


def get_soldier_row(soldier_id: str) -> Optional[Dict[str, Any]]:
    rows = sb_select("company_dashboard_current", filters=[("soldier_id", "eq", soldier_id)], limit=1)
    return rows[0] if rows else None


def get_latest_recommendations(soldier_id: str, limit: int = 5) -> pd.DataFrame:
    try:
        return pd.DataFrame(sb_select("recommendations", order="rec_date", desc=True, filters=[("soldier_id", "eq", soldier_id)], limit=limit))
    except Exception:
        return pd.DataFrame()


def get_recent_training(soldier_id: str, limit: int = 8) -> pd.DataFrame:
    try:
        return pd.DataFrame(sb_select("training_sessions", order="session_date", desc=True, filters=[("soldier_id", "eq", soldier_id)], limit=limit))
    except Exception:
        return pd.DataFrame()


def get_muscle_loads(soldier_id: str) -> Dict[str, int]:
    loads: Dict[str, int] = {}
    try:
        rows = sb_select("latest_muscle_group_loads", filters=[("soldier_id", "eq", soldier_id)])
        for r in rows:
            loads[str(r.get("muscle_group_code"))] = n(r.get("load_value"))
    except Exception:
        rows = []
    if not loads:
        # Legacy fallback if needed.
        try:
            legacy = sb_select("muscle_loads", order="load_date", desc=True, filters=[("soldier_id", "eq", soldier_id)], limit=1)
            if legacy:
                l = legacy[0]
                loads = {
                    "chest": n(l.get("chest"), 40), "back": n(l.get("back"), 45), "shoulders": n(l.get("shoulders"), 45),
                    "arms": n(l.get("arms"), 40), "core": n(l.get("core"), 50), "quads": n(l.get("legs"), 55),
                    "hamstrings": max(0, min(100, n(l.get("legs"), 55) + 3)), "glutes": max(0, min(100, n(l.get("legs"), 55) - 4)), "calves": n(l.get("calves"), 45),
                }
        except Exception:
            pass
    defaults = {"chest": 40, "back": 45, "shoulders": 46, "arms": 38, "core": 55, "glutes": 48, "quads": 62, "hamstrings": 58, "calves": 48}
    defaults.update({k: int(v) for k, v in loads.items() if k in MUSCLE_LABELS})
    return defaults



# =========================================================
# Hierarchy labels and ordering
# =========================================================
def _first_number(value: Any, default: int = 99) -> int:
    import re
    m = re.search(r"\d+", safe(value, ""))
    return int(m.group(0)) if m else default


def enrich_hierarchy_columns(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df
    out = df.copy()
    if "platoon_name" not in out.columns:
        out["platoon_name"] = ""
    if "section_name" not in out.columns:
        out["section_name"] = ""
    out["platoon_order"] = out["platoon_name"].apply(lambda x: _first_number(x, 99))
    out["section_order"] = out["section_name"].apply(lambda x: _first_number(x, 0 if safe(x, "") in {"", "—"} else 99))
    out["section_full_label"] = out.apply(
        lambda r: f"{safe(r.get('platoon_name'))} · {safe(r.get('section_name'))}" if safe(r.get('section_name'), '') not in {'', '—'} else safe(r.get('platoon_name')),
        axis=1,
    )
    out["rank_order"] = out.get("rank_code", pd.Series([""] * len(out))).map({"CAP": 0, "TEN": 1, "1SARG": 2, "2SARG": 3, "FUR": 4, "1CAB": 5, "2CAB": 6, "SOLD": 7}).fillna(99).astype(int)
    out["commander_sort"] = out.get("is_commander", pd.Series([False] * len(out))).apply(lambda x: 0 if bool(x) else 1)
    # Tenentes comandantes ficam antes das secções; comandantes de secção ficam antes dos respetivos militares.
    out.loc[out.get("rank_code", "") == "TEN", "section_order"] = -1
    return out


def sort_operational(df: pd.DataFrame) -> pd.DataFrame:
    out = enrich_hierarchy_columns(df)
    if out.empty:
        return out
    sort_cols = [c for c in ["platoon_order", "section_order", "commander_sort", "rank_order", "full_name"] if c in out.columns]
    return out.sort_values(sort_cols, ascending=True).copy()


def section_options_for(df: pd.DataFrame, selected_platoon: str) -> List[str]:
    dff = df.copy()
    if selected_platoon != "Todos" and "platoon_name" in dff:
        dff = dff[dff["platoon_name"] == selected_platoon]
    dff = enrich_hierarchy_columns(dff)
    if selected_platoon == "Todos":
        vals = [x for x in dff.get("section_full_label", pd.Series(dtype=str)).dropna().unique().tolist() if x and x != "—"]
    else:
        vals = [x for x in dff.get("section_name", pd.Series(dtype=str)).dropna().unique().tolist() if x and x != "—"]
    return ["Todas"] + sorted(vals, key=lambda x: (_first_number(x, 99), x))


def apply_section_filter(df: pd.DataFrame, selected_platoon: str, selected_section: str) -> pd.DataFrame:
    out = enrich_hierarchy_columns(df)
    if selected_platoon != "Todos" and "platoon_name" in out:
        out = out[out["platoon_name"] == selected_platoon]
    if selected_section != "Todas":
        if selected_platoon == "Todos":
            out = out[out["section_full_label"] == selected_section]
        else:
            out = out[out["section_name"] == selected_section]
    return out

# =========================================================
# Top bar and navigation
# =========================================================
def context_title(profile: Dict[str, Any], mode: str, page: str) -> str:
    role = profile_role(profile)
    if mode == "command" and is_command_role(profile):
        scope = command_scope_label(profile)
        if page == "Dashboard":
            return f"Modo comandante · Dashboard — {scope}"
        if page == "Militares":
            return f"Modo comandante · Militares — {scope}"
        if page == "Simular treino":
            return f"Modo comandante · Simulador coletivo — {scope}"
        if page == "Admin":
            return "Administração"
        return f"Modo comandante · {page} — {scope}"

    soldier = get_profile_soldier(profile)
    who = profile_display(profile)
    if soldier:
        who = f"{safe(soldier.get('rank_code'))} {safe(soldier.get('full_name'))}".strip()
    if page == "Meu perfil":
        return f"Meu perfil · {who}"
    if page == "Digital Twin":
        return f"Digital Twin · {who}"
    if page == "Simular treino":
        return f"Simulador individual · {who}"
    return f"{page} · {who}"


def nav_button_grid(label: str, options: List[str], selected: str, key_prefix: str) -> str:
    """Full-width navigation buttons with visible active state."""
    st.markdown(f'<div class="nav-label">{html.escape(label)}</div>', unsafe_allow_html=True)
    if not options:
        return selected
    selected = selected if selected in options else options[0]
    chosen = selected
    cols = st.columns(len(options), gap="large")
    for i, opt in enumerate(options):
        btn_type = "primary" if opt == selected else "secondary"
        safe_key = ''.join(ch if ch.isalnum() else '_' for ch in opt.lower())
        if cols[i].button(opt, key=f"{key_prefix}_{i}_{safe_key}", use_container_width=True, type=btn_type):
            chosen = opt
    if chosen != selected:
        if key_prefix == "mode_btn":
            st.session_state["mode"] = "command" if chosen == "Modo comandante" else "individual"
            st.session_state.pop("page", None)
        else:
            st.session_state["page"] = chosen
        st.rerun()
    return chosen

def top_bar(profile: Dict[str, Any]) -> str:
    role = profile_role(profile)
    role_label = ROLE_LABELS.get(role, role)

    if is_command_role(profile):
        mode = current_mode(profile)
    else:
        mode = "individual"
        st.session_state["mode"] = "individual"

    if mode == "command" and is_command_role(profile):
        pages = ["Dashboard", "Militares", "Simular treino"]
        if role == "admin":
            pages.append("Admin")
    else:
        pages = ["Meu perfil", "Digital Twin", "Simular treino"]

    current_page = st.session_state.get("page") if st.session_state.get("page") in pages else pages[0]
    st.session_state["page"] = current_page
    active_context = context_title(profile, mode, current_page)

    st.markdown(f"""
    <div class="main-header">
      <div>
        <h1>Military Digital Twin</h1>
        <p>Sessão iniciada · {html.escape(profile_display(profile))} · {html.escape(role_label)}</p>
        <div class="header-context">{html.escape(active_context)}</div>
      </div>
      <a class="header-chip logout-link" href="?logout=1" target="_self">Terminar sessão</a>
    </div>
    """, unsafe_allow_html=True)

    if is_command_role(profile):
        selected_mode_label = "Modo comandante" if mode == "command" else "Modo individual"
        selected_mode_label = nav_button_grid("Escolher modo", ["Modo comandante", "Modo individual"], selected_mode_label, "mode_btn")
        mode = "command" if selected_mode_label == "Modo comandante" else "individual"
        st.session_state["mode"] = mode
        if mode == "command":
            pages = ["Dashboard", "Militares", "Simular treino"]
            if role == "admin":
                pages.append("Admin")
        else:
            pages = ["Meu perfil", "Digital Twin", "Simular treino"]
    else:
        st.session_state["mode"] = "individual"
        pages = ["Meu perfil", "Digital Twin", "Simular treino"]

    if st.session_state.get("page") not in pages:
        st.session_state["page"] = pages[0]
    selected = nav_button_grid("Secções disponíveis", pages, st.session_state["page"], "page_btn")
    st.session_state["page"] = selected
    return selected

# =========================================================
# Dashboard / command views
# =========================================================
def filter_snapshot(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df
    df = enrich_hierarchy_columns(df)
    st.markdown('<div class="section-title">Filtros operacionais</div>', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns([1.1, 1.1, 1.2, 1.0], gap="large")
    platoons = ["Todos"] + sorted([x for x in df.get("platoon_name", pd.Series(dtype=str)).dropna().unique().tolist() if x], key=lambda x: (_first_number(x), x))
    with c1:
        platoon = st.selectbox("Pelotão", platoons, key="dash_filter_platoon")
    with c2:
        sections = section_options_for(df, platoon)
        section = st.selectbox("Secção", sections, key="dash_filter_section")
    with c3:
        statuses = st.multiselect("Estado", STATUS_ORDER, default=STATUS_ORDER, key="dash_filter_status")
    with c4:
        min_ready = st.slider("Prontidão mínima", 0, 100, 0, key="dash_filter_ready")
    out = apply_section_filter(df, platoon, section)
    if statuses and "readiness_status" in out:
        out = out[out["readiness_status"].isin(statuses)]
    if "readiness_score" in out:
        out = out[out["readiness_score"].fillna(0) >= min_ready]
    return sort_operational(out)


def render_metrics(df: pd.DataFrame) -> None:
    total = len(df)
    ready = int((df["readiness_status"] == "Pronto").sum()) if not df.empty else 0
    attention = int((df["readiness_status"] == "Atenção").sum()) if not df.empty else 0
    risk = int((df["readiness_status"] == "Risco").sum()) if not df.empty else 0
    avg = int(round(df["readiness_score"].dropna().mean())) if not df.empty and "readiness_score" in df else 0
    c1, c2, c3, c4, c5 = st.columns(5, gap="large")
    with c1: metric_card("Militares analisados", total, command_scope_label(st.session_state["profile"]))
    with c2: metric_card("Prontos", ready, "prontidão ≥ 75")
    with c3: metric_card("Atenção", attention, "55 ≤ prontidão < 75")
    with c4: metric_card("Risco", risk, "prontidão < 55 ou risco alto")
    with c5: metric_card("Prontidão média", f"{avg}%", "média do escalão")


def render_charts(df: pd.DataFrame) -> None:
    if df.empty:
        st.info("Sem dados para visualizar neste filtro.")
        return
    left, right = st.columns([1.1, 1], gap="large")
    colors = {"Pronto": "#22c55e", "Atenção": "#f59e0b", "Risco": "#ef4444"}
    with left:
        chart_df = df.sort_values("readiness_score", ascending=True).tail(20)
        fig = px.bar(chart_df, x="readiness_score", y="full_name", orientation="h", color="readiness_status", color_discrete_map=colors, labels={"readiness_score":"Prontidão", "full_name":"Militar", "readiness_status":"Estado"}, title="Prontidão por militar")
        st.plotly_chart(apply_chart_style(fig, 440), use_container_width=True)
    with right:
        fig = px.scatter(df, x="readiness_score", y="injury_risk", size="recovery_score", color="readiness_status", color_discrete_map=colors, hover_name="full_name", labels={"readiness_score":"Prontidão", "injury_risk":"Risco de lesão", "readiness_status":"Estado"}, title="Prontidão vs risco")
        st.plotly_chart(apply_chart_style(fig, 440), use_container_width=True)

    df_group = enrich_hierarchy_columns(df)
    group_col = "section_full_label" if "section_full_label" in df_group and df_group["section_full_label"].notna().any() else "platoon_name"
    if group_col in df_group:
        g = df_group.groupby([group_col, "readiness_status"]).size().reset_index(name="militares")
        fig = px.bar(g, x=group_col, y="militares", color="readiness_status", color_discrete_map=colors, title="Estado por subunidade", labels={group_col:"Subunidade", "militares":"Militares", "readiness_status":"Estado"})
        st.plotly_chart(apply_chart_style(fig, 380), use_container_width=True)


def operational_table(df: pd.DataFrame, title: str = "Tabela operacional") -> None:
    if df.empty:
        st.info("Sem militares para mostrar neste filtro.")
        return
    rows = []
    cols = ["rank_code", "full_name", "platoon_name", "section_name", "readiness_status", "readiness_score", "injury_risk", "recovery_score", "cooper_m", "fatigue_score", "sleep_hours", "is_commander", "military_number"]
    view = sort_operational(df[[c for c in cols if c in df.columns]].copy())
    for _, r in view.iterrows():
        status = safe(r.get("readiness_status"), "Atenção")
        rows.append(f"""
<tr>
  <td class="rank-cell">{html.escape(safe(r.get('rank_code')))}</td>
  <td class="name-cell">{html.escape(safe(r.get('full_name')))}</td>
  <td>{html.escape(safe(r.get('platoon_name')))}</td>
  <td>{html.escape(safe(r.get('section_name')))}</td>
  <td><span class="status-pill {status_class(status)}">{html.escape(status)}</span></td>
  <td>{progress_html(r.get('readiness_score'))}</td>
  <td>{progress_html(r.get('injury_risk'), inverse=True)}</td>
  <td>{progress_html(r.get('recovery_score'))}</td>
  <td>{html.escape(safe(r.get('cooper_m')))} m</td>
  <td>{progress_html(r.get('fatigue_score'), inverse=True, label=f"{n(r.get('fatigue_score'))}/10")}</td>
  <td>{html.escape(safe(r.get('sleep_hours')))} h</td>
</tr>""")
    table_html = f"""<div class="table-shell">
<div class="table-title"><span>{html.escape(title)}</span><span>{len(view)} militar(es)</span></div>
<table class="op-table">
<thead><tr><th>Posto</th><th>Militar</th><th>Pelotão</th><th>Secção</th><th>Estado</th><th>Prontidão</th><th>Risco</th><th>Recuperação</th><th>Cooper</th><th>Fadiga</th><th>Sono</th></tr></thead>
<tbody>{''.join(rows)}</tbody>
</table>
</div>"""
    st.markdown(table_html, unsafe_allow_html=True)


def commander_dashboard(profile: Dict[str, Any]) -> None:
    scope = command_scope_label(profile)
    df = accessible_snapshot(exclude_own=True, profile=profile)
    df = filter_snapshot(df)
    render_metrics(df)
    st.divider()
    render_charts(df)
    operational_table(df, "Tabela operacional")

# =========================================================
# Soldier summary pages
# =========================================================
def render_individual_landing(soldier: Dict[str, Any], title: str = "Meu estado") -> None:
    if not soldier:
        st.warning("Perfil individual não encontrado para este utilizador.")
        return
    c1, c2, c3, c4 = st.columns(4, gap="large")
    status = safe(soldier.get("readiness_status"), "Atenção")
    with c1: metric_card("Prontidão", pct(soldier.get("readiness_score")), status)
    with c2: metric_card("Risco operacional", "Baixo" if n(soldier.get("injury_risk")) < 35 else "Moderado" if n(soldier.get("injury_risk")) < 60 else "Elevado", f"{pct(soldier.get('injury_risk'))}")
    with c3: metric_card("Recuperação", pct(soldier.get("recovery_score")), "sono / fadiga / carga")
    with c4: metric_card("Cooper", f"{n(soldier.get('cooper_m'))} m", "último teste")
    left, right = st.columns([1.05, .95], gap="large")
    with left:
        st.markdown('<div class="info-card"><h3>Resumo rápido</h3>' +
                    info_row("Prontidão", pct(soldier.get("readiness_score"))) +
                    info_row("Risco", pct(soldier.get("injury_risk"))) +
                    info_row("Recuperação", pct(soldier.get("recovery_score"))) +
                    info_row("Fadiga reportada", f"{n(soldier.get('fatigue_score'))}/10") +
                    info_row("Sono", f"{safe(soldier.get('sleep_hours'))} h") +
                    "</div>", unsafe_allow_html=True)
    recs = get_latest_recommendations(str(soldier.get("soldier_id")))
    with right:
        if not recs.empty:
            rec = recs.iloc[0]
            title_r = f"{safe(rec.get('priority'))} · {safe(rec.get('title'))}"
            msg = safe(rec.get("message"))
        else:
            title_r = "Sem recomendações críticas"
            msg = "Mantém o plano atual e regista feedback após o treino."
        planning = "Apto para treino normal" if status == "Pronto" else "Apto com controlo de carga" if status == "Atenção" else "Reduzir carga e monitorizar"
        st.markdown(f"""
        <div class="info-card"><h3>O que fazer agora</h3>
          <div class="section-card"><b>{html.escape(title_r)}</b><br>{html.escape(msg)}</div>
          <div class="section-card"><b>Estado para planeamento:</b><br>{html.escape(planning)}</div>
          <div class="section-card"><b>Próximo passo:</b><br>Usa o Digital Twin para ver carga muscular ou Simular treino para testar uma sessão.</div>
        </div>
        """, unsafe_allow_html=True)


def soldiers_page(profile: Dict[str, Any]) -> None:
    df = accessible_snapshot(exclude_own=True, profile=profile)
    if df.empty:
        st.info("Sem militares acessíveis.")
        return
    df = enrich_hierarchy_columns(df)
    st.markdown('<div class="section-title">Militares acessíveis</div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 1, 2], gap="large")
    with c1:
        platoons = ["Todos"] + sorted([x for x in df.get("platoon_name", pd.Series(dtype=str)).dropna().unique().tolist() if x], key=lambda x: (_first_number(x), x))
        platoon = st.selectbox("Filtrar pelotão", platoons, key="soldier_filter_platoon")
    with c2:
        sections = section_options_for(df, platoon)
        section = st.selectbox("Filtrar secção", sections, key="soldier_filter_section")
    dff = sort_operational(apply_section_filter(df, platoon, section))
    with c3:
        choices = [f"{r.rank_code} {r.full_name}" for r in dff.itertuples()]
        selected = st.selectbox("Selecionar militar", choices, key="soldier_selected") if choices else None
    row = dff.iloc[choices.index(selected)].to_dict() if selected and choices else None
    if row:
        render_commander_authorized_summary(row)
    operational_table(dff, "Militares filtrados")


def render_commander_authorized_summary(soldier: Dict[str, Any]) -> None:
    st.markdown(f'<div class="section-title">{html.escape(safe(soldier.get("rank_code")))} {html.escape(safe(soldier.get("full_name")))}</div>', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4, gap="large")
    risk = n(soldier.get("injury_risk"))
    readiness = n(soldier.get("readiness_score"))
    recovery = n(soldier.get("recovery_score"))
    status = safe(soldier.get("readiness_status"), "Atenção")
    with c1: metric_card("Prontidão", f"{readiness}%", status)
    with c2: metric_card("Risco operacional", "Baixo" if risk < 35 else "Moderado" if risk < 60 else "Elevado", f"{risk}%")
    with c3: metric_card("Disponibilidade", "Apto" if status == "Pronto" else "Condicionado" if status == "Atenção" else "Não recomendado", "para planeamento")
    with c4: metric_card("Cooper", f"{n(soldier.get('cooper_m'))} m", "último teste")
    left, right = st.columns([1, 1], gap="large")
    with left:
        st.markdown('<div class="info-card"><h3>Resumo operacional autorizado</h3>' +
                    info_row("Pelotão", safe(soldier.get("platoon_name"))) +
                    info_row("Secção", safe(soldier.get("section_name"))) +
                    info_row("Prontidão", f"{readiness}%") +
                    info_row("Risco", f"{risk}%") +
                    info_row("Recuperação", f"{recovery}%") +
                    info_row("Sono", f"{safe(soldier.get('sleep_hours'))} h") +
                    "</div>", unsafe_allow_html=True)
    with right:
        if status == "Pronto":
            action = "Pode integrar treino planeado; manter recolha de feedback pós-treino."
        elif status == "Atenção":
            action = "Integrar com controlo de volume; evitar estímulos intensos consecutivos."
        else:
            action = "Reduzir carga; priorizar recuperação e reavaliar antes de treino intenso."
        st.markdown(f'<div class="info-card"><h3>Decisão para planeamento</h3>{info_row("Estado", status)}{info_row("Ação recomendada", action)}</div>', unsafe_allow_html=True)

# =========================================================
# Dynamic SVG Digital Twin
# =========================================================
def svg_style_fill(loads: Dict[str, int], key: str, opacity: float = .86) -> str:
    return f'fill="{color_for_load(loads.get(key, 0))}" fill-opacity="{opacity}" stroke="#dbe9cf" stroke-opacity=".55" stroke-width="1.2"'


def twin_svg(loads: Dict[str, int], sex: str) -> str:
    """Dynamic anatomical SVG twin.

    One male base and one female base. Each muscle zone is a separate SVG
    shape and its colour is calculated from the current soldier's muscle load.
    """
    female = str(sex).upper().startswith("F")
    title = "Silhueta feminina" if female else "Silhueta masculina"

    def z(key: str, op: float = .86) -> str:
        return f'fill="{color_for_load(loads.get(key, 0))}" fill-opacity="{op}" stroke="#f1f8e8" stroke-opacity=".46" stroke-width="1.25" filter="url(#zoneGlow)"'

    if female:
        shoulder = 74; waist = 34; hip = 58; head_rx = 22; head_ry = 29
        label_symbol = "♀"
    else:
        shoulder = 88; waist = 42; hip = 48; head_rx = 24; head_ry = 30
        label_symbol = "♂"

    def anatomical_base(cx: int, back: bool = False) -> str:
        extra_hair = ''
        if female:
            extra_hair = '<circle cx="0" cy="13" r="12" fill="#101813" stroke="#dbe9cf" stroke-opacity=".18"/>'
        return f'''
        <g transform="translate({cx},52)">
          {extra_hair}
          <ellipse cx="0" cy="45" rx="{head_rx}" ry="{head_ry}" fill="#121a15" stroke="#dbe9cf" stroke-opacity=".32" stroke-width="1.2"/>
          <path d="M-16 73 Q0 86 16 73 L23 103 Q0 115 -23 103Z" fill="#121a15" stroke="#dbe9cf" stroke-opacity=".22"/>
          <path d="M-{shoulder} 112 C-{shoulder-18} 94 -38 94 -20 101 C-10 106 10 106 20 101 C38 94 {shoulder-18} 94 {shoulder} 112 C78 150 68 200 {waist} 204 C{waist-2} 238 {hip} 264 {hip} 286 C25 300 12 307 0 307 C-12 307 -25 300 -{hip} 286 C-{hip} 264 -{waist-2} 238 -{waist} 204 C-68 200 -78 150 -{shoulder} 112Z" fill="#172019" stroke="#dbe9cf" stroke-opacity=".25" stroke-width="1.2"/>
          <path d="M-{shoulder+6} 126 C-{shoulder+34} 150 -{shoulder+41} 197 -{shoulder+34} 254 C-{shoulder+31} 285 -{shoulder+20} 323 -{shoulder+8} 331 C-{shoulder-3} 333 -{shoulder-18} 333 -{shoulder-24} 323 C-{shoulder-32} 292 -{shoulder-28} 231 -{shoulder-22} 184 C-{shoulder-19} 154 -{shoulder-13} 134 -{shoulder+6} 126Z" fill="#121a15" stroke="#dbe9cf" stroke-opacity=".20"/>
          <path d="M{shoulder+6} 126 C{shoulder+34} 150 {shoulder+41} 197 {shoulder+34} 254 C{shoulder+31} 285 {shoulder+20} 323 {shoulder+8} 331 C{shoulder-3} 333 {shoulder-18} 333 {shoulder-24} 323 C{shoulder-32} 292 {shoulder-28} 231 {shoulder-22} 184 C{shoulder-19} 154 {shoulder-13} 134 {shoulder+6} 126Z" fill="#121a15" stroke="#dbe9cf" stroke-opacity=".20"/>
          <path d="M-{hip-6} 304 C-{hip-18} 342 -{hip-8} 383 -31 420 C-21 432 -8 427 -7 414 C-10 366 -5 333 0 310 C5 333 10 366 7 414 C8 427 21 432 31 420 C{hip+8} 383 {hip+18} 342 {hip-6} 304 C18 319 -18 319 -{hip-6} 304Z" fill="#121a15" stroke="#dbe9cf" stroke-opacity=".22"/>
          <path d="M-29 422 C-18 436 -17 501 -21 541 L-45 541 C-52 494 -48 445 -38 425 C-36 418 -31 418 -29 422Z" fill="#121a15" stroke="#dbe9cf" stroke-opacity=".20"/>
          <path d="M29 422 C18 436 17 501 21 541 L45 541 C52 494 48 445 38 425 C36 418 31 418 29 422Z" fill="#121a15" stroke="#dbe9cf" stroke-opacity=".20"/>
        </g>'''

    def front_zones(cx: int) -> str:
        shoulders = z("shoulders", .84); arms = z("arms", .82); chest = z("chest", .82); core = z("core", .82); quads = z("quads", .86); calves = z("calves", .82)
        if female:
            chest_path_l = 'M-48 122 C-34 105 -12 109 -4 129 C-15 145 -34 153 -54 146 C-58 136 -56 128 -48 122Z'
            chest_path_r = 'M48 122 C34 105 12 109 4 129 C15 145 34 153 54 146 C58 136 56 128 48 122Z'
            core_path = 'M-25 154 C-12 145 12 145 25 154 C29 196 24 243 0 263 C-24 243 -29 196 -25 154Z'
        else:
            chest_path_l = 'M-57 119 C-38 98 -7 104 -2 134 C-18 154 -42 164 -61 148 C-65 136 -64 126 -57 119Z'
            chest_path_r = 'M57 119 C38 98 7 104 2 134 C18 154 42 164 61 148 C65 136 64 126 57 119Z'
            core_path = 'M-30 156 C-13 145 13 145 30 156 C34 198 28 249 0 271 C-28 249 -34 198 -30 156Z'
        return f'''
        <g transform="translate({cx},52)">
          <path d="M-{shoulder+2} 118 C-{shoulder-10} 95 -44 92 -26 108 C-34 134 -55 155 -{shoulder-8} 154 C-{shoulder+7} 145 -{shoulder+10} 130 -{shoulder+2} 118Z" {shoulders}/>
          <path d="M{shoulder+2} 118 C{shoulder-10} 95 44 92 26 108 C34 134 55 155 {shoulder-8} 154 C{shoulder+7} 145 {shoulder+10} 130 {shoulder+2} 118Z" {shoulders}/>
          <path d="M-{shoulder-8} 154 C-{shoulder+24} 174 -{shoulder+23} 244 -{shoulder+14} 310 C-{shoulder+6} 324 -{shoulder-10} 323 -{shoulder-18} 307 C-{shoulder-22} 253 -{shoulder-19} 194 -{shoulder-8} 154Z" {arms}/>
          <path d="M{shoulder-8} 154 C{shoulder+24} 174 {shoulder+23} 244 {shoulder+14} 310 C{shoulder+6} 324 {shoulder-10} 323 {shoulder-18} 307 C{shoulder-22} 253 {shoulder-19} 194 {shoulder-8} 154Z" {arms}/>
          <path d="{chest_path_l}" {chest}/>
          <path d="{chest_path_r}" {chest}/>
          <path d="{core_path}" {core}/>
          <path d="M-1 156 L-1 266" stroke="#08140d" stroke-opacity=".38" stroke-width="2"/>
          <path d="M-21 186 L21 186 M-22 218 L22 218 M-17 246 L17 246" stroke="#08140d" stroke-opacity=".28" stroke-width="1.2"/>
          <path d="M-{hip-3} 301 C-20 315 -15 376 -28 421 C-39 431 -55 424 -57 410 C-58 364 -54 322 -{hip-3} 301Z" {quads}/>
          <path d="M{hip-3} 301 C20 315 15 376 28 421 C39 431 55 424 57 410 C58 364 54 322 {hip-3} 301Z" {quads}/>
          <path d="M-32 428 C-22 441 -21 503 -24 535 L-45 535 C-51 490 -48 449 -39 430 C-36 424 -34 424 -32 428Z" {calves}/>
          <path d="M32 428 C22 441 21 503 24 535 L45 535 C51 490 48 449 39 430 C36 424 34 424 32 428Z" {calves}/>
        </g>'''

    def back_zones(cx: int) -> str:
        shoulders = z("shoulders", .84); arms = z("arms", .82); back = z("back", .84); glutes = z("glutes", .86); hams = z("hamstrings", .86); calves = z("calves", .82)
        return f'''
        <g transform="translate({cx},52)">
          <path d="M-{shoulder+2} 118 C-{shoulder-9} 95 -44 92 -26 108 C-34 136 -57 158 -{shoulder-8} 156 C-{shoulder+7} 146 -{shoulder+10} 130 -{shoulder+2} 118Z" {shoulders}/>
          <path d="M{shoulder+2} 118 C{shoulder-9} 95 44 92 26 108 C34 136 57 158 {shoulder-8} 156 C{shoulder+7} 146 {shoulder+10} 130 {shoulder+2} 118Z" {shoulders}/>
          <path d="M-{shoulder-8} 154 C-{shoulder+24} 174 -{shoulder+23} 244 -{shoulder+14} 310 C-{shoulder+6} 324 -{shoulder-10} 323 -{shoulder-18} 307 C-{shoulder-22} 253 -{shoulder-19} 194 -{shoulder-8} 154Z" {arms}/>
          <path d="M{shoulder-8} 154 C{shoulder+24} 174 {shoulder+23} 244 {shoulder+14} 310 C{shoulder+6} 324 {shoulder-10} 323 {shoulder-18} 307 C{shoulder-22} 253 {shoulder-19} 194 {shoulder-8} 154Z" {arms}/>
          <path d="M-54 120 C-27 102 -7 118 0 144 L0 262 C-32 242 -50 199 -58 156 C-61 140 -60 128 -54 120Z" {back}/>
          <path d="M54 120 C27 102 7 118 0 144 L0 262 C32 242 50 199 58 156 C61 140 60 128 54 120Z" {back}/>
          <path d="M0 112 L0 274" stroke="#f1f8e8" stroke-opacity=".24" stroke-width="1.8"/>
          <path d="M-{hip-4} 274 C-21 250 -2 258 -1 300 C-17 324 -48 316 -55 294 C-56 284 -51 277 -{hip-4} 274Z" {glutes}/>
          <path d="M{hip-4} 274 C21 250 2 258 1 300 C17 324 48 316 55 294 C56 284 51 277 {hip-4} 274Z" {glutes}/>
          <path d="M-{hip-2} 318 C-20 330 -17 382 -31 421 C-43 431 -58 422 -57 405 C-54 362 -51 333 -{hip-2} 318Z" {hams}/>
          <path d="M{hip-2} 318 C20 330 17 382 31 421 C43 431 58 422 57 405 C54 362 51 333 {hip-2} 318Z" {hams}/>
          <path d="M-32 428 C-22 441 -21 503 -24 535 L-45 535 C-51 490 -48 449 -39 430 C-36 424 -34 424 -32 428Z" {calves}/>
          <path d="M32 428 C22 441 21 503 24 535 L45 535 C51 490 48 449 39 430 C36 424 34 424 32 428Z" {calves}/>
        </g>'''

    return f'''
    <svg viewBox="0 0 960 670" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Digital twin muscular dinâmico">
      <defs>
        <radialGradient id="bgTwin" cx="50%" cy="23%" r="86%"><stop offset="0%" stop-color="#16351f"/><stop offset="100%" stop-color="#031008"/></radialGradient>
        <filter id="zoneGlow"><feDropShadow dx="0" dy="0" stdDeviation="4" flood-color="#fff8cf" flood-opacity=".10"/></filter>
        <filter id="bodyShadow"><feDropShadow dx="0" dy="18" stdDeviation="14" flood-color="#000" flood-opacity=".36"/></filter>
        <pattern id="grid" width="28" height="28" patternUnits="userSpaceOnUse"><path d="M28 0 L0 0 0 28" fill="none" stroke="#dbe9cf" stroke-opacity=".045" stroke-width="1"/></pattern>
      </defs>
      <rect width="960" height="670" rx="26" fill="url(#bgTwin)"/>
      <rect width="960" height="670" rx="26" fill="url(#grid)"/>
      <text x="36" y="50" fill="#fff8cf" font-size="25" font-weight="950" letter-spacing="5">DIGITAL TWIN</text>
      <text x="36" y="79" fill="#b8c9aa" font-size="14" font-weight="700">{html.escape(title)} {label_symbol} · grupos musculares dinâmicos</text>
      <circle cx="296" cy="342" r="222" fill="none" stroke="#dbe9cf" stroke-opacity=".07"/>
      <circle cx="674" cy="342" r="222" fill="none" stroke="#dbe9cf" stroke-opacity=".07"/>
      <g filter="url(#bodyShadow)">{anatomical_base(296, False)}{anatomical_base(674, True)}</g>
      {front_zones(296)}
      {back_zones(674)}
      <g transform="translate(118,626)">
        <circle cx="0" cy="0" r="7" fill="#22c55e"/><text x="16" y="5" fill="#dbe9cf" font-size="13">Controlado</text>
        <circle cx="140" cy="0" r="7" fill="#d7b92f"/><text x="156" y="5" fill="#dbe9cf" font-size="13">Atenção</text>
        <circle cx="270" cy="0" r="7" fill="#f59e0b"/><text x="286" y="5" fill="#dbe9cf" font-size="13">Elevado</text>
        <circle cx="386" cy="0" r="7" fill="#ef4444"/><text x="402" y="5" fill="#dbe9cf" font-size="13">Crítico</text>
      </g>
    </svg>
    '''

def twin_zone_overlays(loads: Dict[str, int], sex: str, predicted: bool = False) -> str:
    """SVG overlays aligned to the embedded 980x1224 anatomical base images.

    This avoids the old crop/percentage mismatch: the image and highlights share
    the same SVG coordinate system, so each colour stays on the intended group.
    """
    female = str(sex).upper().startswith("F")

    def val(key: str) -> int:
        return n(loads.get(key, 0))

    def fill(key: str) -> str:
        return color_for_load(val(key))

    def attrs(key: str, opacity: float = 0.54) -> str:
        label = html.escape(MUSCLE_LABELS.get(key, key))
        return f'fill="{fill(key)}" fill-opacity="{opacity}" stroke="rgba(255,248,207,.28)" stroke-width="1.2"><title>{label}: {val(key)}%</title>'

    def ellipse(key: str, cx: float, cy: float, rx: float, ry: float, rotate: float = 0, opacity: float = 0.54) -> str:
        tr = f' transform="rotate({rotate} {cx} {cy})"' if rotate else ""
        return f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}"{tr} {attrs(key, opacity)}</ellipse>'

    def poly(key: str, pts: str, opacity: float = 0.54) -> str:
        return f'<polygon points="{pts}" {attrs(key, opacity)}</polygon>'

    def path(key: str, d: str, opacity: float = 0.54) -> str:
        return f'<path d="{d}" {attrs(key, opacity)}</path>'

    zones: List[str] = []
    if female:
        # FRONT — left figure
        zones += [
            ellipse("shoulders", 184, 290, 43, 66, -14, .50),
            ellipse("shoulders", 389, 290, 43, 66, 14, .50),
            ellipse("arms", 154, 445, 30, 116, 5, .49),
            ellipse("arms", 423, 445, 30, 116, -5, .49),
            ellipse("chest", 247, 330, 58, 36, -6, .44),
            ellipse("chest", 326, 330, 58, 36, 6, .44),
            poly("core", "238,392 336,392 358,560 218,560", .48),
            ellipse("quads", 232, 704, 44, 132, 5, .56),
            ellipse("quads", 342, 704, 44, 132, -5, .56),
            ellipse("calves", 215, 932, 31, 132, -3, .50),
            ellipse("calves", 360, 932, 31, 132, 3, .50),
            # BACK — right figure
            ellipse("shoulders", 580, 282, 43, 66, -16, .46),
            ellipse("shoulders", 790, 282, 43, 66, 16, .46),
            ellipse("arms", 540, 448, 30, 116, 6, .48),
            ellipse("arms", 834, 448, 30, 116, -6, .48),
            path("back", "M616 290 C652 245,725 245,760 290 L760 435 C730 463,647 463,616 435 Z", .46),
            ellipse("glutes", 638, 590, 60, 72, -8, .50),
            ellipse("glutes", 738, 590, 60, 72, 8, .50),
            ellipse("hamstrings", 630, 780, 40, 145, 4, .55),
            ellipse("hamstrings", 752, 780, 40, 145, -4, .55),
            ellipse("calves", 610, 956, 31, 120, -4, .48),
            ellipse("calves", 775, 956, 31, 120, 4, .48),
        ]
    else:
        # FRONT — left figure
        zones += [
            ellipse("shoulders", 176, 298, 47, 70, -14, .50),
            ellipse("shoulders", 405, 298, 47, 70, 14, .50),
            ellipse("arms", 145, 458, 34, 126, 5, .48),
            ellipse("arms", 435, 458, 34, 126, -5, .48),
            ellipse("chest", 248, 342, 64, 42, -6, .43),
            ellipse("chest", 331, 342, 64, 42, 6, .43),
            poly("core", "244,392 342,392 370,610 216,610", .48),
            ellipse("quads", 234, 735, 47, 142, 5, .57),
            ellipse("quads", 348, 735, 47, 142, -5, .57),
            ellipse("calves", 214, 968, 34, 132, -4, .50),
            ellipse("calves", 372, 968, 34, 132, 4, .50),
            # BACK — right figure
            ellipse("shoulders", 582, 294, 48, 70, -16, .47),
            ellipse("shoulders", 805, 294, 48, 70, 16, .47),
            ellipse("arms", 538, 462, 34, 128, 6, .47),
            ellipse("arms", 852, 462, 34, 128, -6, .47),
            path("back", "M605 288 C652 238,735 238,784 288 L774 450 C736 494,654 494,616 450 Z", .47),
            ellipse("glutes", 642, 615, 62, 76, -8, .51),
            ellipse("glutes", 748, 615, 62, 76, 8, .51),
            ellipse("hamstrings", 628, 792, 42, 152, 4, .56),
            ellipse("hamstrings", 768, 792, 42, 152, -4, .56),
            ellipse("calves", 608, 988, 35, 124, -4, .48),
            ellipse("calves", 794, 988, 35, 124, 4, .48),
        ]
    return "\n".join(zones)




def realistic_twin_html(soldier: Dict[str, Any], loads: Dict[str, int], title_extra: str = "") -> str:
    sex = safe(soldier.get("sex"), "M")
    female = str(sex).upper().startswith("F")
    img_b64 = FEMALE_TWIN_BASE_WEBP if female else MALE_TWIN_BASE_WEBP
    silhouette_label = "Silhueta feminina" if female else "Silhueta masculina"
    top_key = max(loads, key=loads.get) if loads else "core"
    top_label = MUSCLE_LABELS.get(top_key, top_key)
    title_extra = title_extra or "grupos musculares dinâmicos"
    return f'''
    <style>
      body {{ margin:0; background:transparent; font-family: Inter, Segoe UI, Arial, sans-serif; }}
      .real-twin-card {{ background: linear-gradient(180deg,#06170d,#020b06); border: 1px solid rgba(255,248,207,.18); border-radius: 24px; padding: 20px 20px 16px; box-shadow: 0 28px 70px rgba(16,32,21,.24); color: #fff8cf; overflow:hidden; }}
      .real-twin-head {{display:flex; justify-content:space-between; align-items:flex-start; gap:18px; margin-bottom:12px;}}
      .real-twin-head h3 {{margin:0; font-size:24px; letter-spacing:.18em; text-transform:uppercase; font-weight:950;}}
      .real-twin-head p {{margin:6px 0 0; color:#c4d5b5; font-weight:800; font-size:13px;}}
      .twin-pill {{border:1px solid rgba(255,248,207,.22); border-radius:999px; padding:9px 12px; color:#fff8cf; font-size:12px; font-weight:950; white-space:nowrap;}}
      .img-stage {{position:relative; width:min(100%, 700px); margin:0 auto; aspect-ratio: 980 / 1224; border-radius:18px; overflow:hidden; background:#020b06;}}
      .img-stage::before {{content:""; position:absolute; inset:0; background:radial-gradient(circle at 50% 25%,rgba(255,248,207,.08),transparent 38%); z-index:2; pointer-events:none;}}
      .img-stage svg {{position:absolute; inset:0; width:100%; height:100%; display:block; z-index:1;}}
      .muscle-zone-svg {{mix-blend-mode:screen; filter:saturate(1.28);}}
      .legend {{display:flex; gap:22px; flex-wrap:wrap; align-items:center; justify-content:center; margin-top:14px; color:#dce9d0; font-size:12px; font-weight:900;}}
      .legend span {{display:inline-flex; align-items:center; gap:7px;}}
      .dot {{width:12px; height:12px; border-radius:50%; display:inline-block;}}
    </style>
    <div class="real-twin-card">
      <div class="real-twin-head">
        <div><h3>Digital Twin</h3><p>{html.escape(silhouette_label)} · {html.escape(title_extra)} · zona principal: {html.escape(top_label)}</p></div>
        <div class="twin-pill">coloração dinâmica</div>
      </div>
      <div class="img-stage">
        <svg viewBox="0 0 980 1224" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="{html.escape(silhouette_label)} digital twin">
          <image href="data:image/webp;base64,{img_b64}" x="0" y="0" width="980" height="1224" preserveAspectRatio="xMidYMid meet" />
          <g class="muscle-zone-svg">{twin_zone_overlays(loads, sex)}</g>
        </svg>
      </div>
      <div class="legend">
        <span><i class="dot" style="background:#22c55e"></i>Controlado</span>
        <span><i class="dot" style="background:#d7b92f"></i>Atenção</span>
        <span><i class="dot" style="background:#f59e0b"></i>Elevado</span>
        <span><i class="dot" style="background:#ef4444"></i>Crítico</span>
      </div>
    </div>
    '''


def render_dynamic_twin(soldier: Dict[str, Any], loads: Dict[str, int]) -> None:
    components.html(realistic_twin_html(soldier, loads), height=1020, scrolling=False)


def twin_page(profile: Dict[str, Any]) -> None:
    soldier = get_profile_soldier(profile)
    if not soldier:
        st.warning("Este utilizador ainda não tem soldier_id associado no perfil.")
        return
    loads = get_muscle_loads(str(soldier.get("soldier_id")))
    c1, c2, c3, c4 = st.columns(4, gap="large")
    avg_load = int(round(sum(loads.values()) / max(1, len(loads))))
    top_group = max(loads, key=loads.get)
    with c1: metric_card("Prontidão", pct(soldier.get("readiness_score")), safe(soldier.get("readiness_status")))
    with c2: metric_card("Carga muscular", f"{avg_load}%", f"maior: {MUSCLE_LABELS.get(top_group, top_group)}")
    with c3: metric_card("Risco", "Baixo" if n(soldier.get("injury_risk")) < 35 else "Moderado" if n(soldier.get("injury_risk")) < 60 else "Elevado", pct(soldier.get("injury_risk")))
    with c4: metric_card("Recuperação", pct(soldier.get("recovery_score")), "sono / fadiga / carga")

    left, right = st.columns([1.18, .92], gap="large")
    with left:
        render_dynamic_twin(soldier, loads)
    with right:
        bars = pd.DataFrame([{"Grupo": MUSCLE_LABELS.get(k, k), "Carga": v, "Estado": load_label(v)} for k, v in loads.items()]).sort_values("Carga", ascending=True)
        fig = px.bar(bars, x="Carga", y="Grupo", orientation="h", color="Estado", color_discrete_map={"Controlado":"#22c55e", "Atenção":"#d7b92f", "Elevado":"#f59e0b", "Crítico":"#ef4444"}, title="Carga por grupo muscular", text="Carga")
        fig.update_traces(texttemplate="%{text}%", textposition="outside")
        st.plotly_chart(apply_chart_style(fig, 440), use_container_width=True)
        highest = bars.sort_values("Carga", ascending=False).iloc[0]
        critical = bars[bars["Carga"] >= 75]
        if not critical.empty:
            msg = "Reduzir estímulo nas zonas críticas e priorizar recuperação ativa."
        elif int(highest["Carga"]) >= 60:
            msg = f"Controlar volume em {highest['Grupo']}; evitar novo estímulo intenso consecutivo."
        else:
            msg = "Carga muscular equilibrada; treino pode avançar com controlo normal."
        st.markdown(f"""
        <div class="info-card"><h3>Leitura muscular automática</h3>
          {info_row('Zona mais carregada', f'{highest["Grupo"]} · {int(highest["Carga"])}%')}
          {info_row('Estado muscular', 'Sem zona crítica' if critical.empty else f'{len(critical)} zona(s) críticas')}
          {info_row('Recomendação', msg)}
        </div>
        """, unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        recent = get_recent_training(str(soldier.get("soldier_id")))
        if not recent.empty:
            recent = recent[[c for c in ["session_date", "session_type", "duration_min", "intensity", "focus_area"] if c in recent.columns]].head(5)
            st.markdown('<div class="info-card"><h3>Treinos recentes</h3></div>', unsafe_allow_html=True)
            st.dataframe(recent, use_container_width=True, hide_index=True)

# =========================================================
# Simulations
# =========================================================
def decision_for(readiness: int, risk: int) -> str:
    if risk >= 75 or readiness < 45:
        return "Retirar/Adaptar"
    if risk >= 58 or readiness < 60:
        return "Monitorizar"
    return "Executa"


def training_parameters(training_type: str) -> Tuple[Dict[str, Any], int, int, str]:
    params: Dict[str, Any] = {"training_type": training_type}
    if training_type == "Corrida contínua":
        c1, c2, c3 = st.columns(3, gap="large")
        with c1: duration = st.slider("Duração", 20, 90, 45)
        with c2: intensity = st.slider("Intensidade", 1, 10, 6)
        with c3: pace = st.selectbox("Zona de ritmo", ["Leve", "Moderada", "Forte"])
        params.update({"duration": duration, "intensity": intensity, "pace_zone": pace})
        focus = "Pernas"
    elif training_type == "Corrida intervalada":
        c1, c2, c3, c4 = st.columns(4, gap="large")
        with c1: reps = st.slider("Repetições", 4, 12, 8)
        with c2: dist = st.selectbox("Distância", [200, 400, 800, 1000], index=1)
        with c3: rec = st.slider("Recuperação (s)", 30, 180, 90)
        with c4: intensity = st.slider("Intensidade", 1, 10, 8)
        duration = int(reps * (dist / 180 + rec / 60))
        params.update({"repetitions": reps, "distance_m": dist, "recovery_s": rec, "intensity": intensity})
        focus = "Pernas"
    elif training_type == "Marcha com carga":
        c1, c2, c3, c4 = st.columns(4, gap="large")
        with c1: duration = st.slider("Duração", 30, 180, 90)
        with c2: load = st.slider("Carga externa (kg)", 5, 35, 18)
        with c3: terrain = st.selectbox("Terreno", ["Plano", "Misto", "Inclinado"])
        with c4: intensity = st.slider("Intensidade", 1, 10, 7)
        params.update({"duration": duration, "external_load_kg": load, "terrain": terrain, "intensity": intensity})
        focus = "Pernas/Core"
    elif training_type == "Circuito de força":
        c1, c2, c3 = st.columns(3, gap="large")
        with c1: rounds = st.slider("Rondas", 2, 8, 4)
        with c2: intensity = st.slider("Intensidade", 1, 10, 7)
        with c3: focus = st.selectbox("Foco", ["Full body", "Superior", "Inferior", "Core"])
        duration = rounds * 12
        params.update({"rounds": rounds, "intensity": intensity, "focus": focus})
    elif training_type == "Treino técnico-tático":
        c1, c2, c3 = st.columns(3, gap="large")
        with c1: duration = st.slider("Duração", 30, 180, 75)
        with c2: intensity = st.slider("Intensidade", 1, 10, 6)
        with c3: scenario = st.selectbox("Cenário", ["Patrulha", "Progressão", "Combate aproximado", "Reconhecimento"])
        params.update({"duration": duration, "intensity": intensity, "scenario": scenario})
        focus = "Operacional"
    else:
        c1, c2 = st.columns(2, gap="large")
        with c1: duration = st.slider("Duração", 15, 60, 30)
        with c2: intensity = st.slider("Intensidade", 1, 5, 2)
        modality = st.selectbox("Modalidade", ["Bicicleta leve", "Mobilidade", "Caminhada", "Natação leve"])
        params.update({"duration": duration, "intensity": intensity, "modality": modality})
        focus = "Recuperação"
    return params, duration, intensity, focus


def accessible_groups(df: pd.DataFrame) -> Dict[str, pd.DataFrame]:
    df = enrich_hierarchy_columns(df)
    groups = {"Todo o escalão acessível": df}
    if "platoon_name" in df:
        for name in sorted(df["platoon_name"].dropna().unique().tolist(), key=lambda x: (_first_number(x), x)):
            groups[f"Pelotão · {name}"] = df[df["platoon_name"] == name]
    if "section_full_label" in df:
        for name in sorted(df["section_full_label"].dropna().unique().tolist(), key=lambda x: (_first_number(x), x)):
            if name and name != "—":
                groups[f"Secção · {name}"] = df[df["section_full_label"] == name]
    return groups


def simulate_group_training(profile: Dict[str, Any]) -> None:
    df = accessible_snapshot(exclude_own=True, profile=profile)
    if df.empty:
        st.info("Sem militares acessíveis para simular.")
        return
    groups = accessible_groups(df)
    selected_group = st.selectbox("Grupo a simular", list(groups.keys()))
    group_df = groups[selected_group].copy()
    st.caption(f"Grupo selecionado: {selected_group} · {len(group_df)} militar(es)")
    training_type = st.selectbox("Tipo de treino", ["Corrida contínua", "Corrida intervalada", "Marcha com carga", "Circuito de força", "Treino técnico-tático", "Recuperação ativa"])
    params, duration, intensity, focus = training_parameters(training_type)
    impact = int(round(intensity * 2.1 + duration / 10))
    recovery_bonus = 10 if training_type == "Recuperação ativa" else 0
    rows = []
    for _, r in group_df.iterrows():
        base_ready = n(r.get("readiness_score"), 60)
        base_risk = n(r.get("injury_risk"), 35)
        fatigue = n(r.get("fatigue_score"), 4)
        predicted_readiness = max(0, min(100, base_ready - impact + recovery_bonus - max(0, fatigue - 5)))
        predicted_risk = max(0, min(100, base_risk + int(impact * .75) - recovery_bonus))
        rows.append({
            "soldier_id": r.get("soldier_id"),
            "Posto": r.get("rank_code"), "Militar": r.get("full_name"), "Estado": r.get("readiness_status"),
            "Prontidão atual": base_ready, "Prontidão prevista": predicted_readiness,
            "Risco atual": base_risk, "Risco previsto": predicted_risk,
            "Impacto": predicted_readiness - base_ready,
            "Decisão": decision_for(predicted_readiness, predicted_risk),
        })
    sim = pd.DataFrame(rows).sort_values(["Decisão", "Risco previsto"], ascending=[True, False])
    c1, c2, c3, c4 = st.columns(4, gap="large")
    with c1: metric_card("Prontidão média atual", f"{int(round(group_df['readiness_score'].mean()))}%", selected_group)
    with c2: metric_card("Prontidão média prevista", f"{int(round(sim['Prontidão prevista'].mean()))}%", "após treino")
    with c3: metric_card("Militares a adaptar", int((sim["Decisão"] != "Executa").sum()), "Monitorizar ou Retirar/Adaptar")
    with c4: metric_card("Risco elevado previsto", int((sim["Risco previsto"] >= 60).sum()), "risco ≥ 60")
    st.dataframe(sim.drop(columns=["soldier_id"]), use_container_width=True, hide_index=True)
    if st.button("Guardar simulação coletiva", use_container_width=True):
        sim_group_id = str(uuid.uuid4())
        payloads = []
        for row in rows:
            payloads.append({
                "simulation_group_id": sim_group_id,
                "soldier_id": row["soldier_id"],
                "created_by_profile_id": profile.get("id"),
                "training_type": training_type,
                "duration_min": duration,
                "intensity": intensity,
                "parameters": params,
                "predicted_readiness": int(row["Prontidão prevista"]),
                "predicted_injury_risk": int(row["Risco previsto"]),
                "decision": row["Decisão"],
                "notes": f"Simulação coletiva: {selected_group}; foco: {focus}",
            })
        try:
            sb_insert_many("training_simulations", payloads)
            st.success("Simulação coletiva guardada.")
        except Exception as exc:
            st.error("Não foi possível guardar a simulação.")
            st.caption(str(exc))


def muscle_delta_for_training(training_type: str, intensity: int, duration: int, focus: str) -> Dict[str, int]:
    base = max(2, int(round(intensity * 1.25 + duration / 22)))
    delta = {k: 0 for k in MUSCLE_LABELS}
    if training_type in {"Corrida contínua", "Corrida intervalada"}:
        mult = 1.35 if training_type == "Corrida intervalada" else 1.0
        delta.update({"quads": int(base * mult), "hamstrings": int(base * 1.05 * mult), "calves": int(base * 1.1 * mult), "glutes": int(base * .75 * mult), "core": int(base * .45)})
    elif training_type == "Marcha com carga":
        delta.update({"quads": base + 8, "hamstrings": base + 6, "calves": base + 5, "glutes": base + 7, "core": base + 5, "back": base + 3, "shoulders": base + 2})
    elif training_type == "Circuito de força":
        if focus == "Superior":
            delta.update({"chest": base + 6, "back": base + 5, "shoulders": base + 5, "arms": base + 6, "core": base + 2})
        elif focus == "Inferior":
            delta.update({"quads": base + 7, "hamstrings": base + 6, "glutes": base + 6, "calves": base + 3, "core": base + 2})
        elif focus == "Core":
            delta.update({"core": base + 8, "back": base + 3, "glutes": base + 2})
        else:
            delta.update({k: base for k in MUSCLE_LABELS})
    elif training_type == "Treino técnico-tático":
        delta.update({"quads": base, "hamstrings": base, "calves": base - 1, "glutes": base - 1, "core": base, "back": base - 1, "shoulders": base - 1})
    else:  # recuperação ativa
        delta = {k: -max(2, int(base / 2)) for k in MUSCLE_LABELS}
    return {k: int(v) for k, v in delta.items()}


def update_loads(loads: Dict[str, int], delta: Dict[str, int]) -> Dict[str, int]:
    return {k: max(0, min(100, n(loads.get(k)) + int(delta.get(k, 0)))) for k in MUSCLE_LABELS}


def simulate_individual_training(profile: Dict[str, Any]) -> None:
    soldier = get_profile_soldier(profile)
    if not soldier:
        st.warning("Perfil individual não encontrado.")
        return

    st.markdown('<div class="section-title">Simulador individual de treino</div>', unsafe_allow_html=True)
    left_cfg, right_cfg = st.columns([1.05, .95], gap="large")
    with left_cfg:
        training_type = st.selectbox("Tipo de treino", ["Corrida contínua", "Corrida intervalada", "Marcha com carga", "Circuito de força", "Treino técnico-tático", "Recuperação ativa"])
        params, duration, intensity, focus = training_parameters(training_type)
    with right_cfg:
        st.markdown('<div class="info-card"><h3>Objetivo da simulação</h3>' +
                    info_row("Pergunta", "Compensa fazer este treino agora?") +
                    info_row("Base", "prontidão, risco, fadiga, recuperação e carga muscular") +
                    info_row("Resultado", "decisão + impacto no Digital Twin") +
                    "</div>", unsafe_allow_html=True)

    loads_now = get_muscle_loads(str(soldier.get("soldier_id")))
    delta = muscle_delta_for_training(training_type, intensity, duration, str(focus))
    loads_pred = update_loads(loads_now, delta)

    impact = int(round(intensity * 2.1 + duration / 10))
    fatigue = n(soldier.get("fatigue_score"), 4)
    recovery = n(soldier.get("recovery_score"), 60)
    recovery_bonus = 12 if training_type == "Recuperação ativa" else 0
    fatigue_penalty = max(0, fatigue - 5) * 2
    recovery_penalty = max(0, 55 - recovery) // 5
    muscle_penalty = max(0, max(loads_pred.values()) - 70) // 4

    base_ready = n(soldier.get("readiness_score"), 60)
    base_risk = n(soldier.get("injury_risk"), 35)
    predicted_readiness = max(0, min(100, base_ready - impact - fatigue_penalty - recovery_penalty - muscle_penalty + recovery_bonus))
    predicted_risk = max(0, min(100, base_risk + int(impact * .70) + muscle_penalty * 2 - recovery_bonus))
    decision = decision_for(predicted_readiness, predicted_risk)
    benefit = "Alto" if training_type == "Recuperação ativa" or (predicted_risk < 55 and predicted_readiness >= 60) else "Moderado" if decision == "Monitorizar" else "Baixo"

    c1, c2, c3, c4 = st.columns(4, gap="large")
    with c1: metric_card("Prontidão atual", f"{base_ready}%", safe(soldier.get("readiness_status")))
    with c2: metric_card("Prontidão prevista", f"{predicted_readiness}%", f"impacto {predicted_readiness - base_ready} p.p.")
    with c3: metric_card("Risco previsto", f"{predicted_risk}%", decision)
    with c4: metric_card("Benefício estimado", benefit, f"foco: {focus}")

    lcol, rcol = st.columns([1.08, .92], gap="large")
    with lcol:
        render_dynamic_twin(soldier, loads_pred)
    with rcol:
        impact_rows = []
        for k in MUSCLE_LABELS:
            impact_rows.append({
                "Grupo": MUSCLE_LABELS[k],
                "Atual": loads_now.get(k, 0),
                "Após treino": loads_pred.get(k, 0),
                "Impacto": loads_pred.get(k, 0) - loads_now.get(k, 0),
                "Estado previsto": load_label(loads_pred.get(k, 0)),
            })
        impact_df = pd.DataFrame(impact_rows).sort_values("Após treino", ascending=False)
        fig = px.bar(impact_df.sort_values("Após treino"), x="Após treino", y="Grupo", orientation="h", color="Estado previsto", color_discrete_map={"Controlado":"#22c55e", "Atenção":"#d7b92f", "Elevado":"#f59e0b", "Crítico":"#ef4444"}, title="Impacto previsto no Digital Twin", text="Após treino")
        fig.update_traces(texttemplate="%{text}%", textposition="outside")
        st.plotly_chart(apply_chart_style(fig, 420), use_container_width=True)
        top_after = impact_df.iloc[0]
        if decision == "Executa":
            action = "Treino recomendado. Mantém recolha de feedback pós-sessão."
        elif decision == "Monitorizar":
            action = "Treino possível, mas reduz volume/intensidade ou controla de perto a resposta."
        else:
            action = "Não recomendado sem adaptação. Prioriza recuperação ou treino alternativo."
        st.markdown('<div class="info-card"><h3>Decisão do simulador</h3>' +
                    info_row("Decisão", decision) +
                    info_row("Zona mais afetada", f"{top_after['Grupo']} · {int(top_after['Após treino'])}%") +
                    info_row("Ação", action) +
                    "</div>", unsafe_allow_html=True)

    st.markdown('<div class="section-title">Detalhe por grupo muscular</div>', unsafe_allow_html=True)
    st.dataframe(impact_df, use_container_width=True, hide_index=True)

    if st.button("Guardar simulação individual", use_container_width=True):
        try:
            sb_insert_many("training_simulations", [{
                "simulation_group_id": str(uuid.uuid4()),
                "soldier_id": soldier.get("soldier_id"),
                "created_by_profile_id": profile.get("id"),
                "training_type": training_type,
                "duration_min": duration,
                "intensity": intensity,
                "parameters": {**params, "muscle_delta": delta, "predicted_muscle_loads": loads_pred},
                "predicted_readiness": predicted_readiness,
                "predicted_injury_risk": predicted_risk,
                "decision": decision,
                "notes": f"Simulação individual; foco: {focus}; benefício: {benefit}",
            }])
            st.success("Simulação individual guardada.")
        except Exception as exc:
            st.error("Não foi possível guardar a simulação.")
            st.caption(str(exc))


def simulate_training(profile: Dict[str, Any]) -> None:
    if current_mode(profile) == "command" and is_command_role(profile):
        simulate_group_training(profile)
    else:
        simulate_individual_training(profile)

# =========================================================
# Admin quick inspection
# =========================================================
def admin_page(profile: Dict[str, Any]) -> None:
    if profile_role(profile) != "admin":
        st.error("Acesso reservado a administrador.")
        return
    st.markdown('<div class="section-title">Administração</div>', unsafe_allow_html=True)
    for table in ["profiles", "soldiers", "org_units", "command_assignments", "company_dashboard_current"]:
        with st.expander(table):
            try:
                st.dataframe(pd.DataFrame(sb_select(table, limit=200)), use_container_width=True)
            except Exception as exc:
                st.caption(str(exc))

# =========================================================
# Main
# =========================================================
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
    elif page == "Militares":
        soldiers_page(profile)
    elif page == "Meu perfil" or page == "Militar":
        soldier = get_profile_soldier(profile)
        render_individual_landing(soldier, "Meu perfil" if page == "Meu perfil" else "Militar")
    elif page == "Digital Twin":
        twin_page(profile)
    elif page == "Simular treino":
        simulate_training(profile)
    elif page == "Admin":
        admin_page(profile)

if __name__ == "__main__":
    main()

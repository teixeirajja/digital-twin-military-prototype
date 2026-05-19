from __future__ import annotations

import html
import math
import uuid
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
  border-radius: 12px !important; border: 1px solid rgba(20,83,45,.25) !important; background: #fff !important;
  color: var(--g700) !important; font-weight: 900 !important; min-height: 42px; box-shadow: 0 8px 22px rgba(16,32,21,.07) !important;
}
.stButton > button:hover, .stFormSubmitButton > button:hover {background: var(--g700) !important; color: #fff !important;}

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
.header-chip {display:inline-flex; align-items:center; justify-content:center; min-width:150px; padding:11px 16px; border-radius:14px; border:1px solid rgba(255,248,207,.30); color:#fff8cf; font-weight:900; background:rgba(0,0,0,.14);}

/* Radio navigation */
[data-testid="stRadio"] > label {display:none !important;}
[data-testid="stRadio"] div[role="radiogroup"] {display:flex !important; flex-direction:row !important; flex-wrap:wrap !important; gap:8px !important; background:rgba(255,255,255,.78) !important; border:1px solid var(--line) !important; border-radius:999px !important; padding:8px !important; width:fit-content !important; box-shadow:0 10px 28px rgba(16,32,21,.07) !important;}
[data-testid="stRadio"] div[role="radiogroup"] label {display:flex !important; align-items:center !important; justify-content:center !important; min-height:42px !important; padding:0 18px !important; border-radius:999px !important; border:1px solid rgba(20,83,45,.18) !important; background:#fff !important; color:var(--g800) !important; box-shadow:0 5px 14px rgba(16,32,21,.05) !important; cursor:pointer !important; font-weight:900 !important;}
[data-testid="stRadio"] div[role="radiogroup"] label:has(input:checked) {background:linear-gradient(135deg, var(--g800), var(--g600)) !important; color:#fff8cf !important; border-color:var(--g600) !important;}
[data-testid="stRadio"] div[role="radiogroup"] label input, [data-testid="stRadio"] div[role="radiogroup"] label > div:first-child {display:none !important;}
[data-testid="stRadio"] div[role="radiogroup"] label p {color:inherit !important; font-size:.92rem !important; font-weight:900 !important;}

.section-card {background:#fff; border:1px solid var(--line); border-radius:18px; padding:18px; box-shadow:var(--shadow); margin-bottom:16px;}
.section-title {background:#fff; border:1px solid var(--line); border-left:6px solid var(--g700); border-radius:14px; padding:16px 18px; font-size:1.1rem; font-weight:950; color:var(--ink); letter-spacing:.05em; margin:10px 0 16px;}
.metric-card {background:#fff; border:1px solid var(--line); border-left:5px solid var(--g700); border-radius:16px; padding:17px 18px; box-shadow:var(--shadow); min-height:128px;}
.metric-card small {display:block; text-transform:uppercase; color:var(--g700); font-weight:950; letter-spacing:.06em; margin-bottom:12px;}
.metric-card h2 {margin:0 0 9px; font-size:1.86rem; color:var(--ink) !important; font-weight:950;}
.metric-card p {margin:0; color:var(--muted); font-weight:700; font-size:.86rem;}
.info-card {background:#fff; border:1px solid var(--line); border-radius:18px; padding:18px; box-shadow:var(--shadow);}
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
.table-shell {border-radius:18px; overflow:hidden; border:1px solid var(--line); background:#fff; box-shadow:var(--shadow); margin:18px 0;}
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

@media(max-width:900px){.block-container{padding-left:1rem!important; padding-right:1rem!important}.main-header{flex-direction:column; align-items:flex-start}.metric-card{min-height:110px}}
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
    for k in ["access_token", "refresh_token", "profile", "user_email", "page"]:
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


def accessible_snapshot() -> pd.DataFrame:
    """Reads current accessible force snapshot. RLS should restrict by logged-in user."""
    try:
        df = pd.DataFrame(sb_select("company_dashboard_current", order="full_name"))
    except Exception as exc:
        st.error("Não foi possível ler a vista company_dashboard_current.")
        st.caption(str(exc))
        return pd.DataFrame()
    if df.empty:
        return df
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
# Top bar and navigation
# =========================================================
def top_bar(profile: Dict[str, Any]) -> str:
    role = profile_role(profile)
    role_label = ROLE_LABELS.get(role, role)
    st.markdown(f"""
    <div class="main-header">
      <div>
        <h1>Military Digital Twin</h1>
        <p>Sessão iniciada · {html.escape(profile_display(profile))} · {html.escape(role_label)}</p>
      </div>
      <div class="header-chip">Terminar sessão</div>
    </div>
    """, unsafe_allow_html=True)
    _, right = st.columns([7, 1.25])
    with right:
        if st.button("Terminar sessão", use_container_width=True, key="logout_btn"):
            logout()
    if role == "soldier":
        pages = ["Militar", "Digital Twin", "Simular treino"]
    else:
        pages = ["Dashboard", "Militares", "Meu perfil", "Digital Twin", "Simular treino"]
        if role == "admin":
            pages.append("Admin")
    default = st.session_state.get("page") if st.session_state.get("page") in pages else pages[0]
    selected = st.radio("Navegação", pages, index=pages.index(default), horizontal=True, key="nav_radio")
    st.session_state["page"] = selected
    return selected

# =========================================================
# Dashboard / command views
# =========================================================
def filter_snapshot(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df
    st.markdown('<div class="section-title">Filtros operacionais</div>', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns([1.1, 1.1, 1.2, 1.0])
    platoons = ["Todos"] + sorted([x for x in df.get("platoon_name", pd.Series(dtype=str)).dropna().unique().tolist()])
    sections = ["Todas"] + sorted([x for x in df.get("section_name", pd.Series(dtype=str)).dropna().unique().tolist()])
    with c1:
        platoon = st.selectbox("Pelotão", platoons)
    with c2:
        section = st.selectbox("Secção", sections)
    with c3:
        statuses = st.multiselect("Estado", STATUS_ORDER, default=STATUS_ORDER)
    with c4:
        min_ready = st.slider("Prontidão mínima", 0, 100, 0)
    out = df.copy()
    if platoon != "Todos" and "platoon_name" in out:
        out = out[out["platoon_name"] == platoon]
    if section != "Todas" and "section_name" in out:
        out = out[out["section_name"] == section]
    if statuses and "readiness_status" in out:
        out = out[out["readiness_status"].isin(statuses)]
    if "readiness_score" in out:
        out = out[out["readiness_score"].fillna(0) >= min_ready]
    return out


def render_metrics(df: pd.DataFrame) -> None:
    total = len(df)
    ready = int((df["readiness_status"] == "Pronto").sum()) if not df.empty else 0
    attention = int((df["readiness_status"] == "Atenção").sum()) if not df.empty else 0
    risk = int((df["readiness_status"] == "Risco").sum()) if not df.empty else 0
    avg = int(round(df["readiness_score"].dropna().mean())) if not df.empty and "readiness_score" in df else 0
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1: metric_card("Militares analisados", total, command_scope_label(st.session_state["profile"]))
    with c2: metric_card("Prontos", ready, "prontidão ≥ 75")
    with c3: metric_card("Atenção", attention, "55 ≤ prontidão < 75")
    with c4: metric_card("Risco", risk, "prontidão < 55 ou risco alto")
    with c5: metric_card("Prontidão média", f"{avg}%", "média do escalão")


def render_charts(df: pd.DataFrame) -> None:
    if df.empty:
        st.info("Sem dados para visualizar neste filtro.")
        return
    left, right = st.columns([1.1, 1])
    colors = {"Pronto": "#22c55e", "Atenção": "#f59e0b", "Risco": "#ef4444"}
    with left:
        chart_df = df.sort_values("readiness_score", ascending=True).tail(20)
        fig = px.bar(chart_df, x="readiness_score", y="full_name", orientation="h", color="readiness_status", color_discrete_map=colors, labels={"readiness_score":"Prontidão", "full_name":"Militar", "readiness_status":"Estado"}, title="Prontidão por militar")
        st.plotly_chart(apply_chart_style(fig, 440), use_container_width=True)
    with right:
        fig = px.scatter(df, x="readiness_score", y="injury_risk", size="recovery_score", color="readiness_status", color_discrete_map=colors, hover_name="full_name", labels={"readiness_score":"Prontidão", "injury_risk":"Risco de lesão", "readiness_status":"Estado"}, title="Prontidão vs risco")
        st.plotly_chart(apply_chart_style(fig, 440), use_container_width=True)

    group_col = "section_name" if "section_name" in df and df["section_name"].notna().any() else "platoon_name"
    if group_col in df:
        g = df.groupby([group_col, "readiness_status"]).size().reset_index(name="militares")
        fig = px.bar(g, x=group_col, y="militares", color="readiness_status", color_discrete_map=colors, title="Estado por subunidade", labels={group_col:"Subunidade", "militares":"Militares", "readiness_status":"Estado"})
        st.plotly_chart(apply_chart_style(fig, 360), use_container_width=True)


def operational_table(df: pd.DataFrame, title: str = "Tabela operacional") -> None:
    if df.empty:
        st.info("Sem militares para mostrar neste filtro.")
        return
    rows = []
    cols = ["rank_code", "full_name", "platoon_name", "section_name", "readiness_status", "readiness_score", "injury_risk", "recovery_score", "cooper_m", "fatigue_score", "sleep_hours"]
    view = df[[c for c in cols if c in df.columns]].copy().sort_values(["readiness_status", "readiness_score"], ascending=[True, False])
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
        </tr>
        """)
    st.markdown(f"""
    <div class="table-shell">
      <div class="table-title"><span>{html.escape(title)}</span><span>{len(view)} militar(es)</span></div>
      <table class="op-table">
        <thead><tr><th>Posto</th><th>Militar</th><th>Pelotão</th><th>Secção</th><th>Estado</th><th>Prontidão</th><th>Risco</th><th>Recuperação</th><th>Cooper</th><th>Fadiga</th><th>Sono</th></tr></thead>
        <tbody>{''.join(rows)}</tbody>
      </table>
    </div>
    """, unsafe_allow_html=True)


def commander_dashboard(profile: Dict[str, Any]) -> None:
    scope = command_scope_label(profile)
    st.markdown(f'<div class="section-title">Dashboard — {html.escape(scope)}</div>', unsafe_allow_html=True)
    df = accessible_snapshot()
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
    st.markdown(f'<div class="section-title">{html.escape(title)} · {html.escape(safe(soldier.get("rank_code")))} {html.escape(safe(soldier.get("full_name")))}</div>', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    status = safe(soldier.get("readiness_status"), "Atenção")
    with c1: metric_card("Prontidão", pct(soldier.get("readiness_score")), status)
    with c2: metric_card("Risco operacional", "Baixo" if n(soldier.get("injury_risk")) < 35 else "Moderado" if n(soldier.get("injury_risk")) < 60 else "Elevado", f"{pct(soldier.get('injury_risk'))}")
    with c3: metric_card("Recuperação", pct(soldier.get("recovery_score")), "sono / fadiga / carga")
    with c4: metric_card("Cooper", f"{n(soldier.get('cooper_m'))} m", "último teste")
    left, right = st.columns([1.05, .95])
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
    df = accessible_snapshot()
    if df.empty:
        st.info("Sem militares acessíveis.")
        return
    st.markdown('<div class="section-title">Militares acessíveis</div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 1, 2])
    with c1:
        platoons = ["Todos"] + sorted([x for x in df.get("platoon_name", pd.Series(dtype=str)).dropna().unique().tolist()])
        platoon = st.selectbox("Filtrar pelotão", platoons, key="soldier_filter_platoon")
    with c2:
        dff = df if platoon == "Todos" else df[df["platoon_name"] == platoon]
        sections = ["Todas"] + sorted([x for x in dff.get("section_name", pd.Series(dtype=str)).dropna().unique().tolist()])
        section = st.selectbox("Filtrar secção", sections, key="soldier_filter_section")
    dff = df.copy()
    if platoon != "Todos": dff = dff[dff["platoon_name"] == platoon]
    if section != "Todas": dff = dff[dff["section_name"] == section]
    with c3:
        choices = [f"{r.rank_code} {r.full_name}" for r in dff.itertuples()]
        selected = st.selectbox("Selecionar militar", choices)
    row = dff.iloc[choices.index(selected)].to_dict() if choices else None
    if row:
        render_commander_authorized_summary(row)
    operational_table(dff, "Militares filtrados")


def render_commander_authorized_summary(soldier: Dict[str, Any]) -> None:
    st.markdown(f'<div class="section-title">{html.escape(safe(soldier.get("rank_code")))} {html.escape(safe(soldier.get("full_name")))}</div>', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    risk = n(soldier.get("injury_risk"))
    readiness = n(soldier.get("readiness_score"))
    recovery = n(soldier.get("recovery_score"))
    status = safe(soldier.get("readiness_status"), "Atenção")
    with c1: metric_card("Prontidão", f"{readiness}%", status)
    with c2: metric_card("Risco operacional", "Baixo" if risk < 35 else "Moderado" if risk < 60 else "Elevado", f"{risk}%")
    with c3: metric_card("Disponibilidade", "Apto" if status == "Pronto" else "Condicionado" if status == "Atenção" else "Não recomendado", "para planeamento")
    with c4: metric_card("Cooper", f"{n(soldier.get('cooper_m'))} m", "último teste")
    left, right = st.columns([1, 1])
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
    # Smooth vector silhouette: front and back views with independent muscle zones.
    is_female = str(sex).upper().startswith("F")
    title = "Silhueta feminina" if is_female else "Silhueta masculina"
    # geometry tweaks
    torso_w = 70 if is_female else 82
    hip_w = 76 if is_female else 68
    shoulder_y = 112
    head_r = 22 if is_female else 24
    front_x, back_x = 205, 535
    bg = "#031008"
    # Helper to build one view.
    def base_person(cx: int, back: bool = False) -> str:
        # base dark body layers
        return f'''
        <g transform="translate({cx},0)">
          <circle cx="0" cy="58" r="{head_r}" fill="#1a211d" stroke="#6f7f66" stroke-opacity=".45"/>
          <path d="M -12 82 Q 0 98 12 82 L 17 105 L -17 105 Z" fill="#1a211d" stroke="#6f7f66" stroke-opacity=".35"/>
          <path d="M {-torso_w/2} 118 Q {-torso_w/2-8} 190 {-hip_w/2} 248 L {hip_w/2} 248 Q {torso_w/2+8} 190 {torso_w/2} 118 Q 0 100 {-torso_w/2} 118" fill="#111b15" stroke="#6f7f66" stroke-opacity=".35"/>
          <path d="M {-hip_w/2} 248 Q -18 270 -14 310 L -20 405 Q -19 455 -10 505 L -42 505 Q -55 455 -51 405 L -48 318 Q -55 278 {-hip_w/2} 248" fill="#111b15" stroke="#6f7f66" stroke-opacity=".35"/>
          <path d="M {hip_w/2} 248 Q 18 270 14 310 L 20 405 Q 19 455 10 505 L 42 505 Q 55 455 51 405 L 48 318 Q 55 278 {hip_w/2} 248" fill="#111b15" stroke="#6f7f66" stroke-opacity=".35"/>
          <path d="M {-torso_w/2} 124 Q -92 140 -94 205 L -102 315 Q -100 345 -84 360 L -66 360 Q -72 320 -70 270 L -63 175 Q -58 140 {-torso_w/2} 124" fill="#111b15" stroke="#6f7f66" stroke-opacity=".35"/>
          <path d="M {torso_w/2} 124 Q 92 140 94 205 L 102 315 Q 100 345 84 360 L 66 360 Q 72 320 70 270 L 63 175 Q 58 140 {torso_w/2} 124" fill="#111b15" stroke="#6f7f66" stroke-opacity=".35"/>
        </g>'''
    def front_zones(cx: int) -> str:
        chest = svg_style_fill(loads, "chest")
        shoulders = svg_style_fill(loads, "shoulders")
        arms = svg_style_fill(loads, "arms")
        core = svg_style_fill(loads, "core")
        quads = svg_style_fill(loads, "quads")
        calves = svg_style_fill(loads, "calves")
        return f'''
        <g transform="translate({cx},0)">
          <ellipse cx="{-torso_w/2-17}" cy="142" rx="24" ry="42" {shoulders}/>
          <ellipse cx="{torso_w/2+17}" cy="142" rx="24" ry="42" {shoulders}/>
          <path d="M -92 178 Q -72 170 -65 205 L -70 292 Q -84 300 -99 292 L -96 205 Q -96 190 -92 178" {arms}/>
          <path d="M 92 178 Q 72 170 65 205 L 70 292 Q 84 300 99 292 L 96 205 Q 96 190 92 178" {arms}/>
          <path d="M -35 128 Q -6 116 -2 158 Q -18 176 -43 170 Q -50 145 -35 128" {chest}/>
          <path d="M 35 128 Q 6 116 2 158 Q 18 176 43 170 Q 50 145 35 128" {chest}/>
          <path d="M -28 176 L 28 176 Q 31 218 20 244 L -20 244 Q -31 218 -28 176" {core}/>
          <line x1="0" y1="180" x2="0" y2="242" stroke="#061006" stroke-opacity=".45" stroke-width="2"/>
          <line x1="-25" y1="198" x2="25" y2="198" stroke="#061006" stroke-opacity=".35"/>
          <line x1="-24" y1="220" x2="24" y2="220" stroke="#061006" stroke-opacity=".35"/>
          <path d="M -42 258 Q -18 272 -18 330 L -25 398 Q -44 404 -57 394 L -53 315 Q -56 280 -42 258" {quads}/>
          <path d="M 42 258 Q 18 272 18 330 L 25 398 Q 44 404 57 394 L 53 315 Q 56 280 42 258" {quads}/>
          <path d="M -31 405 Q -18 415 -14 500 L -40 500 Q -51 432 -45 410 Q -39 404 -31 405" {calves}/>
          <path d="M 31 405 Q 18 415 14 500 L 40 500 Q 51 432 45 410 Q 39 404 31 405" {calves}/>
        </g>'''
    def back_zones(cx: int) -> str:
        backc = svg_style_fill(loads, "back")
        shoulders = svg_style_fill(loads, "shoulders")
        arms = svg_style_fill(loads, "arms")
        glutes = svg_style_fill(loads, "glutes")
        hams = svg_style_fill(loads, "hamstrings")
        calves = svg_style_fill(loads, "calves")
        return f'''
        <g transform="translate({cx},0)">
          <ellipse cx="{-torso_w/2-17}" cy="142" rx="24" ry="42" {shoulders}/>
          <ellipse cx="{torso_w/2+17}" cy="142" rx="24" ry="42" {shoulders}/>
          <path d="M -92 178 Q -72 170 -65 205 L -70 292 Q -84 300 -99 292 L -96 205 Q -96 190 -92 178" {arms}/>
          <path d="M 92 178 Q 72 170 65 205 L 70 292 Q 84 300 99 292 L 96 205 Q 96 190 92 178" {arms}/>
          <path d="M -44 125 Q -18 118 0 145 L 0 235 Q -34 214 -48 170 Q -52 146 -44 125" {backc}/>
          <path d="M 44 125 Q 18 118 0 145 L 0 235 Q 34 214 48 170 Q 52 146 44 125" {backc}/>
          <line x1="0" y1="116" x2="0" y2="250" stroke="#dbe9cf" stroke-opacity=".32" stroke-width="2"/>
          <path d="M -38 252 Q -6 235 -2 280 Q -16 302 -44 292 Q -54 270 -38 252" {glutes}/>
          <path d="M 38 252 Q 6 235 2 280 Q 16 302 44 292 Q 54 270 38 252" {glutes}/>
          <path d="M -45 302 Q -20 310 -20 392 Q -38 404 -55 394 Q -56 330 -45 302" {hams}/>
          <path d="M 45 302 Q 20 310 20 392 Q 38 404 55 394 Q 56 330 45 302" {hams}/>
          <path d="M -31 405 Q -18 415 -14 500 L -40 500 Q -51 432 -45 410 Q -39 404 -31 405" {calves}/>
          <path d="M 31 405 Q 18 415 14 500 L 40 500 Q 51 432 45 410 Q 39 404 31 405" {calves}/>
        </g>'''
    return f'''
    <svg viewBox="0 0 820 590" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Digital twin muscular dinâmico">
      <defs>
        <radialGradient id="halo" cx="50%" cy="20%" r="80%"><stop offset="0%" stop-color="#15351f"/><stop offset="100%" stop-color="{bg}"/></radialGradient>
        <filter id="glow"><feGaussianBlur stdDeviation="2.1" result="blur"/><feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
        <pattern id="grid" width="30" height="30" patternUnits="userSpaceOnUse"><path d="M 30 0 L 0 0 0 30" fill="none" stroke="#c7d9bf" stroke-opacity=".05" stroke-width="1"/></pattern>
      </defs>
      <rect width="820" height="590" rx="22" fill="url(#halo)"/>
      <rect width="820" height="590" rx="22" fill="url(#grid)"/>
      <circle cx="205" cy="270" r="180" fill="none" stroke="#c7d9bf" stroke-opacity=".08"/>
      <circle cx="535" cy="270" r="180" fill="none" stroke="#c7d9bf" stroke-opacity=".08"/>
      <text x="34" y="45" fill="#fff8cf" font-size="22" font-weight="900" letter-spacing="4">DIGITAL TWIN</text>
      <text x="34" y="72" fill="#b8c9aa" font-size="13" font-weight="700">{html.escape(title)} · carga muscular dinâmica</text>
      {base_person(front_x)}{front_zones(front_x)}
      {base_person(back_x, True)}{back_zones(back_x)}
      <g transform="translate(85,540)">
        <circle cx="0" cy="0" r="7" fill="#22c55e"/><text x="15" y="5" fill="#dbe9cf" font-size="12">Controlado</text>
        <circle cx="130" cy="0" r="7" fill="#d7b92f"/><text x="145" y="5" fill="#dbe9cf" font-size="12">Atenção</text>
        <circle cx="250" cy="0" r="7" fill="#f59e0b"/><text x="265" y="5" fill="#dbe9cf" font-size="12">Elevado</text>
        <circle cx="360" cy="0" r="7" fill="#ef4444"/><text x="375" y="5" fill="#dbe9cf" font-size="12">Crítico</text>
      </g>
    </svg>
    '''


def render_dynamic_twin(soldier: Dict[str, Any], loads: Dict[str, int]) -> None:
    sex = safe(soldier.get("sex"), "M")
    svg = twin_svg(loads, sex)
    st.markdown('<div class="twin-shell"><div class="twin-title"><h3>Mapa corporal de carga</h3><span>SVG dinâmico · por grupo muscular</span></div>', unsafe_allow_html=True)
    components.html(svg, height=710, scrolling=False)
    st.markdown('</div>', unsafe_allow_html=True)


def twin_page(profile: Dict[str, Any]) -> None:
    soldier = get_profile_soldier(profile)
    if not soldier:
        st.warning("Este utilizador ainda não tem soldier_id associado no perfil.")
        return
    loads = get_muscle_loads(str(soldier.get("soldier_id")))
    st.markdown(f'<div class="section-title">Digital Twin · {html.escape(safe(soldier.get("rank_code")))} {html.escape(safe(soldier.get("full_name")))}</div>', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    avg_load = int(round(sum(loads.values()) / max(1, len(loads))))
    top_group = max(loads, key=loads.get)
    with c1: metric_card("Prontidão", pct(soldier.get("readiness_score")), safe(soldier.get("readiness_status")))
    with c2: metric_card("Carga muscular", f"{avg_load}%", f"maior: {MUSCLE_LABELS.get(top_group, top_group)}")
    with c3: metric_card("Risco", "Baixo" if n(soldier.get("injury_risk")) < 35 else "Moderado" if n(soldier.get("injury_risk")) < 60 else "Elevado", pct(soldier.get("injury_risk")))
    with c4: metric_card("Recuperação", pct(soldier.get("recovery_score")), "sono / fadiga / carga")

    left, right = st.columns([1.18, .92])
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
        c1, c2, c3 = st.columns(3)
        with c1: duration = st.slider("Duração", 20, 90, 45)
        with c2: intensity = st.slider("Intensidade", 1, 10, 6)
        with c3: pace = st.selectbox("Zona de ritmo", ["Leve", "Moderada", "Forte"])
        params.update({"duration": duration, "intensity": intensity, "pace_zone": pace})
        focus = "Pernas"
    elif training_type == "Corrida intervalada":
        c1, c2, c3, c4 = st.columns(4)
        with c1: reps = st.slider("Repetições", 4, 12, 8)
        with c2: dist = st.selectbox("Distância", [200, 400, 800, 1000], index=1)
        with c3: rec = st.slider("Recuperação (s)", 30, 180, 90)
        with c4: intensity = st.slider("Intensidade", 1, 10, 8)
        duration = int(reps * (dist / 180 + rec / 60))
        params.update({"repetitions": reps, "distance_m": dist, "recovery_s": rec, "intensity": intensity})
        focus = "Pernas"
    elif training_type == "Marcha com carga":
        c1, c2, c3, c4 = st.columns(4)
        with c1: duration = st.slider("Duração", 30, 180, 90)
        with c2: load = st.slider("Carga externa (kg)", 5, 35, 18)
        with c3: terrain = st.selectbox("Terreno", ["Plano", "Misto", "Inclinado"])
        with c4: intensity = st.slider("Intensidade", 1, 10, 7)
        params.update({"duration": duration, "external_load_kg": load, "terrain": terrain, "intensity": intensity})
        focus = "Pernas/Core"
    elif training_type == "Circuito de força":
        c1, c2, c3 = st.columns(3)
        with c1: rounds = st.slider("Rondas", 2, 8, 4)
        with c2: intensity = st.slider("Intensidade", 1, 10, 7)
        with c3: focus = st.selectbox("Foco", ["Full body", "Superior", "Inferior", "Core"])
        duration = rounds * 12
        params.update({"rounds": rounds, "intensity": intensity, "focus": focus})
    elif training_type == "Treino técnico-tático":
        c1, c2, c3 = st.columns(3)
        with c1: duration = st.slider("Duração", 30, 180, 75)
        with c2: intensity = st.slider("Intensidade", 1, 10, 6)
        with c3: scenario = st.selectbox("Cenário", ["Patrulha", "Progressão", "Combate aproximado", "Reconhecimento"])
        params.update({"duration": duration, "intensity": intensity, "scenario": scenario})
        focus = "Operacional"
    else:
        c1, c2 = st.columns(2)
        with c1: duration = st.slider("Duração", 15, 60, 30)
        with c2: intensity = st.slider("Intensidade", 1, 5, 2)
        modality = st.selectbox("Modalidade", ["Bicicleta leve", "Mobilidade", "Caminhada", "Natação leve"])
        params.update({"duration": duration, "intensity": intensity, "modality": modality})
        focus = "Recuperação"
    return params, duration, intensity, focus


def accessible_groups(df: pd.DataFrame) -> Dict[str, pd.DataFrame]:
    groups = {"Todo o escalão acessível": df}
    if "platoon_name" in df:
        for name in sorted(df["platoon_name"].dropna().unique().tolist()):
            groups[f"Pelotão · {name}"] = df[df["platoon_name"] == name]
    if "section_name" in df:
        for name in sorted(df["section_name"].dropna().unique().tolist()):
            groups[f"Secção · {name}"] = df[df["section_name"] == name]
    return groups


def simulate_group_training(profile: Dict[str, Any]) -> None:
    st.markdown('<div class="section-title">Simulador de treino coletivo</div>', unsafe_allow_html=True)
    df = accessible_snapshot()
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
    c1, c2, c3, c4 = st.columns(4)
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


def simulate_individual_training(profile: Dict[str, Any]) -> None:
    soldier = get_profile_soldier(profile)
    if not soldier:
        st.warning("Perfil individual não encontrado.")
        return
    st.markdown('<div class="section-title">Simular treino individual</div>', unsafe_allow_html=True)
    training_type = st.selectbox("Tipo de treino", ["Corrida contínua", "Corrida intervalada", "Marcha com carga", "Circuito de força", "Treino técnico-tático", "Recuperação ativa"])
    params, duration, intensity, focus = training_parameters(training_type)
    impact = int(round(intensity * 2.1 + duration / 10))
    recovery_bonus = 10 if training_type == "Recuperação ativa" else 0
    base_ready = n(soldier.get("readiness_score"), 60)
    base_risk = n(soldier.get("injury_risk"), 35)
    predicted_readiness = max(0, min(100, base_ready - impact + recovery_bonus))
    predicted_risk = max(0, min(100, base_risk + int(impact * .75) - recovery_bonus))
    c1, c2, c3 = st.columns(3)
    with c1: metric_card("Prontidão atual", f"{base_ready}%", safe(soldier.get("readiness_status")))
    with c2: metric_card("Prontidão prevista", f"{predicted_readiness}%", "após treino")
    with c3: metric_card("Risco previsto", f"{predicted_risk}%", decision_for(predicted_readiness, predicted_risk))
    if st.button("Guardar simulação individual", use_container_width=True):
        try:
            sb_insert_many("training_simulations", [{
                "simulation_group_id": str(uuid.uuid4()),
                "soldier_id": soldier.get("soldier_id"),
                "created_by_profile_id": profile.get("id"),
                "training_type": training_type,
                "duration_min": duration,
                "intensity": intensity,
                "parameters": params,
                "predicted_readiness": predicted_readiness,
                "predicted_injury_risk": predicted_risk,
                "decision": decision_for(predicted_readiness, predicted_risk),
                "notes": f"Simulação individual; foco: {focus}",
            }])
            st.success("Simulação individual guardada.")
        except Exception as exc:
            st.error("Não foi possível guardar a simulação.")
            st.caption(str(exc))


def simulate_training(profile: Dict[str, Any]) -> None:
    if profile_role(profile) == "soldier":
        simulate_individual_training(profile)
    else:
        simulate_group_training(profile)

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

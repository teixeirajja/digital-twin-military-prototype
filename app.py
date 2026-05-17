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
    with m1: metric_card("Militares analisados", total, "dados da base Supabase")
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
            subtitle=f"{len(display_df)} militar(es) filtrados · dados da base Supabase",
            bar_columns={
                "readiness_score": "good",
                "injury_risk": "risk",
                "recovery_score": "good",
                "fatigue_score": "risk",
            },
        )


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

from __future__ import annotations

import math
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

/* Push the app below Streamlit Cloud's owner toolbar and hide Streamlit UI elements when possible */
.block-container {padding-top: 4.6rem; padding-bottom: 2rem;}
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
[data-testid="stToolbar"] {visibility: hidden; height: 0%; position: fixed;}
[data-testid="stDecoration"] {display: none;}
[data-testid="stStatusWidget"] {visibility: hidden;}
[data-testid="stHeader"] {display: none;}

.main-header {
    border-radius: 22px;
    padding: 26px 30px;
    background: linear-gradient(135deg, #07140c 0%, #174d28 52%, #2f8f3a 100%);
    color: white;
    margin-bottom: 22px;
    box-shadow: 0 16px 38px rgba(12, 66, 29, 0.20);
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 18px;
}
.header-left h1 {margin: 0; font-size: 2.05rem; letter-spacing: -0.03em;}
.header-left p {margin: 8px 0 0 0; color: rgba(255,255,255,0.86);}
.header-logout {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    min-width: 118px;
    padding: 10px 16px;
    border-radius: 14px;
    border: 1px solid rgba(255,255,255,0.42);
    color: white !important;
    text-decoration: none !important;
    font-weight: 800;
    background: rgba(255,255,255,0.10);
}
.header-logout:hover {background: rgba(255,255,255,0.18);}
.login-card {
    max-width: 460px;
    margin: 7vh auto 0 auto;
    padding: 28px;
    border-radius: 24px;
    background: white;
    box-shadow: 0 20px 60px rgba(0,0,0,0.11);
    border: 1px solid rgba(30, 64, 175, 0.08);
}
.metric-card {
    padding: 18px 18px;
    border-radius: 18px;
    background: #111827;
    color: white;
    box-shadow: 0 14px 26px rgba(15,23,42,0.13);
    min-height: 124px;
}
.metric-card small {color:#b8c5d6; font-size:0.78rem;}
.metric-card h2 {font-size:2.05rem; margin: 11px 0 4px 0;}
.metric-card p {margin:0; color:#dbe6f1; font-size:0.82rem;}
.soft-card {
    padding: 18px;
    border-radius: 18px;
    background: #fff;
    border: 1px solid #e5e7eb;
    box-shadow: 0 12px 28px rgba(15,23,42,0.06);
}
.status-pill {
    display:inline-block;
    padding:5px 11px;
    border-radius:999px;
    font-weight:700;
    font-size:0.78rem;
}
.pill-pronto {background:#dcfce7;color:#166534;}
.pill-atencao {background:#fef3c7;color:#92400e;}
.pill-risco {background:#fee2e2;color:#991b1b;}
.section-title {font-size: 1.22rem; font-weight: 800; margin: 8px 0 12px;}

.nav-card {
    padding: 12px 16px;
    margin: 0 0 18px 0;
    border-radius: 18px;
    background: #f8fafc;
    border: 1px solid #e5e7eb;
}
.footer-note {color:#6b7280;font-size:0.82rem;margin-top:16px;}

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
    st.markdown('<div class="login-card">', unsafe_allow_html=True)
    st.markdown("## 🛡️ Military Digital Twin")
    st.caption("Plataforma de monitorização, prontidão e simulação de treino militar.")

    with st.form("login_form"):
        email = st.text_input("Email", placeholder="cap.teixeira@militarytwin.pt")
        password = st.text_input("Password", type="password")
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

    st.divider()
    st.caption("Demo: cap.teixeira@militarytwin.pt / Cmd2026!  ·  hugo.dias@militarytwin.pt / Mil2026!")
    st.markdown('</div>', unsafe_allow_html=True)


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
        # O comandante não precisa de ver o digital twin individual; fica focado em decisão operacional.
        page_options = ["Dashboard", "Militar", "Simular treino"]
    elif role == "treinador":
        page_options = ["Dashboard", "Militar", "Digital Twin", "Simular treino"]

    st.markdown(f"""
    <div class="main-header">
        <div class="header-left">
            <h1>Military Digital Twin</h1>
            <p>{profile.get('rank','')} {profile.get('full_name','')} · {ROLE_LABELS.get(profile.get('role'), profile.get('role'))}</p>
        </div>
        <a class="header-logout" href="?logout=1" target="_self">Logout</a>
    </div>
    """, unsafe_allow_html=True)

    choice = st.radio("Navegação", page_options, horizontal=True, label_visibility="collapsed")
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
        fig.update_layout(height=480, legend_title_text="Estado")
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
        fig.update_layout(height=480)
        st.plotly_chart(fig, use_container_width=True)

    st.markdown('<div class="section-title">Tabela operacional</div>', unsafe_allow_html=True)
    cols = [c for c in ["rank", "full_name", "status", "readiness_score", "injury_risk", "recovery_score", "cooper_m", "fatigue_score", "sleep_hours"] if c in view.columns]
    if cols:
        sort_cols = [c for c in ["status", "readiness_score"] if c in view.columns]
        display_df = view[cols]
        if sort_cols:
            display_df = display_df.sort_values(sort_cols, ascending=[True, False][:len(sort_cols)])
        st.dataframe(display_df, use_container_width=True, hide_index=True)


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
        fig.update_layout(height=430, legend_title_text="Decisão")
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
        fig.update_layout(height=430)
        st.plotly_chart(fig, use_container_width=True)

    table_cols = ["rank", "full_name", "status", "Prontidão atual", "Prontidão prevista", "Risco atual", "Risco previsto", "Impacto", "Decisão"]
    st.dataframe(sim[table_cols].sort_values(["Decisão", "Prontidão prevista"]), use_container_width=True, hide_index=True)

    with st.expander("Resumo dos parâmetros simulados"):
        st.json({k: v for k, v in params.items() if k not in ["load_factor", "risk_factor"]})

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

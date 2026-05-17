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
.block-container {padding-top: 1.1rem; padding-bottom: 2rem;}
.main-header {
    border-radius: 22px;
    padding: 26px 30px;
    background: linear-gradient(135deg, #07140c 0%, #174d28 52%, #2f8f3a 100%);
    color: white;
    margin-bottom: 22px;
    box-shadow: 0 16px 38px rgba(12, 66, 29, 0.20);
}
.main-header h1 {margin: 0; font-size: 2.05rem; letter-spacing: -0.03em;}
.main-header p {margin: 8px 0 0 0; color: rgba(255,255,255,0.86);}
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

    ids = soldiers["id"].tolist()
    readiness = df_from("readiness_scores", order="score_date", desc=True, filters=[("soldier_id", "in", ids)])
    tests = df_from("physical_tests", order="test_date", desc=True, filters=[("soldier_id", "in", ids)])
    daily = df_from("daily_records", order="record_date", desc=True, filters=[("soldier_id", "in", ids)])

    readiness_l = latest_by(readiness, "soldier_id", "score_date") if not readiness.empty else pd.DataFrame()
    tests_l = latest_by(tests, "soldier_id", "test_date") if not tests.empty else pd.DataFrame()
    daily_l = latest_by(daily, "soldier_id", "record_date") if not daily.empty else pd.DataFrame()

    df = soldiers.rename(columns={"id": "soldier_id"})
    if not readiness_l.empty:
        df = df.merge(readiness_l.drop(columns=["id", "created_at"], errors="ignore"), on="soldier_id", how="left")
    if not tests_l.empty:
        df = df.merge(tests_l.drop(columns=["id", "created_at"], errors="ignore"), on="soldier_id", how="left")
    if not daily_l.empty:
        df = df.merge(daily_l.drop(columns=["id", "created_at"], errors="ignore"), on="soldier_id", how="left")

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
    c1, c2, c3 = st.columns([5, 2, 1])
    with c1:
        st.markdown(f"""
        <div class="main-header">
            <h1>Military Digital Twin</h1>
            <p>{profile.get('rank','')} {profile.get('full_name','')} · {ROLE_LABELS.get(profile.get('role'), profile.get('role'))}</p>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        page_options = ["Dashboard", "Militar", "Digital Twin", "Simular treino", "Admin"]
        role = profile.get("role")
        if role == "militar":
            page_options = ["Militar", "Digital Twin", "Simular treino"]
        elif role in ["comandante", "treinador"]:
            page_options = ["Dashboard", "Militar", "Digital Twin", "Simular treino"]
        choice = st.selectbox("Página", page_options, label_visibility="collapsed")
    with c3:
        if st.button("Logout", use_container_width=True):
            logout()
    return choice


def commander_dashboard(profile: Dict[str, Any]) -> None:
    st.markdown('<div class="section-title">Dashboard do comandante</div>', unsafe_allow_html=True)
    df = assemble_snapshot()
    if df.empty:
        st.warning("Ainda não há dados acessíveis para este utilizador.")
        return

    platoons = ["Todos"] + sorted([x for x in df.get("platoon_id", pd.Series(dtype=str)).dropna().unique().tolist()])
    states = ["Todos"] + STATUS_ORDER
    c1, c2, c3 = st.columns(3)
    with c1:
        state = st.selectbox("Estado", states)
    with c2:
        min_ready = st.slider("Prontidão mínima", 0, 100, 0)
    with c3:
        show_risk = st.checkbox("Mostrar só risco elevado", value=False)

    view = df.copy()
    if state != "Todos":
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
    g1, g2 = st.columns([1, 1])
    with g1:
        fig = px.bar(view.sort_values("readiness_score", ascending=True), x="readiness_score", y="full_name", color="status",
                     color_discrete_map={"Pronto": "#22c55e", "Atenção": "#f59e0b", "Risco": "#ef4444"},
                     labels={"readiness_score": "Prontidão", "full_name": "Militar"}, title="Prontidão por militar")
        fig.update_layout(height=480, legend_title_text="Estado")
        st.plotly_chart(fig, use_container_width=True)
    with g2:
        fig = px.scatter(view, x="readiness_score", y="injury_risk", size="recovery_score", color="status",
                         hover_name="full_name", color_discrete_map={"Pronto": "#22c55e", "Atenção": "#f59e0b", "Risco": "#ef4444"},
                         labels={"readiness_score": "Prontidão", "injury_risk": "Risco de lesão", "recovery_score": "Recuperação"},
                         title="Prontidão vs risco de lesão")
        fig.update_layout(height=480)
        st.plotly_chart(fig, use_container_width=True)

    st.markdown('<div class="section-title">Tabela operacional</div>', unsafe_allow_html=True)
    cols = [c for c in ["rank", "full_name", "status", "readiness_score", "injury_risk", "recovery_score", "cooper_m", "fatigue_score", "sleep_hours"] if c in view.columns]
    st.dataframe(view[cols].sort_values(["status", "readiness_score"], ascending=[True, False]), use_container_width=True, hide_index=True)


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


def simulate_training(profile: Dict[str, Any]) -> None:
    st.markdown('<div class="section-title">Simulador de treino</div>', unsafe_allow_html=True)
    all_soldiers = get_soldiers()
    if all_soldiers.empty:
        st.warning("Não há militares acessíveis.")
        return

    if profile.get("role") == "militar":
        own = get_soldier_for_profile(profile["id"])
        if not own:
            st.error("Este utilizador ainda não tem militar associado.")
            return
        soldier_id = own["id"]
        soldier_name = f"{own.get('rank','')} {own['full_name']}"
        st.info(f"Simulação para: {soldier_name}")
    else:
        name_map = {f"{row.get('rank','')} {row['full_name']}": row["id"] for _, row in all_soldiers.iterrows()}
        soldier_name = st.selectbox("Militar", list(name_map.keys()))
        soldier_id = name_map[soldier_name]

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

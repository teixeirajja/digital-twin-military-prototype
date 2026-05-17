import html
from datetime import date

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import streamlit.components.v1 as components

from utils.data_loader import build_latest_snapshot, load_data
from utils.metrics import add_scores, generate_recommendation, muscular_load_from_recent
from utils.simulator import TRAINING_BASE_LOAD, simulate_training
from utils.styles import inject_css, metric_card

st.set_page_config(
    page_title="Digital Twin Militar",
    page_icon="🟢",
    layout="wide",
    initial_sidebar_state="collapsed",
)

inject_css()


def topbar(user_label: str, role: str):
    st.markdown(
        f"""
        <div class="topbar">
            <div class="topbar-title">Digital Twin Militar</div>
            <div class="topbar-subtitle">Protótipo EITT · Utilizador: <b>{html.escape(user_label)}</b> · Perfil: <b>{html.escape(role)}</b></div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def gauge(title, value, suffix=""):
    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=value,
            number={"suffix": suffix},
            title={"text": title},
            gauge={
                "axis": {"range": [0, 100]},
                "bar": {"color": "#2E7D32"},
                "steps": [
                    {"range": [0, 55], "color": "#5A1E1E"},
                    {"range": [55, 75], "color": "#5D5120"},
                    {"range": [75, 100], "color": "#123B23"},
                ],
            },
        )
    )
    fig.update_layout(height=260, margin=dict(l=20, r=20, t=40, b=20))
    return fig


def risk_gauge(title, value, suffix=""):
    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=value,
            number={"suffix": suffix},
            title={"text": title},
            gauge={
                "axis": {"range": [0, 100]},
                "bar": {"color": "#C62828"},
                "steps": [
                    {"range": [0, 40], "color": "#123B23"},
                    {"range": [40, 65], "color": "#5D5120"},
                    {"range": [65, 100], "color": "#5A1E1E"},
                ],
            },
        )
    )
    fig.update_layout(height=260, margin=dict(l=20, r=20, t=40, b=20))
    return fig


def status_class(value):
    if value >= 75:
        return "status-good"
    if value >= 55:
        return "status-warning"
    return "status-risk"


def status_label(value):
    if value >= 75:
        return "Pronto"
    if value >= 55:
        return "Atenção"
    return "Risco"


def body_color(value):
    if value >= 70:
        return "#c0392b"
    if value >= 45:
        return "#f1c40f"
    return "#27ae60"


def render_digital_twin(muscle_load: dict, gender: str = "M"):
    trunk_label = "TOP + calções" if gender == "F" else "boxers"
    parts = {
        "head": 22,
        "shoulders": muscle_load.get("Peito/Ombros", 30),
        "chest": muscle_load.get("Peito/Ombros", 30),
        "back": muscle_load.get("Costas", 30),
        "core": muscle_load.get("Core/Lombar", 30),
        "quads": muscle_load.get("Quadríceps", 30),
        "posterior": muscle_load.get("Posterior", 30),
        "calves": muscle_load.get("Gémeos", 30),
    }
    html_block = f"""
    <style>
      .twin-wrap {{
        display:flex; gap:28px; align-items:center; justify-content:center;
        background:#111827; padding:22px; border-radius:22px; border:1px solid rgba(255,255,255,.08);
        font-family:Arial, sans-serif; color:#F5F5F5;
      }}
      .body {{ width:260px; height:520px; position:relative; }}
      .part {{ position:absolute; border-radius:999px; border:2px solid rgba(255,255,255,.28); box-shadow:0 10px 24px rgba(0,0,0,.25); }}
      .head {{ left:100px; top:10px; width:58px; height:58px; background:{body_color(parts['head'])}; }}
      .neck {{ left:113px; top:66px; width:32px; height:30px; background:#9ca3af; border-radius:10px; position:absolute; }}
      .torso {{ left:74px; top:90px; width:112px; height:154px; background:{body_color(parts['chest'])}; border-radius:40px 40px 28px 28px; }}
      .core {{ left:86px; top:190px; width:88px; height:92px; background:{body_color(parts['core'])}; border-radius:26px; opacity:.92; }}
      .left-arm {{ left:38px; top:104px; width:34px; height:168px; background:{body_color(parts['shoulders'])}; transform:rotate(8deg); }}
      .right-arm {{ right:38px; top:104px; width:34px; height:168px; background:{body_color(parts['shoulders'])}; transform:rotate(-8deg); }}
      .shorts {{ left:78px; top:258px; width:104px; height:52px; background:#1f2937; border-radius:18px; position:absolute; border:2px solid rgba(255,255,255,.30); display:flex; align-items:center; justify-content:center; font-size:11px; color:#d1d5db; text-align:center; padding:4px; }}
      .left-leg {{ left:82px; top:306px; width:42px; height:164px; background:{body_color(parts['quads'])}; }}
      .right-leg {{ left:138px; top:306px; width:42px; height:164px; background:{body_color(parts['posterior'])}; }}
      .left-calf {{ left:84px; top:438px; width:36px; height:78px; background:{body_color(parts['calves'])}; }}
      .right-calf {{ left:142px; top:438px; width:36px; height:78px; background:{body_color(parts['calves'])}; }}
      .legend {{ min-width:260px; }}
      .legend h3 {{ margin:0 0 10px 0; }}
      .legend-row {{ display:flex; justify-content:space-between; gap:18px; border-bottom:1px solid rgba(255,255,255,.09); padding:9px 0; }}
      .pill {{ border-radius:999px; padding:3px 10px; font-weight:bold; color:#111; }}
      .green {{ background:#27ae60; }} .yellow {{ background:#f1c40f; }} .red {{ background:#c0392b; color:#fff; }}
    </style>
    <div class="twin-wrap">
      <div class="body">
        <div class="part head"></div><div class="neck"></div>
        <div class="part torso"></div><div class="part core"></div>
        <div class="part left-arm"></div><div class="part right-arm"></div>
        <div class="shorts">{trunk_label}</div>
        <div class="part left-leg"></div><div class="part right-leg"></div>
        <div class="part left-calf"></div><div class="part right-calf"></div>
      </div>
      <div class="legend">
        <h3>Saturação muscular prevista</h3>
    """
    for muscle, value in muscle_load.items():
        cls = "red" if value >= 70 else "yellow" if value >= 45 else "green"
        html_block += f"<div class='legend-row'><span>{html.escape(muscle)}</span><span class='pill {cls}'>{int(value)}%</span></div>"
    html_block += """
        <p style="color:#9BA3AF; margin-top:14px; font-size:13px;">Protótipo visual: as cores representam zonas com maior carga acumulada, não diagnóstico médico.</p>
      </div>
    </div>
    """
    components.html(html_block, height=570, scrolling=False)


militares, registos, testes, lesoes = load_data()
snapshot = add_scores(build_latest_snapshot(militares, registos, testes))
snapshot["recomendacao"] = snapshot.apply(generate_recommendation, axis=1)

# Login visual simples
all_profiles = snapshot.copy()
all_profiles["label"] = all_profiles["posto"] + " " + all_profiles["nome"] + " · " + all_profiles["role"].str.capitalize()

login_col1, login_col2, login_col3 = st.columns([2.0, 2.0, 1.0])
with login_col1:
    selected_label = st.selectbox("Escolher perfil de demonstração", all_profiles["label"].tolist(), index=0)
selected_user = all_profiles[all_profiles["label"] == selected_label].iloc[0]
role = selected_user["role"]
user_label = f"{selected_user['posto']} {selected_user['nome']}"

with login_col2:
    st.selectbox("Ambiente", ["Protótipo local", "Servidor online / demo"], index=1)
with login_col3:
    st.button("Logout", use_container_width=True)

topbar(user_label, "Comandante" if role == "comandante" else "Militar")

soldiers = snapshot[snapshot["role"] == "militar"].copy()

if role == "comandante":
    st.subheader("Dashboard do comandante")
    f1, f2, f3, f4 = st.columns([1.3, 1.3, 1.3, 1])
    with f1:
        unidade = st.selectbox("Unidade", ["Todas"] + sorted(soldiers["unidade"].dropna().unique().tolist()))
    with f2:
        pelotao = st.selectbox("Pelotão", ["Todos"] + sorted(soldiers["pelotao"].dropna().unique().tolist()))
    with f3:
        estado = st.selectbox("Estado", ["Todos", "Pronto", "Atenção", "Risco"])
    with f4:
        st.date_input("Data", value=date.today())

    view = soldiers.copy()
    if unidade != "Todas":
        view = view[view["unidade"] == unidade]
    if pelotao != "Todos":
        view = view[view["pelotao"] == pelotao]
    if estado != "Todos":
        view = view[view["estado_twin"] == estado]

    ready = int((view["prontidao"] >= 75).sum())
    attention = int(((view["prontidao"] >= 55) & (view["prontidao"] < 75)).sum())
    risk = int((view["prontidao"] < 55).sum())

    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        metric_card("Militares analisados", len(view), "dados fictícios do MVP")
    with c2:
        metric_card("Prontos", ready, "prontidão ≥ 75")
    with c3:
        metric_card("Atenção", attention, "55 ≤ prontidão < 75")
    with c4:
        metric_card("Risco", risk, "prontidão < 55")
    with c5:
        metric_card("Prontidão média", f"{view['prontidao'].mean():.0f}%" if len(view) else "—", "média da unidade")

    st.divider()

    graph_col1, graph_col2 = st.columns([1.25, 1])
    with graph_col1:
        fig = px.bar(
            view.sort_values("prontidao"),
            x="prontidao",
            y="nome",
            orientation="h",
            color="estado_twin",
            title="Prontidão por militar",
            range_x=[0, 100],
            labels={"prontidao": "Prontidão (%)", "nome": "Militar", "estado_twin": "Estado"},
        )
        fig.update_layout(height=460, margin=dict(l=10, r=10, t=60, b=20))
        st.plotly_chart(fig, use_container_width=True)

    with graph_col2:
        fig2 = px.scatter(
            view,
            x="carga_treino_ua",
            y="fadiga",
            size="risco_lesao",
            color="nivel_risco",
            hover_name="nome",
            title="Carga, fadiga e risco de lesão",
            labels={"carga_treino_ua": "Carga treino (UA)", "fadiga": "Fadiga", "nivel_risco": "Risco"},
            range_y=[0, 10],
        )
        fig2.update_layout(height=460, margin=dict(l=10, r=10, t=60, b=20))
        st.plotly_chart(fig2, use_container_width=True)

    st.subheader("Tabela operacional")
    table_cols = [
        "posto", "nome", "pelotao", "funcao", "prontidao", "risco_lesao", "fadiga",
        "dor_muscular", "carga_treino_ua", "estado_twin", "recomendacao",
    ]
    st.dataframe(
        view[table_cols].sort_values(["estado_twin", "prontidao"]),
        use_container_width=True,
        hide_index=True,
        column_config={
            "prontidao": st.column_config.ProgressColumn("Prontidão", min_value=0, max_value=100),
            "risco_lesao": st.column_config.ProgressColumn("Risco lesão", min_value=0, max_value=100),
            "carga_treino_ua": st.column_config.NumberColumn("Carga UA"),
            "estado_twin": "Estado Twin",
            "recomendacao": "Recomendação",
        },
    )

    st.subheader("Alertas prioritários")
    alerts = view[(view["risco_lesao"] >= 60) | (view["prontidao"] < 60)].sort_values("risco_lesao", ascending=False)
    if alerts.empty:
        st.success("Sem alertas críticos neste momento.")
    else:
        for _, row in alerts.head(5).iterrows():
            st.warning(f"{row['posto']} {row['nome']} — risco {row['risco_lesao']}%, prontidão {row['prontidao']}%. {row['recomendacao']}")

else:
    # Perfil militar
    soldier = snapshot[snapshot["id"] == selected_user["id"]].iloc[0]
    soldier_id = soldier["id"]
    history = registos[registos["id"] == soldier_id].sort_values("data").copy()
    test_history = testes[testes["id"] == soldier_id].sort_values("data").copy()
    muscle_load = muscular_load_from_recent(registos, soldier_id)

    st.subheader(f"Área do militar · {soldier['posto']} {soldier['nome']}")
    tab_inicio, tab_progresso, tab_treino, tab_twin, tab_perfil = st.tabs(
        ["Início", "Progresso", "Treino", "Digital Twin", "Perfil"]
    )

    with tab_inicio:
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            metric_card("Prontidão", f"{soldier['prontidao']}%", status_label(soldier["prontidao"]))
        with c2:
            metric_card("Risco de lesão", f"{soldier['risco_lesao']}%", soldier["nivel_risco"])
        with c3:
            metric_card("Cooper", f"{int(soldier['cooper_m_teste'])} m", "último teste")
        with c4:
            metric_card("Carga diária", f"{int(soldier['carga_treino_ua'])} UA", "último registo")

        g1, g2 = st.columns(2)
        with g1:
            st.plotly_chart(gauge("Prontidão atual", int(soldier["prontidao"]), "%"), use_container_width=True)
        with g2:
            st.plotly_chart(risk_gauge("Risco de lesão", int(soldier["risco_lesao"]), "%"), use_container_width=True)

        st.info(f"Recomendação do sistema: {soldier['recomendacao']}")

    with tab_progresso:
        st.markdown("### Evolução recente")
        if not history.empty:
            fig = px.line(
                history,
                x="data",
                y=["carga_treino_ua", "fadiga", "dor_muscular"],
                markers=True,
                title="Carga, fadiga e dor muscular",
                labels={"value": "Valor", "data": "Data", "variable": "Métrica"},
            )
            fig.update_layout(height=430, margin=dict(l=10, r=10, t=60, b=20))
            st.plotly_chart(fig, use_container_width=True)

        if not test_history.empty:
            fig2 = px.line(
                test_history,
                x="data",
                y="cooper_m",
                markers=True,
                title="Evolução no teste de Cooper",
                labels={"cooper_m": "Distância Cooper (m)", "data": "Data"},
            )
            fig2.update_layout(height=390, margin=dict(l=10, r=10, t=60, b=20))
            st.plotly_chart(fig2, use_container_width=True)

        st.dataframe(history.tail(10), use_container_width=True, hide_index=True)

    with tab_treino:
        st.markdown("### Simulador de treino")
        st.caption("Objetivo: testar impacto provável de um treino antes da execução real.")

        s1, s2, s3 = st.columns(3)
        with s1:
            training_type = st.selectbox("Tipo de treino", list(TRAINING_BASE_LOAD.keys()))
        with s2:
            duration = st.slider("Duração (min)", min_value=10, max_value=120, value=45, step=5)
        with s3:
            intensity = st.slider("Intensidade percebida", min_value=1, max_value=10, value=6)

        result = simulate_training(
            int(soldier["prontidao"]),
            int(soldier["risco_lesao"]),
            training_type,
            duration,
            intensity,
            muscle_load,
        )

        r1, r2, r3 = st.columns(3)
        with r1:
            metric_card("Carga prevista", f"{result['session_load']}", "unidades arbitrárias")
        with r2:
            metric_card("Prontidão após treino", f"{result['readiness_after']}%", "estimativa")
        with r3:
            metric_card("Risco após treino", f"{result['risk_after']}%", "estimativa")

        if result["risk_after"] >= 70:
            st.error(result["warning"])
        elif result["readiness_after"] < 55:
            st.warning(result["warning"])
        else:
            st.success(result["warning"])

        before_after = pd.DataFrame(
            {
                "Métrica": ["Prontidão", "Risco de lesão"],
                "Antes": [soldier["prontidao"], soldier["risco_lesao"]],
                "Depois": [result["readiness_after"], result["risk_after"]],
            }
        )
        fig = go.Figure()
        fig.add_trace(go.Bar(name="Antes", x=before_after["Métrica"], y=before_after["Antes"]))
        fig.add_trace(go.Bar(name="Depois", x=before_after["Métrica"], y=before_after["Depois"]))
        fig.update_layout(barmode="group", height=360, yaxis_range=[0, 100], title="Impacto previsto do treino")
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("### Saturação muscular após simulação")
        render_digital_twin(result["muscle_load_after"], soldier["genero"])

    with tab_twin:
        st.markdown("### Digital Twin visual")
        st.caption("Representação simplificada para discussão com stakeholders. Não substitui avaliação médica ou fisiológica.")
        render_digital_twin(muscle_load, soldier["genero"])

    with tab_perfil:
        st.markdown("### Perfil e histórico")
        p1, p2 = st.columns(2)
        with p1:
            st.dataframe(
                pd.DataFrame(
                    [
                        ["Posto", soldier["posto"]],
                        ["Nome", soldier["nome"]],
                        ["Idade", soldier["idade"]],
                        ["Altura", f"{soldier['altura_cm']} cm"],
                        ["Peso", f"{soldier['peso_kg']} kg"],
                        ["Unidade", soldier["unidade"]],
                        ["Pelotão", soldier["pelotao"]],
                        ["Função", soldier["funcao"]],
                    ],
                    columns=["Campo", "Valor"],
                ),
                use_container_width=True,
                hide_index=True,
            )
        with p2:
            soldier_injuries = lesoes[lesoes["id"] == soldier_id]
            if soldier_injuries.empty:
                st.success("Sem lesões registadas.")
            else:
                st.dataframe(soldier_injuries, use_container_width=True, hide_index=True)

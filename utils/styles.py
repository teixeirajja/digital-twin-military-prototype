import streamlit as st


def inject_css():
    st.markdown(
        """
        <style>
        .block-container {
            padding-top: 1.2rem;
            padding-bottom: 2rem;
        }
        .topbar {
            background: linear-gradient(90deg, #132414 0%, #1F3B22 55%, #2E7D32 100%);
            padding: 16px 22px;
            border-radius: 18px;
            border: 1px solid rgba(255,255,255,0.10);
            margin-bottom: 18px;
        }
        .topbar-title {
            font-size: 28px;
            font-weight: 800;
            margin-bottom: 4px;
        }
        .topbar-subtitle {
            color: #D9EAD3;
            font-size: 14px;
        }
        .metric-card {
            background: #161B22;
            border: 1px solid rgba(255,255,255,0.08);
            border-radius: 18px;
            padding: 18px;
            min-height: 105px;
            box-shadow: 0 8px 20px rgba(0,0,0,0.15);
        }
        .metric-card .label {
            color: #9BA3AF;
            font-size: 13px;
            margin-bottom: 8px;
        }
        .metric-card .value {
            font-size: 30px;
            font-weight: 800;
        }
        .metric-card .hint {
            color: #C8D6C2;
            font-size: 12px;
            margin-top: 4px;
        }
        .status-good { color: #7CFC9A; font-weight: 700; }
        .status-warning { color: #FFD166; font-weight: 700; }
        .status-risk { color: #FF6B6B; font-weight: 700; }
        .small-muted { color: #9BA3AF; font-size: 13px; }
        </style>
        """,
        unsafe_allow_html=True,
    )


def metric_card(label, value, hint=""):
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="label">{label}</div>
            <div class="value">{value}</div>
            <div class="hint">{hint}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

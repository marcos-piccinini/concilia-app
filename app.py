import time
from io import BytesIO

import streamlit_authenticator as stauth
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import streamlit_authenticator as stauth

from auth import (
    feedback_completado_hoy,
    get_conciliaciones_hoy,
    get_users_for_auth,
    guardar_feedback,
    registrar_historial,
    registrar_nuevo_usuario_db,
)
from logic import procesar_conciliacion

# ── PAGE CONFIG ───────────────────────────────────────────────
st.set_page_config(
    page_title="Concilia · Conciliacion Bancaria Inteligente",
    page_icon="logo.jpg",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── DESIGN TOKENS (LIGHT THEME) ───────────────────────────────
PRIMARY   = "#4f46e5"  # Indigo 600
PRIMARY2  = "#7c3aed"  # Violet 600
SUCCESS   = "#10b981"
WARNING   = "#f59e0b"
DANGER    = "#ef4444"
BG        = "#f8fafc"  # Slate 50
BG2       = "#f1f5f9"  # Slate 100
CARD      = "#ffffff"  # White
BORDER    = "#e2e8f0"  # Slate 200
TEXT      = "#0f172a"  # Slate 900
MUTED     = "#64748b"  # Slate 500

# ── GLOBAL CSS ────────────────────────────────────────────────
st.markdown(f"""
<style>
/* ─ Fonts ─────────────────────────────────────────────── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
html, body, [class*="css"] {{ font-family: 'Inter', sans-serif !important; }}

/* ─ App background ─────────────────────────────────────── */
.stApp {{ background: {BG} !important; color: {TEXT}; }}

/* ─ Hide Streamlit chrome ──────────────────────────────── */
#MainMenu, footer, header {{ visibility: hidden; }}

/* ─ Logo Circular ──────────────────────────────────────── */
[data-testid="stImage"] img {{
    border-radius: 50% !important;
    object-fit: cover !important;
    border: 2px solid {BORDER} !important;
    box-shadow: 0 4px 12px rgba(0,0,0,0.05) !important;
}}

/* ─ Sidebar ────────────────────────────────────────────── */
[data-testid="stSidebar"] {{
    background: {BG2} !important;
    border-right: 1px solid {BORDER} !important;
}}
[data-testid="stSidebar"] * {{ color: {TEXT} !important; }}

/* ─ File uploader ──────────────────────────────────────── */
[data-testid="stFileUploaderDropzone"] {{
    background: {CARD} !important;
    border: 2px dashed {BORDER} !important;
    border-radius: 12px !important;
    transition: border-color 0.2s ease !important;
}}
[data-testid="stFileUploaderDropzone"]:hover {{
    border-color: {PRIMARY}80 !important;
    background: {BG2} !important;
}}

/* ─ Selectbox, Text inputs, Textarea ───────────────────── */
[data-baseweb="select"] > div, [data-baseweb="input"] > div, textarea {{
    background: {CARD} !important;
    border-color: {BORDER} !important;
    border-radius: 8px !important;
    color: {TEXT} !important;
}}
input {{ color: {TEXT} !important; }}

/* ─ Slider & Progress bar ──────────────────────────────── */
[data-testid="stSlider"] [data-baseweb="slider"] div[role="slider"] {{
    background: {PRIMARY} !important;
    border-color: {PRIMARY} !important;
}}
[data-testid="stSlider"] div[class*="Track"] div:first-child,
[data-testid="stProgressBar"] > div > div {{
    background: linear-gradient(90deg, {PRIMARY} 0%, {PRIMARY2} 100%) !important;
    border-radius: 99px !important;
}}
[data-testid="stProgressBar"] > div {{
    background: {BORDER} !important;
    border-radius: 99px !important;
}}

/* ─ Tabs ───────────────────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {{
    background: {CARD};
    border-radius: 10px;
    padding: 4px;
    gap: 4px;
    border: 1px solid {BORDER};
}}
.stTabs [data-baseweb="tab"] {{
    border-radius: 7px !important;
    color: {MUTED} !important;
    font-weight: 500 !important;
    padding: 6px 16px !important;
}}
.stTabs [aria-selected="true"] {{
    background: linear-gradient(135deg, {PRIMARY} 0%, {PRIMARY2} 100%) !important;
    color: #ffffff !important;
}}

/* ─ Dataframe & Expander ───────────────────────────────── */
[data-testid="stDataFrame"], [data-testid="stExpander"] {{
    border: 1px solid {BORDER} !important;
    border-radius: 10px !important;
    background: {CARD} !important;
    overflow: hidden !important;
}}

/* ─ Divider & Alerts ───────────────────────────────────── */
hr {{ border-color: {BORDER} !important; margin: 1.5rem 0 !important; }}
[data-testid="stAlert"] {{ border-radius: 10px !important; }}

/* ─ Custom components ──────────────────────────────────── */
.sidebar-divider {{
    border-top: 1px solid {BORDER};
    margin: 12px 0;
}}
.sidebar-label {{
    font-size: 11px; font-weight: 600; color: {MUTED};
    text-transform: uppercase; letter-spacing: 0.08em;
    margin-bottom: 4px;
}}
.sidebar-value {{
    font-size: 14px; font-weight: 500; color: {TEXT};
}}
.page-title {{
    font-size: 1.8rem; font-weight: 700; color: {TEXT};
    line-height: 1.2; margin-bottom: 4px;
}}
.page-subtitle {{
    font-size: 0.9rem; color: {MUTED}; margin-bottom: 1.5rem;
}}
.section-label {{
    font-size: 0.85rem; font-weight: 600; color: {TEXT};
    text-transform: uppercase; letter-spacing: 0.06em; margin-bottom: 6px;
}}
.metric-card {{
    background: {CARD}; border: 1px solid {BORDER};
    border-radius: 12px; padding: 18px 20px; text-align: center;
    box-shadow: 0 2px 8px rgba(0,0,0,0.02);
}}
.metric-val {{
    font-size: 2.2rem; font-weight: 700; line-height: 1; margin-bottom: 4px;
}}
.metric-lbl {{
    font-size: 0.75rem; font-weight: 600; color: {MUTED};
    text-transform: uppercase; letter-spacing: 0.07em;
}}
.upload-hint {{
    background: {CARD}; border: 1px dashed {BORDER};
    border-radius: 12px; padding: 24px; text-align: center; margin-top: 8px;
}}
.survey-wrap {{
    background: linear-gradient(135deg, {CARD} 0%, {BG2} 100%);
    border: 1px solid {PRIMARY}30;
    border-radius: 16px; padding: 32px 36px; margin: 24px 0;
    box-shadow: 0 4px 16px rgba(0,0,0,0.04);
}}
.survey-badge {{
    display: inline-flex; align-items: center; gap: 6px;
    background: {PRIMARY}10; border: 1px solid {PRIMARY}30;
    border-radius: 20px; padding: 5px 14px;
    font-size: 0.82rem; color: {PRIMARY}; font-weight: 600;
    margin-bottom: 14px;
}}
.survey-title {{
    font-size: 1.25rem; font-weight: 600; color: {TEXT}; margin-bottom: 2px;
}}
.survey-sub {{
    font-size: 0.88rem; color: {MUTED}; margin-bottom: 24px;
}}
.limit-card {{
    background: #fffbeb; border: 1px solid #fcd34d;
    border-radius: 14px; padding: 28px; text-align: center; margin: 20px 0;
}}
.progress-label {{
    font-size: 0.88rem; color: {MUTED}; margin-bottom: 6px;
}}
[data-testid="stImage"] {{
    display: flex !important;
    justify-content: center !important;
    width: 100% !important;
    margin: 0 auto !important;
}}
label p, .st-form label p {{
    color: #0f172a !important;
    font-weight: 600 !important;
}}
input::placeholder {{
    color: #94a3b8 !important;
}}

/* Fix definitivo para hacer visibles TODOS los botones y sus textos (incluido el Login) */
.stButton > button, 
[data-testid="stForm"] button,
[data-testid="baseButton-secondary"],
[data-testid="baseButton-primary"] {{
    background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%) !important;
    border: none !important;
    border-radius: 8px !important;
}}

.stButton > button p, 
[data-testid="stForm"] button p,
.stButton > button div, 
[data-testid="stForm"] button div {{
    color: #ffffff !important;
    font-weight: 600 !important;
    text-shadow: none !important;
}}
</style>
""", unsafe_allow_html=True)

# ── HELPERS ───────────────────────────────────────────────────

RATING_LABELS = ["", "Muy mala", "Mala", "Regular", "Por debajo del promedio",
                 "Promedio", "Buena", "Muy buena", "Excelente", "Sobresaliente", "Perfecta"]

def rating_display(val: int) -> str:
    return f"Puntuacion: {val}/10 — {RATING_LABELS[val]}"

def get_index(cols, keywords):
    for i, c in enumerate(cols):
        if any(k in str(c).lower() for k in keywords):
            return i
    return 0

def plotly_light_layout(title: str, height: int = 300) -> dict:
    return dict(
        title=dict(text=title, font=dict(color=TEXT, size=13), x=0),
        paper_bgcolor=CARD,
        plot_bgcolor=CARD,
        font=dict(color=TEXT, family="Inter, sans-serif"),
        legend=dict(font=dict(color=MUTED), bgcolor=CARD),
        margin=dict(t=44, b=16, l=16, r=16),
        height=height,
    )

# ── AUTH SETUP ────────────────────────────────────────────────
credentials = get_users_for_auth()
if credentials is None:
    st.error("No se pudo conectar a la base de datos.")
    st.stop()

authenticator = stauth.Authenticate(
    credentials,
    "concilia_session_v3",
    "signature_key_secreta",
    cookie_expiry_days=30,
)

# ── LOGIN & REGISTRO ──────────────────────────────────────────
if not st.session_state.get("authentication_status"):
    _l, center, _r = st.columns([1, 1, 1])
    with center:
        st.markdown('<div style="padding: 40px 0 24px 0; text-align:center;">', unsafe_allow_html=True)
        st.image("logo.jpg", width=180)
        st.markdown('</div>', unsafe_allow_html=True)

        tab_login, tab_registro = st.tabs(["Iniciar Sesion", "Crear Cuenta"])

        with tab_login:
            try:
                authenticator.login()
            except Exception as e:
                st.error(f"Error en autenticacion: {e}")

            if st.session_state.get("authentication_status") is False:
                st.error("Usuario o contrasena incorrectos. Volve a intentarlo.")

        with tab_registro:
            with st.form("registro_form"):
                st.subheader("Nueva Cuenta")
                new_user = st.text_input("Username", placeholder="ej: santi").strip().lower()
                new_name = st.text_input("Nombre Completo", placeholder="ej: Santino Domeniconi").strip()
                new_email = st.text_input("Email (@gmail.com)", placeholder="ej: santi@gmail.com").strip().lower()
                new_pwd = st.text_input("Contrasena", type="password", placeholder="Escribi tu contrasena").strip()
                submit_reg = st.form_submit_button("Registrarse")

                if submit_reg:
                    if not new_user or not new_name or not new_email or not new_pwd:
                        st.error("Todos los campos son obligatorios.")
                    elif not new_email.endswith("@gmail.com"):
                        st.error("El correo electronico debe ser @gmail.com.")
                    else:
                        success, msg = registrar_nuevo_usuario_db(new_user, new_name, new_pwd, new_email)
                        if success:
                            st.success(msg + " Ya podes iniciar sesion en la otra pestana.")
                        else:
                            st.error(msg)

    st.stop()

# ── MAIN APP (autenticado) ────────────────────────────────────
username: str = st.session_state["username"]
name: str     = st.session_state["name"]

# ── SIDEBAR ───────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div style="text-align: center; padding: 10px 0;">', unsafe_allow_html=True)
    st.image("logo.jpg", width=120)
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="sidebar-divider"></div>', unsafe_allow_html=True)

    # User info
    st.markdown(f"""
    <div class="sidebar-label">Sesion activa</div>
    <div class="sidebar-value">{name}</div>
    <div style="font-size:12px;color:{MUTED};margin-bottom:12px;">@{username}</div>
    <div class="sidebar-divider"></div>
    """, unsafe_allow_html=True)

    # Daily usage
    conc_hoy   = get_conciliaciones_hoy(username)
    survey_ok  = feedback_completado_hoy(username)
    limite     = 2 if survey_ok else 1
    usadas     = min(conc_hoy, limite)

    st.markdown(f"""
    <div class="sidebar-label" style="margin-top:4px;">Uso de hoy</div>
    <div class="sidebar-value" style="margin-bottom:8px;">{usadas} de {limite} conciliaciones</div>
    """, unsafe_allow_html=True)
    st.progress(usadas / limite)

    if not survey_ok:
        st.markdown(f"""
        <div style="background:{PRIMARY}10;border:1px solid {PRIMARY}30;border-radius:8px;
                    padding:10px 12px;margin-top:10px;font-size:12px;color:{PRIMARY};font-weight:500;">
            Completá la encuesta post-conciliacion y desbloqueá una conciliacion extra hoy
        </div>
        """, unsafe_allow_html=True)

    st.markdown(f'<div class="sidebar-divider" style="margin-top:14px;"></div>', unsafe_allow_html=True)
    authenticator.logout("Cerrar sesion")

# ── HEADER ────────────────────────────────────────────────────
st.markdown("""
<div class="page-title">Conciliacion Bancaria</div>
<div class="page-subtitle">Detectá automaticamente coincidencias entre tu extracto bancario y tu registro contable</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# VISTA RESULTADOS
# ══════════════════════════════════════════════════════════════
if "r_coin" in st.session_state:
    coincidencias = st.session_state["r_coin"]
    solo_banco    = st.session_state["r_banco"]
    solo_contable = st.session_state["r_conta"]
    col_b         = st.session_state.get("r_col_b", "")
    col_c         = st.session_state.get("r_col_c", "")

    total  = len(coincidencias) + len(solo_banco) + len(solo_contable)
    pct_ok = (len(coincidencias) / total * 100) if total else 0.0

    if st.session_state.get("show_survey"):
        st.markdown(f"""
        <div style="background:{PRIMARY}10;border:1px solid {PRIMARY}30;border-radius:10px;
                    padding:10px 16px;margin-bottom:16px;font-size:13px;color:{PRIMARY};
                    display:flex;align-items:center;gap:8px;font-weight:500;">
            <span>Tu encuesta está al pie de esta página — completala y desbloqueás una conciliacion extra hoy</span>
        </div>
        """, unsafe_allow_html=True)

    # ── Metricas ──────────────────────────────────────────
    st.markdown('<div class="page-title" style="font-size:1.3rem;">Resultados</div>', unsafe_allow_html=True)
    st.write("")

    m1, m2, m3, m4 = st.columns(4, gap="medium")
    for _col, val, label, color in [
        (m1, len(coincidencias), "Coincidencias", PRIMARY),
        (m2, len(solo_banco),    "Solo Banco",    WARNING),
        (m3, len(solo_contable), "Solo Contable", DANGER),
        (m4, f"{pct_ok:.1f}%",   "Tasa match",   SUCCESS),
    ]:
        with _col:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-val" style="color:{color};">{val}</div>
                <div class="metric-lbl">{label}</div>
            </div>
            """, unsafe_allow_html=True)

    st.write("")

    # ── Graficos ──────────────────────────────────────────
    ch1, ch2 = st.columns(2, gap="medium")

    with ch1:
        fig_pie = go.Figure(data=[go.Pie(
            labels=["Coincidencias", "Solo Banco", "Solo Contable"],
            values=[len(coincidencias), len(solo_banco), len(solo_contable)],
            hole=0.62,
            marker=dict(colors=[PRIMARY, WARNING, DANGER], line=dict(color=CARD, width=2)),
            textinfo="label+percent",
            textfont=dict(color=TEXT, size=11),
            hovertemplate="%{label}: %{value} registros<extra></extra>",
        )])
        fig_pie.update_layout(**plotly_light_layout("Distribucion de registros"))
        st.plotly_chart(fig_pie, use_container_width=True, config={"displayModeBar": False})

    with ch2:
        try:
            def _sum(df, col):
                if df.empty or col not in df.columns:
                    return 0.0
                return pd.to_numeric(df[col], errors="coerce").abs().sum()

            fig_bar = go.Figure(data=[go.Bar(
                x=["Coincidencias", "Solo Banco", "Solo Contable"],
                y=[_sum(coincidencias, f"{col_b}_banco"), _sum(solo_banco, col_b), _sum(solo_contable, col_c)],
                marker_color=[PRIMARY, WARNING, DANGER],
                text=[f"${v:,.0f}" for v in [_sum(coincidencias, f"{col_b}_banco"), _sum(solo_banco, col_b), _sum(solo_contable, col_c)]],
                textposition="outside",
                textfont=dict(color=TEXT, size=11),
                hovertemplate="%{x}: $%{y:,.2f}<extra></extra>",
            )])
            layout = plotly_light_layout("Montos por categoria")
            layout.update(dict(
                xaxis=dict(showgrid=False, tickfont=dict(color=MUTED)),
                yaxis=dict(showgrid=True, gridcolor=BORDER, tickfont=dict(color=MUTED), zeroline=False),
                showlegend=False,
            ))
            fig_bar.update_layout(**layout)
            st.plotly_chart(fig_bar, use_container_width=True, config={"displayModeBar": False})
        except Exception:
            st.info("Grafico de montos no disponible para estas columnas.")

    st.divider()

    # ── Tabs de datos ─────────────────────────────────────
    tab1, tab2, tab3 = st.tabs([
        f"Coincidencias ({len(coincidencias)})",
        f"Solo Banco ({len(solo_banco)})",
        f"Solo Contable ({len(solo_contable)})",
    ])
    with tab1:
        if coincidencias.empty:
            st.info("No se encontraron coincidencias entre los archivos.")
        else:
            st.dataframe(coincidencias, use_container_width=True, height=420)
    with tab2:
        if solo_banco.empty:
            st.success("Todos los registros del banco tienen coincidencia contable.")
        else:
            st.dataframe(solo_banco, use_container_width=True, height=420)
    with tab3:
        if solo_contable.empty:
            st.success("Todos los registros contables tienen coincidencia bancaria.")
        else:
            st.dataframe(solo_contable, use_container_width=True, height=420)

    # ── Descarga ──────────────────────────────────────────
    st.divider()
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        (coincidencias if not coincidencias.empty else pd.DataFrame({"Mensaje": ["Sin datos"]})).to_excel(
            writer, index=False, sheet_name="Coincidencias")
        (solo_banco if not solo_banco.empty else pd.DataFrame({"Mensaje": ["Sin datos"]})).to_excel(
            writer, index=False, sheet_name="Solo Banco")
        (solo_contable if not solo_contable.empty else pd.DataFrame({"Mensaje": ["Sin datos"]})).to_excel(
            writer, index=False, sheet_name="Solo Contable")
    st.download_button(
        label="Descargar Reporte Excel",
        data=output.getvalue(),
        file_name="reporte_conciliacion.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        type="primary",
        use_container_width=True,
    )

    st.divider()

    # ── Encuesta ──────────────────────────────────────────
    if st.session_state.get("show_survey"):
        st.markdown(f"""
        <div class="survey-wrap">
            <div class="survey-badge">Completá la encuesta · Desbloqueás +1 conciliacion hoy</div>
            <div class="survey-title">¿Cómo fue tu experiencia?</div>
            <div class="survey-sub">Tu feedback nos ayuda a mejorar Concilia. Tardás menos de 30 segundos.</div>
        </div>
        """, unsafe_allow_html=True)

        r_ui = st.slider("Interfaz y experiencia de uso", 1, 10, 7, key="s_ui",
                         help="¿Qué tan fácil e intuitiva te resultó la interfaz?")
        st.caption(rating_display(r_ui))
        st.write("")

        r_res = st.slider("Precision y utilidad de los resultados", 1, 10, 7, key="s_res",
                          help="¿Los resultados reflejan correctamente tu conciliacion?")
        st.caption(rating_display(r_res))
        st.write("")

        comentario = st.text_area(
            "Comentarios adicionales (opcional)",
            placeholder="¿Qué mejorarías? ¿Qué te resultó más útil? ¿Encontraste algún problema?",
            key="s_comment",
        )

        btn1, btn2 = st.columns([4, 1])
        with btn1:
            if st.button("Enviar y desbloquear conciliacion extra", type="primary",
                         use_container_width=True, key="btn_enviar"):
                guardar_feedback(username, r_ui, r_res, comentario)
                st.session_state["show_survey"] = False
                st.rerun()
        with btn2:
            if st.button("Saltar", use_container_width=True, key="btn_saltar"):
                st.session_state["show_survey"] = False
                st.rerun()

    # ── Accion post-encuesta ──────────────────────────────
    else:
        conc_hoy  = get_conciliaciones_hoy(username)
        survey_ok = feedback_completado_hoy(username)
        limite    = 2 if survey_ok else 1

        if conc_hoy < limite:
            st.markdown(f"""
            <div style="background:{CARD};border:1px solid {BORDER};border-radius:12px;
                        padding:20px 24px;display:flex;align-items:center;justify-content:space-between;gap:16px;">
                <div>
                    <div style="font-size:14px;font-weight:600;color:{TEXT};margin-bottom:2px;">
                        ¿Querés conciliar otro archivo?
                    </div>
                    <div style="font-size:12px;color:{MUTED};">
                        Tenés {limite - conc_hoy} conciliacion{'es' if limite - conc_hoy > 1 else ''} disponible{'s' if limite - conc_hoy > 1 else ''} hoy
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            st.write("")
            if st.button("Nueva Conciliacion", type="primary", use_container_width=True, key="btn_nueva"):
                for k in ["r_coin", "r_banco", "r_conta", "r_col_b", "r_col_c", "show_survey"]:
                    st.session_state.pop(k, None)
                st.rerun()
        else:
            st.markdown(f"""
            <div class="limit-card">
                <div style="font-size:1rem;font-weight:600;color:#92400e;margin-bottom:4px;">Limite diario alcanzado</div>
                <div style="font-size:0.85rem;color:#b45309;">Usaste tus {limite} conciliaciones de hoy. Volvé mañana.</div>
            </div>
            """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# VISTA UPLOAD
# ══════════════════════════════════════════════════════════════
else:
    conc_hoy  = get_conciliaciones_hoy(username)
    survey_ok = feedback_completado_hoy(username)
    limite    = 2 if survey_ok else 1

    if conc_hoy >= limite:
        st.markdown(f"""
        <div class="limit-card">
            <div style="font-size:1.1rem;font-weight:600;color:#92400e;margin-bottom:6px;">
                Limite diario alcanzado
            </div>
            <div style="font-size:0.88rem;color:#b45309;">
                Usaste tus {limite} conciliaciones de hoy. Volvé mañana para continuar.
            </div>
        </div>
        """, unsafe_allow_html=True)

    else:
        # ── Carga de archivos ─────────────────────────────
        col1, col2 = st.columns(2, gap="large")
        with col1:
            st.markdown('<div class="section-label">Extracto Bancario</div>', unsafe_allow_html=True)
            file_banco = st.file_uploader(
                "Extracto bancario", type=["csv", "xlsx"],
                label_visibility="collapsed", key="file_banco",
            )
        with col2:
            st.markdown('<div class="section-label">Registro Contable</div>', unsafe_allow_html=True)
            file_contable = st.file_uploader(
                "Registro contable", type=["csv", "xlsx"],
                label_visibility="collapsed", key="file_contable",
            )

        if file_banco is None or file_contable is None:
            st.markdown(f"""
            <div class="upload-hint">
                <div style="color:{MUTED};font-size:0.88rem;font-weight:500;">
                    Subí ambos archivos (CSV o Excel) para comenzar el mapeo y la conciliacion
                </div>
            </div>
            """, unsafe_allow_html=True)

        else:
            # ── Lectura de archivos ───────────────────────
            try:
                df_banco    = pd.read_csv(file_banco)    if file_banco.name.endswith(".csv")    else pd.read_excel(file_banco)
                df_contable = pd.read_csv(file_contable) if file_contable.name.endswith(".csv") else pd.read_excel(file_contable)
            except Exception as e:
                st.error(f"No se pudo leer uno de los archivos: {e}")
                st.stop()

            # ── Mapeo de columnas ─────────────────────────
            st.divider()
            st.markdown('<div class="section-label">Mapeo de Columnas</div>', unsafe_allow_html=True)
            st.caption("Verificá que cada selector apunta a la columna correcta de tu archivo")

            map1, map2 = st.columns(2, gap="large")
            with map1:
                st.markdown(f"<div style='font-size:13px;font-weight:600;color:{TEXT};margin-bottom:8px;'>Extracto Bancario</div>", unsafe_allow_html=True)
                banco_cols      = df_banco.columns.tolist()
                col_monto_banco = st.selectbox("Monto",       banco_cols, index=get_index(banco_cols, ["importe","monto","valor","suma","total"]),        key="monto_b")
                col_fecha_banco = st.selectbox("Fecha",       banco_cols, index=get_index(banco_cols, ["fecha","date","dia"]),                       key="fecha_b")
                col_desc_banco  = st.selectbox("Descripcion", banco_cols, index=get_index(banco_cols, ["descripcion","detalle","concepto"]), key="desc_b")
            with map2:
                st.markdown(f"<div style='font-size:13px;font-weight:600;color:{TEXT};margin-bottom:8px;'>Registro Contable</div>", unsafe_allow_html=True)
                conta_cols      = df_contable.columns.tolist()
                col_monto_conta = st.selectbox("Monto",       conta_cols, index=get_index(conta_cols, ["importe","monto","valor","suma","total"]),        key="monto_l")
                col_fecha_conta = st.selectbox("Fecha",       conta_cols, index=get_index(conta_cols, ["fecha","date","dia"]),                       key="fecha_l")
                col_desc_conta  = st.selectbox("Descripcion", conta_cols, index=get_index(conta_cols, ["descripcion","detalle","concepto"]), key="desc_l")

            with st.expander("Vista previa de los archivos cargados"):
                vp1, vp2 = st.columns(2)
                with vp1:
                    st.caption("Extracto Bancario — primeras filas")
                    st.dataframe(df_banco.head(), use_container_width=True)
                with vp2:
                    st.caption("Registro Contable — primeras filas")
                    st.dataframe(df_contable.head(), use_container_width=True)

            st.divider()

            # ── Boton procesar ────────────────────────────
            if st.button("Procesar Conciliacion", type="primary", use_container_width=True):
                prog_bar  = st.progress(0)
                prog_text = st.empty()

                def step(pct: int, msg: str):
                    prog_bar.progress(pct)
                    prog_text.markdown(f'<div class="progress-label">{msg}</div>', unsafe_allow_html=True)

                step(10, "Limpiando y normalizando datos...")
                time.sleep(0.35)
                step(35, "Buscando coincidencias exactas por monto...")
                time.sleep(0.2)

                coincidencias, solo_banco, solo_contable = procesar_conciliacion(
                    df_banco, df_contable,
                    col_fecha_banco, col_monto_banco, col_desc_banco,
                    col_fecha_conta, col_monto_conta, col_desc_conta,
                )

                step(72, "Aplicando algoritmo de fuzzy matching...")
                time.sleep(0.3)
                step(90, "Calculando estadisticas y generando reporte...")
                time.sleep(0.25)
                step(100, "Conciliacion completada exitosamente.")
                time.sleep(0.55)

                prog_bar.empty()
                prog_text.empty()

                registrar_historial(username, len(coincidencias), len(solo_banco), len(solo_contable))

                st.session_state["r_coin"]       = coincidencias
                st.session_state["r_banco"]      = solo_banco
                st.session_state["r_conta"]      = solo_contable
                st.session_state["r_col_b"]      = col_monto_banco
                st.session_state["r_col_c"]      = col_monto_conta
                st.session_state["show_survey"]  = not feedback_completado_hoy(username)

                st.rerun()
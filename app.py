import streamlit as st
import pandas as pd
import streamlit_authenticator as stauth
from logic import procesar_conciliacion
from auth import get_users_for_auth, registrar_historial
from io import BytesIO

st.set_page_config(page_title="Concilia v1.0", layout="wide")

# -- LÓGICA DE AUTENTICACIÓN --
credentials = get_users_for_auth()

if credentials is None:
    st.error("No se pudo conectar a la base de datos local o no se ha inicializado. Por favor, ejecuta 'python db_setup.py'.")
    st.stop()

authenticator = stauth.Authenticate(
    credentials,
    "concilia_session",
    "signature_key_secreta",
    cookie_expiry_days=30
)

# Renderizar formulario de login
try:
    authenticator.login()
except Exception as e:
    st.error(f"Error en el sistema de autenticación: {e}")

if st.session_state.get('authentication_status'):
    # -- APLICACIÓN PRINCIPAL (Usuario Logueado) --
    with st.sidebar:
        st.write(f'Bienvenido/a **{st.session_state["name"]}**')
        authenticator.logout('Cerrar Sesión')
        
    st.title("Concilia v1.0")
    st.write("Sube tus archivos para realizar la conciliación:")
    
    col1, col2 = st.columns(2)
    
    with col1:
        file_banco = st.file_uploader("Sube el extracto bancario", type=["csv", "xlsx"])
    
    with col2:
        file_contable = st.file_uploader("Sube el registro contable", type=["csv", "xlsx"])
    
    if file_banco is None or file_contable is None:
        st.warning("⚠️ Por favor, sube ambos archivos (Extracto Bancario y Registro Contable) para comenzar el mapeo y la conciliación.")
    else:
        try:
            if file_banco.name.endswith('.csv'):
                df_banco = pd.read_csv(file_banco)
            else:
                df_banco = pd.read_excel(file_banco)
                
            if file_contable.name.endswith('.csv'):
                df_contable = pd.read_csv(file_contable)
            else:
                df_contable = pd.read_excel(file_contable)
                
            def get_index(cols, keywords):
                for i, c in enumerate(cols):
                    if any(k in str(c).lower() for k in keywords):
                        return i
                return None
                
            st.divider()
            st.subheader("Mapeo Dinámico de Columnas")
            st.write("Verifica y selecciona qué columna corresponde a cada dato en los archivos subidos:")
            
            map_col1, map_col2 = st.columns(2)
            
            with map_col1:
                st.markdown("#### Extracto Bancario")
                banco_cols = df_banco.columns.tolist()
                col_monto_banco = st.selectbox("Columna de Monto", banco_cols, index=get_index(banco_cols, ['importe', 'monto', 'valor', 'suma', 'total']), key="monto_b")
                col_fecha_banco = st.selectbox("Columna de Fecha", banco_cols, index=get_index(banco_cols, ['fecha', 'date', 'día']), key="fecha_b")
                col_desc_banco = st.selectbox("Columna de Descripción", banco_cols, index=get_index(banco_cols, ['descripción', 'descripcion', 'detalle', 'concepto']), key="desc_b")
                
            with map_col2:
                st.markdown("#### Registro Contable")
                conta_cols = df_contable.columns.tolist()
                col_monto_conta = st.selectbox("Columna de Monto", conta_cols, index=get_index(conta_cols, ['importe', 'monto', 'valor', 'suma', 'total']), key="monto_l")
                col_fecha_conta = st.selectbox("Columna de Fecha", conta_cols, index=get_index(conta_cols, ['fecha', 'date', 'día']), key="fecha_l")
                col_desc_conta = st.selectbox("Columna de Descripción", conta_cols, index=get_index(conta_cols, ['descripción', 'descripcion', 'detalle', 'concepto']), key="desc_l")
                
            with st.expander("Ver vistas previas de los archivos"):
                col_vp1, col_vp2 = st.columns(2)
                with col_vp1:
                    st.subheader("Extracto Bancario")
                    st.dataframe(df_banco.head())
                with col_vp2:
                    st.subheader("Registro Contable")
                    st.dataframe(df_contable.head())
            
            st.divider()
            
            if st.button("Procesar Conciliación", type="primary", use_container_width=True):
                if not col_monto_banco:
                    st.error("Error: Falta seleccionar la columna de Monto en el Extracto Bancario.")
                elif not col_monto_conta:
                    st.error("Error: Falta seleccionar la columna de Monto en el Registro Contable.")
                else:
                    with st.spinner("Limpiando datos y aplicando fuzzy matching..."):
                        coincidencias, solo_banco, solo_contable = procesar_conciliacion(
                            df_banco, df_contable,
                            col_fecha_banco, col_monto_banco, col_desc_banco,
                            col_fecha_conta, col_monto_conta, col_desc_conta
                        )
                        
                        st.success("¡Procesamiento completado con éxito!")
                        
                        # Registrar el historial del evento
                        registrar_historial(
                            st.session_state["username"],
                            len(coincidencias),
                            len(solo_banco),
                            len(solo_contable)
                        )
                        
                        tab1, tab2, tab3 = st.tabs([
                            f"Coincidencias ({len(coincidencias)})", 
                            f"Solo en Banco ({len(solo_banco)})", 
                            f"Solo en Contable ({len(solo_contable)})"
                        ])
                        
                        with tab1:
                            st.dataframe(coincidencias, use_container_width=True)
                            
                        with tab2:
                            st.dataframe(solo_banco, use_container_width=True)
                            
                        with tab3:
                            st.dataframe(solo_contable, use_container_width=True)
                            
                        output = BytesIO()
                        with pd.ExcelWriter(output, engine='openpyxl') as writer:
                            if not coincidencias.empty:
                                coincidencias.to_excel(writer, index=False, sheet_name='Coincidencias')
                            else:
                                pd.DataFrame({'Mensaje': ['Sin datos']}).to_excel(writer, index=False, sheet_name='Coincidencias')
                                
                            if not solo_banco.empty:
                                solo_banco.to_excel(writer, index=False, sheet_name='Solo Banco')
                            else:
                                pd.DataFrame({'Mensaje': ['Sin datos']}).to_excel(writer, index=False, sheet_name='Solo Banco')
                                
                            if not solo_contable.empty:
                                solo_contable.to_excel(writer, index=False, sheet_name='Solo Contable')
                            else:
                                pd.DataFrame({'Mensaje': ['Sin datos']}).to_excel(writer, index=False, sheet_name='Solo Contable')
                                
                        excel_data = output.getvalue()
                        
                        st.download_button(
                            label="Descargar Reporte Final en Excel",
                            data=excel_data,
                            file_name="reporte_conciliacion.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            type="primary"
                        )
                    
        except Exception as e:
            st.error(f"Ocurrió un error al procesar los archivos: {e}")

elif st.session_state.get('authentication_status') is False:
    st.error('Username o contraseña incorrectos')
    
elif st.session_state.get('authentication_status') is None:
    st.warning('Por favor, inicia sesión para utilizar el sistema')

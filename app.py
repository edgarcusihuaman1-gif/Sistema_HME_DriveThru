import streamlit as st
import pandas as pd
from datetime import datetime

# Configuración de página web en español
st.set_page_config(
    page_title="Panel HME Autoservicio",
    page_icon="🚗",
    layout="wide"
)

EXCEL_FILE = "DRIVE TRHU BASE.xlsx"

# Cargar datos e inicializar el estado de la sesión (Session State)
@st.cache_data
def cargar_datos_iniciales():
    xls = pd.ExcelFile(EXCEL_FILE)
    df_hme = pd.read_excel(xls, sheet_name="Drive HME")
    df_2025 = pd.read_excel(xls, sheet_name="Atenciones 2025")
    df_2026 = pd.read_excel(xls, sheet_name="Atenciones 2026")
    df_cotiz = pd.read_excel(xls, sheet_name="Cotizaciones")
    return df_hme, df_2025, df_2026, df_cotiz

# Inicializar bases de datos editables en memoria
if 'df_hme' not in st.session_state:
    df_hme_ini, df_2025_ini, df_2026_ini, df_cotiz_ini = cargar_datos_iniciales()
    st.session_state.df_hme = df_hme_ini
    st.session_state.df_2025 = df_2025_ini
    st.session_state.df_2026 = df_2026_ini
    st.session_state.df_cotiz = df_cotiz_ini

# Menú de Navegación en Español
st.sidebar.title("🚗 Panel de Control HME")
opcion = st.sidebar.radio(
    "Seleccione un Módulo:",
    [
        "📊 Panel General", 
        "📋 Inventario y Estado de Tiendas", 
        "🛠️ Histórico de Atenciones", 
        "📝 Registrar Nueva Atención", 
        "💵 Catálogo de Repuestos"
    ]
)

# -------------------------------------------------------------
# MÓDULO 1: PANEL GENERAL
# -------------------------------------------------------------
if opcion == "📊 Panel General":
    st.title("📊 Panel de Control General - HME Autoservicio")
    st.caption("Resumen consolidado e indicadores clave de rendimiento")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Tiendas Monitoreadas", len(st.session_state.df_hme))
    c2.metric("Auriculares Operativos", int(st.session_state.df_hme['HEADPHONE OPERATIVOS'].sum()))
    c3.metric("Auriculares Averiados", int(st.session_state.df_hme['HEADPHONE AVERIADOS'].sum()))
    
    costo_total = st.session_state.df_2026['COSTO DE ATENCION'].sum() if 'COSTO DE ATENCION' in st.session_state.df_2026.columns else 0
    c4.metric("Gasto Atenciones 2026", f"${costo_total:,.2f} USD")

    st.markdown("---")

    col_left, col_right = st.columns([1.2, 1])
    
    with col_left:
        st.subheader("📶 Estado de Auriculares por Tienda")
        st.bar_chart(st.session_state.df_hme.set_index('TIENDA')[['HEADPHONE OPERATIVOS', 'HEADPHONE AVERIADOS']])

    with col_right:
        st.subheader("⚠️ Equipos en Estado Crítico")
        criticos = st.session_state.df_hme[
            (st.session_state.df_hme['CARGADOR OPERATIVO'] != 'OPERATIVO') | 
            (st.session_state.df_hme['HEADPHONE AVERIADOS'] > 0)
        ][['TIENDA', 'UBICACIÓN', 'HEADPHONE AVERIADOS', 'CARGADOR OPERATIVO']]
        st.dataframe(criticos, use_container_width=True, hide_index=True)

# -------------------------------------------------------------
# MÓDULO 2: INVENTARIO Y ACTUALIZACIÓN DIRECTA DE TIENDAS
# -------------------------------------------------------------
elif opcion == "📋 Inventario y Estado de Tiendas":
    st.title("📋 Inventario Técnico y Modificación Directa")
    st.info("💡 Puede editar los datos directamente en la tabla interactiva a continuación:")

    # Editor de datos interactivo
    df_editado = st.data_editor(
        st.session_state.df_hme, 
        num_rows="dynamic", 
        use_container_width=True,
        key="editor_tiendas"
    )

    if st.button("💾 Guardar Cambios en la Web"):
        st.session_state.df_hme = df_editado
        st.success("✅ ¡El inventario ha sido actualizado correctamente en la plataforma!")

# -------------------------------------------------------------
# MÓDULO 3: HISTÓRICO DE ATENCIONES
# -------------------------------------------------------------
elif opcion == "🛠️ Histórico de Atenciones":
    st.title("🛠️ Registro de Atenciones y Mantenimiento")
    t1, t2 = st.tabs(["Atenciones 2026", "Atenciones 2025"])
    
    with t1:
        st.subheader("Atenciones del Año 2026")
        st.dataframe(st.session_state.df_2026, use_container_width=True, hide_index=True)
    with t2:
        st.subheader("Atenciones del Año 2025")
        st.dataframe(st.session_state.df_2025, use_container_width=True, hide_index=True)

# -------------------------------------------------------------
# MÓDULO 4: REGISTRAR NUEVA ATENCIÓN DESDE LA WEB
# -------------------------------------------------------------
elif opcion == "📝 Registrar Nueva Atención":
    st.title("📝 Registrar Nueva Atención o Ticket de Soporte")
    st.caption("Complete el formulario para guardar una nueva visita o soporte técnico en el sistema.")

    with st.form("formulario_atencion"):
        col1, col2 = st.columns(2)
        
        with col1:
            tiendas_disponibles = st.session_state.df_hme['TIENDA'].unique()
            tienda_seleccionada = st.selectbox("Seleccionar Tienda:", tiendas_disponibles)
            fecha_atencion = st.date_input("Fecha de Atención:", datetime.now())
            tipo_atencion = st.selectbox("Tipo de Atención:", ["Preventivo", "Correctivo", "Garantía", "Instalación"])
            tecnico_responsable = st.text_input("Técnico Asignado:")

        with col2:
            diagnostico_tecnico = st.text_area("Diagnóstico / Detalle del Problema:")
            solucion_aplicada = st.text_area("Solución / Trabajos Realizados:")
            costo_servicio = st.number_input("Costo de Atención ($ USD):", min_value=0.0, step=10.0)

        boton_enviar = st.form_submit_button("💾 Registrar Atención")

        if boton_enviar:
            # Obtener ubicación automática de la tienda seleccionada
            filtro_tienda = st.session_state.df_hme[st.session_state.df_hme['TIENDA'] == tienda_seleccionada]
            ubicacion = filtro_tienda['UBICACIÓN'].values[0] if len(filtro_tienda) > 0 else ""

            # Estructurar nueva fila
            nuevo_ticket = pd.DataFrame([{
                "FECHA": fecha_atencion.strftime("%Y-%m-%d"),
                "TIENDA": tienda_seleccionada,
                "UBICACIÓN": ubicación,
                "TIPO DE ATENCION": tipo_atencion,
                "TECNICO": tecnico_responsable,
                "DIAGNOSTICO": diagnostico_tecnico,
                "SOLUCION": solucion_aplicada,
                "COSTO DE ATENCION": costo_servicio
            }])

            # Actualizar datos en memoria
            st.session_state.df_2026 = pd.concat([st.session_state.df_2026, nuevo_ticket], ignore_index=True)
            st.success("✅ ¡Atención registrada con éxito en el sistema!")
            st.balloons()

# -------------------------------------------------------------
# MÓDULO 5: CATÁLOGO DE REPUESTOS Y COTIZACIONES
# -------------------------------------------------------------
elif opcion == "💵 Catálogo de Repuestos":
    st.title("💵 Catálogo de Repuestos y Precios HME")
    st.dataframe(st.session_state.df_cotiz, use_container_width=True, hide_index=True)

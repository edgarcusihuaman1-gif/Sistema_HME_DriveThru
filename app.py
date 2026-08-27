import streamlit as st
import pandas as pd
from datetime import datetime
import io

# Configuración de página web
st.set_page_config(
    page_title="Panel HME Autoservicio",
    page_icon="🚗",
    layout="wide"
)

# Estilo CSS para ocultar menú nativo y comprimir encabezados/tablas
estilo_oculto = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    h1 {
        font-size: 1.6rem !important;
        padding-top: 0rem !important;
    }
    h2 {
        font-size: 1.3rem !important;
    }
    h3 {
        font-size: 1.1rem !important;
    }
    .stHeader {
        padding-top: 0.5rem !important;
    }
    [data-testid="stTable"] th, [data-testid="stDataEditor"] th {
        font-size: 13px !important;
        white-space: nowrap !important;
    }
    </style>
"""
st.markdown(estilo_oculto, unsafe_allow_html=True)

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

if 'df_hme' not in st.session_state:
    df_hme_ini, df_2025_ini, df_2026_ini, df_cotiz_ini = cargar_datos_iniciales()
    st.session_state.df_hme = df_hme_ini
    st.session_state.df_2025 = df_2025_ini
    st.session_state.df_2026 = df_2026_ini
    st.session_state.df_cotiz = df_cotiz_ini

# -------------------------------------------------------------
# DICCIONARIO GLOBAL DE ACOPTAMIENTO DE ENCABEZADOS
# -------------------------------------------------------------
RENOMBRAR_GLOBAL = {
    # Tabla Inventario
    'HEADPHONE OPERATIVOS': 'Headph. Operat.',
    'HEADPHONE AVERIADOS': 'Headph. Averiados',
    'TOTAL HEADPHONE': 'Total Headph.',
    'CARGADOR DE BATERIAS': 'Cargador Bat.',
    'CARGADOR OPERATIVO': 'Estado Cargador',
    'UBICACIÓN': 'Ubicación',
    'TIENDA': 'Tienda',
    # Tabla Atenciones
    'TIPO DE ATENCION': 'Tipo Atenc.',
    'COSTO DE ATENCION': 'Costo ($)',
    'DIAGNOSTICO': 'Diagnóstico',
    'SOLUCION': 'Solución',
    'TECNICO': 'Técnico',
    'FECHA': 'Fecha'
}

def acortar_columnas(df):
    """Aplica los nombres cortos a cualquier DataFrame de manera dinámica."""
    columnas_existentes = {k: v for k, v in RENOMBRAR_GLOBAL.items() if k in df.columns}
    return df.rename(columns=columnas_existentes)

# -------------------------------------------------------------
# FUNCIONES AUXILIARES DE EXPORTACIÓN (EXCEL Y PDF)
# -------------------------------------------------------------
def exportar_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Reporte')
    return output.getvalue()

def generar_html_reporte(titulo, df):
    df_corto = acortar_columnas(df)
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>{titulo}</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; color: #333; }}
            h1 {{ color: #1E3A8A; text-align: center; border-bottom: 2px solid #1E3A8A; padding-bottom: 10px; font-size: 18px; }}
            p.fecha {{ text-align: right; font-size: 11px; color: #666; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 15px; font-size: 11px; }}
            th, td {{ border: 1px solid #ddd; padding: 6px; text-align: left; }}
            th {{ background-color: #1E3A8A; color: white; }}
            tr:nth-child(even) {{ background-color: #f2f2f2; }}
        </style>
    </head>
    <body>
        <h1>🚗 Sistema HME Drive-Thru</h1>
        <h2>{titulo}</h2>
        <p class="fecha">Fecha de emisión: {datetime.now().strftime('%d/%m/%Y %H:%M')}</p>
        {df_corto.to_html(index=False, classes='table')}
    </body>
    </html>
    """
    return html_content.encode('utf-8')

# Menú de Navegación
st.sidebar.title("🚗 HME Control")
opcion = st.sidebar.radio(
    "Menú Principal:",
    [
        "📊 Panel General", 
        "📋 Inventario de Tiendas", 
        "🛠️ Histórico Atenciones", 
        "📝 Nueva Atención", 
        "💵 Cotizaciones",
        "📥 Exportar Datos"
    ]
)

# -------------------------------------------------------------
# MÓDULO 1: PANEL GENERAL
# -------------------------------------------------------------
if opcion == "📊 Panel General":
    st.title("📊 Panel General HME")
    st.caption("Indicadores clave e inventario general")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Tiendas", len(st.session_state.df_hme))
    c2.metric("Auric. Operativos", int(st.session_state.df_hme['HEADPHONE OPERATIVOS'].sum()))
    c3.metric("Auric. Averiados", int(st.session_state.df_hme['HEADPHONE AVERIADOS'].sum()))
    
    costo_total = st.session_state.df_2026['COSTO DE ATENCION'].sum() if 'COSTO DE ATENCION' in st.session_state.df_2026.columns else 0
    c4.metric("Gasto 2026", f"${costo_total:,.2f} USD")

    st.markdown("---")

    col_left, col_right = st.columns([1.2, 1])
    
    with col_left:
        st.subheader("📶 Estado de Auriculares")
        st.bar_chart(st.session_state.df_hme.set_index('TIENDA')[['HEADPHONE OPERATIVOS', 'HEADPHONE AVERIADOS']])

    with col_right:
        st.subheader("⚠️ Equipos en Estado Crítico")
        criticos = st.session_state.df_hme[
            (st.session_state.df_hme['CARGADOR OPERATIVO'] != 'OPERATIVO') | 
            (st.session_state.df_hme['HEADPHONE AVERIADOS'] > 0)
        ][['TIENDA', 'UBICACIÓN', 'HEADPHONE AVERIADOS', 'CARGADOR OPERATIVO']]
        st.dataframe(acortar_columnas(criticos), use_container_width=True, hide_index=True)

# -------------------------------------------------------------
# MÓDULO 2: INVENTARIO DE TIENDAS
# -------------------------------------------------------------
elif opcion == "📋 Inventario de Tiendas":
    st.title("📋 Inventario de Tiendas")
    st.info("💡 Edite los datos directamente en la tabla:")

    # Mostrar tabla ajustada
    df_editado = st.data_editor(
        acortar_columnas(st.session_state.df_hme), 
        num_rows="dynamic", 
        use_container_width=True,
        key="editor_tiendas"
    )

    col_btn1, col_btn2, col_btn3 = st.columns([2, 1, 1])
    with col_btn1:
        if st.button("💾 Guardar Cambios"):
            inv_renombrado = {v: k for k, v in RENOMBRAR_GLOBAL.items()}
            st.session_state.df_hme = df_editado.rename(columns=inv_renombrado)
            st.success("✅ ¡Inventario actualizado!")

    with col_btn2:
        st.download_button(
            label="📊 Exportar Excel",
            data=exportar_excel(st.session_state.df_hme),
            file_name=f"Inventario_HME_{datetime.now().strftime('%Y%m%d')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    with col_btn3:
        st.download_button(
            label="📄 Exportar PDF",
            data=generar_html_reporte("Reporte de Inventario de Tiendas", st.session_state.df_hme),
            file_name=f"Inventario_HME_{datetime.now().strftime('%Y%m%d')}.html",
            mime="text/html"
        )

# -------------------------------------------------------------
# MÓDULO 3: HISTÓRICO DE ATENCIONES
# -------------------------------------------------------------
elif opcion == "🛠️ Histórico Atenciones":
    st.title("🛠️ Histórico de Atenciones")
    t1, t2 = st.tabs(["Atenciones 2026", "Atenciones 2025"])
    
    with t1:
        st.subheader("Año 2026")
        st.dataframe(acortar_columnas(st.session_state.df_2026), use_container_width=True, hide_index=True)
        
        c1, c2 = st.columns(2)
        with c1:
            st.download_button(
                label="📊 Descargar Excel (2026)",
                data=exportar_excel(st.session_state.df_2026),
                file_name=f"Atenciones_2026_{datetime.now().strftime('%Y%m%d')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        with c2:
            st.download_button(
                label="📄 Descargar PDF (2026)",
                data=generar_html_reporte("Reporte de Atenciones 2026", st.session_state.df_2026),
                file_name=f"Atenciones_2026_{datetime.now().strftime('%Y%m%d')}.html",
                mime="text/html"
            )

    with t2:
        st.subheader("Año 2025")
        st.dataframe(acortar_columnas(st.session_state.df_2025), use_container_width=True, hide_index=True)

        c1, c2 = st.columns(2)
        with c1:
            st.download_button(
                label="📊 Descargar Excel (2025)",
                data=exportar_excel(st.session_state.df_2025),
                file_name=f"Atenciones_2025_{datetime.now().strftime('%Y%m%d')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        with c2:
            st.download_button(
                label="📄 Descargar PDF (2025)",
                data=generar_html_reporte("Reporte de Atenciones 2025", st.session_state.df_2025),
                file_name=f"Atenciones_2025_{datetime.now().strftime('%Y%m%d')}.html",
                mime="text/html"
            )

# -------------------------------------------------------------
# MÓDULO 4: REGISTRAR NUEVA ATENCIÓN
# -------------------------------------------------------------
elif opcion == "📝 Nueva Atención":
    st.title("📝 Registrar Atención")
    st.caption("Complete el formulario para guardar una nueva visita o soporte técnico.")

    with st.form("formulario_atencion"):
        col1, col2 = st.columns(2)
        
        with col1:
            tiendas_disponibles = st.session_state.df_hme['TIENDA'].unique()
            tienda_seleccionada = st.selectbox("Tienda:", tiendas_disponibles)
            fecha_atencion = st.date_input("Fecha:", datetime.now())
            tipo_atencion = st.selectbox("Tipo:", ["Preventivo", "Correctivo", "Garantía", "Instalación"])
            tecnico_responsable = st.text_input("Técnico:")

        with col2:
            diagnostico_tecnico = st.text_area("Diagnóstico / Problema:")
            solucion_aplicada = st.text_area("Solución Realizada:")
            costo_servicio = st.number_input("Costo ($ USD):", min_value=0.0, step=10.0)

        boton_enviar = st.form_submit_button("💾 Guardar Atención")

        if boton_enviar:
            filtro_tienda = st.session_state.df_hme[st.session_state.df_hme['TIENDA'] == tienda_seleccionada]
            ubicacion = filtro_tienda['UBICACIÓN'].values[0] if len(filtro_tienda) > 0 else ""

            nuevo_ticket = pd.DataFrame([{
                "FECHA": fecha_atencion.strftime("%Y-%m-%d"),
                "TIENDA": tienda_seleccionada,
                "UBICACIÓN": ubicacion,
                "TIPO DE ATENCION": tipo_atencion,
                "TECNICO": tecnico_responsable,
                "DIAGNOSTICO": diagnostico_tecnico,
                "SOLUCION": solucion_aplicada,
                "COSTO DE ATENCION": costo_servicio
            }])

            st.session_state.df_2026 = pd.concat([st.session_state.df_2026, nuevo_ticket], ignore_index=True)
            st.success("✅ ¡Atención registrada correctamente!")
            st.balloons()

# -------------------------------------------------------------
# MÓDULO 5: CATÁLOGO Y COTIZACIONES
# -------------------------------------------------------------
elif opcion == "💵 Cotizaciones":
    st.title("💵 Catálogo de Repuestos")
    st.dataframe(acortar_columnas(st.session_state.df_cotiz), use_container_width=True, hide_index=True)

# -------------------------------------------------------------
# MÓDULO 6: EXPORTAR DATOS
# -------------------------------------------------------------
elif opcion == "📥 Exportar Datos":
    st.title("📥 Centro de Exportación")
    st.caption("Seleccione la tabla que desea descargar en Excel o PDF:")

    modulo_exportar = st.selectbox("Seleccionar Tabla:", ["Inventario de Tiendas", "Atenciones 2026", "Atenciones 2025", "Catálogo de Repuestos"])

    if modulo_exportar == "Inventario de Tiendas":
        df_target = st.session_state.df_hme
    elif modulo_exportar == "Atenciones 2026":
        df_target = st.session_state.df_2026
    elif modulo_exportar == "Atenciones 2025":
        df_target = st.session_state.df_2025
    else:
        df_target = st.session_state.df_cotiz

    st.write("### Vista Previa:")
    st.dataframe(acortar_columnas(df_target), use_container_width=True, hide_index=True)

    col1, col2 = st.columns(2)

    with col1:
        st.download_button(
            label="📊 Descargar Excel (.xlsx)",
            data=exportar_excel(df_target),
            file_name=f"{modulo_exportar}_{datetime.now().strftime('%Y%m%d')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )

    with col2:
        st.download_button(
            label="📄 Descargar PDF / Impresión",
            data=generar_html_reporte(modulo_exportar, df_target),
            file_name=f"{modulo_exportar}_{datetime.now().strftime('%Y%m%d')}.html",
            mime="text/html",
            use_container_width=True
        )

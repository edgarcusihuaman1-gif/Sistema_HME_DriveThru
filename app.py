import streamlit as st
import pandas as pd
from datetime import datetime

# Configuración de página web
st.set_page_config(
    page_title="Panel HME Drive-Thru",
    page_icon="🚗",
    layout="wide"
)

EXCEL_FILE = "DRIVE TRHU BASE.xlsx"

def cargar_datos():
    xls = pd.ExcelFile(EXCEL_FILE)
    df_hme = pd.read_excel(xls, sheet_name="Drive HME")
    df_2025 = pd.read_excel(xls, sheet_name="Atenciones 2025")
    df_2026 = pd.read_excel(xls, sheet_name="Atenciones 2026")
    df_cotiz = pd.read_excel(xls, sheet_name="Cotizaciones")
    return df_hme, df_2025, df_2026, df_cotiz

try:
    df_hme, df_2025, df_2026, df_cotiz = cargar_datos()

    # Menú Lateral
    st.sidebar.title("🚗 Panel de Control HME")
    opcion = st.sidebar.radio(
        "Módulos:",
        ["Panel de Control General", "Hardware Inventario", "Histórico Mantenimiento", "📝 Registrar Atención", "Cotizaciones & Repuestos"]
    )

    # 1. PANEL DE CONTROL GENERAL
    if opcion == "Panel de Control General":
        st.title("📊 Panel de Control General HME Autoservicio")
        st.caption("Resumen consolidado de infraestructura y soporte técnico")

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Tiendas Monitoreadas", len(df_hme))
        c2.metric("Auriculares Operativos", int(df_hme['HEADPHONE OPERATIVOS'].sum()))
        c3.metric("Auriculares Averiados", int(df_hme['HEADPHONE AVERIADOS'].sum()))
        c4.metric("Gasto Atenciones 2026", f"${df_2026['COSTO DE ATENCION'].sum():,.2f} USD")

        st.markdown("---")

        col_left, col_right = st.columns([1.2, 1])
        
        with col_left:
            st.subheader("📶 Estado de Auriculares por Tienda")
            st.bar_chart(df_hme.set_index('TIENDA')[['HEADPHONE OPERATIVOS', 'HEADPHONE AVERIADOS']])

        with col_right:
            st.subheader("⚠️ Alertas de Equipos Críticos")
            criticos = df_hme[
                (df_hme['CARGADOR OPERATIVO'] != 'OPERATIVO') | 
                (df_hme['HEADPHONE AVERIADOS'] > 0)
            ][['TIENDA', 'UBICACIÓN', 'HEADPHONE AVERIADOS', 'CARGADOR OPERATIVO']]
            st.dataframe(criticos, use_container_width=True, hide_index=True)

    # 2. HARDWARE INVENTARIO
    elif opcion == "Hardware Inventario":
        st.title("📋 Inventario Técnico de Equipos")
        
        marcas = ["Todas"] + list(df_hme['MARCA'].unique())
        marca_sel = st.selectbox("Filtrar por Marca:", marcas)
        
        df_mostrar = df_hme if marca_sel == "Todas" else df_hme[df_hme['MARCA'] == marca_sel]
        st.dataframe(df_mostrar, use_container_width=True, hide_index=True)

    # 3. HISTÓRICO MANTENIMIENTO
    elif opcion == "Histórico Mantenimiento":
        st.title("🛠️ Registro de Atenciones y Mantenimiento")
        t1, t2 = st.tabs(["Atenciones 2026", "Atenciones 2025"])
        
        with t1:
            st.dataframe(df_2026, use_container_width=True, hide_index=True)
        with t2:
            st.dataframe(df_2025, use_container_width=True, hide_index=True)

    # 4. REGISTRAR NUEVA ATENCIÓN / TICKET
    elif opcion == "📝 Registrar Atención":
        st.title("📝 Registrar Nueva Atención / Mantenimiento")
        st.caption("Ingresa los datos para guardar una nueva visita o soporte en la base de datos de 2026")

        with st.form("form_atencion"):
            col1, col2 = st.columns(2)
            
            with col1:
                tienda_sel = st.selectbox("Seleccionar Tienda:", df_hme['TIENDA'].unique())
                fecha = st.date_input("Fecha de Atención:", datetime.now())
                tipo_atencion = st.selectbox("Tipo de Atención:", ["Preventivo", "Correctivo", "Garantía", "Instalación"])
                tecnico = st.text_input("Técnico Asignado:")

            with col2:
                diagnostico = st.text_area("Diagnóstico / Detalle del Problema:")
                solucion = st.text_area("Solución / Trabajos Realizados:")
                costo = st.number_input("Costo de Atención (USD):", min_value=0.0, step=10.0)

            submitted = st.form_submit_button("💾 Guardar Registro")

            if submitted:
                # Obtener ubicación correspondiente a la tienda
                ubicacion = df_hme[df_hme['TIENDA'] == tienda_sel]['UBICACIÓN'].values[0] if len(df_hme[df_hme['TIENDA'] == tienda_sel]) > 0 else ""
                
                # Crear nuevo registro
                nuevo_registro = pd.DataFrame([{
                    "FECHA": fecha.strftime("%Y-%m-%d"),
                    "TIENDA": tienda_sel,
                    "UBICACIÓN": ubicación,
                    "TIPO DE ATENCION": tipo_atencion,
                    "TECNICO": tecnico,
                    "DIAGNOSTICO": diagnostico,
                    "SOLUCION": solucion,
                    "COSTO DE ATENCION": costo
                }])

                # Concatenar y guardar en Excel
                df_2026_actualizado = pd.concat([df_2026, nuevo_registro], ignore_index=True)

                with pd.ExcelWriter(EXCEL_FILE, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
                    df_2026_actualizado.to_excel(writer, sheet_name="Atenciones 2026", index=False)

                st.success("✅ ¡Atención registrada correctamente en la hoja 'Atenciones 2026'!")
                st.balloons()

    # 5. COTIZACIONES & REPUESTOS
    elif opcion == "Cotizaciones & Repuestos":
        st.title("💵 Catálogo de Repuestos HME")
        st.dataframe(df_cotiz, use_container_width=True, hide_index=True)

except Exception as e:
    st.error(f"Error al cargar datos: {e}")
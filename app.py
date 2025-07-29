import streamlit as st
import pandas as pd
import os
from datetime import datetime
from utils.load_clean_alds import cargar_alds
from utils.load_clean_mes import cargar_mes
from utils.load_clean_oee import cargar_oee
from utils.helpers import generar_union_final
from io import BytesIO

# Configuracion de pagina
st.set_page_config(page_title="Master Daily Quantities Tracking CVT Final Processes", layout="wide")
st.title("Master Daily Quantities Tracking CVT Final Processes")

shifts = ["1st Shift", "2nd Shift", "3rd Shift"]
orden_partes = [
    "L-0G005-1036-17",
    "L-0G005-0095-41",
    "L-0G005-1015-05",
    "L-0G005-1043-12"
]
index_completo = pd.MultiIndex.from_product([shifts, orden_partes], names=["Shift", "Parte"])

# Variables de estado para almacenar chatarra fisica
if "scrap_fisico_df" not in st.session_state:
    st.session_state.scrap_fisico_df = {
        (shift, parte): 0
        for shift in ["1st Shift", "2nd Shift", "3rd Shift"]
        for parte in [
            "L-0G005-1036-17",
            "L-0G005-0095-41",
            "L-0G005-1015-05",
            "L-0G005-1043-12",
        ]
    }

# --- PANEL LATERAL PARA INGRESO DE CHATARRA FÍSICA ---
st.sidebar.header("Ingreso de chatarra física")
turnos = ["1st Shift", "2nd Shift", "3rd Shift"]
partes = ["L-0G005-1036-17", "L-0G005-0095-41", "L-0G005-1015-05", "L-0G005-1043-12"]

for turno in turnos:
    st.sidebar.subheader(turno)
    for i, parte in enumerate(partes):
        orden_key = f"{i:02d}_{turno}_{parte}"
        st.session_state.scrap_fisico_df[(turno, parte)] = st.sidebar.number_input(
            f"{parte}", min_value=0, step=1, key=orden_key, value=st.session_state.scrap_fisico_df[(turno, parte)]
        )


# --- Carga de archivos ---
st.sidebar.header("Carga de archivos")
alds_file = st.sidebar.file_uploader("Archivo ALDS (.csv)", type="csv")
mes_file = st.sidebar.file_uploader("Archivo MES (.xls)", type=["xls"])
oee_file = st.sidebar.file_uploader("Archivo OEE (.csv)", type="csv")

# Botón para procesar todo
tabla_final = None
if st.sidebar.button("Procesar datos"):
    df_alds = cargar_alds(alds_file) if alds_file else None
    df_mes = cargar_mes(mes_file) if mes_file else None
    df_oee = cargar_oee(oee_file) if oee_file else None

    if any([df_alds is not None, df_mes is not None, df_oee is not None]):
        tabla_final = generar_union_final(df_alds, df_mes, df_oee)

        # Agregar columna "Físico" desde el scrap ingresado
        scrap_fisico_df_series = pd.Series({
            (shift, parte): cantidad
            for (shift, parte), cantidad in st.session_state.scrap_fisico_df.items()
        })
        scrap_fisico_df = scrap_fisico_df_series.reset_index()
        scrap_fisico_df.columns = ["Shift", "Parte", "Fisico"]

        tabla_final = pd.merge(tabla_final, scrap_fisico_df, on=["Shift", "Parte"], how="left")

        # Orden específico de columnas
        columnas_ordenadas = [
            "Shift", "Parte",
            "MES",
            "ALDS Serie", "ALDS Rework",
            "OEE Serie", "OEE Rework", 
            "MES SCRAP", "Físico", "OEE SCRAP"
        ]
    
        # Agregar columnas que existan, en orden, y omitir las que no
        columnas_presentes = [col for col in columnas_ordenadas if col in df_result.columns]

        # Mostrar tabla
        st.success("Datos procesados correctamente")
        st.dataframe(tabla_final, use_container_width=True)

        # Exportar Excel
        output_path = "tabla_final_completa.xlsx"
        tabla_final.to_excel(output_path, index=False)
        with open(output_path, "rb") as f:
            st.download_button("Descargar Excel", f, file_name="tabla_final_completa.xlsx")
    else:
        st.warning("Por favor, sube al menos uno de los archivos para procesar los datos.")




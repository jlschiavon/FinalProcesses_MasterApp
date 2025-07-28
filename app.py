import streamlit as st
import pandas as pd
import os
from datetime import datetime
from utils.load_clean_alds import cargar_alds
from utils.load_clean_mes import cargar_mes
from utils.load_clean_oee import cargar_oee
from utils.helpers import unir_datos

# Configuracion de pagina
st.set_page_config(page_title="Master Daily Quantities Tracking CVT Final Processes", layout="wide")
st.title("Master Daily Quantities Tracking CVT Final Processes")

# Variables de estado para almacenar chatarra fisica
if "scrap_fisico" not in st.session_state:
    st.session_state.scrap_fisico = {
        (shift, parte): 0
        for shift in ["1st Shift", "2nd Shift", "3rd Shift"]
        for parte in [
            "L-0G005-1036-17",
            "L-0G005-0095-41",
            "L-0G005-1015-05",
            "L-0G005-1043-12",
        ]
    }

# --- Panel para ingresar scrap fisico ---
st.sidebar.header("Ingreso de chatarra física")
turnos = ["1st Shift", "2nd Shift", "3rd Shift"]
partes = ["L-0G005-1036-17", "L-0G005-0095-41", "L-0G005-1015-05", "L-0G005-1043-12"]

for turno in turnos:
    st.sidebar.subheader(turno)
    for parte in partes:
        key = f"{turno}_{parte}"
        st.session_state.scrap_fisico[(turno, parte)] = st.sidebar.number_input(
            f"{parte}", min_value=0, step=1, key=key, value=st.session_state.scrap_fisico[(turno, parte)]
        )

# --- Carga de archivos ---
st.sidebar.header("Carga de archivos")
file_alds = st.sidebar.file_uploader("Archivo ALDS (.csv)", type="csv")
file_mes = st.sidebar.file_uploader("Archivo MES (.xls)", type=["xls"])
file_oee = st.sidebar.file_uploader("Archivo OEE (.csv)", type="csv")

# Botón para procesar todo
df_result = None
if st.sidebar.button("Procesar datos"):
    if file_alds and file_mes and file_oee:
        df_alds = cargar_y_limpiar_alds(file_alds)
        df_mes = cargar_y_limpiar_mes(file_mes)
        df_oee = cargar_y_limpiar_oee(file_oee)
        df_result = unir_datos(df_alds, df_mes, df_oee)

        # Agregar columna "Físico" desde el scrap ingresado
        scrap_fisico_series = pd.Series(
            {
                (shift, parte): cantidad
                for (shift, parte), cantidad in st.session_state.scrap_fisico.items()
            }
        )
        scrap_fisico_df = scrap_fisico_series.reset_index()
        scrap_fisico_df.columns = ["Shift", "Parte", "Físico"]

        df_result = pd.merge(df_result, scrap_fisico_df, on=["Shift", "Parte"], how="left")
        df_result["Físico"] = df_result["Físico"].fillna(0).astype(int)

        # Mostrar tabla
        st.success("Datos procesados correctamente")
        st.dataframe(df_result, use_container_width=True)

        # Exportar Excel
        output_path = "tabla_final_completa.xlsx"
        df_result.to_excel(output_path, index=False)
        with open(output_path, "rb") as f:
            st.download_button("Descargar Excel", f, file_name="tabla_final_completa.xlsx")

    else:
        st.warning("Por favor, sube los tres archivos requeridos para procesar los datos.")

# app.py
import streamlit as st
from utils.load_clean_alds import cargar_alds
from utils.load_clean_mes import cargar_mes
from utils.load_clean_oee import cargar_oee
from utils.helpers import generar_union_final
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="Master Daily Quantities Tracking CVT Final Processes", layout="wide")

st.title("📊 Master Daily Quantities Tracking - CVT Final Processes")
st.markdown("Sube los archivos diarios de ALDS, MES y OEE para obtener un resumen consolidado por parte y turno.")

# --- VARIABLES DE CHATARRA FÍSICA ---
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

# --- PANEL LATERAL PARA INGRESO DE CHATARRA FÍSICA ---
st.sidebar.header("Ingreso de chatarra física")
turnos = ["1st Shift", "2nd Shift", "3rd Shift"]
partes = ["L-0G005-1036-17", "L-0G005-0095-41", "L-0G005-1015-05", "L-0G005-1043-12"]

for turno in turnos:
    st.sidebar.subheader(turno)
    for i, parte in enumerate(partes):
        orden_key = f"{turno}_{i:02d}_{parte}"
        st.session_state.scrap_fisico[(turno, parte)] = st.sidebar.number_input(
            f"{parte}", min_value=0, step=1, key=orden_key, value=st.session_state.scrap_fisico[(turno, parte)]
        )

# --- ARCHIVOS ---
alds_file = st.file_uploader("📄 Cargar archivo ALDS (.csv)", type=["csv"])
mes_file = st.file_uploader("📄 Cargar archivo MES (.xls, .xlsx)", type=["xls", "xlsx"])
oee_file = st.file_uploader("📄 Cargar archivo OEE (.csv)", type=["csv"])

if alds_file and mes_file and oee_file:
    df_alds = cargar_alds(alds_file)
    df_mes = cargar_mes(mes_file)
    df_oee = cargar_oee(oee_file)

    tabla_final = generar_union_final(df_alds, df_mes, df_oee)

    # Reemplazar columna "Fisico" con los valores ingresados manualmente
    scrap_fisico_series = pd.Series(
        {
            (shift, parte): cantidad
            for (shift, parte), cantidad in st.session_state.scrap_fisico.items()
        }
    )
    scrap_fisico_df = scrap_fisico_series.reset_index()
    scrap_fisico_df.columns = ["Shift", "Parte", "Fisico"]

    tabla_final["Shift"] = tabla_final["Shift"].str.strip()
    tabla_final["Parte"] = tabla_final["Parte"].str.strip()
    scrap_fisico_df["Shift"] = scrap_fisico_df["Shift"].str.strip()
    scrap_fisico_df["Parte"] = scrap_fisico_df["Parte"].str.strip()

    tabla_final = pd.merge(tabla_final.drop(columns=[col for col in tabla_final.columns if col.lower() == "fisico"]), scrap_fisico_df, on=["Shift", "Parte"], how="left")
    tabla_final["Fisico"] = tabla_final["Fisico"].fillna(0).astype(int)

    st.success("✅ Datos procesados correctamente")
    st.dataframe(tabla_final, use_container_width=True)

    output = BytesIO()
    tabla_final.to_excel(output, index=False, engine='openpyxl')
    st.download_button("📥 Descargar Excel", data=output.getvalue(), file_name="tabla_final_completa.xlsx")
else:
    st.warning("Por favor sube los tres archivos para continuar.")

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import io

# Encabezado
st.markdown("# 📊 Análisis de Reconocimiento Facial")

# Centramos las imágenes y hacemos responsivo
col1, col2, col3 = st.columns([1, 2, 1])
with col1:
    st.write("")
with col2:
    st.markdown(
        """
        <div style="display: flex; justify-content: center; gap: 20px;">
            <img src='https://raw.githubusercontent.com/soriio/Analizador/main/images/ifd.jpeg' style='width: 20%; min-width: 80px;'>
            <img src='https://raw.githubusercontent.com/soriio/Analizador/main/images/sistecredito.jpg' style='width: 20%; min-width: 80px;'>
        </div>
        <style>
            h1, h2, h3, p { font-size: calc(1rem + 0.5vw); }
            table { width: 100%; display: block; overflow-x: auto; }
        </style>
        """,
        unsafe_allow_html=True
    )
with col3:
    st.write("")

# Subir archivos
st.markdown("## 📂 Selecciona archivos de reconocimiento facial")
uploaded_files = st.file_uploader("📎 Sube tus archivos HTML", type=["htm", "html"], accept_multiple_files=True)

if uploaded_files:
    for uploaded_file in uploaded_files:
        try:
            df_list = pd.read_html(uploaded_file)
            if not df_list:
                st.error(f"⚠️ No se encontraron tablas en el archivo {uploaded_file.name}.")
                continue
            
            df = df_list[0]
            
            df.columns = pd.Index([f"{col}_{i}" if col in df.columns[:i] else col for i, col in enumerate(df.columns)])
            
            df.rename(columns={"Nombre completo": "Nombre", "Lista de verificación": "Lista de verificacion"}, inplace=True)
            
            nombres_esperados = {
                "Dia": ["Dia", "Fecha", "Timestamp"],
                "Nombre": ["Nombre", "Nombre completo", "Rostro reconocido"],
                "ID": ["ID", "Identificación"],
                "Lista de verificacion": ["Lista de verificación"],
                "Camara": ["Camara", "Cámara"]
            }
            
            renombres = {col: nuevo_nombre for nuevo_nombre, posibles in nombres_esperados.items() for col in df.columns if col in posibles}
            df.rename(columns=renombres, inplace=True)
            
            tipo_reporte = ""
            if "Nombre" in df.columns and "ID" in df.columns:
                st.markdown(f"### 📄 Reporte de Rostros Reconocidos ({uploaded_file.name})")
                tipo_reporte = "reconocidos"
            elif "Imagen detectada" in df.columns:
                st.markdown(f"### 🚨 Reporte de Rostros No Reconocidos ({uploaded_file.name})")
                tipo_reporte = "no_reconocidos"
            else:
                st.error(f"⚠️ No se encontraron columnas necesarias en {uploaded_file.name}.")
                continue

            if "Dia" in df.columns:
                df["Dia"] = pd.to_datetime(df["Dia"], errors='coerce')
            
            st.success(f"✅ Archivo procesado correctamente: {uploaded_file.name}")

            fecha_inicio, fecha_fin = df["Dia"].min(), df["Dia"].max()
            st.write(f"📅 **Intervalo del Reporte:** Desde `{fecha_inicio}` hasta `{fecha_fin}`")

            if tipo_reporte == "reconocidos" and "Camara" in df.columns and "Lista de verificacion" in df.columns:
                personas_por_camara_lista = df.groupby(["Camara", "Lista de verificacion"]).size().reset_index(name="Cantidad")
                st.write("📋 **Resumen de Datos:**")
                st.write(personas_por_camara_lista)

                st.write("📊 **Gráfica de Personas por Cámara y Lista de Verificación**")
                fig, ax = plt.subplots(figsize=(8, 5))
                for lista in personas_por_camara_lista["Lista de verificacion"].unique():
                    subset = personas_por_camara_lista[personas_por_camara_lista["Lista de verificacion"] == lista]
                    bars = ax.bar(subset["Camara"].astype(str), subset["Cantidad"], label=lista)
                    
                    # Agregar los valores encima de las barras
                    for bar in bars:
                        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() - 0.5, int(bar.get_height()), ha='center', va='bottom', color='black', fontweight='bold')
                
                ax.set_xlabel("Cámara")
                ax.set_ylabel("Cantidad de Personas")
                ax.set_title("Cantidad de Personas por Cámara y Lista de Verificación")
                ax.legend(title="Lista de Verificación")
                ax.grid(axis="y", linestyle="--", alpha=0.7)
                st.pyplot(fig)
            elif tipo_reporte == "no_reconocidos" and "Camara" in df.columns:
                camara_no_reconocidos = df.groupby(["Camara"]).size().reset_index(name="Cantidad")
                st.write("📋 **Resumen de Cámaras con Rostros No Reconocidos:**")
                st.write(camara_no_reconocidos)
                
                st.write("📊 **Gráfica de Cámaras con Rostros No Reconocidos**")
                fig, ax = plt.subplots(figsize=(8, 5))
                bars = ax.bar(camara_no_reconocidos["Camara"].astype(str), camara_no_reconocidos["Cantidad"], color="red")
                
                # Agregar los valores encima de las barras
                for bar in bars:
                    ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() - 0.5, int(bar.get_height()), ha='center', va='bottom', color='black', fontweight='bold')
                
                ax.set_xlabel("Cámara")
                ax.set_ylabel("Cantidad de Rostros No Reconocidos")
                ax.set_title("Cantidad de Rostros No Reconocidos por Cámara")
                ax.grid(axis="y", linestyle="--", alpha=0.7)
                st.pyplot(fig)
            else:
                st.warning("⚠️ No se encontraron las columnas necesarias para el análisis.")
        except Exception as e:
            st.error(f"❌ Ocurrió un error al procesar el archivo {uploaded_file.name}: {e}")

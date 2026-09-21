import streamlit as st
import pandas as pd
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
import io

st.set_page_config(page_title="Gestión de Torneos de Billar", layout="wide")

st.title("🎱 Sistema de Torneos de Billar")

# Menú principal con las 3 modalidades solicitadas
menu = st.sidebar.selectbox("Seleccione la Modalidad de Torneo", [
    "Todos contra Todos",
    "Torneos Eliminación Directa", 
    "Torneos Doble Eliminación"
])

# ==========================================
# 1. TODOS CONTRA TODOS (100% Intacto)
# ==========================================
if menu == "Todos contra Todos":
    st.subheader("Modalidad: Todos contra todos (Round-Robin)")

    if "jugadores" not in st.session_state:
        st.session_state.jugadores = [
            "Emanuel Villalobos", "Alejandro Breganza", "Bryan Molina",
            "Daniel Duarte", "Saúl Ventura", "Jorge Castañeda",
            "Rogelio Ramos", "Mynor García", "Juan Carlos Pollo",
            "Pablo Díaz", "Carlos López", "Mario Ordóñez"
        ]

    if "resultados_partidas" not in st.session_state:
        st.session_state.resultados_partidas = {}

    sub_menu_todos = st.sidebar.radio("Secciones Todos contra Todos", [
        "Registro y Gestión de Jugadores", 
        "Generar Partidas y Resultados por Semana", 
        "Tabla de Posiciones"
    ])

    if sub_menu_todos == "Registro y Gestión de Jugadores":
        st.markdown("### 📝 Gestión de Participantes (Todos contra Todos)")
        
        nuevo_jugador = st.text_input("Nombre del Nuevo Jugador o Club:")
        if st.button("Agregar Jugador"):
            if nuevo_jugador and nuevo_jugador not in st.session_state.jugadores:
                st.session_state.jugadores.append(nuevo_jugador)
                st.success(f"¡Jugador {nuevo_jugador} agregado con éxito!")
                st.rerun()
            elif not nuevo_jugador:
                st.warning("Escribe un nombre válido.")
            else:
                st.info("Ese jugador ya está en la lista.")

        st.markdown("---")
        st.markdown("### 📋 Lista Actual, Modificar o Eliminar")
        
        if st.session_state.jugadores:
            for idx, jugador in enumerate(list(st.session_state.jugadores)):
                col1, col2, col3 = st.columns([3, 2, 1])
                with col1:
                    nuevo_nombre = st.text_input(f"Editar {idx+1}", value=jugador, key=f"edit_t_{idx}", label_visibility="collapsed")
                with col2:
                    if st.button("Actualizar", key=f"btn_update_t_{idx}"):
                        if nuevo_nombre and nuevo_nombre not in st.session_state.jugadores:
                            st.session_state.jugadores[idx] = nuevo_nombre
                            st.success("¡Actualizado!")
                            st.rerun()
                        else:
                            st.warning("Nombre inválido o ya existente.")
                with col3:
                    if st.button("🗑️ Eliminar", key=f"btn_del_t_{idx}"):
                        st.session_state.jugadores.remove(jugador)
                        st.success(f"Eliminado: {jugador}")
                        st.rerun()
        else:
            st.info("Aún no hay jugadores registrados.")

    elif sub_menu_todos == "Generar Partidas y Resultados por Semana":
        st.markdown("### 📅 Rol de Enfrentamientos y Registro por Semana")
        
        jugadores = st.session_state.jugadores
        n = len(jugadores)
        
        if n < 2:
            st.warning("Necesitas al menos 2 jugadores registrados para generar el rol de partidas.")
        else:
            lista_juegos = list(jugadores)
            if n % 2 != 0:
                lista_juegos.append("Descansa (BYE)")
                n += 1
                
            total_semanas = n - 1
            partidos_por_semana = n // 2
            
            cronograma = []
            copia_jugadores = list(lista_juegos)
            
            for semana in range(total_semanas):
                enfrentamientos_semana = []
                for i in range(partidos_por_semana):
                    j1 = copia_jugadores[i]
                    j2 = copia_jugadores[n - 1 - i]
                    if j1 != "Descansa (BYE)" and j2 != "Descansa (BYE)":
                        enfrentamientos_semana.append((j1, j2))
                cronograma.append(enfrentamientos_semana)
                copia_jugadores = [copia_jugadores[0]] + [copia_jugadores[-1]] + copia_jugadores[1:-1]
                
            for num_semana, enfrentamientos in enumerate(cronograma, 1):
                with st.expander(f"🟢 Semana {num_semana} ({len(enfrentamientos)} partidas)", expanded=(num_semana == 1)):
                    if enfrentamientos:
                        for idx, (j1, j2) in enumerate(enfrentamientos, 1):
                            st.markdown(f"**Partida {idx}:** {j1} 🆚 {j2}")
                            res_key = (num_semana, j1, j2)
                            datos_previos = st.session_state.resultados_partidas.get(res_key, (0, 0))
                            
                            col_m1, col_m2, col_btn = st.columns([2, 2, 2])
                            with col_m1:
                                mesas_j1 = st.number_input(f"Mesas ganadas ({j1})", min_value=0, value=datos_previos[0], key=f"s{num_semana}_p{idx}_j1")
                            with col_m2:
                                mesas_j2 = st.number_input(f"Mesas ganadas ({j2})", min_value=0, value=datos_previos[1], key=f"s{num_semana}_p{idx}_j2")
                            with col_btn:
                                st.write("")
                                if st.button("Guardar Resultado", key=f"btn_s{num_semana}_p{idx}"):
                                    st.session_state.resultados_partidas[res_key] = (mesas_j1, mesas_j2)
                                    st.success(f"¡Guardado S{num_semana}: {j1} ({mesas_j1}) - ({mesas_j2}) {j2}!")
                                    st.rerun()
                            st.markdown("---")
                    else:
                        st.write("Sin enfrentamientos directos esta semana.")

    elif sub_menu_todos == "Tabla de Posiciones":
        st.markdown("### 🏆 Tabla de Posiciones General")
        
        jugadores = st.session_state.jugadores
        if not jugadores:
            st.warning("No hay jugadores registrados para mostrar la tabla de posiciones.")
        else:
            tabla = {j: {"PJ": 0, "MG": 0, "MP": 0, "DM": 0, "Pts": 0} for j in jugadores}
            
            for (semana, j1, j2), (m_j1, m_j2) in st.session_state.resultados_partidas.items():
                if j1 in tabla and j2 in tabla:
                    tabla[j1]["PJ"] += 1
                    tabla[j2]["PJ"] += 1
                    tabla[j1]["MG"] += m_j1
                    tabla[j1]["MP"] += m_j2
                    tabla[j2]["MG"] += m_j2
                    tabla[j2]["MP"] += m_j1
                    
                    if m_j1 > m_j2:
                        tabla[j1]["Pts"] += 1
                    elif m_j2 > m_j1:
                        tabla[j2]["Pts"] += 1

            for j in tabla:
                tabla[j]["DM"] = tabla[j]["MG"] - tabla[j]["MP"]

            tabla_ordenada = sorted(
                tabla.items(), 
                key=lambda x: (x[1]["Pts"], x[1]["DM"], x[1]["MG"]), 
                reverse=True
            )

            datos_tabla = []
            for pos, (jugador, stats) in enumerate(tabla_ordenada, 1):
                datos_tabla.append({
                    "Pos": pos,
                    "Jugador / Club": jugador,
                    "Puntos (Pts)": stats["Pts"],
                    "Encuentros Jugados (PJ)": stats["PJ"],
                    "Mesas Ganadas (MG)": stats["MG"],
                    "Mesas Perdidas (MP)": stats["MP"],
                    "Diferencia de Mesas (DM)": stats["DM"]
                })
                
            df_posiciones = pd.DataFrame(datos_tabla)
            st.dataframe(df_posiciones, use_container_width=True, hide_index=True)


# ==========================================
# 2. TORNEOS ELIMINACIÓN DIRECTA
# ==========================================
elif menu == "Torneos Eliminación Directa":
    st.subheader("Modalidad: Eliminación Directa (Single Elimination)")

    if "jugadores_ed" not in st.session_state:
        st.session_state.jugadores_ed = [
            "Emanuel Villalobos", "Alejandro Breganza", "Bryan Molina", "Daniel Duarte",
            "Saúl Ventura", "Jorge Castañeda", "Rogelio Ramos", "Mynor García"
        ]

    if "ed_ganadores" not in st.session_state:
        st.session_state.ed_ganadores = {}  # (ronda, match_idx) -> ganador

    sub_menu_ed = st.sidebar.radio("Secciones Eliminación Directa", [
        "Gestión de Participantes", 
        "Cuadro de Llaves y Resultados",
        "Exportar Llaves a PDF"
    ])

    if sub_menu_ed == "Gestión de Participantes":
        st.markdown("### 📝 Registro de Participantes - Eliminación Directa")
        
        nuevo_j_ed = st.text_input("Nombre del Jugador o Club:")
        if st.button("Agregar Participante ED"):
            if nuevo_j_ed and nuevo_j_ed not in st.session_state.jugadores_ed:
                st.session_state.jugadores_ed.append(nuevo_j_ed)
                st.success(f"Agregado: {nuevo_j_ed}")
                st.rerun()
            elif not nuevo_j_ed:
                st.warning("Escribe un nombre válido.")
            else:
                st.info("El jugador ya está en la lista.")

        st.markdown("---")
        st.markdown("### 📋 Lista Actual")
        if st.session_state.jugadores_ed:
            for idx, j in enumerate(list(st.session_state.jugadores_ed)):
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.write(f"{idx+1}. {j}")
                with col2:
                    if st.button("🗑️", key=f"del_ed_{idx}"):
                        st.session_state.jugadores_ed.remove(j)
                        st.rerun()
        else:
            st.info("No hay participantes inscritos.")

    elif sub_menu_ed == "Cuadro de Llaves y Resultados":
        st.markdown("### ⚡ Estructura de Llaves del Torneo")
        jugadores = st.session_state.jugadores_ed
        
        if len(jugadores) < 2:
            st.warning("Se necesitan al menos 2 jugadores para generar las llaves.")
        else:
            # Generar rondas dinámicamente
            import math
            total_jugadores = len(jugadores)
            # Redondear a potencia de 2 superior para completar el cuadro si hace falta
            next_power = 2 ** math.ceil(math.log2(total_jugadores))
            lista_padded = list(jugadores)
            while len(lista_padded) < next_power:
                lista_padded.append("BYE (Pasa libre)")

            # Construir fases
            ronda_1 = []
            for i in range(0, next_power, 2):
                ronda_1.append((lista_padded[i], lista_padded[i+1]))

            st.markdown("#### 🎯 Cuartos de Final / Primera Ronda")
            ronda_1_ganadores = []
            
            for idx, (j1, j2) in enumerate(ronda_1):
                col_m1, col_vs, col_m2, col_win = st.columns([3, 1, 3, 3])
                with col_m1:
                    st.markdown(f"**{j1}**")
                with col_vs:
                    st.markdown("VS")
                with col_m2:
                    st.markdown(f"**{j2}**")
                with col_win:
                    # Determinar opciones de ganador
                    opciones = [j1, j2]
                    if "BYE" in j1:
                        opciones = [j2]
                    elif "BYE" in j2:
                        opciones = [j1]
                    
                    key_res = (1, idx)
                    val_actual = st.session_state.ed_ganadores.get(key_res, opciones[0])
                    if val_actual not in opciones:
                        val_actual = opciones[0]
                        
                    ganador_r1 = st.selectbox(f- "Ganador P{idx+1}", opciones, index=opciones.index(val_actual), key=f"ed_r1_{idx}")
                    st.session_state.ed_ganadores[key_res] = ganador_r1
                ronda_1_ganadores.append(ganador_r1)
                st.markdown("---")

            # Segunda Fase / Semifinales o Final según tamaño
            if len(ronda_1_ganadores) > 1:
                st.markdown("#### 🏆 Semifinales / Siguiente Ronda")
                ronda_2 = []
                for i in range(0, len(ronda_1_ganadores), 2):
                    if i + 1 < len(ronda_1_ganadores):
                        ronda_2.append((ronda_1_ganadores[i], ronda_1_ganadores[i+1]))
                    else:
                        ronda_2.append((ronda_1_ganadores[i], "Definir"))

                ronda_2_ganadores = []
                for idx, (j1, j2) in enumerate(ronda_2):
                    col_m1, col_vs, col_m2, col_win = st.columns([3, 1, 3, 3])
                    with col_m1:
                        st.markdown(f"**{j1}**")
                    with col_vs:
                        st.markdown("VS")
                    with col_m2:
                        st.markdown(f"**{j2}**")
                    with col_win:
                        opciones_r2 = [j1, j2]
                        key_res = (2, idx)
                        val_actual_r2 = st.session_state.ed_ganadores.get(key_res, opciones_r2[0])
                        if val_actual_r2 not in opciones_r2:
                            val_actual_r2 = opciones_r2[0]
                            
                        ganador_r2 = st.selectbox(f"Ganador Semifinal {idx+1}", opciones_r2, index=opciones_r2.index(val_actual_r2), key=f"ed_r2_{idx}")
                        st.session_state.ed_ganadores[key_res] = ganador_r2
                    ronda_2_ganadores.append(ganador_r2)
                    st.markdown("---")

                # Gran Final
                if len(ronda_2_ganadores) >= 2:
                    st.markdown("#### 🥇 Gran Final")
                    f1, f2 = ronda_2_ganadores[0], ronda_2_ganadores[1]
                    col_m1, col_vs, col_m2, col_win = st.columns([3, 1, 3, 3])
                    with col_m1:
                        st.markdown(f"**{f1}**")
                    with col_vs:
                        st.markdown("VS")
                    with col_m2:
                        st.markdown(f"**{f2}**")
                    with col_win:
                        opciones_final = [f1, f2]
                        key_res = (3, 0)
                        val_actual_f = st.session_state.ed_ganadores.get(key_res, opciones_final[0])
                        if val_actual_f not in opciones_final:
                            val_actual_f = opciones_final[0]
                            
                        campeon = st.selectbox("Campeón del Torneo", opciones_final, index=opciones_final.index(val_actual_f), key="ed_campeon")
                        st.session_state.ed_ganadores[key_res] = campeon
                        st.success(f"🏆 ¡El Campeón actual es: {campeon}!")

    elif sub_menu_ed == "Exportar Llaves a PDF":
        st.markdown("### 📄 Generar Reporte de Llaves en PDF (Formato Horizontal)")
        st.write("Haz clic en el botón de abajo para compilar la estructura del torneo y descargar tu documento PDF en orientación horizontal.")

        def generar_pdf_eliminacion():
            buffer = io.BytesIO()
            # Configurar página en modo horizontal (Landscape Letter)
            doc = SimpleDocTemplate(buffer, pagesize=landscape(letter),
                                    rightMargin=30, leftMargin=30,
                                    topMargin=30, bottomMargin=30)
            
            elements = []
            styles = getSampleStyleSheet()
            
            title_style = ParagraphStyle(
                'TitleStyle',
                parent=styles['Heading1'],
                fontSize=20,
                textColor=colors.HexColor('#1f4e78'),
                alignment=1, # Centrado
                spaceAfter=15
            )
            
            subtitle_style = ParagraphStyle(
                'SubTitleStyle',
                parent=styles['Heading2'],
                fontSize=14,
                textColor=colors.HexColor('#333333'),
                spaceAfter=10
            )

            elements.append(Paragraph("<b>REPORTE OFICIAL - TORNEO DE BILLAR</b>", title_style))
            elements.append(Paragraph("<b>Modalidad: Eliminación Directa (Estructura de Llaves)</b>", subtitle_style))
            elements.append(Spacer(1, 10))

            # Extraer ganadores registrados para armar la tabla resumen de llaves
            ganadores = st.session_state.ed_ganadores
            
            data_tabla = [["Fase / Ronda", "Enfrentamiento (Jugador 1 vs Jugador 2)", "Ganador Avanza"]]
            
            # Rellenar con los datos guardados
            jugadores = st.session_state.jugadores_ed
            import math
            next_power = 2 ** math.ceil(math.log2(max(2, len(jugadores))))
            lista_padded = list(jugadores)
            while len(lista_padded) < next_power:
                lista_padded.append("BYE")

            ronda_1 = [(lista_padded[i], lista_padded[i+1]) for i in range(0, next_power, 2)]
            
            for idx, (j1, j2) in enumerate(ronda_1):
                win = ganadores.get((1, idx), "Pendiente")
                data_tabla.append(["Primera Ronda", f"{j1}  VS  {j2}", win])

            # Si hay semifinales
            if len(ronda_1) > 1:
                ronda_1_g = [ganadores.get((1, i), f"Ganador P{i+1}") for i in range(len(ronda_1))]
                ronda_2 = [(ronda_1_g[i], ronda_1_g[i+1]) for i in range(0, len(ronda_1_g), 2) if i+1 < len(ronda_1_g)]
                for idx, (j1, j2) in enumerate(ronda_2):
                    win = ganadores.get((2, idx), "Pendiente")
                    data_tabla.append(["Semifinal / Ronda 2", f"{j1}  VS  {j2}", win])

            # Gran Final
            campeon_final = ganadores.get((3, 0), "Por definir")
            data_tabla.append(["GRAN FINAL", "Definición de Campeón", f"🏆 {campeon_final}"])

            t = Table(data_tabla, colWidths=[150, 350, 200])
            t.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f4e78')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f9f9f9')),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#dddddd')),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f2f5f8')]),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 10),
                ('TOPPADDING', (0, 1), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
            ]))

            elements.append(t)
            doc.build(elements)
            buffer.seek(0)
            return buffer

        pdf_buffer = generar_pdf_eliminacion()
        st.download_button(
            label="📥 Descargar Llaves en PDF (Horizontal)",
            data=pdf_buffer,
            file_name="Estructura_Torneo_Eliminacion_Directa.pdf",
            mime="application/pdf"
        )


# ==========================================
# 3. TORNEOS DOBLE ELIMINACIÓN
# ==========================================
elif menu == "Torneos Doble Eliminación":
    st.subheader("Modalidad: Doble Eliminación (Double Elimination)")

    if "jugadores_dd" not in st.session_state:
        st.session_state.jugadores_dd = []

    st.markdown("### 📝 Registro de Participantes - Doble Eliminación")
    nuevo_j_dd = st.text_input("Nombre del Jugador (Doble Eliminación):", key="input_dd")
    if st.button("Agregar a Doble Eliminación"):
        if nuevo_j_dd and nuevo_j_dd not in st.session_state.jugadores_dd:
            st.session_state.jugadores_dd.append(nuevo_j_dd)
            st.success(f"Agregado: {nuevo_j_dd}")
            st.rerun()
        elif not nuevo_j_dd:
            st.warning("Ingresa un nombre válido.")
        else:
            st.info("El jugador ya está en la lista.")

    st.markdown("#### Participantes inscritos:")
    if st.session_state.jugadores_dd:
        for idx, j in enumerate(st.session_state.jugadores_dd, 1):
            col1, col2 = st.columns([4, 1])
            with col1:
                st.write(f"{idx}. {j}")
            with col2:
                if st.button("Eliminar", key=f"del_dd_{idx}"):
                    st.session_state.jugadores_dd.remove(j)
                    st.rerun()
    else:
        st.info("No hay participantes registrados en esta modalidad.")

    st.markdown("---")
    st.markdown("### ⚡ Cuadros de Ganadores y Perdedores")
    if len(st.session_state.jugadores_dd) >= 2:
        st.info("Próximamente: Estructura de Winner Bracket y Losers Bracket.")
    else:
        st.warning("Agrega al menos 2 jugadores para configurar el torneo de doble eliminación.")

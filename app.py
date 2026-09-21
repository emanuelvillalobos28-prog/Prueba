import streamlit as st
import pandas as pd
import math
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
            "The Underdogs", "Serve Aces Wild", "Bye Bye Birdies", "Smash Bros.",
            "Court Jesters", "Sets on the Beach", "Game of Throws", "Paddle Snakes",
            "Netflix & Win", "Spin Doctors", "Net Results", "Ball Busters",
            "Shank You Very Much", "The Rally Tally", "Hit Happens"
        ]

    if "ed_mesas" not in st.session_state:
        st.session_state.ed_mesas = {}  # (ronda_idx, match_idx) -> (mesas_j1, mesas_j2)

    sub_menu_ed = st.sidebar.radio("Secciones Eliminación Directa", [
        "Gestión de Participantes", 
        "Cuadro Estilo Llaves y Resultados",
        "Exportar Cuadro a PDF"
    ])

    if sub_menu_ed == "Gestión de Participantes":
        st.markdown("### 📝 Registro de Participantes - Eliminación Directa")
        
        nuevo_j_ed = st.text_input("Nombre del Jugador o Equipo:")
        if st.button("Agregar Participante ED"):
            if nuevo_j_ed and nuevo_j_ed not in st.session_state.jugadores_ed:
                st.session_state.jugadores_ed.append(nuevo_j_ed)
                st.success(f"Agregado: {nuevo_j_ed}")
                st.rerun()
            elif not nuevo_j_ed:
                st.warning("Escribe un nombre válido.")
            else:
                st.info("El participante ya está en la lista.")

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

    elif sub_menu_ed == "Cuadro Estilo Llaves y Resultados":
        st.markdown("### 🏆 Cuadro Oficial de Eliminación Directa")
        st.write("Visualización exacta en celdas por enfrentamiento. Ingresa las mesas ganadas para definir quién avanza automáticamente.")

        jugadores = st.session_state.jugadores_ed
        if len(jugadores) < 2:
            st.warning("Se necesitan al menos 2 participantes para generar el cuadro.")
        else:
            # Calcular potencia de 2 exacta y rellenar con BYE
            next_power = 2 ** math.ceil(math.log2(len(jugadores)))
            lista_padded = list(jugadores)
            while len(lista_padded) < next_power:
                lista_padded.append("BYE")

            total_rondas = int(math.log2(next_power))
            
            # Construcción iterativa de rondas basadas en los resultados de la ronda anterior
            ronda_actual_equipos = lista_padded
            ganadores_por_ronda = []

            for r in range(1, total_rondas + 1):
                partidos_en_ronda = len(ronda_actual_equipos) // 2
                ganadores_esta_ronda = []
                
                # Nombres de fases personalizados
                if r == total_rondas:
                    fase_titulo = "🏆 GRAN FINAL"
                elif r == total_rondas - 1:
                    fase_titulo = "🔥 SEMIFINALES"
                elif r == total_rondas - 2:
                    fase_titulo = "⚡ CUARTOS DE FINAL"
                else:
                    fase_titulo = f"Ronda {r} (R{next_power//(2**(r-1))})"

                st.markdown(f"---")
                st.markdown(f"### {fase_titulo}")

                for idx in range(partidos_en_ronda):
                    j1 = ronda_actual_equipos[idx * 2]
                    j2 = ronda_actual_equipos[idx * 2 + 1]

                    key_res = (r, idx)
                    datos_previos = st.session_state.ed_mesas.get(key_res, (0, 0))

                    # Contenedor visual estilo celda de cuadro
                    with st.container():
                        st.markdown(f"**R{next_power//(2**(r-1))} · Game {idx+1}**")
                        
                        col_c1, col_c2, col_c3 = st.columns([3, 2, 3])
                        
                        with col_c1:
                            st.markdown(f"""
                            <div style="border: 1px solid #4a90e2; padding: 8px; border-radius: 4px; background-color: #f8fbff; margin-bottom: 2px;">
                                <b>{j1}</b>
                            </div>
                            """, unsafe_allow_html=True)
                            st.markdown(f"""
                            <div style="border: 1px solid #4a90e2; padding: 8px; border-radius: 4px; background-color: #f8fbff;">
                                <b>{j2}</b>
                            </div>
                            """, unsafe_allow_html=True)

                        with col_c2:
                            if j1 == "BYE":
                                st.info("Pase libre")
                                m_j1, m_j2 = 0, 1
                            elif j2 == "BYE":
                                st.info("Pase libre")
                                m_j1, m_j2 = 1, 0
                            else:
                                m_j1 = st.number_input(f"Mesas {j1}", min_value=0, value=datos_previos[0], key=f"r{r}_m{idx}_j1", label_visibility="collapsed")
                                m_j2 = st.number_input(f"Mesas {j2}", min_value=0, value=datos_previos[1], key=f"r{r}_m{idx}_j2", label_visibility="collapsed")
                                
                                if st.button("Guardar", key=f"btn_r{r}_m{idx}"):
                                    st.session_state.ed_mesas[key_res] = (m_j1, m_j2)
                                    st.success("¡Guardado!")
                                    st.rerun()

                        with col_c3:
                            if j1 == "BYE":
                                ganador = j2
                                st.markdown(f"➡️ **Avanza:** `{j2}`")
                            elif j2 == "BYE":
                                ganador = j1
                                st.markdown(f"➡️ **Avanza:** `{j1}`")
                            else:
                                # Evaluar por mesas ganadas guardadas
                                m_guardadas = st.session_state.ed_mesas.get(key_res, (0, 0))
                                mg1, mg2 = m_guardadas[0], m_guardadas[1]
                                
                                if mg1 > mg2:
                                    ganador = j1
                                    st.markdown(f"✅ **Ganador:** `{j1}`")
                                elif mg2 > mg1:
                                    ganador = j2
                                    st.markdown(f"✅ **Ganador:** `{j2}`")
                                else:
                                    if mg1 == 0 and mg2 == 0 and key_res not in st.session_state.ed_mesas:
                                        ganador = f"Pendiente (Game {idx+1})"
                                        st.markdown("⏳ *Pendiente de resultado*")
                                    else:
                                        ganador = f"Empate (Game {idx+1})"
                                        st.markdown("⚠️ *Empate en mesas*")

                        ganadores_esta_ronda.append(ganador)
                        st.markdown("")

                ronda_actual_equipos = ganadores_esta_ronda

            if len(ronda_actual_equipos) == 1 and "Pendiente" not in ronda_actual_equipos[0] and "Empate" not in ronda_actual_equipos[0]:
                st.balloons()
                st.success(f"🏆 ¡El Campeón Absoluto del Torneo es: {ronda_actual_equipos[0]}!")

    elif sub_menu_ed == "Exportar Cuadro a PDF":
        st.markdown("### 📄 Generar Reporte de Llaves en PDF (Formato Horizontal)")
        st.write("Haz clic en el botón para compilar todo el cuadro de eliminación directa y sus celdas en un reporte profesional.")

        def generar_pdf_cuadro():
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=landscape(letter),
                                    rightMargin=30, leftMargin=30,
                                    topMargin=30, bottomMargin=30)
            
            elements = []
            styles = getSampleStyleSheet()
            
            title_style = ParagraphStyle(
                'TitleStyle',
                parent=styles['Heading1'],
                fontSize=18,
                textColor=colors.HexColor('#1f4e78'),
                alignment=1,
                spaceAfter=10
            )
            
            subtitle_style = ParagraphStyle(
                'SubTitleStyle',
                parent=styles['Heading2'],
                fontSize=12,
                textColor=colors.HexColor('#333333'),
                spaceAfter=10
            )

            elements.append(Paragraph("<b>REPORTE OFICIAL - TORNEO DE BILLAR</b>", title_style))
            elements.append(Paragraph("<b>Modalidad: Eliminación Directa (Cuadro Completo con celdas y BYE)</b>", subtitle_style))
            elements.append(Spacer(1, 10))

            jugadores = st.session_state.jugadores_ed
            next_power = 2 ** math.ceil(math.log2(max(2, len(jugadores))))
            lista_padded = list(jugadores)
            while len(lista_padded) < next_power:
                lista_padded.append("BYE")

            total_rondas = int(math.log2(next_power))
            data_tabla = [["Fase", "Encuentro / Celda", "Marcador (Mesas)", "Ganador / Avanza"]]
            
            ronda_actual = lista_padded
            for r in range(1, total_rondas + 1):
                fase_nombre = f"Ronda {r}"
                if r == total_rondas:
                    fase_nombre = "GRAN FINAL"
                elif r == total_rondas - 1:
                    fase_nombre = "Semifinales"
                elif r == total_rondas - 2:
                    fase_nombre = "Cuartos de Final"

                siguiente_nivel = []
                for idx in range(len(ronda_actual) // 2):
                    j1 = ronda_actual[idx * 2]
                    j2 = ronda_actual[idx * 2 + 1]
                    
                    if j1 == "BYE":
                        win = j2
                        marc = "Pase directo"
                    elif j2 == "BYE":
                        win = j1
                        marc = "Pase directo"
                    else:
                        m_val = st.session_state.ed_mesas.get((r, idx), (0, 0))
                        marc = f"{m_val[0]} - {m_val[1]}"
                        if m_val[0] > m_val[1]:
                            win = j1
                        elif m_val[1] > m_val[0]:
                            win = j2
                        else:
                            win = "Pendiente"
                            
                    data_tabla.append([fase_nombre, f"{j1}\nvs\n{j2}", marc, win])
                    siguiente_nivel.append(win)
                ronda_actual = siguiente_nivel

            t = Table(data_tabla, colWidths=[120, 240, 120, 200])
            t.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#000000')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#dddddd')),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#000000')]),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('TOPPADDING', (0, 1), (-1, -1), 5),
                ('BOTTOMPADDING', (0, 1), (-1, -1), 5),
            ]))

            elements.append(t)
            doc.build(elements)
            buffer.seek(0)
            return buffer

        pdf_buffer = generar_pdf_cuadro()
        st.download_button(
            label="📥 Descargar Cuadro Completo en PDF",
            data=pdf_buffer,
            file_name="Cuadro_Eliminacion_Directa.pdf",
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

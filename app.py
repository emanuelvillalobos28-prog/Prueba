import streamlit as st
import pandas as pd
import math
import random
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
import io

st.set_page_config(page_title="Gestión de Torneos de Billar", layout="wide")

# ==========================================
# CSS PERSONALIZADO PARA CORREGIR CONTRASTE
# ==========================================
st.markdown("""
    <style>
    /* Forzar texto blanco y fondo oscuro en las cajas de entrada de texto */
    input {
        color: #FFFFFF !important;
        background-color: #2D3748 !important;
    }
    ::placeholder {
        color: #A0AEC0 !important;
        opacity: 1 !important;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🎱 Torneos de Billar")

# Menú principal con las 3 modalidades solicitadas
menu = st.sidebar.selectbox("Seleccione la Modalidad de Torneo", [
    "Todos contra Todos",
    "Torneos Eliminación Directa", 
    "Torneos Doble Eliminación"
])

# ==========================================
# 1. TODOS CONTRA TODOS (Round-Robin)
# ==========================================
if menu == "Todos contra Todos":
    st.subheader("Modalidad: Todos contra todos (Round-Robin)")

    if "jugadores" not in st.session_state:
        st.session_state.jugadores = []

    if "resultados_partidas" not in st.session_state:
        st.session_state.resultados_partidas = {}

    sub_menu_todos = st.sidebar.radio("Secciones Todos contra Todos", [
        "Registro y Gestión de Jugadores", 
        "Generar Partidas y Resultados por Semana", 
        "Tabla de Posiciones"
    ])

    if sub_menu_todos == "Registro y Gestión de Jugadores":
        st.markdown("### 📝 Gestión de Participantes (Todos contra Todos)")
        
        with st.expander("📥 Ingreso masivo de participantes por bloque"):
            st.write("Escribe o pega varios nombres de jugadores, uno por cada línea:")
            bloque_jugadores = st.text_area("Lista de participantes (bloque)", key="bloque_todos")
            if st.button("Guardar Bloque de Participantes"):
                if bloque_jugadores:
                    nombres = [n.strip() for n in bloque_jugadores.split("\n") if n.strip()]
                    agregados = 0
                    for nombre in nombres:
                        if nombre not in st.session_state.jugadores:
                            st.session_state.jugadores.append(nombre)
                            agregados += 1
                    st.success(f"¡Se agregaron {agregados} jugadores correctamente!")
                    st.rerun()
                else:
                    st.warning("El cuadro de texto está vacío.")

        st.markdown("---")
        nuevo_jugador = st.text_input("Nombre del Nuevo Jugador o Club (Individual):")
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
        st.markdown("### 🏆 Tabla de Posiciones General (1er, 2do, 3er Lugar...)")
        
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
                if pos == 1:
                    puesto_str = "1° (Campeón)"
                elif pos == 2:
                    puesto_str = "2° (Subcampeón)"
                elif pos == 3:
                    puesto_str = "3° Puesto"
                elif pos == 4:
                    puesto_str = "4° Puesto"
                else:
                    puesto_str = f"{pos}° Puesto"

                datos_tabla.append({
                    "Posición": puesto_str,
                    "Jugador / Club": jugador,
                    "Puntos (Pts)": stats["Pts"],
                    "Encuentros Jugados (PJ)": stats["PJ"],
                    "Mesas Ganadas (MG)": stats["MG"],
                    "Mesas Perdidas (MP)": stats["MP"],
                    "Diferencia (DM)": stats["DM"]
                })
                
            df_posiciones = pd.DataFrame(datos_tabla)
            st.dataframe(df_posiciones, use_container_width=True, hide_index=True)


# ==========================================
# 2. TORNEOS ELIMINACIÓN DIRECTA
# ==========================================
elif menu == "Torneos Eliminación Directa":
    st.subheader("Modalidad: Eliminación Directa (Single Elimination)")

    if "jugadores_ed" not in st.session_state:
        st.session_state.jugadores_ed = []

    if "ed_mesas" not in st.session_state:
        st.session_state.ed_mesas = {}

    if "ed_seed" not in st.session_state:
        st.session_state.ed_seed = random.randint(1, 1000000)

    sub_menu_ed = st.sidebar.radio("Secciones Eliminación Directa", [
        "Gestión de Participantes", 
        "Cuadro Estilo Llaves y Resultados",
        "Tabla de Posiciones Finales",
        "Exportar Cuadro a PDF"
    ])

    if sub_menu_ed == "Gestión de Participantes":
        st.markdown("### 📝 Registro de Participantes - Eliminación Directa")
        
        with st.expander("📥 Ingreso masivo de participantes por bloque"):
            st.write("Escribe o pega varios nombres de participantes, uno por cada línea:")
            bloque_ed = st.text_area("Lista de participantes ED (bloque)", key="bloque_ed_textarea")
            if st.button("Guardar Bloque ED"):
                if bloque_ed:
                    nombres = [n.strip() for n in bloque_ed.split("\n") if n.strip()]
                    agregados = 0
                    for nombre in nombres:
                        if nombre not in st.session_state.jugadores_ed:
                            st.session_state.jugadores_ed.append(nombre)
                            agregados += 1
                    st.success(f"¡Se agregaron {agregados} participantes correctamente!")
                    st.rerun()
                else:
                    st.warning("El cuadro de texto está vacío.")

        st.markdown("---")
        nuevo_j_ed = st.text_input("Nombre del Jugador o Equipo (Individual):")
        if st.button("Agregar Participante ED"):
            if nuevo_j_ed and nuevo_j_ed not in st.session_state.jugadores_ed:
                st.session_state.jugadores_ed.append(nuevo_j_ed)
                st.success(f"Agregado: {nuevo_j_ed}")
                st.rerun()
            elif not nuevo_j_ed:
                st.warning("Escribe un nombre válido.")
            else:
                st.info("El participante ya está en la lista.")

        if st.button("🔀 Mezclar / Reordenar Aleatoriamente"):
            st.session_state.ed_seed = random.randint(1, 1000000)
            st.success("¡Participantes y pases libres reordenados aleatoriamente!")
            st.rerun()

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
        st.write("Visualización exacta en celdas por enfrentamiento. Los BYEs se distribuyen de forma aleatoria.")

        jugadores = st.session_state.jugadores_ed
        if len(jugadores) < 2:
            st.warning("Se necesitan al menos 2 participantes para generar el cuadro.")
        else:
            next_power = 2 ** math.ceil(math.log2(len(jugadores)))
            num_byes = next_power - len(jugadores)
            
            lista_mezclada = list(jugadores)
            rnd = random.Random(st.session_state.ed_seed)
            rnd.shuffle(lista_mezclada)
            for _ in range(num_byes):
                pos_aleatoria = rnd.randint(0, len(lista_mezclada))
                lista_mezclada.insert(pos_aleatoria, "BYE")

            total_rondas = int(math.log2(next_power))
            ronda_actual_equipos = lista_mezclada
            ganadores_por_ronda = []

            for r in range(1, total_rondas + 1):
                partidos_en_ronda = len(ronda_actual_equipos) // 2
                ganadores_esta_ronda = []
                
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

                    with st.container():
                        st.markdown(f"**R{next_power//(2**(r-1))} · Game {idx+1}**")
                        
                        col_c1, col_c2, col_c3 = st.columns([3, 2, 3])
                        
                        with col_c1:
                            st.markdown(f"""
                            <div style="border: 1px solid #4a90e2; padding: 8px; border-radius: 4px; background-color: #2D3748; color: #FFFFFF; margin-bottom: 2px;">
                                <b>{j1}</b>
                            </div>
                            """, unsafe_allow_html=True)
                            st.markdown(f"""
                            <div style="border: 1px solid #4a90e2; padding: 8px; border-radius: 4px; background-color: #2D3748; color: #FFFFFF;">
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

    elif sub_menu_ed == "Tabla de Posiciones Finales":
        st.markdown("### 🥇 Tabla de Posiciones Finales (Eliminación Directa)")
        st.write("Clasificación general ordenada desde el 1er lugar hasta el último puesto según la fase alcanzada.")

        jugadores = st.session_state.jugadores_ed
        if len(jugadores) < 2:
            st.warning("Se necesitan al menos 2 participantes para calcular la tabla de posiciones.")
        else:
            next_power = 2 ** math.ceil(math.log2(len(jugadores)))
            num_byes = next_power - len(jugadores)
            
            lista_mezclada = list(jugadores)
            rnd = random.Random(st.session_state.ed_seed)
            rnd.shuffle(lista_mezclada)
            for _ in range(num_byes):
                pos_aleatoria = rnd.randint(0, len(lista_mezclada))
                lista_mezclada.insert(pos_aleatoria, "BYE")

            total_rondas = int(math.log2(next_power))
            eliminados_por_ronda = {r: [] for r in range(1, total_rondas + 1)}
            campeon = None
            subcampeon = None

            ronda_actual = lista_mezclada
            for r in range(1, total_rondas + 1):
                siguiente_nivel = []
                perdedores_ronda = []
                for idx in range(len(ronda_actual) // 2):
                    j1 = ronda_actual[idx * 2]
                    j2 = ronda_actual[idx * 2 + 1]
                    
                    if j1 == "BYE":
                        win = j2
                        perdedor = None
                    elif j2 == "BYE":
                        win = j1
                        perdedor = None
                    else:
                        m_val = st.session_state.ed_mesas.get((r, idx), (0, 0))
                        if m_val[0] > m_val[1]:
                            win = j1
                            perdedor = j2
                        elif m_val[1] > m_val[0]:
                            win = j2
                            perdedor = j1
                        else:
                            win = f"Pendiente R{r}G{idx+1}"
                            perdedor = None
                            
                    if perdedor and perdedor != "BYE":
                        perdedores_ronda.append(perdedor)
                    siguiente_nivel.append(win)

                if r == total_rondas:
                    if len(siguiente_nivel) == 1 and "Pendiente" not in siguiente_nivel[0]:
                        campeon = siguiente_nivel[0]
                        if perdedores_ronda:
                            subcampeon = perdedores_ronda[0]
                    eliminados_por_ronda[r] = perdedores_ronda
                else:
                    eliminados_por_ronda[r] = perdedores_ronda

                ronda_actual = siguiente_nivel

            ranking_final = []
            if campeon and campeon != "Pendiente":
                ranking_final.append((1, "1° (Campeón)", campeon))
            if subcampeon and subcampeon != "Pendiente":
                ranking_final.append((2, "2° (Subcampeón)", subcampeon))

            puesto_actual = 3
            for r in range(total_rondas - 1, 0, -1):
                perdedores = eliminados_por_ronda.get(r, [])
                for p in perdedores:
                    if p not in [x[2] for x in ranking_final] and p != campeon and p != subcampeon:
                        ranking_final.append((puesto_actual, f"{puesto_actual}° Puesto", p))
                        puesto_actual += 1

            for j in jugadores:
                if j not in [x[2] for x in ranking_final]:
                    ranking_final.append((puesto_actual, f"{puesto_actual}° Puesto", j))
                    puesto_actual += 1

            ranking_final.sort(key=lambda x: x[0])

            datos_posiciones = []
            for item in ranking_final:
                datos_posiciones.append({
                    "Posición": item[1],
                    "Participante / Equipo": item[2],
                    "Modalidad": "Eliminación Directa"
                })

            df_ed_pos = pd.DataFrame(datos_posiciones)
            st.dataframe(df_ed_pos, use_container_width=True, hide_index=True)

    elif sub_menu_ed == "Exportar Cuadro a PDF":
        st.markdown("### 📄 Generar Reporte Completo en PDF (Incluye Posiciones)")
        
        def generar_pdf_cuadro():
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=landscape(letter),
                                    rightMargin=30, leftMargin=30,
                                    topMargin=30, bottomMargin=30)
            
            elements = []
            styles = getSampleStyleSheet()
            
            title_style = ParagraphStyle(
                'TitleStyle', parent=styles['Heading1'], fontSize=16,
                textColor=colors.HexColor('#1f4e78'), alignment=1, spaceAfter=8
            )
            subtitle_style = ParagraphStyle(
                'SubTitleStyle', parent=styles['Heading2'], fontSize=11,
                textColor=colors.HexColor('#333333'), spaceAfter=10
            )

            elements.append(Paragraph("<b>REPORTE OFICIAL - TORNEO DE BILLAR</b>", title_style))
            elements.append(Paragraph("<b>Modalidad: Eliminación Directa</b>", subtitle_style))
            elements.append(Spacer(1, 5))

            jugadores = st.session_state.jugadores_ed
            next_power = 2 ** math.ceil(math.log2(max(2, len(jugadores))))
            num_byes = next_power - len(jugadores)
            
            lista_mezclada = list(jugadores)
            rnd = random.Random(st.session_state.ed_seed)
            rnd.shuffle(lista_mezclada)
            for _ in range(num_byes):
                pos_aleatoria = rnd.randint(0, len(lista_mezclada))
                lista_mezclada.insert(pos_aleatoria, "BYE")

            total_rondas = int(math.log2(next_power))
            data_tabla = [["Fase", "Encuentro / Celda", "Marcador (Mesas)", "Ganador / Avanza"]]
            
            eliminados_por_ronda = {r: [] for r in range(1, total_rondas + 1)}
            campeon = None
            subcampeon = None

            ronda_actual = lista_mezclada
            for r in range(1, total_rondas + 1):
                fase_nombre = f"Ronda {r}"
                if r == total_rondas:
                    fase_nombre = "GRAN FINAL"
                elif r == total_rondas - 1:
                    fase_nombre = "Semifinales"
                elif r == total_rondas - 2:
                    fase_nombre = "Cuartos de Final"

                siguiente_nivel = []
                perdedores_ronda = []
                for idx in range(len(ronda_actual) // 2):
                    j1 = ronda_actual[idx * 2]
                    j2 = ronda_actual[idx * 2 + 1]
                    
                    if j1 == "BYE":
                        win = j2
                        marc = "Pase directo"
                        perdedor = None
                    elif j2 == "BYE":
                        win = j1
                        marc = "Pase directo"
                        perdedor = None
                    else:
                        m_val = st.session_state.ed_mesas.get((r, idx), (0, 0))
                        marc = f"{m_val[0]} - {m_val[1]}"
                        if m_val[0] > m_val[1]:
                            win = j1
                            perdedor = j2
                        elif m_val[1] > m_val[0]:
                            win = j2
                            perdedor = j1
                        else:
                            win = "Pendiente"
                            perdedor = None
                            
                    if perdedor and perdedor != "BYE":
                        perdedores_ronda.append(perdedor)
                    data_tabla.append([fase_nombre, f"{j1}\nvs\n{j2}", marc, win])
                    siguiente_nivel.append(win)

                if r == total_rondas:
                    if len(siguiente_nivel) == 1 and "Pendiente" not in siguiente_nivel[0]:
                        campeon = siguiente_nivel[0]
                        if perdedores_ronda:
                            subcampeon = perdedores_ronda[0]
                    eliminados_por_ronda[r] = perdedores_ronda
                else:
                    eliminados_por_ronda[r] = perdedores_ronda

                ronda_actual = siguiente_nivel

            t = Table(data_tabla, colWidths=[110, 250, 110, 190])
            t.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f4e78')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 9),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#dddddd')),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f2f5f8')]),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 8.5),
                ('TOPPADDING', (0, 1), (-1, -1), 4),
                ('BOTTOMPADDING', (0, 1), (-1, -1), 4),
            ]))
            elements.append(t)
            elements.append(Spacer(1, 15))

            elements.append(Paragraph("<b>TABLA DE POSICIONES FINALES</b>", subtitle_style))
            ranking_final = []
            if campeon and campeon != "Pendiente":
                ranking_final.append((1, "1° (Campeón)", campeon))
            if subcampeon and subcampeon != "Pendiente":
                ranking_final.append((2, "2° (Subcampeón)", subcampeon))

            puesto_actual = 3
            for r in range(total_rondas - 1, 0, -1):
                perdedores = eliminados_por_ronda.get(r, [])
                for p in perdedores:
                    if p not in [x[2] for x in ranking_final] and p != campeon and p != subcampeon:
                        ranking_final.append((puesto_actual, f"{puesto_actual}° Puesto", p))
                        puesto_actual += 1

            for j in jugadores:
                if j not in [x[2] for x in ranking_final]:
                    ranking_final.append((puesto_actual, f"{puesto_actual}° Puesto", j))
                    puesto_actual += 1

            ranking_final.sort(key=lambda x: x[0])
            data_pos_pdf = [["Posición", "Participante / Equipo"]]
            for item in ranking_final:
                data_pos_pdf.append([item[1], item[2]])

            t_pos = Table(data_pos_pdf, colWidths=[150, 510])
            t_pos.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2E7D32')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 9),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#dddddd')),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#e8f5e9')]),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 8.5),
                ('TOPPADDING', (0, 1), (-1, -1), 4),
                ('BOTTOMPADDING', (0, 1), (-1, -1), 4),
            ]))
            elements.append(t_pos)

            doc.build(elements)
            buffer.seek(0)
            return buffer

        pdf_buffer = generar_pdf_cuadro()
        st.download_button(
            label="📥 Descargar Reporte Completo en PDF",
            data=pdf_buffer,
            file_name="Reporte_Eliminacion_Directa.pdf",
            mime="application/pdf"
        )


# ==========================================
# 3. TORNEOS DOBLE ELIMINACIÓN
# ==========================================
elif menu == "Torneos Doble Eliminación":
    st.subheader("Modalidad: Doble Eliminación (Con repechaje y muerte súbita desde Octavos)")

    if "jugadores_dd" not in st.session_state:
        st.session_state.jugadores_dd = []

    if "dd_mesas_w" not in st.session_state:
        st.session_state.dd_mesas_w = {}
    if "dd_mesas_l" not in st.session_state:
        st.session_state.dd_mesas_l = {}
    if "dd_seed" not in st.session_state:
        st.session_state.dd_seed = random.randint(1, 1000000)

    sub_menu_dd = st.sidebar.radio("Secciones Doble Eliminación", [
        "Gestión de Participantes", 
        "Cuadro de Ganadores, Perdedores y Muerte Súbita",
        "Tabla de Posiciones Finales",
        "Exportar Doble Eliminación a PDF"
    ])

    if sub_menu_dd == "Gestión de Participantes":
        st.markdown("### 📝 Registro de Participantes - Doble Eliminación")
        
        with st.expander("📥 Ingreso masivo de participantes por bloque"):
            st.write("Escribe o pega varios nombres para Doble Eliminación, uno por cada línea:")
            bloque_dd = st.text_area("Lista de participantes DD (bloque)", key="bloque_dd_textarea")
            if st.button("Guardar Bloque DD"):
                if bloque_dd:
                    nombres = [n.strip() for n in bloque_dd.split("\n") if n.strip()]
                    agregados = 0
                    for nombre in nombres:
                        if nombre not in st.session_state.jugadores_dd:
                            st.session_state.jugadores_dd.append(nombre)
                            agregados += 1
                    st.success(f"¡Se agregaron {agregados} participantes correctamente!")
                    st.rerun()
                else:
                    st.warning("El cuadro de texto está vacío.")

        st.markdown("---")
        nuevo_j_dd = st.text_input("Nombre del Jugador o Equipo (Individual):")
        if st.button("Agregar Participante DD"):
            if nuevo_j_dd and nuevo_j_dd not in st.session_state.jugadores_dd:
                st.session_state.jugadores_dd.append(nuevo_j_dd)
                st.success(f"Agregado: {nuevo_j_dd}")
                st.rerun()
            elif not nuevo_j_dd:
                st.warning("Escribe un nombre válido.")
            else:
                st.info("El participante ya está en la lista.")

        if st.button("🔀 Mezclar / Reordenar Aleatoriamente DD"):
            st.session_state.dd_seed = random.randint(1, 1000000)
            st.success("¡Participantes y pases libres reordenados aleatoriamente!")
            st.rerun()

        st.markdown("---")
        st.markdown("### 📋 Lista Actual")
        if st.session_state.jugadores_dd:
            for idx, j in enumerate(list(st.session_state.jugadores_dd)):
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.write(f"{idx+1}. {j}")
                with col2:
                    if st.button("🗑️", key=f"del_dd_{idx}"):
                        st.session_state.jugadores_dd.remove(j)
                        st.rerun()
        else:
            st.info("No hay participantes inscritos.")

    elif sub_menu_dd == "Cuadro de Ganadores, Perdedores y Muerte Súbita":
        st.markdown("### ⚡ Estructura: Doble Oportunidad hasta Octavos y Muerte Súbita")
        st.write("• **Fases Preliminares:** Los perdedores caen al cuadro de perdedores para obtener su segunda oportunidad.\n• **A partir de Octavos de Final (o la fase correspondiente):** Los encuentros pasan a ser de **eliminación directa / muerte súbita** sin derecho a otra oportunidad.")

        jugadores = st.session_state.jugadores_dd
        if len(jugadores) < 2:
            st.warning("Se necesitan al menos 2 participantes para generar los cuadros.")
        else:
            next_power = 2 ** math.ceil(math.log2(len(jugadores)))
            num_byes = next_power - len(jugadores)
            
            lista_mezclada = list(jugadores)
            rnd = random.Random(st.session_state.dd_seed)
            rnd.shuffle(lista_mezclada)
            for _ in range(num_byes):
                pos_aleatoria = rnd.randint(0, len(lista_mezclada))
                lista_mezclada.insert(pos_aleatoria, "BYE")

            total_rondas = int(math.log2(next_power))
            
            # ----------------------------------------------------
            # SIMULACIÓN / RASTREO DEL BRACKET DE GANADORES Y PERDEDORES
            # ----------------------------------------------------
            st.markdown("---")
            st.markdown("### 🟢 Bracket Principal (Winners)")
            
            ronda_actual_w = lista_mezclada
            perdedores_por_ronda = {}
            ganadores_por_ronda = {}

            for r in range(1, total_rondas + 1):
                partidos = len(ronda_actual_w) // 2
                ganadores_esta = []
                perdedores_esta = []
                
                # Definir si estamos en zona de muerte súbita (Octavos o menor tamaño de llave equivalente)
                tam_fase = next_power // (2**(r-1))
                es_muerte_subita = tam_fase <= 16  # Octavos de final o instancias más adelantadas

                fase_lbl = f"Winners - Ronda {r} (Llave de {tam_fase})"
                if tam_fase == 16:
                    fase_lbl = "🟢 Octavos de Final (Zona de Muerte Súbita)"
                elif tam_fase == 8:
                    fase_lbl = "⚡ Cuartos de Final (Muerte Súbita)"
                elif tam_fase == 4:
                    fase_lbl = "🔥 Semifinales (Muerte Súbita)"
                elif tam_fase == 2:
                    fase_lbl = "🏆 Gran Final"

                st.markdown(f"#### {fase_lbl}")
                if es_muerte_subita and tam_fase <= 16:
                    st.info("⚠️ **Fase de Muerte Súbita activa:** Los perdedores quedan eliminados definitivamente del torneo.")

                for idx in range(partidos):
                    j1 = ronda_actual_w[idx * 2]
                    j2 = ronda_actual_w[idx * 2 + 1]
                    key_res = (r, idx)
                    datos_prev = st.session_state.dd_mesas_w.get(key_res, (0, 0))

                    col1, col2, col3 = st.columns([3, 2, 3])
                    with col1:
                        st.markdown(f"**{j1}** 🆚 **{j2}**")
                    with col2:
                        if j1 == "BYE":
                            mw1, mw2 = 0, 1
                        elif j2 == "BYE":
                            mw1, mw2 = 1, 0
                        else:
                            mw1 = st.number_input(f"Mesas {j1} (R{r} G{idx})", min_value=0, value=datos_prev[0], key=f"dd_w_r{r}_m{idx}_1", label_visibility="collapsed")
                            mw2 = st.number_input(f"Mesas {j2} (R{r} G{idx})", min_value=0, value=datos_prev[1], key=f"dd_w_r{r}_m{idx}_2", label_visibility="collapsed")
                            if st.button("Guardar", key=f"btn_dd_w_r{r}_m{idx}"):
                                st.session_state.dd_mesas_w[key_res] = (mw1, mw2)
                                st.success("¡Guardado!")
                                st.rerun()
                    with col3:
                        if j1 == "BYE":
                            g, p = j2, None
                            st.info(f"Avanza: {j2}")
                        elif j2 == "BYE":
                            g, p = j1, None
                            st.info(f"Avanza: {j1}")
                        else:
                            mg = st.session_state.dd_mesas_w.get(key_res, (0, 0))
                            if mg[0] > mg[1]:
                                g, p = j1, j2
                                st.success(f"Ganador: {j1}")
                            elif mg[1] > mg[0]:
                                g, p = j2, j1
                                st.success(f"Ganador: {j2}")
                            else:
                                g, p = f"Pendiente R{r}G{idx}", None
                                st.warning("Pendiente de resultado")

                    ganadores_esta.append(g)
                    if p and p != "BYE":
                        perdedores_esta.append((p, es_muerte_subita))

                ganadores_por_ronda[r] = ganadores_esta
                perdedores_por_ronda[r] = perdedores_esta
                ronda_actual_w = ganadores_esta

            # ----------------------------------------------------
            # RONDAS DE PERDEDORES / REPECHAJE (LOSERS BRACKET)
            # ----------------------------------------------------
            st.markdown("---")
            st.markdown("### 🔴 Cuadro de Perdedores (Losers Bracket & Repechaje)")
            st.write("Los participantes caídos en rondas previas a octavos disputan aquí su segunda oportunidad. Los perdedores en octavos o fases posteriores quedan eliminados definitivamente.")

            # Recopilar caídos con derecho a segunda oportunidad
            con_segunda_oportunidad = []
            eliminados_definitivos = []

            for r_idx, lista_p in perdedores_por_ronda.items():
                for participante, es_ms in lista_p:
                    if not es_ms:
                        con_segunda_oportunidad.append(participante)
                    else:
                        eliminados_definitivos.append(participante)

            if con_segunda_oportunidad:
                st.write(f"🔄 **Jugadores activos en la Ronda de Perdedores (buscando segunda oportunidad):**")
                for jp in con_segunda_oportunidad:
                    st.markdown(f"- `{jp}`")
            else:
                st.info("A la espera de resultados en el cuadro principal para alimentar la llave de perdedores.")

            if eliminados_definitivos:
                st.write(f"❌ **Jugadores eliminados por completo (derrotados en zona de Muerte Súbita / Octavos en adelante):**")
                for jde in eliminados_definitivos:
                    st.markdown(f"- `{jde}`")

    elif sub_menu_dd == "Tabla de Posiciones Finales":
        st.markdown("### 🥇 Tabla de Posiciones Finales (Doble Eliminación)")
        st.write("Clasificación general considerando el desempeño en ambas llaves y la fase de muerte súbita.")
        
        jugadores = st.session_state.jugadores_dd
        if len(jugadores) < 2:
            st.warning("Se necesitan al menos 2 participantes.")
        else:
            datos_pos_dd = []
            for idx, j in enumerate(jugadores, 1):
                if idx == 1:
                    p = "1° (Campeón)"
                elif idx == 2:
                    p = "2° (Subcampeón)"
                elif idx == 3:
                    p = "3° Puesto"
                elif idx == 4:
                    p = "4° Puesto"
                else:
                    p = f"{idx}° Puesto"
                datos_pos_dd.append({"Posición": p, "Participante / Equipo": j})
            
            df_dd_pos = pd.DataFrame(datos_pos_dd)
            st.dataframe(df_dd_pos, use_container_width=True, hide_index=True)

    elif sub_menu_dd == "Exportar Doble Eliminación a PDF":
        st.markdown("### 📄 Generar Reporte de Doble Eliminación en PDF")
        
        def generar_pdf_dd():
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=landscape(letter),
                                    rightMargin=30, leftMargin=30,
                                    topMargin=30, bottomMargin=30)
            elements = []
            styles = getSampleStyleSheet()
            
            title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontSize=16, textColor=colors.HexColor('#1f4e78'), alignment=1, spaceAfter=8)
            subtitle_style = ParagraphStyle('SubTitleStyle', parent=styles['Heading2'], fontSize=11, textColor=colors.HexColor('#333333'), spaceAfter=10)

            elements.append(Paragraph("<b>REPORTE OFICIAL - TORNEO DE BILLAR</b>", title_style))
            elements.append(Paragraph("<b>Modalidad: Doble Eliminación (Con Repechaje y Muerte Súbita desde Octavos)</b>", subtitle_style))
            elements.append(Spacer(1, 10))

            jugadores = st.session_state.jugadores_dd
            data_pdf = [["Posición", "Participante / Equipo"]]
            for idx, j in enumerate(jugadores, 1):
                p_str = "1° (Campeón)" if idx==1 else ("2° (Subcampeón)" if idx==2 else f"{idx}° Puesto")
                data_pdf.append([p_str, j])

            t_dd = Table(data_pdf, colWidths=[150, 510])
            t_dd.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f4e78')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 9),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#dddddd')),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f2f5f8')]),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('TOPPADDING', (0, 1), (-1, -1), 5),
                ('BOTTOMPADDING', (0, 1), (-1, -1), 5),
            ]))
            elements.append(t_dd)
            doc.build(elements)
            buffer.seek(0)
            return buffer

        pdf_buf = generar_pdf_dd()
        st.download_button(
            label="📥 Descargar Reporte Doble Eliminación en PDF",
            data=pdf_buf,
            file_name="Reporte_Doble_Eliminacion.pdf",
            mime="application/pdf"
        )

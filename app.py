import streamlit as st
import pandas as pd

st.set_page_config(page_title="Gestión de Torneos de Billar", layout="wide")

st.title("🎱 Sistema de Torneos de Billar")

# Menú principal con las 3 modalidades solicitadas
menu = st.sidebar.selectbox("Seleccione la Modalidad de Torneo", [
    "Todos contra Todos",
    "Torneos Eliminación Directa", 
    "Torneos Doble Eliminación"
])

# ==========================================
# 1. TODOS CONTRA TODOS (100% Intacto como lo pediste)
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
        st.session_state.jugadores_ed = []

    st.markdown("### 📝 Registro de Participantes - Eliminación Directa")
    nuevo_j_ed = st.text_input("Nombre del Jugador (Eliminación Directa):", key="input_ed")
    if st.button("Agregar a Eliminación Directa"):
        if nuevo_j_ed and nuevo_j_ed not in st.session_state.jugadores_ed:
            st.session_state.jugadores_ed.append(nuevo_j_ed)
            st.success(f"Agregado: {nuevo_j_ed}")
            st.rerun()
        elif not nuevo_j_ed:
            st.warning("Ingresa un nombre válido.")
        else:
            st.info("El jugador ya está en la lista.")

    st.markdown("#### Participantes inscritos:")
    if st.session_state.jugadores_ed:
        for idx, j in enumerate(st.session_state.jugadores_ed, 1):
            col1, col2 = st.columns([4, 1])
            with col1:
                st.write(f"{idx}. {j}")
            with col2:
                if st.button("Eliminar", key=f"del_ed_{idx}"):
                    st.session_state.jugadores_ed.remove(j)
                    st.rerun()
    else:
        st.info("No hay participantes registrados en esta modalidad.")

    st.markdown("---")
    st.markdown("### ⚡ Llaves del Torneo")
    if len(st.session_state.jugadores_ed) >= 2:
        st.info("Próximamente: Generador de llaves de eliminación directa por rondas (Cuartos, Semifinales, Final).")
    else:
        st.warning("Agrega al menos 2 jugadores para configurar las llaves.")


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

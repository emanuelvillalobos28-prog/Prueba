import streamlit as st

st.set_page_config(page_title="Gestión de Torneos de Billar", layout="centered")

st.title("🎱 Sistema de Torneos de Billar")
st.subheader("Modalidad: Todos contra todos (Round-Robin)")

# Inicializar la lista de jugadores y estadísticas en el estado de la sesión si no existen
if "jugadores" not in st.session_state:
    st.session_state.jugadores = [
        "Emanuel Villalobos", "Alejandro Breganza", "Bryan Molina",
        "Daniel Duarte", "Saúl Ventura", "Jorge Castañeda",
        "Rogelio Ramos", "Mynor García", "Juan Carlos Pollo",
        "Pablo Díaz", "Carlos López", "Mario Ordóñez"
    ]

if "resultados" not in st.session_state:
    st.session_state.resultados = {}  # Formato clave: (jugador1, jugador2) -> (puntos1, puntos2)

# Menú principal actualizado con las nuevas opciones
menu = st.sidebar.selectbox("Menú Principal", [
    "Registro y Gestión de Jugadores", 
    "Generar Partidas y Semanas", 
    "Tabla de Posiciones"
])

if menu == "Registro y Gestión de Jugadores":
    st.markdown("### 📝 Gestión de Participantes")
    
    # Agregar nuevo jugador
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
                # Opción para modificar nombre directamente
                nuevo_nombre = st.text_input(f"Editar {idx+1}", value=jugador, key=f"edit_{idx}", label_visibility="collapsed")
            with col2:
                if st.button("Actualizar", key=f"btn_update_{idx}"):
                    if nuevo_nombre and nuevo_nombre not in st.session_state.jugadores:
                        st.session_state.jugadores[idx] = nuevo_nombre
                        st.success("¡Actualizado!")
                        st.rerun()
                    else:
                        st.warning("Nombre inválido o ya existente.")
            with col3:
                if st.button("🗑️ Eliminar", key=f"btn_del_{idx}"):
                    st.session_state.jugadores.remove(jugador)
                    st.success(f"Eliminado: {jugador}")
                    st.rerun()
    else:
        st.info("Aún no hay jugadores registrados.")

elif menu == "Generar Partidas y Semanas":
    st.markdown("### 📅 Rol de Enfrentamientos por Semana")
    
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
                        st.write(f"**Partida {idx}:** {j1} 🆚 {j2}")
                else:
                    st.write("Sin enfrentamientos directos esta semana.")

elif menu == "Tabla de Posiciones":
    st.markdown("### 🏆 Tabla de Posiciones y Resultados")
    
    jugadores = st.session_state.jugadores
    if not jugadores:
        st.warning("No hay jugadores registrados para mostrar la tabla de posiciones.")
    else:
        # Estructura para acumular estadísticas
        tabla = {j: {"PJ": 0, "G": 0, "P": 0, "Pts": 0} for j in jugadores}
        
        # Calcular estadísticas basándose en los enfrentamientos del Round-Robin
        n = len(jugadores)
        if n >= 2:
            lista_juegos = list(jugadores)
            if n % 2 != 0:
                lista_juegos.append("Descansa (BYE)")
                n += 1
            
            total_semanas = n - 1
            partidos_por_semana = n // 2
            copia_jugadores = list(lista_juegos)
            
            for semana in range(total_semanas):
                for i in range(partidos_por_semana):
                    j1 = copia_jugadores[i]
                    j2 = copia_jugadores[n - 1 - i]
                    if j1 != "Descansa (BYE)" and j2 != "Descansa (BYE)":
                        # Verificar si hay un resultado registrado para este par
                        par_key = tuple(sorted([j1, j2]))
                        if par_key in st.session_state.resultados:
                            res = st.session_state.resultados[par_key]
                            # Asumimos que res guarda (ganador, perdedor) o puntajes
                            ganador = res.get("ganador")
                            if ganador:
                                tabla[ganador]["G"] += 1
                                perdedor = j2 if ganador == j1 else j1
                                tabla[perdedor]["P"] += 1
                                tabla[j1]["PJ"] += 1
                                tabla[j2]["PJ"] += 1
                copia_jugadores = [copia_jugadores[0]] + [copia_jugadores[-1]] + copia_jugadores[1:-1]

        # Calcular puntos (Ej: 3 puntos por partida ganada)
        for j in tabla:
            tabla[j]["Pts"] = tabla[j]["G"] * 3

        # Ordenar por Puntos de mayor a menor
        tabla_ordenada = sorted(tabla.items(), key=lambda x: (x[1]["Pts"], x[1]["G"]), reverse=True)

        st.markdown("#### Posiciones Actuales")
        for pos, (jugador, stats) in enumerate(tabla_ordenada, 1):
            st.write(f"**{pos}. {jugador}** — Pts: **{stats['Pts']}** | PJ: {stats['PJ']} | G: {stats['G']} | P: {stats['P']}")

        st.markdown("---")
        st.markdown("#### 📝 Registrar Resultado de Partida")
        match_j1 = st.selectbox("Jugador 1", jugadores, key="res_j1")
        match_j2 = st.selectbox("Jugador 2", [j for j in jugadores if j != match_j1], key="res_j2")
        ganador_partida = st.selectbox("¿Quién ganó la partida?", [match_j1, match_j2])

        if st.button("Guardar Resultado"):
            par_key = tuple(sorted([match_j1, match_j2]))
            st.session_state.resultados[par_key] = {"ganador": ganador_partida}
            st.success(f"¡Resultado guardado! Ganador: {ganador_partida}")
            st.rerun()

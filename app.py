import streamlit as st

st.set_page_config(page_title="Gestión de Torneos de Billar", layout="centered")

st.title("🎱 Sistema de Torneos de Billar")
st.subheader("Modalidad: Todos contra todos (Round-Robin)")

# Inicializar la lista de jugadores en el estado de la sesión si no existe
if "jugadores" not in st.session_state:
    st.session_state.jugadores = [
        "Emanuel Villalobos", "Alejandro Breganza", "Bryan Molina",
        "Daniel Duarte", "Saúl Ventura", "Jorge Castañeda",
        "Rogelio Ramos", "Mynor García", "Juan Carlos Pollo",
        "Pablo Díaz", "Carlos López", "Mario Ordóñez"
    ]

# Menú lateral para navegación
menu = st.sidebar.selectbox("Menú Principal", ["Registro de Jugadores", "Generar Partidas y Semanas"])

if menu == "Registro de Jugadores":
    st.markdown("### Agrega a los participantes del torneo")
    
    nuevo_jugador = st.text_input("Nombre del Jugador o Club:")
    if st.button("Agregar Jugador"):
        if nuevo_jugador and nuevo_jugador not in st.session_state.jugadores:
            st.session_state.jugadores.append(nuevo_jugador)
            st.success(f"¡Jugador {nuevo_jugador} agregado con éxito!")
        elif not nuevo_jugador:
            st.warning("Escribe un nombre válido.")
        else:
            st.info("Ese jugador ya está en la lista.")

    st.markdown("### Lista actual de participantes:")
    if st.session_state.jugadores:
        for i, jugador in enumerate(st.session_state.jugadores, 1):
            st.write(f"{i}. {jugador}")
    else:
        st.info("Aún no hay jugadores registrados.")

elif menu == "Generar Partidas y Semanas":
    st.markdown("### 📅 Rol de Enfrentamientos por Semana")
    
    jugadores = st.session_state.jugadores
    n = len(jugadores)
    
    if n < 2:
        st.warning("Necesitas al menos 2 jugadores registrados para generar el rol de partidas.")
    else:
        # Si el número de jugadores es impar, agregamos un "BYE" (descansa)
        lista_juegos = list(jugadores)
        tiene_bye = False
        if n % 2 != 0:
            lista_juegos.append("Descansa (BYE)")
            n += 1
            tiene_bye = True
            
        total_semanas = n - 1
        partidos_por_semana = n // 2
        
        st.info(f"Se han organizado **{total_semanas} semanas** de competencia para un total de {len(jugadores)} jugadores.")
        
        # Generador Round-Robin
        cronograma = []
        copia_jugadores = list(lista_juegos)
        
        for semana in range(total_semanas):
            enfrentamientos_semana = []
            for i in range(partidos_por_semana):
                j1 = copia_jugadores[i]
                j2 = copia_jugadores[n - 1 - i]
                # Si no involucra al "BYE" fantasma, se añade al calendario
                if j1 != "Descansa (BYE)" and j2 != "Descansa (BYE)":
                    enfrentamientos_semana.append((j1, j2))
            
            cronograma.append(enfrentamientos_semana)
            
            # Rotar los jugadores manteniendo fijo el primero
            copia_jugadores = [copia_jugadores[0]] + [copia_jugadores[-1]] + copia_jugadores[1:-1]
            
        # Mostrar el rol organizado por semana de forma consecutiva
        for num_semana, enfrentamientos in enumerate(cronograma, 1):
            with st.expander(f"🟢 Semana {num_semana} ({len(enfrentamientos)} partidas)", expanded=(num_semana == 1)):
                if enfrentamientos:
                    for idx, (j1, j2) in enumerate(enfrentamientos, 1):
                        col1, col2 = st.columns([4, 1])
                        with col1:
                            st.write(f"**Partida {idx}:** {j1} 🆚 {j2}")
                        with col2:
                            # Campo simulado para asignar mesa de juego
                            st.text(f"Mesa {(idx % 4) + 1}")
                else:
                    st.write("Esta semana no hay enfrentamientos directos registrados.")

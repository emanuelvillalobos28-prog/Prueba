import streamlit as st

st.set_page_config(page_title="Gestión de Torneos de Billar", layout="centered")

st.title("🎱 Sistema de Torneos de Billar")
st.subheader("Modalidad: Todos contra todos (Round-Robin)")

# Menú lateral para navegación sencilla
menu = st.sidebar.selectbox("Menú Principal", ["Registro de Jugadores", "Generar Partidas", "Tabla de Posiciones"])

if menu == "Registro de Jugadores":
    st.markdown("### Agrega a los participantes del torneo")
    if "jugadores" not in st.session_state:
        st.session_state.jugadores = []

    nuevo_jugador = st.text_input("Nombre del Jugador o Club:")
    if st.button("Agregar Jugador"):
        if nuevo_jugador and nuevo_jugador not in st.session_state.jugadores:
            st.session_state.jugadores.append(nuevo_jugador)
            st.success(f"¡Jugador {nuevo_jugador} agregado con éxito!")
        elif not nuevo_jugador:
            st.warning("Escribe un nombre válido.")
        else:
            st.info("Ese jugador ya está en la lista.")

    st.write("#### Lista actual de participantes:")
    if st.session_state.jugadores:
        for i, j in enumerate(st.session_state.jugadores, 1):
            st.write(f"{i}. {j}")
    else:
        st.info("Aún no hay jugadores registrados.")

elif menu == "Generar Partidas":
    st.markdown("### Rol de enfrentamientos")
    if "jugadores" in st.session_state and len(st.session_state.jugadores) >= 2:
        jugadores = st.session_state.jugadores
        st.write("Se generarán los cruces de todos contra todos:")
        
        # Generador simple de enfrentamientos
        partidas = []
        for i in range(len(jugadores)):
            for j in range(i + 1, len(jugadores)):
                partidas.append((jugadores[i], jugadores[j]))
        
        for idx, (p1, p2) in enumerate(partidas, 1):
            st.write(f"Partida {idx}: **{p1}** vs **{p2}**")
    else:
        st.warning("Necesitas registrar al menos 2 jugadores en la sección anterior.")

elif menu == "Tabla de Posiciones":
    st.markdown("### Clasificación General")
    st.info("La tabla se actualizará conforme se registren los resultados de las partidas.")

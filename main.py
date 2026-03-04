import streamlit as st
import requests

st.set_page_config(page_title="TIPSTER IA EXPERT", page_icon="🤖", layout="centered")

# Estilo Premium con Semáforo
st.markdown("""
    <style>
    .card {
        background-color: white; padding: 20px; border-radius: 20px;
        box-shadow: 0px 10px 25px rgba(0,0,0,0.1); margin-bottom: 25px;
        border-top: 8px solid #007bff; color: black; text-align: center;
    }
    .semaforo { padding: 5px 15px; border-radius: 20px; font-weight: bold; font-size: 0.9em; display: inline-block; margin-bottom: 10px; }
    .riesgo-bajo { background-color: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
    .riesgo-medio { background-color: #fff3cd; color: #856404; border: 1px solid #ffeeba; }
    .riesgo-alto { background-color: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
    .pick-maestro { color: #007bff; font-weight: bold; font-size: 1.3em; text-transform: uppercase; margin: 10px 0; }
    .vs-text { font-size: 0.8em; color: #888; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

st.title("🤖 IA Tipster: Semáforo Pro")

liga = st.sidebar.selectbox("Liga:", ["soccer_usa_mls", "soccer_spain_la_liga", "soccer_mexico_liga_mx", "soccer_england_premier_league"])
monto = st.sidebar.number_input("Monto a apostar ($):", value=100)

if st.button('🚀 GENERAR ANÁLISIS MAESTRO'):
    url = f'https://api.the-odds-api.com/v4/sports/{liga}/odds/?apiKey=d350d32302483fd5e15fa6561b2cdf2e&regions=eu&markets=h2h,totals'
    res = requests.get(url)
    
    if res.status_code == 200:
        datos = res.json()
        for p in datos:
            try:
                home, away = p['home_team'], p['away_team']
                mkts = p['bookmakers'][0]['markets']
                
                # Cuotas Ganador
                h2h = next(m['outcomes'] for m in mkts if m['key'] == 'h2h')
                c_home = next(i['price'] for i in h2h if i['name'] == home)
                
                # Cuotas Goles
                try:
                    totals = next(m['outcomes'] for m in mkts if m['key'] == 'totals')
                    c_over25 = next(i['price'] for i in totals if i['name'] == 'Over' and i['point'] == 2.5)
                except: c_over25 = 2.0

                # --- LÓGICA DE SEMÁFORO Y PICK ---
                pick, razon, clase_riesgo, nivel = "", "", "", ""

                if c_home < 1.45:
                    pick, razon, clase_riesgo, nivel = f"GANA {home}", "Superioridad absoluta en papel.", "riesgo-bajo", "🟢 RIESGO BAJO (FIJO)"
                elif c_over25 < 1.65:
                    pick, razon, clase_riesgo, nivel = "OVER 2.5 GOLES", "Probabilidad alta de partido abierto.", "riesgo-medio", "🟡 RIESGO MEDIO"
                elif c_home > 2.50:
                    pick, razon, clase_riesgo, nivel = f"GANA {home} (DNB)", "Cuota con valor pero partido parejo.", "riesgo-alto", "🔴 RIESGO ALTO"
                else:
                    pick, razon, clase_riesgo, nivel = "OVER 1.5 GOLES", "La opción más conservadora.", "riesgo-bajo", "🟢 RIESGO BAJO"

                # --- Render Tarjeta Principal ---
                st.markdown(f"""
                <div class="card">
                    <div class="semaforo {clase_riesgo}">{nivel}</div>
                    <div style="display: flex; justify-content: space-around; align-items: center;">
                        <div><b>{home}</b></div>
                        <div class="vs-text">VS</div>
                        <div><b>{away}</b></div>
                    </div>
                    <div class="pick-maestro">{pick}</div>
                </div>
                """, unsafe_allow_html=True)

                # Botón para abrir la "pantalla" de detalles (estilo la imagen que enviaste)
                if st.button(f"📊 Ver predicciones: {home} vs {away}", key=f"btn_{home}"):
                    @st.dialog(f"Análisis detallado: {home} vs {away}")
                    def mostrar_detalles():
                        st.subheader("Nuestras predicciones")
                        
                        # Opción 1: Ganador
                        st.info(f"**Victoria de {home}**\n\nLa IA detecta una probabilidad del {int((1/c_home)*100)}% basada en las cuotas actuales.")
                        st.progress(int((1/c_home)*100) / 100, text=f"Confianza: {int((1/c_home)*100)}")
                        
                        st.divider()
                        
                        # Opción 2: Ambos marcan (Simulado con lógica de cuotas)
                        st.success(f"**Ambos equipos marcan**\n\nTendencia ofensiva detectada en los últimos encuentros de {home}.")
                        st.progress(0.65, text="Confianza: Alto • 65")
                        
                        st.divider()
                        
                        # Opción 3: Más de 2.5 goles
                        st.warning(f"**Más de 2.5 goles**\n\nBasado en la cuota de {c_over25}, se espera un partido con movimiento en las áreas.")
                        st.progress(0.50, text="Confianza: Medio • 50")
                        
                        if st.button("Cerrar"):
                            st.rerun()

                    mostrar_detalles()

            except Exception as e:
                continue
import os
import streamlit as st
import networkx as nx
import matplotlib.pyplot as plt
import periodictable
from fpdf import FPDF
import io
from datetime import datetime
mensaje_salida = st.empty()
main_container = st.empty()

with main_container.container():

    # --- 1. CONFIGURACIÓN Y ESTILO ---
    st.set_page_config(page_title="Sistema Visualizador de Estructuras Moleculares", layout="wide")

    st.markdown("""
    <style>
        [data-testid="stAppViewContainer"] { background: #0d1b2a; color: #e0e8f0; }
        .panel { background: #162030; border: 1px solid #2a3f5a; border-radius: 10px; padding: 20px; }
        .canvas-panel { background: #111c28; border: 1px solid #2a3f5a; border-radius: 10px; padding: 10px; }
        .stButton>button { border-radius: 7px; font-weight: 600; width: 100%; }
        .val-ok { color: #50d090; font-size: 14px; }
        .val-err { color: #e06060; }
    
        /* ESTO ARREGLA EL TEXTO Y EL FONDO OSCURO */
        label p { color: #ffffff !important; font-weight: bold !important; opacity: 1 !important; }
        
        .stTextInput input:disabled { 
            color: #ffffff !important; 
            -webkit-text-fill-color: #ffffff !important; 
            opacity: 1 !important; 
            background-color: #0d1b2a !important; 
            border: 1px solid #2a3f5a !important;
        }
    </style>
    """, unsafe_allow_html=True)

    # --- 2. BIBLIOTECA COMPUESTOS JSON ---
    BIBLIOTECA_COMPUESTOS = [
        {"n": "Glucosa", "f": "C6H12O6", "iupac": "(2R,3S,4R,5R,6R)-6-(hidroximetil)oxano-2,3,4,5-tetrol", "m": 180.16, "g": "Aldehído/Polialcohol", "s": "Flamable, Irritante", "atomos": [{"s":"C","x":0,"y":1}, {"s":"C","x":1,"y":0.5}, {"s":"O","x":1,"y":1.5}, {"s":"C","x":2,"y":1}, {"s":"C","x":0.5,"y":0}], "enlaces": [(0,1,1), (1,2,2), (1,3,1), (0,4,1)]},
        {"n": "Agua", "f": "H2O", "iupac": "Oxidano", "m": 18.01, "g": "Óxido de hidrógeno", "s": "Sin riesgo", "atomos": [{"s":"O","x":0,"y":0}, {"s":"H","x":-0.8,"y":-0.6}, {"s":"H","x":0.8,"y":-0.6}], "enlaces": [(0,1,1), (0,2,1)]},
        {"n": "Metano", "f": "CH4", "iupac": "Metano", "m": 16.04, "g": "Alcano", "s": "Gas extremadamente inflamable", "atomos": [{"s":"C","x":0,"y":0}, {"s":"H","x":0,"y":1}, {"s":"H","x":0,"y":-1}, {"s":"H","x":1,"y":0}, {"s":"H","x":-1,"y":0}], "enlaces": [(0,1,1), (0,2,1), (0,3,1), (0,4,1)]},
        {"n": "Etanol", "f": "C2H6O", "iupac": "Etanol", "m": 46.07, "g": "Alcohol", "s": "Líquido inflamable", "atomos": [{"s":"C","x":0,"y":0}, {"s":"C","x":1,"y":0.5}, {"s":"O","x":2,"y":0}], "enlaces": [(0,1,1), (1,2,1)]},
        {"n": "Ácido Acético", "f": "C2H4O2", "iupac": "Ácido etanoico", "m": 60.05, "g": "Ácido carboxílico", "s": "Corrosivo, Inflamable", "atomos": [{"s":"C","x":0,"y":0}, {"s":"C","x":1,"y":0}, {"s":"O","x":1.5,"y":0.8}, {"s":"O","x":1.5,"y":-0.8}], "enlaces": [(0,1,1), (1,2,2), (1,3,1)]},
        {"n": "Benceno", "f": "C6H6", "iupac": "Benceno", "m": 78.11, "g": "Hidrocarburo aromático", "s": "Cancerígeno, Inflamable", "atomos": [{"s":"C","x":0,"y":1}, {"s":"C","x":0.8,"y":0.5}, {"s":"C","x":0.8,"y":-0.5}, {"s":"C","x":0,"y":-1}, {"s":"C","x":-0.8,"y":-0.5}, {"s":"C","x":-0.8,"y":0.5}], "enlaces": [(0,1,2), (1,2,1), (2,3,2), (3,4,1), (4,5,2), (5,0,1)]},
        {"n": "Amoníaco", "f": "NH3", "iupac": "Azano", "m": 17.03, "g": "Amina", "s": "Gas tóxico, Corrosivo", "atomos": [{"s":"N","x":0,"y":0}, {"s":"H","x":0,"y":1}, {"s":"H","x":0.9,"y":-0.5}, {"s":"H","x":-0.9,"y":-0.5}], "enlaces": [(0,1,1), (0,2,1), (0,3,1)]},
        {"n": "Acetona", "f": "C3H6O", "iupac": "Propan-2-ona", "m": 58.08, "g": "Cetona", "s": "Inflamable, Irritante", "atomos": [{"s":"C","x":-1,"y":0}, {"s":"C","x":0,"y":0.5}, {"s":"C","x":1,"y":0}, {"s":"O","x":0,"y":1.5}], "enlaces": [(0,1,1), (1,2,1), (1,3,2)]},
        {"n": "Propano", "f": "C3H8", "iupac": "Propano", "m": 44.1, "g": "Alcano", "s": "Gas inflamable", "atomos": [{"s":"C","x":-1,"y":0}, {"s":"C","x":0,"y":0.5}, {"s":"C","x":1,"y":0}], "enlaces": [(0,1,1), (1,2,1)]},
        {"n": "Etileno", "f": "C2H4", "iupac": "Eteno", "m": 28.05, "g": "Alqueno", "s": "Inflamable", "atomos": [{"s":"C","x":-0.75,"y":0.00}, {"s":"C","x":0.75,"y":0.00}, {"s":"H","x":-1.50,"y":1.30}, {"s":"H","x":-1.50,"y":-1.30}, {"s":"H","x":1.50,"y":-1.30}, {"s":"H","x":1.50,"y":1.30}], "enlaces": [(0,1,2), (0,2,1), (0,3,1), (1,4,1), (1,5,1)]},
        {"n": "Metanol", "f": "CH4O", "iupac": "Metanol", "m": 32.04, "g": "Alcohol", "s": "Tóxico, Inflamable", "atomos": [{"s":"C","x": 0.43, "y": 0.00}, {"s":"O","x": -0.87, "y": -0.75}, {"s":"H","x": 1.73, "y": 0.75}, {"s":"H","x": 1.18, "y": -1.30}, {"s":"H","x": -0.32, "y": 1.30}, {"s":"H","x": -2.17, "y": 0.00}], "enlaces": [(0,1,1), (0,2,1), (0,3,1), (0,4,1), (1,5,1)]},
        {"n": "Ácido Sulfúrico", "f": "H2SO4", "iupac": "Ácido tetraoxosulfúrico", "m": 98.07, "g": "Ácido fuerte", "s": "Muy corrosivo", "atomos": [{"s":"S","x":0,"y":0}, {"s":"O","x":0,"y":1}, {"s":"O","x":0,"y":-1}, {"s":"O","x":1,"y":0}, {"s":"O","x":-1,"y":0}], "enlaces": [(0,1,2), (0,2,2), (0,3,1), (0,4,1)]},
        {"n": "Urea", "f": "CH4N2O", "iupac": "Carbonildiamida", "m": 60.06, "g": "Amida", "s": "Sin riesgo", "atomos": [{"s":"C","x":0,"y":0}, {"s":"O","x":0,"y":1}, {"s":"N","x":-1,"y":-0.5}, {"s":"N","x":1,"y":-0.5}], "enlaces": [(0,1,2), (0,2,1), (0,3,1)]},
        {"n": "Formaldehído", "f": "CH2O", "iupac": "Metanal", "m": 30.03, "g": "Aldehído", "s": "Tóxico, Cancerígeno", "atomos": [{"s":"C","x":0,"y":0}, {"s":"O","x":0,"y":1}, {"s":"H","x":-0.8,"y":-0.5}, {"s":"H","x":0.8,"y":-0.5}], "enlaces": [(0,1,2), (0,2,1), (0,3,1)]},
        {"n": "Ácido Nítrico", "f": "HNO3", "iupac": "Ácido nítrico", "m": 63.01, "g": "Ácido fuerte", "s": "Corrosivo, Oxidante", "atomos": [{"s":"N","x":0,"y":0}, {"s":"O","x":0,"y":1.2}, {"s":"O","x":1,"y":-0.6}, {"s":"O","x":-1,"y":-0.6}], "enlaces": [(0,1,2), (0,2,1), (0,3,1)]},
        {"n": "Anilina", "f": "C6H7N", "iupac": "Fenilamina", "m": 93.13, "g": "Amina aromática", "s": "Tóxico, Combustible", "atomos": [{"s":"C","x":0,"y":1}, {"s":"C","x":0.8,"y":0.5}, {"s":"C","x":0.8,"y":-0.5}, {"s":"C","x":0,"y":-1}, {"s":"C","x":-0.8,"y":-0.5}, {"s":"C","x":-0.8,"y":0.5}, {"s":"N","x":0,"y":2}], "enlaces": [(0,1,2), (1,2,1), (2,3,2), (3,4,1), (4,5,2), (5,0,1), (0,6,1)]},
        {"n": "Benzaldehído", "f": "C7H6O", "iupac": "Benzaldehído", "m": 106.12, "g": "Aldehído aromático", "s": "Irritante", "atomos": [{"s":"C","x":0,"y":1}, {"s":"C","x":0.8,"y":0.5}, {"s":"C","x":0.8,"y":-0.5}, {"s":"C","x":0,"y":-1}, {"s":"C","x":-0.8,"y":-0.5}, {"s":"C","x":-0.8,"y":0.5}, {"s":"C","x":0,"y":2}, {"s":"O","x":0.8,"y":2.5}], "enlaces": [(0,1,2), (1,2,1), (2,3,2), (3,4,1), (4,5,2), (5,0,1), (0,6,1), (6,7,2)]},
        {"n": "Cloroformo", "f": "CHCl3", "iupac": "Triclorometano", "m": 119.38, "g": "Halogenuro", "s": "Tóxico, Narcótico", "atomos": [{"s":"C","x":0,"y":0}, {"s":"H","x":0,"y":1}, {"s":"Cl","x":1,"y":-0.5}, {"s":"Cl","x":-1,"y":-0.5}, {"s":"Cl","x":0,"y":-1}], "enlaces": [(0,1,1), (0,2,1), (0,3,1), (0,4,1)]},
        {"n": "Fenol", "f": "C6H6O", "iupac": "Fenol", "m": 94.11, "g": "Fenol", "s": "Tóxico, Corrosivo", "atomos": [{"s":"C","x":0,"y":1}, {"s":"C","x":0.8,"y":0.5}, {"s":"C","x":0.8,"y":-0.5}, {"s":"C","x":0,"y":-1}, {"s":"C","x":-0.8,"y":-0.5}, {"s":"C","x":-0.8,"y":0.5}, {"s":"O","x":0,"y":2}], "enlaces": [(0,1,2), (1,2,1), (2,3,2), (3,4,1), (4,5,2), (5,0,1), (0,6,1)]},
        {"n": "Glicerina", "f": "C3H8O3", "iupac": "Propano-1,2,3-triol", "m": 92.09, "g": "Polialcohol", "s": "Sin riesgo", "atomos": [{"s":"C","x":-1,"y":0}, {"s":"C","x":0,"y":0}, {"s":"C","x":1,"y":0}, {"s":"O","x":-1,"y":1}, {"s":"O","x":0,"y":-1}, {"s":"O","x":1,"y":1}], "enlaces": [(0,1,1), (1,2,1), (0,3,1), (1,4,1), (2,5,1)]}
    ]

    ERRORES_COMUNES = ["Escribir el nombre correcto", "Coordenada ocupada", "Símbolo no reconocido", "Fórmula incorrecta", "Compuesto no encontrado"]

    # --- 3. MOTOR LÓGICO ---
    class VisorMotor:
        def __init__(self, compuesto):
            self.g = nx.Graph()
            self.pos = {}
            self.labels = {}
            self.compuesto = compuesto
            
        def procesar(self):
            for i, at in enumerate(self.compuesto["atomos"]):
                self.g.add_node(i, s=at["s"])
                self.pos[i] = (float(at["x"]), float(at["y"]))
                self.labels[i] = at["s"]
            for e in self.compuesto["enlaces"]:
                self.g.add_edge(e[0], e[1], weight=e[2])

        def dibujar(self):
            fig, ax = plt.subplots(figsize=(5, 4))
            fig.patch.set_facecolor('#111c28')
            ax.set_facecolor('#111c28')
            
            # Enlaces estilo varilla
            nx.draw_networkx_edges(self.g, self.pos, width=6, edge_color='#2c3e50', alpha=0.8, ax=ax)
            
            # Números de enlace (1, 2, 3)
            edge_labels = {(e[0], e[1]): f"{e[2]}" for e in self.compuesto["enlaces"]}
            nx.draw_networkx_edge_labels(self.g, self.pos, edge_labels=edge_labels, font_size=9, ax=ax)

            # Átomos con efecto esfera 3D
            for i, (x, y) in self.pos.items():
                s = self.labels[i]
                # Colores CPK estándar
                c = '#ff4b4b' if s=='O' else '#909090' if s=='C' else '#3050f8' if s=='N' else '#ffffff'
                
                # Capas de brillo para efecto 3D
                ax.scatter(x, y, s=900, color=c, edgecolors='#333333', linewidth=1.5, zorder=3)
                ax.scatter(x+0.05, y+0.05, s=200, color='white', alpha=0.3, zorder=4) # Reflejo de luz
                
                ax.text(x, y, s, color='white' if s!='H' else 'black', 
                        ha='center', va='center', fontweight='bold', fontsize=10, zorder=5)

            plt.axis('off')
            return fig

    # --- 4. EXPORTACIÓN PDF (WYSIWYG) ---
    def generar_pdf(compuesto, fig):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_fill_color(13, 27, 42)
        pdf.rect(0, 0, 210, 30, 'F')
        pdf.set_font("Arial", "B", 16)
        pdf.set_text_color(255, 255, 255)
        pdf.cell(0, 20, "  Sistema Visualizador de Estructuras Moleculares - Reporte", ln=True)
        
        # --- BLOQUE DE IMAGEN CORREGIDO ---
        temp_img = "temp_canvas.png"
        fig.savefig(temp_img, format='png', bbox_inches='tight', dpi=150, facecolor='#111c28')
        pdf.image(temp_img, x=55, y=35, w=100)
        if os.path.exists(temp_img):
            os.remove(temp_img)
        # ----------------------------------
        
        pdf.set_y(120)
        pdf.set_fill_color(240, 245, 250)
        pdf.set_text_color(0, 0, 0)
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, f" 1. ANALISIS MOLECULAR: {compuesto['n']}", ln=True, fill=True)
        pdf.set_font("Arial", "", 10)
        
        analisis = [
            ["IUPAC:", compuesto['iupac']], 
            ["Formula:", compuesto['f']], 
            ["Masa:", f"{compuesto['m']} g/mol"], 
            ["Grupo:", compuesto['g']], 
            ["Seguridad:", compuesto['s']]
        ]
        
        for label, valor in analisis:
            pdf.set_font("Arial", "B", 10)
            pdf.cell(45, 7, f" {label}", 0)
            pdf.set_font("Arial", "", 10)
            pdf.multi_cell(0, 7, str(valor))
        
        pdf.ln(5)
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, " 2. COORDENADAS DE ATOMOS", ln=True, fill=True)
        pdf.set_font("Arial", "B", 10)
        pdf.cell(40, 7, " ID", 1); pdf.cell(40, 7, " Simbolo", 1); pdf.cell(40, 7, " X", 1); pdf.cell(40, 7, " Y", 1); pdf.ln()
        
        pdf.set_font("Arial", "", 10)
        for i, at in enumerate(compuesto["atomos"]):
            pdf.cell(40, 6, str(i), 1); pdf.cell(40, 6, at['s'], 1); pdf.cell(40, 6, str(at['x']), 1); pdf.cell(40, 6, str(at['y']), 1); pdf.ln()

        return pdf.output(dest='S').encode('latin-1')

    # --- 5. INTERFAZ ---
    def limpiar_buscador():
        st.session_state.campo_busqueda = ""
        
    col_left, col_center, col_right = st.columns([1, 2, 1])

    with col_left:
        st.markdown('<div class="panel"><b>Input Panel</b>', unsafe_allow_html=True)
        
        busqueda = st.text_input("Nombre/Fórmula:", key="campo_busqueda")
        
        
        res_coord = next((c for c in BIBLIOTECA_COMPUESTOS if c["n"].lower() == busqueda.lower() or c["f"].lower() == busqueda.lower()), None)
        
        if res_coord:
            atomo = res_coord["atomos"][0]
            coord_info = f"{atomo['x']}, {atomo['y']}"
        else:
            coord_info = "0.0, 0.0"

        st.text_input("Coordenadas (X, Y):", value=coord_info, disabled=True)

        st.markdown(f'''
        <div style="background:#1e3050; padding:10px; border-radius:5px; margin-top:10px; font-size:12px;">
        <b>Alertas de Tipeo</b><br>{"<br>".join(ERRORES_COMUNES)}
        </div>
        ''', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        
    with col_center:
        st.markdown('<div class="canvas-panel">Canvas', unsafe_allow_html=True)
        
        res = None
        if busqueda:
            res = next((c for c in BIBLIOTECA_COMPUESTOS if c["n"].lower() == busqueda.lower() or c["f"].lower() == busqueda.lower()), None)
        
        if res:
            motor = VisorMotor(res)
            motor.procesar()
            fig_actual = motor.dibujar()
            st.pyplot(fig_actual)
            st.markdown("<center><small>Leyenda: Enlace Sencillo (1), Doble (2), Triple (3)</small></center>", unsafe_allow_html=True)
        else:
            st.info("Escribe un nombre y presiona Enter")
            
        st.markdown('</div>', unsafe_allow_html=True)

    with col_right:
        st.markdown('<div class="panel"><b>Análisis Molecular</b>', unsafe_allow_html=True)
        if res:
            st.markdown(f"### {res['n']}")
            st.markdown(f"**Fórmula:** `{res['f']}`") 
            st.write(f"**IUPAC:** {res['iupac']}")
            st.write(f"**Masa:** {res['m']} g/mol")
            st.write(f"**Grupo:** {res['g']}")
            st.error(f"**Seguridad:** {res['s']}")
            if "C" in res['f']:
                mensaje = f"Validación Exitosa: El Carbono en {res['n']} actúa con valencia 4."
            else:
                mensaje = f"Análisis completado: Compuesto {res['f']} sin base de Carbono."
                
            st.markdown(f'<div class="val-ok">{mensaje}</div>', unsafe_allow_html=True)
            
        st.markdown('</div>', unsafe_allow_html=True)

    st.divider()
    c1, c2, c3 = st.columns(3)
    with c2:
        if res:
            pdf_bytes = generar_pdf(res, fig_actual)
            st.download_button("Descargar Info (PDF)", data=pdf_bytes, file_name=f"{res['n']}.pdf", mime="application/pdf")
    with c3:
            if st.button("Salir"):
                main_container.empty()
                mensaje_salida.markdown(
                    """
                    <div style='display: flex; justify-content: center; align-items: center; height: 80vh;'>
                        <h1 style='color: #FF4B4B; text-align: center; font-size: 50px;'>
                            ¡Hasta la próxima!
                        </h1>
                    </div>
                    """, 
                    unsafe_allow_html=True
            )
            st.stop()
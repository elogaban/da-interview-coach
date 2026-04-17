import streamlit as st
import asyncio
import sys
from fpdf import FPDF
from scraper import generate_smart_questions

# Correctif pour la gestion de l'asynchronisme sur Windows
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

class PDF(FPDF):
    def header(self):
        self.set_font('Helvetica', 'B', 15)
        self.cell(0, 10, 'Mes Fiches de Revision Data Analyst', 0, 1, 'C')
        self.ln(5)

    def chapter_title(self, num, label):
        self.set_font('Helvetica', 'B', 12)
        txt = f"Question {num}: {label}".encode('latin-1', 'replace').decode('latin-1')
        self.set_fill_color(200, 220, 255)
        self.cell(0, 10, txt, 0, 1, 'L', 1)
        self.ln(2)

    def chapter_body(self, expert_ans, simple_ans):
        self.set_font('Helvetica', 'B', 10)
        self.cell(0, 10, "Reponse Expert :", 0, 1)
        self.set_font('Helvetica', '', 10)
        txt_exp = expert_ans.encode('latin-1', 'replace').decode('latin-1')
        self.multi_cell(0, 5, txt_exp)
        self.ln(2)
        self.set_font('Helvetica', 'B', 10)
        self.cell(0, 10, "L'essentiel (en langage clair) :", 0, 1)
        self.set_font('Helvetica', '', 10)
        txt_simple = simple_ans.encode('latin-1', 'replace').decode('latin-1')
        self.multi_cell(0, 5, txt_simple)
        self.ln(10)

def create_pdf(questions):
    pdf = PDF()
    pdf.add_page()
    for i, q in enumerate(questions, 1):
        pdf.chapter_title(i, q.question)
        pdf.chapter_body(q.perfect_answer, q.explanation_child)
    
    pdf_output = pdf.output(dest='S')
    if isinstance(pdf_output, bytearray):
        return bytes(pdf_output)
    return pdf_output

st.set_page_config(page_title="Coach Data Pro", page_icon="🤖", layout="wide")
st.title("🤖 Mon Coach de Révision Data")

with st.sidebar:
    st.header("🎯 Personnalisation")
    level = st.selectbox("Niveau cible :", ["Junior", "Senior", "Expert"])
    topic = st.text_input("Sujet spécifique :", placeholder="Laissez vide pour un mix")
    
    if 'questions' in st.session_state:
        st.divider()
        st.header("📥 Export")
        try:
            pdf_bytes = create_pdf(st.session_state.questions)
            st.download_button(
                label="📥 Télécharger en PDF",
                data=pdf_bytes,
                file_name=f"fiches_{level.lower()}.pdf",
                mime="application/pdf",
                use_container_width=True
            )
        except Exception as e:
            st.error(f"Erreur PDF : {e}")

# Gestion dynamique du bouton
button_label = "🚀 Générer 10 nouvelles questions" if 'questions' in st.session_state else f"🚀 Générer mes fiches ({level})"

if st.button(button_label, type="primary"):
    with st.spinner("Le coach prépare vos fiches..."):
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            data = loop.run_until_complete(generate_smart_questions(level, topic))
            if data and data.questions:
                st.session_state.questions = data.questions
                st.session_state.current_level = level
                st.rerun()
        except Exception as e:
            st.error(f"Erreur : {e}")

# Affichage des questions
if 'questions' in st.session_state:
    st.divider()
    for i, q in enumerate(st.session_state.questions, 1):
        # CHANGEMENT ICI : expanded=False pour que tout soit fermé par défaut
        with st.expander(f"Question {i} : {q.question}", expanded=False):
            st.caption(f"📂 {q.category} | 📊 {q.difficulty}")
            st.markdown("### 🎯 Réponse Expert")
            st.write(q.perfect_answer)
            st.markdown("---")
            st.markdown("### 💡 L'essentiel (en langage clair)")
            st.write(q.explanation_child)
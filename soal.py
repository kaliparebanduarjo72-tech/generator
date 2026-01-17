import streamlit as st
import google.generativeai as genai
from PyPDF2 import PdfReader
from docx import Document
from docx.shared import Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from io import BytesIO
import os
import re

# --- 1. KONFIGURASI API ---
def init_api():
    try:
        api_key = st.secrets.get("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY")
        if not api_key:
            st.error("⚠️ API Key tidak ditemukan di Secrets!")
            st.stop()
        genai.configure(api_key=api_key)
        model_list = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        selected = "models/gemini-1.5-flash" if "models/gemini-1.5-flash" in model_list else model_list[0]
        return genai.GenerativeModel(selected)
    except Exception as e:
        st.error(f"Kesalahan Konfigurasi: {e}")
        st.stop()

model = init_api()

# --- 2. FUNGSI EKSPOR KE WORD DENGAN LOGIKA TABEL ---
def export_to_word(full_text, school_name):
    doc = Document()
    title = doc.add_heading(school_name, 0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    lines = full_text.split('\n')
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        if line.startswith('|'):
            table_data = []
            while i < len(lines) and lines[i].strip().startswith('|'):
                if not re.match(r'^[|\s:-]+$', lines[i].strip()):
                    cells = [c.strip() for c in lines[i].split('|') if c.strip()]
                    if cells: table_data.append(cells)
                i += 1
            
            if table_data:
                table = doc.add_table(rows=len(table_data), cols=len(table_data[0]))
                table.style = 'Table Grid'
                for r_idx, row_cells in enumerate(table_data):
                    for c_idx, val in enumerate(row_cells):
                        if c_idx < len(table.columns):
                            table.cell(r_idx, c_idx).text = val
            continue
        
        if line:
            clean_text = line.replace("**", "").replace("###", "")
            p = doc.add_paragraph(clean_text)
            if any(x in line for x in ["KISI-KISI", "KARTU SOAL", "NASKAH"]):
                p.bold = True
        else:
            doc.add_paragraph("")
        i += 1

    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer

# --- 3. UI STREAMLIT ---
st.set_page_config(page_title="GuruAI - Full Edition", layout="wide")

st.markdown("""
    <style>
    .header-box { background: linear-gradient(135deg, #1e3c72, #2a5298); color: white; padding: 20px; border-radius: 15px; text-align: center; }
    .main-card { background: white; padding: 20px; border-radius: 15px; box-shadow: 0 4px 10px rgba(0,0,0,0.1); margin-top: 20px; color: black; }
    div[data-testid="stMarkdownContainer"] table { width: 100%; border-collapse: collapse; border: 1px solid #444; }
    div[data-testid="stMarkdownContainer"] th, td { padding: 8px; border: 1px solid #444; font-size: 12px; }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<div class="header-box"><h1>SMP NEGERI 2 KALIPARE</h1><p>Generator Soal Lengkap: PG, Kompleks, Menjodohkan, B/S, Uraian</p></div>', unsafe_allow_html=True)

col1, col2 = st.columns([2, 1])

with col1:
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    input_choice = st.radio("Sumber Materi:", ["Teks Manual", "Upload PDF"])
    materi_teks = ""
    if input_choice == "Teks Manual":
        materi_teks = st.text_area("Tempel Materi Pelajaran:", height=300)
    else:
        file_pdf = st.file_uploader("Unggah PDF", type=["pdf"])
        if file_pdf:
            reader = PdfReader(file_pdf)
            for page in reader.pages: materi_teks += page.extract_text()
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.write("⚙️ **Parameter Soal**")
    mapel = st.text_input("Mata Pelajaran", "Seni Rupa")
    
    # MENGEMBALIKAN PILIHAN BENTUK SOAL 
    bentuk_soal = st.multiselect(
        "Bentuk Soal:",
        ["Pilihan Ganda (PG)", "PG Kompleks", "Benar/Salah", "Menjodohkan", "Uraian"],
        default=["Pilihan Ganda (PG)", "Benar/Salah"]
    )
    
    jumlah = st.slider("Jumlah Soal", 1, 30, 5)
    
    if st.button("Generate Perangkat Lengkap ✨", use_container_width=True):
        if materi_teks:
            with st.spinner("AI sedang merancang soal variatif dan stimulus..."):
                str_bentuk = ", ".join(bentuk_soal)
                prompt = (
                    f"Materi: {materi_teks[:4000]}. Mapel: {mapel}. Sekolah: SMP NEGERI 2 KALIPARE.\n\n"
                    f"Buatkan {jumlah} soal HOTS dengan variasi bentuk: {str_bentuk}.\n"
                    f"Setiap soal wajib memiliki STIMULUS (teks, kasus, atau data) sebelum pertanyaan.\n\n"
                    f"FORMAT OUTPUT:\n"
                    f"1. **KISI-KISI SOAL**: Tabel Markdown (No | TP | Materi | Indikator | Level | No Soal)\n"
                    f"2. **KARTU SOAL**: Tabel Markdown per soal (Nomor | Indikator | Level | Kunci | Rumusan Soal)\n"
                    f"3. **NASKAH SOAL**: Opsi PG (A, B, C, D) wajib BARIS BARU. Untuk Menjodohkan, buat format premis dan respon yang jelas.\n"
                    f"4. **KUNCI JAWABAN & PEMBAHASAN**.\n\n"
                    f"PENTING: Gunakan pembatas tabel '|' secara konsisten."
                )
                response = model.generate_content(prompt)
                st.session_state['hasil_final'] = response.text
        else:
            st.warning("Masukkan materi terlebih dahulu!")

if 'hasil_final' in st.session_state:
    st.markdown("### Preview Perangkat Penilaian")
    st.markdown(st.session_state['hasil_final'])
    
    st.divider()
    st.download_button(
        "📥 Download Word (Tabel Kisi-kisi & Kartu Soal)", 
        data=export_to_word(st.session_state['hasil_final'], "SMP NEGERI 2 KALIPARE"), 
        file_name=f"Perangkat_Ujian_{mapel}.docx", 
        use_container_width=True
    )

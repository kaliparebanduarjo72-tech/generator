import streamlit as st
import google.generativeai as genai
from PyPDF2 import PdfReader
from docx import Document
from docx.shared import Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from fpdf import FPDF
from io import BytesIO
import os
import re

# --- 1. KONFIGURASI API ---
def init_api():
    try:
        api_key = st.secrets.get("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY")
        if not api_key:
            st.error("⚠️ API Key tidak ditemukan!")
            st.stop()
        genai.configure(api_key=api_key)
        model_list = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        selected = "models/gemini-1.5-flash" if "models/gemini-1.5-flash" in model_list else model_list[0]
        return genai.GenerativeModel(selected)
    except Exception as e:
        st.error(f"Kesalahan Konfigurasi: {e}")
        st.stop()

model = init_api()

# --- 2. FUNGSI EKSPOR KE WORD (DENGAN TABEL ASLI) ---
def create_word_table(doc, markdown_table):
    """Mengubah teks tabel markdown menjadi tabel asli di Word"""
    lines = [line.strip() for line in markdown_table.strip().split('\n') if line.strip()]
    if len(lines) < 2: return
    
    # Ambil baris data (abaikan baris pemisah |---|)
    rows_data = []
    for line in lines:
        if re.match(r'^[|\s:-]+$', line): continue
        cells = [c.strip() for c in line.split('|') if c.strip()]
        if cells: rows_data.append(cells)
    
    if not rows_data: return

    table = doc.add_table(rows=len(rows_data), cols=len(rows_data[0]))
    table.style = 'Table Grid'
    
    for i, row in enumerate(rows_data):
        for j, cell_text in enumerate(row):
            if j < len(table.columns):
                table.cell(i, j).text = cell_text

def export_to_word(full_text, school_name):
    doc = Document()
    
    # Header Sekolah
    title = doc.add_heading(school_name, 0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    # Memisahkan teks berdasarkan bagian tabel dan teks biasa
    sections = re.split(r'(\n\|.*\|\n)', full_text)
    
    for section in sections:
        if "|" in section and "---" not in section: # Deteksi baris tabel
            # Jika bagian ini terlihat seperti tabel, kita kumpulkan barisnya
            create_word_table(doc, section)
        else:
            # Teks biasa (bersihkan sisa markdown)
            clean_text = section.replace("**", "").replace("###", "").strip()
            if clean_text:
                p = doc.add_paragraph(clean_text)
                p.alignment = WD_ALIGN_PARAGRAPH.LEFT

    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer

# --- 3. UI STREAMLIT ---
st.set_page_config(page_title="GuruAI - SMPN 2 Kalipare", layout="wide")

st.markdown("""
    <style>
    .header-box { background: linear-gradient(135deg, #1e3c72, #2a5298); color: white; padding: 20px; border-radius: 15px; text-align: center; }
    .main-card { background: white; padding: 20px; border-radius: 15px; box-shadow: 0 4px 10px rgba(0,0,0,0.1); margin-top: 20px; color: black; }
    div[data-testid="stMarkdownContainer"] table { width: 100%; border-collapse: collapse; border: 1px solid #444; }
    div[data-testid="stMarkdownContainer"] th, td { padding: 8px; border: 1px solid #444; }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<div class="header-box"><h1>SMP NEGERI 2 KALIPARE</h1><p>Penulisan Kisi-kisi & Kartu Soal Otomatis</p></div>', unsafe_allow_html=True)

col1, col2 = st.columns([2, 1])

with col1:
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    input_choice = st.radio("Sumber:", ["Teks Manual", "Upload PDF"])
    materi = ""
    if input_choice == "Teks Manual":
        materi = st.text_area("Materi:", height=250)
    else:
        f = st.file_uploader("Upload PDF", type=["pdf"])
        if f:
            reader = PdfReader(f)
            for page in reader.pages: materi += page.extract_text()
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.write("⚙️ **Pengaturan**")
    mapel = st.text_input("Mata Pelajaran", "Seni Rupa")
    jumlah = st.slider("Jumlah Soal", 1, 20, 5)
    
    if st.button("Generate Perangkat Soal ✨", use_container_width=True):
        if materi:
            with st.spinner("Menyusun tabel dan naskah..."):
                prompt = (
                    f"Materi: {materi[:4000]}. Mapel: {mapel}. Sekolah: SMP NEGERI 2 KALIPARE.\n\n"
                    f"Buatkan {jumlah} soal PG dan Benar/Salah.\n"
                    f"STRUKTUR WAJIB:\n"
                    f"1. KISI-KISI SOAL: (Gunakan Tabel Markdown: No | TP | Materi | Indikator | Level | No Soal)\n"
                    f"2. KARTU SOAL: (Buat Tabel Markdown untuk TIAP soal. Baris WAJIB: Nomor, Indikator, Level, Bentuk, Kunci Jawaban, Rumusan Soal)\n"
                    f"3. NASKAH SOAL: (Susun rapi. Opsi A, B, C, D WAJIB tersusun kebawah/baris baru)\n"
                    f"4. KUNCI JAWABAN: (Daftar singkat)\n"
                    f"\nPENTING: Opsi jawaban jangan menyamping. Contoh:\n"
                    f"A. Opsi 1\nB. Opsi 2\n"
                )
                response = model.generate_content(prompt)
                st.session_state['hasil'] = response.text
        else:
            st.warning("Isi materi!")

if 'hasil' in st.session_state:
    st.markdown("### Preview Hasil")
    st.markdown(st.session_state['hasil'])
    
    st.divider()
    st.download_button(
        "📥 Download Word (Tabel Asli)", 
        data=export_to_word(st.session_state['hasil'], "SMP NEGERI 2 KALIPARE"), 
        file_name=f"Soal_{mapel}.docx", 
        use_container_width=True
    )

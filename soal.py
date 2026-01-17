import streamlit as st
from PyPDF2 import PdfReader
from fpdf import FPDF
import time

# 1. KONFIGURASI HALAMAN
st.set_page_config(page_title="AI Generator & PDF Reader", page_icon="📄")

# 2. CSS KUSTOM (Gaya Kertas Ujian & Glassmorphism)
st.markdown("""
    <style>
    .stTextInput input, .stTextArea textarea {
        border-radius: 15px !important;
        border: 2px solid #e0e0e0 !important;
    }
    div.stButton > button {
        background: linear-gradient(135deg, #007bff, #00c6ff);
        color: white !important;
        border-radius: 50px !important;
        width: 100%;
        font-weight: bold;
        height: 3em;
    }
    .exam-paper {
        background-color: white;
        padding: 30px;
        border-left: 8px solid #007bff;
        border-radius: 15px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        color: #333;
        margin-top: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. HEADER
st.title("📄 AI Soal Generator")
st.write("Unggah materi PDF atau ketik topik untuk membuat soal otomatis.")

# 4. FITUR UPLOAD PDF
uploaded_file = st.file_uploader("Unggah Materi (PDF)", type="pdf")
konten_materi = ""

if uploaded_file is not None:
    reader = PdfReader(uploaded_file)
    # Mengambil teks dari halaman pertama sebagai contoh
    halaman = reader.pages[0]
    konten_materi = halaman.extract_text()
    st.success("PDF berhasil dibaca!")
    with st.expander("Lihat isi materi"):
        st.write(konten_materi)

# 5. INPUT TAMBAHAN
topik = st.text_input("Atau masukkan Topik Materi secara manual:", placeholder="Contoh: Ekosistem")
jumlah = st.slider("Jumlah Soal", 1, 5, 3)

# 6. TOMBOL GENERATE
if st.button("BUAT SOAL SEKARANG"):
    sumber = topik if topik else (konten_materi[:100] if konten_materi else None)
    
    if sumber:
        with st.spinner('Sedang memproses...'):
            time.sleep(2)
            st.markdown("### 📝 Hasil Draft Soal")
            
            hasil_html = f"<div class='exam-paper'>"
            hasil_html += f"<h2>Lembar Ujian: {topik if topik else 'Dari PDF'}</h2>"
            
            for i in range(1, jumlah + 1):
                hasil_html += f"<p><strong>Soal {i}:</strong> Apa kesimpulan utama dari materi tentang {topik if topik else 'PDF ini'}?</p>"
                hasil_html += "<p><small>A. ......... B. ......... C. .........</small></p><hr>"
            
            hasil_html += "</div>"
            st.markdown(hasil_html, unsafe_allow_html=True)
            st.balloons()
    else:
        st.warning("Mohon unggah PDF atau isi topik terlebih dahulu.")

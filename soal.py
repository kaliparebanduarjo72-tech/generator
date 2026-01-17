import streamlit as st
import time

# 0. Konfigurasi Halaman (Opsional tapi direkomendasikan)
st.set_page_config(page_title="AI Generator Soal", page_icon="📝")

# 1. --- KUSTOMISASI CSS & JS (DIGABUNGKAN) ---
st.markdown("""
    <style>
    /* CSS: Efek Glassmorphism pada Input */
    .stTextArea textarea, .stTextInput input {
        background: rgba(255, 255, 255, 0.9);
        border-radius: 15px !important;
        border: 2px solid #e0e0e0 !important;
        transition: all 0.3s ease;
    }
    .stTextArea textarea:focus, .stTextInput input:focus {
        border-color: #007bff !important;
        box-shadow: 0 0 15px rgba(0, 123, 255, 0.2) !important;
    }

    /* CSS: Animasi Berdenyut pada Tombol */
    div.stButton > button {
        background: linear-gradient(135deg, #007bff, #00c6ff);
        color: white !important;
        border-radius: 50px !important;
        border: none !important;
        padding: 10px 25px !important;
        font-weight: 700 !important;
        text-transform: uppercase;
        letter-spacing: 1px;
        transition: transform 0.2s ease;
        width: 100%;
    }
    div.stButton > button:hover {
        transform: scale(1.02);
        box-shadow: 0 10px 20px rgba(0, 123, 255, 0.3);
    }

    /* CSS: Styling Hasil AI agar Seperti Kertas Ujian */
    .exam-paper {
        background-color: white;
        padding: 30px;
        border-left: 8px solid #007bff;
        border-radius: 15px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        font-family: 'Inter', sans-serif;
        color: #333;
        margin-top: 20px;
    }
    
    .question-box {
        margin-bottom: 20px;
        padding-bottom: 10px;
        border-bottom: 1px dashed #eee;
    }
    </style>

    <script>
    const scrollResult = () => {
        window.scrollTo({
            top: document.body.scrollHeight,
            behavior: 'smooth'
        });
    };
    </script>
    """, unsafe_allow_html=True)

# 2. --- HEADER APLIKASI ---
st.title("📝 AI Question Generator")
st.write("Masukkan topik materi Anda di bawah ini untuk membuat soal secara otomatis.")

# 3. --- INPUT AREA ---
with st.container():
    topik = st.text_input("Topik Materi", placeholder="Contoh: Ekosistem Laut atau Sejarah Proklamasi")
    
    col1, col2 = st.columns(2)
    with col1:
        tingkat = st.selectbox("Tingkat Kesulitan", ["Mudah", "Sedang", "Sulit"])
    with col2:
        jumlah = st.slider("Jumlah Soal", 1, 10, 5)

# 4. --- LOGIKA GENERATOR ---
if st.button("GENERATE SOAL SEKARANG"):
    if topik:
        with st.spinner('Sedang merancang soal untuk Anda...'):
            # Simulasi loading agar terasa seperti AI sedang berpikir
            time.sleep(2) 
            
            # Memulai kontainer hasil
            st.markdown("### 📄 Hasil Draft Soal")
            
            # Membuat konten soal (Placeholder logic)
            # Di bagian ini nantinya Anda bisa hubungkan ke API OpenAI/Gemini
            hasil_html = f"<div class='exam-paper'>"
            hasil_html += f"<h2>Ujian: {topik}</h2>"
            hasil_html += f"<p><strong>Tingkat:</strong> {tingkat} | <strong>Jumlah:</strong> {jumlah} Soal</p><br>"
            
            for i in range(1, jumlah + 1):
                hasil_html += f"""
                <div class='question-box'>
                    <strong>Soal {i}:</strong> Apa peran utama dari komponen {topik} dalam sistem yang lebih luas?
                    <br><br>
                    <small>A. .................... B. .................... C. ....................</small>
                </div>
                """
            
            hasil_html += "</div>"
            
            # Menampilkan hasil ke layar
            st.markdown(hasil_html, unsafe_allow_html=True)
            st.balloons()
            
    else:
        st.error("Mohon isi topik materi terlebih dahulu!")

# 5. --- FOOTER ---
st.markdown("---")
st.caption("Aplikasi ini menggunakan Streamlit Custom CSS untuk tampilan modern.")

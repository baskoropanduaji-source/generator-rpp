import streamlit as st
import google.generativeai as genai
from docx import Document
from docx.shared import Pt, RGBColor, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
import io
import re
import datetime

# ==========================================
# 1. KONFIGURASI HALAMAN
# ==========================================
st.set_page_config(
    page_title="Generator RPP - Baskoro Pandu Aji",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS Custom (Clean)
st.markdown("""
<style>
    .stApp { background-color: #f1f8f3; }
    h1 { color: #1b5e20 !important; font-family: 'Helvetica', sans-serif; }
    h2, h3 { color: #2e7d32 !important; }
    div[data-testid="stForm"] { background-color: #ffffff; padding: 30px; border-radius: 15px; border-top: 5px solid #4caf50; }
    div.stButton > button { background-color: #2e7d32; color: white; width: 100%; }
    .profile-img { display: block; margin: 0 auto; width: 120px; border-radius: 50%; }
    .clean-btn { display: block; text-align: center; background: white; color: #2e7d32; padding: 10px; margin: 5px 0; border: 1px solid #2e7d32; text-decoration: none; border-radius: 5px; }
    .main-btn { display: block; text-align: center; background: #2e7d32; color: white !important; padding: 10px; margin: 10px 0; text-decoration: none; border-radius: 5px; }
    .donation-box { background: #fff3cd; color: #856404; padding: 15px; border-radius: 5px; text-align: center; margin-top: 20px; font-size: 12px; }
    .footer-text { text-align: center; color: #888; font-size: 11px; margin-top: 40px; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. API SETUP
# ==========================================
try:
    api_key = st.secrets["GEMINI_API_KEY"]
except:
    api_key = "" 

if api_key:
    genai.configure(api_key=api_key)

# ==========================================
# 3. SIDEBAR
# ==========================================
with st.sidebar:
    st.markdown('<img src="https://i.ibb.co.com/00QNsb6/IMG-6622-2.jpg" class="profile-img">', unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center; color: #1b5e20;'>Baskoro Pandu Aji, S.Pd.</h3>", unsafe_allow_html=True)
    
    st.markdown('<a href="https://baskoropandu.my.canva.site/profil-baskoro-pandu-aji" target="_blank" class="main-btn">KUNJUNGI PROFIL</a>', unsafe_allow_html=True)
    st.info("Pengembang Aplikasi Pendidikan & Kepala Sekolah SDN 183/II Sumber Mulya")
    
    st.write("---")
    st.markdown("**KONTAK SAYA**")
    st.markdown('<a href="https://wa.me/6281329951000" target="_blank" class="clean-btn">WhatsApp</a>', unsafe_allow_html=True)
    st.markdown('<a href="https://instagram.com/baskoro_panduaji" target="_blank" class="clean-btn">Instagram</a>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="donation-box">
        <b>TRAKTIR KOPI / DONASI</b><br>
        Support Top Up GoPay:<br>
        <h3 style="margin:5px 0;">081329951000</h3>
        a.n Baskoro Pandu Aji
    </div>
    """, unsafe_allow_html=True)

# ==========================================
# 4. LOGIKA AI
# ==========================================
def generate_rpp(data):
    if not api_key: return "Error: API Key belum terdeteksi."
    
    prompt = f"""
    Buat RPP/Modul Ajar Kurikulum Merdeka (Deep Learning).
    Langsung isi konten tanpa pembuka.
    Identitas tidak perlu (sudah ada tabel).
    Format: Markdown.
    
    DATA:
    Mapel: {data['mapel']} | Topik: {data['topik']} | TP: {data['tp']} | Model: {data['metode']}
    
    STRUKTUR:
    ## A. CAPAIAN PEMBELAJARAN
    (Isi singkat)
    ## B. KOMPONEN PERANCANGAN
    **1. Mitra:** (Isi)
    **2. Lingkungan:** (Isi)
    **3. Digital:** (Isi)
    ## C. KOMPONEN INTI
    **1. TP:** {data['tp']}
    **2. Pemahaman Bermakna:** (Isi)
    **3. Pertanyaan Pemantik:** (Isi)
    ## D. KEGIATAN PEMBELAJARAN (Model: {data['metode']})
    (Gunakan List Poin-Poin untuk: Pendahuluan, Inti sesuai sintaks, Penutup)
    ## E. ASESMEN
    (Rencana, Formatif, Sumatif)
    ## F. MEDIA
    (Buku, Video Youtube Relevan, Artikel)
    ## G. LAMPIRAN
    (LKPD & Rubrik Penilaian dalam Tabel)
    """
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content(prompt)
    return response.text.replace("<br>", "\n")

# ==========================================
# 5. FORMATTER WORD
# ==========================================
def create_docx(text, data):
    doc = Document()
    style = doc.styles['Normal']
    style.font.name = 'Times New Roman'
    style.font.size = Pt(12)
    
    p = doc.add_paragraph("RANCANGAN PEMBELAJARAN MENDALAM")
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.runs[0].bold = True
    
    doc.add_heading('INFORMASI UMUM', level=1).style.font.color.rgb = RGBColor(0,0,0)
    table = doc.add_table(rows=8, cols=3)
    table.style = 'Table Grid'
    info = [
        ("Nama Penyusun", ":", data['guru']), ("Sekolah", ":", data['sekolah']),
        ("Kelas/Fase", ":", f"{data['kelas']}/{data['fase']}"), ("Tahun", ":", data['tahun']),
        ("Topik", ":", data['topik']), ("Waktu", ":", data['waktu']),
        ("Model", ":", data['metode']), ("Profil", ":", ", ".join(data['profil']))
    ]
    for i, row_data in enumerate(info):
        cells = table.rows[i].cells
        cells[0].text = row_data[0]
        cells[1].text = row_data[1]
        cells[2].text = row_data[2]
    
    doc.add_paragraph()
    
    # Parsing Text
    for line in text.split('\n'):
        line = line.strip()
        if not line: continue
        if line.startswith('# '): doc.add_heading(line.replace('# ', ''), 1).style.font.color.rgb = RGBColor(0,0,0)
        elif line.startswith('## '): doc.add_heading(line.replace('## ', ''), 2).style.font.color.rgb = RGBColor(0,0,0)
        elif line.startswith('* ') or line.startswith('- '): doc.add_paragraph(line[2:], style='List Bullet')
        elif "|" in line: doc.add_paragraph(line) # Simple table fallback
        else: doc.add_paragraph(line)
        
    # Tanda Tangan
    doc.add_paragraph("\n\n")
    sig = doc.add_table(rows=1, cols=2)
    sig.autofit = True
    
    kiri = sig.rows[0].cells[0].add_paragraph(f"Mengetahui,\nKepala Sekolah\n\n\n{data['kepsek']}\nNIP. {data['nip_kepsek']}")
    kiri.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    kanan = sig.rows[0].cells[1].add_paragraph(f"{data['kota']}, {data['tanggal']}\nGuru Mata Pelajaran\n\n\n{data['guru']}\nNIP. {data['nip_guru']}")
    kanan.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    bio = io.BytesIO()
    doc.save(bio)
    return bio

# ==========================================
# 6. UI UTAMA
# ==========================================
st.title("GENERATOR RPP PINTAR")
st.markdown("Kurikulum Merdeka & Deep Learning")

with st.form("main_form"):
    c1, c2 = st.columns(2)
    with c1:
        guru = st.text_input("Nama Guru", "Tuti Haryanti, S.Pd.")
        nip_guru = st.text_input("NIP Guru")
        sekolah = st.text_input("Sekolah", "SDN 183/II Sumber Mulya")
        kota = st.text_input("Kota", "Jambi")
    with c2:
        kepsek = st.text_input("Kepala Sekolah", "Baskoro Pandu Aji, S.Pd.")
        nip_kepsek = st.text_input("NIP Kepsek")
        tanggal = st.text_input("Tanggal", datetime.date.today().strftime("%d %B %Y"))
        
    st.markdown("---")
    c3, c4 = st.columns(2)
    with c3:
        mapel = st.text_input("Mapel", "Koding & AI")
        kelas = st.selectbox("Kelas", [str(i) for i in range(1,7)])
        fase = st.selectbox("Fase", ["A","B","C"])
        tahun = st.text_input("Tahun Ajar", "2024/2025")
    with c4:
        topik = st.text_input("Topik")
        waktu = st.text_input("Waktu", "2 x 35 Menit")
        metode = st.selectbox("Model", ["PBL", "PjBL", "Inquiry"])
        
    tp = st.text_area("Tujuan Pembelajaran (TP)")
    
    c5, c6 = st.columns(2)
    with c5: asesmen = st.multiselect("Asesmen", ["Tertulis", "Lisan", "Proyek"], default=["Tertulis"])
    with c6: profil = st.multiselect("Profil Pancasila", ["Bernalar Kritis", "Kreatif", "Mandiri"], default=["Bernalar Kritis"])
    
    submit = st.form_submit_button("BUAT RPP SEKARANG")

if submit:
    if not api_key: st.error("API Key belum disetting di Secrets!")
    else:
        with st.spinner("Sedang memproses..."):
            data = {"guru":guru, "nip_guru":nip_guru, "kepsek":kepsek, "nip_kepsek":nip_kepsek, "kota":kota, "tanggal":tanggal, "sekolah":sekolah, "mapel":mapel, "kelas":kelas, "fase":fase, "tahun":tahun, "topik":topik, "waktu":waktu, "metode":metode, "tp":tp, "asesmen":asesmen, "profil":profil}
            
            hasil = generate_rpp(data)
            st.markdown(hasil)
            
            docx = create_docx(hasil, data)
            st.download_button("UNDUH DOCX", docx.getvalue(), "RPP.docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document")

st.markdown("""<div class="footer-text">Copyright © 2025 Baskoro Pandu Aji, S.Pd.</div>""", unsafe_allow_html=True)

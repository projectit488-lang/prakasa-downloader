import os
import tempfile
import streamlit as st
import yt_dlp

# Set konfigurasi halaman browser
st.set_page_config(page_title="Prakasa Downloader", page_icon="🎬", layout="centered")

# --- HEADER APP ---
col_logo, col_title = st.columns([1, 4])
with col_title:
    st.title("🎬 Prakasa Downloader")
    st.caption("Unduh Video & Audio YouTube Langsung ke Browser Kamu")

st.markdown("---")

# --- INPUT URL & FORMAT ---
url = st.text_input("Link / URL YouTube:", placeholder="https://www.youtube.com/watch?v=...")

option = st.radio("Pilih Format Unduhan:", ["MP3 (Audio)", "MP4 (Video)"], horizontal=True)

# --- PILIHAN KUALITAS/RESOLUSI ---
if option == "MP3 (Audio)":
    quality = st.selectbox(
        "Pilih Kualitas Audio (Bitrate):",
        options=["320 kbps (Kualitas Terbaik)", "192 kbps (Kualitas Standar)", "128 kbps (Ukuran Kecil)"],
        index=1
    )
    bitrate_map = {
        "320 kbps (Kualitas Terbaik)": "320",
        "192 kbps (Kualitas Standar)": "192",
        "128 kbps (Ukuran Kecil)": "128"
    }
    selected_quality = bitrate_map[quality]
else:
    res = st.selectbox(
        "Pilih Resolusi Video:",
        options=["1080p (Full HD)", "720p (HD)", "480p (SD)", "360p (Rendah)"],
        index=1
    )
    res_map = {
        "1080p (Full HD)": "1080",
        "720p (HD)": "720",
        "480p (SD)": "480",
        "360p (Rendah)": "360"
    }
    selected_quality = res_map[res]

# Inisialisasi penyimpanan session untuk data file
if "download_data" not in st.session_state:
    st.session_state["download_data"] = None

# --- PROSES PEMPROSESAN ---
if st.button("Proses Video", type="primary", use_container_width=True):
    if not url.strip():
        st.warning("⚠️ Harap masukkan link YouTube terlebih dahulu!")
    else:
        status = st.empty()
        status.info("⏳ Sedang mengunduh dan memproses media dari YouTube... Mohon tunggu.")
        
        # Reset state unduhan sebelumnya
        st.session_state["download_data"] = None

        # Menggunakan direktori sementara agar tidak menumpuk file sampah di komputer
        with tempfile.TemporaryDirectory() as temp_dir:
            out_template = os.path.join(temp_dir, '%(title)s.%(ext)s')

            if option == "MP3 (Audio)":
                ydl_opts = {
                    'format': 'bestaudio/best',
                    'outtmpl': out_template,
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': selected_quality,
                    }],
                    'quiet': True,
                }
            else:
                # Format string untuk membatasi resolusi maksimum sesuai pilihan user
                format_str = (
                    f'bestvideo[height<={selected_quality}][ext=mp4]+bestaudio[ext=m4a]/'
                    f'best[height<={selected_quality}][ext=mp4]/best[height<={selected_quality}]/best'
                )
                ydl_opts = {
                    'format': format_str,
                    'outtmpl': out_template,
                    'merge_output_format': 'mp4',
                    'quiet': True,
                }

            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=True)
                    filename = ydl.prepare_filename(info)
                    
                    # Penyesuaian nama file jika dikonversi ke MP3
                    if option == "MP3 (Audio)":
                        base, _ = os.path.splitext(filename)
                        filename = base + ".mp3"

                if os.path.exists(filename):
                    # Membaca data binary file untuk dikirim ke browser
                    with open(filename, "rb") as f:
                        file_bytes = f.read()

                    file_name = os.path.basename(filename)
                    mime_type = "audio/mpeg" if option == "MP3 (Audio)" else "video/mp4"

                    st.session_state["download_data"] = {
                        "bytes": file_bytes,
                        "name": file_name,
                        "mime": mime_type
                    }
                    status.success("✅ Pemrosesan selesai! Klik tombol download di bawah.")
                    st.balloons()
                else:
                    status.error("❌ File hasil proses tidak ditemukan.")

            except Exception as e:
                status.error(f"❌ Terjadi kesalahan: {e}")

# --- TOMBOL DOWNLOAD KE BROWSER ---
if st.session_state["download_data"] is not None:
    data = st.session_state["download_data"]
    st.markdown("---")
    st.download_button(
        label=f"📥 Download Ke HP / Komputer ({data['name']})",
        data=data["bytes"],
        file_name=data["name"],
        mime=data["mime"],
        use_container_width=True,
        type="primary"
    )
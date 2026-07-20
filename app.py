import streamlit as st
import requests

# Set konfigurasi halaman browser
st.set_page_config(page_title="Prakasa Downloader", page_icon="🎬", layout="centered")

# --- HEADER APP ---
st.title("🎬 Prakasa Downloader")
st.caption("Unduh Video & Audio YouTube via API Server")
st.markdown("---")

# --- MASUKKAN RAPIDAPI KEY ---
# Disarankan disimpan di Streamlit Secrets, atau bisa di-input via sidebar
API_KEY = st.secrets.get("6489fa60f8mshbc6351d4d65d62fp1bed4ejsn90afd3f18a41", "")

if not API_KEY:
    API_KEY = st.sidebar.text_input("Masukkan RapidAPI Key:", type="password")
    st.sidebar.info("Dapatkan API Key gratis di RapidAPI.com")

# --- INPUT URL & FORMAT ---
url = st.text_input("Link / URL YouTube:", placeholder="https://www.youtube.com/watch?v=...")
option = st.radio("Pilih Format Unduhan:", ["MP3 (Audio)", "MP4 (Video)"], horizontal=True)

# Function untuk memanggil RapidAPI (Contoh menggunakan endpoint Y2Mate / YT Downloader)
def get_download_link_from_api(video_url, format_type, api_key):
    # Endpoint API (Sesuaikan jika kamu memakai penyedia API lain di RapidAPI)
    api_url = "https://youtube-mp3-downloader2.p.rapidapi.com/ytmp3/ytmp3/"
    
    headers = {
        "x-rapidapi-key": api_key,
        "x-rapidapi-host": "youtube-mp3-downloader2.p.rapidapi.com"
    }
    
    querystring = {"url": video_url}
    
    response = requests.get(api_url, headers=headers, params=querystring)
    
    if response.status_code == 200:
        data = response.json()
        # Mengembalikan link download dari respon JSON API
        return data.get("link") or data.get("download_url")
    else:
        raise Exception(f"API Error {response.status_code}: {response.text}")

# --- PROSES PEMPROSESAN ---
if st.button("Proses Video", type="primary", use_container_width=True):
    if not url.strip():
        st.warning("⚠️ Harap masukkan link YouTube terlebih dahulu!")
    elif not API_KEY:
        st.error("❌ RapidAPI Key belum diisi!")
    else:
        status = st.empty()
        status.info("⏳ Meminta link unduhan dari API Server...")

        try:
            download_url = get_download_link_from_api(url, option, API_KEY)

            if download_url:
                status.success("✅ Pemrosesan selesai! Klik tombol di bawah untuk mengunduh.")
                st.balloons()
                
                # Tampilkan tombol langsung ke link download
                st.markdown("---")
                st.link_button(
                    label=f"📥 Download File ({option})",
                    url=download_url,
                    use_container_width=True,
                    type="primary"
                )
            else:
                status.error("❌ Gagal mendapatkan link unduhan dari API.")

        except Exception as e:
            status.error(f"❌ Terjadi kesalahan: {e}")

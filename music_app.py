import streamlit as st
import base64
import os
from streamlit_option_menu import option_menu
from state_manager import save_state, load_state
import time
import json
from streamlit_lottie import st_lottie

# ---- Page Configuration ----    
st.set_page_config(page_title="Music-app", layout="centered")

# --- Splash Animation ---
def load_lottiefile(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)

if "show_intro" not in st.session_state:
    st.session_state.show_intro = True

if st.session_state.show_intro:
    lottie_intro = load_lottiefile("music.json")
    splash = st.empty()
    with splash.container():
        st.markdown("<h1 style='text-align:center;'>Welcome to MUSIC HUB!</h1>", unsafe_allow_html=True)
        st_lottie(lottie_intro, height=280, speed=0.5, loop=False)
        time.sleep(2)
    splash.empty()
    st.session_state.show_intro = False



# ---- Set Background & Neon Sidebar ----
def set_local_background(image_file):
    with open(image_file, "rb") as img:
        encoded = base64.b64encode(img.read()).decode()
    css = f"""
    <style>
    html, body, .stApp {{
        background-image: url("data:image/jpg;base64,{encoded}");
        background-size: cover;
        background-repeat: no-repeat;
        background-attachment: fixed;
        background-position: center;
    }}
    [data-testid="stAppViewContainer"],
    [data-testid="stHeader"],
    [data-testid="stToolbar"],
    [data-testid="stVerticalBlock"],
    .main, .block-container,
    .css-1d391kg, .css-18ni7ap {{
        background: transparent !important;
    }}
    section[data-testid="stSidebar"] {{
        background-color: rgba(255, 255, 255, 0.08) !important;
        backdrop-filter: blur(12px);
        box-shadow: inset 0 0 10px #00ffff60, 0 0 20px #00ffff88;
        border-right: 1px solid rgba(255, 255, 255, 0.2);
    }}
    section[data-testid="stSidebar"] * {{
        background-color: transparent !important;
    }}
    button:hover {{
        border: 1px solid #00ffff !important;
        box-shadow: 0 0 12px #00ffff60;
        color: #00ffff !important;
        transition: all 0.3s ease-in-out;
    }}
    #inspo-quote {{
        position: fixed;
        bottom: 12px;
        right: 18px;
        font-size: 14px;
        font-style: italic;
        color: #ffffffcc;
        background: rgba(0,0,0,0.25);
        padding: 6px 12px;
        border-radius: 8px;
        z-index: 999;
        pointer-events: none;
    }}
    </style>
    <div id="inspo-quote">“Where words fail, music speaks.” 🎧</div>
    """
    st.markdown(css, unsafe_allow_html=True)

set_local_background("wallpaper.jpg")

# ---- Load Songs from Local Folder ----
ASSET_FOLDER = "assets/songs"

if "songs" not in st.session_state:
    st.session_state.songs = []
    if os.path.exists(ASSET_FOLDER):
        for file in os.listdir(ASSET_FOLDER):
            if file.endswith((".mp3", ".wav")):
                with open(os.path.join(ASSET_FOLDER, file), "rb") as audio:
                    st.session_state.songs.append({
                        "name": file,
                        "data": audio.read()
                    })

# ---- Load Likes and Playlists from state_manager ----
if "liked" not in st.session_state or "playlists" not in st.session_state:
    liked, playlists = load_state()
    st.session_state.liked = liked
    st.session_state.playlists = playlists

# ---- Sidebar Navigation ----
with st.sidebar:
    page = option_menu(
        "🎧 Music time Menu",
        ["All Songs", "Liked", "Playlists"],
        icons=["music-note-list", "heart-fill", "music-player"],
        menu_icon="vinyl",
        default_index=0,
    )

    st.subheader("🔍 Search Songs")
    search_query = st.text_input("Type to search", key="search_box")

    if page == "Playlists":
        st.subheader("➕ Create New Playlist")
        new_playlist = st.text_input("Playlist Name")
        if st.button("Create"):
            if new_playlist and new_playlist not in st.session_state.playlists:
                st.session_state.playlists[new_playlist] = []
                save_state(st.session_state.liked, st.session_state.playlists)
                st.success(f"Playlist created: {new_playlist}")

        st.subheader("🗑️ Delete a Playlist")
        if st.session_state.playlists:
            to_delete = st.selectbox("Select playlist", list(st.session_state.playlists.keys()))
            if st.button("Delete Playlist"):
                del st.session_state.playlists[to_delete]
                save_state(st.session_state.liked, st.session_state.playlists)
                st.success(f"Deleted playlist: {to_delete}")
        else:
            st.caption("No playlists to delete.")

# ---- Title + Upload ----
st.title(f"🎵 {page}")

# ---- Display Function ----
def display_song(song, idx):
    st.markdown(f"### {idx}. {song['name']}")
    st.audio(song["data"])
    col1, col2 = st.columns(2)

    if song["name"] in st.session_state.liked:
        if col1.button("❤️ Unlike", key=f"unlike_{song['name']}"):
            st.session_state.liked.remove(song["name"])
            save_state(st.session_state.liked, st.session_state.playlists)
    else:
        if col1.button("🤍 Like", key=f"like_{song['name']}"):
            st.session_state.liked.add(song["name"])
            save_state(st.session_state.liked, st.session_state.playlists)

    if st.session_state.playlists:
        selected = col2.selectbox("Add to playlist", list(st.session_state.playlists.keys()), key=f"pl_{song['name']}")
        if col2.button("➕ Add", key=f"add_{song['name']}"):
            if song["name"] not in st.session_state.playlists[selected]:
                st.session_state.playlists[selected].append(song["name"])
                save_state(st.session_state.liked, st.session_state.playlists)
                st.success(f"Added to {selected}")

    st.markdown("<hr style='margin: 20px 0;'>", unsafe_allow_html=True)

# ---- Page Content ----
filtered = [s for s in st.session_state.songs if search_query.lower() in s["name"].lower()] if search_query else st.session_state.songs

if page == "All Songs":
    for idx, song in enumerate(filtered, 1):
        display_song(song, idx)
elif page == "Liked":
    liked_songs = [s for s in filtered if s["name"] in st.session_state.liked]
    if liked_songs:
        for idx, song in enumerate(liked_songs, 1):
            display_song(song, idx)
    else:
        st.info("No liked songs match your search.")
elif page == "Playlists":
    for pl_name, song_names in st.session_state.playlists.items():
        st.subheader(f"📂 {pl_name}")
        matched = [s for s in st.session_state.songs if s["name"] in song_names]
        if search_query:
            matched = [s for s in matched if search_query.lower() in s["name"].lower()]
        if matched:
            for idx, song in enumerate(matched, 1):
                display_song(song, idx)
        else:
            st.caption("🫗 No matching songs in this playlist.")

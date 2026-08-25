import os
import spotipy
import streamlit as st
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv
import secrets

from ffushler import (get_playlist, get_tracks, shuffle, update_playlist)

st.set_page_config(page_title="ffushler",
                   layout="centered",
                   initial_sidebar_state="collapsed")
load_dotenv()

SCOPE = "playlist-read-private playlist-modify-private playlist-modify-public"

st.title("🔀 ffushler")
st.caption("A better way to shuffle your gigantic playlists")

if not os.getenv("SPOTIPY_CLIENT_ID"):
    st.error("Please set the SPOTIPY_CLIENT_ID environment variable.")
    st.stop()

REDIRECT_URI = os.getenv("SPOTIPY_REDIRECT_URI", "http://127.0.0.1:8501")


sp_oauth = SpotifyOAuth(scope=SCOPE, redirect_uri=REDIRECT_URI ,open_browser=False, cache_path=None)

if "oauth_state" not in st.session_state:
    st.session_state["oauth_state"] = secrets.token_urlsafe(24)


if "code" in st.query_params:
    returned_state = st.query_params.get("state")
    expected_state = st.session_state.get("oauth_state")

    if not returned_state or returned_state != expected_state:
        pass

    try:
        st.session_state['token_info'] = sp_oauth.get_access_token(
        st.query_params['code'], as_dict = True, check_cache=False
        )

    except Exception:
        st.error("Login failed. Please try again")
        st.query_params.clear()
        st.session_state.pop("oauth_state", None)
        st.stop()

    
    st.query_params.clear()
    st.session_state.pop("oauth_state", None)
    st.rerun()
        

if "token_info" not in st.session_state:
    st.warning("Please authenticate with Spotify.")
    authorize_url = sp_oauth.get_authorize_url(state=st.session_state["oauth_state"])
    st.markdown(
        f'''
        <a href="{authorize_url}" target="_self" style="text-decoration: none;">
            <div style="
                display: inline-flex;
                align-items: center;
                gap: 0.5rem;
                background-color: #1DB954;
                color: white;
                padding: 0.6em 1.4em;
                border-radius: 999px;
                font-weight: 600;
                font-size: 1rem;
                width: fit-content;
            ">
                🎧 Login with Spotify
            </div>
        </a>
        ''',
        unsafe_allow_html=True
    )

    st.stop()

token_info = st.session_state["token_info"]

if sp_oauth.is_token_expired(token_info):
    token_info=sp_oauth.refresh_access_token(token_info["refresh_token"])
    st.session_state["token_info"] = token_info

sp = spotipy.Spotify(auth=token_info["access_token"])
st.success(f"Connected as : {sp.current_user()['display_name']}")

with st.form("shuffle_form"):
    playlist_url = st.text_input("Paste playlist URL")
    target_name = st.text_input("Name of shuffled playlist:", value="ffushled  playlist")
    submit = st.form_submit_button("Generate Shuffle")

if submit and playlist_url:
    with st.spinner("Shuffling...."):
        try:
            source_id = get_playlist(playlist_url)
            
            raw_tracks = get_tracks(sp, source_id)
            if not raw_tracks:
                st.warning("No tracks found.")
            else:
                shuffled = shuffle(raw_tracks)
                update_playlist(sp, target_name, shuffled)

                st.balloons()
                st.success("Success! You can find the shuffled playlist on your Spotify profile")

        except ValueError as e:
            st.error(str(e))
        except spotipy.SpotifyException as e:
            st.error(f"Spotify API Error: ({e.http_status}):{e.msg}")
        except Exception as e:
            st.error(f"Something went wrong. Please try again.")

st.divider()
st.caption("Built by [dot](https://github.com/dot-shreejeet)")

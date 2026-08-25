# ffushler

A Spotify playlist shuffler that goes beyond Spotify's built-in shuffle. Instead of a fully random order, ffushler groups tracks by primary artist and interleaves them —
so you get variety without the same artist popping up two or three times in a row,
which is a common complaint with naive shuffling on large playlists.

## How it works

1. Paste a Spotify playlist URL into the app
2. ffushler fetches every track in the playlist (handling pagination for large
   playlists automatically)
3. Tracks are grouped by primary artist, shuffled within each group, then
   interleaved column-by-column so no single artist dominates any stretch of
   the new order
4. The result is written to a playlist on your own Spotify account — either a
   new one, or an existing one with a matching name that you own

## Live demo

🔗 https://ffushler-dot-shreejeet.streamlit.app

## Tech stack

- **Python**
- **[Streamlit](https://streamlit.io/)** — web app framework
- **[Spotipy](https://spotipy.readthedocs.io/)** — Spotify Web API client
- **Spotify Web API** — OAuth login, playlist read/write

## Running it locally

**Prerequisites:** Python 3.10+, a free Spotify account, and a Spotify Developer
app (free to create).

1. **Clone the repo**
   ```bash
   git clone https://github.com/YOUR_USERNAME/ffushler.git
   cd ffushler
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Create a Spotify app**
   Go to the [Spotify Developer Dashboard](https://developer.spotify.com/dashboard),
   create an app, and note your **Client ID** and **Client Secret**.

4. **Set up environment variables**
   Copy the example file and fill in your credentials:
   ```bash
   cp .env.example .env
   ```
   Edit `.env`:
   ```
   SPOTIPY_CLIENT_ID=your_client_id_here
   SPOTIPY_CLIENT_SECRET=your_client_secret_here
   SPOTIPY_REDIRECT_URI=http://127.0.0.1:8501
   ```

5. **Register the redirect URI**
   In your Spotify app's dashboard settings, add `http://127.0.0.1:8501` under
   **Redirect URIs**, and add your own Spotify account's email under
   **User Management** (required while the app is in Development Mode).

6. **Run the app**
   ```bash
   streamlit run web_app.py
   ```

## Project structure

```
ffushler/
├── web_app.py       # Streamlit UI, OAuth flow, session handling
├── ffushler.py       # Core logic: playlist parsing, fetching, shuffling
├── requirements.txt  # Pinned dependencies
├── .env.example       # Template for required environment variables
└── .gitignore
```

## Known limitations

- **Development Mode allowlist:** Spotify restricts newly created apps to a
  25-user allowlist unless approved for extended quota — fine for a personal
  project, but means the live demo isn't open to everyone by default.
- **OAuth `state` verification:** implemented for CSRF protection, but not
  strictly enforced due to a session-persistence quirk with Streamlit's local
  dev server across the full OAuth redirect round-trip. Spotify's own
  allowlist serves as the practical access boundary in the meantime.

## Author

*dot*

import random
import spotipy


def get_playlist(url):
    if "playlist/" in url:
        required_url = url.split("playlist/")[1].split("?")[0]
    elif "spotify:playlist:" in url:
        required_url = url.split(":")[-1]
    else:
        required_url = url

    if len(required_url) != 22 or not required_url.isalnum():
        raise ValueError("Invalid playlist url")
    return required_url


def get_tracks(sp, playlist_id):
    tracks = []
    results = sp.playlist_items(playlist_id)
    def get_all_tracks(arr):
        for entry in arr:
            track = entry.get('item')
            if track and not track['is_local'] and track.get('type') == 'track':
                artists = track.get('artists')
                if artists and len(artists) >0 and artists[0].get('id'):
                    tracks.append({'uri' : track['uri'], 'artist_id' : artists[0]['id']})
    get_all_tracks(results['items'])

    while results['next']:
        results = sp.next(results)
        get_all_tracks(results['items'])

    return tracks

def fiedler_fill(tracks, target_length):
    k = len(tracks)
    n = target_length
    if k==n:
        return tracks.copy()
    if k ==0:
        return [None] * n
    segments = []
    n_rem = n
    k_rem = k
    while k_rem > 0:
        if k_rem ==1:
            r = n_rem
        else:
            r_float = n_rem / k_rem
            noise = r_float * random.uniform(-0.1, 0.1)
            r = int(r_float + noise)
            r = max(1, min(r, n_rem - k_rem + 1))

        segments.append(r)
        n_rem -= r
        k_rem -= 1
    padding = []
    track_i=0
    for seg in segments:
        padding.append(tracks[track_i])
        track_i += 1
        padding.extend([None] * (seg - 1))

    offset = random.randint(0, target_length -1)
    padding = padding[-offset:] + padding[:-offset]

    return padding

def shuffle(tracks):
    if not tracks:
        return []
    artist_map = {}
    for track in tracks:
        artist_map.setdefault(track['artist_id'], []).append(track)

    for id in artist_map:
        random.shuffle(artist_map[id])

    maximum_len = max(len(tracks) for tracks in artist_map.values())

    padded_tracks = {}
    for id, tracks in artist_map.items():
        padded_tracks[id] = fiedler_fill(tracks, maximum_len)

    final_tracks = []
    for column in range(maximum_len):
        col_tracks = []

        for id, padded_list in padded_tracks.items():
            track = padded_list[column]
            if track is not None:
                col_tracks.append(track)
        random.shuffle(col_tracks)
        if final_tracks and len(col_tracks) > 1:
            last_artist = final_tracks[-1]['artist_id']
            if col_tracks[0]['artist_id'] == last_artist:
                col_tracks.append(col_tracks.pop(0))

        final_tracks.extend(col_tracks)

    return [track['uri'] for track in final_tracks]

def update_playlist(sp, target_name, shuffled):
    user_id = sp.current_user()['id']
    target_id = None

    playlists = sp.current_user_playlists()
    while playlists and not target_id:
        for p in playlists['items']:
            if p['name'] == target_name and p.get('owner', {}).get('id')==user_id:
                target_id = p['id']
                break
        if playlists['next'] and not target_id:
            playlists = sp.next(playlists)
        else:
            break

    if not target_id:
        new_playlist = sp._post("me/playlists", payload={
            "name": target_name,
            "public": False,
            "description": "sent to u by dot"
        })
        target_id = new_playlist['id']
    batch_size = 100
    sp._put(f"playlists/{target_id}/items", payload={
        "uris":shuffled[:batch_size]
    })
    for i in range(batch_size, len(shuffled), batch_size):
        sp._post(f"playlists/{target_id}/items",payload={
            "uris":shuffled[i:i+batch_size]
        })


                        